# -*- coding: utf-8 -*-
"""
build_idef0.py — лабораторная работа №1 (практики 1–2): функциональная модель
IDEF0 «КАК ЕСТЬ» (AS-IS) основного бизнес-процесса ООО «ТехноСервис».

Строит (отдельные файлы, не смешивая с практиками 3–6):
  diagrams/idef0-*.svg + images/idef0-*.png   — 23 диаграммы (A-0, ур.1, ур.2×4,
                                                 ур.3×16, дерево узлов);
  docs/practice-01-02-idef0-as-is.md          — отчёт с таблицами и проверками;
  docs/otchet-idef0-as-is.docx                — отчёт Word;
  site/idef0-as-is.html                       — страница-просмотр.

Запуск:  python tools/build_idef0.py
"""
from __future__ import annotations

import html
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gfx import Scene, render_svg, render_png, wrap, measure  # noqa: E402
import shapes as S                                             # noqa: E402
import data_idef0 as M                                         # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG_DIR = os.path.join(ROOT, "diagrams")
PNG_DIR = os.path.join(ROOT, "images")
DOCS = os.path.join(ROOT, "docs")
SITE = os.path.join(ROOT, "site")

BOX_F, BOX_S = "#eef4fd", "#12325e"


def emit(scene, name, png_scale=2.0):
    os.makedirs(SVG_DIR, exist_ok=True)
    os.makedirs(PNG_DIR, exist_ok=True)
    with open(os.path.join(SVG_DIR, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(render_svg(scene))
    render_png(scene, os.path.join(PNG_DIR, name + ".png"), scale=png_scale)
    print(f"  {name} ({scene.width:.0f}x{scene.height:.0f})")


# --------------------------------------------------------------------------- #
#  Фигуры IDEF0
# --------------------------------------------------------------------------- #

def idef0_box(sc, x, y, w, h, num, name, size=13.5):
    sc.rect(x, y, w, h, fill=BOX_F, stroke=BOX_S, sw=2.2)
    lines = name.split("\n") if isinstance(name, str) else list(name)
    lines, size = S_fit(lines, w - 24, size)
    sc.text_center(x + w / 2, y + h / 2 - 6, lines, size=size, weight="bold", color=S.C_TITLE)
    sc.text(x + w - 7, y + h - 8, num, size=10.5, weight="bold", anchor="end", color=S.C_MUTED)
    return dict(x=x, y=y, w=w, h=h, cx=x + w / 2, cy=y + h / 2,
                L=x, R=x + w, T=y, B=y + h)


def S_fit(lines, max_w, size):
    for s in (size, size - 1, size - 2):
        if max(measure(l, s, "sans", "bold") for l in lines) <= max_w:
            return lines, s
    out = []
    for l in lines:
        out.extend(wrap(l, size - 2, max_w, "sans", "bold"))
    return out, size - 2


def arrow(sc, pts, label=None, at=None, dy=-13, size=11, anchor="middle",
          max_width=None, sw=1.9, color=S.C_FLOW):
    sc.arrow(pts, color=color, sw=sw, head=10)
    if label:
        S.label(sc, (at or pts[-1])[0], (at or pts[-1])[1] + dy, label, size=size,
                anchor=anchor, max_width=max_width, color=S.C_TEXT)


def icom_side(sc, box, kind, items, lanes, x_offsets=None, border=None, size=10.5,
              maxw=210):
    """Рисует стрелки ICOM одной стороны блока. kind: in/out/ctrl/mech."""
    res = []
    n = len(items)
    for i, it in enumerate(items):
        txt = it[0] if isinstance(it, (list, tuple)) else it
        if kind == "in":
            y = lanes[i]
            pts = [(border, y), (box["L"], y)]
            at = ((border + box["L"]) / 2, y)
        elif kind == "out":
            y = lanes[i]
            pts = [(box["R"], y), (border, y)]
            at = ((box["R"] + border) / 2, y)
        elif kind == "ctrl":
            x = box["cx"] + (x_offsets[i] if x_offsets else 0)
            y = lanes[i]
            pts = [(x, y), (x, box["T"])]
            at = (x, y - 8)
        else:  # mech
            x = box["cx"] + (x_offsets[i] if x_offsets else 0)
            y = lanes[i]
            pts = [(x, y), (x, box["B"])]
            at = (x, y + 14)
        arrow(sc, pts, label=txt, at=at, dy=0, size=size, max_width=maxw)
        res.append(pts)
    return res


# --------------------------------------------------------------------------- #
#  Контекстная диаграмма A-0
# --------------------------------------------------------------------------- #

def diag_context():
    sc = Scene(1560, 950)
    S.title_block(sc, "IDEF0 «как есть». Контекстная диаграмма A-0",
                  f"Основной бизнес-процесс {M.COMPANY} — «{M.PROCESS}»")
    b = idef0_box(sc, 620, 300, 380, 190, "A0", M.PROCESS, size=16)
    icom_side(sc, b, "in", M.CONTEXT["inputs"], [340, 395, 450], border=40, size=11)
    icom_side(sc, b, "out", M.CONTEXT["outputs"], [340, 395, 450], border=1520, size=11)
    icom_side(sc, b, "ctrl", M.CONTEXT["controls"], [105, 152, 199],
              x_offsets=[-220, 0, 220], size=11, maxw=200)
    icom_side(sc, b, "mech", M.CONTEXT["mechs"], [612, 676],
              x_offsets=[-70, 70], size=11, maxw=230)
    S.legend(sc, 40, 760, [
        ("process", "Блок деятельности (работа/процесс)"),
        ("flow", "Вход / выход (стрелки слева и справа)"),
        ("flow", "Управление (стрелка сверху) и механизм (стрелка снизу)"),
    ], title="Условные обозначения IDEF0", col_w=560, row_h=30)
    x, y, w, h = 660, 760, 860, 150
    sc.rect(x, y, w, h, fill="#fbfcfe", stroke="#c9d4e4", sw=1.2, rx=8)
    sc.text(x + 16, y + 24, "Чтение контекста (модель «как есть»)", size=12.5,
            weight="bold", anchor="start", color=S.C_TITLE)
    for i, ln in enumerate([
        "Вход — то, что перерабатывается процессом: требования и материалы заказчика, обратная связь сопровождения.",
        "Управление — ограничения и правила: договор, стандарты (ГОСТ 34.602), план-график и бюджет.",
        "Механизм — исполнители и инструменты: персонал проектных ролей и набор систем (Jira, Git, CI/CD, Figma).",
        "Выход — результат бизнеса: готовый продукт, документация, подписанный акт сдачи-приёмки.",
    ]):
        sc.text(x + 16, y + 52 + i * 23, ln, size=10.8, anchor="start", color=S.C_TEXT)
    return sc


# --------------------------------------------------------------------------- #
#  Уровень 1
# --------------------------------------------------------------------------- #

L1_POS = {"A1": (150, 300, 270, 160), "A2": (570, 300, 270, 160),
          "A3": (990, 300, 270, 160), "A4": (1410, 300, 270, 160)}

FLOW1_PTS = {
    ("A1", "A2"): [(420, 380), (570, 380)],
    ("A2", "A3"): [(840, 380), (990, 380)],
    ("A3", "A2"): [(1125, 460), (1125, 560), (705, 560), (705, 460)],
    ("A3", "A4"): [(1260, 380), (1410, 380)],
}


def diag_level1():
    sc = Scene(1980, 860)
    S.title_block(sc, "IDEF0 «как есть». Уровень 1 — декомпозиция блока A0",
                  "Этапы жизненного цикла разработки ПО: A1 анализ и проектирование, "
                  "A2 разработка кода, A3 тестирование, A4 внедрение и сдача")
    boxes = {}
    for b in M.LEVEL1["blocks"]:
        x, y, w, h = L1_POS[b["num"]]
        boxes[b["num"]] = idef0_box(sc, x, y, w, h, b["num"], b["name"])
    # внешние входы A1 и выходы A4
    icom_side(sc, boxes["A1"], "in", M.LEVEL1["blocks"][0]["ins"], [340, 400], border=40,
              maxw=104)
    icom_side(sc, boxes["A4"], "out", M.LEVEL1["blocks"][3]["outs"], [340, 390, 440],
              border=1940, maxw=240)
    # выход A1 за границу (ТЗ и документация заказчику) — ветвление вверх
    arrow(sc, [(420, 335), (455, 335), (455, 90)],
          label="Согласованное ТЗ, документация,\nмакеты — заказчику и техдиректору (ИП 7–9)",
          at=(465, 96), dy=0, anchor="start", max_width=250)
    # управления и механизмы
    ctrl1 = {b["num"]: b["ctrl"] for b in M.LEVEL1["blocks"]}
    mech1 = {b["num"]: b["mech"] for b in M.LEVEL1["blocks"]}
    for num, bx in boxes.items():
        icom_side(sc, bx, "ctrl", ctrl1[num], [150, 190][:len(ctrl1[num])],
                  x_offsets=[-60, 60][:len(ctrl1[num])])
        icom_side(sc, bx, "mech", mech1[num], [640, 690][:len(mech1[num])],
                  x_offsets=[-60, 60][:len(mech1[num])])
    # внутренние потоки
    lbl1 = {("A1", "A2"): ((435, 386), 120), ("A2", "A3"): ((855, 366), 190),
            ("A3", "A4"): ((1285, 366), 140), ("A3", "A2"): ((915, 560), 230)}
    for src, dst, lab in M.LEVEL1["flows"]:
        pts = FLOW1_PTS[(src, dst)]
        at, mw = lbl1[(src, dst)]
        arrow(sc, pts, label=lab, at=at, dy=0, max_width=mw)
    sc.text(60, 800, "Обратная связь A3 → A2 («баг-репорты на исправление») и возврат "
                     "«исправленная сборка» A2 → A3 образуют цикл устранения дефектов модели «как есть».",
            size=10.5, weight="italic", anchor="start", color=S.C_MUTED)
    return sc


# --------------------------------------------------------------------------- #
#  Уровень 2 (custom-раскладка + явные внешние стрелки)
# --------------------------------------------------------------------------- #

FLOW2_PTS = {
    ("A1", "A11", "A12"): [(370, 380), (470, 380)],
    ("A1", "A12", "A13"): [(720, 360), (775, 360), (775, 240), (830, 240)],
    ("A1", "A12", "A14"): [(720, 400), (795, 400), (795, 520), (830, 520)],
    ("A2", "A21", "A24"): [(390, 210), (500, 210), (500, 440), (620, 440)],
    ("A2", "A22", "A24"): [(390, 460), (620, 460)],
    ("A2", "A23", "A24"): [(390, 710), (540, 710), (540, 480), (620, 480)],
    ("A3", "A31", "A34"): [(390, 220), (860, 220), (860, 340), (900, 340)],
    ("A3", "A32", "A34"): [(390, 520), (450, 520), (450, 620), (1020, 620), (1020, 460)],
    ("A3", "A33", "A34"): [(770, 440), (900, 440)],
    ("A4", "A41", "A42"): [(390, 340), (450, 340), (450, 220), (520, 220)],
    ("A4", "A41", "A43"): [(390, 380), (450, 380), (450, 530), (520, 530)],
    ("A4", "A42", "A43"): [(740, 280), (740, 470)],
    ("A4", "A43", "A44"): [(770, 530), (860, 530), (860, 360), (900, 360)],
}
L2_CANVAS = {"A1": (1260, 780), "A2": (1080, 860), "A3": (1380, 800), "A4": (1380, 780)}


def diag_level2(key):
    spec = M.LEVEL2[key]
    W, H = L2_CANVAS[key]
    sc = Scene(W, H)
    S.title_block(sc, "IDEF0 «как есть». Уровень 2 — " + spec["title"],
                  f"Диаграмма узла {key}: блоки, внутренние потоки, стрелки ICOM границы")
    boxes = {}
    for b in spec["blocks"]:
        x, y, w, h = b["pos"]
        boxes[b["num"]] = idef0_box(sc, x, y, w, h, b["num"], b["name"], size=12.5)
    for b in spec["blocks"]:
        bx = boxes[b["num"]]
        icom_side(sc, bx, "ctrl", b["ctrl"], [bx["T"] - 34, bx["T"] - 72][:len(b["ctrl"])],
                  x_offsets=[-55, 55][:len(b["ctrl"])], size=10)
        icom_side(sc, bx, "mech", b["mech"], [bx["B"] + 34, bx["B"] + 72][:len(b["mech"])],
                  x_offsets=[-55, 55][:len(b["mech"])], size=10)
    for src, dst, lab in spec["flows"]:
        pts = FLOW2_PTS[(key, src, dst)]
        at = ((pts[0][0] + pts[-1][0]) / 2, (pts[0][1] + pts[-1][1]) / 2)
        if len(pts) > 2:
            at = ((pts[1][0] + pts[2][0]) / 2, (pts[1][1] + pts[2][1]) / 2)
        anc, mw = "middle", 200
        ov = {("A1", "A11", "A12"): ((420, 386), "middle", 95),
              ("A4", "A42", "A43"): ((752, 375), "start", 140),
              ("A3", "A31", "A34"): ((748, 240), "middle", 200),
              ("A3", "A32", "A34"): ((445, 570), "middle", 150),
              ("A3", "A33", "A34"): ((835, 414), "middle", 120)}
        if (key, src, dst) in ov:
            at, anc, mw = ov[(key, src, dst)]
        arrow(sc, pts, label=lab, at=at, dy=-14, size=10.5, max_width=mw, anchor=anc)
    for e in spec["ext"]:
        bx = boxes[e["block"]]
        pts = [tuple(p) for p in e["points"]]
        at = e.get("at") or ((pts[0][0] + pts[-1][0]) / 2, (pts[0][1] + pts[-1][1]) / 2)
        arrow(sc, pts, label=e["label"], at=at,
              dy=(-14 if e["kind"] in ("in", "out") and not e.get("at") else 0),
              size=10.5, max_width=220)
    return sc


# --------------------------------------------------------------------------- #
#  Уровень 3 (цепочечный шаблон)
# --------------------------------------------------------------------------- #

def diag_level3(key):
    spec = M.LEVEL3[key]
    blocks = spec["blocks"]
    n = len(blocks)
    BW, BH, GAP, X0, Y = 250, 110, 130, 150, 300
    W = X0 + n * BW + (n - 1) * GAP + 300
    H = 720
    sc = Scene(W, H)
    S.title_block(sc, f"IDEF0 «как есть». Уровень 3 — декомпозиция блока {key} "
                      f"«{spec['name']}»",
                  "Элементарные работы: одна роль, один результат, без промежуточных решений")
    boxes = []
    for i, b in enumerate(blocks):
        x = X0 + i * (BW + GAP)
        boxes.append(idef0_box(sc, x, Y, BW, BH, b["num"], b["name"], size=12))
    # вход/выход границы
    icom_side(sc, boxes[0], "in", spec["ins"], [Y + BH / 2 - 18, Y + BH / 2 + 18][:len(spec["ins"])],
              border=40, size=10.5, maxw=104)
    icom_side(sc, boxes[-1], "out", spec["outs"],
              [Y + BH / 2 - 18, Y + BH / 2 + 18][:len(spec["outs"])], border=W - 40, size=10.5)
    # управление / механизм каждого блока
    for i, b in enumerate(blocks):
        bx = boxes[i]
        icom_side(sc, bx, "ctrl", [b["ctrl"]], [Y - 66], size=10)
        icom_side(sc, bx, "mech", [b["mech"]], [Y + BH + 62], size=10)
    # цепочка
    for i, lab in enumerate(spec["chain"]):
        a, b = boxes[i], boxes[i + 1]
        arrow(sc, [(a["R"], Y + BH / 2), (b["L"], Y + BH / 2)], label=lab,
              at=((a["R"] + b["L"]) / 2, Y + BH / 2), dy=-16, size=10, max_width=GAP + 60)
    return sc


# --------------------------------------------------------------------------- #
#  Дерево узлов
# --------------------------------------------------------------------------- #

def diag_tree():
    W, H = 1960, 1240
    sc = Scene(W, H)
    S.title_block(sc, "Дерево узлов функциональной модели IDEF0 «как есть»",
                  "A0 → уровень 1 (A1–A4) → уровень 2 (A11–A44) → уровень 3 (A111–A444); "
                  "61 узел декомпозиции")
    # корень
    root = dict(x=W / 2 - 130, y=90, w=260, h=46)
    sc.rect(root["x"], root["y"], root["w"], root["h"], fill=BOX_F, stroke=BOX_S, sw=2.2)
    sc.text_center(W / 2, root["y"] + 23, f"A0 — {M.PROCESS}", size=12.5, weight="bold",
                   color=S.C_TITLE)
    cols = ["A1", "A2", "A3", "A4"]
    colw = 470
    x0 = 40
    y1 = 190
    for ci, c in enumerate(cols):
        cx = x0 + ci * colw + colw / 2 - 60
        # уровень 1
        b1 = M.LEVEL1["blocks"][ci]
        n1 = dict(x=cx - 40, y=y1, w=200, h=40)
        sc.rect(n1["x"], n1["y"], n1["w"], n1["h"], fill="#dce8fa", stroke=BOX_S, sw=1.9)
        sc.text_center(cx + 60, y1 + 20, f"{c} {b1['name'].replace(chr(10), ' ')}",
                       size=11, weight="bold", color=S.C_TITLE, max_width=190)
        sc.poly([(W / 2, root["y"] + root["h"]), (W / 2, 165), (cx + 60, 165), (cx + 60, y1)],
                stroke=BOX_S, sw=1.5)
        # уровень 2 + 3
        y = y1 + 70
        kids2 = [k for k in M.LEVEL2_ORDER if k.startswith(c)] if hasattr(M, "LEVEL2_ORDER") else \
                [f"{c}{i}" for i in range(1, 5)]
        rail_y = y1 + 52
        ticks = []
        last_c = y + 17
        for k2 in kids2:
            name2 = _level2_name(k2)
            n2 = dict(x=cx, y=y, w=180, h=34)
            sc.rect(n2["x"], n2["y"], n2["w"], n2["h"], fill="#eef4fd", stroke=BOX_S, sw=1.6)
            sc.text_center(cx + 90, y + 17, f"{k2} {name2}", size=10, weight="bold",
                           color=S.C_TITLE, max_width=172)
            ticks.append([(cx - 14, y + 17), (cx, y + 17)])
            last_c = y + 17
            y += 42
            kids3 = M.LEVEL3[k2]["blocks"]
            if kids3:
                sc.poly([(cx + 18, n2["y"] + 34), (cx + 18, y + 13 + (len(kids3) - 1) * 30)],
                        stroke="#7d94b8", sw=1.2)
            for b3 in kids3:
                n3 = dict(x=cx + 34, y=y, w=176, h=26)
                sc.rect(n3["x"], n3["y"], n3["w"], n3["h"], fill="#f7fafd", stroke="#7d94b8", sw=1.2)
                sc.text_center(cx + 34 + 88, y + 13, f"{b3['num']} {b3['name']}", size=8.6,
                               color=S.C_TEXT, max_width=170)
                sc.poly([(cx + 18, y + 13), (cx + 34, y + 13)], stroke="#7d94b8", sw=1.2)
                y += 30
            y += 16
        sc.poly([(cx + 60, y1 + 40), (cx + 60, rail_y), (cx - 14, rail_y), (cx - 14, last_c)],
                stroke=BOX_S, sw=1.3)
        for t in ticks:
            sc.poly(t, stroke=BOX_S, sw=1.3)
    return sc


def _level2_name(k2):
    parent = k2[:2]
    for b in M.LEVEL2[parent]["blocks"]:
        if b["num"] == k2:
            return b["name"].replace("\n", " ")
    return ""


# --------------------------------------------------------------------------- #
#  Текстовая часть: markdown
# --------------------------------------------------------------------------- #

def _md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c).replace("|", "\\|").replace("\n", "<br>")
                                     for c in r) + " |")
    return "\n".join(out)


def _fig(name, alt):
    return (f"![{alt}](../images/{name}.png)\n\n"
            f"*Векторная версия: [{name}.svg](../diagrams/{name}.svg).*\n")


def build_md():
    L = ["# Лабораторная работа №1. Функциональная модель IDEF0 «КАК ЕСТЬ» (AS-IS)\n",
         f"**Организация:** {M.COMPANY}. **Основной бизнес-процесс:** «{M.PROCESS}» (узел A0).  "
         "**Нотация:** IDEF0 (SADT). **Глубина модели:** контекстная диаграмма A-0 + три уровня "
         "декомпозиции (A1–A4; A11–A44; A111–A444). Диаграммы продублированы в формате Dia "
         "(библиотека SADT/IDEF0), каталог `dia/`.\n"]
    L.append("## 1. Методика IDEF0 и правила, соблюдённые в модели\n")
    L.append(_md_table(["Правило", "Как выполнено в модели"],
                       [[a, b] for a, b in M.IDEF0_RULES]))
    L.append("\n## 2. Контекстная диаграмма A-0\n")
    L.append(_fig("idef0-a-minus-0", "Контекстная диаграмма A-0"))
    L.append("### 2.1. Стрелки контекста (ICOM)\n")
    rows = ([["Вход", n[0], "Заказчик, сопровождающие подразделения → блок A0"]
             for n in M.CONTEXT["inputs"]] +
            [["Выход", n[0], "Блок A0 → заказчик, бухгалтерия, архив"] for n in M.CONTEXT["outputs"]] +
            [["Управление", n[0], "Договор и нормативная база → ограничивают процесс"]
             for n in M.CONTEXT["controls"]] +
            [["Механизм", n[0], "Персонал и инструменты, выполняющие процесс"]
             for n in M.CONTEXT["mechs"]])
    L.append(_md_table(["Тип стрелки", "Наименование", "Смысл"], rows))
    L.append("\n## 3. Уровень 1 — декомпозиция A0\n")
    L.append(_fig("idef0-level1", "Уровень 1"))
    L.append(_md_table(
        ["Узел", "Наименование", "Входы", "Выходы", "Управление", "Механизмы"],
        [[b["num"], b["name"].replace("\n", " "), "<br>".join(b["ins"]),
          "<br>".join(b["outs"]), "<br>".join(b["ctrl"]), "<br>".join(b["mech"])]
         for b in M.LEVEL1["blocks"]]))
    L.append("\nВнутренние потоки уровня 1: " +
             "; ".join(f"{s} → {d}: {t.replace(chr(10), ' ')}" for s, d, t in M.LEVEL1["flows"]) +
             ". Цикл A3 → A2 → A3 отражает возврат дефектов на исправление «как есть».\n")
    L.append("## 4. Уровень 2 — декомпозиции A1…A4\n")
    for key in ["A1", "A2", "A3", "A4"]:
        spec = M.LEVEL2[key]
        L.append(f"### 4.{['A1','A2','A3','A4'].index(key)+1}. Диаграмма узла {key}\n")
        L.append(_fig(f"idef0-level2-{key.lower()}", spec["title"]))
        L.append(_md_table(
            ["Узел", "Наименование", "Управление", "Механизмы"],
            [[b["num"], b["name"].replace("\n", " "), "<br>".join(b["ctrl"]),
              "<br>".join(b["mech"])] for b in spec["blocks"]]))
        L.append("\nПотоки: " + "; ".join(f"{s} → {d}: {t.replace(chr(10), ' ')}"
                                          for s, d, t in spec["flows"]) + ".\n")
    L.append("## 5. Уровень 3 — декомпозиции A11…A44 (элементарные работы)\n")
    for key in M.LEVEL3:
        spec = M.LEVEL3[key]
        L.append(f"### 5.{list(M.LEVEL3).index(key)+1}. Диаграмма узла {key} «{spec['name']}»\n")
        L.append(_fig(f"idef0-level3-{key.lower()}", f"Декомпозиция {key}"))
        L.append(f"Вход диаграммы: {spec['ins'][0]}. Выход диаграммы: {spec['outs'][0]}.\n")
        L.append(_md_table(
            ["Узел", "Элементарная работа", "Управление (регламент/стандарт)", "Механизм"],
            [[b["num"], b["name"], b["ctrl"], b["mech"]] for b in spec["blocks"]]))
        L.append("\nПоследовательность: " + " → ".join(b["num"] for b in spec["blocks"]) +
                 "; передаваемые объекты: " + "; ".join(spec["chain"]) + ".\n")
    L.append("## 6. Дерево узлов модели\n")
    L.append(_fig("idef0-node-tree", "Дерево узлов"))
    L.append("Дерево узлов: A0; уровень 1 — " + ", ".join(f"A{i}" for i in range(1, 5)) +
             "; уровень 2 — " + ", ".join(f"A{i}{j}" for i in range(1, 5) for j in range(1, 5)) +
             "; уровень 3 — 60 узлов A111…A444 (полный перечень в разделах 5 и на диаграмме).\n")
    L.append("## 7. Проверка синтаксиса модели\n")
    for i, (a, b) in enumerate(M.IDEF0_RULES, 1):
        L.append(f"{i}. **{a}.** {b}")
    L.append("\n## 8. Приложение. Выполнение в редакторе Dia (библиотека SADT/IDEF0)\n")
    for n in M.DIA_NOTES:
        L.append("- " + n)
    L.append("\nФайлы Dia: " + ", ".join("`dia/" + f + "`" for f in _dia_names()) + ".\n")
    return "\n".join(L)


def _dia_names():
    names = ["idef0-a-minus-0", "idef0-level1"]
    names += [f"idef0-level2-{k.lower()}" for k in ["A1", "A2", "A3", "A4"]]
    names += [f"idef0-level3-{k.lower()}" for k in M.LEVEL3]
    return names


# --------------------------------------------------------------------------- #
#  Сайт
# --------------------------------------------------------------------------- #

def build_site():
    from build_docs import CSS, html_table, inline_svg
    P = []
    P.append(f"""<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Лаб. №1 · IDEF0 «как есть» · {html.escape(M.COMPANY)}</title>
<style>{CSS}</style></head><body>
<header class="top"><h1>Лабораторная работа №1 · IDEF0 «КАК ЕСТЬ» (AS-IS)</h1>
<p>{html.escape(M.COMPANY)} · основной бизнес-процесс «{html.escape(M.PROCESS)}» (A0)</p>
<p>Контекстная диаграмма A-0, три уровня декомпозиции (A1–A4, A11–A44, A111–A444),
дерево узлов; дублирование в Dia (SADT/IDEF0)</p></header>
<nav><a href="index.html">← Практики 3–6</a><a href="#ctx">A-0 контекст</a>
<a href="#l1">Уровень 1</a><a href="#l2">Уровень 2</a><a href="#l3">Уровень 3</a>
<a href="#tree">Дерево узлов</a><a href="#dia">Dia</a></nav><main>""")
    P.append(f"""<section id="ctx"><h2>Контекстная диаграмма A-0</h2>
<p class="sub">Основной бизнес-процесс организации с входами, выходами, управлениями и механизмами.</p>
<figure>{inline_svg('idef0-a-minus-0')}<figcaption>Рис. 1 — контекстная диаграмма A-0</figcaption></figure>
{html_table(["Тип стрелки", "Наименование"],
            [["Вход", n[0]] for n in M.CONTEXT["inputs"]] +
            [["Выход", n[0]] for n in M.CONTEXT["outputs"]] +
            [["Управление", n[0]] for n in M.CONTEXT["controls"]] +
            [["Механизм", n[0]] for n in M.CONTEXT["mechs"]])}</section>""")
    P.append(f"""<section id="l1"><h2>Уровень 1 — декомпозиция A0</h2>
<figure>{inline_svg('idef0-level1')}<figcaption>Рис. 2 — уровень 1: A1–A4</figcaption></figure>
{html_table(["Узел", "Наименование", "Входы", "Выходы", "Управление", "Механизмы"],
            [[b["num"], b["name"].replace(chr(10), " "), "<br>".join(b["ins"]),
              "<br>".join(b["outs"]), "<br>".join(b["ctrl"]), "<br>".join(b["mech"])]
             for b in M.LEVEL1["blocks"]])}</section>""")
    P.append("""<section id="l2"><h2>Уровень 2 — декомпозиции A1…A4</h2>""" + "".join(
        f"""<h3>Узел {k}</h3><figure>{inline_svg(f'idef0-level2-{k.lower()}')}
<figcaption>Диаграмма узла {k}</figcaption></figure>
{html_table(["Узел", "Наименование", "Управление", "Механизмы"],
            [[b["num"], b["name"].replace(chr(10), ' '), '<br>'.join(b["ctrl"]),
              '<br>'.join(b["mech"])] for b in M.LEVEL2[k]["blocks"]])}"""
        for k in ["A1", "A2", "A3", "A4"]) + "</section>")
    P.append("""<section id="l3"><h2>Уровень 3 — декомпозиции A11…A44</h2>""" + "".join(
        f"""<h3>Узел {k} «{html.escape(M.LEVEL3[k]['name'])}»</h3>
<figure>{inline_svg(f'idef0-level3-{k.lower()}')}<figcaption>Диаграмма узла {k}</figcaption></figure>
{html_table(["Узел", "Элементарная работа", "Управление", "Механизм"],
            [[b["num"], b["name"], b["ctrl"], b["mech"]] for b in M.LEVEL3[k]["blocks"]])}"""
        for k in M.LEVEL3) + "</section>")
    P.append(f"""<section id="tree"><h2>Дерево узлов</h2>
<figure>{inline_svg('idef0-node-tree')}<figcaption>Рис. — дерево узлов модели (61 узел декомпозиции)</figcaption></figure></section>""")
    P.append(f"""<section id="dia"><h2>Приложение: диаграммы в Dia (SADT/IDEF0)</h2>
<ul>{''.join(f'<li>{html.escape(n)}</li>' for n in M.DIA_NOTES)}</ul>
<p class="sub">Файлы: {' , '.join('dia/' + f + '.dia' for f in _dia_names())}</p></section>""")
    P.append("</main><footer>Отчёты: docs/practice-01-02-idef0-as-is.md · "
             "docs/otchet-idef0-as-is.docx · генератор: tools/build_idef0.py</footer>"
             "</body></html>")
    os.makedirs(SITE, exist_ok=True)
    with open(os.path.join(SITE, "idef0-as-is.html"), "w", encoding="utf-8") as f:
        f.write("\n".join(P))
    print("  site/idef0-as-is.html")


# --------------------------------------------------------------------------- #
#  DOCX
# --------------------------------------------------------------------------- #

def build_docx():
    from build_report import setup, para, table, figure
    from docx import Document
    doc = Document()
    setup(doc)
    para(doc, M.COMPANY, size=11, space_after=2)
    doc.add_heading("Лабораторная работа №1. Функциональная модель IDEF0 «КАК ЕСТЬ»", level=1)
    para(doc, f"Основной бизнес-процесс: «{M.PROCESS}» (A0). Контекстная диаграмма A-0, "
              "три уровня декомпозиции, дерево узлов. Дублирование в Dia (SADT/IDEF0).")
    doc.add_heading("Контекстная диаграмма A-0", level=2)
    figure(doc, "idef0-a-minus-0", "Рис. 1 — контекстная диаграмма A-0")
    table(doc, ["Тип стрелки", "Наименование"],
          [["Вход", n[0]] for n in M.CONTEXT["inputs"]] +
          [["Выход", n[0]] for n in M.CONTEXT["outputs"]] +
          [["Управление", n[0]] for n in M.CONTEXT["controls"]] +
          [["Механизм", n[0]] for n in M.CONTEXT["mechs"]], widths=[4, 22])
    doc.add_heading("Уровень 1", level=2)
    figure(doc, "idef0-level1", "Рис. 2 — уровень 1")
    table(doc, ["Узел", "Наименование", "Входы", "Выходы", "Управление", "Механизмы"],
          [[b["num"], b["name"].replace("\n", " "), "\n".join(b["ins"]), "\n".join(b["outs"]),
            "\n".join(b["ctrl"]), "\n".join(b["mech"])] for b in M.LEVEL1["blocks"]],
          size=8.5, widths=[1.5, 4, 5, 5, 5, 5.5])
    doc.add_heading("Уровень 2", level=2)
    for k in ["A1", "A2", "A3", "A4"]:
        doc.add_heading(f"Узел {k}", level=3)
        figure(doc, f"idef0-level2-{k.lower()}", f"Диаграмма узла {k}")
        table(doc, ["Узел", "Наименование", "Управление", "Механизмы"],
              [[b["num"], b["name"].replace("\n", " "), "\n".join(b["ctrl"]),
                "\n".join(b["mech"])] for b in M.LEVEL2[k]["blocks"]],
              widths=[2, 7, 8, 9])
    doc.add_heading("Уровень 3", level=2)
    for k in M.LEVEL3:
        doc.add_heading(f"Узел {k} «{M.LEVEL3[k]['name']}»", level=3)
        figure(doc, f"idef0-level3-{k.lower()}", f"Диаграмма узла {k}")
        table(doc, ["Узел", "Элементарная работа", "Управление", "Механизм"],
              [[b["num"], b["name"], b["ctrl"], b["mech"]] for b in M.LEVEL3[k]["blocks"]],
              size=8.5, widths=[2, 9, 7, 8])
    doc.add_heading("Дерево узлов", level=2)
    figure(doc, "idef0-node-tree", "Рис. — дерево узлов модели")
    doc.add_heading("Проверка синтаксиса IDEF0", level=2)
    for i, (a, b) in enumerate(M.IDEF0_RULES, 1):
        para(doc, f"{i}. {a}. {b}", size=10, space_after=3)
    doc.add_heading("Приложение: Dia (SADT/IDEF0)", level=2)
    for n in M.DIA_NOTES:
        para(doc, "• " + n, size=10, space_after=3)
    out = os.path.join(DOCS, "otchet-idef0-as-is.docx")
    doc.save(out)
    print("  docs/otchet-idef0-as-is.docx")


# --------------------------------------------------------------------------- #

def main():
    print("Сборка IDEF0 AS-IS…")
    emit(diag_context(), "idef0-a-minus-0")
    emit(diag_level1(), "idef0-level1")
    for k in ["A1", "A2", "A3", "A4"]:
        emit(diag_level2(k), f"idef0-level2-{k.lower()}")
    for k in M.LEVEL3:
        emit(diag_level3(k), f"idef0-level3-{k.lower()}")
    emit(diag_tree(), "idef0-node-tree")
    os.makedirs(DOCS, exist_ok=True)
    with open(os.path.join(DOCS, "practice-01-02-idef0-as-is.md"), "w", encoding="utf-8") as f:
        f.write(build_md())
    print("  docs/practice-01-02-idef0-as-is.md")
    build_site()
    build_docx()


if __name__ == "__main__":
    main()
