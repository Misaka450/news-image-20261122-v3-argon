import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";

// Copy the rendered page into the directory the make.fun harness reads.
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
const here = dirname(new URL(import.meta.url).pathname);
copyFileSync(join(here, "entry.png"), join(outDir, "entry.png"));
console.log("wrote entry.png to " + outDir);
