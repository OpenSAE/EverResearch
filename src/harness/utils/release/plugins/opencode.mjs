/* Register bundled ResearchHarness skills in OpenCode's server plugin. */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const skills = JSON.parse(readFileSync(new URL("./skills.json", import.meta.url), "utf8"));
const root = fileURLToPath(new URL("./skills", import.meta.url));

export default {
  id: "ever-research",
  async server() {
    return {
      config(config) {
        const current = config.skills ?? {};
        const paths = current.paths ?? [];
        if (!paths.includes(root)) config.skills = { ...current, paths: [...paths, root] };
      },
    };
  },
  async setup(ctx) {
    const definitions = skills.map(({ id, name, description, path }) => {
      const location = new URL(path, import.meta.url);
      const markdown = readFileSync(location, "utf8");
      return { id, name, description, path: fileURLToPath(location),
        content: markdown.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, "") };
    });
    const registration = await ctx.skill.transform((editor) => {
      for (const skill of definitions) {
        if (!editor.get(skill.id)) editor.add(skill);
      }
    });
    return () => registration.dispose();
  },
};
