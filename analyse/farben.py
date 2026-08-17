#!/usr/bin/env python3
"""Markenfarben je Wettbewerber.

Der erste Versuch zaehlte einfach alle Hex-Werte im Quelltext — dabei kamen
Bootstrap- und WordPress-Standardpaletten heraus (#dc3545, #00d084, #0693e3),
also Framework-Beiwerk statt Marke. Diese Fassung sucht gezielt dort, wo eine
Marke ihre Farbe wirklich hinterlegt, und wirft bekannte Framework-Werte raus.
"""
import re, json, colorsys, subprocess, concurrent.futures as cf, pathlib

WURZEL = pathlib.Path(__file__).resolve().parent.parent
SP = WURZEL / "quellen"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121 Safari/537.36"

# Standardpaletten, die nichts ueber die Marke aussagen
FRAMEWORK = {
    # Bootstrap 3/4/5
    "#337ab7", "#5cb85c", "#5bc0de", "#f0ad4e", "#d9534f", "#dc3545", "#28a745",
    "#17a2b8", "#ffc107", "#007bff", "#6610f2", "#6f42c1", "#e83e8c", "#fd7e14",
    "#20c997", "#0d6efd", "#198754", "#0dcaf0", "#3c763d", "#8a6d3b", "#a94442",
    "#31708f", "#f2dede", "#dff0d8",
    # WordPress-Editor-Standardpalette
    "#00d084", "#0693e3", "#ff6900", "#fcb900", "#7bdcb5", "#8ed1fc", "#eb144c",
    "#f78da7", "#9b51e0", "#cf2e2e", "#abb8c3", "#ff5e1f",
    # Divi / Wix / Elementor Standard
    "#2ea3f2", "#116dff", "#61ce70", "#6ec1e4", "#4054b2", "#23a455", "#18ce0f",
    "#1863dc", "#dd3333", "#4a8eff", "#ff5062", "#8557d3", "#30b570", "#2ca8ff",
}

ZIEL_SELEKTOREN = re.compile(
    r"(?:^|\})[^{}]*?(?:header|\.header|\.site-header|nav|\.nav|\.navbar|\.btn|button|"
    r"\.button|\.cta|footer|\.footer|\.primary|\.brand|\.hero|\.banner|\.menu)[^{}]*?\{([^}]{0,600})\}",
    re.I | re.S)


def hol(url, t=25):
    try:
        r = subprocess.run(["curl", "-sSL", "--max-time", str(t), "-A", UA,
                            "-w", "\n@@%{http_code}", url], capture_output=True, text=True)
        b, _, c = r.stdout.rpartition("\n@@")
        return b, c.strip()
    except Exception:
        return "", "000"


def norm(c):
    c = c.lower()
    return "#" + ("".join(ch * 2 for ch in c) if len(c) == 3 else c)


def markig(hexv):
    """Ist das eine Farbe, die als Marke taugt — also bunt genug und nicht zu blass?"""
    r, g, b = (int(hexv[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return s >= 0.30 and 0.12 <= l <= 0.86


def hue(hexv):
    r, g, b = (int(hexv[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return colorsys.rgb_to_hls(r, g, b)[0]


def eine(dom):
    basis = None
    home = ""
    for h in (f"https://www.{dom}", f"https://{dom}"):
        home, c = hol(h, 35)
        if c.startswith("2") and len(home) > 500:
            basis = h
            break
    if not basis:
        return dom, {"farben": [], "quelle": "nicht erreichbar"}

    punkte, quelle = {}, []

    # 1. theme-color: die einzige Stelle, an der eine Marke ihre Farbe ausdruecklich benennt
    for m in re.finditer(r'<meta[^>]+name=["\']theme-color["\'][^>]+content=["\']\s*(#[0-9a-fA-F]{3,6})', home, re.I):
        c = norm(m.group(1)[1:])
        if markig(c):
            punkte[c] = punkte.get(c, 0) + 40
            quelle.append("theme-color")

    css = home
    for href in re.findall(r'<link[^>]+rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)', home)[:5]:
        u = href if href.startswith("http") else (
            "https:" + href if href.startswith("//") else basis.rstrip("/") + "/" + href.lstrip("/"))
        t, _ = hol(u, 20)
        css += "\n" + t[:500000]

    # 2. benannte Marken-Variablen
    for m in re.finditer(r"--[\w-]*(?:primary|accent|brand|main|theme|corporate|highlight)[\w-]*\s*:\s*(#[0-9a-fA-F]{3,6})", css, re.I):
        c = norm(m.group(1)[1:])
        if markig(c):
            punkte[c] = punkte.get(c, 0) + 22
            quelle.append("CSS-Variable")

    # 3. Farben auf Kopf, Navigation, Schaltflaechen und Fuss
    for m in ZIEL_SELEKTOREN.finditer(css):
        for c in re.findall(r"(?:background(?:-color)?|border-color|color)\s*:\s*#([0-9a-fA-F]{3,6})\b", m.group(1)):
            c = norm(c)
            if markig(c):
                punkte[c] = punkte.get(c, 0) + 6
                quelle.append("Komponente")

    # 4. schwache Grundzaehlung als Rueckfall
    for c in re.findall(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b", css):
        c = norm(c)
        if markig(c):
            punkte[c] = punkte.get(c, 0) + 1

    for f in FRAMEWORK:
        punkte.pop(f, None)

    gewaehlt, hues = [], []
    for c, _ in sorted(punkte.items(), key=lambda x: -x[1]):
        h = hue(c)
        if all(min(abs(h - h2), 1 - abs(h - h2)) > 0.055 for h2 in hues):
            gewaehlt.append(c)
            hues.append(h)
        if len(gewaehlt) == 3:
            break
    return dom, {"farben": gewaehlt, "quelle": ", ".join(sorted(set(quelle))) or "Grundzählung"}


if __name__ == "__main__":
    doms = list(json.loads((SP / "markt.json").read_text(encoding="utf-8")).keys())
    out = {}
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for d, r in ex.map(eine, doms):
            out[d] = r
            print(f"{d:<24} {str(r['farben']):<36} ← {r['quelle']}")
    (SP / "farben.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
