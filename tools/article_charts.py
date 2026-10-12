"""Charts and diagrams for articles, written as SVG in assets/img/grafieken/.

Run: python3 tools/article_charts.py && python3 tools/render_svg.py
(render_svg.py turns each SVG into a WebP with the site font, for <img> and link previews.)
All figures here are explanatory illustrations; the articles say so where values are fictitious.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "img" / "grafieken"
INK, SOFT, LINE = "#1f272e", "#4b5661", "#e3ebe8"
LEAF, LEAF_DEEP, LAGOON, LAGOON_DEEP, NIGHT = "#17c15c", "#0b7a42", "#1aa5b6", "#0a6a78", "#172129"
RED = "#c2412d"
W, H = 1600, 900


def svg(body, title, subtitle):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            f'font-family="Instrument Sans, Segoe UI, sans-serif">\n'
            f'<rect width="100%" height="100%" fill="#ffffff"/>\n'
            f'<text x="150" y="82" font-size="40" font-weight="650" fill="{INK}">{title}</text>\n'
            f'<text x="150" y="128" font-size="27" fill="{SOFT}">{subtitle}</text>\n{body}</svg>\n')


def text(x, y, s, size=25, color=SOFT, weight=None, anchor=None):
    extra = (f' font-weight="{weight}"' if weight else "") + (f' text-anchor="{anchor}"' if anchor else "")
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}"{extra}>{s}</text>\n'


def axes(x0, x1, y_of, ticks, unit):
    out = ""
    for v in ticks:
        y = y_of(v)
        out += f'<line x1="{x0}" x2="{x1}" y1="{y:.1f}" y2="{y:.1f}" stroke="{LINE}" stroke-width="2"/>\n'
        label = f"{v:g}".replace(".", ",")
        out += text(x0 - 22, y + 9, f"{label}{unit}", anchor="end")
    return out


def hours_axis(x_of, y, step=3):
    return "".join(text(x_of(h), y, f"{h}u", anchor="middle") for h in range(0, 25, step))


def dynamic_price_day():
    """Illustrative day-ahead energy price over one sunny day, with battery charge/discharge windows."""
    prices = [0.11, 0.10, 0.09, 0.09, 0.10, 0.12, 0.16, 0.20, 0.18, 0.12, 0.06, 0.01,
              -0.02, -0.03, -0.01, 0.03, 0.09, 0.17, 0.24, 0.26, 0.21, 0.16, 0.13, 0.12]
    x0, x1, ytop, ybot = 170, 1530, 190, 740
    lo, hi = -0.08, 0.36
    x_of = lambda h: x0 + (x1 - x0) * h / 24
    y_of = lambda p: ybot - (ybot - ytop) * (p - lo) / (hi - lo)
    body = axes(x0, x1, y_of, [-0.05, 0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35], " €")
    # windows
    body += f'<rect x="{x_of(11):.1f}" y="{ytop}" width="{x_of(15) - x_of(11):.1f}" height="{ybot - ytop}" fill="#e9f8ef"/>\n'
    body += f'<rect x="{x_of(17):.1f}" y="{ytop}" width="{x_of(21) - x_of(17):.1f}" height="{ybot - ytop}" fill="#e3f4f6"/>\n'
    body += text((x_of(11) + x_of(15)) / 2, ytop + 36, "Batterij laadt", 26, LEAF_DEEP, 650, "middle")
    body += text((x_of(11) + x_of(15)) / 2, ytop + 68, "goedkoop of negatief", 23, LEAF_DEEP, None, "middle")
    body += text((x_of(17) + x_of(21)) / 2, ytop + 36, "Batterij ontlaadt", 26, LAGOON_DEEP, 650, "middle")
    body += text((x_of(17) + x_of(21)) / 2, ytop + 68, "duur uur vermijden", 23, LAGOON_DEEP, None, "middle")
    # zero line emphasised
    body += f'<line x1="{x0}" x2="{x1}" y1="{y_of(0):.1f}" y2="{y_of(0):.1f}" stroke="{SOFT}" stroke-width="2.5"/>\n'
    # step line (hourly prices)
    pts = []
    for h, p in enumerate(prices):
        pts += [f"{x_of(h):.1f},{y_of(p):.1f}", f"{x_of(h + 1):.1f},{y_of(p):.1f}"]
    body += f'<polyline points="{" ".join(pts)}" fill="none" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>\n'
    body += text(x_of(13.5), y_of(-0.03) + 40, "negatieve prijs", 23, RED, 600, "middle")
    body += hours_axis(x_of, 790)
    body += text(150, 850, "Voorbeeld met fictieve prijzen per kWh, enkel het energiedeel (zonder nettarieven en heffingen).", 23)
    return svg(body, "Een dag met dynamische prijzen", "De energieprijs verandert per uur of per kwartier, volgens de markt van de dag ervoor")


def box(x, y, w, h, label, sub=None, fill="#f3f7f5", stroke=LINE, color=INK):
    out = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{fill}" stroke="{stroke}" stroke-width="3"/>\n'
    if sub:
        out += text(x + w / 2, y + h / 2 - 4, label, 27, color, 650, "middle")
        out += text(x + w / 2, y + h / 2 + 30, sub, 22, SOFT if color == INK else color, None, "middle")
    else:
        out += text(x + w / 2, y + h / 2 + 9, label, 27, color, 650, "middle")
    return out


def arrow(x1, y1, x2, y2, color=INK, label=None, dashed=False):
    dash = ' stroke-dasharray="12 9"' if dashed else ""
    out = (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="5"{dash} '
           f'marker-end="url(#arrow-{color[1:]})"/>\n')
    if label:
        out += text((x1 + x2) / 2, min(y1, y2) - 14, label, 21, color, 600, "middle")
    return out


def markers(*colors):
    return "<defs>" + "".join(
        f'<marker id="arrow-{c[1:]}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>' for c in colors) + "</defs>\n"


def ac_dc_charging():
    body = markers(INK, LEAF_DEEP, RED)
    # Row 1: AC
    y1 = 230
    body += text(150, y1 - 20, "AC-laadpaal", 30, INK, 650)
    body += box(150, y1, 230, 120, "Zonnepanelen", "gelijkstroom")
    body += box(470, y1, 230, 120, "Omvormer", "naar wisselstroom")
    body += box(790, y1, 230, 120, "Verdeelkast", "huis en net")
    body += box(1110, y1, 230, 120, "Laadpaal", "7 tot 22 kW")
    body += box(1370, y1 + 150, 160, 100, "Wagen", None)
    body += arrow(380, y1 + 60, 462, y1 + 60)
    body += arrow(700, y1 + 60, 782, y1 + 60)
    body += arrow(1020, y1 + 60, 1102, y1 + 60)
    body += arrow(1225, y1 + 120, 1360, y1 + 196)
    body += box(790, y1 + 190, 230, 90, "Net", None, "#fdecea", "#f3c7c0", RED)
    body += arrow(905, y1 + 190, 905, y1 + 128, RED)
    body += text(905, y1 + 312, "levert bij wat de omvormer niet haalt: telt mee in je piek", 22, RED, 600, "middle")
    # Row 2: DC
    y2 = 640
    body += text(150, y2 - 20, "DC-laden vanuit het batterijsysteem", 30, INK, 650)
    body += box(150, y2, 230, 120, "Zonnepanelen", "gelijkstroom")
    body += box(470, y2, 230, 120, "Batterij", "gelijkstroom")
    body += box(790, y2, 330, 120, "DC-laadmodule", "geen omzetting naar AC", "#e9f8ef", "#bfe9cf")
    body += box(1370, y2 + 10, 160, 100, "Wagen", None)
    body += arrow(380, y2 + 60, 462, y2 + 60, LEAF_DEEP)
    body += arrow(700, y2 + 60, 782, y2 + 60, LEAF_DEEP)
    body += arrow(1120, y2 + 60, 1362, y2 + 60, LEAF_DEEP)
    body += text(1240, y2 + 160, "blijft aan de gelijkstroomkant van je installatie", 22, LEAF_DEEP, 600, "middle")
    return svg(body, "AC-laden of DC-laden: welke weg gaat de energie?", "Vereenvoudigd schema van een woning met zonnepanelen en een batterij")


def house(x, y, lit, label, sub, note):
    """A simple house with three circuits; lit is a list of 3 booleans."""
    out = f'<polygon points="{x},{y + 120} {x + 190},{y} {x + 380},{y + 120}" fill="#f3f7f5" stroke="{INK}" stroke-width="4"/>\n'
    out += f'<rect x="{x + 30}" y="{y + 120}" width="320" height="300" fill="#f3f7f5" stroke="{INK}" stroke-width="4"/>\n'
    names = ["Koelkast", "Verlichting", "Kookplaat"]
    for i, on in enumerate(lit):
        cy = y + 170 + i * 85
        fill = LEAF if on else "#cfd8d5"
        out += f'<circle cx="{x + 90}" cy="{cy}" r="22" fill="{fill}"/>\n'
        out += text(x + 128, cy + 9, names[i], 24, INK if on else "#7b8682")
    out += text(x + 190, y + 470, label, 28, INK, 650, "middle")
    out += text(x + 190, y + 506, sub, 23, SOFT, None, "middle")
    out += text(x + 190, y + 540, note, 23, SOFT, None, "middle")
    return out


def backup_options():
    body = house(150, 200, [False, False, False], "Zonder back-up", "alles valt uit, ook", "zonnepanelen en batterij")
    body += house(610, 200, [True, False, False], "Noodstopcontact", "één stopcontact aan het toestel", "voor een paar toestellen")
    body += house(1070, 200, [True, True, False], "Back-up-schakeling", "gekozen kringen blijven", "werken, los van het net")
    body += text(150, 850, "Vereenvoudigd: wat blijft werken tijdens een stroomonderbreking. Een volledige woning op back-up vraagt meer vermogen.", 23)
    return svg(body, "Stroomonderbreking: drie situaties", "Een batterij mag nooit stroom naar het net sturen; wat werkt, hangt af van de installatie")


def write(name, content):
    (OUT / f"{name}.svg").write_text(content, encoding="utf-8")
    print("wrote", name)


if __name__ == "__main__":
    write("dynamische-prijzen-dag", dynamic_price_day())
    write("ac-dc-laden", ac_dc_charging())
    write("back-up-opties", backup_options())
