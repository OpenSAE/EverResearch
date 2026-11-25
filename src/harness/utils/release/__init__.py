"""Build the public ResearchHarness artifacts from an explicit file selection.

Use from a ResearchHarness checkout. Builds from an isolated copy and writes
archives, a member inventory, and checksums to a selected local directory.
"""

import argparse
from hashlib import sha256
import json
import posixpath
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import tomllib
from urllib.parse import unquote
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import yaml


SKILLS = {
    "extract-structure": ("LICENSE", "README*.md", "AGENTS.md", "agents/*.yaml", "references/*.md",
                          "scripts/*.py", "assets/viewer/*", "assets/screenshots/*.png",
                          "docs/index.html", "examples/*.html"),
    "maintain-base": ("references/*.md",),
    "maintain-code": ("check_dependencies.py", "references/*.md"),
    "maintain-conf": (),
    "maintain-dataset": ("references/*.md",),
    "maintain-experiment": ("references/*.md",),
    "maintain-github": ("references/*.md", "scripts/publish.py"),
    "maintain-huggingface": ("scripts/download_assets.py",),
    "maintain-knowledge": (),
    "maintain-model": ("references/*.md",),
    "maintain-optional": ("references/*.md",),
    "maintain-project": ("references/*.md",),
    "maintain-skill": ("references/*.md", "exam/exam_rule.md", "exam/.gitignore", "agent_log/.gitignore"),
    "maintain-task": ("references/*.md",),
    "maintain-tmp": (),
}
CORE = (
    "LICENSE", "README.md", "pyproject.toml",
    "src/harness/*.py", "src/harness/core/*.py", "src/harness/core/README.md",
    "src/harness/projects/*.py", "src/harness/projects/*.md", "src/harness/projects/*.md.in",
    "src/harness/projects/standalone/*.py", "src/harness/projects/standalone/*.md",
    "src/harness/projects/standalone/offline/*.py", "src/harness/projects/standalone/offline/*.md",
    "src/harness/utils/*.py", "src/harness/utils/transfer/*.py", "src/harness/utils/transfer/README.md",
    "src/harness/utils/release/*.py", "src/harness/utils/release/install.mjs",
)
CUB = "src/harness/projects/templates/cub"
CUB_FILES = (
    ".gitignore", ".researchharness/maintain.py", ".researchharness/mode.toml",
    ".researchharness/offline/check.py", ".researchharness/offline/operations.md",
    "AGENTS.md", "README.md", "pyproject.toml", "conf/config.yaml",
    "base/**/*.py", "datasets/**/*.py", "doc/**/*.md", "models/**/*.py",
    "models/**/config.toml", "tasks/**/*.py", "tests/*.py", "experiment/**/recipe.toml",
)
SHARED = ("src/harness/projects/README.md", "src/harness/projects/operations.md")
ARTIFACT_GUIDE = "src/harness/utils/release/README.md"
SECRETS = re.compile(
    rb"(?:gh[pousr]_|github_pat_|hf_)[A-Za-z0-9_]{25,}|"
    rb"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----|/(?:workspace|home|root)/[^\s<>\"')]+"
)
LINK = re.compile(r"\[[^\]\n]+\]\((<[^>]+>|[^\s)]+)\)")


def select(root, patterns):
    if root.is_symlink():
        raise ValueError(f"Release source is a symlink: {root}")
    selected = {}
    for pattern in patterns:
        for path in root.glob(pattern):
            if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
                raise ValueError(f"Release member crosses a source symlink: {path}")
            if path.is_file() and "__pycache__" not in path.parts:
                selected[path.relative_to(root).as_posix()] = path.read_bytes()
    return selected


def json_bytes(data):
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode()


def archive(path, members):
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as output:
        for name, content in sorted(members.items()):
            member = ZipInfo(name)
            member.external_attr = 0o100644 << 16
            output.writestr(member, content, compress_type=ZIP_DEFLATED)


def validate_skill_members(skills):
    for name, content in skills.items():
        if not name.endswith(".md"):
            continue
        body = re.sub(r"```[\s\S]*?```", "", content.decode("utf-8"))
        if name.endswith("/SKILL.md"):
            _, frontmatter, _ = body.split("---", 2)
            metadata = yaml.safe_load(frontmatter)
            if (metadata.get("name") != name.split("/")[0]
                    or not 0 < len(metadata.get("description", "")) <= 1024):
                raise ValueError(f"Invalid Agent Skills metadata: {name}")
        for match in LINK.finditer(body):
            link = unquote(match[1].strip("<>").split("#")[0])
            if not link or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", link):
                continue
            target = posixpath.normpath(posixpath.join(posixpath.dirname(name), link))
            if target not in skills and not any(item.startswith(target + "/") for item in skills):
                raise ValueError(f"Unresolved skill reference in {name}: {link}")


def package(root, output):
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    version = project["version"]
    skills = {}
    for name, patterns in SKILLS.items():
        members = select(root / ".agents/skills" / name, ("SKILL.md", *patterns))
        if "SKILL.md" not in members:
            raise ValueError(f"Missing skill: {name}")
        skills.update({f"{name}/{path}": content for path, content in members.items()})
    validate_skill_members(skills)
    resources = {f".agents/skills/{path}": content for path, content in skills.items()}
    cub = select(root / CUB, CUB_FILES)
    if not {"README.md", "pyproject.toml", "conf/config.yaml"} <= cub.keys():
        raise ValueError("The CUB example is incomplete")
    resources.update({f"{CUB}/{path}": content for path, content in cub.items()})
    resources.update(select(root, SHARED))
    source = {**select(root, (*CORE, ARTIFACT_GUIDE)), **resources}
    for name, content in source.items():
        if name.endswith((".md", ".py", ".yaml", ".toml", ".mjs", ".json", ".js", ".css", ".html")) and SECRETS.search(content):
            raise ValueError(f"Review possible private content in {name}")
    with tempfile.TemporaryDirectory(prefix="researchharness-build-") as temporary:
        stage = Path(temporary) / "source"
        for name, content in source.items():
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        resource_name = "src/harness/public_resources.zip"
        archive(stage / resource_name, resources)
        source[resource_name] = (stage / resource_name).read_bytes()
        wheel_output = Path(temporary) / "wheel"
        subprocess.run(["uv", "build", "--wheel", "--out-dir", str(wheel_output), str(stage)], check=True)
        built_wheel, = wheel_output.glob("*.whl")
        wheel = output / built_wheel.name
        shutil.copyfile(built_wheel, wheel)
        with ZipFile(wheel) as installed:
            if installed.read("harness/public_resources.zip") != source[resource_name]:
                raise ValueError("Wheel resources differ from the audited source")
            expected = {name.removeprefix("src/") for name in source if name.startswith("src/harness/")
                        and not name.startswith(f"{CUB}/") and name.endswith(".py")}
            if not expected <= set(installed.namelist()):
                raise ValueError(f"Missing wheel modules: {expected - set(installed.namelist())}")
        archive(output / f"researchharness-{version}-source.zip", source)
        archive(output / f"researchharness-{version}-example.zip", {f"BirdStudy/{k}": v for k, v in cub.items()})
        build_plugins(output, version, skills, source["LICENSE"], source[ARTIFACT_GUIDE])
        build_npm(Path(temporary), output, version, wheel, source)
    (output / "verify.py").write_bytes(source["src/harness/utils/release/verify.py"])
    (output / "INSTALL.md").write_bytes(source[ARTIFACT_GUIDE])
    inventory = {}
    for path in sorted(output.iterdir()):
        inventory[path.name] = sha256(path.read_bytes()).hexdigest()
    (output / "SHA256SUMS").write_text(
        "".join(f"{digest}  {name}\n" for name, digest in inventory.items()), encoding="ascii",
    )
    (output / "CONTENTS.json").write_bytes(json_bytes({
        "version": version, "public_source": sorted(source), "wheel_resources": sorted(resources),
        "archives": inventory,
    }))


def build_plugins(output, version, skills, license_text, guide):
    name = "researchharness"
    description = "Maintain and verify research projects using shared ResearchHarness skills and rh."
    members = {f"skills/{path}": body for path, body in skills.items()}
    members.update({"LICENSE": license_text, "README.md": guide})
    manifest = {"name": name, "version": version, "description": description}
    platform_manifests = {
        "agent-plugin": ("plugin.json", {
            "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", **manifest,
        }),
        "claude-plugin": (".claude-plugin/plugin.json", {**manifest, "author": {"name": "OpenSAE"}}),
        "gemini-extension": ("gemini-extension.json", manifest),
    }
    for platform, (path, config) in platform_manifests.items():
        archive(output / f"{name}-{version}-{platform}.zip", {**members, path: json_bytes(config)})
    archive(output / f"{name}-{version}-skills.zip", members)


def build_npm(temporary, output, version, wheel, source):
    npm = temporary / "npm"
    npm.mkdir()
    installer = npm / "install.mjs"
    installer.write_bytes(source["src/harness/utils/release/install.mjs"])
    installer.chmod(0o755)
    shutil.copyfile(wheel, npm / wheel.name)
    (npm / "README.md").write_bytes(source[ARTIFACT_GUIDE])
    (npm / "LICENSE").write_bytes(source["LICENSE"])
    (npm / "package.json").write_bytes(json_bytes({
        "name": "@opensae/researchharness", "version": version,
        "description": "Install ResearchHarness tools and project skills",
        "bin": {"researchharness": "install.mjs"},
        "engines": {"node": ">=18"}, "license": "Apache-2.0",
        "files": ["install.mjs", wheel.name],
    }))
    subprocess.run(["npm", "pack", "--pack-destination", str(output)], cwd=npm, check=True)


def main(argv):
    parser = argparse.ArgumentParser(prog="rh utils release")
    parser.add_argument("--source", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    root = args.source.resolve(strict=True)
    output = args.output.resolve()
    if output.exists():
        parser.error("Choose a new output directory for this build")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".researchharness-release-", dir=output.parent) as work:
        stage = Path(work) / "release"
        stage.mkdir()
        package(root, stage)
        stage.replace(output)
    print(output)
    return 0
