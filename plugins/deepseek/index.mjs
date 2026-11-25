/* Purpose: expose the packaged EverResearch skills through DeepSeek Harness.
 * Scope: the profile where the user installs this Cordis bundle. */
import { readFile } from "node:fs/promises";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

export const name = "ever-research";
export const inject = ["skills"];

const definitions = JSON.parse(readFileSync(new URL("./skills.json", import.meta.url), "utf8"));
const candidates = definitions.map(({ name, description, path }) => {
  const locator = new URL(path, import.meta.url);
  return { name, description, locator, provider: "ever-research", source: "bundled",
    invocation: { modelInvocable: true, userInvocable: true },
    resourceBase: { kind: "directory", path: fileURLToPath(new URL("./", locator)) },
    rank: 600 };
});

export function apply(ctx) {
  ctx.skills.registerProvider(() => ({
    name,
    list: async () => candidates,
    async get(candidate) {
      const { locator, rank, ...definition } = candidate;
      const markdown = await readFile(locator, "utf8");
      return { ...definition, content: markdown.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, "") };
    },
  }));
}
