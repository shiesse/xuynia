# -*- coding: utf-8 -*-
"""
build_docs.py — генерация текстовой части практик №3–№6 из data.py:
  * docs/practice-03-dfd.md
  * docs/practice-04-idef3.md
  * docs/practice-05-06-idef1x.md
  * site/index.html  (одностраничник со встроенными SVG и таблицами)

Запуск:  python tools/build_docs.py
"""
from __future__ import annotations

import html
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data as D  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
SITE = os.path.join(ROOT, "site")
DIAG = os.path.join(ROOT, "diagrams")
IMG = os.path.join(ROOT, "images")


# --------------------------------------------------------------------------- #
#  Markdown-хелперы
# --------------------------------------------------------------------------- #

def cell(v):
    return str(v).replace("|", "\\|").replace("\n", "<br>")


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(cell(c) for c in r) + " |")
    return "\n".join(out)


def fig(name, alt, rel_img="../images", rel_svg="../diagrams"):
    return (f"![{alt}]({rel_img}/{name}.png)\n\n"
            f"*Рис. — [{name}.svg]({rel_svg}/{name}.svg) (векторная версия для печати).*\n")


# --------------------------------------------------------------------------- #
#  Практика 3
# --------------------------------------------------------------------------- #

def practice3_md():
    L = []
    L.append("# Практика №3. Нотация DFD (диаграммы потоков данных), стандарт Гейна–Сарсона\n")
    L.append(f"**Объект моделирования:** {D.COMPANY} ({D.DOMAIN}).  \n"
             f"**Моделируемый процесс:** {D.PARENT_PROCESS} — узел декомпозиции A0 "
             "«Разработка программного обеспечения» функциональной модели IDEF0.\n")
    L.append("## 1. Элементы нотации Гейна–Сарсона\n")
    L.append(md_table(
        ["Элемент", "Графическое представление", "Назначение в модели"],
        [
            ["Внешняя сущность (external entity)", "Прямоугольник",
             "Источник или приёмник данных вне границ моделируемого процесса: «Заказчик», "
             "«Технический директор»"],
            ["Процесс (process)", "Прямоугольник со скруглёнными углами, разделённый на зону "
                                  "номера и зону наименования",
             "Преобразование входных потоков в выходные: A1 на уровне 0; 1.1–1.3 на уровне 1"],
            ["Хранилище данных (data store)", "Открытый справа прямоугольник с полем "
                                               "идентификатора (D1, D2)",
             "Накопитель данных, к которому процессы пишут и из которого читают "
             "(реестр требований, файловое хранилище)"],
            ["Поток данных (data flow)", "Стрелка с подписью имени потока",
             "Перемещение данных между сущностями, процессами и хранилищами"],
            ["Управляющий поток", "Пунктирная стрелка",
             "Регламенты, стандарты, договор — данные, ограничивающие выполнение процесса, "
             "но не преобразуемые им"],
        ]))
    L.append("\n> В нотации Гейна–Сарсона процесс изображается скруглённым прямоугольником; "
             "круг/овал — эквивалентный элемент нотации Yourdon/DeMarco. Хранилище данных на "
             "контекстном уровне (уровень 0) не показывается и появляется только при декомпозиции.\n")

    L.append("## 2. Уровень 0 (контекстная диаграмма)\n")
    L.append(fig("dfd-a1-level0", "DFD уровень 0"))
    L.append("Один процесс **«Анализ требований и проектирование»** (A1), две внешние сущности — "
             "«Заказчик» и «Технический директор» — и потоки данных, включая требуемые условием "
             "«Первичная заявка», «Согласованное ТЗ» и «Макеты».\n")
    L.append("### 2.1. Спецификация потоков данных (уровень 0)\n")
    L.append(md_table(
        ["Код", "Имя потока", "Откуда", "Куда", "Тип", "Структура данных (тип данных)", "ИП*"],
        [[f["id"], f["name"], f["src"], f["dst"], f["kind"], f["type"], f["ip"]]
         for f in D.DFD_L0_FLOWS]))
    L.append("\n\\* ИП — номер информационного потока из модели «как есть» (Файл 1), "
             "с которым соотносится поток DFD.\n")

    L.append("## 3. Уровень 1 (декомпозиция процесса A1)\n")
    L.append(fig("dfd-a1-level1", "DFD уровень 1"))
    L.append("### 3.1. Подпроцессы\n")
    L.append(md_table(
        ["№", "Наименование", "Исполнитель (механизм IDEF0)", "Входы", "Выходы", "Узел IDEF0"],
        [[p["id"], p["name"], p["actor"], p["in_"], p["out"], p["idef0"]]
         for p in D.DFD_L1_PROCESSES]))
    L.append("\n### 3.2. Хранилища данных\n")
    L.append(md_table(
        ["ID", "Наименование", "Физическая реализация", "Состав данных"],
        [[s["id"], s["name"], s["impl"], s["content"]] for s in D.DFD_L1_STORES]))
    L.append("\n### 3.3. Спецификация потоков данных (уровень 1)\n")
    L.append(md_table(
        ["Код", "Имя потока", "Откуда", "Куда", "Тип", "Структура данных (тип данных)", "ИП*"],
        [[f["id"], f["name"], f["src"], f["dst"], f["kind"], f["type"], f["ip"]]
         for f in D.DFD_L1_FLOWS]))
    L.append("\n## 4. Балансировка и проверка модели\n")
    for i, n in enumerate(D.DFD_BALANCE_NOTES, 1):
        L.append(f"{i}. {n}")
    L.append("")
    return "\n".join(L)


# --------------------------------------------------------------------------- #
#  Практика 4
# --------------------------------------------------------------------------- #

def practice4_md():
    L = []
    L.append("# Практика №4. Нотация IDEF3 (диаграмма потока работ, Process Flow)\n")
    L.append(f"**Объект моделирования:** {D.COMPANY}.  \n"
             "**Моделируемый процесс:** A3 «Тестирование и контроль качества» — выбран потому, "
             "что содержит ветвления и циклы (возврат дефектов на исправление), которые не "
             "выражаются линейной DFD.\n")
    L.append("## 1. Элементы нотации IDEF3\n")
    L.append(md_table(
        ["Элемент", "Графика", "Назначение"],
        [
            ["UOB (Unit of Behavior) — единица поведения", "Прямоугольник с номером в левом "
             "верхнем углу", "Отдельная работа процесса (ручное тестирование, исправление багов…)"],
            ["Перекрёсток (junction)", "Квадрат с символом: `&` — синхронное И, `≥1` — "
             "асинхронное ИЛИ, `X` — взаимоисключающее ИЛИ",
             "Точка слияния (fan-in) или разветвления (fan-out) потоков работ"],
            ["Объект ссылки (Reference Object)", "Прямоугольник с «тенью»",
             "Документ/артефакт, на который опирается работа (ТЗ, тест-кейсы, баг-репорт), "
             "связывается тонкой штриховой линией"],
            ["Связь предшествования (link)", "Стрелка", "Порядок выполнения работ"],
        ]))
    L.append("\n## 2. Диаграмма потока работ A3\n")
    L.append(fig("idef3-a3", "IDEF3 A3"))
    L.append("## 3. Спецификация единиц поведения (UOB)\n")
    L.append(md_table(
        ["№", "Наименование UOB", "Исполнитель", "Условие начала (триггер)", "Вход", "Выход",
         "Узел IDEF0"],
        [[u["num"], u["name"], u["actor"], u["trigger"], u["in_"], u["out"], u["idef0"]]
         for u in D.IDEF3_UOBS]))
    L.append("\n## 4. Перекрёстки: типы и обоснование выбора\n")
    L.append(md_table(
        ["ID", "Тип", "Режим", "Место в процессе", "Связи", "Обоснование (почему выбран "
         "именно этот тип)"],
        [[j["id"], j["type"], j["mode"], j["place"], j["links"], j["why"]]
         for j in D.IDEF3_JUNCTIONS]))
    L.append("\n### 4.1. Синхронность и асинхронность: правило выбора\n")
    L.append("- **Синхронный перекрёсток (`&`, И):** активация выхода возможна только после "
             "прихода **всех** входящих связей (fan-in) либо все выходы активируются **одновременно** "
             "(fan-out). Применяется там, где работы обязаны выполняться над одним и тем же "
             "объектом (релиз-кандидат) и решение принимается по полному набору результатов — "
             "J3 и J2.\n"
             "- **Асинхронный перекрёсток (`≥1`, ИЛИ):** для активации достаточно **хотя бы одной** "
             "связи; ветви могут выполняться параллельно и независимо. Применяется для логических "
             "условий и циклов возврата — J1 и J4.\n"
             "- **Взаимоисключающее ИЛИ (`X`, XOR)** в данной модели не используется: оно запретило "
             "бы одновременную работу ветвей «исправление дефектов» и «подготовка отчёта», что "
             "противоречит практике параллельной работы QA и разработчиков.\n")
    L.append("## 5. Объекты ссылок\n")
    L.append(md_table(
        ["Объект ссылки", "Содержание", "Связан с"],
        [[r["name"], r["desc"], r["links"]] for r in D.IDEF3_REFOBJS]))
    L.append("\n## 6. Сценарии выполнения процесса\n")
    for title, text in D.IDEF3_SCENARIOS:
        L.append(f"**{title}.** {text}\n")
    L.append("")
    return "\n".join(L)


# --------------------------------------------------------------------------- #
#  Практики 5–6
# --------------------------------------------------------------------------- #

def constraints(a):
    c = []
    if a["pk"]:
        c.append("PK")
    if a["fk"]:
        c.append("FK")
    c.append("NOT NULL" if not a["null"] else "NULL")
    return ", ".join(c)


def practice56_md():
    L = []
    L.append("# Практики №5–6. Нотация IDEF1X (логическая модель данных)\n")
    L.append(f"**Предметная область:** «Управление проектами разработки ПО» {D.COMPANY} — "
             "данные процессов A0–A4 функциональной модели IDEF0 и информационных потоков ИП 1–25.\n")
    L.append("## 1. Правила нотации, использованные в модели\n")
    L.append(md_table(
        ["Правило", "Как отражено на диаграмме"],
        [
            ["Независимая сущность", "Прямоугольник с прямыми углами (ЗАКАЗЧИК, СОТРУДНИК, "
                                     "ДОГОВОР, ДОКУМЕНТ)"],
            ["Зависимая сущность", "Прямоугольник со скруглёнными углами (ПРОЕКТ, ЗАДАЧА, "
                                   "ТЕСТ_КЕЙС, БАГ_РЕПОРТ) — существует только через родителя"],
            ["Идентифицирующая связь", "Сплошная линия; внешний ключ родителя входит в первичный "
                                       "ключ потомка; «гусиная лапка» на стороне «многие»"],
            ["Неидентифицирующая связь", "Пунктирная линия; FK — обычный атрибут потомка, "
                                         "допускает NULL (необязательная связь)"],
            ["Кардинальность", "Одиночная засечка у родителя («один»), «гусиная лапка» у потомка "
                               "(«многие»); для 1:1 — засечки с обеих сторон"],
            ["Ключи", "PK подчёркнут в карточке сущности; FK помечен маркером FK; тип данных "
                      "указан моноширинным шрифтом"],
        ]))
    L.append("\n## 2. Диаграмма «сущность–связь»\n")
    L.append(fig("idef1x-model", "IDEF1X модель данных"))
    L.append("## 3. Перечень сущностей\n")
    L.append(md_table(
        ["№", "Сущность", "Тип", "Комментарий"],
        [[e["num"], e["name"], "зависимая" if e["dependent"] else "независимая", e["comment"]]
         for e in D.ENTITIES]))
    L.append("\n## 4. Спецификация связей\n")
    L.append(md_table(
        ["Родитель", "Потомок", "Кардинальность", "Тип связи", "Внешний ключ (FK)",
         "Бизнес-правило"],
        [[r["parent"], r["child"], r["card"],
          "идентифицирующая" if r["identifying"] else "неидентифицирующая", r["fk"], r["rule"]]
         for r in D.RELATIONSHIPS]))
    L.append("\n## 5. Спецификация атрибутов\n")
    rows = []
    for e in D.ENTITIES:
        for a in e["attrs"]:
            rows.append([e["name"], a["name"], a["type"], constraints(a), a["desc"]])
    L.append(md_table(
        ["Имя сущности", "Имя атрибута", "Тип данных", "Ограничения", "Описание"], rows))
    L.append("\n## 6. Нормализация и целостность модели\n")
    for i, n in enumerate(D.NORMALIZATION_NOTES, 1):
        L.append(f"{i}. {n}")
    L.append("\n## 7. Соответствие модели этапам жизненного цикла (IDEF0 A0–A4)\n")
    L.append(md_table(["Этап IDEF0", "Сущности и данные этапа"],
                      [[a, b] for a, b in D.IDEF1X_MAPPING]))
    L.append("\n## 8. Физическая реализация\n")
    L.append("Логическая модель реализована в виде DDL-скрипта PostgreSQL: "
             "[`sql/schema.sql`](../sql/schema.sql) — первичные и внешние ключи, "
             "каскадное удаление для идентифицирующих связей, `ON DELETE SET NULL` для "
             "необязательных неидентифицирующих, CHECK-ограничения доменов, индексы по FK.\n")
    return "\n".join(L)


# --------------------------------------------------------------------------- #
#  HTML-сайт
# --------------------------------------------------------------------------- #

CSS = """
:root{--ink:#14213d;--mut:#5b6b82;--line:#dbe3ee;--acc:#1a56b0;--bg:#f7f9fc}
*{box-sizing:border-box}
body{margin:0;font:15px/1.65 -apple-system,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;
color:var(--ink);background:var(--bg)}
header.top{background:linear-gradient(135deg,#0b1f3a,#1a355e);color:#fff;padding:44px 8vw 38px}
header.top h1{margin:0 0 10px;font-size:30px;letter-spacing:.3px}
header.top p{margin:4px 0;color:#c9d6ea;font-size:14.5px}
nav{position:sticky;top:0;background:#ffffffee;backdrop-filter:blur(6px);border-bottom:1px solid var(--line);
padding:10px 8vw;display:flex;gap:18px;flex-wrap:wrap;z-index:5}
nav a{color:var(--acc);text-decoration:none;font-size:13.5px;font-weight:600}
nav a:hover{text-decoration:underline}
main{padding:34px 8vw 80px;max-width:1500px;margin:0 auto}
section{background:#fff;border:1px solid var(--line);border-radius:14px;padding:30px 34px;margin:0 0 34px;
box-shadow:0 1px 3px rgba(16,42,90,.06)}
h2{margin:0 0 6px;font-size:24px;color:#0b1f3a}
h3{margin:26px 0 8px;font-size:17.5px;color:#12325e}
.sub{color:var(--mut);font-size:13.5px;margin:0 0 18px}
figure{margin:18px 0;padding:14px;background:#fbfcfe;border:1px solid var(--line);border-radius:10px;
overflow:auto}
figure svg{display:block;margin:0 auto;max-width:100%;height:auto}
figcaption{color:var(--mut);font-size:12.5px;margin-top:10px;text-align:center}
table{border-collapse:collapse;width:100%;margin:14px 0 6px;font-size:13px}
th{background:#eef3fb;color:#12325e;text-align:left;padding:8px 10px;border:1px solid var(--line);
font-size:12.5px}
td{padding:7px 10px;border:1px solid var(--line);vertical-align:top}
tr:nth-child(even) td{background:#fafcff}
code{background:#eef1f6;border-radius:4px;padding:1px 5px;font:12.5px/1.5 'JetBrains Mono',Consolas,monospace}
.badge{display:inline-block;background:#e8f0fe;color:#1a56b0;border-radius:20px;padding:2px 10px;
font-size:12px;font-weight:600;margin-right:6px}
.note{background:#fff8ec;border:1px solid #f0dcb4;border-radius:10px;padding:12px 16px;font-size:13.5px;
color:#6b4a12;margin:14px 0}
ul{margin:8px 0 8px 20px;padding:0}
li{margin:4px 0}
footer{color:var(--mut);font-size:12.5px;padding:0 8vw 50px}
"""


def html_table(headers, rows):
    th = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    body = []
    for r in rows:
        tds = "".join(f"<td>{html.escape(str(c))}</td>" for c in r)
        body.append(f"<tr>{tds}</tr>")
    return f"<table><thead><tr>{th}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def inline_svg(name):
    with open(os.path.join(DIAG, name + ".svg"), encoding="utf-8") as f:
        svg = f.read()
    # убираем xml-декларацию и делаем svg масштабируемым
    svg = svg.replace('role="img"', 'role="img" style="min-width:1100px"', 1)
    return svg


def build_site():
    parts = [f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Практики 3–6 · DFD, IDEF3, IDEF1X · {html.escape(D.COMPANY)}</title>
<style>{CSS}</style></head><body>
<header class="top">
<h1>Моделирование процессов и данных: практики №3–№6</h1>
<p>{html.escape(D.COMPANY)} · {html.escape(D.DOMAIN)}</p>
<p>DFD (Гейн–Сарсон) · IDEF3 (поток работ) · IDEF1X (логическая модель данных) —
единый сквозной пример на процессе «Разработка программного обеспечения» (A0)</p>
</header>
<nav>
<a href="#p3">Практика 3 · DFD</a>
<a href="#p4">Практика 4 · IDEF3</a>
<a href="#p56">Практики 5–6 · IDEF1X</a>
<a href="#spec">Сводные спецификации</a>
<a href="idef0-as-is.html">Лабораторная №1 · IDEF0 «как есть»</a>
</nav>
<main>"""]

    # ---------------- Практика 3
    parts.append(f"""<section id="p3">
<h2>Практика №3 · DFD в нотации Гейна–Сарсона</h2>
<p class="sub">Моделируемый процесс: {html.escape(D.PARENT_PROCESS)}. Уровень 0 — контекстная
диаграмма, уровень 1 — декомпозиция на три подпроцесса с хранилищами данных.</p>
<h3>Уровень 0. Контекстная диаграмма</h3>
<figure>{inline_svg('dfd-a1-level0')}
<figcaption>Рис. 1. DFD уровня 0: один процесс, внешние сущности «Заказчик» и
«Технический директор», потоки F01–F10</figcaption></figure>
{html_table(["Код", "Имя потока", "Откуда", "Куда", "Тип", "Структура данных", "ИП"],
            [[f["id"], f["name"], f["src"], f["dst"], f["kind"], f["type"], f["ip"]]
             for f in D.DFD_L0_FLOWS])}
<h3>Уровень 1. Декомпозиция процесса A1</h3>
<figure>{inline_svg('dfd-a1-level1')}
<figcaption>Рис. 2. DFD уровня 1: подпроцессы 1.1–1.3, хранилища D1–D2, процесс-приёмник A2</figcaption></figure>
{html_table(["№", "Подпроцесс", "Исполнитель", "Входы", "Выходы", "Узел IDEF0"],
            [[p["id"], p["name"], p["actor"], p["in_"], p["out"], p["idef0"]]
             for p in D.DFD_L1_PROCESSES])}
{html_table(["ID", "Хранилище", "Реализация", "Состав данных"],
            [[s["id"], s["name"], s["impl"], s["content"]] for s in D.DFD_L1_STORES])}
{html_table(["Код", "Имя потока", "Откуда", "Куда", "Тип", "Структура данных", "ИП"],
            [[f["id"], f["name"], f["src"], f["dst"], f["kind"], f["type"], f["ip"]]
             for f in D.DFD_L1_FLOWS])}
<div class="note"><b>Балансировка и проверка:</b><ul>""" +
                 "".join(f"<li>{html.escape(n)}</li>" for n in D.DFD_BALANCE_NOTES) +
                 "</ul></div></section>")

    # ---------------- Практика 4
    parts.append(f"""<section id="p4">
<h2>Практика №4 · IDEF3: диаграмма потока работ</h2>
<p class="sub">Моделируемый процесс: A3 «Тестирование и контроль качества» — содержит ветвления
и цикл возврата дефектов на исправление.</p>
<figure>{inline_svg('idef3-a3')}
<figcaption>Рис. 3. IDEF3: UOB 1–5, перекрёстки J1–J4, объекты ссылок</figcaption></figure>
{html_table(["№", "UOB", "Исполнитель", "Триггер", "Вход", "Выход", "IDEF0"],
            [[u["num"], u["name"], u["actor"], u["trigger"], u["in_"], u["out"], u["idef0"]]
             for u in D.IDEF3_UOBS])}
<h3>Перекрёстки и обоснование их типов</h3>
{html_table(["ID", "Тип", "Режим", "Место", "Связи", "Обоснование"],
            [[j["id"], j["type"], j["mode"], j["place"], j["links"], j["why"]]
             for j in D.IDEF3_JUNCTIONS])}
<h3>Объекты ссылок</h3>
{html_table(["Объект ссылки", "Содержание", "Связан с"],
            [[r["name"], r["desc"], r["links"]] for r in D.IDEF3_REFOBJS])}
<h3>Сценарии выполнения</h3><ul>""" +
                 "".join(f"<li><b>{html.escape(t)}.</b> {html.escape(x)}</li>"
                         for t, x in D.IDEF3_SCENARIOS) + "</ul></section>")

    # ---------------- Практики 5-6
    attr_rows = []
    for e in D.ENTITIES:
        for a in e["attrs"]:
            attr_rows.append([e["name"], a["name"], a["type"], constraints(a), a["desc"]])
    parts.append(f"""<section id="p56">
<h2>Практики №5–6 · IDEF1X: логическая модель данных</h2>
<p class="sub">Предметная область «Управление проектами разработки ПО»: 8 сущностей,
идентифицирующие и неидентифицирующие связи, кардинальности 1:M и 1:1, нормализация до 3НФ.</p>
<figure>{inline_svg('idef1x-model')}
<figcaption>Рис. 4. IDEF1X: сущности, PK/FK, связи «гусиная лапка»</figcaption></figure>
{html_table(["№", "Сущность", "Тип", "Комментарий"],
            [[e["num"], e["name"], "зависимая" if e["dependent"] else "независимая", e["comment"]]
             for e in D.ENTITIES])}
<h3>Связи</h3>
{html_table(["Родитель", "Потомок", "Кардинальность", "Тип связи", "FK", "Бизнес-правило"],
            [[r["parent"], r["child"], r["card"],
              "идентифицирующая" if r["identifying"] else "неидентифицирующая", r["fk"], r["rule"]]
             for r in D.RELATIONSHIPS])}
<h3>Соответствие этапам IDEF0</h3>
{html_table(["Этап IDEF0", "Сущности и данные этапа"], [[a, b] for a, b in D.IDEF1X_MAPPING])}
<div class="note">DDL-реализация модели — <code>sql/schema.sql</code> (PostgreSQL):
PK/FK, каскады для идентифицирующих связей, CHECK-ограничения доменов.</div>
</section>""")

    # ---------------- Сводные спецификации
    parts.append(f"""<section id="spec">
<h2>Сводная спецификация атрибутов (практика №6, таблица)</h2>
<p class="sub">Полная таблица «Имя сущности — Имя атрибута — Тип данных — Ограничения — Описание».</p>
{html_table(["Имя сущности", "Имя атрибута", "Тип данных", "Ограничения", "Описание"], attr_rows)}
</section>""")

    parts.append("""</main>
<footer>Документы: docs/practice-03-dfd.md · docs/practice-04-idef3.md ·
docs/practice-05-06-idef1x.md · отчёт DOCX: docs/otchet-praktiki-3-6.docx ·
диаграммы генерируются кодом: tools/build_diagrams.py</footer>
</body></html>""")
    os.makedirs(SITE, exist_ok=True)
    with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print("  site/index.html")


def main():
    os.makedirs(DOCS, exist_ok=True)
    for name, fn in [("practice-03-dfd.md", practice3_md),
                     ("practice-04-idef3.md", practice4_md),
                     ("practice-05-06-idef1x.md", practice56_md)]:
        with open(os.path.join(DOCS, name), "w", encoding="utf-8") as f:
            f.write(fn())
        print("  docs/" + name)
    build_site()


if __name__ == "__main__":
    main()
