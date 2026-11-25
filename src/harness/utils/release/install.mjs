#!/usr/bin/env node
/* Purpose: install the bundled ResearchHarness wheel and project skills.
 * Scope: local, explicitly selected projects and hosts. */
import { spawnSync } from "node:child_process";
import { readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const directory = dirname(fileURLToPath(import.meta.url));
const usage = "researchharness [--dry-run] [--mcp] --project PATH [--agent NAME ...]";
const forwarded = [];
let dryRun = false;
let withMcp = false;
let project = false;
const agents = new Set([
  "codex", "claude-code", "cursor", "github-copilot", "gemini-cli", "qwen-code",
  "opencode", "openclaw", "deepseek-harness", "generic",
]);

function run(command, args) {
  const child = spawnSync(command, args, { stdio: "inherit" });
  if (child.error) throw new Error(`${command}: ${child.error.message}`);
  if (child.status !== 0) process.exit(child.status ?? 1);
}

try {
  const options = process.argv.slice(2);
  for (let index = 0; index < options.length; index++) {
    const option = options[index];
    if (option === "--help" || option === "-h") {
      console.log(usage);
      process.exit(0);
    }
    if (option === "--dry-run") {
      dryRun = true;
    } else if (option === "--mcp") {
      withMcp = true;
    } else if (option === "--project" || option === "--agent") {
      const value = options[++index];
      if (!value || value.startsWith("--") || (option === "--agent" && !agents.has(value))) {
        throw new Error(`Invalid value for ${option}: ${value ?? ""}`);
      }
      if (option === "--project") {
        if (project) throw new Error("Select exactly one project");
        project = true;
      }
      forwarded.push(option, value);
    } else {
      throw new Error(`Unknown option: ${option}`);
    }
  }
  if (!project) throw new Error("--project is required");
  const wheels = readdirSync(directory).filter((name) => name.endsWith(".whl"));
  if (wheels.length !== 1) throw new Error("Installer must contain exactly one ResearchHarness wheel");
  const wheel = join(directory, wheels[0]);
  const spec = withMcp ? `${wheel}[mcp]` : wheel;
  if (dryRun) {
    console.log(JSON.stringify({ python: ["uv", "tool", "install", spec], skills: ["rh", "skills", "install", ...forwarded] }, null, 2));
  } else {
    run("uv", ["tool", "install", "--reinstall", spec]);
    const bin = spawnSync("uv", ["tool", "dir", "--bin"], { encoding: "utf8" });
    if (bin.error || bin.status !== 0 || !bin.stdout.trim()) {
      throw new Error("Could not locate the uv tool binary directory");
    }
    const executable = process.platform === "win32" ? "rh.exe" : "rh";
    run(join(bin.stdout.trim(), executable), ["skills", "install", ...forwarded]);
  }
} catch (error) {
  console.error(error.message);
  console.error(usage);
  process.exitCode = 2;
}
