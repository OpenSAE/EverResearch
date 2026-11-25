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
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--target", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+){2}", args.version):
        parser.error("Use a three-part release version")
    if not re.fullmatch(r"[a-f0-9]{40}", args.target):
        parser.error("Use the full commit SHA as --target")
    publish(args.version, args.target, args.source.resolve())


if __name__ == "__main__":
    main()
