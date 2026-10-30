"""Charts and diagrams for articles, written as SVG in assets/img/grafieken/.

Run: python3 tools/article_charts.py && python3 tools/render_svg.py
(render_svg.py turns each SVG into a WebP with the site font, for <img> and link previews.)
All figures here are explanatory illustrations; the articles say so where values are fictitious.
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "img" / "grafieken"
INK, SOFT, LINE = "#1f272e", "#4b5661", "#e3ebe8"
LEAF, LEAF_DEEP, LAGOON, LAGOON_DEEP, NIGHT = "#17c15c", "#0b7a42", "#1aa5b6", "#0a6a78", "#172129"
RED = "#c2412d"
W, H = 1600, 900


def svg(body, title, subtitle, sub_size=27):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            f'font-family="Instrument Sans, Segoe UI, sans-serif">\n'
            f'<rect width="100%" height="100%" fill="#ffffff"/>\n'
            f'<text x="150" y="82" font-size="40" font-weight="650" fill="{INK}">{title}</text>\n'
            f'<text x="150" y="128" font-size="{sub_size}" fill="{SOFT}">{subtitle}</text>\n{body}</svg>\n')


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
    body += box(1110, y1, 230, 120, "Laadpaal", "3,7 tot 11 kW")
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
    body += house(1070, 200, [True, True, False], "Back-upschakeling", "gekozen kringen blijven", "werken, los van het net")
    body += text(150, 850, "Vereenvoudigd: wat blijft werken tijdens een stroomonderbreking. Een volledige woning op back-up vraagt meer vermogen.", 23)
    return svg(body, "Stroomonderbreking: drie situaties", "Bij een stroomonderbreking mag een batterij geen stroom naar het net sturen; wat werkt, hangt af van de installatie", sub_size=22)


def grid_voltage_day():
    """Illustrative 10-minute average grid voltage on a sunny day at a crowded street, with trips at 253 V."""
    import math
    x0, x1, ytop, ybot = 170, 1530, 190, 740
    lo, hi = 224, 268
    x_of = lambda h: x0 + (x1 - x0) * (h - 5) / 17   # 5u .. 22u
    y_of = lambda v: ybot - (ybot - ytop) * (v - lo) / (hi - lo)
    body = axes(x0, x1, y_of, [225, 230, 235, 240, 245, 250, 255, 260, 265], " V")
    # limits
    for v, label, color, dash in ((253, "253 V: gemiddelde over 10 minuten (230 V + 10%)", RED, "16 10"),
                                  (264.5, "264,5 V: ogenblikkelijke grens (230 V + 15%)", SOFT, "6 8")):
        y = y_of(v)
        body += f'<line x1="{x0}" x2="{x1}" y1="{y:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="4" stroke-dasharray="{dash}"/>\n'
        body += text(x1, y - 14, label, 23, color, 600, "end")
    # voltage curve: rises with solar, falls back each time the inverter trips, then climbs again
    pts, trips = [], []
    h, tripped_until = 5.0, -1
    while h <= 22.0001:
        sun = max(0.0, math.sin(math.pi * (h - 6.5) / 14))
        v = 231 + 23.5 * sun ** 1.6
        if tripped_until > h:
            v -= 7.5
        elif v >= 253 and 11 <= h <= 15.5:
            trips.append(h)
            tripped_until = h + 0.55
            v = 253.2
        pts.append(f"{x_of(h):.1f},{y_of(v):.1f}")
        h += 1 / 6
    for t in trips:
        body += f'<rect x="{x_of(t):.1f}" y="{ytop}" width="{x_of(t + 0.55) - x_of(t):.1f}" height="{ybot - ytop}" fill="#fdecea"/>\n'
    body += f'<polyline points="{" ".join(pts)}" fill="none" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>\n'
    if trips:
        mid = (x_of(trips[0]) + x_of(trips[-1] + 0.55)) / 2
        body += text(mid, y_of(258.5), "omvormer schakelt af", 23, RED, 600, "middle")
    body += "".join(text(x_of(t), 790, f"{t}u", anchor="middle") for t in range(6, 23, 2))
    body += text(150, 850, "Voorbeeld met fictieve meetwaarden: netspanning op een zonnige dag in een straat met veel zonnepanelen.", 23)
    return svg(body, "Te hoge netspanning op een zonnige dag", "Komt het gemiddelde over 10 minuten boven 253 V, dan schakelt de omvormer even af")


def battery_size_trend():
    """Average capacity of newly connected home batteries in Flanders (Fluvius open data, via Solar Magazine)."""
    bars = [("2024", 9.1, "± 9 kWh"), ("2025", 11.5, "± 11,5 kWh"), ("2026*", 22.0, "± 22 kWh")]
    x0, x1, ytop, ybot = 170, 1530, 190, 740
    y_of = lambda v: ybot - (ybot - ytop) * v / 25
    body = axes(x0, x1, y_of, [0, 5, 10, 15, 20, 25], " kWh")
    slot = (x1 - x0) / len(bars)
    for i, (label, v, shown) in enumerate(bars):
        bx = x0 + slot * i + slot * 0.25
        bw = slot * 0.5
        color = LEAF if label.startswith("2026") else INK
        body += f'<rect x="{bx:.1f}" y="{y_of(v):.1f}" width="{bw:.1f}" height="{ybot - y_of(v):.1f}" rx="8" fill="{color}"/>\n'
        body += text(bx + bw / 2, y_of(v) - 18, shown, 30, INK, 650, "middle")
        body += text(bx + bw / 2, 790, label, 28, INK, 600, "middle")
    body += text(150, 828, "* januari tot mei 2026, voorlopig. Gemiddelden volgens Solar Magazine op basis van open data van Fluvius;", 22)
    body += text(150, 856, "2024 is een eigen schatting.", 22)
    return svg(body, "Nieuwe thuisbatterijen worden groter", "Gemiddelde opslagcapaciteit van nieuw aangesloten thuisbatterijen in Vlaanderen")


def zendure_mode_choice():
    body = markers(INK)
    rows = [("Vast contract", "één prijs, dag en nacht", "Zelfverbruik", "zonnestroom eerst zelf gebruiken, de batterij laadt enkel met zon"),
            ("Dag- en nachttarief", "goedkoper 's nachts en weekend", "Zelfverbruik of TOU", "TOU kan ook in de goedkope uren uit het net laden"),
            ("Dynamisch contract", "prijs per uur of kwartier", "ZENKI of TOU", "ZENKI plant zelf, bij TOU kies je zelf de prijszones")]
    body += text(150, 192, "Welk contract heb je?", 27, SOFT, 600)
    body += text(640, 192, "Begin met deze modus", 27, SOFT, 600)
    for i, (label, sub, mode, why) in enumerate(rows):
        y = 215 + i * 165
        body += box(150, y, 380, 125, label, sub)
        body += arrow(535, y + 62, 628, y + 62)
        body += box(640, y, 890, 125, mode, why, "#e9f8ef", "#bfe9cf", LEAF_DEEP)
    y = 720
    body += box(150, y, 680, 95, "Vaste routine of eigen sturing", "kies Aangepast: je eigen schema")
    body += box(850, y, 680, 95, "Liever niets instellen", "kies Auto: beslist zelf, geen extra instellingen")
    body += text(150, 868, "Vereenvoudigd. Zelfverbruik, ZENKI en TOU vragen een gekoppelde meter, zoals een P1-lezer op je digitale meter.", 23)
    return svg(body, "Welke Zendure-modus past bij jou?", "Je contract bepaalt meestal de beste start; wisselen kan altijd in de app")


def zendure_self_consumption():
    body = markers(LEAF_DEEP, INK)
    rows = [("Je zonnestroom gaat naar", LEAF_DEEP, [("1. Je huis", "eerst je eigen verbruik"), ("2. De batterij", "het overschot"),
                                                  ("3. Het net", "als injecteren toegelaten is")]),
            ("Je verbruik komt van", INK, [("1. De zonnepanelen", "wat ze op dat moment maken"), ("2. De batterij", "zolang ze lading heeft"),
                                           ("3. Het net", "pas als de rest niet volstaat")])]
    for r, (title, color, steps) in enumerate(rows):
        y = 240 + r * 250
        body += text(150, y - 22, title, 30, INK, 650)
        for i, (label, sub) in enumerate(steps):
            x = 150 + i * 470
            first = i == 0
            body += box(x, y, 400, 130, label, sub, "#e9f8ef" if first else "#f3f7f5", "#bfe9cf" if first else LINE,
                        LEAF_DEEP if first else INK)
            if i < 2:
                body += arrow(x + 405, y + 65, x + 462, y + 65, color)
    body += box(150, 690, 1340, 95, "De batterij laadt in deze modus enkel met zonnestroom, nooit uit het net", None, "#e9f8ef", "#bfe9cf", LEAF_DEEP)
    body += text(150, 850, "Volgorde volgens de beschrijving van Zendure bij de modi van HEMS 2.0 (juni 2026).", 23)
    return svg(body, "Zo verdeelt de modus Zelfverbruik je stroom", "Zonnestroom wordt eerst in huis gebruikt; de batterij vangt het verschil op")


def zendure_tou_zones():
    prices = [0.12, 0.11, 0.10, 0.10, 0.11, 0.13, 0.17, 0.21, 0.19, 0.13, 0.07, 0.03,
              0.01, 0.00, 0.02, 0.05, 0.10, 0.18, 0.25, 0.27, 0.22, 0.17, 0.14, 0.13]
    low, high = 0.08, 0.185
    x0, x1, ytop, ybot = 170, 1530, 190, 740
    lo, hi = -0.02, 0.32
    x_of = lambda h: x0 + (x1 - x0) * h / 24
    y_of = lambda p: ybot - (ybot - ytop) * (p - lo) / (hi - lo)
    body = f'<rect x="{x0}" y="{y_of(low):.1f}" width="{x1 - x0}" height="{ybot - y_of(low):.1f}" fill="#e9f8ef"/>\n'
    body += f'<rect x="{x0}" y="{ytop}" width="{x1 - x0}" height="{y_of(high) - ytop:.1f}" fill="#e3f4f6"/>\n'
    body += axes(x0, x1, y_of, [0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30], " €")
    for v, color in ((low, LEAF_DEEP), (high, LAGOON_DEEP)):
        body += f'<line x1="{x0}" x2="{x1}" y1="{y_of(v):.1f}" y2="{y_of(v):.1f}" stroke="{color}" stroke-width="3" stroke-dasharray="14 9"/>\n'
    pts = []
    for h, p in enumerate(prices):
        pts += [f"{x_of(h):.1f},{y_of(p):.1f}", f"{x_of(h + 1):.1f},{y_of(p):.1f}"]
    body += f'<polyline points="{" ".join(pts)}" fill="none" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>\n'
    body += text(x1 - 16, ytop + 40, "Hoog: de batterij ontlaadt", 26, LAGOON_DEEP, 650, "end")
    body += text(x_of(13), y_of(0.15), "Midden: zoals je instelt,", 23, SOFT, 600, "middle")
    body += text(x_of(13), y_of(0.15) + 32, "bv. een reserve bewaren", 23, SOFT, 600, "middle")
    body += text(x1 - 16, ybot - 22, "Laag: de batterij laadt, ook uit het net", 26, LEAF_DEEP, 650, "end")
    body += hours_axis(x_of, 790)
    body += text(150, 850, "Voorbeeld met fictieve prijzen per kWh. De grenzen voor laag en hoog kies je zelf in de app.", 23)
    return svg(body, "TOU-modus: sturen op prijszones", "Jij legt vast wanneer een prijs laag of hoog is; de batterij volgt die regels")


def sigen_settings_layers():
    body = text(150, 200, "1. Kies één werkmodus", 30, INK, 650)
    modes = [("Sigen AI", "plant op prijs en weer"), ("Zelfverbruik", "eigen zonnestroom eerst"),
             ("Tijdsturing", "jouw laad- en ontlaaduren"), ("Volledig injecteren", "zoveel mogelijk naar het net")]
    for i, (label, sub) in enumerate(modes):
        body += box(150 + i * 345, 225, 320, 120, label, sub, "#e9f8ef" if i < 3 else "#f3f7f5",
                    "#bfe9cf" if i < 3 else LINE, LEAF_DEEP if i < 3 else INK)
    body += text(150, 440, "2. Stel daarnaast in, los van de modus", 30, INK, 650)
    extra = [("Piekbeperking", "maximum dat je van het net haalt"), ("Back-up-reserve", "lading voor een stroompanne"),
             ("Injectielimiet", "maximum naar het net"), ("Je wagen laden", "snel of met zonne-overschot"),
             ("Slimme verbruikers", "toestellen op overschot")]
    for i, (label, sub) in enumerate(extra):
        x = 150 + (i % 3) * 460
        y = 465 + (i // 3) * 150
        body += box(x, y, 420, 120, label, sub, "#e3f4f6", "#b6e0e6", LAGOON_DEEP)
    body += text(150, 868, "Vereenvoudigd overzicht van de mySigen-app. Back-up vraagt een Sigen Energy Gateway.", 23)
    return svg(body, "Zo zit de mySigen-app in elkaar", "Eén modus bepaalt het dagelijkse gedrag; extra functies leggen grenzen en voorrang vast")


def sigen_peak_shaving():
    demand = [0.6, 0.7, 0.9, 1.4, 1.2, 2.6, 5.8, 6.2, 3.4, 1.8, 4.8, 4.6, 1.6, 1.1, 0.8, 0.7]  # per half hour, 16u-24u
    cap = 2.5
    x0, x1, ytop, ybot = 170, 1530, 190, 740
    lo, hi = 0, 7
    n = len(demand)
    x_of = lambda i: x0 + (x1 - x0) * i / n
    y_of = lambda v: ybot - (ybot - ytop) * (v - lo) / (hi - lo)
    body = axes(x0, x1, y_of, [0, 1, 2, 3, 4, 5, 6, 7], " kW")
    for i, v in enumerate(demand):
        grid = min(v, cap)
        body += f'<rect x="{x_of(i) + 4:.1f}" y="{y_of(grid):.1f}" width="{x_of(1) - x0 - 8:.1f}" height="{ybot - y_of(grid):.1f}" fill="{INK}"/>\n'
        if v > cap:
            body += f'<rect x="{x_of(i) + 4:.1f}" y="{y_of(v):.1f}" width="{x_of(1) - x0 - 8:.1f}" height="{y_of(cap) - y_of(v):.1f}" fill="{LAGOON}"/>\n'
    body += f'<line x1="{x0}" x2="{x1}" y1="{y_of(cap):.1f}" y2="{y_of(cap):.1f}" stroke="{RED}" stroke-width="4" stroke-dasharray="16 10"/>\n'
    body += text(x0 + 12, y_of(cap) - 14, "ingestelde maximale piek: 2,5 kW", 24, RED, 650)
    body += f'<rect x="170" y="200" width="26" height="26" fill="{LAGOON}"/>\n' + text(208, 222, "uit de batterij", 24, INK)
    body += f'<rect x="420" y="200" width="26" height="26" fill="{INK}"/>\n' + text(458, 222, "van het net", 24, INK)
    body += text(x_of(6.9), y_of(6.2) - 16, "koken", 23, SOFT, 600, "middle")
    body += text(x_of(10.9), y_of(4.8) - 16, "vaatwas en droogkast", 23, SOFT, 600, "middle")
    body += "".join(text(x_of(i), 790, f"{16 + i // 2}u", anchor="middle") for i in range(0, n + 1, 2))
    body += text(150, 850, "Voorbeeld met fictieve waarden voor één avond. Werkt zolang de batterij genoeg lading en vermogen heeft.", 23)
    return svg(body, "Piekbeperking: de batterij neemt de pieken over", "Wat boven je ingestelde maximum uitkomt, levert de batterij in plaats van het net")


def sigen_battery_levels():
    bx, bw, btop, bbot = 440, 260, 200, 780
    y_of = lambda pct: bbot - (bbot - btop) * pct / 100
    body = f'<rect x="{bx}" y="{btop - 1}" width="{bw}" height="{bbot - btop + 2}" rx="26" fill="#f3f7f5" stroke="{INK}" stroke-width="4"/>\n'
    body += f'<rect x="{bx + 95}" y="{btop - 30}" width="70" height="26" rx="6" fill="{INK}"/>\n'
    zones = [(0, 25, LAGOON, "Back-up-reserve of ontlaadgrens", "met een Gateway: blijft over voor een stroompanne"),
             (25, 95, LEAF, "Dagelijks gebruik", "de werkmodus en piekbeperking gebruiken dit deel"),
             (95, 100, "#cfd8d5", "Boven je laadgrens", "de batterij laadt niet verder dan je laadgrens")]
    for a, b, color, label, sub in zones:
        body += f'<rect x="{bx + 14}" y="{y_of(b) + 3:.1f}" width="{bw - 28}" height="{y_of(a) - y_of(b) - 6:.1f}" rx="12" fill="{color}"/>\n'
        mid = (y_of(a) + y_of(b)) / 2
        ty = mid if b - a > 10 else y_of(b) - 2
        body += f'<line x1="{bx + bw + 10}" x2="{bx + bw + 70}" y1="{ty:.1f}" y2="{ty:.1f}" stroke="{SOFT}" stroke-width="2"/>\n'
        body += text(bx + bw + 90, ty - 6, label, 28, INK, 650)
        body += text(bx + bw + 90, ty + 28, sub, 23, SOFT)
    py = y_of(60)
    body += f'<line x1="{bx - 40}" x2="{bx + bw}" y1="{py:.1f}" y2="{py:.1f}" stroke="{RED}" stroke-width="4" stroke-dasharray="14 9"/>\n'
    body += text(bx - 50, py - 10, "piekbeperking:", 23, RED, 650, "end")
    body += text(bx - 50, py + 20, "laadt in de daluren", 23, RED, None, "end")
    body += text(bx - 50, py + 48, "tot dit niveau", 23, RED, None, "end")
    for pct in (0, 25, 95):
        body += text(bx + bw / 2, y_of(pct) - 10 if pct else y_of(pct) - 14, f"{pct}%", 22, "#ffffff" if pct != 95 else INK, 650, "middle")
    body += text(150, 850, "Voorbeeldwaarden. Welke grenzen bij jou passen, hangt af van je verbruik en hoe vaak de stroom uitvalt.", 23)
    return svg(body, "Hoe de laadniveaus van je SigenStor samenwerken", "Je batterij is opgedeeld in zones; elke instelling legt een grens vast")


# Praktijkvoorbeeld: 10 kWh bijgeplaatst bij een bestaande hybride omvormer (echte meetwaarden, anoniem).
CASE_MONTHS = [  # maand, opgewekt, verbruik, waarvan uit eigen zonnestroom (kWh, afgelezen en afgerond)
    ("juni*", 280, 230, 140), ("juli", 850, 550, 550), ("augustus", 620, 540, 460),
    ("september", 410, 540, 390), ("oktober*", 190, 340, 190)]
CASE_NOTE = "Meetwaarden van één woning uit de monitoringapp van de installatie, van de plaatsing in juni tot 18 oktober 2026."


def case_split():
    """Where the solar energy went and where the consumption came from, since the battery was added."""
    x0, x1 = 150, 1450
    rows = [(215, "Opgewekt door de zonnepanelen", "2.360 kWh",
             [(75, "zelf gebruikt", "1.760 kWh", LEAF, "#ffffff"), (25, "naar het net", "598 kWh", "#cfd8d5", INK)]),
            (535, "Verbruikt in de woning", "2.210 kWh",
             [(79, "uit eigen zonnestroom", "1.740 kWh", LEAF, "#ffffff"), (21, "van het net", "470 kWh", INK, "#ffffff")])]
    body = ""
    for y, label, total, parts in rows:
        body += text(x0, y, label, 30, INK, 650)
        body += text(x1, y, total, 30, INK, 650, "end")
        bx, top, h = x0, y + 28, 190
        for pct, name, kwh, fill, color in parts:
            w = (x1 - x0) * pct / 100
            body += f'<rect x="{bx:.1f}" y="{top}" width="{w:.1f}" height="{h}" fill="{fill}"/>\n'
            cx = bx + w / 2
            body += text(cx, top + 92, f"{pct}%", 60, color, 650, "middle")
            body += text(cx, top + 140, f"{kwh} {name}", 25, color, None, "middle")
            bx += w
    body += text(150, 850, CASE_NOTE + " Afgerond.", 23)
    return svg(body, "Woning 1: na het bijplaatsen van 10 kWh opslag", "Waar de zonnestroom naartoe ging en waar het verbruik vandaan kwam")


def case_months():
    """Per month: solar production next to consumption, split into own solar energy and grid."""
    x0, x1, ytop, ybot = 170, 1530, 250, 740
    hi = 900
    y_of = lambda v: ybot - (ybot - ytop) * v / hi
    body = axes(x0, x1, y_of, [0, 200, 400, 600, 800], " kWh")
    legend = [("#bfe9cf", "opgewekt"), (LEAF, "verbruik uit eigen zonnestroom"), (INK, "verbruik van het net")]
    for lx, (color, label) in zip((170, 350, 790), legend):
        body += f'<rect x="{lx}" y="178" width="26" height="26" rx="4" fill="{color}"/>\n' + text(lx + 38, 200, label, 24, INK)
    slot = (x1 - x0) / len(CASE_MONTHS)
    bw = 92
    for i, (month, made, used, own) in enumerate(CASE_MONTHS):
        cx = x0 + slot * i + slot / 2
        px, ux = cx - bw - 8, cx + 8
        body += f'<rect x="{px:.1f}" y="{y_of(made):.1f}" width="{bw}" height="{ybot - y_of(made):.1f}" rx="6" fill="#bfe9cf"/>\n'
        body += f'<rect x="{ux:.1f}" y="{y_of(own):.1f}" width="{bw}" height="{ybot - y_of(own):.1f}" fill="{LEAF}"/>\n'
        if used > own:
            body += f'<rect x="{ux:.1f}" y="{y_of(used):.1f}" width="{bw}" height="{y_of(own) - y_of(used):.1f}" fill="{INK}"/>\n'
        share = round(own / used * 100)
        shown = "± 100%" if share >= 99 else f"{share}%"
        body += text(ux + bw / 2, y_of(used) - 16, shown, 27, LEAF_DEEP, 650, "middle")
        body += text(cx, 790, month, 27, INK, 600, "middle")
    body += text(150, 850, "Het percentage is het deel van het verbruik uit eigen zonnestroom. * juni vanaf de plaatsing, oktober tot en met 18 oktober.", 23)
    body += text(150, 880, "Meetwaarden van één woning, maandwaarden afgelezen uit de monitoringapp en afgerond op 10 kWh.", 23)
    return svg(body, "Woning 1 per maand: zonnestroom en verbruik", "In juli vrijwel volledig uit eigen zonnestroom, richting herfst stijgt het aandeel van het net")


CASE2_MONTHS = [  # woning 2: maand, uit de batterij, van het net (kWh, uit de monitoringapp)
    ("mei*", 42.81, 0.02), ("juni", 156.90, 6.15), ("juli", 172.73, 12.72),
    ("augustus", 154.25, 17.37), ("september", 187.86, 33.07), ("oktober*", 107.77, 34.22)]
CASE3_MONTHS = [  # woning 3
    ("mei*", 80.85, 0.86), ("juni", 145.62, 0.28), ("juli", 166.22, 1.20),
    ("augustus", 146.75, 5.70), ("september", 133.51, 1.40), ("oktober*", 75.18, 28.91)]


def ac_case_months(title, months, start_note):
    """AC-coupled home: consumption not covered directly by solar, from battery or grid, per month."""
    x0, x1, ytop, ybot = 170, 1530, 250, 740
    hi = 250
    y_of = lambda v: ybot - (ybot - ytop) * v / hi
    body = axes(x0, x1, y_of, [0, 50, 100, 150, 200, 250], " kWh")
    for lx, (color, label) in zip((170, 420), [(LAGOON, "uit de batterij"), (INK, "van het net")]):
        body += f'<rect x="{lx}" y="178" width="26" height="26" rx="4" fill="{color}"/>\n' + text(lx + 38, 200, label, 24, INK)
    slot = (x1 - x0) / len(months)
    bw = 120
    for i, (month, bat, grid) in enumerate(months):
        cx = x0 + slot * i + slot / 2
        bx = cx - bw / 2
        body += f'<rect x="{bx:.1f}" y="{y_of(bat):.1f}" width="{bw}" height="{ybot - y_of(bat):.1f}" fill="{LAGOON}"/>\n'
        body += f'<rect x="{bx:.1f}" y="{y_of(bat + grid):.1f}" width="{bw}" height="{y_of(bat) - y_of(bat + grid):.1f}" fill="{INK}"/>\n'
        share = bat / (bat + grid) * 100
        shown = "± 100%" if share >= 99.5 else f"{share:.0f}%"
        body += text(cx, y_of(bat + grid) - 46, shown, 27, LAGOON_DEEP, 650, "middle")
        grid_shown = "< 0,1" if grid < 0.1 else (f"{grid:.1f}" if grid < 10 else f"{grid:.0f}").replace(".", ",")
        body += text(cx, y_of(bat + grid) - 16, f"net: {grid_shown} kWh", 22, SOFT, None, "middle")
        body += text(cx, 790, month, 27, INK, 600, "middle")
    body += text(150, 850, "De app van deze installatie ziet de bestaande zonnepanelen niet: rechtstreeks gebruikte zonnestroom zit er niet in.", 23)
    body += text(150, 880, f"Het percentage is het deel uit de batterij. * mei vanaf de plaatsing op {start_note}, oktober tot en met 18 oktober 2026.", 23)
    return svg(body, title, "Per maand: hoeveel daarvan uit de batterij kwam en hoeveel van het net")


def case_overview():
    """Hero: the three homes side by side, each with its own headline figure."""
    cards = [("Woning 1", "op de bestaande hybride omvormer", "79%", "van het totale verbruik", "uit eigen zonnestroom", "470 kWh van het net", "juni tot 18 oktober"),
             ("Woning 2", "AC-gekoppelde batterij, gezin van vier", "89%", "van het verbruik buiten de zon", "uit de batterij", "104 kWh van het net", "23 mei tot 18 oktober"),
             ("Woning 3", "AC-gekoppelde batterij", "95%", "van het verbruik buiten de zon", "uit de batterij", "38 kWh van het net", "11 mei tot 18 oktober")]
    body = ""
    w, gap, top, h = 420, 50, 190, 600
    for i, (name, kind, big, l1, l2, grid, period) in enumerate(cards):
        x = 150 + i * (w + gap)
        fill, deep = ("#e9f8ef", LEAF_DEEP) if i == 0 else ("#e3f4f6", LAGOON_DEEP)
        body += f'<rect x="{x}" y="{top}" width="{w}" height="{h}" rx="22" fill="{fill}"/>\n'
        cx = x + w / 2
        body += text(cx, top + 70, name, 34, INK, 650, "middle")
        body += text(cx, top + 108, kind, 22, SOFT, None, "middle")
        body += text(cx, top + 260, big, 110, deep, 650, "middle")
        body += text(cx, top + 320, l1, 25, INK, None, "middle")
        body += text(cx, top + 354, l2, 25, INK, None, "middle")
        body += f'<line x1="{x + 40}" x2="{x + w - 40}" y1="{top + 410}" y2="{top + 410}" stroke="{LINE}" stroke-width="3"/>\n'
        body += text(cx, top + 470, grid, 30, INK, 650, "middle")
        body += text(cx, top + 510, period, 23, SOFT, None, "middle")
    body += text(150, 850, "Meetwaarden van drie woningen uit de monitoringapps, 2026. Bij woning 2 en 3 telt de rechtstreeks gebruikte zonnestroom", 22)
    body += text(150, 880, "niet mee. Daarom zijn de percentages niet onderling vergelijkbaar.", 22)
    return svg(body, "Drie woningen, telkens ongeveer 10 kWh opslag bijgeplaatst", "Wat de batterij deed tussen de plaatsing en 18 oktober 2026")


def contract_shares_creg():
    """Share of Belgian household contracts by price group (CREG study F3188, contracts on 30 September 2025)."""
    rows = [("Elektriciteit", 51, 9), ("Aardgas", 64, 10)]
    x0, x1 = 360, 1530
    body = ""
    for i, (label, dear, cheap) in enumerate(rows):
        y = 250 + i * 250
        mid = 100 - dear - cheap
        x_of = lambda p: x0 + (x1 - x0) * p / 100
        body += text(150, y + 70, label, 30, INK, 650)
        segs = [(0, dear, RED, "#ffffff", f"{dear}%", "bij de 10 duurste"),
                (dear, dear + mid, "#dfe6e3", INK, f"{mid}%", "de rest van de markt"),
                (dear + mid, 100, LEAF, "#ffffff", f"{cheap}%", "")]
        for a, b, fill, ink, big, small in segs:
            body += f'<rect x="{x_of(a):.1f}" y="{y}" width="{x_of(b) - x_of(a):.1f}" height="120" fill="{fill}"/>\n'
            cx = (x_of(a) + x_of(b)) / 2
            body += text(cx, y + 62 if small else y + 74, big, 34, ink, 700, "middle")
            if small:
                body += text(cx, y + 96, small, 22, ink, None, "middle")
        body += text(x_of(100), y + 160, f"{cheap}% bij de 10 goedkoopste producten", 23, LEAF_DEEP, 600, "end")
    body += text(150, 850, "Bron: CREG, studie F3188 (12 maart 2026), lopende contracten van Belgische gezinnen op 30 september 2025.", 22)
    body += text(150, 880, "De rest van de markt is het verschil met 100%.", 22)
    return svg(body, "De meeste gezinnen zitten bij een duur product", "Aandeel van de energiecontracten van gezinnen per prijsgroep, België")


def gsc_what_is_allowed():
    """What you may change while the installation still receives groenestroomcertificaten (Fluvius rules)."""
    ok_fill, ok_line = "#e9f8ef", "#bfe9cf"
    cond_fill, cond_line = "#e7f5f7", "#b5dde3"
    no_fill, no_line = "#fdecea", "#f3c7c0"
    rows = [
        ("Thuisbatterij AC-gekoppeld", "mag", "batterij met eigen omvormer, niet tussen omvormer en groenestroomteller", ok_fill, ok_line, LEAF_DEEP),
        ("Hybride omvormer + batterij", "mag", "met bidirectionele groenestroomteller en nieuwe AREI-keuring", ok_fill, ok_line, LEAF_DEEP),
        ("Omvormer vervangen, zonder batterij", "enkel bij defect", "nieuwe omvormer op de C10/26-lijst, max. 5 kVA (1-fase) of 10 kVA (3-fase)", cond_fill, cond_line, LAGOON_DEEP),
        ("Defecte panelen vervangen", "onder voorwaarden", "één op één, gelijkaardig paneel, met bewijs van het defect", cond_fill, cond_line, LAGOON_DEEP),
        ("Panelen bijleggen", "niet", "extra panelen enkel op een aparte omvormer, als nieuwe installatie", no_fill, no_line, RED),
    ]
    body = ""
    y = 180
    for label, verdict, note, fill, line, color in rows:
        body += f'<rect x="150" y="{y}" width="1300" height="112" rx="18" fill="{fill}" stroke="{line}" stroke-width="3"/>\n'
        body += text(185, y + 48, label, 29, INK, 650)
        body += text(185, y + 88, note, 22, SOFT)
        body += f'<rect x="1150" y="{y + 30}" width="270" height="52" rx="26" fill="#ffffff" stroke="{color}" stroke-width="3"/>\n'
        body += text(1285, y + 65, verdict, 24, color, 650, "middle")
        y += 128
    body += text(150, 850, "Bron: Fluvius, aanpassingen aan je installatie zonnepanelen en toelichting PV-installatie (versie 2.0). De regels van Fluvius", 21)
    body += text(150, 878, "zeggen niets specifieks over een AC-gekoppelde batterij. Elke wijziging meld je in Mijn Fluvius.", 21)
    return svg(body, "Groenestroomcertificaten: wat mag je veranderen?", "Wat er mag aan een installatie die nog groenestroomcertificaten krijgt")


def gsc_end_years():
    """Until when certificates run, per period of commissioning (Vlaanderen.be)."""
    groups = [
        ("2006 tot juli 2012", "20 jaar", 2006, 2012.58, 20),
        ("augustus tot december 2012", "10 jaar", 2012.58, 2013, 10),
        ("2013 tot maart 2018", "15 jaar", 2013, 2018.25, 15),
        ("april 2018 tot 2020", "10 jaar", 2018.25, 2020.99, 10),
        ("januari tot 16 juli 2021", "max. 12 jaar", 2021, 2021.54, 12),
    ]
    x0, x1, start, end = 560, 1500, 2022, 2034
    x_of = lambda yr: x0 + (x1 - x0) * (yr - start) / (end - start)
    body = ""
    for yr in range(start, end + 1, 2):
        x = x_of(yr)
        body += f'<line x1="{x:.1f}" x2="{x:.1f}" y1="190" y2="760" stroke="{LINE}" stroke-width="2"/>\n'
        body += text(x, 795, str(yr), 23, SOFT, None, "middle")
    now = x_of(2026.83)
    body += f'<line x1="{now:.1f}" x2="{now:.1f}" y1="180" y2="760" stroke="{RED}" stroke-width="3" stroke-dasharray="10 8"/>\n'
    body += text(now, 172, "nu", 22, RED, 650, "middle")
    y = 215
    for label, dur, a, b, years in groups:
        ea, eb = a + years, b + years
        xa, xb = max(x_of(ea), x0), x_of(eb)
        ended = eb <= 2026.83
        color = "#c9d5d1" if ended else ("#b5dde3" if a >= 2013 else LEAF)
        body += text(150, y + 30, label, 25, INK, 650)
        ended = (b + years) <= 2026.83
        big_only = a >= 2013
        span = f"{int(a + years)} tot {int(b + years)}" if int(a + years) != int(b + years) else f"{int(b + years)}"
        status = "al afgelopen" if ended else (f"tot {int(b + years)}, enkel nog boven 10 kW" if big_only else f"loopt af {span}")
        body += text(150, y + 62, f"steun {dur}: {status}", 21, SOFT if ended or big_only else LEAF_DEEP, 600)
        if xb > x0:
            body += f'<rect x="{xa:.1f}" y="{y + 12}" width="{max(xb - xa, 8):.1f}" height="44" rx="10" fill="{color}"/>\n'
        y += 108
    body += text(150, 836, "Installaties tot 10 kW (de meeste woningen) van na 2012 krijgen vandaag geen certificaten: de bandingfactor is sinds 1 augustus 2022 nul,", 21)
    body += text(150, 862, "en na 1 juli 2015 is er geen categorie meer. Installaties van na 16 juli 2021 krijgen geen certificaten.", 21)
    body += text(150, 888, "Bron: Vlaanderen.be, groenestroomcertificaten voor zonnepanelen en overzicht bandingfactor zonnepanelen.", 21)
    return svg(body, "Tot wanneer krijg je groenestroomcertificaten?", "Looptijd van de steun volgens de datum waarop je installatie in dienst kwam")


def panel_degradation():
    """Remaining power of crystalline panels by age: NREL median 0,5 %/jaar, spread 0,4 to 0,9 %/jaar."""
    x0, x1, ytop, ybot = 200, 1520, 190, 740
    years = 30
    x_of = lambda a: x0 + (x1 - x0) * a / years
    y_of = lambda pct: ybot - (ybot - ytop) * (pct - 70) / 30
    body = axes(x0, x1, y_of, [70, 75, 80, 85, 90, 95, 100], "%")
    for a in range(0, years + 1, 5):
        body += text(x_of(a), 785, f"{a} jaar", 23, SOFT, None, "middle")
    hi = [(a, 100 * (1 - 0.004) ** a) for a in range(years + 1)]
    lo = [(a, 100 * (1 - 0.009) ** a) for a in range(years + 1)]
    band = " ".join(f"{x_of(a):.1f},{y_of(v):.1f}" for a, v in hi) + " " + " ".join(f"{x_of(a):.1f},{y_of(v):.1f}" for a, v in reversed(lo))
    body += f'<polygon points="{band}" fill="{LEAF}" fill-opacity="0.18"/>\n'
    mid = " ".join(f"{x_of(a):.1f},{y_of(100 * (1 - 0.005) ** a):.1f}" for a in range(years + 1))
    body += f'<polyline points="{mid}" fill="none" stroke="{LEAF_DEEP}" stroke-width="5"/>\n'
    a = 16
    v = 100 * (1 - 0.005) ** a
    body += f'<circle cx="{x_of(a):.1f}" cy="{y_of(v):.1f}" r="10" fill="{LEAF_DEEP}"/>\n'
    body += text(x_of(a) + 20, y_of(v) - 22, "paneel uit 2010: ± 92%", 25, INK, 650)
    body += text(x_of(22), y_of(100 * (1 - 0.009) ** 22) + 50, "sneller of trager dan de mediaan", 22, LEAF_DEEP, 600, "middle")
    body += text(150, 850, "Lijn: mediaan van 0,5% verlies per jaar. Band: 0,4 tot 0,9% per jaar. Een individueel paneel kan daarbuiten vallen, bijvoorbeeld door een defect.", 21)
    body += text(150, 878, "Bron: NREL, Jordan en Kurtz (mediaan 0,5%) en Jordan e.a. 2016 (gemiddelde 0,8 tot 0,9%); ondergrens 0,4%: garantie JinkoSolar Tiger Neo.", 21)
    return svg(body, "Hoeveel vermogen heeft een zonnepaneel nog?", "Resterend vermogen van kristallijne zonnepanelen naargelang hun leeftijd")


def panels_vs_inverter():
    """Typical life of panels versus string inverters."""
    x0, x1 = 420, 1500
    x_of = lambda yr: x0 + (x1 - x0) * yr / 30
    body = ""
    for yr in range(0, 31, 5):
        x = x_of(yr)
        body += f'<line x1="{x:.1f}" x2="{x:.1f}" y1="210" y2="640" stroke="{LINE}" stroke-width="2"/>\n'
        body += text(x, 680, f"{yr} jaar", 23, SOFT, None, "middle")
    rows = [
        ("Zonnepanelen", "gaan volgens pv magazine 25 tot 30 jaar of langer mee", 25, 30, LEAF, (0, 25)),
        ("Omvormer", "gaat volgens pv magazine meestal 10 tot 15 jaar mee", 10, 15, LAGOON, (0, 10)),
    ]
    y = 250
    for label, sub, a, b, color, solid in rows:
        body += text(150, y + 40, label, 30, INK, 650)
        body += text(150, y + 76, "", 21)
        if solid:
            body += f'<rect x="{x_of(solid[0]):.1f}" y="{y}" width="{x_of(solid[1]) - x_of(solid[0]):.1f}" height="60" rx="12" fill="{color}"/>\n'
            body += f'<rect x="{x_of(a):.1f}" y="{y}" width="{x_of(b) - x_of(a):.1f}" height="60" rx="12" fill="{color}" fill-opacity="0.35"/>\n'
        else:
            body += f'<rect x="{x_of(a):.1f}" y="{y}" width="{x_of(b) - x_of(a):.1f}" height="60" rx="12" fill="{color}"/>\n'
        body += text(x_of(0) + 20, y + 106, sub, 23, INK, 600)
        y += 200
    body += text(150, 760, "Tijdens het leven van je panelen vervang je de omvormer vaak minstens één keer:", 25, INK, 600)
    body += text(150, 796, "een goed moment om aan een batterij te denken.", 25, INK, 600)
    body += text(150, 868, "Bron: pv magazine (6 augustus 2025), met cijfers van EnergySage voor string-omvormers.", 21)
    return svg(body, "Panelen gaan langer mee dan de omvormer", "Typische levensduur van de onderdelen van een zonne-installatie")


def battery_capacity_power():
    """Capacity (kWh) versus power (kW) and the Vlaanderen.be rule of thumb of 1 to 1,5 kWh per kWp."""
    body = markers(INK)
    body += text(150, 190, "Capaciteit (kWh)", 30, INK, 650)
    body += text(150, 232, "hoeveel energie ze kan opslaan", 25)
    body += f'<rect x="170" y="280" width="150" height="190" rx="18" fill="#ffffff" stroke="{INK}" stroke-width="4"/>\n'
    body += f'<rect x="174" y="352" width="142" height="114" rx="14" fill="{LEAF}"/>\n'
    body += text(360, 360, "Genoeg opslag voor een hele", 24)
    body += text(360, 392, "avond kan toch te weinig", 24)
    body += text(360, 424, "vermogen hebben.", 24)
    body += text(840, 190, "Vermogen (kW)", 30, INK, 650)
    body += text(840, 232, "hoeveel stroom ze op hetzelfde moment", 25)
    body += text(840, 262, "kan leveren of opnemen", 25)
    body += text(840, 330, "Voorbeeld: laadpaal en oven vragen samen 9 kW", 24, INK, 600)
    unit = 690 / 9
    body += f'<rect x="840" y="352" width="{3 * unit:.1f}" height="70" rx="12" fill="{LAGOON}"/>\n'
    body += text(840 + 1.5 * unit, 396, "batterij 3 kW", 24, "#ffffff", 650, "middle")
    body += f'<rect x="{840 + 3 * unit:.1f}" y="352" width="{6 * unit:.1f}" height="70" rx="12" fill="#eef1f0" stroke="{SOFT}" stroke-width="3"/>\n'
    body += text(840 + 6 * unit, 396, "6 kW van het net", 24, INK, 650, "middle")
    body += text(840, 464, "Wat de batterij niet kan leveren, komt van het net.", 24)
    body += f'<line x1="150" x2="1530" y1="525" y2="525" stroke="{LINE}" stroke-width="3"/>\n'
    body += text(150, 580, "Vuistregel van Vlaanderen.be om de capaciteit af te stemmen op je zonnepanelen", 30, INK, 650)
    body += box(150, 615, 270, 96, "8 kWp", "zonne-installatie")
    body += text(485, 678, "×", 44, INK, 650, "middle")
    body += box(550, 615, 450, 96, "1 tot 1,5 kWh", "batterijcapaciteit per kWp")
    body += text(1060, 678, "=", 44, INK, 650, "middle")
    body += box(1120, 615, 410, 96, "± 8 tot 12 kWh", "een vertrekpunt", "#e9f8ef", "#bfe9cf", LEAF_DEEP)
    body += text(150, 770, "Geen eindantwoord: er bestaat geen standaardgrootte. Kijk ook naar je huidige en toekomstige", 25, INK, 600)
    body += text(150, 804, "verbruik, naar wanneer je het gebruikt en naar wat je met de batterij wil doen.", 25, INK, 600)
    body += text(150, 850, "Bron: Vlaanderen.be, Thuisbatterij. Voorbeeld met fictieve waarden: batterij van 3 kW, vraag van 9 kW, installatie van 8 kWp.", 22)
    return svg(body, "Capaciteit en vermogen: twee verschillende maten", "De vuistregel van 1 tot 1,5 kWh per kWp is een vertrekpunt, geen standaardgrootte")


def self_use_vs_injection():
    """Worked example from the article: 4.000 kWh a year, 30% used directly, 30 ct avoided versus 3 ct injection."""
    x0, x1 = 150, 1530
    body = text(150, 190, "Een jaar zonnestroom: 4.000 kWh", 30, INK, 650)
    w_self = (x1 - x0) * 0.3
    body += f'<rect x="{x0}" y="215" width="{w_self:.1f}" height="70" rx="12" fill="{LEAF}"/>\n'
    body += f'<rect x="{x0 + w_self:.1f}" y="215" width="{(x1 - x0) - w_self:.1f}" height="70" rx="12" fill="#cfd8d5"/>\n'
    body += text(x0 + w_self / 2, 260, "1.200 kWh", 28, "#ffffff", 650, "middle")
    body += text(x0 + w_self + (x1 - x0 - w_self) / 2, 260, "2.800 kWh", 28, INK, 650, "middle")
    body += text(x0 + w_self / 2, 322, "meteen zelf gebruikt (30%)", 24, LEAF_DEEP, 600, "middle")
    body += text(x0 + w_self + (x1 - x0 - w_self) / 2, 322, "geïnjecteerd op het net", 24, SOFT, 600, "middle")
    body += f'<line x1="150" x2="1530" y1="360" y2="360" stroke="{LINE}" stroke-width="3"/>\n'
    body += text(150, 412, "Wat is één kWh in dit voorbeeld waard?", 30, INK, 650)
    bx, per_ct = 640, 29
    rows = [("Zelf gebruikt", "je haalt die kWh niet van het net", 30, LEAF, "30 cent bespaard"),
            ("Geïnjecteerd", "vergoeding van je leverancier", 3, "#9fb2ad", "3 cent")]
    y = 440
    for label, sub, ct, color, shown in rows:
        body += text(150, y + 30, label, 27, INK, 650)
        body += text(150, y + 62, sub, 22)
        body += f'<rect x="{bx}" y="{y}" width="{ct * per_ct}" height="70" rx="12" fill="{color}"/>\n'
        if ct > 10:
            body += text(bx + ct * per_ct / 2, y + 45, shown, 28, "#ffffff", 650, "middle")
        else:
            body += text(bx + ct * per_ct + 20, y + 45, shown, 28, INK, 650)
        y += 100
    xa, xb = bx + 3 * per_ct, bx + 30 * per_ct
    body += f'<path d="M{xa} 632 V650 H{xb} V632" fill="none" stroke="{LEAF_DEEP}" stroke-width="4"/>\n'
    body += text((xa + xb) / 2, 686, "27 cent meer per kWh die je zelf gebruikt", 27, LEAF_DEEP, 650, "middle")
    body += box(150, 715, 1380, 80, "1.000 kWh extra zelf gebruiken is hier ongeveer € 270 per jaar waard", None, "#e9f8ef", "#bfe9cf", LEAF_DEEP)
    body += text(150, 828, "Voorbeeld met fictieve waarden: 30 cent per kWh afname, 3 cent per kWh injectie. Capaciteitstarief, vaste kosten en opslagverliezen", 21)
    body += text(150, 854, "zijn niet meegerekend. Een rekenvoorbeeld, geen belofte: je echte cijfers hangen af van je verbruik, je contract en de energieprijzen.", 21)
    return svg(body, "Zelf gebruiken of injecteren: het verschil", "Een kWh die je niet van het net haalt, is meer waard dan een kWh die je injecteert")


def inverter_split_day():
    """One sunny day: 20 kWh, 6 kWh used directly, 14 kWh injected; plus the reasons an inverter injects less."""
    body = markers(INK)
    body += box(150, 215, 300, 120, "Zonnepanelen", "20 kWh die dag")
    body += box(560, 215, 300, 120, "Omvormer", "gelijk- naar wisselstroom")
    body += box(960, 170, 420, 100, "Huis", "6 kWh meteen zelf gebruikt", "#e9f8ef", "#bfe9cf", LEAF_DEEP)
    body += box(960, 290, 420, 100, "Net", "14 kWh geïnjecteerd", "#eef1f0", LINE)
    body += arrow(450, 275, 552, 275)
    body += arrow(860, 262, 952, 222)
    body += arrow(860, 290, 952, 340)
    body += text(150, 450, "Wat is die 14 kWh waard?", 30, INK, 650)
    body += box(150, 475, 660, 96, "14 kWh injecteren", "levert ongeveer € 0,42 op", "#eef1f0", LINE)
    body += text(840, 534, "of", 26, SOFT, 600, "middle")
    body += box(870, 475, 660, 96, "Diezelfde 14 kWh later zelf gebruiken", "vermijdt ongeveer € 4,20 aan afname", "#e9f8ef", "#bfe9cf", LEAF_DEEP)
    body += text(150, 640, "Wanneer injecteert je omvormer minder of niets?", 30, INK, 650)
    body += box(150, 665, 440, 105, "Te hoge netspanning", "hij schakelt automatisch af")
    body += box(620, 665, 440, 105, "Injectiebegrenzing", "bijvoorbeeld na een netstudie")
    body += box(1090, 665, 440, 105, "Sturing op prijs", "bij een negatieve prijs")
    body += text(150, 826, "Voorbeeld met fictieve waarden: 30 cent per kWh afname en 3 cent per kWh injectie; opslagverliezen en capaciteitstarief", 21)
    body += text(150, 852, "zijn niet meegerekend. De redenen om minder te injecteren, met hun bronnen, staan in het artikel.", 21)
    return svg(body, "Wat doet je omvormer op een zonnige dag?", "Wat je niet meteen gebruikt, gaat naar het net, en dat is veel minder waard dan zelf gebruiken")


def frequency_50hz():
    """Grid frequency scale around 50 Hz with the thresholds named in the article, and the reserve sequence."""
    body = markers(INK)
    n, x_a, x_b, yc, amp = 4, 150, 520, 205, 38
    pts = " ".join(f"{x_a + (x_b - x_a) * i / 200:.1f},{yc - amp * math.sin(2 * math.pi * n * i / 200):.1f}" for i in range(201))
    body += f'<polyline points="{pts}" fill="none" stroke="{LEAF_DEEP}" stroke-width="5" stroke-linejoin="round"/>\n'
    body += text(570, 198, "50 Hz = 50 volledige trillingen per seconde", 30, INK, 650)
    body += text(570, 236, "De stroom wisselt dus 100 keer per seconde van richting.", 25)
    x_of = lambda f: 170 + (f - 48.9) * 971.4
    yb, hb = 400, 50
    body += f'<rect x="170" y="{yb}" width="{x_of(49.0) - 170:.1f}" height="{hb}" fill="#f6d9d4"/>\n'
    body += f'<rect x="{x_of(49.0):.1f}" y="{yb}" width="{x_of(49.8) - x_of(49.0):.1f}" height="{hb}" fill="#eef1f0"/>\n'
    body += f'<rect x="{x_of(49.8):.1f}" y="{yb}" width="{x_of(50.2) - x_of(49.8):.1f}" height="{hb}" fill="#e3f4f6"/>\n'
    body += f'<rect x="{x_of(49.95):.1f}" y="{yb}" width="{x_of(50.05) - x_of(49.95):.1f}" height="{hb}" fill="{LEAF}"/>\n'
    body += f'<rect x="{x_of(50.2):.1f}" y="{yb}" width="{1530 - x_of(50.2):.1f}" height="{hb}" fill="#c4e6ec"/>\n'
    body += text((x_of(49.0) + x_of(49.8)) / 2, yb + 33, "zakt ze verder: noodmaatregelen", 23, INK, 600, "middle")
    for f, label, color in [(49.0, "49,0 Hz", RED), (49.8, "49,8 Hz", INK), (50.0, "50 Hz", LEAF_DEEP), (50.2, "50,2 Hz", INK)]:
        body += text(x_of(f), 488, label, 23, color, 650, "middle")
    body += text(170, 305, "Meer verbruik dan productie:", 25, INK, 650)
    body += text(170, 337, "de frequentie daalt, bijvoorbeeld naar 49,95 Hz", 23)
    body += text(1530, 305, "Meer productie dan verbruik:", 25, INK, 650, "end")
    body += text(1530, 337, "de frequentie stijgt, bijvoorbeeld naar 50,05 Hz", 23, SOFT, None, "end")
    body += text(x_of(50.0), 385, "Normaal: 50 Hz ± 0,05 Hz", 24, LEAF_DEEP, 650, "middle")
    body += text(170, 545, "Vanaf 49,0 Hz schakelt België automatisch", 23, RED, 600)
    body += text(170, 575, "verbruik af, in stappen.", 23, RED, 600)
    body += text(x_of(50.0) - 140, 545, "Bij 49,8 of 50,2 Hz (0,2 Hz afwijking)", 23, LAGOON_DEEP, 600, "middle")
    body += text(x_of(50.0) - 140, 575, "is de primaire reserve volledig ingezet.", 23, LAGOON_DEEP, 600, "middle")
    body += text(1530, 625, "Boven 50,2 Hz verminderen omvormers van zonnepanelen", 23, LAGOON_DEEP, 600, "end")
    body += text(1530, 655, "die sinds 2013 geplaatst zijn geleidelijk hun vermogen.", 23, LAGOON_DEEP, 600, "end")
    body += text(150, 710, "Elia grijpt in met reserves, stap voor stap", 30, INK, 650)
    body += box(150, 730, 430, 86, "FCR: enkele seconden", "automatisch, stabiliseert")
    body += box(625, 730, 430, 86, "aFRR: binnen 7,5 minuten", "automatisch, terug naar 50 Hz")
    body += box(1100, 730, 430, 86, "mFRR: binnen 15 minuten", "manueel, grote onevenwichten")
    body += arrow(582, 773, 618, 773)
    body += arrow(1057, 773, 1093, 773)
    body += text(150, 856, "Bron: Elia, ENTSO-E, Synergrid (C10/11) en Energuide (Sibelga). Vereenvoudigd weergegeven.", 22)
    return svg(body, "50 Hz: hoe ver mag de frequentie afwijken?", "Wat er gebeurt op het Europese net als productie en verbruik uit evenwicht raken")


def write(name, content):
    (OUT / f"{name}.svg").write_text(content, encoding="utf-8")
    print("wrote", name)


if __name__ == "__main__":
    write("dynamische-prijzen-dag", dynamic_price_day())
    write("ac-dc-laden", ac_dc_charging())
    write("back-up-opties", backup_options())
    write("netspanning-zonnige-dag", grid_voltage_day())
    write("batterijgrootte-vlaanderen", battery_size_trend())
    write("zendure-modus-kiezen", zendure_mode_choice())
    write("zendure-zelfverbruik", zendure_self_consumption())
    write("zendure-tou-prijszones", zendure_tou_zones())
    write("sigen-instellingen", sigen_settings_layers())
    write("sigen-piekbeperking", sigen_peak_shaving())
    write("sigen-laadniveaus", sigen_battery_levels())
    write("thuisbatterij-bijplaatsen-verdeling", case_split())
    write("thuisbatterij-bijplaatsen-per-maand", case_months())
    write("thuisbatterij-bijplaatsen-woning-2", ac_case_months("Woning 2: verbruik dat de zon niet rechtstreeks dekte", CASE2_MONTHS, "23 mei"))
    write("thuisbatterij-bijplaatsen-woning-3", ac_case_months("Woning 3: verbruik dat de zon niet rechtstreeks dekte", CASE3_MONTHS, "11 mei"))
    write("thuisbatterij-bijplaatsen-overzicht", case_overview())
    write("energiecontracten-prijsgroep", contract_shares_creg())
    write("groenestroomcertificaten-wat-mag", gsc_what_is_allowed())
    write("groenestroomcertificaten-looptijd", gsc_end_years())
    write("zonnepanelen-vermogen-leeftijd", panel_degradation())
    write("panelen-omvormer-levensduur", panels_vs_inverter())
    write("batterij-capaciteit-vermogen", battery_capacity_power())
    write("zelfverbruik-of-injectie", self_use_vs_injection())
    write("omvormer-zonnige-dag", inverter_split_day())
    write("frequentie-50-hz", frequency_50hz())
