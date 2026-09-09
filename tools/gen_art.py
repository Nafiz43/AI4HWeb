"""Generate the symposium artwork as SVG. Run from the repo root."""
import math

NAVY, MID, GOLD = '#022851', '#1a4166', '#ffbf00'

DEFS = '''  <defs>
    <linearGradient id="ground" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fdfaf3"/><stop offset="1" stop-color="#f3ece0"/>
    </linearGradient>
    <radialGradient id="ball" cx=".34" cy=".3" r=".78">
      <stop offset="0" stop-color="#5b8ab8"/><stop offset=".55" stop-color="#1a4166"/><stop offset="1" stop-color="#022851"/>
    </radialGradient>
    <radialGradient id="goldball" cx=".34" cy=".3" r=".78">
      <stop offset="0" stop-color="#ffe9a3"/><stop offset=".55" stop-color="#ffbf00"/><stop offset="1" stop-color="#b98600"/>
    </radialGradient>
    <linearGradient id="rod" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="__H__">
      <stop offset="0" stop-color="#ffd75e"/><stop offset=".5" stop-color="#e5a800"/><stop offset="1" stop-color="#c08f00"/>
    </linearGradient>
    <linearGradient id="glass" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#8fb4d4" stop-opacity=".55"/><stop offset="1" stop-color="#1a4166" stop-opacity=".65"/>
    </linearGradient>
  </defs>
'''


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{title}">\n{DEFS.replace("__H__", str(h))}'
            f'  <rect width="{w}" height="{h}" fill="url(#ground)"/>\n{body}</svg>\n')


def shadow(cx, cy, rx, ry=None, o=.13):
    return f'  <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry or rx*0.16:.0f}" fill="{NAVY}" opacity="{o}"/>\n'


def sphere(x, y, r, gold=False):
    fill = 'url(#goldball)' if gold else 'url(#ball)'
    return (f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}"/>'
            f'<circle cx="{x - r*.3:.1f}" cy="{y - r*.34:.1f}" r="{r*.22:.1f}" fill="#fff" opacity=".45"/>\n')


# ---------------------------------------------------------------- 01 lattice
def lattice():
    xs, ys = [178, 288, 398], [186, 268, 350]
    off = (74, -62)
    front = [(x, y) for y in ys for x in xs]
    back = [(x + off[0], y + off[1]) for x, y in front]
    out = shadow(320, 372, 168)
    bonds = []
    for grid, w, op in ((back, 5, .5), (front, 7, 1)):
        for i, (x, y) in enumerate(grid):
            if i % 3 < 2:
                bonds.append((grid[i], grid[i + 1], w, op))
            if i < 6:
                bonds.append((grid[i], grid[i + 3], w, op))
    for a, b in zip(front, back):
        bonds.append((a, b, 5, .65))
    for (x1, y1), (x2, y2), w, op in bonds:
        out += (f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="url(#rod)" '
                f'stroke-width="{w}" stroke-linecap="round" opacity="{op}"/>\n')
    for x, y in back:
        out += sphere(x, y, 15)
    for i, (x, y) in enumerate(front):
        out += sphere(x, y, 21, gold=(i == 4))
    return svg(640, 400, out, 'Lattice of linked spheres representing basic science')


# ------------------------------------------------------- 02 stacked compute
def layers():
    out = shadow(320, 352, 152)
    cx, hw, hd, t = 320, 106, 40, 13
    plates = ((272, False), (200, True), (128, False))
    for y, gold in plates:
        L, T, R, B = (cx - hw, y), (cx, y - hd), (cx + hw, y), (cx, y + hd)
        face = 'url(#goldball)' if gold else 'url(#glass)'
        side = '#c08f00' if gold else '#33587c'
        out += (f'  <polygon points="{L[0]},{L[1]} {B[0]},{B[1]} {R[0]},{R[1]} '
                f'{R[0]},{R[1]+t} {B[0]},{B[1]+t} {L[0]},{L[1]+t}" fill="{side}" opacity=".8"/>\n')
        out += (f'  <polygon points="{L[0]},{L[1]} {T[0]},{T[1]} {R[0]},{R[1]} {B[0]},{B[1]}" '
                f'fill="{face}" opacity="{".9" if gold else ".95"}" stroke="{MID}" '
                f'stroke-width="2" stroke-opacity=".45"/>\n')
    # a node on each side of every plate, wired to that plate's edge
    for y, _ in plates:
        for sx, ex, bend in ((92, cx - hw, -34), (548, cx + hw, -34)):
            out += (f'  <path d="M{sx} {y} Q{(sx+ex)//2} {y+bend} {ex} {y}" fill="none" '
                    f'stroke="url(#rod)" stroke-width="4.5" stroke-linecap="round"/>\n')
        out += sphere(92, y, 16) + sphere(548, y, 16)
    out += sphere(cx, 60, 14, gold=True)
    out += (f'  <path d="M{cx} 74 L{cx} 88" stroke="url(#rod)" stroke-width="4.5" stroke-linecap="round"/>\n')
    return svg(640, 400, out, 'Stacked computational layers wired to surrounding nodes')


# ------------------------------------------------------------- 03 hyperboloid
def hyperboloid():
    cx, rx, ry, top, bot, twist = 320, 122, 32, 112, 306, math.radians(132)
    out = shadow(320, 340, 140)

    def pt(a, y):
        return cx + rx * math.cos(a), y + ry * math.sin(a)

    lines = []
    for k in range(28):
        a = 2 * math.pi * k / 28
        for d in (twist, -twist):
            x1, y1 = pt(a, top)
            x2, y2 = pt(a + d, bot)
            depth = (math.sin(a) + math.sin(a + d)) / 2      # +1 = front of the form
            lines.append((depth, x1, y1, x2, y2))
    for depth, x1, y1, x2, y2 in sorted(lines):
        op = .18 + .5 * (depth + 1) / 2
        out += (f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{NAVY}" stroke-width="1.6" opacity="{op:.2f}"/>\n')
    for y in (top, bot):
        out += (f'  <ellipse cx="{cx}" cy="{y}" rx="{rx}" ry="{ry}" fill="none" '
                f'stroke="{MID}" stroke-width="3" opacity=".85"/>\n')
    out += (f'  <ellipse cx="{cx}" cy="209" rx="176" ry="60" fill="none" stroke="url(#rod)" '
            f'stroke-width="5" transform="rotate(-18 {cx} 209)"/>\n')
    out += sphere(487, 148, 16, gold=True)
    return svg(640, 400, out, 'Ruled hyperboloid surface ringed by an orbit, representing theory')


# ---------------------------------------------------------------- 04 signal
def signal():
    cx, cy = 320, 196
    out = shadow(320, 350, 150)
    for r, op in ((146, .28), (112, .38), (78, .5)):
        out += (f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#glass)" opacity="{op}" '
                f'stroke="{MID}" stroke-width="2" stroke-opacity=".45"/>\n')
    out += sphere(cx, cy, 46, gold=True)
    trace = ('M46 196 H150 L172 196 L190 152 L208 250 L228 172 L246 196 H286 '
             'L306 196 L322 104 L340 292 L358 196 H430 L452 196 L470 158 L486 236 L502 196 H594')
    out += (f'  <path d="{trace}" fill="none" stroke="url(#rod)" stroke-width="7" '
            f'stroke-linejoin="round" stroke-linecap="round"/>\n')
    out += sphere(46, 196, 13, gold=True) + sphere(594, 196, 13, gold=True)
    return svg(640, 400, out, 'Health signal passing through concentric discs')


# ------------------------------------------------------------------- hero
def hero():
    """One idea, read left to right: a network of people and data becomes a
    health signal, and lands on a single outcome."""
    W, H = 1200, 700          # cropped tight to the composition
    out = ('  <radialGradient id="glow" cx=".5" cy=".5" r=".5">'
           '<stop offset="0" stop-color="#ffbf00" stop-opacity=".55"/>'
           '<stop offset="1" stop-color="#ffbf00" stop-opacity="0"/></radialGradient>\n')

    # the ribbon: data carrying across the frame
    out += ('  <path d="M-60 430 C 190 264, 372 620, 610 432 S 1000 214, 1260 362" fill="none" '
            'stroke="url(#glass)" stroke-width="126" stroke-linecap="round" opacity=".8"/>\n')
    out += (f'  <path d="M-60 528 C 214 386, 396 706, 636 528 S 1014 318, 1260 476" fill="none" '
            f'stroke="{MID}" stroke-width="40" stroke-linecap="round" opacity=".22"/>\n')

    # one network, denser on the left, thinning as it feeds into the signal
    nodes = [(78, 236), (168, 168), (150, 322), (262, 246), (238, 400), (330, 150),
             (352, 330), (300, 520), (432, 236), (412, 452), (516, 158), (524, 348),
             (470, 590), (612, 250), (596, 462), (700, 168), (724, 344), (836, 236),
             (880, 128), (960, 300), (1064, 190), (1126, 288)]
    edges = set()
    for i, a in enumerate(nodes):
        near = sorted(range(len(nodes)), key=lambda j: math.dist(a, nodes[j]))[1:4]
        for j in near:
            if math.dist(a, nodes[j]) < 205:
                edges.add((min(i, j), max(i, j)))
    for i, j in sorted(edges):
        (x1, y1), (x2, y2) = nodes[i], nodes[j]
        fade = .34 - .2 * (x1 + x2) / (2 * W)        # thins out towards the right
        out += (f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{MID}" '
                f'stroke-width="1.7" opacity="{fade:.2f}"/>\n')
    for i, (x, y) in enumerate(nodes):
        r = 13 - 5 * (x / W)                          # smaller with distance
        out += sphere(x, y, r, gold=(i in (4, 13)))

    # the signal: leaves the network, steadies, beats, and arrives
    out += ('  <path d="M78 236 C 200 292, 236 392, 342 420 S 520 452, 616 470 '
            'L742 470 L764 470 L784 418 L806 552 L828 436 L848 470 L900 470 '
            'L920 470 L938 400 L956 540 L974 470 L1046 470" fill="none" stroke="url(#rod)" '
            'stroke-width="7" stroke-linejoin="round" stroke-linecap="round"/>\n')

    out += '  <circle cx="1072" cy="470" r="86" fill="url(#glow)"/>\n'
    out += sphere(1072, 470, 26, gold=True)
    return svg(W, H, out, 'A research network flowing into a health signal')


for name, fn in (('topic-basic', lattice), ('topic-methods', layers), ('topic-theory', hyperboloid),
                 ('topic-clinical', signal), ('symposium-hero', hero)):
    open(f'img/{name}.svg', 'w').write(fn())
    print('wrote', name)
