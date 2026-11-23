import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
copyFileSync(join(dirname(new URL(import.meta.url).pathname), "entry.png"), join(outDir, "entry.png"));
