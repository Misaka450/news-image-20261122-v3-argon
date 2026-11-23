#!/usr/bin/env python3
"""
v3 Card Grid Front-Page Infographic Builder ("THE WORLD IN ONE DAY")
Strictly implements /root/makefun/ni/v3argon/SPEC.md at 4000x4000 resolution (4x scale).
Pure Python + Pillow vector/line-art rendering. Deterministic output.
"""

from collections import Counter
import hashlib
import math
import os
from typing import Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Font Paths (TeX Gyre Termes = Times Serif, TeX Gyre Heros = Helvetica Sans)
# ---------------------------------------------------------------------------
FONT_SERIF_BOLD = "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyretermes-bold.otf"
FONT_SERIF_REG = "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyretermes-regular.otf"
FONT_SERIF_ITALIC = "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyretermes-italic.otf"
FONT_SERIF_BOLDITALIC = "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyretermes-bolditalic.otf"

FONT_SANS_BOLD = "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyreheros-bold.otf"
FONT_SANS_REG = "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyreheros-regular.otf"
FONT_SANS_ITALIC = "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyreheros-italic.otf"
FONT_SANSCN_BOLD = "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyreheroscn-bold.otf"

# ---------------------------------------------------------------------------
# 20 Stories (Strictly following SPEC.md table without any addition/deletion/modification)
# ---------------------------------------------------------------------------
STORIES: List[Dict[str, object]] = [
    {
        "id": 1,
        "region": "CLIMATE",
        "topic": "SUMMIT DIPLOMACY",
        "title": "COP31 ends without a deal",
        "lead": "Overnight plenary collapses past 03:00 as envoys reject final finance text.",
        "source": "Reuters, BBC, Guardian",
        "status": "CONFIRMED",
    },
    {
        "id": 2,
        "region": "MID EAST",
        "topic": "GULF ESCALATION",
        "title": "Iran claims strikes on two US bases",
        "lead": "State outlets allege missile salvo hit Patriot radar site in Bahrain.",
        "source": "Fars, Dawn",
        "status": "CLAIM",
    },
    {
        "id": 3,
        "region": "AT SEA",
        "topic": "MEDITERRANEAN FLEET",
        "title": "Russian frigate Merkury ablaze in Benghazi",
        "lead": "Port fire engulfs warship in eastern Libya as crews battle hull blaze.",
        "source": "AP, Al Jazeera, Reuters",
        "status": "CONFIRMED",
    },
    {
        "id": 4,
        "region": "AT SEA",
        "topic": "MARITIME SECURITY",
        "title": "Maltese tanker hit by suicide drone boat",
        "lead": "Uncrewed surface craft strikes starboard hull in sea lane; crew safe.",
        "source": "Reuters",
        "status": "CONFIRMED",
    },
    {
        "id": 5,
        "region": "EUROPE",
        "topic": "KYIV OBLAST STRIKE",
        "title": "Russian drones hit Dymer flats, 2 dead",
        "lead": "Overnight drone wave hits residential block across 19 Ukrainian sites.",
        "source": "Kyiv Independent",
        "status": "REPORTED",
    },
    {
        "id": 6,
        "region": "EUROPE",
        "topic": "ENERGY GRID CRISIS",
        "title": "Emergency blackouts across five regions",
        "lead": "Grid operators impose urgent outages after high-voltage line damage.",
        "source": "DTEK, Ukrenergo",
        "status": "CONFIRMED",
    },
    {
        "id": 7,
        "region": "MID EAST",
        "topic": "STRAIT OF HORMUZ",
        "title": "Two VLCCs crippled by mines in Hormuz",
        "lead": "Military statement alleges twin supertankers disabled in transit lane.",
        "source": "Iran military",
        "status": "CLAIM",
    },
    {
        "id": 8,
        "region": "MID EAST",
        "topic": "HUMANITARIAN TOLL",
        "title": "Gaza death toll rises to 74,742",
        "lead": "Health officials publish updated Sunday cumulative casualty registry.",
        "source": "Gaza health ministry",
        "status": "CONFIRMED",
    },
    {
        "id": 9,
        "region": "AFRICA",
        "topic": "SUDAN CONFLICT",
        "title": "Drones hit Khartoum homes and UN site, 4 dead",
        "lead": "Aerial munitions strike capital homes and humanitarian compound zone.",
        "source": "WarStrikes",
        "status": "REPORTED",
    },
    {
        "id": 10,
        "region": "AFRICA",
        "topic": "UN CASUALTY AUDIT",
        "title": "UN: drones cause nearly 3/4 of Sudan war deaths",
        "lead": "Audit finds loitering munitions cause almost 75% of civilian deaths.",
        "source": "Reuters",
        "status": "CONFIRMED",
    },
    {
        "id": 11,
        "region": "ASIA-PAC",
        "topic": "MONSOON DISASTER",
        "title": "Vietnam floods kill at least 41",
        "lead": "Central province deluge submerges homes as rescue boats evacuate towns.",
        "source": "multiple",
        "status": "CONFIRMED",
    },
    {
        "id": 12,
        "region": "ASIA-PAC",
        "topic": "SEISMIC TREMOR",
        "title": "Bangladesh quake kills 6, felt in Kolkata",
        "lead": "Shallow tremor topples rural masonry walls and shakes eastern India.",
        "source": "multiple",
        "status": "CONFIRMED",
    },
    {
        "id": 13,
        "region": "EUROPE",
        "city": "BRATISLAVA",
        "title": "Fico refuses EU's €450bn loan to Ukraine",
        "lead": "Slovak PM vows veto on joint EU debt package.",
        "source": "Reuters",
        "status": "CONFIRMED",
        "lat": 48.1,
        "lon": 17.1,
    },
    {
        "id": 14,
        "region": "EUROPE",
        "city": "BRUSSELS",
        "title": "Commission proposes €450bn loan for Kyiv",
        "lead": "EU executive unveils long-term defence facility.",
        "source": "Reuters",
        "status": "CONFIRMED",
        "lat": 50.8,
        "lon": 4.3,
    },
    {
        "id": 15,
        "region": "AMERICAS",
        "city": "WASHINGTON",
        "title": "US pushes for Russia-Ukraine peace by early Jan 2027",
        "lead": "Envoys press accelerated winter ceasefire timetable.",
        "source": "FT",
        "status": "REPORTED",
        "lat": 38.9,
        "lon": -77.0,
    },
    {
        "id": 16,
        "region": "EUROPE",
        "city": "PARIS",
        "title": "French Senate passes police shooting law",
        "lead": "Upper chamber approves revised vehicle-stop rules.",
        "source": "Reuters",
        "status": "CONFIRMED",
        "lat": 48.8,
        "lon": 2.3,
    },
    {
        "id": 17,
        "region": "AMERICAS",
        "city": "MEXICO CITY",
        "title": "Mexico captures FBI ten most wanted fugitive",
        "lead": "Federal forces detain high-priority suspect in raid.",
        "source": "Reuters",
        "status": "CONFIRMED",
        "lat": 19.4,
        "lon": -99.1,
    },
    {
        "id": 18,
        "region": "ASIA-PAC",
        "city": "HONG KONG",
        "title": "Hong Kong election turnout hits record",
        "lead": "Polling stations log record voter participation rate.",
        "source": "China Daily",
        "status": "CONFIRMED",
        "lat": 22.3,
        "lon": 114.2,
    },
    {
        "id": 19,
        "region": "ASIA-PAC",
        "city": "ISLAMABAD",
        "title": "Pakistan's first astronaut departs for Beijing",
        "lead": "Specialist leaves for orbital mission training in China.",
        "source": "APP",
        "status": "CONFIRMED",
        "lat": 33.7,
        "lon": 73.1,
    },
    {
        "id": 20,
        "region": "MID EAST",
        "city": "LAHJ",
        "title": "Missile hits Lahj health centre, about 10 dead",
        "lead": "Strike hits southern Yemen clinic, mass casualties.",
        "source": "Soth24",
        "status": "CLAIM",
        "lat": 13.0,
        "lon": 44.9,
    },
]

SCORE_BAR_ITEMS: List[Tuple[str, str]] = [
    ("74,742", "GAZA DEAD"),
    ("03:00", "COP31 DEADLINE"),
    ("148", "DRONES OVER UKRAINE"),
    ("41", "VIETNAM FLOOD DEAD"),
    ("450bn", "EU LOAN TO KYIV"),
    ("17", "PAKISTAN CREW RECOVERED"),
]

# 7 Region order and distinct editorial colors (深蓝/砖红/墨绿/紫/橙/青/灰)
REGION_ORDER: List[str] = [
    "EUROPE",
    "MID EAST",
    "ASIA-PAC",
    "AMERICAS",
    "AFRICA",
    "CLIMATE",
    "AT SEA",
]

REGION_COLORS: Dict[str, Tuple[int, int, int]] = {
    "EUROPE": (25, 74, 122),     # 深蓝 Deep Navy Blue
    "MID EAST": (166, 46, 38),   # 砖红 Brick Red
    "ASIA-PAC": (26, 94, 67),    # 墨绿 Forest Green
    "AMERICAS": (95, 52, 125),   # 紫 Royal Purple
    "AFRICA": (196, 92, 24),     # 橙 Deep Ochre Orange
    "CLIMATE": (18, 118, 130),   # 青 Deep Teal Cyan
    "AT SEA": (68, 84, 98),      # 灰 Slate Navy Grey
}

STATUS_COLORS: Dict[str, Tuple[int, int, int]] = {
    "CONFIRMED": (27, 117, 62),  # 绿底白字
    "REPORTED": (186, 114, 14),  # 琥珀
    "CLAIM": (184, 34, 34),      # 红
}

# Palette
BG_PAPER = (247, 244, 236)
CARD_BG = (253, 251, 246)
ILLUS_BG = (242, 238, 227)
INK_BLACK = (20, 24, 31)
INK_DARK = (40, 46, 56)
INK_GREY = (95, 102, 112)
INK_LIGHT_BORDER = (204, 198, 184)
ACCENT_RED = (184, 29, 19)
WHITE = (255, 255, 255)


# ---------------------------------------------------------------------------
# Font Cache & Hard Constraint Functions: fit() and no_overlap()
# ---------------------------------------------------------------------------
_FONT_CACHE: Dict[Tuple[str, int], ImageFont.FreeTypeFont] = {}


def get_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    key = (path, int(size))
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = ImageFont.truetype(path, int(size))
    return _FONT_CACHE[key]


def fit(
    text: str,
    font: ImageFont.FreeTypeFont,
    max_w: int,
    max_lines: int,
    min_px: int = 32,
    max_h: Optional[int] = None,
    line_gap_ratio: float = 0.14,
) -> Tuple[ImageFont.FreeTypeFont, List[str], Tuple[int, int, int]]:
    """
    Hard requirement fit(text, font, max_w, max_lines):
    Measures bounding box of `text` using `font`.
    If width > max_w or wrapped lines > max_lines (or height > max_h),
    shrinks font size by 1px per step down to `min_px` (8px * 4 = 32px at 4000x4000).
    Raises ValueError if still overflowing at `min_px`.
    Returns (fitted_font, lines, (block_w, block_h, line_step)).
    """
    font_path = getattr(font, "path", FONT_SANS_REG)
    start_size = int(getattr(font, "size", min_px))
    words = text.split()
    if not words:
        raise ValueError("fit() received empty text")

    for sz in range(start_size, min_px - 1, -1):
        f = get_font(font_path, sz)
        lines: List[str] = []
        current = words[0]
        possible = True

        # Check if first word alone exceeds max_w
        bb0 = f.getbbox(current)
        if (bb0[2] - bb0[0]) > max_w:
            continue

        for w in words[1:]:
            candidate = current + " " + w
            bb = f.getbbox(candidate)
            if (bb[2] - bb[0]) <= max_w:
                current = candidate
            else:
                lines.append(current)
                current = w
                bb_w = f.getbbox(current)
                if (bb_w[2] - bb_w[0]) > max_w:
                    possible = False
                    break
        if not possible:
            continue
        lines.append(current)

        if len(lines) > max_lines:
            continue

        max_line_w = 0
        line_heights: List[int] = []
        for ln in lines:
            bb = f.getbbox(ln)
            lw = bb[2] - bb[0]
            lh = bb[3] - bb[1]
            if lw > max_line_w:
                max_line_w = lw
            line_heights.append(lh)

        if max_line_w > max_w:
            continue

        ref_bb = f.getbbox("Ay")
        base_lh = max(ref_bb[3] - ref_bb[1], max(line_heights))
        gap = max(2, int(round(sz * line_gap_ratio)))
        line_step = base_lh + gap
        total_h = base_lh * len(lines) + gap * (len(lines) - 1)

        if max_h is not None and total_h > max_h:
            continue

        return f, lines, (max_line_w, total_h, line_step)

    raise ValueError(
        f"fit() failed: text={text!r} cannot fit in max_w={max_w}, "
        f"max_lines={max_lines}, max_h={max_h} even at min_px={min_px}"
    )


BoxEntry = Tuple[float, float, float, float, str, str]


def no_overlap(boxes: List[BoxEntry]) -> int:
    """
    Hard requirement no_overlap(boxes):
    Checks all pairs of registered bounding boxes (all text blocks + illustration blocks + number blocks).
    Raises RuntimeError immediately if any two boxes intersect.
    Returns total number of pairwise checks performed.
    """
    n = len(boxes)
    checks = 0
    for i in range(n):
        ax0, ay0, ax1, ay1, alabel, akind = boxes[i]
        if ax1 <= ax0 or ay1 <= ay0:
            raise RuntimeError(f"Invalid bounding box for {alabel}: {(ax0, ay0, ax1, ay1)}")
        for j in range(i + 1, n):
            bx0, by0, bx1, by1, blabel, bkind = boxes[j]
            checks += 1
            if max(ax0, bx0) < min(ax1, bx1) and max(ay0, by0) < min(ay1, by1):
                ix_w = min(ax1, bx1) - max(ax0, bx0)
                ix_h = min(ay1, by1) - max(ay0, by0)
                raise RuntimeError(
                    f"Collision detected between [{akind}] {alabel} {(ax0, ay0, ax1, ay1)} "
                    f"and [{bkind}] {blabel} {(bx0, by0, bx1, by1)} "
                    f"(intersection {ix_w:.1f}x{ix_h:.1f}px)"
                )
    return checks


def draw_fitted_text(
    draw: ImageDraw.ImageDraw,
    boxes: List[BoxEntry],
    text: str,
    font: ImageFont.FreeTypeFont,
    x: int,
    y: int,
    max_w: int,
    max_lines: int,
    fill: Tuple[int, int, int],
    label: str,
    min_px: int,
    align: str = "left",
    max_h: Optional[int] = None,
    line_gap_ratio: float = 0.14,
    register_box: bool = True,
) -> Tuple[int, int, int, int, ImageFont.FreeTypeFont]:
    """
    Runs fit(), draws each line with exact ink top-alignment, and registers
    the tight union ink bounding box into `boxes` for `no_overlap(boxes)`.
    """
    f, lines, (block_w, block_h, line_step) = fit(
        text, font, max_w, max_lines, min_px=min_px, max_h=max_h, line_gap_ratio=line_gap_ratio
    )
    union_x0: Optional[int] = None
    union_y0: Optional[int] = None
    union_x1: Optional[int] = None
    union_y1: Optional[int] = None

    cur_y = y
    for idx, ln in enumerate(lines):
        bb = f.getbbox(ln)
        lw = bb[2] - bb[0]
        lh = bb[3] - bb[1]
        if align == "center":
            draw_x = x + (max_w - lw) // 2 - bb[0]
        elif align == "right":
            draw_x = x + max_w - lw - bb[0]
        else:
            draw_x = x - bb[0]
        draw_y = cur_y - bb[1]
        draw.text((draw_x, draw_y), ln, font=f, fill=fill)

        ink_x0 = draw_x + bb[0]
        ink_y0 = draw_y + bb[1]
        ink_x1 = draw_x + bb[2]
        ink_y1 = draw_y + bb[3]

        union_x0 = ink_x0 if union_x0 is None else min(union_x0, ink_x0)
        union_y0 = ink_y0 if union_y0 is None else min(union_y0, ink_y0)
        union_x1 = ink_x1 if union_x1 is None else max(union_x1, ink_x1)
        union_y1 = ink_y1 if union_y1 is None else max(union_y1, ink_y1)

        cur_y += line_step

    assert union_x0 is not None and union_y0 is not None and union_x1 is not None and union_y1 is not None
    if register_box:
        boxes.append((union_x0, union_y0, union_x1, union_y1, label, "text"))
    return union_x0, union_y0, union_x1, union_y1, f


# ---------------------------------------------------------------------------
# 12 Bespoke Architectural / Technical Line-Art Illustrations (No Faces!)
# ---------------------------------------------------------------------------
def draw_card_illustration(
    draw: ImageDraw.ImageDraw,
    story_id: int,
    box: Tuple[int, int, int, int],
    accent: Tuple[int, int, int],
    S: float,
) -> None:
    """
    Draws clean 2px*S (=8px at 4000x4000) technical/editorial line-art inside `box`.
    Strictly NO human faces.
    """
    x0, y0, x1, y1 = box
    w = x1 - x0
    h = y1 - y0
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2
    lw = max(2, int(round(2.0 * S)))      # Primary line width: 2px -> 8px
    lw_thin = max(1, int(round(1.0 * S))) # Detail line width: 1px -> 4px
    ink = INK_BLACK

    # Illustration panel background & frame
    draw.rectangle([x0, y0, x1, y1], fill=ILLUS_BG, outline=INK_LIGHT_BORDER, width=lw_thin)

    # Subtle corner registration ticks
    tick = int(6 * S)
    draw.line([(x0 + lw, y0 + tick), (x0 + lw, y0 + lw), (x0 + tick, y0 + lw)], fill=accent, width=lw_thin)
    draw.line([(x1 - lw, y0 + tick), (x1 - lw, y0 + lw), (x1 - tick, y0 + lw)], fill=accent, width=lw_thin)
    draw.line([(x0 + lw, y1 - tick), (x0 + lw, y1 - lw), (x0 + tick, y1 - lw)], fill=accent, width=lw_thin)
    draw.line([(x1 - lw, y1 - tick), (x1 - lw, y1 - lw), (x1 - tick, y1 - lw)], fill=accent, width=lw_thin)

    if story_id == 1:
        # #1 COP31 ends without a deal: Fractured climate globe grid + suspended gavel & broken bar chart
        r = int(21 * S)
        gy = y0 + int(32 * S)
        draw.arc([cx - r, gy - r, cx + r, gy + r], 15, 165, fill=ink, width=lw)
        draw.arc([cx - r, gy - r, cx + r, gy + r], 195, 345, fill=accent, width=lw)
        draw.ellipse([cx - int(11 * S), gy - r, cx + int(11 * S), gy + r], outline=ink, width=lw_thin)
        draw.line([(cx - r, gy), (cx + r, gy)], fill=ink, width=lw_thin)
        # Suspended gavel / sounding block below
        by = y0 + int(68 * S)
        draw.rectangle([cx - int(18 * S), by, cx - int(2 * S), by + int(7 * S)], outline=ink, width=lw)
        draw.rectangle([cx + int(4 * S), by - int(6 * S), cx + int(20 * S), by + int(1 * S)], outline=accent, width=lw)
        draw.line([(cx - int(3 * S), by - int(10 * S)), (cx + int(5 * S), by + int(10 * S))], fill=accent, width=lw)
        # Rising CO2 bars at bottom
        base_y = y1 - int(8 * S)
        for idx, bh in enumerate([8, 12, 16, 21]):
            bx = x0 + int((11 + idx * 12) * S)
            draw.rectangle([bx, base_y - int(bh * S), bx + int(7 * S), base_y], outline=ink if idx < 3 else accent, width=lw)

    elif story_id == 2:
        # #2 Iran claims strikes on two US bases: Patriot phased-array radar + sweep arcs + incoming trajectories
        rx = x0 + int(18 * S)
        ry = y1 - int(14 * S)
        # Radar pedestal and tilted phased array panel
        draw.polygon(
            [(rx - int(8 * S), ry), (rx + int(12 * S), ry), (rx + int(4 * S), ry - int(14 * S))],
            outline=ink,
            width=lw,
        )
        draw.polygon(
            [
                (rx - int(6 * S), ry - int(14 * S)),
                (rx + int(14 * S), ry - int(34 * S)),
                (rx + int(22 * S), ry - int(28 * S)),
                (rx + int(2 * S), ry - int(8 * S)),
            ],
            outline=ink,
            width=lw,
        )
        # Radar emission arcs
        for rad in [18, 28, 38]:
            rr = int(rad * S)
            draw.arc([rx - rr, ry - int(26 * S) - rr, rx + rr, ry - int(26 * S) + rr], -65, 10, fill=accent, width=lw_thin)
        # Two incoming ballistic trajectories + target crosshairs
        draw.line([(x1 - int(10 * S), y0 + int(10 * S)), (cx + int(4 * S), cy + int(2 * S))], fill=accent, width=lw)
        draw.line([(x1 - int(6 * S), y0 + int(26 * S)), (cx + int(12 * S), cy + int(18 * S))], fill=accent, width=lw)
        for tx, ty in [(cx + int(4 * S), cy + int(2 * S)), (cx + int(12 * S), cy + int(18 * S))]:
            cr = int(5 * S)
            draw.ellipse([tx - cr, ty - cr, tx + cr, ty + cr], outline=accent, width=lw)

    elif story_id == 3:
        # #3 Russian frigate Merkury ablaze in Benghazi: Warship hull + mast + fire/smoke plumes
        wy = y0 + int(68 * S)
        # Frigate hull
        draw.polygon(
            [
                (x0 + int(6 * S), wy - int(10 * S)),
                (x1 - int(6 * S), wy - int(12 * S)),
                (x1 - int(12 * S), wy + int(4 * S)),
                (x0 + int(12 * S), wy + int(4 * S)),
            ],
            outline=ink,
            width=lw,
        )
        # Superstructure & radar mast
        draw.rectangle([cx - int(14 * S), wy - int(22 * S), cx + int(8 * S), wy - int(10 * S)], outline=ink, width=lw)
        draw.line([(cx - int(4 * S), wy - int(22 * S)), (cx - int(4 * S), wy - int(38 * S))], fill=ink, width=lw)
        draw.line([(cx - int(11 * S), wy - int(31 * S)), (cx + int(3 * S), wy - int(31 * S))], fill=ink, width=lw)
        # Geometric flame & smoke plumes rising amidships
        draw.polygon(
            [
                (cx + int(2 * S), wy - int(22 * S)),
                (cx + int(10 * S), y0 + int(12 * S)),
                (cx + int(14 * S), wy - int(26 * S)),
                (cx + int(22 * S), y0 + int(18 * S)),
                (cx + int(18 * S), wy - int(12 * S)),
            ],
            outline=accent,
            width=lw,
        )
        # Sea wave lines below
        for row in range(2):
            sy = wy + int((11 + row * 8) * S)
            draw.line([(x0 + int(8 * S), sy), (cx - int(4 * S), sy - int(3 * S)), (cx + int(8 * S), sy + int(3 * S)), (x1 - int(8 * S), sy)], fill=ink, width=lw_thin)

    elif story_id == 4:
        # #4 Maltese tanker hit by suicide drone boat: Tanker profile + USV drone boat + wake & impact burst
        ty = y0 + int(40 * S)
        # Tanker hull + bridge tower + deck pipeline
        draw.polygon(
            [
                (x0 + int(6 * S), ty),
                (x1 - int(8 * S), ty),
                (x1 - int(13 * S), ty + int(13 * S)),
                (x0 + int(10 * S), ty + int(13 * S)),
            ],
            outline=ink,
            width=lw,
        )
        draw.rectangle([x0 + int(12 * S), ty - int(14 * S), x0 + int(22 * S), ty], outline=ink, width=lw)
        # Impact starburst on starboard side
        ix, iy = cx + int(6 * S), ty + int(8 * S)
        for ang in range(0, 360, 45):
            rad = math.radians(ang)
            r_in, r_out = int(3 * S), int(11 * S)
            draw.line(
                [(ix + int(r_in * math.cos(rad)), iy + int(r_in * math.sin(rad))),
                 (ix + int(r_out * math.cos(rad)), iy + int(r_out * math.sin(rad)))],
                fill=accent,
                width=lw,
            )
        # Drone boat (USV) approaching from bottom right with wake lines
        ux, uy = x1 - int(22 * S), y1 - int(18 * S)
        draw.polygon([(ux - int(8 * S), uy - int(6 * S)), (ux + int(8 * S), uy), (ux - int(2 * S), uy + int(6 * S))], outline=accent, width=lw)
        draw.line([(ux - int(6 * S), uy - int(4 * S)), (ix + int(4 * S), iy + int(6 * S))], fill=accent, width=lw)

    elif story_id == 5:
        # #5 Russian drones hit Dymer flats, 2 dead: Multi-story apartment block + damaged corner + delta drone
        bx0, by0 = x0 + int(12 * S), y0 + int(36 * S)
        bx1, by1 = x1 - int(12 * S), y1 - int(8 * S)
        # Building outline with fractured top-right roof
        draw.polygon(
            [
                (bx0, by1),
                (bx0, by0),
                (bx1 - int(14 * S), by0),
                (bx1 - int(10 * S), by0 + int(10 * S)),
                (bx1 - int(3 * S), by0 + int(6 * S)),
                (bx1, by0 + int(16 * S)),
                (bx1, by1),
            ],
            outline=ink,
            width=lw,
        )
        # Window grid (3 cols x 4 rows)
        for r_idx in range(4):
            for c_idx in range(3):
                if r_idx == 0 and c_idx == 2:
                    continue
                wx = bx0 + int((6 + c_idx * 12) * S)
                wy = by0 + int((8 + r_idx * 11) * S)
                draw.rectangle([wx, wy, wx + int(7 * S), wy + int(6 * S)], outline=ink, width=lw_thin)
        # Delta-wing drone silhouette diving toward roof
        dx, dy = cx - int(4 * S), y0 + int(17 * S)
        draw.polygon([(dx + int(14 * S), dy + int(6 * S)), (dx - int(10 * S), dy - int(6 * S)), (dx - int(4 * S), dy + int(8 * S))], outline=accent, width=lw)

    elif story_id == 6:
        # #6 Emergency blackouts across five regions: High-voltage transmission pylon + snapped cables + bolt
        py_top = y0 + int(12 * S)
        py_bot = y1 - int(8 * S)
        # Pylon A-frame legs
        draw.line([(cx - int(4 * S), py_top), (cx - int(16 * S), py_bot)], fill=ink, width=lw)
        draw.line([(cx + int(4 * S), py_top), (cx + int(16 * S), py_bot)], fill=ink, width=lw)
        draw.line([(cx - int(4 * S), py_top), (cx + int(4 * S), py_top)], fill=ink, width=lw)
        # Cross-arms
        for ay, aw in [(y0 + int(26 * S), 22), (y0 + int(44 * S), 24)]:
            draw.line([(cx - int(aw * S), ay), (cx + int(aw * S), ay)], fill=ink, width=lw)
        # Lattice X-bracing
        draw.line([(cx - int(7 * S), y0 + int(26 * S)), (cx + int(10 * S), y0 + int(52 * S))], fill=ink, width=lw_thin)
        draw.line([(cx + int(7 * S), y0 + int(26 * S)), (cx - int(10 * S), y0 + int(52 * S))], fill=ink, width=lw_thin)
        draw.line([(cx - int(10 * S), y0 + int(52 * S)), (cx + int(14 * S), y0 + int(78 * S))], fill=ink, width=lw_thin)
        draw.line([(cx + int(10 * S), y0 + int(52 * S)), (cx - int(14 * S), y0 + int(78 * S))], fill=ink, width=lw_thin)
        # Lightning / outage bolt on right
        lx = x1 - int(14 * S)
        ly = y0 + int(52 * S)
        draw.line([(lx, ly), (lx - int(7 * S), ly + int(11 * S)), (lx - int(1 * S), ly + int(11 * S)), (lx - int(8 * S), ly + int(24 * S))], fill=accent, width=lw)

    elif story_id == 7:
        # #7 Two VLCCs crippled by mines in Hormuz: Strait shorelines + two naval horned mines + 2 tanker hulls
        # Top and bottom strait coastline contours
        draw.line([(x0 + int(4 * S), y0 + int(18 * S)), (cx - int(4 * S), y0 + int(26 * S)), (x1 - int(4 * S), y0 + int(14 * S))], fill=ink, width=lw)
        draw.line([(x0 + int(4 * S), y1 - int(14 * S)), (cx + int(4 * S), y1 - int(24 * S)), (x1 - int(4 * S), y1 - int(12 * S))], fill=ink, width=lw)
        # Two VLCC supertanker deck silhouettes (top-down naval chart view)
        for tx, ty in [(x0 + int(10 * S), y0 + int(36 * S)), (cx - int(2 * S), y0 + int(54 * S))]:
            draw.polygon(
                [(tx, ty), (tx + int(22 * S), ty), (tx + int(27 * S), ty + int(5 * S)), (tx + int(22 * S), ty + int(10 * S)), (tx, ty + int(10 * S))],
                outline=ink,
                width=lw,
            )
        # Two horned sea mines
        for mx, my in [(x1 - int(16 * S), y0 + int(38 * S)), (x0 + int(18 * S), y0 + int(62 * S))]:
            mr = int(6 * S)
            draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], outline=accent, width=lw)
            for ang in range(0, 360, 45):
                rad = math.radians(ang)
                draw.line(
                    [(mx + int(mr * math.cos(rad)), my + int(mr * math.sin(rad))),
                     (mx + int((mr + int(4 * S)) * math.cos(rad)), my + int((mr + int(4 * S)) * math.sin(rad)))],
                    fill=accent,
                    width=lw,
                )

    elif story_id == 8:
        # #8 Gaza death toll rises to 74,742: Broken concrete arches + ECG pulse line + tally monument grid
        base_y = y1 - int(12 * S)
        # Ruined arch pillars
        draw.line([(x0 + int(10 * S), base_y), (x0 + int(10 * S), y0 + int(34 * S))], fill=ink, width=lw)
        draw.line([(cx - int(2 * S), base_y), (cx - int(2 * S), y0 + int(34 * S))], fill=ink, width=lw)
        draw.arc([x0 + int(10 * S), y0 + int(22 * S), cx - int(2 * S), y0 + int(46 * S)], 180, 360, fill=ink, width=lw)
        # Broken second pillar
        draw.line([(cx + int(10 * S), base_y), (cx + int(10 * S), y0 + int(44 * S)), (x1 - int(10 * S), y0 + int(52 * S)), (x1 - int(10 * S), base_y)], fill=ink, width=lw)
        # ECG pulse line transitioning to flatline at top
        py = y0 + int(16 * S)
        draw.line(
            [
                (x0 + int(6 * S), py),
                (x0 + int(18 * S), py),
                (x0 + int(22 * S), py - int(8 * S)),
                (x0 + int(27 * S), py + int(10 * S)),
                (x0 + int(32 * S), py - int(5 * S)),
                (x0 + int(36 * S), py),
                (x1 - int(6 * S), py),
            ],
            fill=accent,
            width=lw,
        )

    elif story_id == 9:
        # #9 Drones hit Khartoum homes and UN site, 4 dead: Compound walls + UN communication mast + UAV above
        by = y1 - int(10 * S)
        # Compound wall & flat-roofed dwellings
        draw.rectangle([x0 + int(8 * S), by - int(24 * S), cx - int(2 * S), by], outline=ink, width=lw)
        draw.rectangle([cx + int(2 * S), by - int(32 * S), x1 - int(8 * S), by], outline=ink, width=lw)
        # UN site communications mast + globe laurel emblem ring
        mx = cx + int(14 * S)
        draw.line([(mx, by - int(32 * S)), (mx, y0 + int(36 * S))], fill=ink, width=lw)
        draw.ellipse([mx - int(7 * S), by - int(22 * S), mx + int(7 * S), by - int(8 * S)], outline=accent, width=lw)
        # Fixed-wing UAV loitering overhead + target beam
        ux, uy = x0 + int(22 * S), y0 + int(18 * S)
        draw.line([(ux - int(14 * S), uy), (ux + int(14 * S), uy)], fill=accent, width=lw)
        draw.line([(ux, uy - int(7 * S)), (ux, uy + int(9 * S))], fill=accent, width=lw)
        draw.line([(ux - int(5 * S), uy + int(9 * S)), (ux + int(5 * S), uy + int(9 * S))], fill=accent, width=lw)
        draw.line([(ux, uy + int(11 * S)), (x0 + int(19 * S), by - int(26 * S))], fill=accent, width=lw_thin)

    elif story_id == 10:
        # #10 UN: drones cause nearly 3/4 of Sudan war deaths: 3/4 (270 deg) ring gauge + drone blueprint inside
        r_out = int(23 * S)
        r_in = int(16 * S)
        gy = cy - int(4 * S)
        # Full background ring
        draw.ellipse([cx - r_out, gy - r_out, cx + r_out, gy + r_out], outline=INK_LIGHT_BORDER, width=lw_thin)
        # 3/4 (270 degree) heavy arc (-90 to 180)
        draw.arc([cx - r_out, gy - r_out, cx + r_out, gy + r_out], -90, 180, fill=accent, width=lw * 2)
        draw.ellipse([cx - r_in, gy - r_in, cx + r_in, gy + r_in], outline=ink, width=lw_thin)
        # Drone silhouette inside ring
        draw.line([(cx - int(10 * S), gy), (cx + int(10 * S), gy)], fill=ink, width=lw)
        draw.line([(cx, gy - int(8 * S)), (cx, gy + int(9 * S))], fill=ink, width=lw)
        draw.line([(cx - int(4 * S), gy + int(8 * S)), (cx + int(4 * S), gy + int(8 * S))], fill=ink, width=lw)
        # "3/4" geometric bar meter at bottom
        my = y1 - int(14 * S)
        for seg in range(4):
            sx = x0 + int((10 + seg * 12) * S)
            draw.rectangle(
                [sx, my, sx + int(9 * S), my + int(6 * S)],
                fill=accent if seg < 3 else None,
                outline=accent if seg < 3 else ink,
                width=lw_thin,
            )

    elif story_id == 11:
        # #11 Vietnam floods kill at least 41: Submerged gabled roofs + flood depth ruler + waves & rain
        # Flood depth gauge on left edge
        gx = x0 + int(10 * S)
        draw.line([(gx, y0 + int(14 * S)), (gx, y1 - int(10 * S))], fill=accent, width=lw)
        for tk in range(6):
            ty = y0 + int((18 + tk * 12) * S)
            draw.line([(gx, ty), (gx + int(6 * S), ty)], fill=accent, width=lw)
        # Gabled house roof protruding above rising floodwaters
        rx = cx + int(4 * S)
        ry = y0 + int(44 * S)
        draw.polygon([(rx - int(18 * S), ry + int(14 * S)), (rx, ry), (rx + int(18 * S), ry + int(14 * S))], outline=ink, width=lw)
        # Layered flood wave lines across bottom half
        for w_idx in range(3):
            wy = y0 + int((60 + w_idx * 11) * S)
            pts = []
            for step in range(7):
                px = x0 + int((18 + step * 7) * S)
                py = wy + (int(3 * S) if step % 2 == 0 else -int(3 * S))
                pts.append((px, py))
            draw.line(pts, fill=accent if w_idx == 0 else ink, width=lw)
        # Diagonal monsoon rain streaks at top
        for r_idx in range(4):
            sx = x0 + int((22 + r_idx * 10) * S)
            draw.line([(sx + int(4 * S), y0 + int(12 * S)), (sx, y0 + int(26 * S))], fill=ink, width=lw_thin)

    elif story_id == 12:
        # #12 Bangladesh quake kills 6, felt in Kolkata: Seismograph waveform + concentric epicentre shock rings
        # Seismograph trace across top half
        sy = y0 + int(28 * S)
        trace = [
            (x0 + int(6 * S), sy),
            (x0 + int(16 * S), sy - int(3 * S)),
            (x0 + int(21 * S), sy + int(7 * S)),
            (x0 + int(27 * S), sy - int(16 * S)),
            (cx, sy + int(18 * S)),
            (cx + int(6 * S), sy - int(20 * S)),
            (cx + int(12 * S), sy + int(12 * S)),
            (cx + int(17 * S), sy - int(6 * S)),
            (x1 - int(6 * S), sy),
        ]
        draw.line(trace, fill=accent, width=lw)
        # Concentric epicentre wave rings at bottom + fault fracture line
        ey = y0 + int(70 * S)
        for rad in [7, 14, 21]:
            rr = int(rad * S)
            draw.ellipse([cx - rr, ey - int(rr * 0.65), cx + rr, ey + int(rr * 0.65)], outline=ink if rad > 7 else accent, width=lw)
        draw.line([(cx - int(18 * S), ey - int(12 * S)), (cx, ey), (cx + int(16 * S), ey + int(12 * S))], fill=accent, width=lw)


# ---------------------------------------------------------------------------
# Section 7 Left: World Map with 7 Colored Regions & Markers 13-20
# ---------------------------------------------------------------------------
def draw_world_map_section(
    draw: ImageDraw.ImageDraw,
    boxes: List[BoxEntry],
    map_box: Tuple[int, int, int, int],
    map_stories: List[Dict[str, object]],
    S: float,
    min_px: int,
) -> None:
    """
    Draws the Section 7 World Map (occupying ~470px logical width on the left),
    colored by the 7 regions, and marks stories 13-20 with non-overlapping
    numbered pins + city labels.
    """
    x0, y0, x1, y1 = map_box
    lw = max(2, int(round(2.0 * S)))
    lw_thin = max(1, int(round(1.0 * S)))

    # Outer card container for map
    draw.rectangle([x0, y0, x1, y1], fill=CARD_BG, outline=INK_BLACK, width=lw)

    # Map Top Header Strip
    hdr_h = int(24 * S)
    draw.rectangle([x0, y0, x1, y0 + hdr_h], fill=INK_BLACK)
    f_hdr = get_font(FONT_SANS_BOLD, int(10 * S))
    draw_fitted_text(
        draw,
        boxes,
        "GLOBAL DISPATCH MAP · REGIONAL ZONES & LOCATIONS 13–20",
        f_hdr,
        x0 + int(10 * S),
        y0 + int(6 * S),
        (x1 - x0) - int(20 * S),
        1,
        WHITE,
        "map_header_title",
        min_px=min_px,
    )

    # Inner ocean viewport
    pad = int(6 * S)
    leg_h = int(22 * S)
    mx0 = x0 + pad
    my0 = y0 + hdr_h + pad
    mx1 = x1 - pad
    my1 = y1 - leg_h - pad
    mw = mx1 - mx0
    mh = my1 - my0

    OCEAN_BG = (232, 239, 243)
    draw.rectangle([mx0, my0, mx1, my1], fill=OCEAN_BG, outline=INK_LIGHT_BORDER, width=lw_thin)

    # Graticule lines (latitude & longitude grid)
    for frac in [0.2, 0.4, 0.6, 0.8]:
        gx = int(mx0 + mw * frac)
        gy = int(my0 + mh * frac)
        draw.line([(gx, my0), (gx, my1)], fill=(212, 222, 228), width=lw_thin)
        draw.line([(mx0, gy), (mx1, gy)], fill=(212, 222, 228), width=lw_thin)

    def ll_to_xy(lon: float, lat: float) -> Tuple[int, int]:
        # Equirectangular projection cropped to lon [-135, 155], lat [-45, 72]
        nx = (lon - (-135.0)) / (155.0 - (-135.0))
        ny = (72.0 - lat) / (72.0 - (-45.0))
        nx = max(0.03, min(0.97, nx))
        ny = max(0.04, min(0.96, ny))
        return int(mx0 + nx * mw), int(my0 + ny * mh)

    def tint(rgb: Tuple[int, int, int], alpha: float = 0.38) -> Tuple[int, int, int]:
        return (
            int(OCEAN_BG[0] * (1 - alpha) + rgb[0] * alpha),
            int(OCEAN_BG[1] * (1 - alpha) + rgb[1] * alpha),
            int(OCEAN_BG[2] * (1 - alpha) + rgb[2] * alpha),
        )

    # Stylized continent / region polygons colored by the 7 regions
    region_polys: List[Tuple[str, List[Tuple[float, float]]]] = [
        # AMERICAS (North & South America)
        (
            "AMERICAS",
            [
                (-128, 62), (-95, 64), (-62, 52), (-75, 35), (-82, 24),
                (-98, 18), (-84, 9), (-105, 22), (-124, 48),
            ],
        ),
        (
            "AMERICAS",
            [
                (-80, 9), (-60, 10), (-36, -6), (-48, -28), (-68, -42),
                (-74, -18), (-80, -2),
            ],
        ),
        # EUROPE
        (
            "EUROPE",
            [
                (-9, 37), (-8, 48), (2, 52), (10, 62), (32, 66),
                (40, 56), (36, 45), (24, 38), (12, 38),
            ],
        ),
        # AFRICA
        (
            "AFRICA",
            [
                (-16, 16), (-6, 34), (11, 36), (32, 30), (49, 11),
                (40, -15), (22, -34), (12, -18), (8, 4), (-12, 7),
            ],
        ),
        # MID EAST
        (
            "MID EAST",
            [
                (34, 31), (36, 38), (48, 38), (60, 26), (54, 15),
                (43, 12), (35, 22),
            ],
        ),
        # ASIA-PAC (South/East/SE Asia + Oceania)
        (
            "ASIA-PAC",
            [
                (62, 26), (52, 42), (75, 56), (132, 54), (142, 38),
                (122, 22), (104, 10), (96, 18), (78, 8), (68, 22),
            ],
        ),
        (
            "ASIA-PAC",
            [
                (114, -22), (132, -13), (150, -22), (146, -37), (116, -34),
            ],
        ),
        # CLIMATE (Global Polar/Equatorial Climate Belt Zone)
        (
            "CLIMATE",
            [
                (-54, 62), (-22, 65), (-18, 70), (-48, 70),
            ],
        ),
        # AT SEA (Mediterranean & Red Sea/Hormuz Naval Corridor)
        (
            "AT SEA",
            [
                (0, 32), (33, 32), (35, 36), (2, 37),
            ],
        ),
    ]

    for reg_name, coords in region_polys:
        pts = [ll_to_xy(lon, lat) for lon, lat in coords]
        base_col = REGION_COLORS[reg_name]
        draw.polygon(pts, fill=tint(base_col, 0.40), outline=base_col, width=lw_thin)

    # Subtle watermark region names on the ocean/continents (non-overlapping background)
    # Now place numbered pins 13-20 with leader lines to their exact geographic lat/lon!
    # Custom distinct callout positions (nx, ny in map viewport [0..1]) so pins 13-20
    # and their city labels are well-spaced and pass no_overlap(boxes) with big margins.
    callout_slots: Dict[int, Tuple[float, float, str]] = {
        15: (0.14, 0.30, "WASHINGTON"),
        17: (0.10, 0.62, "MEXICO CITY"),
        16: (0.37, 0.14, "PARIS"),
        14: (0.37, 0.31, "BRUSSELS"),
        13: (0.53, 0.14, "BRATISLAVA"),
        20: (0.50, 0.66, "LAHJ"),
        19: (0.69, 0.34, "ISLAMABAD"),
        18: (0.76, 0.62, "HONG KONG"),
    }

    pin_sz = int(20 * S)
    f_pin = get_font(FONT_SANS_BOLD, int(11 * S))
    f_city = get_font(FONT_SANSCN_BOLD, int(8.5 * S))

    for st in map_stories:
        sid = int(st["id"])
        reg = str(st["region"])
        col = REGION_COLORS[reg]
        lat = float(st["lat"])
        lon = float(st["lon"])
        gx, gy = ll_to_xy(lon, lat)

        fx, fy, city_name = callout_slots[sid]
        px = int(mx0 + fx * mw)
        py = int(my0 + fy * mh)

        # Leader line from exact geographic coordinate to pin box
        draw.line([(gx, gy), (px + pin_sz // 2, py + pin_sz // 2)], fill=col, width=lw)
        dot_r = int(3.5 * S)
        draw.ellipse([gx - dot_r, gy - dot_r, gx + dot_r, gy + dot_r], fill=col, outline=WHITE, width=lw_thin)

        # Pin Number Square (registered as 编号块!)
        p_box = (px, py, px + pin_sz, py + pin_sz)
        draw.rectangle(list(p_box), fill=col, outline=WHITE, width=lw_thin)
        boxes.append((p_box[0], p_box[1], p_box[2], p_box[3], f"map_pin_num_{sid}", "number"))

        # Centered number inside pin (do not double-register inside its own number block)
        num_str = str(sid)
        nbb = f_pin.getbbox(num_str)
        nw, nh = nbb[2] - nbb[0], nbb[3] - nbb[1]
        draw.text(
            (px + (pin_sz - nw) // 2 - nbb[0], py + (pin_sz - nh) // 2 - nbb[1]),
            num_str,
            font=f_pin,
            fill=WHITE,
        )

        # City label badge right next to the pin (registered as 文本块!)
        lbl_x = px + pin_sz + int(3 * S)
        lbl_max_w = int(68 * S)
        cbb = f_city.getbbox(city_name)
        cw = cbb[2] - cbb[0]
        ch = cbb[3] - cbb[1]
        pad_x = int(3 * S)
        pad_y = int(2 * S)
        pill_x0 = lbl_x
        pill_y0 = py + (pin_sz - (ch + 2 * pad_y)) // 2
        pill_x1 = pill_x0 + cw + 2 * pad_x
        pill_y1 = pill_y0 + ch + 2 * pad_y
        draw.rectangle([pill_x0, pill_y0, pill_x1, pill_y1], fill=WHITE, outline=col, width=lw_thin)

        draw_fitted_text(
            draw,
            boxes,
            city_name,
            f_city,
            pill_x0 + pad_x,
            pill_y0 + pad_y,
            lbl_max_w,
            1,
            INK_BLACK,
            f"map_city_label_{sid}",
            min_px=min_px,
        )

    # Bottom 7-region mini legend strip inside map card
    ly0 = my1 + int(4 * S)
    seg_w = mw / len(REGION_ORDER)
    f_leg = get_font(FONT_SANSCN_BOLD, int(8 * S))
    for idx, reg in enumerate(REGION_ORDER):
        sx0 = int(mx0 + idx * seg_w) + int(1 * S)
        sx1 = int(mx0 + (idx + 1) * seg_w) - int(1 * S)
        sy0 = ly0
        sy1 = y1 - int(4 * S)
        draw.rectangle([sx0, sy0, sx1, sy1], fill=REGION_COLORS[reg])
        draw_fitted_text(
            draw,
            boxes,
            reg,
            f_leg,
            sx0 + int(2 * S),
            sy0 + int(3 * S),
            (sx1 - sx0) - int(4 * S),
            1,
            WHITE,
            f"map_legend_{reg}",
            min_px=min_px,
            align="center",
        )


# ---------------------------------------------------------------------------
# Main Render Pipeline
# ---------------------------------------------------------------------------
def build_infographic(canvas_size: int = 4000) -> Tuple[Image.Image, Dict[str, object]]:
    """
    Renders the complete front-page infographic at `canvas_size x canvas_size`
    (default 4000x4000 -> scale factor S = 4.0 relative to 1000x1000 SPEC grid).
    Enforces fit() on every text block and no_overlap(boxes) across all elements.
    """
    assert len(STORIES) == 20, f"Expected 20 stories, got {len(STORIES)}"
    S = canvas_size / 1000.0
    min_px = int(round(8 * S))  # 8px -> 32px at 4000x4000
    lw_main = max(2, int(round(2.0 * S)))
    lw_thin = max(1, int(round(1.0 * S)))

    img = Image.new("RGB", (canvas_size, canvas_size), BG_PAPER)
    draw = ImageDraw.Draw(img)
    boxes: List[BoxEntry] = []

    # Outer grid alignment rails: x = 18..982 (width 964 -> 3856px at 4000x4000)
    X_LEFT = int(round(18 * S))
    X_RIGHT = int(round(982 * S))
    CONTENT_W = X_RIGHT - X_LEFT  # 964 * S = 3856px

    # =========================================================================
    # 1. 顶部条 (Top Bar: y = 6..32, height 26px -> 104px, font 11px -> 44px ALL CAPS)
    # =========================================================================
    top_y0 = int(round(6 * S))
    top_y1 = int(round(32 * S))
    draw.rectangle([X_LEFT, top_y0, X_RIGHT, top_y1], fill=INK_BLACK)

    f_top = get_font(FONT_SANS_BOLD, int(round(11 * S)))
    top_text_y = top_y0 + int(round(7.5 * S))
    draw_fitted_text(
        draw,
        boxes,
        "THE WORLD IN ONE DAY",
        f_top,
        X_LEFT + int(round(10 * S)),
        top_text_y,
        int(round(240 * S)),
        1,
        WHITE,
        "top_bar_left",
        min_px=min_px,
        align="left",
    )
    draw_fitted_text(
        draw,
        boxes,
        "20 STORIES · 7 REGIONS · EVERY ONE DATED SUNDAY 22 NOVEMBER 2026",
        f_top,
        X_LEFT + int(round(260 * S)),
        top_text_y,
        CONTENT_W - int(round(270 * S)),
        1,
        (238, 228, 202),
        "top_bar_right",
        min_px=min_px,
        align="right",
    )

    # =========================================================================
    # 2. 超大日期 + 双色饰线 (Date 86px->344px bold serif, y 30..150, black 3px + red 1px)
    # =========================================================================
    f_date = get_font(FONT_SERIF_BOLD, int(round(86 * S)))
    date_max_w = int(round(980 * S))
    date_x = (canvas_size - date_max_w) // 2
    date_y = int(round(48 * S))
    draw_fitted_text(
        draw,
        boxes,
        "Sunday 22 November 2026",
        f_date,
        date_x,
        date_y,
        date_max_w,
        1,
        INK_BLACK,
        "hero_date",
        min_px=min_px,
        align="center",
    )

    # Bicolor decorative rule (黑 3px + 红 1px, spanning full width)
    rule_black_y0 = int(round(145 * S))
    rule_black_y1 = rule_black_y0 + int(round(3 * S))
    rule_red_y0 = rule_black_y1 + int(round(2 * S))
    rule_red_y1 = rule_red_y0 + max(1, int(round(1 * S)))
    draw.rectangle([X_LEFT, rule_black_y0, X_RIGHT, rule_black_y1], fill=INK_BLACK)
    draw.rectangle([X_LEFT, rule_red_y0, X_RIGHT, rule_red_y1], fill=ACCENT_RED)

    # =========================================================================
    # 3. 单行概要 (Red italic 15px -> 60px)
    # =========================================================================
    f_summary = get_font(FONT_SERIF_BOLDITALIC, int(round(15 * S)))
    summary_y = int(round(161 * S))
    summary_text = (
        "COP31 puts its final deal to the vote · "
        "Iran claims Patriot radar hit in Bahrain · "
        "Russia's overnight drones hit 19 sites in Ukraine"
    )
    draw_fitted_text(
        draw,
        boxes,
        summary_text,
        f_summary,
        X_LEFT,
        summary_y,
        CONTENT_W,
        1,
        ACCENT_RED,
        "red_summary_line",
        min_px=min_px,
        align="center",
    )

    # =========================================================================
    # 4. 记分条 (6 Cells, y ~ 190..244, Big number 30px -> 120px bold + label 9px -> 36px)
    # =========================================================================
    score_y0 = int(round(190 * S))
    score_y1 = int(round(245 * S))
    draw.rectangle([X_LEFT, score_y0, X_RIGHT, score_y1], fill=CARD_BG, outline=INK_BLACK, width=lw_main)

    cell_w = CONTENT_W / len(SCORE_BAR_ITEMS)
    f_score_num = get_font(FONT_SERIF_BOLD, int(round(30 * S)))
    f_score_lbl = get_font(FONT_SANSCN_BOLD, int(round(9 * S)))

    for idx, (num_txt, lbl_txt) in enumerate(SCORE_BAR_ITEMS):
        cx0 = int(round(X_LEFT + idx * cell_w))
        cx1 = int(round(X_LEFT + (idx + 1) * cell_w))
        if idx > 0:
            draw.line([(cx0, score_y0), (cx0, score_y1)], fill=INK_LIGHT_BORDER, width=lw_main)

        # Top accent bar per score cell
        draw.rectangle([cx0 + int(4 * S), score_y0 + int(3 * S), cx1 - int(4 * S), score_y0 + int(6 * S)], fill=ACCENT_RED if idx in (0, 2) else INK_BLACK)

        inner_w = (cx1 - cx0) - int(round(12 * S))
        inner_x = cx0 + int(round(6 * S))

        draw_fitted_text(
            draw,
            boxes,
            num_txt,
            f_score_num,
            inner_x,
            score_y0 + int(round(11 * S)),
            inner_w,
            1,
            INK_BLACK if idx != 0 else ACCENT_RED,
            f"score_num_{idx}",
            min_px=min_px,
            align="center",
        )
        draw_fitted_text(
            draw,
            boxes,
            lbl_txt,
            f_score_lbl,
            inner_x,
            score_y0 + int(round(40 * S)),
            inner_w,
            1,
            INK_GREY,
            f"score_lbl_{idx}",
            min_px=min_px,
            align="center",
        )

    # =========================================================================
    # 5. 七色区域条 (y = 253..273, height 20px -> 80px, dynamically counted from STORIES!)
    # =========================================================================
    region_counts: Counter = Counter(str(s["region"]) for s in STORIES)
    total_counted = sum(region_counts[r] for r in REGION_ORDER)
    if total_counted != len(STORIES):
        raise RuntimeError(f"Region count mismatch: {total_counted} != {len(STORIES)}")

    reg_y0 = int(round(253 * S))
    reg_y1 = reg_y0 + int(round(20 * S))  # Exact 20px * S (= 80px)
    reg_seg_w = CONTENT_W / len(REGION_ORDER)
    f_reg_bar = get_font(FONT_SANS_BOLD, int(round(10 * S)))

    for idx, reg_name in enumerate(REGION_ORDER):
        rx0 = int(round(X_LEFT + idx * reg_seg_w)) + (int(round(1.5 * S)) if idx > 0 else 0)
        rx1 = int(round(X_LEFT + (idx + 1) * reg_seg_w)) - (int(round(1.5 * S)) if idx < len(REGION_ORDER) - 1 else 0)
        draw.rectangle([rx0, reg_y0, rx1, reg_y1], fill=REGION_COLORS[reg_name])

        cnt = region_counts[reg_name]
        reg_label = f"{reg_name} {cnt}"
        draw_fitted_text(
            draw,
            boxes,
            reg_label,
            f_reg_bar,
            rx0 + int(round(4 * S)),
            reg_y0 + int(round(5 * S)),
            (rx1 - rx0) - int(round(8 * S)),
            1,
            WHITE,
            f"region_bar_{reg_name}",
            min_px=min_px,
            align="center",
        )

    # =========================================================================
    # 6. 编号卡片区 (12 Cards, 3 cols x 4 rows, y = 281..705)
    #    Col width = 316px, Card height = 100px, Gap = 8px
    # =========================================================================
    CARD_W = int(round(316 * S))
    CARD_H = int(round(100 * S))
    CARD_GAP = int(round(8 * S))
    CARDS_Y0 = int(round(281 * S))

    f_card_num = get_font(FONT_SANS_BOLD, int(round(17 * S)))
    f_card_tag = get_font(FONT_SANS_BOLD, int(round(8 * S)))
    f_card_title = get_font(FONT_SERIF_BOLD, int(round(17 * S)))
    f_card_lead = get_font(FONT_SANS_REG, int(round(11 * S)))
    f_card_source = get_font(FONT_SERIF_ITALIC, int(round(9 * S)))
    f_card_status = get_font(FONT_SANS_BOLD, int(round(8 * S)))

    card_stories = STORIES[:12]
    for idx, st in enumerate(card_stories):
        sid = int(st["id"])
        col_idx = idx % 3
        row_idx = idx // 3

        cx0 = X_LEFT + col_idx * (CARD_W + CARD_GAP)
        cy0 = CARDS_Y0 + row_idx * (CARD_H + CARD_GAP)
        cx1 = cx0 + CARD_W
        cy1 = cy0 + CARD_H

        reg = str(st["region"])
        reg_col = REGION_COLORS[reg]
        status = str(st["status"])
        status_col = STATUS_COLORS[status]

        # Card background & top region accent rule
        draw.rectangle([cx0, cy0, cx1, cy1], fill=CARD_BG, outline=INK_LIGHT_BORDER, width=lw_thin)
        draw.rectangle([cx0, cy0, cx1, cy0 + int(round(2.5 * S))], fill=reg_col)

        # 6a. Left Number Square (32x32 -> 128x128, solid region color, white bold 17px -> 68px)
        num_sz = int(round(32 * S))
        nx0 = cx0 + int(round(3 * S))
        ny0 = cy0 + int(round(4 * S))
        nx1 = nx0 + num_sz
        ny1 = ny0 + num_sz
        draw.rectangle([nx0, ny0, nx1, ny1], fill=reg_col)
        boxes.append((nx0, ny0, nx1, ny1, f"card_num_box_{sid}", "number"))

        num_txt = str(sid)
        nbb = f_card_num.getbbox(num_txt)
        nw, nh = nbb[2] - nbb[0], nbb[3] - nbb[1]
        draw.text(
            (nx0 + (num_sz - nw) // 2 - nbb[0], ny0 + (num_sz - nh) // 2 - nbb[1]),
            num_txt,
            font=f_card_num,
            fill=WHITE,
        )

        # Decorative vertical region index spine below the 32x32 number square (non-overlapping)
        spine_x = nx0 + num_sz // 2
        draw.line([(spine_x, ny1 + int(4 * S)), (spine_x, cy1 - int(6 * S))], fill=reg_col, width=lw_main)
        draw.ellipse(
            [spine_x - int(3 * S), cy1 - int(10 * S), spine_x + int(3 * S), cy1 - int(4 * S)],
            fill=reg_col,
        )

        # 6b. Illustration Band (64x96 vertical strip -> 256x384, 2px->8px line art, no faces)
        il_w = int(round(64 * S))
        il_h = int(round(94 * S))
        il_x0 = nx1 + int(round(3 * S))
        il_y0 = cy0 + int(round(4 * S))
        il_x1 = il_x0 + il_w
        il_y1 = il_y0 + il_h
        draw_card_illustration(draw, sid, (il_x0, il_y0, il_x1, il_y1), reg_col, S)
        boxes.append((il_x0, il_y0, il_x1, il_y1, f"card_illus_box_{sid}", "illustration"))

        # 6c. Right Text Column inside Card (width = 207px -> 828px)
        tx0 = il_x1 + int(round(4 * S))
        tx_max_w = (cx1 - int(round(3 * S))) - tx0

        # Region + Topic Small Tag (8px -> 32px ALL CAPS, grey)
        tag_text = f"{reg} · {st['topic']}"
        _, _, _, tag_y1, _ = draw_fitted_text(
            draw,
            boxes,
            tag_text,
            f_card_tag,
            tx0,
            cy0 + int(round(4 * S)),
            tx_max_w,
            1,
            INK_GREY,
            f"card_tag_{sid}",
            min_px=min_px,
        )

        # Bold Serif Title (17px -> 68px, max 2 lines)
        title_y0 = tag_y1 + int(round(2.5 * S))
        _, _, _, title_y1, _ = draw_fitted_text(
            draw,
            boxes,
            str(st["title"]),
            f_card_title,
            tx0,
            title_y0,
            tx_max_w,
            2,
            INK_BLACK,
            f"card_title_{sid}",
            min_px=min_px,
            max_h=int(round(36 * S)),
            line_gap_ratio=0.10,
        )

        # Lead / Summary (11px -> 44px, max 2 lines)
        lead_y0 = title_y1 + int(round(3 * S))
        _, _, _, lead_y1, _ = draw_fitted_text(
            draw,
            boxes,
            str(st["lead"]),
            f_card_lead,
            tx0,
            lead_y0,
            tx_max_w,
            2,
            INK_DARK,
            f"card_lead_{sid}",
            min_px=min_px,
            max_h=int(round(25 * S)),
            line_gap_ratio=0.12,
        )

        # Bottom Row: Source (9px -> 36px italic) on left + Status Badge (8px -> 32px white on green/amber/red) on right
        footer_y = cy1 - int(round(13 * S))

        # Measure status pill first so source max_w never collides with status pill
        s_bb = f_card_status.getbbox(status)
        sw = s_bb[2] - s_bb[0]
        sh = s_bb[3] - s_bb[1]
        pill_pad_x = int(round(4 * S))
        pill_pad_y = int(round(2 * S))
        pill_w = sw + 2 * pill_pad_x
        pill_h = sh + 2 * pill_pad_y
        pill_x1 = cx1 - int(round(4 * S))
        pill_x0 = pill_x1 - pill_w
        pill_y1 = cy1 - int(round(3 * S))
        pill_y0 = pill_y1 - pill_h

        draw.rectangle([pill_x0, pill_y0, pill_x1, pill_y1], fill=status_col)
        draw_fitted_text(
            draw,
            boxes,
            status,
            f_card_status,
            pill_x0 + pill_pad_x,
            pill_y0 + pill_pad_y,
            sw + int(2 * S),
            1,
            WHITE,
            f"card_status_{sid}",
            min_px=min_px,
        )

        source_max_w = (pill_x0 - tx0) - int(round(6 * S))
        draw_fitted_text(
            draw,
            boxes,
            str(st["source"]),
            f_card_source,
            tx0,
            footer_y,
            source_max_w,
            1,
            INK_GREY,
            f"card_source_{sid}",
            min_px=min_px,
        )

    # =========================================================================
    # 7. 下半部 (y = 713..962):
    #    Left: Map (width ~464px logical) with 7 regions & markers 13-20
    #    Right: Numbered List 13-20 (width ~492px logical), 8 items, max 2 lines each
    # =========================================================================
    LOWER_Y0 = int(round(713 * S))
    LOWER_Y1 = int(round(962 * S))
    MAP_W = int(round(460 * S))
    LOWER_GAP = int(round(8 * S))

    map_box = (X_LEFT, LOWER_Y0, X_LEFT + MAP_W, LOWER_Y1)
    list_stories = STORIES[12:]
    draw_world_map_section(draw, boxes, map_box, list_stories, S, min_px=min_px)

    # Right Numbered List 13-20 Container
    LX0 = X_LEFT + MAP_W + LOWER_GAP
    LX1 = X_RIGHT
    LW = LX1 - LX0
    draw.rectangle([LX0, LOWER_Y0, LX1, LOWER_Y1], fill=CARD_BG, outline=INK_BLACK, width=lw_main)

    # Right List Header Strip
    lhdr_h = int(round(24 * S))
    draw.rectangle([LX0, LOWER_Y0, LX1, LOWER_Y0 + lhdr_h], fill=INK_BLACK)
    f_lhdr = get_font(FONT_SANS_BOLD, int(round(10 * S)))
    draw_fitted_text(
        draw,
        boxes,
        "NUMBERED DISPATCH BRIEFINGS 13–20 · CITY, HEADLINE, SOURCE & VERIFICATION",
        f_lhdr,
        LX0 + int(round(10 * S)),
        LOWER_Y0 + int(round(6 * S)),
        LW - int(round(20 * S)),
        1,
        WHITE,
        "list_header_title",
        min_px=min_px,
    )

    # 8 Rows for Stories 13-20
    rows_y0 = LOWER_Y0 + lhdr_h + int(round(2 * S))
    rows_h = (LOWER_Y1 - int(round(2 * S))) - rows_y0
    row_step = rows_h / len(list_stories)  # ~27.6px logical -> 110.5px physical per item

    f_list_num = get_font(FONT_SANS_BOLD, int(round(13 * S)))
    f_list_title = get_font(FONT_SERIF_BOLD, int(round(12 * S)))
    f_list_meta = get_font(FONT_SANS_REG, int(round(9 * S)))
    f_list_source = get_font(FONT_SERIF_ITALIC, int(round(9 * S)))
    f_list_status = get_font(FONT_SANS_BOLD, int(round(8 * S)))

    for idx, st in enumerate(list_stories):
        sid = int(st["id"])
        ry0 = int(round(rows_y0 + idx * row_step))
        ry1 = int(round(rows_y0 + (idx + 1) * row_step))
        reg = str(st["region"])
        reg_col = REGION_COLORS[reg]
        status = str(st["status"])
        status_col = STATUS_COLORS[status]
        city = str(st["city"]).upper()

        if idx > 0:
            draw.line([(LX0 + int(6 * S), ry0), (LX1 - int(6 * S), ry0)], fill=INK_LIGHT_BORDER, width=lw_thin)

        # Left Number Square (22x22 logical -> 88x88 physical)
        lnum_sz = int(round(22 * S))
        lnx0 = LX0 + int(round(6 * S))
        lny0 = ry0 + ((ry1 - ry0) - lnum_sz) // 2
        lnx1 = lnx0 + lnum_sz
        lny1 = lny0 + lnum_sz
        draw.rectangle([lnx0, lny0, lnx1, lny1], fill=reg_col)
        boxes.append((lnx0, lny0, lnx1, lny1, f"list_num_box_{sid}", "number"))

        s_num = str(sid)
        nbb = f_list_num.getbbox(s_num)
        nw, nh = nbb[2] - nbb[0], nbb[3] - nbb[1]
        draw.text(
            (lnx0 + (lnum_sz - nw) // 2 - nbb[0], lny0 + (lnum_sz - nh) // 2 - nbb[1]),
            s_num,
            font=f_list_num,
            fill=WHITE,
        )

        # Status Badge on far right of row
        st_bb = f_list_status.getbbox(status)
        stw, sth = st_bb[2] - st_bb[0], st_bb[3] - st_bb[1]
        p_px = int(round(4 * S))
        p_py = int(round(2 * S))
        pw = stw + 2 * p_px
        ph = sth + 2 * p_py
        px1 = LX1 - int(round(8 * S))
        px0 = px1 - pw
        py0 = ry0 + ((ry1 - ry0) - ph) // 2
        py1 = py0 + ph
        draw.rectangle([px0, py0, px1, py1], fill=status_col)
        draw_fitted_text(
            draw,
            boxes,
            status,
            f_list_status,
            px0 + p_px,
            py0 + p_py,
            stw + int(2 * S),
            1,
            WHITE,
            f"list_status_{sid}",
            min_px=min_px,
        )

        # Line 1: ALL-CAPS CITY + Bold Title (12px -> 48px bold)
        ltx0 = lnx1 + int(round(6 * S))
        ltx_max_w = (px0 - ltx0) - int(round(8 * S))
        headline_line = f"{city} — {st['title']}"
        _, _, _, l1_y1, _ = draw_fitted_text(
            draw,
            boxes,
            headline_line,
            f_list_title,
            ltx0,
            ry0 + int(round(3 * S)),
            ltx_max_w,
            1,
            INK_BLACK,
            f"list_title_{sid}",
            min_px=min_px,
        )

        # Line 2: Region tag + concise lead + Source (9px -> 36px italic)
        src_txt = f"Source: {st['source']}"
        src_bb = f_list_source.getbbox(src_txt)
        src_w = (src_bb[2] - src_bb[0]) + int(round(4 * S))
        src_x0 = px0 - int(round(8 * S)) - src_w

        line2_y = l1_y1 + int(round(2.5 * S))
        draw_fitted_text(
            draw,
            boxes,
            src_txt,
            f_list_source,
            src_x0,
            line2_y,
            src_w,
            1,
            INK_GREY,
            f"list_source_{sid}",
            min_px=min_px,
            align="right",
        )

        meta_max_w = (src_x0 - ltx0) - int(round(6 * S))
        meta_txt = f"[{reg}] {st['lead']}"
        draw_fitted_text(
            draw,
            boxes,
            meta_txt,
            f_list_meta,
            ltx0,
            line2_y,
            meta_max_w,
            1,
            INK_DARK,
            f"list_meta_{sid}",
            min_px=min_px,
        )

    # =========================================================================
    # 8. 底部 DATE CHECK (Deep black bar, white text 9px -> 36px)
    # =========================================================================
    dc_y0 = int(round(968 * S))
    dc_y1 = int(round(994 * S))
    draw.rectangle([X_LEFT, dc_y0, X_RIGHT, dc_y1], fill=INK_BLACK)

    # Red badge on left of DATE CHECK bar
    badge_w = int(round(92 * S))
    draw.rectangle([X_LEFT, dc_y0, X_LEFT + badge_w, dc_y1], fill=ACCENT_RED)
    f_dc_bold = get_font(FONT_SANS_BOLD, int(round(9 * S)))
    draw_fitted_text(
        draw,
        boxes,
        "DATE CHECK",
        f_dc_bold,
        X_LEFT + int(round(6 * S)),
        dc_y0 + int(round(8 * S)),
        badge_w - int(round(12 * S)),
        1,
        WHITE,
        "date_check_badge",
        min_px=min_px,
        align="center",
    )

    dc_msg = (
        "STRICTLY 2026-11-22 (SUNDAY 22 NOVEMBER 2026) EVENTS ONLY · "
        "EXCLUDES FRI/SAT OLD NEWS, RETRACTIONS & DUPLICATES · "
        "MULTI-OUTLET REPORTS OF SAME EVENT MERGED"
    )
    draw_fitted_text(
        draw,
        boxes,
        dc_msg,
        f_dc_bold,
        X_LEFT + badge_w + int(round(10 * S)),
        dc_y0 + int(round(8 * S)),
        CONTENT_W - badge_w - int(round(20 * S)),
        1,
        WHITE,
        "date_check_text",
        min_px=min_px,
        align="left",
    )

    # =========================================================================
    # Enforce Hard Collision Check across ALL Text, Illustration, and Number Boxes
    # =========================================================================
    pairwise_checks = no_overlap(boxes)

    stats = {
        "canvas_size": canvas_size,
        "total_stories": len(STORIES),
        "cards_count": len(card_stories),
        "list_count": len(list_stories),
        "region_counts": {r: region_counts[r] for r in REGION_ORDER},
        "total_boxes": len(boxes),
        "text_boxes": sum(1 for b in boxes if b[5] == "text"),
        "illustration_boxes": sum(1 for b in boxes if b[5] == "illustration"),
        "number_boxes": sum(1 for b in boxes if b[5] == "number"),
        "pairwise_checks": pairwise_checks,
    }
    return img, stats


def main() -> None:
    out_dir = os.path.dirname(os.path.abspath(__file__))
    entry_path = os.path.join(out_dir, "entry.png")
    preview_path = os.path.join(out_dir, "preview-300.png")

    max_bytes = 8 * 1024 * 1024  # 8 MB hard limit
    max_pixels = 16_000_000      # 16M pixel ceiling

    chosen_img: Optional[Image.Image] = None
    chosen_stats: Optional[Dict[str, object]] = None

    for candidate_size in [4000, 3600, 3200]:
        if candidate_size * candidate_size > max_pixels:
            raise RuntimeError(f"Resolution {candidate_size}x{candidate_size} exceeds 16M pixels")
        img, stats = build_infographic(canvas_size=candidate_size)
        img.save(entry_path, format="PNG", optimize=True, compress_level=9)
        fsize = os.path.getsize(entry_path)
        if fsize <= max_bytes:
            chosen_img = img
            chosen_stats = stats
            chosen_stats["file_bytes"] = fsize
            break

    if chosen_img is None or chosen_stats is None:
        raise RuntimeError("Failed to produce entry.png under 8MB limit even at 3200x3200")

    # Generate 300x300 preview from main image
    preview = chosen_img.resize((300, 300), resample=Image.Resampling.LANCZOS)
    preview.save(preview_path, format="PNG", optimize=True, compress_level=9)

    with open(entry_path, "rb") as f:
        entry_md5 = hashlib.md5(f.read()).hexdigest()
    with open(preview_path, "rb") as f:
        preview_md5 = hashlib.md5(f.read()).hexdigest()

    print(f"ENTRY_PATH={entry_path}")
    print(f"RESOLUTION={chosen_stats['canvas_size']}x{chosen_stats['canvas_size']}")
    print(f"PIXELS={int(chosen_stats['canvas_size']) ** 2}")
    print(f"BYTES={chosen_stats['file_bytes']} ({int(chosen_stats['file_bytes']) / (1024 * 1024):.3f} MiB)")
    print(f"ENTRY_MD5={entry_md5}")
    print(f"PREVIEW_MD5={preview_md5}")
    print(f"STORIES={chosen_stats['total_stories']} (cards={chosen_stats['cards_count']}, list={chosen_stats['list_count']})")
    print(f"REGION_COUNTS={chosen_stats['region_counts']}")
    print(
        f"COLLISION_CHECK=PASSED (boxes={chosen_stats['total_boxes']}: "
        f"text={chosen_stats['text_boxes']}, illus={chosen_stats['illustration_boxes']}, "
        f"num={chosen_stats['number_boxes']}; pairwise_checks={chosen_stats['pairwise_checks']}, overlaps=0)"
    )


if __name__ == "__main__":
    main()
