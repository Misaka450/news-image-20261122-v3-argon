# news-image-20261122 — v3 card-grid edition (Argon build)

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

A broadsheet front page for **Sunday 22 November 2026**: 20 dated dispatches across 7 fronts
(Europe 5 · Middle East 4 · Asia-Pac 4 · Americas 2 · Africa 2 · Climate 1 · At Sea 2),
every one carrying its source outlet and a CONFIRMED / REPORTED / CLAIM status tag.

**Layout** (built from scratch in code, no image models, no stock art):
- extra-large 344px date masthead + dual rule + red kicker line
- 6-cell scoreboard (74,742 Gaza dead · COP31 deadline · 148 drones · 41 Vietnam flood dead · €450bn loan · 17 recovered)
- 7-colour region strip with live counts (counted from the story list, never hard-coded)
- 12 numbered cards in a 3×4 grid, each with an abstract line-drawn illustration band
- 7-region world map with pins 13–20 beside a numbered global briefings list
- DATE CHECK bar: strictly 2026-11-22 events only; multi-outlet reports of the same event merged

**Canvas**: 4000×4000 (the competition's 16,000,000-pixel ceiling) so the page stays crisp
when scaled to any judge thumbnail; a 300×300 preview is included.

All text blocks pass a bounding-box `fit()` check and a pairwise collision test (174 boxes,
15,051 pairwise checks, 0 intersections); the render is deterministic (two runs produce
byte-identical PNGs).

## Run it

```sh
python3 build.py          # writes entry.png and preview-300.png (same bytes every run)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts   # place the image where the harness looks
```

## Files

- `build.py` — the renderer (single file, Pillow only; `fit()` + collision detection included)
- `entry.png` — 4000×4000, ~1.1 MiB
- `preview-300.png` — 300×300 thumbnail
- `main.ts` — harness entry point
