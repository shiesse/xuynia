"""
gfx.py — мини-библиотека для построения диаграмм (DFD / IDEF3 / IDEF1X).

Одна и та же "сцена" (Scene) рендерится двумя бэкендами:
  * render_svg() -> строка SVG (вектор, для GitHub / сайта / печати);
  * render_png() -> растр через Pillow (для вставки в Word, презентации).

Геометрия (стрелки, "гусиные лапки", рамки) считается один раз в Python,
поэтому SVG и PNG выглядят идентично и не зависят от поддержки <marker>
или dominant-baseline конкретным просмотрщиком.

Текст задаётся базовой линией (baseline) — так же, как в типографике,
чтобы SVG одинаково выглядел в браузере, в Word и при конвертации camo.
"""
from __future__ import annotations

import html
import math
import os
from typing import Sequence

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
FONT_FILES = {
    ("sans", "regular"): "DejaVuSans.ttf",
    ("sans", "bold"): "DejaVuSans-Bold.ttf",
    ("sans", "italic"): "DejaVuSans-Oblique.ttf",
    ("mono", "regular"): "DejaVuSansMono.ttf",
    ("mono", "bold"): "DejaVuSansMono.ttf",
    ("mono", "italic"): "DejaVuSansMono.ttf",
}
SVG_FONT_FAMILY = {
    "sans": "'DejaVu Sans','Liberation Sans',Arial,Helvetica,sans-serif",
    "mono": "'DejaVu Sans Mono','Liberation Mono',Consolas,monospace",
}

# Базовая линия однострочного текста, визуально отцентрованного по cy
BASELINE_K = 0.355  # для DejaVu Sans: (capheight/2) примерно 0.36 em

_pil_fonts: dict = {}


def _pil_font(size: float, family: str = "sans", weight: str = "regular"):
    """Шрифт Pillow, закэшированный по целому размеру в пикселях."""
    key = (family, weight, int(round(size)))
    if key not in _pil_fonts:
        from PIL import ImageFont

        path = os.path.join(FONT_DIR, FONT_FILES[(family, weight)])
        _pil_fonts[key] = ImageFont.truetype(path, int(round(size)))
    return _pil_fonts[key]


def measure(text: str, size: float, family: str = "sans", weight: str = "regular") -> float:
    """Ширина строки в условных единицах сцены (пикселях диаграммы)."""
    return float(_pil_font(size, family, weight).getlength(text))


def wrap(text: str, size: float, max_width: float, family: str = "sans",
         weight: str = "regular") -> list[str]:
    """Перенос строки по словам так, чтобы она влезла в max_width.
    Символ \\n задаёт принудительный разрыв строки."""
    if "\n" in text:
        out: list[str] = []
        for part in text.split("\n"):
            out.extend(wrap(part, size, max_width, family, weight))
        return out
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    cur = words[0]
    for w in words[1:]:
        trial = cur + " " + w
        if measure(trial, size, family, weight) <= max_width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def fit(text: str, size: float, max_width: float, family: str = "sans",
        weight: str = "regular") -> tuple[list[str], float]:
    """Возвращает (строки, подобранный размер шрифта) — уменьшает шрифт,
    если текст не влезает даже после переносов (не более чем на 3 шага)."""
    for s in (size, size - 1, size - 2, size - 3):
        lines = wrap(text, s, max_width, family, weight)
        if max((measure(l, s, family, weight) for l in lines), default=0) <= max_width:
            return lines, s
    return wrap(text, size - 3, max_width, family, weight), size - 3


# --------------------------------------------------------------------------- #
#  Сцена
# --------------------------------------------------------------------------- #

class Scene:
    """Список графических примитивов + два рендерера."""

    def __init__(self, width: float, height: float, bg: str = "#ffffff"):
        self.width = width
        self.height = height
        self.bg = bg
        self.items: list[dict] = []

    # --- примитивы -------------------------------------------------------- #
    def rect(self, x, y, w, h, fill=None, stroke="#1f3b63", sw=1.6, rx=0,
             dash=None, opacity=1.0, z=None):
        self.items.append(dict(kind="rect", x=x, y=y, w=w, h=h, fill=fill,
                               stroke=stroke, sw=sw, rx=rx, dash=dash,
                               opacity=opacity, z=z or 0))

    def poly(self, points, fill=None, stroke=None, sw=1.6, dash=None,
             close=False, opacity=1.0, z=None, join="round"):
        self.items.append(dict(kind="poly", points=[tuple(p) for p in points],
                               fill=fill, stroke=stroke, sw=sw, dash=dash,
                               close=close, opacity=opacity, z=z or 0, join=join))

    def ellipse(self, cx, cy, rx, ry, fill=None, stroke="#1f3b63", sw=1.6,
                dash=None, opacity=1.0, z=None):
        self.items.append(dict(kind="ellipse", cx=cx, cy=cy, rx=rx, ry=ry,
                               fill=fill, stroke=stroke, sw=sw, dash=dash,
                               opacity=opacity, z=z or 0))

    def text(self, x, y, lines, size=13, weight="regular", anchor="middle",
             color="#14213d", family="sans", spacing=1.3, underline=False,
             opacity=1.0, z=None):
        """y — базовая линия ПЕРВОЙ строки; lines — строка или список строк."""
        if isinstance(lines, str):
            lines = [lines]
        self.items.append(dict(kind="text", x=x, y=y, lines=list(lines), size=size,
                               weight=weight, anchor=anchor, color=color,
                               family=family, spacing=spacing, underline=underline,
                               opacity=opacity, z=z or 0))

    def text_center(self, x, cy, text_, size=13, weight="regular", anchor="middle",
                    color="#14213d", family="sans", spacing=1.3, underline=False,
                    max_width=None, z=None):
        """Текст (блок строк), вертикально отцентрованный относительно cy."""
        if max_width is not None:
            lines, size = fit(text_, size, max_width, family, weight)
        else:
            lines = wrap(text_, size, 10 ** 6, family, weight) if isinstance(text_, str) else list(text_)
        n = len(lines)
        first_baseline = cy - (n - 1) * size * spacing / 2 + size * BASELINE_K
        self.text(x, first_baseline, lines, size=size, weight=weight, anchor=anchor,
                  color=color, family=family, spacing=spacing, underline=underline, z=z)
        return lines

    # --- стрелки ---------------------------------------------------------- #
    def arrow(self, points, color="#37474f", sw=1.9, dash=None, head=11.0,
              head_at="end", opacity=1.0, z=None):
        """Ломаная с наконечником. head_at: 'end' | 'both' | 'none'."""
        pts = [tuple(p) for p in points]
        body, heads = self._arrow_geometry(pts, head, head_at, sw)
        self.poly(body, stroke=color, sw=sw, dash=dash, opacity=opacity, z=z)
        for h in heads:
            self.poly(h, fill=color, stroke=color, sw=0.6, close=True,
                      opacity=opacity, z=(z or 0) + 1)
        return body, heads

    @staticmethod
    def _arrow_geometry(pts, head, head_at, sw):
        pts = [p for i, p in enumerate(pts) if i == 0 or p != pts[i - 1]]
        heads = []
        body = list(pts)
        if head_at in ("end", "both") and len(pts) >= 2:
            tip, base, tri = _arrowhead(pts[-2], pts[-1], head)
            heads.append(tri)
            body[-1] = base
        if head_at == "both" and len(pts) >= 2:
            tip, base, tri = _arrowhead(pts[1], pts[0], head)
            heads.append(tri)
            body[0] = base
        return body, heads


def _unit(v):
    n = math.hypot(v[0], v[1])
    return (v[0] / n, v[1] / n) if n else (1.0, 0.0)


def _arrowhead(p_from, p_to, head):
    """Треугольник-наконечник: tip, base (точка уреза линии), полигон."""
    dx, dy = _unit((p_to[0] - p_from[0], p_to[1] - p_from[1]))
    px, py = -dy, dx
    base = (p_to[0] - dx * head, p_to[1] - dy * head)
    w = head * 0.42
    tri = [p_to, (base[0] + px * w, base[1] + py * w), (base[0] - px * w, base[1] - py * w)]
    return p_to, base, tri


# --------------------------------------------------------------------------- #
#  Бэкенд 1: SVG
# --------------------------------------------------------------------------- #

def _dash(dash):
    if not dash:
        return ""
    if isinstance(dash, str):
        return f' stroke-dasharray="{dash}"'
    return ' stroke-dasharray="{}"'.format(" ".join(str(d) for d in dash))


def render_svg(scene: Scene) -> str:
    items = sorted(scene.items, key=lambda it: it.get("z", 0))
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{scene.width:g}" height="{scene.height:g}" '
        f'viewBox="0 0 {scene.width:g} {scene.height:g}" font-family="{SVG_FONT_FAMILY["sans"]}", '
        'role="img">',
        f'<rect x="0" y="0" width="{scene.width:g}" height="{scene.height:g}" fill="{scene.bg}"/>',
    ]
    for it in items:
        k = it["kind"]
        op = f' opacity="{it["opacity"]:g}"' if it.get("opacity", 1) != 1 else ""
        if k == "rect":
            fill = it["fill"] or "none"
            stroke = it["stroke"] or "none"
            rx = f' rx="{it["rx"]:g}" ry="{it["rx"]:g}"' if it["rx"] else ""
            out.append(f'<rect x="{it["x"]:g}" y="{it["y"]:g}" width="{it["w"]:g}" height="{it["h"]:g}"'
                       f' fill="{fill}" stroke="{stroke}" stroke-width="{it["sw"]:g}"{rx}{_dash(it["dash"])}{op}/>')
        elif k == "ellipse":
            fill = it["fill"] or "none"
            stroke = it["stroke"] or "none"
            out.append(f'<ellipse cx="{it["cx"]:g}" cy="{it["cy"]:g}" rx="{it["rx"]:g}" ry="{it["ry"]:g}"'
                       f' fill="{fill}" stroke="{stroke}" stroke-width="{it["sw"]:g}"{_dash(it["dash"])}{op}/>')
        elif k == "poly":
            pts = " ".join(f"{x:g},{y:g}" for x, y in it["points"])
            fill = it["fill"] or "none"
            stroke = it["stroke"] or "none"
            close = "Z" if it["close"] else ""
            out.append(f'<path d="M {pts.replace(" ", " L ")}{close}" fill="{fill}" stroke="{stroke}" '
                       f'stroke-width="{it["sw"]:g}" stroke-linejoin="{it["join"]}" stroke-linecap="round"'
                       f'{_dash(it["dash"])}{op}/>')
        elif k == "text":
            fam = SVG_FONT_FAMILY[it["family"]]
            weight = ' font-weight="bold"' if it["weight"] == "bold" else ""
            style = ' font-style="italic"' if it["weight"] == "italic" else ""
            anchor = {"middle": "middle", "start": "start", "end": "end"}[it["anchor"]]
            dy = it["size"] * it["spacing"]
            tspans = []
            for i, ln in enumerate(it["lines"]):
                y = it["y"] + i * dy
                tspans.append(f'<tspan x="{it["x"]:g}" y="{y:g}">{html.escape(ln)}</tspan>')
            deco = ' text-decoration="underline"' if it.get("underline") else ""
            out.append(f'<text font-family="{fam}" font-size="{it["size"]:g}" fill="{it["color"]}" '
                       f'text-anchor="{anchor}"{weight}{style}{deco}{op}>{"".join(tspans)}</text>')
    out.append("</svg>")
    return "\n".join(out)


# --------------------------------------------------------------------------- #
#  Бэкенд 2: PNG (Pillow)
# --------------------------------------------------------------------------- #

def render_png(scene: Scene, path: str, scale: float = 2.0, supersample: float = 3.0):
    from PIL import Image, ImageDraw

    S = supersample
    W, H = int(round(scene.width * S)), int(round(scene.height * S))
    img = Image.new("RGB", (W, H), scene.bg)
    d = ImageDraw.Draw(img)

    def sc(p):
        return (p[0] * S, p[1] * S)

    for it in sorted(scene.items, key=lambda i: i.get("z", 0)):
        k = it["kind"]
        sw = it.get("sw", 0) * S
        if k == "rect":
            x0, y0 = it["x"] * S, it["y"] * S
            x1, y1 = (it["x"] + it["w"]) * S, (it["y"] + it["h"]) * S
            r = it["rx"] * S
            if it["fill"]:
                d.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=it["fill"])
            if it["stroke"]:
                dash = it.get("dash")
                if dash:
                    _dashed_rect(d, x0, y0, x1, y1, r, it["stroke"], sw, dash, S)
                else:
                    d.rounded_rectangle([x0, y0, x1, y1], radius=r, outline=it["stroke"], width=max(1, int(round(sw))))
        elif k == "ellipse":
            x0, y0 = (it["cx"] - it["rx"]) * S, (it["cy"] - it["ry"]) * S
            x1, y1 = (it["cx"] + it["rx"]) * S, (it["cy"] + it["ry"]) * S
            if it["fill"]:
                d.ellipse([x0, y0, x1, y1], fill=it["fill"])
            if it["stroke"]:
                d.ellipse([x0, y0, x1, y1], outline=it["stroke"], width=max(1, int(round(sw))))
        elif k == "poly":
            pts = [sc(p) for p in it["points"]]
            if it["close"]:
                pts_c = pts + [pts[0]]
                if it["fill"]:
                    d.polygon(pts_c, fill=it["fill"])
                if it["stroke"]:
                    d.line(pts_c, fill=it["stroke"], width=max(1, int(round(sw))), joint="curve")
            else:
                if it["fill"]:
                    d.polygon(pts, fill=it["fill"])
                if it["stroke"]:
                    if it.get("dash"):
                        _dashed_poly(d, pts, it["stroke"], max(1, int(round(sw))), it["dash"], S)
                    else:
                        d.line(pts, fill=it["stroke"], width=max(1, int(round(sw))), joint="curve")
        elif k == "text":
            font = _pil_font(it["size"] * S, it["family"], it["weight"])
            for i, ln in enumerate(it["lines"]):
                y = (it["y"] + i * it["size"] * it["spacing"]) * S
                x = it["x"] * S
                anchor = {"middle": "ms", "start": "ls", "end": "rs"}[it["anchor"]]
                d.text((x, y), ln, font=font, fill=it["color"], anchor=anchor)
                if it.get("underline"):
                    wpx = font.getlength(ln)
                    if it["anchor"] == "middle":
                        x0, x1 = x - wpx / 2, x + wpx / 2
                    elif it["anchor"] == "end":
                        x0, x1 = x - wpx, x
                    else:
                        x0, x1 = x, x + wpx
                    yy = y + it["size"] * S * 0.14
                    d.line([(x0, yy), (x1, yy)], fill=it["color"],
                           width=max(1, int(round(it["size"] * S * 0.075))))

    if scale != S:
        img = img.resize((int(round(scene.width * scale)), int(round(scene.height * scale))),
                         Image.LANCZOS)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    img.save(path, "PNG", optimize=True)
    return path


def _dashed_poly(d, pts, color, width, dash, S):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        _dashed_seg(d, x0, y0, x1, y1, color, width, dash, S)


def _dashed_rect(d, x0, y0, x1, y1, r, color, width, dash, S):
    if not r:
        for a, b in [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
                     ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]:
            _dashed_seg(d, a[0], a[1], b[0], b[1], color, width, dash, S)
    else:
        d.rounded_rectangle([x0, y0, x1, y1], radius=r, outline=color, width=max(1, int(round(width))))


def _dashed_seg(d, x0, y0, x1, y1, color, width, dash, S):
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    if L == 0:
        return
    ux, uy = dx / L, dy / L
    pattern = [(v * S) for v in (dash if isinstance(dash, (list, tuple)) else [6, 4])]
    total = sum(pattern) or 1
    pos = 0.0
    i = 0
    while pos < L:
        seg = pattern[i % len(pattern)]
        if i % 2 == 0:
            end = min(pos + seg, L)
            d.line([(x0 + ux * pos, y0 + uy * pos), (x0 + ux * end, y0 + uy * end)],
                   fill=color, width=width)
        pos += seg
        i += 1


# --------------------------------------------------------------------------- #
#  Сохранение пары SVG + PNG
# --------------------------------------------------------------------------- #

def save(scene: Scene, base_path: str, png_scale: float = 2.0, with_png: bool = True):
    """base_path без расширения: создаёт <base>.svg и (опц.) <base>.png."""
    svg_path = base_path + ".svg"
    os.makedirs(os.path.dirname(os.path.abspath(svg_path)), exist_ok=True)
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(render_svg(scene))
    png_path = None
    if with_png:
        png_path = base_path + ".png"
        render_png(scene, png_path, scale=png_scale)
    return svg_path, png_path
