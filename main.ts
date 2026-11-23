import { mkdirSync, copyFileSync } from "node:fs";
import { dirname, join } from "node:path";

const outputDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
mkdirSync(outputDir, { recursive: true });

const scriptDir = dirname(new URL(import.meta.url).pathname);
const sourcePath = join(scriptDir, "entry.png");
const targetPath = join(outputDir, "entry.png");

copyFileSync(sourcePath, targetPath);
console.log(targetPath);
