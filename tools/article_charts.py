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
    body += house(1070, 200, [True, True, False], "Back-upschakeling", "gekozen kringen blijven", "werken, los van het net")
    body += text(150, 850, "Vereenvoudigd: wat blijft werken tijdens een stroomonderbreking. Een volledige woning op back-up vraagt meer vermogen.", 23)
    return svg(body, "Stroomonderbreking: drie situaties", "Een batterij mag nooit stroom naar het net sturen; wat werkt, hangt af van de installatie")


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
    return svg(body, "Te hoge netspanning op een zonnige dag", "Elke keer de spanning de grens raakt, schakelt de omvormer even af")


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
    body += text(150, 850, "* januari tot mei 2026, voorlopig. Gemiddelde van nieuw aangesloten thuisbatterijen, berekend uit open data van Fluvius.", 23)
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
