"""Draw the BeliefGraph architecture figure (paper Fig. 2) as SVG and an HTML preview.

    python3 paper/figures/make_architecture.py
    rsvg-convert -f pdf -o paper/figures/architecture.pdf paper/figures/architecture.svg

Coordinates are in px at 144 px/inch, so the 1032 px width is the 7.16 in IEEE text width and
1 px = 0.5 pt (12 px text prints at 6 pt). The worked example is the one in Fig. 1 (Priya); the
routing probabilities and assignment shading are illustrative.
"""

from pathlib import Path

W, H = 1032, 530
SANS = "Helvetica Neue, Helvetica, Arial, sans-serif"
MATH = "STIX Two Text, Times New Roman, serif"
INK, GRAY, LIGHT = "#222222", "#6B6B6B", "#9A9A9A"

LLM = dict(fill="#FBEBD7", stroke="#C0782E", tag="#9A5414")
DET = dict(fill="#FFFFFF", stroke="#4A4A4A", tag="#555555")
DATA = dict(fill="#EAF1F8", stroke="#3B6E9E", tag="#2F5F8F")
STATUS = {  # fill, stroke, text
    "IN": ("#EDEDED", "#8A8A8A", "#444444"),
    "STALE": ("#F8D3C0", "#C8501A", "#8C3510"),
    "UNK": ("#FBEBB5", "#B98B00", "#7A5C00"),
    "OUT": ("#E9D3EC", "#8B4A92", "#5E2A63"),
}
STALE_EDGE = STATUS["STALE"][1]

out: list[str] = []


def t(x, y, s, size=12, anchor="start", weight="normal", fill=INK, family=SANS, italic=False):
    style = ' font-style="italic"' if italic else ""
    out.append(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" text-anchor="{anchor}" '
               f'font-weight="{weight}" fill="{fill}"{style}>{s}</text>')


def m(s, size=None):
    """Inline math run (italic serif) inside a sans text element."""
    sz = f' font-size="{size}"' if size else ""
    return f'<tspan font-family="{MATH}" font-style="italic"{sz}>{s}</tspan>'


def rect(x, y, w, h, fill, stroke, sw=1.2, rx=5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" '
               f'stroke-width="{sw}"{d}/>')


def line(x1, y1, x2, y2, stroke=INK, sw=1.0, arrow=False, dash=None):
    a = ' marker-end="url(#ah)"' if arrow else ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"{a}{d}/>')


def path(d, stroke=INK, sw=1.0, arrow=False):
    a = ' marker-end="url(#ah)"' if arrow else ""
    out.append(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}"{a}/>')


def circle(x, y, r, fill, stroke, sw=1.1):
    out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def panel(x, y, w, h, kind, title, tag="", sw=1.2):
    rect(x, y, w, h, kind["fill"], kind["stroke"], sw=sw, rx=6)
    t(x + 9, y + 18, title, size=13.5, weight="bold")
    if tag:
        t(x + w - 9, y + 18, tag, size=10.5, anchor="end", fill=kind["tag"])
    line(x + 6, y + 26, x + w - 6, y + 26, stroke=kind["stroke"], sw=0.6)


def chip(x, y, w, label, status, h=17, dash=None):
    f, s, c = STATUS[status] if status else ("#FFFFFF", LIGHT, GRAY)
    rect(x, y, w, h, f, s, sw=1.0, rx=8.5, dash=dash)
    t(x + w / 2, y + h - 5, label, size=10.5, anchor="middle", fill=c, weight="bold" if status else "normal")


def arrow_h(x1, x2, y, label):
    line(x1, y, x2 - 1, y, sw=1.3, arrow=True)
    t((x1 + x2) / 2, y - 6, label, size=12, anchor="middle", family=MATH, italic=True)


def mini_graph(nodes, junctions, edges, status=None, r=10):
    """nodes: id -> (x, y, label); junctions: id -> (x, y); edges: (a, b, kind) where kind marks
    a premise line (into a junction) or a support arrow (out of a junction)."""
    status = status or {}
    for a, b in edges:
        (x1, y1) = nodes[a][:2] if a in nodes else junctions[a]
        (x2, y2) = nodes[b][:2] if b in nodes else junctions[b]
        hot = status.get(a) == "STALE" or (a in junctions and status.get(f"{a}:out") == "STALE")
        if b in nodes:  # junction -> node: stop at the circle edge
            dx, dy = x2 - x1, y2 - y1
            n = (dx * dx + dy * dy) ** 0.5
            x2, y2 = x2 - dx / n * (r + 1), y2 - dy / n * (r + 1)
            line(x1, y1, round(x2, 1), round(y2, 1), stroke=STALE_EDGE if hot else INK, sw=1.3 if hot else 0.9,
                 arrow=True)
        else:
            if a in nodes:
                dx, dy = x2 - x1, y2 - y1
                n = (dx * dx + dy * dy) ** 0.5
                x1, y1 = x1 + dx / n * r, y1 + dy / n * r
            line(round(x1, 1), round(y1, 1), x2, y2, stroke=STALE_EDGE if hot else INK, sw=1.3 if hot else 0.9)
    for j, (x, y) in junctions.items():
        circle(x, y, 2.6, STALE_EDGE if status.get(f"{j}:out") == "STALE" else INK, "none", sw=0)
    for n, (x, y, label) in nodes.items():
        st = status.get(n)
        f, s, c = STATUS[st] if st else ("#FFFFFF", INK, INK)
        circle(x, y, r, f, s, sw=1.3 if st else 1.0)
        t(x, y + 4, m(label), size=12, anchor="middle", fill=c)


def graph_layout(xe, xj, xm, xj4, xm3, y0):
    nodes = {"e1": (xe, y0 + 52, "e₁"), "e2": (xe, y0 + 80, "e₂"), "e4": (xe, y0 + 108, "e₄"),
             "e3": (xe, y0 + 136, "e₃"), "m1": (xm, y0 + 66, "m₁"), "m2": (xm, y0 + 112, "m₂"),
             "m3": (xm3, y0 + 89, "m₃")}
    junctions = {"j1": (xj, y0 + 66), "j2": (xj, y0 + 98), "j3": (xj, y0 + 124), "j4": (xj4, y0 + 89)}
    edges = [("e1", "j1"), ("e2", "j1"), ("j1", "m1"), ("e1", "j2"), ("e4", "j2"), ("j2", "m2"),
             ("e1", "j3"), ("e3", "j3"), ("j3", "m2"), ("m1", "j4"), ("m2", "j4"), ("j4", "m3")]
    return nodes, junctions, edges


# columns (same for both rows) and rows
COLS = [(40, 136), (216, 186), (442, 156), (638, 192), (870, 146)]
R1, R2, PH = 44, 296, 192

# ---------------------------------------------------------------- write time
t(40, 31, '<tspan font-weight="bold" letter-spacing="0.6">WRITE TIME</tspan>'
          '<tspan dx="12" fill="#555555">once per new memory · a few small calls, about 4–5k input tokens, paid once</tspan>',
  size=12.5)
(x0, w0), (x1, w1), (x2, w2), (x3, w3), (x4, w4) = COLS
y = R1

panel(x0, y, w0, PH, DATA, "New memory")
t(x0 + 12, y + 54, m("m₂"), size=21)
for i, s in enumerate(["“Recommended a", "Seattle gym", "membership to", "Priya.”"]):
    t(x0 + 12, y + 78 + i * 16, s, size=12.5)
t(x0 + 12, y + 162, "retrieve the 12", size=10.5, fill=GRAY)
t(x0 + 12, y + 175, "nearest rules", size=10.5, fill=GRAY)

panel(x1, y, w1, PH, LLM, "(a) Route", "LLM · 2 passes")
t(x1 + 10, y + 44, "candidate rules as option letters", size=10.5, fill=GRAY)
rows = [("A", "p₂", "gym rule", 0.78, True), ("B", "p₃", "weekend-plan rule", 0.12, False),
        ("C", "p₁", "restaurant rule", 0.07, False), ("D", "p₄", "renewal rule", 0.02, False)]
for i, (letter, p, name, prob, hl) in enumerate(rows):
    yy = y + 64 + i * 24
    rect(x1 + 10, yy - 11, 14, 14, "#FFFFFF", LLM["stroke"], sw=0.9, rx=2)
    t(x1 + 17, yy, letter, size=10, anchor="middle", weight="bold", fill=LLM["tag"])
    t(x1 + 31, yy, f'{m(p)} {name}', size=11.5)
    out.append(f'<rect x="{x1 + 31}" y="{yy + 3}" width="{round(prob * 140, 1)}" height="4.5" '
               f'fill="{LLM["stroke"] if hl else "#DDBB94"}"/>')
t(x1 + 31, y + 156, "⋮  8 more", size=10.5, fill=GRAY)
t(x1 + 10, y + 172, m('q<tspan font-size="8.5" dy="2.5">m</tspan><tspan dy="-2.5" font-style="normal" font-family="' + SANS + '">: next-letter probabilities</tspan>'), size=10.5, fill=GRAY)
t(x1 + 10, y + 185, "two option orders, averaged", size=10.5, fill=GRAY)

panel(x2, y, w2, PH, DET, "(b) Assign", "no LLM")
t(x2 + 10, y + 44, "memories that name Priya", size=10.5, fill=GRAY)
q = [[0.80, 0.08, 0.12], [0.10, 0.78, 0.12], [0.05, 0.50, 0.45]]
cx0, cy0, cs = x2 + 48, y + 64, 30
for j, p in enumerate(["p₁", "p₂", "p₃"]):
    t(cx0 + j * cs + cs / 2, cy0 - 6, m(p), size=12, anchor="middle")
for i, mm in enumerate(["m₁", "m₂", "m₃"]):
    t(cx0 - 8, cy0 + i * cs + cs / 2 + 4, m(mm), size=12, anchor="end")
    for j in range(3):
        out.append(f'<rect x="{cx0 + j * cs}" y="{cy0 + i * cs}" width="{cs}" height="{cs}" '
                   f'fill="#3B6E9E" fill-opacity="{round(q[i][j] * 0.7, 3)}" stroke="#FFFFFF" stroke-width="1.5"/>')
for i in range(3):
    circle(cx0 + i * cs + cs / 2, cy0 + i * cs + cs / 2, 10.5, "none", INK, sw=1.6)
# greedy would take m3 -> p2 (its highest q), which p2's own memory m2 already holds
out.append(f'<rect x="{cx0 + cs + 4}" y="{cy0 + 2 * cs + 4}" width="{cs - 8}" height="{cs - 8}" fill="none" '
           f'stroke="{STALE_EDGE}" stroke-width="1.2" stroke-dasharray="3 2"/>')
t(x2 + 10, y + 172, "max Σ log q, ≤ 1 per rule", size=10.5, fill=GRAY)
t(x2 + 10, y + 185, f'{m("m₃")}: greedy <tspan fill="{STALE_EDGE}">{m("p₂")}</tspan>, joint {m("p₃")}',
  size=10.5, fill=GRAY)

panel(x3, y, w3, PH, LLM, "(c) Ground", "LLM · 3 samples")
t(x3 + 10, y + 44, f'condition of {m("p₂")}, as OR of ANDs', size=10.5, fill=GRAY)
t(x3 + w3 / 2, y + 66, "city ∧ (exercises ∨ employer pays)", size=11.5, anchor="middle")
t(x3 + w3 / 2, y + 84, "↓ each to one of 16 nearest items", size=10.5, anchor="middle", fill=GRAY)
t(x3 + w3 / 2, y + 108, m("J(m₂) = {e₁, e₄} ∨ {e₁, e₃}"), size=15, anchor="middle")
for k in range(3):
    xx = x3 + 22 + k * 52
    rect(xx, y + 124, 44, 18, "#FFFFFF", LLM["stroke"], sw=0.9, rx=9)
    t(xx + 22, y + 137, f'{m("s" + "₁₂₃"[k])} ✓', size=11, anchor="middle")
t(x3 + 10, y + 172, "sets in ≥ 2 of 3 samples kept;", size=10.5, fill=GRAY)
t(x3 + 10, y + 185, "no support → one retry, then reported", size=10.5, fill=GRAY)

panel(x4, y, w4, PH, DATA, "(d) Graph", "stored")
nodes, junctions, edges = graph_layout(x4 + 20, x4 + 52, x4 + 84, x4 + 108, x4 + 128, y)
mini_graph(nodes, junctions, edges)
t(x4 + 10, y + 172, "+ source reliability", size=10.5, fill=GRAY)
t(x4 + 10, y + 185, "built incrementally", size=10.5, fill=GRAY)

arrow_h(x0 + w0, x1, y + 96, "m₂")
arrow_h(x1 + w1, x2, y + 96, "q")
arrow_h(x2 + w2, x3, y + 96, "p₂")
arrow_h(x3 + w3, x4, y + 96, "J")

# ---------------------------------------------------------------- update time
y = R2
t(40, y - 13, '<tspan font-weight="bold" letter-spacing="0.6">UPDATE TIME</tspan>'
              '<tspan dx="12" fill="#555555">once per update · one LLM call of about 1.4k input tokens, flat in store size</tspan>',
  size=12.5)

panel(x0, y, w0, PH, DATA, "Update")
t(x0 + 12, y + 54, m("u₁"), size=21)
for i, s in enumerate(["“I just finished", "settling into my", "new place in", "Austin.”"]):
    t(x0 + 12, y + 78 + i * 16, s, size=12.5)
t(x0 + 12, y + 162, "source: user,", size=10.5, fill=GRAY)
t(x0 + 12, y + 175, "in conversation", size=10.5, fill=GRAY)

panel(x1, y, w1, PH, LLM, "(e) Read", "LLM · 1 call")
t(x1 + 10, y + 44, "12 nearest facts", size=10.5, fill=GRAY)
facts = [("e₁", "Priya lives in Seattle.", True), ("e₂", "Priya is vegetarian.", False),
         ("e₄", "Priya runs 3× a week.", False)]
for i, (e, s, hl) in enumerate(facts):
    yy = y + 62 + i * 17
    if hl:
        rect(x1 + 6, yy - 12, w1 - 12, 16, STATUS["STALE"][0], STATUS["STALE"][1], sw=0.8, rx=3)
    t(x1 + 12, yy, f'{m(e)}  {s}', size=11.5)
t(x1 + 12, y + 111, "⋮", size=11, fill=GRAY)
line(x1 + 8, y + 118, x1 + w1 - 8, y + 118, stroke=LLM["stroke"], sw=0.6)
for i, (k, v) in enumerate([("target", m("e₁")), ("relation", "supersedes"), ("source", "high")]):
    yy = y + 136 + i * 16
    t(x1 + 12, yy, k, size=11.5, fill=GRAY)
    t(x1 + 78, yy, v, size=11.5, weight="bold")
t(x1 + 12, y + 185, "relation from what is claimed", size=10.5, fill=GRAY)

panel(x2, y, w2, PH, DET, "(f) Effect", "no LLM")
t(x2 + 10, y + 44, f'status of the target {m("e₁")}', size=10.5, fill=GRAY)
rules = [("older than e₁", "ignore", None), ("hedged / weaker", "UNK", "UNK"),
         ("retracts", "OUT", "OUT"), ("supersedes", "STALE", "STALE")]
for i, (cond, lab, st) in enumerate(rules):
    yy = y + 52 + i * 26
    taken = st == "STALE"
    if taken:
        rect(x2 + 5, yy - 2, w2 - 10, 22, "#FDF1EA", STATUS["STALE"][1], sw=0.8, rx=3)
    cond = cond.replace("e₁", m("e₁"))
    t(x2 + 11, yy + 13, cond, size=11.5, weight="bold" if taken else "normal", fill=INK if taken else GRAY)
    chip(x2 + w2 - 50, yy + 1, 42, lab, st, dash=None if st else "2 2")
t(x2 + 10, y + 168, "first matching row applies", size=10.5, fill=GRAY)
t(x2 + w2 / 2, y + 186, m('σ(e₁) = <tspan font-style="normal" font-family="' + SANS + '" font-size="11.5">STALE</tspan>'), size=13.5, anchor="middle")

panel(x3, y, w3, PH, DET, "(g) Propagate", "no LLM · ms", sw=2.2)
nodes, junctions, edges = graph_layout(x3 + 30, x3 + 74, x3 + 114, x3 + 144, x3 + 170, y)
status = {"e1": "STALE", "e2": "IN", "e3": "IN", "e4": "IN", "m1": "STALE", "m2": "STALE", "m3": "STALE",
          "j1:out": "STALE", "j2:out": "STALE", "j3:out": "STALE", "j4:out": "STALE"}
mini_graph(nodes, junctions, edges, status)
t(x3 + w3 / 2, y + 172,
  m('σ(m) = <tspan font-style="normal">max</tspan><tspan font-size="9" dy="3">A∈J(m)</tspan><tspan dy="-3" font-style="normal"> min</tspan>'
    '<tspan font-size="9" dy="3">x∈A</tspan><tspan dy="-3"> σ(x)</tspan>'),
  size=13.5, anchor="middle")
t(x3 + w3 / 2, y + 187, "OUT &lt; UNK &lt; STALE &lt; IN", size=10.5, anchor="middle", fill=GRAY)

panel(x4, y, w4, PH, DATA, "(h) Actions", "to caller")
acts = [("m₁", "recompute", "STALE"), ("m₂", "recompute", "STALE"), ("m₃", "recompute", "STALE"),
        ("rest", "keep", "IN")]
for i, (mm, lab, st) in enumerate(acts):
    yy = y + 44 + i * 23
    t(x4 + 14, yy + 13, m(mm) if mm != "rest" else "others", size=12 if mm != "rest" else 10.5,
      fill=INK if mm != "rest" else GRAY)
    chip(x4 + 56, yy, 76, lab, st)
line(x4 + 8, y + 140, x4 + w4 - 8, y + 140, stroke=DATA["stroke"], sw=0.6)
t(x4 + 10, y + 157, f'if only {m("u₂")} arrived (weak):', size=10.5, fill=GRAY)
t(x4 + 10, y + 171, f'{m("e₃")} uncertain, {m("m₂")} kept', size=10.5, fill=GRAY)
t(x4 + 10, y + 185, f'via {m("{e₁, e₄}")}', size=10.5, fill=GRAY)

arrow_h(x0 + w0, x1, y + 96, "u₁")
arrow_h(x1 + w1, x2, y + 96, "e₁, ρ")
arrow_h(x2 + w2, x3, y + 96, "σ")
arrow_h(x3 + w3, x4, y + 96, "σ")

# the stored graph is read by propagation (P4 bottom -> P8 top)
gx, px = x4 + w4 / 2, x3 + w3 / 2
path(f"M{gx},{R1 + PH} V{R1 + PH + 24} H{px + 40} V{R2 - 1}", stroke=DATA["stroke"], sw=1.3, arrow=True)
t(gx - 8, R1 + PH + 18, f'{m("J")} (read only)', size=11.5, anchor="end", fill=DATA["tag"])

# ---------------------------------------------------------------- legend
ly = 512
items = [(LLM, "LLM call"), (DET, "deterministic"), (DATA, "stored or returned")]
lx = 40
for kind, lab in items:
    rect(lx, ly - 10, 22, 13, kind["fill"], kind["stroke"], sw=1.0, rx=3)
    t(lx + 28, ly + 1, lab, size=11)
    lx += 34 + len(lab) * 6.2
lx += 18
for st, lab in [("IN", "IN · keep"), ("STALE", "STALE · recompute"), ("UNK", "UNK · uncertain"),
                ("OUT", "OUT · withdraw")]:
    f, s, c = STATUS[st]
    circle(lx + 6, ly - 3.5, 6, f, s, sw=1.2)
    t(lx + 17, ly + 1, lab, size=11)
    lx += 30 + len(lab) * 6.0

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
       f'aria-label="BeliefGraph: a write path that records why each memory is believed, and an update path that '
       f'reads one update and propagates statuses over the recorded graph">\n'
       f'<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
       f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs>\n'
       f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>\n' + "\n".join(out) + "\n</svg>\n")
here = Path(__file__).parent
(here / "architecture.svg").write_text(svg)
(here / "architecture.html").write_text(
    "<!doctype html><html><head><meta charset='utf-8'><title>BeliefGraph architecture</title>"
    "<style>body{margin:24px;background:#fff;font-family:Helvetica Neue,Helvetica,Arial,sans-serif}"
    "figure{margin:0;max-width:1100px}svg{max-width:100%;height:auto}figcaption{font-size:13px;color:#444;"
    "margin-top:8px}</style></head><body><figure>" + svg +
    "<figcaption>BeliefGraph v0.8 on the worked example of Fig. 1. Top: the write path records why a memory is "
    "believed. Bottom: the update path reads one update and propagates statuses over the recorded graph."
    "</figcaption></figure></body></html>\n")
print("wrote", here / "architecture.svg")
