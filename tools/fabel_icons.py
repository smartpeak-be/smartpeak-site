"""Pictograms for /fabels-en-feiten/, written as small SVGs in assets/img/fabels/.

Run: python3 tools/fabel_icons.py
Each icon is a rounded plate with a line drawing, in the site colours. They are decorative
(the text says everything), so the page uses them with alt="".
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "img" / "fabels"
INK, LEAF, LEAF_DEEP, LAGOON, RED = "#1f272e", "#17c15c", "#0b7a42", "#1aa5b6", "#c2412d"
PLATE, PLATE_LINE = "#e9f8ef", "#bfe9cf"


def svg(body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" width="96" height="96" '
            f'fill="none" stroke="{INK}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">'
            f'<rect x="3" y="3" width="90" height="90" rx="22" fill="{PLATE}" stroke="{PLATE_LINE}" stroke-width="3"/>'
            f'{body}</svg>\n')


def slash():
    return f'<path d="M24 72 72 24" stroke="{RED}" stroke-width="5"/>'


def battery(x, y, w, h, fill=None, level=None):
    out = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4"/>'
    out += f'<path d="M{x + w / 2 - 5} {y - 4}h10"/>'
    if level:
        lh = (h - 8) * level
        out += f'<rect x="{x + 4}" y="{y + h - 4 - lh}" width="{w - 8}" height="{lh}" rx="2" fill="{fill or LEAF}" stroke="none"/>'
    return out


def house(x=26, y=30, w=44, h=36):
    return (f'<path d="M{x - 4} {y + 4} {x + w / 2} {y - 16} {x + w + 4} {y + 4}"/>'
            f'<path d="M{x} {y}v{h}h{w}v-{h}"/>')


ICONS = {
    # Bij een stroompanne heb ik stroom: a bolt, crossed out
    "stroompanne": f'<path d="M52 18 34 50h14l-6 28 22-36H50l6-24z" fill="#fff"/>' + slash(),
    # Onafhankelijk van het net: house still tied to a pylon
    "onafhankelijk": house(16, 44, 30, 26) + '<path d="M60 74 68 24l8 50M62 40h12M60 52h16"/>'
                     f'<path d="M46 56c8 0 14-8 20-24" stroke="{LAGOON}"/>',
    # Winter: snowflake
    "winter": '<path d="M48 22v52M25.5 35 70.5 61M25.5 61 70.5 35"/>'
              '<path d="M42 26l6 6 6-6M42 70l6-6 6 6M28 42l8-1-3-7M68 54l-8 1 3 7M28 54l8 1-3 7M68 42l-8-1 3-7"/>',
    # Bewolking: sun behind a cloud
    "bewolking": f'<circle cx="38" cy="38" r="10" stroke="{LEAF_DEEP}"/>'
                 f'<path d="M38 18v5M18 38h5M24 24l3.5 3.5M52 24l-3.5 3.5" stroke="{LEAF_DEEP}"/>'
                 '<path d="M34 70h32a10 10 0 0 0 0-20 14 14 0 0 0-27-3 9 9 0 0 0-5 23z" fill="#fff"/>',
    # Zonder zonnepanelen: battery with a price curve
    "zonder-panelen": battery(22, 32, 24, 40, LEAF, .55) +
                      f'<path d="M54 62l8-10 7 6 9-16" stroke="{LAGOON}"/><path d="M52 70h28"/>',
    # Groter is beter: three batteries of growing size
    "groter": battery(18, 54, 14, 20, LEAF, .7) + battery(40, 42, 16, 32, LEAF, .7) + battery(64, 28, 16, 46, "#cfd8d5", .35),
    # LFP kan niet branden: flame with smoke
    "brand": '<path d="M48 76c-12 0-18-8-18-17 0-10 8-14 10-24 6 4 8 10 8 14 3-3 4-7 4-11 7 6 14 13 14 21 0 9-6 17-18 17z" fill="#fff"/>'
             '<path d="M62 22c4 3-4 6 0 9M72 26c4 3-4 6 0 9" stroke="#7b8682"/>',
    # Overal plaatsen: a door (escape route) with an arrow
    "plaatsing": '<path d="M30 74V22h26v52"/><circle cx="50" cy="50" r="2" fill="' + INK + '"/>'
                 f'<path d="M60 48h18M70 40l8 8-8 8" stroke="{LAGOON}"/><path d="M22 74h40"/>',
    # Keuring: clipboard with a check
    "keuring": '<rect x="28" y="24" width="40" height="52" rx="5" fill="#fff"/><path d="M40 20h16v8H40z" fill="' + PLATE + '"/>'
               f'<path d="M37 52l8 8 15-17" stroke="{LEAF_DEEP}" stroke-width="5"/>',
    # Stekkerbatterij: a plug
    "stekker": '<path d="M38 18v14M58 18v14"/><path d="M30 32h36v10a18 18 0 0 1-36 0z" fill="#fff"/><path d="M48 60v16"/>',
    # Injecteren levert altijd iets op: arrow to the grid with a minus
    "injecteren": house(16, 44, 28, 26) + f'<path d="M50 54h22M64 46l8 8-8 8" stroke="{LAGOON}"/>'
                  f'<path d="M66 28h12" stroke="{RED}" stroke-width="5"/>',
    # Premie: gift tag, crossed out
    "premie": '<path d="M30 36h36v34H30z" fill="#fff"/><path d="M26 28h44v8H26zM48 28v42"/>'
              '<path d="M48 28c-4-8-14-8-12-1M48 28c4-8 14-8 12-1"/>' + slash(),
    # Capaciteitstarief: a gauge
    "piek": '<path d="M22 62a26 26 0 0 1 52 0"/><path d="M22 62h52"/>'
            f'<path d="M48 62 62 42" stroke="{RED}" stroke-width="5"/><circle cx="48" cy="62" r="4" fill="{INK}"/>'
            '<path d="M30 46l4 3M48 36v5M66 46l-4 3"/>',
    # Recyclage: two arrows in a circle
    "recyclage": f'<path d="M30 44a20 20 0 0 1 34-10" stroke="{LEAF_DEEP}"/><path d="M66 24v12H54" stroke="{LEAF_DEEP}"/>'
                 f'<path d="M66 52a20 20 0 0 1-34 10" stroke="{LEAF_DEEP}"/><path d="M30 72V60h12" stroke="{LEAF_DEEP}"/>',
    # Levensduur: shield with a check (warranty)
    "levensduur": '<path d="M48 20l24 8v18c0 16-10 26-24 30-14-4-24-14-24-30V28z" fill="#fff"/>'
                  f'<path d="M37 48l8 8 14-15" stroke="{LEAF_DEEP}" stroke-width="5"/>',
    # Wagen volladen: a car next to a small battery
    "wagen": '<path d="M16 62v-8l6-12h28l8 12h4v8z" fill="#fff"/><circle cx="26" cy="64" r="5" fill="#fff"/><circle cx="52" cy="64" r="5" fill="#fff"/>'
             + battery(68, 48, 14, 22, LEAF, .3),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, body in ICONS.items():
        (OUT / f"{name}.svg").write_text(svg(body), encoding="utf-8")
    print(f"wrote {len(ICONS)} icons")


if __name__ == "__main__":
    main()
