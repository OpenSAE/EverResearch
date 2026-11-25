/* Register this bundle's skills using DeepSeek Harness's filesystem provider. */
import { fileURLToPath } from "node:url";
import { apply as registerFilesystem } from "@deepseek-ai/dsh-skill-filesystem";

export const name = "researchharness";
export const inject = ["skills"];

export function apply(ctx) {
  registerFilesystem(ctx, {
    providerName: "researchharness",
    includeDefaultRoots: false,
    customSkillDirs: [fileURLToPath(new URL("./skills", import.meta.url))],
    watch: false,
  });
}
