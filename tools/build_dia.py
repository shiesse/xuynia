# -*- coding: utf-8 -*-
"""Лабораторная работа №1: исходники диаграмм IDEF0 «как есть» для редактора Dia.

Файлы dia/*.dia — gzip-сжатый XML Dia с объектами библиотеки «SADT/IDEF0»
(типы "SADT - box" и "SADT - arrow") и подписями "Standard - Text".
Геометрия совпадает с диаграммами SVG/PNG (tools/build_idef0.py), масштаб 40 px = 1 см.

Запуск:  python tools/build_dia.py
"""
import gzip
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import data_idef0 as M
import build_idef0 as B

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIA_DIR = os.path.join(ROOT, "dia")
PX = 40.0  # пикселей в сантиметре


def cm(v):
    return round(v / PX, 3)


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


HEADER = '''<?xml version="1.0" encoding="ISO-8859-1"?>
<dia:diagram xmlns:dia="http://www.lysator.liu.se/~alla/dia/">
  <dia:diagramdata>
    <dia:attribute name="background">
      <dia:color val="#ffffff"/>
    </dia:attribute>
    <dia:attribute name="paper">
      <dia:composite type="paper">
        <dia:attribute name="name">
          <dia:string>#A4#</dia:string>
        </dia:attribute>
        <dia:attribute name="tmargin">
          <dia:real val="2.82"/>
        </dia:attribute>
        <dia:attribute name="bmargin">
          <dia:real val="2.82"/>
        </dia:attribute>
        <dia:attribute name="lmargin">
          <dia:real val="2.82"/>
        </dia:attribute>
        <dia:attribute name="rmargin">
          <dia:real val="2.82"/>
        </dia:attribute>
        <dia:attribute name="is_portrait">
          <dia:boolean val="true"/>
        </dia:attribute>
        <dia:attribute name="scaling">
          <dia:real val="1"/>
        </dia:attribute>
        <dia:attribute name="fitto">
          <dia:boolean val="false"/>
        </dia:attribute>
      </dia:composite>
    </dia:attribute>
    <dia:attribute name="grid">
      <dia:composite type="grid">
        <dia:attribute name="width_x">
          <dia:real val="1"/>
        </dia:attribute>
        <dia:attribute name="width_y">
          <dia:real val="1"/>
        </dia:attribute>
        <dia:attribute name="visible_x">
          <dia:int val="1"/>
        </dia:attribute>
        <dia:attribute name="visible_y">
          <dia:int val="1"/>
        </dia:attribute>
      </dia:composite>
    </dia:attribute>
    <dia:attribute name="guides">
      <dia:composite type="guides">
        <dia:attribute name="hguides"/>
        <dia:attribute name="vguides"/>
      </dia:composite>
    </dia:attribute>
  </dia:diagramdata>
  <dia:layer name="Background" visible="true">
'''


class Dia(object):
    """Накопитель объектов одного .dia-файла."""

    def __init__(self):
        self.objs = []
        self.n = 0

    def _id(self):
        i = self.n
        self.n += 1
        return "O%d" % i

    def text(self, label, x, y, height=0.35, bold=False):
        """Standard - Text; x, y — px-координаты центра надписи."""
        oid = self._id()
        lines = label.split("\n")
        w = max(len(l) for l in lines) * height * 0.62 / 2 + 0.1
        h = len(lines) * height / 2 + 0.1
        x, y = cm(x), cm(y)
        font = "Helvetica-Bold" if bold else "Helvetica"
        self.objs.append(
            '    <dia:object type="Standard - Text" version="1" id="%s">\n'
            '      <dia:attribute name="obj_pos">\n        <dia:point val="%s,%s"/>\n      </dia:attribute>\n'
            '      <dia:attribute name="obj_bb">\n        <dia:rectangle val="%s,%s;%s,%s"/>\n      </dia:attribute>\n'
            '      <dia:attribute name="text">\n        <dia:composite type="text">\n'
            '          <dia:attribute name="string">\n            <dia:string>#%s#</dia:string>\n          </dia:attribute>\n'
            '          <dia:attribute name="font">\n            <dia:font name="%s"/>\n          </dia:attribute>\n'
            '          <dia:attribute name="height">\n            <dia:real val="%s"/>\n          </dia:attribute>\n'
            '          <dia:attribute name="pos">\n            <dia:point val="%s,%s"/>\n          </dia:attribute>\n'
            '          <dia:attribute name="color">\n            <dia:color val="#000000"/>\n          </dia:attribute>\n'
            '          <dia:attribute name="alignment">\n            <dia:enum val="1"/>\n          </dia:attribute>\n'
            '        </dia:composite>\n      </dia:attribute>\n    </dia:object>\n'
            % (oid, x, y, round(x - w, 2), round(y - h, 2), round(x + w, 2), round(y + h, 2),
               esc(label), font, height, x, y))

    def box(self, num, name, x, y, w, h):
        """SADT - box: прямоугольник деятельности с идентификатором узла."""
        oid = self._id()
        x0, y0, x1, y1 = cm(x), cm(y), cm(x + w), cm(y + h)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        self.objs.append(
            '    <dia:object type="SADT - box" version="0" id="%s">\n'
            '      <dia:attribute name="obj_pos">\n        <dia:point val="%s,%s"/>\n      </dia:attribute>\n'
            '      <dia:attribute name="obj_bb">\n        <dia:rectangle val="%s,%s;%s,%s"/>\n      </dia:attribute>\n'
            '      <dia:attribute name="elem_corner">\n        <dia:point val="%s,%s"/>\n      </dia:attribute>\n'
            '      <dia:attribute name="elem_width">\n        <dia:real val="%s"/>\n      </dia:attribute>\n'
            '      <dia:attribute name="elem_height">\n        <dia:real val="%s"/>\n      </dia:attribute>\n'
            '      <dia:attribute name="padding">\n        <dia:real val="0.5"/>\n      </dia:attribute>\n'
            '      <dia:attribute name="text">\n        <dia:composite type="text">\n'
            '          <dia:attribute name="string">\n            <dia:string>#%s#</dia:string>\n          </dia:attribute>\n'
            '          <dia:attribute name="font">\n            <dia:font name="Helvetica-Bold"/>\n          </dia:attribute>\n'
            '          <dia:attribute name="height">\n            <dia:real val="0.6"/>\n          </dia:attribute>\n'
            '          <dia:attribute name="pos">\n            <dia:point val="%s,%s"/>\n          </dia:attribute>\n'
            '          <dia:attribute name="color">\n            <dia:color val="#000000"/>\n          </dia:attribute>\n'
            '          <dia:attribute name="alignment">\n            <dia:enum val="1"/>\n          </dia:attribute>\n'
            '        </dia:composite>\n      </dia:attribute>\n'
            '      <dia:attribute name="id">\n        <dia:string>#%s#</dia:string>\n      </dia:attribute>\n'
            '      <dia:attribute name="cpl_north">\n        <dia:int val="0"/>\n      </dia:attribute>\n'
            '      <dia:attribute name="cpl_west">\n        <dia:int val="0"/>\n      </dia:attribute>\n'
            '      <dia:attribute name="cpl_south">\n        <dia:int val="0"/>\n      </dia:attribute>\n'
            '      <dia:attribute name="cpl_east">\n        <dia:int val="0"/>\n      </dia:attribute>\n'
            '    </dia:object>\n'
            % (oid, x0, y0, x0 - 0.05, y0 - 0.05, x1 + 0.05, y1 + 0.05, x0, y0,
               round(x1 - x0, 3), round(y1 - y0, 3), esc(name), cx, round(cy + 0.2, 3), num))

    def arrow(self, pts, label=None, at=None, lheight=0.35):
        """SADT - arrow: ортогональная стрелка (список точек в px)."""
        oid = self._id()
        cp = [cm(p[0]) for p in pts]
        xs = [cm(p[0]) for p in pts]
        ys = [cm(p[1]) for p in pts]
        pts_xml = "\n".join('        <dia:point val="%s,%s"/>' % (cm(p[0]), cm(p[1])) for p in pts)
        orients = []
        for i in range(len(pts) - 1):
            dx = pts[i + 1][0] - pts[i][0]
            dy = pts[i + 1][1] - pts[i][1]
            orients.append("1" if abs(dx) < 1e-6 else "0")
        or_xml = "\n".join('        <dia:enum val="%s"/>' % o for o in orients)
        self.objs.append(
            '    <dia:object type="SADT - arrow" version="0" id="%s">\n'
            '      <dia:attribute name="obj_pos">\n        <dia:point val="%s,%s"/>\n      </dia:attribute>\n'
            '      <dia:attribute name="obj_bb">\n        <dia:rectangle val="%s,%s;%s,%s"/>\n      </dia:attribute>\n'
            '      <dia:attribute name="orth_points">\n%s\n      </dia:attribute>\n'
            '      <dia:attribute name="orth_orient">\n%s\n      </dia:attribute>\n'
            '      <dia:attribute name="arrow_style">\n        <dia:enum val="0"/>\n      </dia:attribute>\n'
            '      <dia:attribute name="autogray">\n        <dia:boolean val="true"/>\n      </dia:attribute>\n'
            '    </dia:object>\n'
            % (oid, xs[0], ys[0], min(xs) - 0.1, min(ys) - 0.1, max(xs) + 0.1, max(ys) + 0.1,
               pts_xml, or_xml))
        if label:
            if at is None:
                at = ((pts[0][0] + pts[-1][0]) / 2, (pts[0][1] + pts[-1][1]) / 2 - 14)
            self.text(label, at[0], at[1], height=lheight)

    def write(self, path):
        xml = HEADER + "".join(self.objs) + "  </dia:layer>\n</dia:diagram>\n"
        with gzip.open(path, "wb") as f:
            f.write(xml.encode("utf-8"))
        return path


# --------------------------------------------------------------------------- #
#  Диаграммы
# --------------------------------------------------------------------------- #

def dia_context():
    d = Dia()
    x, y, w, h = 620, 240, 380, 250
    d.box("A0", M.CONTEXT["name"], x, y, w, h)
    cx = x + w / 2
    for i, it in enumerate(M.CONTEXT["controls"]):
        lab = it[0]
        lx = cx + (-220, 0, 220)[i]
        lane = (105, 152, 199)[i]
        d.arrow([(lx, lane), (lx, y)], label=lab, at=(lx, lane - 10))
    for i, it in enumerate(M.CONTEXT["inputs"]):
        lab = it[0]
        ly = (340, 400, 460)[i]
        d.arrow([(40, ly), (x, ly)], label=lab, at=(230, ly - 12))
    for i, it in enumerate(M.CONTEXT["outputs"]):
        lab = it[0]
        ly = (340, 400, 460)[i]
        d.arrow([(x + w, ly), (1520, ly)], label=lab, at=(1260, ly - 12))
    for i, it in enumerate(M.CONTEXT["mechs"]):
        lab = it[0]
        lx = cx + (-70, 70)[i]
        lane = (612, 676)[i]
        d.arrow([(lx, lane), (lx, y + h)], label=lab, at=(lx, lane + 16))
    return d


def dia_level1():
    d = Dia()
    boxes = {}
    for b in M.LEVEL1["blocks"]:
        x, y, w, h = B.L1_POS[b["num"]]
        boxes[b["num"]] = (x, y, w, h)
        d.box(b["num"], b["name"], x, y, w, h)
    for b in M.LEVEL1["blocks"]:
        x, y, w, h = boxes[b["num"]]
        cx = x + w / 2
        for i, lab in enumerate(b["ctrl"]):
            lx = cx + (-60, 60)[i]
            d.arrow([(lx, (150, 190)[i]), (lx, y)], label=lab, at=(lx, (150, 190)[i] - 10), lheight=0.32)
        for i, lab in enumerate(b["mech"]):
            lx = cx + (-60, 60)[i]
            d.arrow([(lx, (640, 690)[i]), (lx, y + h)], label=lab, at=(lx, (640, 690)[i] + 16), lheight=0.32)
    x, y, w, h = boxes["A1"]
    for i, lab in enumerate(M.LEVEL1["blocks"][0]["ins"]):
        ly = (340, 400)[i]
        d.arrow([(40, ly), (x, ly)], label=lab, at=(150, ly - 12), lheight=0.32)
    x, y, w, h = boxes["A4"]
    for i, lab in enumerate(M.LEVEL1["blocks"][3]["outs"]):
        ly = (340, 390, 440)[i]
        d.arrow([(x + w, ly), (1940, ly)], label=lab, at=(1700, ly - 12), lheight=0.32)
    d.arrow([(420, 335), (455, 335), (455, 90)],
            label="Согласованное ТЗ, документация,\nмакеты — заказчику и техдиректору (ИП 7–9)",
            at=(465, 96), lheight=0.32)
    lbl1 = {("A1", "A2"): ((435, 386), 120), ("A2", "A3"): ((855, 366), 190),
            ("A3", "A4"): ((1285, 366), 140), ("A3", "A2"): ((915, 560), 230)}
    for src, dst, lab in M.LEVEL1["flows"]:
        at, _mw = lbl1[(src, dst)]
        d.arrow(B.FLOW1_PTS[(src, dst)], label=lab, at=at, lheight=0.32)
    return d


L2_OV = {("A1", "A11", "A12"): ((420, 386), "middle", 95),
         ("A4", "A42", "A43"): ((752, 375), "start", 140),
         ("A3", "A31", "A34"): ((748, 240), "middle", 200),
         ("A3", "A32", "A34"): ((445, 570), "middle", 150),
         ("A3", "A33", "A34"): ((835, 414), "middle", 120)}


def dia_level2(key):
    spec = M.LEVEL2[key]
    d = Dia()
    boxes = {}
    for b in spec["blocks"]:
        x, y, w, h = b["pos"]
        boxes[b["num"]] = (x, y, w, h)
        d.box(b["num"], b["name"], x, y, w, h)
    for b in spec["blocks"]:
        x, y, w, h = boxes[b["num"]]
        cx = x + w / 2
        for i, lab in enumerate(b["ctrl"]):
            lx = cx + (-55, 55)[i]
            d.arrow([(lx, y - (34, 72)[i]), (lx, y)], label=lab, at=(lx, y - (34, 72)[i] - 10), lheight=0.3)
        for i, lab in enumerate(b["mech"]):
            lx = cx + (-55, 55)[i]
            d.arrow([(lx, y + h + (34, 72)[i]), (lx, y + h)], label=lab,
                    at=(lx, y + h + (34, 72)[i] + 14), lheight=0.3)
    for src, dst, lab in spec["flows"]:
        pts = B.FLOW2_PTS[(key, src, dst)]
        at = ((pts[0][0] + pts[-1][0]) / 2, (pts[0][1] + pts[-1][1]) / 2 - 14)
        if len(pts) > 2:
            at = ((pts[1][0] + pts[2][0]) / 2, (pts[1][1] + pts[2][1]) / 2 - 14)
        if (key, src, dst) in L2_OV:
            p, _anc, _mw = L2_OV[(key, src, dst)]
            at = p
        d.arrow(pts, label=lab, at=at, lheight=0.3)
    for e in spec["ext"]:
        pts = e["points"]
        at = e.get("at")
        if at is None:
            if e["kind"] == "in":
                at = (pts[0][0] + 60, pts[0][1] - 12)
            elif e["kind"] == "out":
                at = (pts[-1][0] - 90, pts[-1][1] - 12)
            else:
                at = ((pts[0][0] + pts[-1][0]) / 2, (pts[0][1] + pts[-1][1]) / 2 - 12)
        d.arrow(pts, label=e["label"], at=at, lheight=0.3)
    return d


def dia_level3(key):
    spec = M.LEVEL3[key]
    blocks = spec["blocks"]
    n = len(blocks)
    BW, BH, GAP, X0, Y = 250, 110, 130, 150, 300
    W = X0 + n * BW + (n - 1) * GAP + 300
    d = Dia()
    boxes = []
    for i, b in enumerate(blocks):
        x = X0 + i * (BW + GAP)
        boxes.append((x, Y, BW, BH))
        d.box(b["num"], b["name"], x, Y, BW, BH)
    for i, lab in enumerate(spec["ins"]):
        ly = Y + BH / 2 - 18 + i * 36
        d.arrow([(40, ly), (X0, ly)], label=lab, at=(150, ly - 12), lheight=0.3)
    for i, lab in enumerate(spec["outs"]):
        ly = Y + BH / 2 - 18 + i * 36
        x = X0 + (n - 1) * (BW + GAP) + BW
        d.arrow([(x, ly), (W - 40, ly)], label=lab, at=(W - 190, ly - 12), lheight=0.3)
    for i, b in enumerate(blocks):
        x, y, w, h = boxes[i]
        d.arrow([(x + w / 2, Y - 66), (x + w / 2, Y)], label=b["ctrl"], at=(x + w / 2, Y - 76), lheight=0.3)
        d.arrow([(x + w / 2, Y + BH + 62), (x + w / 2, Y + BH)], label=b["mech"],
                at=(x + w / 2, Y + BH + 76), lheight=0.3)
    for i, lab in enumerate(spec["chain"]):
        a, b = boxes[i], boxes[i + 1]
        d.arrow([(a[0] + a[2], Y + BH / 2), (b[0], Y + BH / 2)], label=lab,
                at=((a[0] + a[2] + b[0]) / 2, Y + BH / 2 - 16), lheight=0.3)
    return d


def main():
    os.makedirs(DIA_DIR, exist_ok=True)
    jobs = [("idef0-a-minus-0", dia_context()), ("idef0-level1", dia_level1())]
    for k in ("A1", "A2", "A3", "A4"):
        jobs.append(("idef0-level2-" + k.lower(), dia_level2(k)))
    for k in sorted(M.LEVEL3):
        jobs.append(("idef0-level3-" + k.lower(), dia_level3(k)))
    for name, d in jobs:
        d.write(os.path.join(DIA_DIR, name + ".dia"))
        print("  dia/%s.dia (%d objects)" % (name, d.n))
    print("всего файлов: %d" % len(jobs))


if __name__ == "__main__":
    main()
