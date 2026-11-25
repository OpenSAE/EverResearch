#!/usr/bin/env node
/* Purpose: install the bundled EverResearch CLI and project-local skills.
 * Scope: the calling user's tool environment and selected project. */
import { spawnSync } from "node:child_process";
import { readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const directory = dirname(fileURLToPath(import.meta.url));
const usage = "ever-research [--project PATH] [--agent NAME ...] [--dry-run] [--mcp]";
const agents = new Map([
  ["codex", "codex"], ["claude-code", "claude"], ["cursor", "cursor-agent"],
  ["github-copilot", "copilot"], ["gemini-cli", "gemini"], ["qwen-code", "qwen"],
  ["opencode", "opencode"], ["openclaw", "openclaw"], ["deepseek-harness", "dsh"],
  ["generic", null],
]);

function probe(command, args) {
  return spawnSync(command, args, { encoding: "utf8" });
}

function run(command, args) {
  const child = spawnSync(command, args, { stdio: "inherit" });
  if (child.error) throw child.error;
  if (child.status !== 0) process.exit(child.status ?? 1);
}

function options(args) {
  let project, dryRun = false, withMcp = false;
  const selected = new Set();
  for (let index = 0; index < args.length; index++) {
    const option = args[index];
    if (option === "--help" || option === "-h") {
      console.log(usage);
      process.exit(0);
    }
    if (option === "--dry-run") dryRun = true;
    else if (option === "--mcp") withMcp = true;
    else if (option === "--project" || option === "--agent") {
      const value = args[++index];
      if (!value || value.startsWith("--")) throw new Error(`Missing value for ${option}`);
      if (option === "--project") {
        if (project) throw new Error("Select one project");
        project = value;
      } else {
        if (!agents.has(value)) throw new Error(`Unknown agent: ${value}`);
        selected.add(value);
      }
    } else {
      throw new Error(`Unknown option: ${option}`);
    }
  }
  if (selected.size === 0) {
    const locate = process.platform === "win32" ? "where.exe" : "which";
    for (const [host, command] of agents) {
      if (command && probe(locate, [command]).status === 0) selected.add(host);
    }
  }
  if (selected.size === 0) selected.add("generic");
  return { dryRun, withMcp, args: ["--project", project ?? process.cwd(),
    ...Array.from(selected).flatMap((agent) => ["--agent", agent])] };
}

function findPython() {
  const check = ["-I", "-c",
    "import sys; sys.exit(1) if not ((3, 11) <= sys.version_info < (3, 14)) else print(sys.executable)"];
  for (const [command, ...args] of [
    ["python3"], ["python"], ["python3.13"], ["python3.12"], ["python3.11"],
    ["py", "-3.13"], ["py", "-3.12"], ["py", "-3.11"],
  ]) {
    const result = probe(command, [...args, ...check]);
    if (result.status === 0 && result.stdout.trim()) return result.stdout.trim();
  }
  return null;
}

try {
  const configuration = options(process.argv.slice(2));
  const wheels = readdirSync(directory).filter((name) => /^ever_research-.*\.whl$/.test(name));
  if (wheels.length !== 1) throw new Error("Installer must contain one EverResearch wheel");
  const wheel = join(directory, wheels[0]);
  const spec = configuration.withMcp ? `${wheel}[mcp]` : wheel;
  const skills = ["skills", "install", ...configuration.args];
  const uv = probe("uv", ["--version"]).status === 0;
  if (configuration.dryRun) {
    console.log(JSON.stringify({ projectSkills: skills, installer: uv ? "uv" : "Python runner",
      wheel: spec }, null, 2));
  } else if (uv) {
    run("uv", ["tool", "install", "--reinstall", "--python", findPython() ?? "3.13", spec]);
    const bin = probe("uv", ["tool", "dir", "--bin"]);
    if (bin.status !== 0 || !bin.stdout.trim()) {
      throw new Error("Could not locate the uv tool binary directory");
    }
    const executable = process.platform === "win32" ? "rh.exe" : "rh";
    process.env.RH_PLUGIN_WHEEL = wheel;
    run(join(bin.stdout.trim(), executable), skills);
  } else {
    if (configuration.withMcp) throw new Error("The --mcp option requires uv.");
    const python = findPython();
    if (!python) throw new Error("Install Python 3.11, 3.12, or 3.13, or install uv.");
    run(python, ["-I", join(directory, "rh.py"), ...skills]);
  }
} catch (error) {
  console.error(error.message);
  console.error(usage);
  process.exitCode = 2;
}
