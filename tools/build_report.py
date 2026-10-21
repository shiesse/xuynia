# -*- coding: utf-8 -*-
"""
build_report.py — сборка итогового отчёта DOCX по практикам №3–№6
(диаграммы + таблицы спецификаций), формат A4 альбомный.

Запуск:  python tools/build_report.py   ->  docs/otchet-praktiki-3-6.docx
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor

import data as D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "images")
OUT = os.path.join(ROOT, "docs", "otchet-praktiki-3-6.docx")

ACCENT = RGBColor(0x12, 0x32, 0x5E)
MUTED = RGBColor(0x5B, 0x6B, 0x82)


def constraints(a):
    c = []
    if a["pk"]:
        c.append("PK")
    if a["fk"]:
        c.append("FK")
    c.append("NOT NULL" if not a["null"] else "NULL")
    return ", ".join(c)


def setup(doc):
    sec = doc.sections[0]
    sec.orientation = WD_ORIENT.LANDSCAPE
    sec.page_width, sec.page_height = Cm(29.7), Cm(21.0)
    sec.left_margin = sec.right_margin = Cm(1.6)
    sec.top_margin = sec.bottom_margin = Cm(1.4)
    st = doc.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(10.5)
    for name, size in [("Heading 1", 20), ("Heading 2", 15), ("Heading 3", 12.5)]:
        h = doc.styles[name]
        h.font.name = "Calibri"
        h.font.size = Pt(size)
        h.font.color.rgb = ACCENT
        h.font.bold = True


def para(doc, text, size=10.5, italic=False, color=None, space_after=6, bold=False):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.italic = italic
    r.bold = bold
    if color:
        r.font.color.rgb = color
    p.paragraph_format.space_after = Pt(space_after)
    return p


def table(doc, headers, rows, size=8.5, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        r = hdr[i].paragraphs[0].add_run(h)
        r.bold = True
        r.font.size = Pt(size)
        r.font.color.rgb = ACCENT
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(v))
            r.font.size = Pt(size)
    if widths:
        for r_ in t.rows:
            for i, w in enumerate(widths):
                r_.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def figure(doc, name, caption, width=Cm(25.5)):
    doc.add_picture(os.path.join(IMG, name + ".png"), width=width)
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = para(doc, caption, size=9, italic=True, color=MUTED, space_after=10)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER


def build():
    doc = Document()
    setup(doc)

    # ------------------------- титул ---------------------------------------
    para(doc, D.COMPANY + " · " + D.DOMAIN, size=11, color=MUTED, space_after=2)
    h = doc.add_heading("Отчёт по практикам №3–№6", level=1)
    h.alignment = WD_ALIGN_PARAGRAPH.LEFT
    para(doc, "Моделирование бизнес-процессов и данных: DFD (Гейн–Сарсон), IDEF3, IDEF1X. "
              "Сквозной пример — процесс «Разработка программного обеспечения» (A0) и его "
              "декомпозиция A1–A4.", size=11, space_after=4)
    para(doc, "Содержание: Практика 3 — DFD уровня 0 и 1 процесса A1; Практика 4 — IDEF3 "
              "процесса A3; Практики 5–6 — логическая модель данных IDEF1X и спецификация "
              "атрибутов; приложение — DDL (sql/schema.sql).", size=10.5, color=MUTED)

    # ------------------------- практика 3 ----------------------------------
    doc.add_heading("Практика №3. DFD в нотации Гейна–Сарсона", level=2)
    para(doc, "Моделируемый процесс: " + D.PARENT_PROCESS + ". Внешние сущности: «Заказчик», "
                "«Технический директор». Хранилища данных появляются на уровне 1: D1 «База данных "
                "требований», D2 «Файловое хранилище (Figma / Confluence)».")
    table(doc, ["Элемент нотации", "Графика", "Назначение"], [
        ["Внешняя сущность", "Прямоугольник", "Источник/приёмник данных вне процесса"],
        ["Процесс", "Скруглённый прямоугольник с номером", "Преобразование потоков данных"],
        ["Хранилище данных", "Открытый справа прямоугольник с ID", "Запись/чтение накопленных данных"],
        ["Поток данных", "Стрелка с именем", "Перемещение данных"],
        ["Управляющий поток", "Пунктирная стрелка", "Стандарты, регламенты, договор"],
    ], widths=[5, 7, 14])
    doc.add_heading("Уровень 0 (контекстная диаграмма)", level=3)
    figure(doc, "dfd-a1-level0", "Рис. 1 — DFD уровня 0: процесс A1, внешние сущности, потоки F01–F10")
    doc.add_heading("Спецификация потоков данных (уровень 0)", level=3)
    table(doc, ["Код", "Имя потока", "Откуда", "Куда", "Тип", "Структура данных", "ИП"],
          [[f["id"], f["name"], f["src"], f["dst"], f["kind"], f["type"], f["ip"]]
           for f in D.DFD_L0_FLOWS], size=8, widths=[1.2, 4.2, 2.6, 2.6, 2.2, 11.5, 1.6])
    doc.add_heading("Уровень 1 (декомпозиция процесса A1)", level=3)
    figure(doc, "dfd-a1-level1", "Рис. 2 — DFD уровня 1: подпроцессы 1.1–1.3, хранилища D1–D2")
    table(doc, ["№", "Подпроцесс", "Исполнитель", "Входы", "Выходы", "Узел IDEF0"],
          [[p["id"], p["name"], p["actor"], p["in_"], p["out"], p["idef0"]]
           for p in D.DFD_L1_PROCESSES], widths=[1.2, 4.5, 5, 5, 6, 3])
    table(doc, ["ID", "Хранилище", "Реализация", "Состав данных"],
          [[s["id"], s["name"], s["impl"], s["content"]] for s in D.DFD_L1_STORES],
          widths=[1.2, 5, 6, 14])
    doc.add_heading("Спецификация потоков данных (уровень 1)", level=3)
    table(doc, ["Код", "Имя потока", "Откуда", "Куда", "Тип", "Структура данных", "ИП"],
          [[f["id"], f["name"], f["src"], f["dst"], f["kind"], f["type"], f["ip"]]
           for f in D.DFD_L1_FLOWS], size=8, widths=[1.2, 4.2, 3.2, 3.2, 2.6, 10, 1.6])
    doc.add_heading("Балансировка и проверка модели", level=3)
    for i, n in enumerate(D.DFD_BALANCE_NOTES, 1):
        para(doc, f"{i}. {n}", size=10, space_after=3)

    # ------------------------- практика 4 ----------------------------------
    doc.add_page_break()
    doc.add_heading("Практика №4. IDEF3: диаграмма потока работ процесса A3", level=2)
    para(doc, "Процесс A3 «Тестирование и контроль качества» выбран как содержащий ветвления и "
              "цикл возврата дефектов на исправление: линейная DFD такую логику не выражает.")
    figure(doc, "idef3-a3", "Рис. 3 — IDEF3: UOB 1–5, перекрёстки J1–J4 (& и ≥1), объекты ссылок")
    doc.add_heading("Спецификация единиц поведения (UOB)", level=3)
    table(doc, ["№", "UOB", "Исполнитель", "Триггер", "Вход", "Выход", "IDEF0"],
          [[u["num"], u["name"], u["actor"], u["trigger"], u["in_"], u["out"], u["idef0"]]
           for u in D.IDEF3_UOBS], size=8.5, widths=[1, 5, 4.5, 4.5, 4.5, 4.5, 2.5])
    doc.add_heading("Перекрёстки: типы и обоснование", level=3)
    table(doc, ["ID", "Тип", "Режим", "Место", "Связи", "Обоснование выбора типа"],
          [[j["id"], j["type"], j["mode"], j["place"], j["links"], j["why"]]
           for j in D.IDEF3_JUNCTIONS], size=8.5, widths=[1.2, 3.4, 3.6, 3.6, 4.6, 10])
    para(doc, "Правило выбора: синхронный перекрёсток (&) требует прихода всех входящих связей "
              "(fan-in) или одновременно активирует все выходы (fan-out) — используется, когда "
              "работы выполняются над одним объектом и решение принимается по полному набору "
              "результатов (J3, J2). Асинхронный перекрёсток (≥1) активируется хотя бы одной "
              "связью и допускает параллельные ветви и циклы возврата (J1, J4). Взаимоисключающее "
              "ИЛИ (X) не применялось: оно запретило бы параллельную работу ветвей «исправление "
              "дефектов» и «подготовка отчёта».", size=10)
    doc.add_heading("Объекты ссылок", level=3)
    table(doc, ["Объект ссылки", "Содержание", "Связан с"],
          [[r["name"], r["desc"], r["links"]] for r in D.IDEF3_REFOBJS],
          widths=[5, 13, 8])
    doc.add_heading("Сценарии выполнения процесса", level=3)
    for t, x in D.IDEF3_SCENARIOS:
        para(doc, f"{t}. {x}", size=10, space_after=4)

    # ------------------------- практики 5-6 --------------------------------
    doc.add_page_break()
    doc.add_heading("Практики №5–6. IDEF1X: логическая модель данных", level=2)
    para(doc, "Предметная область «Управление проектами разработки ПО»: данные процессов A0–A4 и "
              "информационных потоков ИП 1–25. Восемь сущностей; идентифицирующие связи делают "
              "потомков зависимыми (скруглённые углы, FK в составе PK), неидентифицирующие — "
              "допускают NULL; связь ДОГОВОР↔ПРОЕКТ — 1:1.")
    figure(doc, "idef1x-model", "Рис. 4 — IDEF1X: сущности E1–E8, PK/FK, связи «гусиная лапка»")
    doc.add_heading("Сущности", level=3)
    table(doc, ["№", "Сущность", "Тип", "Комментарий"],
          [[e["num"], e["name"], "зависимая" if e["dependent"] else "независимая", e["comment"]]
           for e in D.ENTITIES], widths=[1.2, 4, 3.5, 17])
    doc.add_heading("Связи", level=3)
    table(doc, ["Родитель", "Потомок", "Кард.", "Тип связи", "FK", "Бизнес-правило"],
          [[r["parent"], r["child"], r["card"],
            "идентиф." if r["identifying"] else "неидентиф.", r["fk"], r["rule"]]
           for r in D.RELATIONSHIPS], size=8.5, widths=[3, 3, 1.6, 2.6, 6, 10])
    doc.add_heading("Спецификация атрибутов", level=3)
    rows = []
    for e in D.ENTITIES:
        for a in e["attrs"]:
            rows.append([e["name"], a["name"], a["type"], constraints(a), a["desc"]])
    table(doc, ["Сущность", "Атрибут", "Тип данных", "Ограничения", "Описание"], rows,
          size=8, widths=[3.2, 4.2, 3.2, 3.2, 12])
    doc.add_heading("Нормализация и целостность", level=3)
    for i, n in enumerate(D.NORMALIZATION_NOTES, 1):
        para(doc, f"{i}. {n}", size=10, space_after=3)
    doc.add_heading("Соответствие этапам IDEF0 (A0–A4)", level=3)
    table(doc, ["Этап IDEF0", "Сущности и данные этапа"],
          [[a, b] for a, b in D.IDEF1X_MAPPING], widths=[8, 18])
    para(doc, "Физическая реализация модели — скрипт sql/schema.sql (PostgreSQL): составные "
              "первичные ключи по правилу миграции IDEF1X, ON DELETE CASCADE для идентифицирующих "
              "связей, ON DELETE SET NULL для необязательных, UNIQUE для связи 1:1, "
              "CHECK-ограничения доменов.", size=10)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    doc.save(OUT)
    print("  docs/otchet-praktiki-3-6.docx")


if __name__ == "__main__":
    build()
