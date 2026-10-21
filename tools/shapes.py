"""
shapes.py — фигурные «кирпичики» нотаций поверх gfx.Scene.

DFD (Гейн–Сарсон):  внешняя сущность, процесс (скруглённый прямоугольник),
                    хранилище данных (открытый прямоугольник), поток.
IDEF3:              UOB, перекрёстки (junctions) & / ≥1 / X, объекты ссылок.
IDEF1X:             сущности (независимая — прямые углы, зависимая — скруглённые),
                    связи «гусиная лапка» (идентифицирующие / неидентифицирующие).
"""
from __future__ import annotations

import math

from gfx import Scene, measure, wrap, fit, _arrowhead, _unit

# Палитра
C_TEXT = "#14213d"
C_MUTED = "#5b6b82"
C_ENTITY_F, C_ENTITY_S = "#e8f0fe", "#1a56b0"
C_PROC_F, C_PROC_S = "#fff4e0", "#c26a00"
C_STORE_F, C_STORE_S = "#eaf7ec", "#2e7d32"
C_FLOW = "#37474f"
C_CTRL = "#7b1fa2"
C_REF_F, C_REF_S = "#f6ecfd", "#7b1fa2"
C_JUNC_S = "#0f172a"
C_REL = "#1a355e"
C_REL_NON = "#7b1fa2"
C_TITLE = "#0b1f3a"
HALO = "#ffffff"


# --------------------------------------------------------------------------- #
#  Общие
# --------------------------------------------------------------------------- #

def title_block(sc: Scene, title: str, subtitle: str = "", x: float = 32, y: float = 34):
    sc.text(x, y, title, size=21, weight="bold", anchor="start", color=C_TITLE)
    if subtitle:
        sc.text(x, y + 24, subtitle, size=12.5, anchor="start", color=C_MUTED)


def label(sc: Scene, x: float, y: float, text_, size=12, color=C_TEXT,
          weight="regular", anchor="middle", halo=True, max_width=None,
          pad=4, italic=False):
    """Подпись с белой «подложкой», чтобы линия не перечёркивала текст."""
    w = weight
    if italic:
        w = "italic"
    if max_width:
        lines, size = fit(text_, size, max_width, "sans", w)
    else:
        lines = wrap(text_, size, 10 ** 6, "sans", w) if isinstance(text_, str) else list(text_)
    if halo:
        tw = max(measure(l, size, "sans", w) for l in lines) + pad * 2
        th = len(lines) * size * 1.3 + pad * 1.2
        hx = x - tw / 2 if anchor == "middle" else (x - pad if anchor == "start" else x - tw + pad)
        sc.rect(hx, y - th / 2, tw, th, fill=HALO, stroke=None, sw=0, rx=4, opacity=0.92, z=8)
    sc.text_center(x, y, lines, size=size, weight=w, anchor=anchor, color=color, z=9)
    return lines


def legend(sc: Scene, x: float, y: float, items: list[tuple], title="Условные обозначения",
           col_w: float = 300, row_h: float = 30):
    """items: [(kind, text)] kind ∈ entity|process|store|flow|ctrl|uob|junction|
    refobj|ent_ind|ent_dep|rel_id|rel_non"""
    n = len(items)
    w = col_w
    h = 30 + n * row_h + 12
    sc.rect(x, y, w, h, fill="#fbfcfe", stroke="#c9d4e4", sw=1.2, rx=8)
    sc.text(x + 14, y + 21, title, size=12.5, weight="bold", anchor="start", color=C_TITLE)
    cy = y + 30 + row_h / 2
    for kind, txt in items:
        _legend_glyph(sc, x + 30, cy, kind)
        sc.text(x + 62, cy + 4.4, txt, size=11.5, anchor="start", color=C_TEXT)
        cy += row_h


def _legend_glyph(sc: Scene, cx: float, cy: float, kind: str):
    if kind == "entity":
        sc.rect(cx - 18, cy - 10, 36, 20, fill=C_ENTITY_F, stroke=C_ENTITY_S, sw=1.4)
    elif kind == "process":
        sc.rect(cx - 18, cy - 10, 36, 20, fill=C_PROC_F, stroke=C_PROC_S, sw=1.4, rx=9)
    elif kind == "store":
        dfd_store(sc, cx - 20, cy - 9, 40, 18, "D", "", label_size=9, pad=4)
    elif kind == "flow":
        sc.arrow([(cx - 20, cy), (cx + 16, cy)], color=C_FLOW, sw=1.7, head=8)
    elif kind == "ctrl":
        sc.arrow([(cx - 20, cy), (cx + 16, cy)], color=C_CTRL, sw=1.7, head=8, dash=[6, 4])
    elif kind == "uob":
        uob(sc, cx - 20, cy - 11, 40, 22, "1", "", num_size=8, label_size=8)
    elif kind == "junction":
        junction(sc, cx, cy, "or", size=18, sym_size=9)
    elif kind == "refobj":
        refobj(sc, cx - 20, cy - 10, 40, 20, "", label_size=8)
    elif kind == "ent_ind":
        sc.rect(cx - 18, cy - 10, 36, 20, fill="#eaf7ec", stroke=C_REL, sw=1.4)
    elif kind == "ent_dep":
        sc.rect(cx - 18, cy - 10, 36, 20, fill="#fff4e0", stroke=C_PROC_S, sw=1.4, rx=8)
    elif kind == "rel_id":
        relationship(sc, [(cx - 20, cy), (cx + 14, cy)], identifying=True, foot=True, tick=True)
    elif kind == "rel_non":
        relationship(sc, [(cx - 20, cy), (cx + 14, cy)], identifying=False, foot=True, tick=True)


# --------------------------------------------------------------------------- #
#  DFD — нотация Гейна–Сарсона
# --------------------------------------------------------------------------- #

def dfd_entity(sc: Scene, x, y, w, h, name, sub=None, size=14, sub_size=10.5):
    sc.rect(x, y, w, h, fill=C_ENTITY_F, stroke=C_ENTITY_S, sw=2.0, rx=2)
    if sub:
        nm = wrap(name, size, w - 18, "sans", "bold")
        sb = wrap(sub, sub_size, w - 18)
        nh = len(nm) * size * 1.3
        sh = len(sb) * sub_size * 1.3
        total = nh + 8 + sh
        sc.text_center(x + w / 2, y + h / 2 - total / 2 + nh / 2, nm, size=size,
                       weight="bold", color=C_ENTITY_S)
        sc.text_center(x + w / 2, y + h / 2 + total / 2 - sh / 2, sb, size=sub_size,
                       color=C_MUTED)
    else:
        sc.text_center(x + w / 2, y + h / 2, name, size=size, weight="bold",
                       color=C_ENTITY_S, max_width=w - 16)
    return dict(x=x, y=y, w=w, h=h, cx=x + w / 2, cy=y + h / 2)


def dfd_process(sc: Scene, x, y, w, h, num, name, num_size=13, label_size=14,
                fill=C_PROC_F, stroke=C_PROC_S):
    """Процесс Гейна–Сарсона: скруглённый прямоугольник, разделённый на
    зону номера (сверху) и зону наименования."""
    sc.rect(x, y, w, h, fill=fill, stroke=stroke, sw=2.0, rx=min(18, h / 3))
    strip = min(30, h * 0.28)
    sc.poly([(x + 1.5, y + strip), (x + w - 1.5, y + strip)], stroke=stroke, sw=1.3)
    sc.text_center(x + w / 2, y + strip / 2, num, size=num_size, weight="bold", color=stroke)
    sc.text_center(x + w / 2, y + strip + (h - strip) / 2, name, size=label_size,
                   weight="bold", color=C_TEXT, max_width=w - 20)
    return dict(x=x, y=y, w=w, h=h, cx=x + w / 2, cy=y + h / 2)


def dfd_store(sc: Scene, x, y, w, h, sid, name, size=13, id_w=None, label_size=None, pad=12):
    """Хранилище данных: прямоугольник, открытый справа, с полем идентификатора."""
    label_size = label_size or size
    id_w = id_w or max(38, measure(sid, size, "sans", "bold") + 2 * pad)
    sc.rect(x, y, w, h, fill=C_STORE_F, stroke=None, sw=0)
    sc.poly([(x, y), (x + w, y)], stroke=C_STORE_S, sw=2.0)
    sc.poly([(x, y + h), (x + w, y + h)], stroke=C_STORE_S, sw=2.0)
    sc.poly([(x, y), (x, y + h)], stroke=C_STORE_S, sw=2.0)
    sc.poly([(x + id_w, y), (x + id_w, y + h)], stroke=C_STORE_S, sw=1.3)
    sc.text_center(x + id_w / 2, y + h / 2, sid, size=size, weight="bold", color=C_STORE_S)
    if name:
        sc.text_center(x + id_w + (w - id_w) / 2, y + h / 2, name, size=label_size,
                       color=C_TEXT, max_width=w - id_w - 14)
    return dict(x=x, y=y, w=w, h=h, cx=x + w / 2, cy=y + h / 2)


def dfd_flow(sc: Scene, pts, text_=None, control=False, color=None, size=12,
             label_at=None, sw=1.9, dash=None, label_dy=-13, anchor="middle",
             tx_weight="regular", label_color=None, max_width=None):
    """Поток данных: ломаная со стрелкой и подписью.
    label_at — точка подписи (по умолчанию середина самого длинного сегмента)."""
    color = color or (C_CTRL if control else C_FLOW)
    dash = dash if dash is not None else ([7, 5] if control else None)
    sc.arrow(pts, color=color, sw=sw, dash=dash)
    if text_:
        if label_at is None:
            label_at = _midpoint(pts)
        label(sc, label_at[0], label_at[1] + label_dy, text_, size=size,
              color=label_color or color, anchor=anchor, max_width=max_width,
              weight=tx_weight)
    return pts


def _midpoint(pts):
    best, bl = None, -1
    for a, b in zip(pts, pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L > bl:
            bl, best = L, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    return best or pts[0]


# --------------------------------------------------------------------------- #
#  IDEF3
# --------------------------------------------------------------------------- #

def uob(sc: Scene, x, y, w, h, num, name, num_size=12, label_size=13,
        fill=C_ENTITY_F, stroke=C_ENTITY_S, actor=None):
    """UOB (Unit of Behavior) — прямоугольник с номером в левом верхнем углу."""
    sc.rect(x, y, w, h, fill=fill, stroke=stroke, sw=2.0)
    if num:
        sc.text(x + 8, y + num_size + 5, num, size=num_size, weight="bold",
                anchor="start", color=stroke)
    sc.text_center(x + w / 2, y + h / 2 + (6 if actor else 0), name, size=label_size,
                   weight="bold", color=C_TEXT, max_width=w - 18)
    if actor:
        sc.text_center(x + w / 2, y + h - 12, actor, size=10, color=C_MUTED,
                       max_width=w - 18)
    return dict(x=x, y=y, w=w, h=h, cx=x + w / 2, cy=y + h / 2)


def junction(sc: Scene, cx, cy, kind="or", size=26, sym_size=None, fill="#ffffff",
             stroke=C_JUNC_S, tag=None, tag_dy=None):
    """Перекрёсток IDEF3: & (синхронное И), ≥1 (асинхронное ИЛИ), X (взаимоискл.)."""
    s = size / 2
    sym_size = sym_size or size * 0.55
    sc.rect(cx - s, cy - s, size, size, fill=fill, stroke=stroke, sw=1.8)
    sym = {"and": "&", "or": "≥1", "xor": "X"}[kind]
    sc.text_center(cx, cy + 0.5, sym, size=sym_size, weight="bold", color=stroke)
    if tag:
        sc.text_center(cx, cy + (tag_dy if tag_dy is not None else -size / 2 - 11), tag,
                       size=10.5, weight="bold", color=C_MUTED)
    return dict(cx=cx, cy=cy, size=size)


def refobj(sc: Scene, x, y, w, h, name, size=11.5, shadow=5, fill=C_REF_F,
           stroke=C_REF_S, label_size=None):
    """Объект ссылки (Reference Object) — прямоугольник с «тенью»."""
    label_size = label_size or size
    sc.rect(x + shadow, y + shadow, w, h, fill="#e2e6ee", stroke=None, sw=0, rx=2)
    sc.rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.7, rx=2)
    if name:
        sc.text_center(x + w / 2, y + h / 2, name, size=label_size, weight="bold",
                       color=stroke, max_width=w - 14)
    return dict(x=x, y=y, w=w, h=h, cx=x + w / 2, cy=y + h / 2)


def idef3_link(sc: Scene, pts, color=C_FLOW, sw=2.0, dashed=False, head=True,
               text_=None, size=11, label_at=None, label_dy=-12):
    sc.arrow(pts, color=color, sw=sw, dash=[6, 4] if dashed else None,
             head_at="end" if head else "none", head=10)
    if text_:
        label(sc, (label_at or _midpoint(pts))[0], (label_at or _midpoint(pts))[1] + label_dy,
              text_, size=size, color=color)


def ref_link(sc: Scene, pts, color=C_REF_S, sw=1.5):
    """Связь объекта ссылки с UOB/перекрёстком — тонкая линия без стрелки."""
    sc.arrow(pts, color=color, sw=sw, dash=[3, 3], head_at="none")


# --------------------------------------------------------------------------- #
#  IDEF1X
# --------------------------------------------------------------------------- #

def entity(sc: Scene, x, y, w, name, attrs, number=None, dependent=False,
           row_h=21, title_h=32, name_size=13, attr_size=11.5,
           fill=None, stroke=None, note=None):
    """attrs: list of dict(name=..., pk=bool, fk=bool, type=..., req=bool)
    Независимая сущность — прямые углы, зависимая — скруглённые (стандарт IDEF1X)."""
    fill = fill or ("#fff7ea" if dependent else "#eef8ef")
    stroke = stroke or (C_PROC_S if dependent else C_STORE_S)
    rx = 10 if dependent else 0
    n = len(attrs)
    h = title_h + n * row_h + (row_h if note else 0) + 8
    sc.rect(x, y, w, h, fill="#ffffff", stroke=stroke, sw=2.0, rx=rx)
    sc.rect(x, y, w, title_h, fill=fill, stroke=None, sw=0, rx=rx)
    sc.poly([(x + 0.5, y + title_h), (x + w - 0.5, y + title_h)], stroke=stroke, sw=1.4)
    if number:
        sc.text(x + 9, y + title_h / 2 + 4.5, number, size=10, weight="bold",
                anchor="start", color=C_MUTED)
    sc.text_center(x + w / 2 + (14 if number else 0), y + title_h / 2, name,
                   size=name_size, weight="bold", color=C_TITLE, max_width=w - (46 if number else 20))
    ay = y + title_h + 6
    seen_fk = False
    for a in attrs:
        cy = ay + row_h / 2
        if a.get("fk") and not seen_fk:
            sc.poly([(x + 8, ay + 1), (x + w - 8, ay + 1)], stroke="#d6dde8", sw=1.0)
            seen_fk = True
        badges = []
        if a.get("pk"):
            badges.append("PK")
        if a.get("fk"):
            badges.append("FK")
        bx = x + w - 10
        if badges:
            sc.text(bx, cy + 4, " ".join(badges), size=9.5, weight="bold", anchor="end",
                    color=(C_STORE_S if a.get("pk") else C_REL_NON))
            bx -= measure(" ".join(badges), 9.5, "sans", "bold") + 8
        sc.text(x + 12, cy + 4, a["name"], size=attr_size, anchor="start",
                color=C_TEXT, underline=bool(a.get("pk")))
        if a.get("type"):
            sc.text(bx, cy + 4, a["type"], size=9.5, anchor="end", color=C_MUTED, family="mono")
        ay += row_h
    if note:
        sc.text_center(x + w / 2, ay + row_h / 2, note, size=9.5, weight="italic",
                       color=C_MUTED, max_width=w - 14)
    return dict(x=x, y=y, w=w, h=h, cx=x + w / 2, cy=y + h / 2, row_h=row_h,
                title_h=title_h, ay0=y + title_h + 6, n=n)


def _foot(sc: Scene, tip, d, color, sw, L=13, spread=0.55):
    px, py = -d[1], d[0]
    base = (tip[0] - d[0] * L, tip[1] - d[1] * L)
    for k in (-1, 0, 1):
        toe = (base[0] + px * L * spread * k + d[0] * L, base[1] + py * L * spread * k + d[1] * L)
        sc.poly([base, toe], stroke=color, sw=sw)


def _tick(sc: Scene, p, d, color, sw, L=9):
    px, py = -d[1], d[0]
    sc.poly([(p[0] + px * L, p[1] + py * L), (p[0] - px * L, p[1] - py * L)],
            stroke=color, sw=sw)


def relationship(sc: Scene, pts, identifying=True, foot=True, tick=True,
                 color=None, sw=1.9, text_=None, label_at=None, size=11,
                 label_dy=-13, foot_at="end", many=True):
    """Связь: сплошная (идентифицирующая) или пунктирная (неидентифицирующая);
    «гусиная лапка» на стороне «многие», одиночная засечка — на стороне «один»."""
    color = color or (C_REL if identifying else C_REL_NON)
    pts = [tuple(p) for p in pts]
    sc.arrow(pts, color=color, sw=sw, dash=None if identifying else [8, 5], head_at="none")
    d_end = _unit((pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]))
    d_start = _unit((pts[0][0] - pts[1][0], pts[0][1] - pts[1][1]))
    if foot:
        tip = pts[-1] if foot_at == "end" else pts[0]
        dd = d_end if foot_at == "end" else d_start
        if many:
            _foot(sc, tip, dd, color, sw)
        else:
            _tick(sc, (tip[0] - dd[0] * 12, tip[1] - dd[1] * 12), dd, color, sw)
    if tick:
        p0 = pts[0] if foot_at == "end" else pts[-1]
        dd0 = d_end if foot_at == "end" else d_start
        _tick(sc, (p0[0] + dd0[0] * 14, p0[1] + dd0[1] * 14), dd0, color, sw)
    if text_:
        at = label_at or _midpoint(pts)
        label(sc, at[0], at[1] + label_dy, text_, size=size, color=color, weight="bold")
    return pts
