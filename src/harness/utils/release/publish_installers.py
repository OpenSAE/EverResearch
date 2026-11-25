"""Publish installer files as GitHub Release assets and verify their contents.

Used by the EverResearch release workflow. Git remains the source for code and
plugin manifests. GitHub CLI uses the identity supplied by the workflow.
"""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory


LEGACY = {
    "0.2.0": "cfea7a7c923e82667e4423a354099755e11b5db4",
    "0.2.1": "022f7b323577cb43589a82807fc30fe5e451c77c",
    "0.2.2": "ce47336a61fc87a79667d9a3101d0d590fcd3dc9",
    "0.2.3": "014084ef0fa1d4a345912646742b8bf87cfcbfd0",
}
INSTALLER_PATH = "plugins/installer/"
PUBLIC_SUFFIXES = (".whl", ".tgz", ".zip")
RELEASE_FIELDS = "isDraft,targetCommitish,assets"


def output(*args):
    return subprocess.check_output(args, text=True, encoding="utf-8").strip()


def gh(*args):
    subprocess.run(["gh", "release", *args], check=True)


def verify_files(directory):
    expected = {}
    for line in (directory / "SHA256SUMS").read_text(encoding="ascii").splitlines():
        digest, name = line.split("  ", 1)
        if not re.fullmatch(r"[a-f0-9]{64}", digest) or not re.fullmatch(r"[A-Za-z0-9_.-]+", name):
            raise ValueError(f"Invalid asset checksum entry: {line}")
        if sha256((directory / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Asset checksum mismatch: {name}")
        expected[name] = digest
    if not expected:
        raise ValueError("The release checksum file is empty")
    return expected


def legacy_files(version, target, directory):
    filenames = output("git", "ls-tree", "-r", "--name-only", target, "--", INSTALLER_PATH)
    checksums = []
    for path in filenames.splitlines():
        name = path.removeprefix(INSTALLER_PATH)
        if not name.endswith(PUBLIC_SUFFIXES) or not re.search(rf"-{re.escape(version)}[-.]", name):
            continue
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", name):
            raise ValueError(f"Invalid filename: {name}")
        payload = subprocess.check_output(["git", "show", f"{target}:{path}"])
        (directory / name).write_bytes(payload)
        checksums.append(f"{sha256(payload).hexdigest()}  {name}\n")
    if not checksums:
        raise ValueError(f"No installer assets found at {target}")
    (directory / "SHA256SUMS").write_text("".join(sorted(checksums)), encoding="ascii")


def release_info(tag):
    result = subprocess.run(["gh", "release", "view", tag, "--json", RELEASE_FIELDS],
                            capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        if "release not found" in result.stderr.lower():
            return None
        raise RuntimeError(result.stderr.strip())
    return json.loads(result.stdout)


def publish(version, target, directory):
    expected = verify_files(directory)
    wanted = sorted({*expected, "SHA256SUMS"})
    tag = f"v{version}"
    release = release_info(tag)
    if release is None:
        gh("create", tag, "--target", target, "--draft", "--title", f"EverResearch {version}",
           "--notes", "Official EverResearch installers and SHA-256 checksums.")
        release = release_info(tag)
    if release is None:
        raise RuntimeError(f"Cannot read {tag} after creation")
    if release["isDraft"]:
        if release["targetCommitish"] != target:
            raise ValueError(f"Draft {tag} targets a different commit")
    else:
        ref = f"refs/tags/{tag}"
        remote_tag = output("git", "ls-remote", "origin", ref, f"{ref}^{{}}")
        parts = dict(line.split("\t", 1)[::-1] for line in remote_tag.splitlines())
        if parts.get(f"{ref}^{{}}", parts.get(ref)) != target:
            raise ValueError(f"Published tag {tag} targets a different commit")
    existing = {asset["name"] for asset in release["assets"]}
    missing = [str(directory / name) for name in wanted if name not in existing]
    if missing:
        if not release["isDraft"]:
            raise ValueError(f"Published release {tag} is missing installer assets")
        gh("upload", tag, *missing)
    with TemporaryDirectory(prefix="everresearch-release-verify-") as temporary:
        downloaded = Path(temporary)
        for name in wanted:
            gh("download", tag, "--pattern", name, "--dir", str(downloaded))
            if sha256((downloaded / name).read_bytes()).digest() != sha256((directory / name).read_bytes()).digest():
                raise ValueError(f"Published asset differs from the verified build: {name}")
    if release["isDraft"]:
        gh("edit", tag, "--draft=false")
    print(f"Verified GitHub Release {tag} ({len(wanted)} files)", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--migrate", action="store_true")
    parser.add_argument("--source", type=Path)
    parser.add_argument("--version")
    parser.add_argument("--target")
    args = parser.parse_args()
    if args.migrate:
        for version, target in LEGACY.items():
            with TemporaryDirectory(prefix=f"everresearch-{version}-") as temporary:
                directory = Path(temporary)
                legacy_files(version, target, directory)
                publish(version, target, directory)
        return
    if not args.source or not args.version or not args.target:
        parser.error("Specify --source, --version, and --target")
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+){2}", args.version):
        parser.error("Use a three-part release version")
    if not re.fullmatch(r"[a-f0-9]{40}", args.target):
        parser.error("Use the full commit SHA as --target")
    publish(args.version, args.target, args.source.resolve())


if __name__ == "__main__":
    main()
