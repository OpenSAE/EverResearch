"""Build the public ResearchHarness artifacts from an explicit file selection.

Use from a ResearchHarness checkout. Builds from an isolated copy and writes
archives, a member inventory, and checksums to a selected local directory.
"""

import argparse
from hashlib import sha256
from io import BytesIO
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
    "LICENSE", "README.md", "README.zh-CN.md", "pyproject.toml",
    "src/harness/*.py", "src/harness/core/*.py", "src/harness/core/README.md",
    "src/harness/projects/*.py", "src/harness/projects/*.md", "src/harness/projects/*.md.in",
    "src/harness/projects/standalone/*.py", "src/harness/projects/standalone/*.md",
    "src/harness/projects/standalone/offline/*.py", "src/harness/projects/standalone/offline/*.md",
    "src/harness/utils/*.py", "src/harness/utils/transfer/*.py", "src/harness/utils/transfer/README.md",
    "src/harness/utils/release/*.py", "src/harness/utils/release/install.mjs",
    "src/harness/utils/release/plugins/*.mjs", "src/harness/utils/release/plugins/*.md",
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
PLUGIN_RUNNER = "src/harness/utils/release/rh.py"
CLI_COMMAND = re.compile(rb"\brh (?:projects|utils|guide|skills|doctor|mcp)\b")
SECRETS = re.compile(
    rb"(?:gh[pousr]_|github_pat_|hf_)[A-Za-z0-9_]{25,}|"
    rb"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----|/(?:workspace|home|root)/[^\s<>\"')]+"
)
PLUGIN_CLI_GUIDANCE = b"""## Run the EverResearch CLI

Use Python 3.11, 3.12, or 3.13 to run `scripts/rh.py` from the current skill,
followed by the arguments after `rh`. For example, pass `projects project check <project-path>` to check a
project. Use `${CLAUDE_SKILL_DIR}` in Claude Code or Cowork and the staged skill
directory in Claude web.

The launcher uses the packaged runtime when available. GitHub marketplace
installs download the pinned wheel once and verify its checksum before use.
The launcher creates a private environment and may fetch Python dependencies.
With no Python execution available, review the files you can
access and tell the user which automated checks you could not run.

For a separate terminal installation, the official PyPI package is
`ever-research` from OpenSAE. The PyPI project named `researchharness` is
maintained separately."""
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


def public_members(root):
    """Select the skills and project resources shared by all build entry points."""
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
    check_public_members(resources)
    return skills, resources, cub


def check_public_members(members):
    for name, content in members.items():
        if name.endswith((".md", ".py", ".yaml", ".toml", ".mjs", ".json", ".js", ".css", ".html")) and SECRETS.search(content):
            raise ValueError(f"Review possible private content in {name}")


def package(root, output):
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    version = project["version"]
    skills, resources, cub = public_members(root)
    source = {**select(root, (*CORE, ARTIFACT_GUIDE)), **resources}
    check_public_members(source)
    with tempfile.TemporaryDirectory(prefix="researchharness-build-") as temporary:
        stage = Path(temporary) / "source"
        for name, content in source.items():
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        wheel_output = Path(temporary) / "wheel"
        subprocess.run(["uv", "build", "--wheel", "--out-dir", str(wheel_output), str(stage)], check=True)
        built_wheel, = wheel_output.glob("*.whl")
        wheel = output / built_wheel.name
        shutil.copyfile(built_wheel, wheel)
        with ZipFile(wheel) as installed:
            with ZipFile(BytesIO(installed.read("harness/public_resources.zip"))) as bundled:
                contents = {name: bundled.read(name) for name in bundled.namelist()}
            if contents != resources:
                raise ValueError("Wheel resources differ from the audited source")
            expected = {name.removeprefix("src/") for name in source if name.startswith("src/harness/")
                        and not name.startswith(f"{CUB}/") and name.endswith(".py")}
            if not expected <= set(installed.namelist()):
                raise ValueError(f"Missing wheel modules: {expected - set(installed.namelist())}")
        archive(output / f"ever-research-{version}-source.zip", source)
        archive(output / f"ever-research-{version}-example.zip", {f"BirdStudy/{k}": v for k, v in cub.items()})
        build_plugins(output, Path(temporary), version, skills, source, wheel)
        build_npm(Path(temporary), output, version, wheel, source)
    (output / "verify.py").write_bytes(source["src/harness/utils/release/verify.py"])
    (output / "INSTALL.md").write_bytes(platform_readme(source, "installer", version))
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


def platform_readme(source, platform, version):
    docs = "src/harness/utils/release/plugins"
    repo = b"https://github.com/OpenSAE/EverResearch"
    guide = b"\n".join((
        f"# EverResearch for {PLATFORM_TITLES[platform]}\n".encode(),
        b"## Purpose and main function\n",
        b"Install OpenSAE's research project maintenance tools and run a first check.\n",
        b"## Scope of application\n",
        b"Use these steps for projects you can access from this environment.\n",
        source[f"{docs}/{platform}.md"],
        source[f"{docs}/usage.md"],
    ))
    downloads = b"https://raw.githubusercontent.com/OpenSAE/EverResearch/main/plugins/installer"
    return (guide.replace(b"@REPO@", repo).replace(b"@DOWNLOAD@", downloads)
            .replace(b"@VERSION@", version.encode()))


PLATFORM_TITLES = {
    "agent-plugin": "Copilot, Qwen and Skills CLI",
    "claude-plugin": "Claude",
    "codex-plugin": "Codex",
    "cursor-plugin": "Cursor",
    "gemini-extension": "Gemini CLI",
    "opencode": "OpenCode",
    "openclaw": "OpenClaw",
    "deepseek": "DeepSeek Harness",
    "installer": "the terminal",
}


def plugin_runtime(skills, runner, wheel, *, isolated=False, include_wheel=True):
    """Supply the launcher and its wheel within an agent's installed skill set."""
    additions = {}
    cli_skills = {path.split("/")[0] for path, body in skills.items()
                  if path.endswith(".md") and CLI_COMMAND.search(body)}
    wheel_data = wheel.read_bytes()
    lock = json_bytes({"filename": wheel.name, "sha256": sha256(wheel_data).hexdigest(),
                       "size": len(wheel_data)})
    for skill in sorted(cli_skills):
        additions[f"{skill}/scripts/rh.py"] = runner
        additions[f"{skill}/scripts/rh-runtime.json"] = lock
        key = f"{skill}/SKILL.md"
        frontmatter, heading, body = skills[key].split(b"---", 2)
        first, rest = body.strip().split(b"\n\n", 1)
        additions[key] = (frontmatter + b"---" + heading + b"---\n\n" + first
                        + b"\n\n" + PLUGIN_CLI_GUIDANCE + b"\n\n" + rest + b"\n")
    if include_wheel:
        for skill in sorted(cli_skills if isolated else {"maintain-project"}):
            additions[f"{skill}/scripts/{wheel.name}"] = wheel_data
    return additions



def build_plugins(output, work, version, skills, source, wheel):
    name = "ever-research"
    description = "Maintain and verify research projects with EverResearch."
    members = {f"skills/{path}": body for path, body in skills.items()}
    members.update({"LICENSE": source["LICENSE"], "README.md": source[ARTIFACT_GUIDE]})
    runtime = plugin_runtime(skills, source[PLUGIN_RUNNER], wheel, include_wheel=False)
    members.update({f"skills/{path}": body for path, body in runtime.items()})
    shared_wheel = {f"skills/maintain-project/scripts/{wheel.name}": wheel.read_bytes()}
    manifest = {"name": name, "version": version, "description": description}
    portable = {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", **manifest,
    }
    interface = {
        "displayName": "EverResearch", "shortDescription": "Maintain research projects",
        "longDescription": ("Inspect and maintain research code, datasets, models, configurations, "
                            "and experiment records. Automated checks require project files and a "
                            "Python-capable agent workspace."),
        "developerName": "OpenSAE", "category": "Developer Tools",
        "capabilities": ["Project maintenance", "Project structure validation"],
        "websiteURL": "https://github.com/OpenSAE/EverResearch",
    }
    platform_manifests = {
        "agent-plugin": ("plugin.json", portable),
        "codex-plugin": (".codex-plugin/plugin.json", {**manifest, "skills": "./skills/", "interface": interface}),
        "cursor-plugin": (".cursor-plugin/plugin.json", {**manifest, "skills": "./skills/", "interface": interface}),
        "claude-plugin": (".claude-plugin/plugin.json", {**manifest, "author": {"name": "OpenSAE"},
                          "homepage": "https://github.com/OpenSAE/EverResearch"}),
        "gemini-extension": ("gemini-extension.json", manifest),
    }
    marketplace = {}
    for platform, (path, config) in platform_manifests.items():
        plugin = {**members, path: json_bytes(config),
                  "README.md": platform_readme(source, platform, version)}
        marketplace.update({f"plugins/{platform}/{file}": contents for file, contents in plugin.items()})
        local_wheels = shared_wheel
        if platform == "claude-plugin":
            # Claude chat stages only the active skill directory in its Python sandbox.
            runtime = plugin_runtime(skills, source[PLUGIN_RUNNER], wheel, isolated=True)
            local_wheels = {f"skills/{key}": body for key, body in runtime.items()
                            if key.endswith(".whl")}
        archive(output / f"{name}-{version}-{platform}.zip", {**plugin, **local_wheels})

    adapter = "src/harness/utils/release/plugins"
    entries = []
    for path, body in skills.items():
        if path.endswith("/SKILL.md"):
            metadata = yaml.safe_load(body.decode().split("---", 2)[1])
            entries.append({"id": metadata["name"], "name": metadata["name"],
                            "description": metadata["description"], "path": f"./skills/{path}"})
    opencode = {
        **members,
        "package.json": json_bytes({**manifest, "name": "@opensae/ever-research-opencode",
                                    "type": "module", "exports": {"./server": "./index.mjs"}}),
        "index.mjs": source[f"{adapter}/opencode.mjs"],
        "skills.json": json_bytes(entries),
        "README.md": platform_readme(source, "opencode", version),
    }
    archive(output / f"{name}-{version}-opencode-plugin.zip", {**opencode, **shared_wheel})
    openclaw = {
        **members,
        "package.json": json_bytes({**manifest, "type": "module",
                                    "openclaw": {"extensions": ["./index.mjs"]}}),
        "openclaw.plugin.json": json_bytes({
            **manifest, "id": name, "skills": ["./skills"],
            "configSchema": {"type": "object", "additionalProperties": False},
        }),
        "index.mjs": source[f"{adapter}/openclaw.mjs"],
        "README.md": platform_readme(source, "openclaw", version),
    }
    archive(output / f"{name}-{version}-openclaw-plugin.zip", {**openclaw, **shared_wheel})
    bundle_name = "@opensae/ever-research-dsh"
    dsh = {
        **members,
        "package.json": json_bytes({
            **manifest, "name": bundle_name, "type": "module", "main": "index.mjs",
            "dsh": {"bundle": {"patch": "./cordis.patch.yml"}},
            "engines": {"dsh": ">=0.2.2-rc.5 <0.3.0"},
        }),
        "cordis.patch.yml": yaml.safe_dump([
            {"insert": [{"id": "ever-research-skills", "name": bundle_name}]},
        ]).encode(),
        "index.mjs": source[f"{adapter}/deepseek.mjs"],
        "skills.json": json_bytes(entries),
        "README.md": platform_readme(source, "deepseek", version),
    }
    dsh_work = work / "deepseek"
    for path, contents in {**dsh, **shared_wheel}.items():
        target = dsh_work / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(contents)
    subprocess.run(["npm", "pack", "--pack-destination", str(output)], cwd=dsh_work, check=True)
    archive(output / f"{name}-{version}-skills.zip", {**members, **shared_wheel})
    for platform, plugin in (("opencode", opencode), ("openclaw", openclaw), ("deepseek", dsh)):
        marketplace.update({f"plugins/{platform}/{file}": contents for file, contents in plugin.items()})
    catalog = {"name": "ever-research", "owner": {"name": "OpenSAE"}}
    for path, platform in {
        ".claude-plugin/marketplace.json": "claude-plugin",
        ".cursor-plugin/marketplace.json": "cursor-plugin",
        ".github/plugin/marketplace.json": "agent-plugin",
    }.items():
        marketplace[path] = json_bytes({
            **catalog, "plugins": [{**manifest, "source": f"./plugins/{platform}"}],
        })
    marketplace[".agents/plugins/marketplace.json"] = json_bytes({
        "name": catalog["name"], "plugins": [{
            "name": name, "source": {"source": "local", "path": "./plugins/codex-plugin"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "interface": {"displayName": "EverResearch"},
        }],
    })
    marketplace["README.md"] = source["README.md"]
    marketplace["LICENSE"] = source["LICENSE"]
    archive(output / f"{name}-{version}-marketplace.zip", marketplace)


def build_npm(temporary, output, version, wheel, source):
    npm = temporary / "npm"
    npm.mkdir()
    installer = npm / "install.mjs"
    installer.write_bytes(source["src/harness/utils/release/install.mjs"])
    installer.chmod(0o755)
    shutil.copyfile(wheel, npm / wheel.name)
    (npm / "README.md").write_bytes(platform_readme(source, "installer", version))
    (npm / "rh.py").write_bytes(source[PLUGIN_RUNNER])
    (npm / "LICENSE").write_bytes(source["LICENSE"])
    (npm / "package.json").write_bytes(json_bytes({
        "name": "@opensae/ever-research", "version": version,
        "description": "Install ResearchHarness tools and project skills",
        "bin": {"ever-research": "install.mjs"},
        "engines": {"node": ">=18"}, "license": "Apache-2.0",
        "files": ["install.mjs", "rh.py", wheel.name],
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
