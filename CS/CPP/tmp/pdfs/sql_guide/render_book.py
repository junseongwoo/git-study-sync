#!/usr/bin/env python3
"""Render the source-grounded SQL study-note JSON files as one searchable PDF.

This module deliberately contains no SQL teaching content.  It consumes the
chapter schema agreed by the writing agents and review.json next to this file.
Run only after the PDF artifact-operation marker has been recorded by the caller.
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import re
import unicodedata
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Flowable, Frame, LongTable, NextPageTemplate, PageBreak,
    PageTemplate, Paragraph, Spacer, TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE.parents[2] / "output" / "pdf" / "SQL_전문가_가이드_요약.pdf"
TITLE = "SQL 전문가 가이드 요약"
PAGE_W, PAGE_H = A4
LEFT = RIGHT = 46
TOP, BOTTOM = 53, 43
TEXT_W = PAGE_W - LEFT - RIGHT
INK = colors.HexColor("#202C38")
ACCENT = colors.HexColor("#235B76")
MUTED = colors.HexColor("#65717C")
PALE = colors.HexColor("#F1F5F7")
RULE = colors.HexColor("#D5DFE4")

MISSING = collections.Counter()
WRAP_EVENTS = 0
FONT_CHARS = {}


def register_fonts(font_dir: Path) -> None:
    for name, filename in (
        ("Malgun", "malgun.ttf"), ("Malgun-Bold", "malgunbd.ttf"),
        ("Consolas", "consola.ttf"), ("Consolas-Bold", "consolab.ttf"),
    ):
        path = font_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Required embedded font missing: {path}")
        pdfmetrics.registerFont(TTFont(name, str(path)))
        FONT_CHARS[name] = set(pdfmetrics.getFont(name).face.charWidths)
    pdfmetrics.registerFontFamily("Malgun", normal="Malgun", bold="Malgun-Bold",
                                  italic="Malgun", boldItalic="Malgun-Bold")
    pdfmetrics.registerFontFamily("Consolas", normal="Consolas", bold="Consolas-Bold",
                                  italic="Consolas", boldItalic="Consolas-Bold")


TRANSLATE = {
    "\u00a0": " ", "\u2007": " ", "\u202f": " ",
    "\u200b": "", "\u200c": "", "\u200d": "", "\ufeff": "",
    "\u00ad": "", "\u2010": "-", "\u2011": "-", "\u2012": "-",
    "\u2013": "-", "\u2014": "-", "\u2212": "-",
    "\ufb01": "fi", "\ufb02": "fl",
    "\u2610": "[ ]", "\u2611": "[v]", "\u2713": "v", "\u2714": "v",
    "\u25aa": "-", "\u25ab": "-", "\u25cf": "-", "\u2022": "-",
}
CHAR_FALLBACK = {
    "→": " -> ", "←": " <- ", "↔": " <-> ", "⇒": " => ",
    "⇔": " <=> ", "↑": "(상승)", "↓": "(하락)",
    "≤": "<=", "≥": ">=", "≠": "!=", "×": "x", "÷": "/",
    "…": "...", "■": "-", "□": "[ ]", "◆": "-", "◇": "-",
    "▶": ">", "▷": ">", "※": "*", "·": "/", "∙": "/",
}


def clean(value) -> str:
    """Normalize unsafe typography while preserving source wording and SQL."""
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        value = ", ".join(str(x) for x in value)
    value = unicodedata.normalize("NFC", str(value)).replace("\r\n", "\n").replace("\r", "\n")
    out = []
    valid = FONT_CHARS.get("Malgun", set()) | FONT_CHARS.get("Consolas", set())
    for char in value:
        if char in TRANSLATE:
            out.append(TRANSLATE[char])
        elif char in "\n\t":
            out.append(char)
        elif unicodedata.category(char) in ("Cc", "Cf", "Cs"):
            continue
        elif not valid or ord(char) in valid:
            out.append(char)
        else:
            replacement = CHAR_FALLBACK.get(char)
            if replacement is None:
                replacement = f"(U+{ord(char):04X})"
                MISSING[f"U+{ord(char):04X} {unicodedata.name(char, 'UNKNOWN')}"] += 1
            out.append(replacement)
    return "".join(out)


def font_runs(value: str, mono=False, bold=False):
    preferred = ("Consolas" if mono else "Malgun") + ("-Bold" if bold else "")
    fallback = "Malgun-Bold" if bold else "Malgun"
    last_font, text = None, ""
    for char in value:
        current = preferred if ord(char) in FONT_CHARS[preferred] else fallback
        if ord(char) not in FONT_CHARS[current]:
            current = next((font for font in ("Malgun", "Consolas", "Malgun-Bold", "Consolas-Bold")
                            if ord(char) in FONT_CHARS[font]), fallback)
        if current != last_font and text:
            yield last_font, text
            text = ""
        text += char
        last_font = current
    if text:
        yield last_font, text


def inline_plain(value: str, mono=False, bold=False) -> str:
    # Normal prose inherits the paragraph font, including bold headings.
    # Font tags are reserved for explicit emphasis, mono text, or fallback.
    return "".join(escape(run) if not mono and not bold and font == "Malgun"
                   else f'<font name="{font}">{escape(run)}</font>'
                   for font, run in font_runs(value, mono, bold))


def inline(value, markdown=True) -> str:
    value = clean(value)
    if not markdown:
        return inline_plain(value).replace("\n", "<br/>")
    result = []
    # Only these two simple, safe inline conventions are interpreted.  All XML
    # from the input is always escaped, including SQL comparison operators.
    for piece in re.split(r"(`[^`\n]+`|\*\*[^*\n]+\*\*)", value):
        if piece.startswith("`") and piece.endswith("`") and len(piece) > 1:
            result.append(inline_plain(piece[1:-1], mono=True))
        elif piece.startswith("**") and piece.endswith("**") and len(piece) > 3:
            result.append(inline_plain(piece[2:-2], bold=True))
        else:
            result.append(inline_plain(piece))
    return "".join(result).replace("\n", "<br/>")


def make_styles():
    common = dict(fontName="Malgun", textColor=INK, wordWrap="CJK", allowWidows=0, allowOrphans=0)
    styles = {
        "body": ParagraphStyle("body", fontSize=10.3, leading=16.1, spaceAfter=6.2, **common),
        "small": ParagraphStyle("small", fontSize=8.0, leading=12.0, spaceAfter=5, **{**common, "textColor": MUTED}),
        "source": ParagraphStyle("source", fontSize=7.6, leading=11, spaceAfter=7, keepWithNext=True,
                                 **{**common, "textColor": MUTED}),
        "part": ParagraphStyle("part", fontSize=8.0, leading=12.0, spaceAfter=5, keepWithNext=True,
                               **{**common, "textColor": MUTED}),
        "section": ParagraphStyle("section", fontName="Malgun-Bold", fontSize=20.5, leading=29,
                                  spaceBefore=2, spaceAfter=17, textColor=ACCENT, wordWrap="CJK", keepWithNext=True),
        "chapter": ParagraphStyle("chapter", fontName="Malgun-Bold", fontSize=15.2, leading=22,
                                  spaceBefore=15, spaceAfter=8, textColor=ACCENT, wordWrap="CJK", keepWithNext=True),
        "sub": ParagraphStyle("sub", fontName="Malgun-Bold", fontSize=11.6, leading=18,
                              spaceBefore=9, spaceAfter=5.5, textColor=INK, wordWrap="CJK", keepWithNext=True),
        "label": ParagraphStyle("label", fontName="Malgun-Bold", fontSize=9.7, leading=15,
                                spaceBefore=6, spaceAfter=3, textColor=ACCENT, wordWrap="CJK", keepWithNext=True),
        "table": ParagraphStyle("table", fontSize=9.0, leading=13.3, spaceAfter=0, **common),
        "table_head": ParagraphStyle("table_head", fontName="Malgun-Bold", fontSize=9.0, leading=13.3,
                                     textColor=INK, wordWrap="CJK", spaceAfter=0),
        "bullet": ParagraphStyle("bullet", fontSize=10.3, leading=16.1, leftIndent=11,
                                 firstLineIndent=-10, spaceAfter=4.4, **common),
        "cover": ParagraphStyle("cover", fontName="Malgun-Bold", fontSize=27.5, leading=42,
                                alignment=TA_CENTER, textColor=INK, wordWrap="CJK"),
        "toc0": ParagraphStyle("toc0", fontName="Malgun-Bold", fontSize=10.2, leading=17,
                               textColor=ACCENT, leftIndent=0, firstLineIndent=0,
                               spaceBefore=9, spaceAfter=3, wordWrap="CJK", rightIndent=25),
        "toc1": ParagraphStyle("toc1", fontName="Malgun", fontSize=9.4, leading=15.6,
                               textColor=INK, leftIndent=14, firstLineIndent=0,
                               spaceBefore=0, spaceAfter=2, wordWrap="CJK", rightIndent=25),
    }
    # Only these short end-page cases use a slightly denser detailed-note
    # rhythm.  Font size, all other chapters, tables, and SQL stay unchanged.
    styles["body_compact"] = ParagraphStyle("body_compact", parent=styles["body"],
                                             leading=15.2, spaceAfter=5.0)
    styles["bullet_compact"] = ParagraphStyle("bullet_compact", parent=styles["bullet"],
                                               leading=15.2, spaceAfter=3.8)
    return styles


def text_width(value, size=8.8):
    return sum(pdfmetrics.stringWidth(run, font, size) for font, run in font_runs(value, mono=True))


def logical_wrap(line: str, max_width: float, font_size: float) -> list[str]:
    """Wrap presentation lines at SQL whitespace/punctuation when possible."""
    global WRAP_EVENTS
    line = line.expandtabs(4).rstrip()
    if not line:
        return [""]
    if text_width(line, font_size) <= max_width:
        return [line]
    WRAP_EVENTS += 1
    indent = re.match(r"\s*", line).group(0)
    continuation = indent + "    "
    # Very deeply indented original SQL still must fit the printed page.
    while text_width(continuation, font_size) > max_width * .28:
        continuation = continuation[2:]
    result = []
    rest = line
    while text_width(rest, font_size) > max_width:
        width, last_break, quote, cut = 0, 0, None, 0
        for i, char in enumerate(rest):
            width += text_width(char, font_size)
            if width > max_width:
                break
            cut = i + 1
            if char in "'\"":
                if quote == char:
                    quote = None
                elif quote is None:
                    quote = char
            if quote is None and (char.isspace() or char in ",);+-*/=<>|"):
                last_break = i + 1
            if ord(char) >= 0x2E80:
                last_break = i + 1
        if last_break >= max(1, int(cut * .43)):
            cut = last_break
        cut = max(1, cut)
        result.append(rest[:cut].rstrip())
        # Whitespace at a visual line break is represented by continuation
        # indentation; no SQL tokens or punctuation are added.
        rest = continuation + rest[cut:].lstrip()
    result.append(rest)
    return result


class SQLBlock(Flowable):
    """Splittable code panel with true mono Latin and Korean font fallback."""
    def __init__(self, sql=None, *, lines=None, continued=False, font_size=8.8, leading=12.1):
        super().__init__()
        self.raw = clean(sql or "")
        self.lines = lines
        self.continued = continued
        self.font_size, self.leading = font_size, leading
        self.pad = 10
        self.head = 12
        self.spaceBefore = 3
        self.spaceAfter = 9
        self.width = TEXT_W

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        if self.lines is None:
            self.lines = []
            raw_lines = self.raw.strip("\n").split("\n")
            for line in raw_lines:
                self.lines.extend(logical_wrap(line, availWidth - 2 * self.pad, self.font_size))
        self.height = 2 * self.pad + self.head + len(self.lines) * self.leading
        return self.width, self.height

    def split(self, availWidth, availHeight):
        self.wrap(availWidth, availHeight)
        count = math.floor((availHeight - 2 * self.pad - self.head) / self.leading)
        if count < 3 or count >= len(self.lines):
            return []
        if len(self.lines) - count == 1 and count > 3:
            count -= 1
        return [
            SQLBlock(lines=self.lines[:count], continued=self.continued,
                     font_size=self.font_size, leading=self.leading),
            SQLBlock(lines=self.lines[count:], continued=True,
                     font_size=self.font_size, leading=self.leading),
        ]

    def draw(self):
        c = self.canv
        c.setFillColor(colors.HexColor("#F5F7F8"))
        c.setStrokeColor(RULE)
        c.setLineWidth(.45)
        c.roundRect(0, 0, self.width, self.height, 3, fill=1, stroke=1)
        c.setFont("Malgun", 7.3)
        c.setFillColor(MUTED)
        c.drawString(self.pad, self.height - self.pad - 5.5,
                     "SQL 원문 (계속)" if self.continued else "SQL 원문")
        y = self.height - self.pad - self.head - self.font_size
        for line in self.lines:
            x = self.pad
            for font, run in font_runs(line, mono=True):
                c.setFont(font, self.font_size)
                c.setFillColor(INK)
                c.drawString(x, y, run)
                x += pdfmetrics.stringWidth(run, font, self.font_size)
            y -= self.leading


class NoteDocument(BaseDocTemplate):
    def __init__(self, output, **kwargs):
        super().__init__(str(output), pagesize=A4, leftMargin=LEFT, rightMargin=RIGHT,
                         topMargin=TOP, bottomMargin=BOTTOM, title=TITLE,
                         author="", subject="제공된 원문 PDF에 근거한 SQL 학습 노트", **kwargs)
        self.heading_pages = []
        self._outline_level = -1
        frame = Frame(LEFT, BOTTOM, TEXT_W, PAGE_H - TOP - BOTTOM,
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="body")
        cover_frame = Frame(LEFT, BOTTOM, TEXT_W, PAGE_H - TOP - BOTTOM,
                            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="cover")
        self.addPageTemplates([
            PageTemplate(id="cover", frames=[cover_frame], onPage=self.cover_page),
            PageTemplate(id="normal", frames=[frame], onPage=self.normal_page),
        ])

    def beforeDocument(self):
        self.heading_pages = []
        self._outline_level = -1

    def cover_page(self, canvas, doc):
        canvas.setTitle(TITLE)
        canvas.setAuthor("")
        canvas.setSubject("원문 순서에 따른 SQL 학습 노트")

    def normal_page(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(.45)
        canvas.line(LEFT, PAGE_H - 34, PAGE_W - RIGHT, PAGE_H - 34)
        canvas.setFont("Malgun", 7.4)
        canvas.setFillColor(MUTED)
        canvas.drawString(LEFT, PAGE_H - 26, TITLE)
        canvas.setFont("Malgun", 8.0)
        canvas.drawRightString(PAGE_W - RIGHT, 25, str(doc.page))
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if not hasattr(flowable, "toc_level"):
            return
        level = flowable.toc_level
        title, key = flowable.toc_title, flowable.toc_key
        self.canv.bookmarkPage(key)
        # Only section/chapter headings are registered, so all levels advance
        # at most by one and the PDF outline remains valid across build passes.
        self.canv.addOutlineEntry(title, key, level=level, closed=(level == 0))
        self.notify("TOCEntry", (level, inline(title, markdown=False), self.page, key))
        self.heading_pages.append({"level": level, "title": title, "key": key, "page": self.page})


class Book:
    def __init__(self, chapters, review):
        self.chapters, self.review = chapters, review
        self.s = make_styles()
        self.story = []
        self.code_index = {}
        self.chapter_ids = []
        self._key_counter = 0
        self._compact_notes = False
        for ch in chapters:
            self.chapter_ids.append(str(ch.get("id", "")))
            for code in ch.get("codes", []):
                key = str(code.get("id", ""))
                if key and key in self.code_index:
                    raise ValueError(f"Duplicate SQL code id: {key}")
                if key:
                    self.code_index[key] = (ch, code)

    def p(self, text, style="body"):
        if text is not None and str(text).strip():
            if self._compact_notes and style == "body":
                style = "body_compact"
            self.story.append(Paragraph(inline(text), self.s[style]))

    def heading(self, text, level, key):
        p = Paragraph(inline(text, markdown=False), self.s["section" if level == 0 else "chapter"])
        p.toc_level, p.toc_title, p.toc_key = level, clean(text), key
        self.story.append(p)

    def label(self, text):
        self.p(text, "label")

    def bullets(self, items, numbered=False, check=False):
        for i, item in enumerate(items or [], 1):
            marker = "[ ] " if check else (f"{i}. " if numbered else "- ")
            style = "bullet_compact" if self._compact_notes else "bullet"
            self.story.append(Paragraph(inline(marker + str(item)), self.s[style]))

    def table(self, headers, rows, widths=None):
        if not headers and not rows:
            return
        count = len(headers) if headers else max(len(r) for r in rows)
        if count == 0:
            return
        if not headers:
            headers = [""] * count
        source_rows = [headers] + list(rows or [])
        data = []
        for ri, row in enumerate(source_rows):
            row = list(row)
            row = row[:count] + [""] * max(0, count - len(row))
            data.append([Paragraph(inline(cell), self.s["table_head" if ri == 0 else "table"]) for cell in row])
        if widths is None:
            # Modest content weighting avoids narrow label columns and huge
            # prose columns while retaining balanced, printable comparisons.
            weights = []
            for ci in range(count):
                values = [clean(r[ci]) for r in source_rows if ci < len(r)]
                samples = sorted(min(len(v), 100) for v in values)
                typical = samples[min(len(samples)-1, int(len(samples) * .7))] if samples else 5
                weights.append(max(7, math.sqrt(typical + 3) * 3))
            if count > 1:
                weights = [min(max(weights) * 1.0, max(min(weights) * 1.0, w)) for w in weights]
            total = sum(weights)
            widths = [TEXT_W * w / total for w in weights]
        t = LongTable(data, colWidths=widths, repeatRows=1, hAlign="LEFT",
                      splitByRow=1, splitInRow=1, spaceBefore=4, spaceAfter=10)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAF0F3")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LINEBELOW", (0, 0), (-1, 0), .6, colors.HexColor("#AABDC8")),
            ("LINEBELOW", (0, 1), (-1, -1), .35, RULE),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFBFC")]),
            ("NOSPLIT", (0, 0), (-1, 0)),
        ]))
        self.story.append(t)

    def blocks(self, blocks):
        for block in blocks or []:
            kind = block.get("type", "p")
            if kind == "p":
                self.p(block.get("text", ""))
            elif kind in ("bullets", "list"):
                self.bullets(block.get("items", []), numbered=bool(block.get("numbered")))
            elif kind == "table":
                self.table(block.get("headers", []), block.get("rows", []))
            elif kind in ("heading", "subheading"):
                self.p(block.get("text", block.get("title", "")), "sub")
            elif kind == "code":
                self.story.append(SQLBlock(block.get("sql", block.get("text", ""))))
            else:
                raise ValueError(f"Unknown content block type: {kind}")

    def source(self, value, prefix="원문 PDF"):
        if not value:
            return
        if isinstance(value, (list, tuple)):
            value = ", ".join(str(v) for v in value)
        value = str(value).strip()
        if value.startswith("원문") or value.startswith("PDF"):
            self.p(value, "source")
        else:
            self.p(f"{prefix} {value}" + ("" if value.endswith("쪽") else "쪽"), "source")

    def ch_title(self, chapter):
        # The author may include the printed chapter number in the title.
        title = str(chapter.get("title", ""))
        order = chapter.get("order", "")
        if re.match(r"^(제\s*)?\d+\s*장", title):
            return title
        return f"{order}. {title}"

    def chapter_heading(self, ch, prefix):
        self.heading(self.ch_title(ch), 1, f"{prefix}-{ch['id']}")
        if ch.get("part"):
            self.p(ch["part"], "part")
        self.source(ch.get("source_range"))

    def code(self, code, concise=False):
        self.p(code.get("title", code.get("id", "SQL")), "sub")
        self.source(code.get("source_pdf_pages", []))
        sql = code.get("sql", "")
        if sql.strip():
            self.story.append(SQLBlock(sql))
        if code.get("purpose"):
            self.label("수행하는 작업")
            self.p(code["purpose"])
        if not concise:
            keywords = code.get("keywords", [])
            if keywords:
                self.label("주요 키워드와 구문의 역할")
                self.table(["키워드·구문", "역할"], [[k.get("term", ""), k.get("role", "")] for k in keywords],
                           [TEXT_W * .26, TEXT_W * .74])
            if code.get("process"):
                self.label("원문에 따른 처리 과정")
                self.bullets(code["process"], numbered=True)
            if code.get("result"):
                self.label("원문 결과·설명")
                self.p(code["result"])
            if code.get("learn"):
                self.label("반드시 이해할 부분")
                self.bullets(code["learn"])

    def section_start(self, title, key):
        self.story.append(PageBreak())
        self.heading(title, 0, key)

    def compose(self):
        # The cover intentionally contains exactly the requested title, with no
        # author, publisher, subtitle, decorative text, or folio.
        self.story.append(Spacer(1, 285))
        self.story.append(Paragraph(TITLE, self.s["cover"]))
        self.story.append(NextPageTemplate("normal"))
        self.story.append(PageBreak())
        self.p("목차", "section")
        toc = TableOfContents()
        toc.levelStyles = [self.s["toc0"], self.s["toc1"]]
        toc.dotsMinLevel = 0
        self.story.append(toc)
        self.story.append(Spacer(1, 15))
        self.p(self.review.get("scope_note",
            "수록 범위: 제공된 PDF에서 확인한 본문 12장을 원문 순서대로 정리했습니다. "
            "원문 목차에 기재된 부록은 제공된 파일에 포함되어 있지 않습니다. "
            "출처에 표시한 쪽수는 원문 PDF의 파일 쪽수입니다."), "small")

        self.section_start("1. 챕터별 핵심 내용 요약", "sec-overview")
        for ch in self.chapters:
            self.chapter_heading(ch, "overview")
            overview = ch.get("overview", {})
            for field, label, numbered in (
                ("topics", "핵심 주제와 주요 개념", False),
                ("flow", "핵심 내용의 흐름", True),
                ("focus", "학습 집중 포인트", False),
            ):
                if overview.get(field):
                    self.label(label)
                    self.bullets(overview[field], numbered=numbered)

        self.section_start("2. 챕터별 상세 학습 노트", "sec-notes")
        for idx, ch in enumerate(self.chapters):
            self._compact_notes = str(ch.get("id", "")) in {"II-3", "III-6", "III-7"}
            if idx:
                self.story.append(PageBreak())
            self.chapter_heading(ch, "notes")
            for section in ch.get("sections", []):
                self.p(section.get("title", ""), "sub")
                self.source(section.get("source_pages"))
                self.blocks(section.get("blocks", []))
            if ch.get("key_points"):
                self.p("반드시 기억할 핵심 포인트", "sub")
                self.bullets(ch["key_points"])
            if ch.get("final_summary"):
                self.p("챕터 최종 요약", "sub")
                self.bullets(ch["final_summary"])
        self._compact_notes = False

        self.section_start("3. SQL 문법과 원문 코드 해설", "sec-sql")
        self.p("다음 SQL은 원문에서 옮긴 코드입니다. 긴 줄의 시각적 줄바꿈과 들여쓰기를 정리했으며, "
               "원문에 확인되지 않은 실행 결과는 덧붙이지 않았습니다.", "small")
        for ch in self.chapters:
            if not ch.get("codes"):
                continue
            self.chapter_heading(ch, "sql")
            for code in ch["codes"]:
                self.code(code)

        self.section_start("4. 핵심 개념 비교 및 구조화 자료", "sec-comparisons")
        comparison_chapters = [ch for ch in self.chapters if ch.get("comparisons")]
        for ch in comparison_chapters:
            self.chapter_heading(ch, "compare")
            for comp in ch["comparisons"]:
                self.p(comp.get("title", ""), "sub")
                self.table(comp.get("headers", []), comp.get("rows", []))

        self.section_start("5. 전체 핵심 내용 복습 자료", "sec-review")
        self.heading("전체 핵심 요약", 1, "review-core")
        self.blocks(self.review.get("blocks", []))

        if self.review.get("syntax"):
            self.heading("SQL 문법 요약표", 1, "review-syntax")
            grouped = collections.OrderedDict()
            for syntax in self.review["syntax"]:
                grouped.setdefault(syntax.get("category", "주요 문법"), []).append(syntax)
            for category, entries in grouped.items():
                self.p(category, "sub")
                self.table(["문법", "원문에 근거한 형태", "역할·조건 / 원문 PDF"], [
                    [s.get("name", ""), s.get("form", ""),
                     str(s.get("role", "")) + (f"\n출처: {s['source']}" if s.get("source") else "")]
                    for s in entries
                ], [TEXT_W * .19, TEXT_W * .39, TEXT_W * .42])

        if self.review.get("comparisons"):
            self.heading("주요 개념 비교표", 1, "review-comparisons")
            for comp in self.review["comparisons"]:
                self.p(comp.get("title", ""), "sub")
                self.table(comp.get("headers", []), comp.get("rows", []))

        if self.review.get("code_groups"):
            self.heading("주요 코드 모음", 1, "review-codes")
            for group in self.review["code_groups"]:
                self.p(group.get("title", ""), "sub")
                for cid in group.get("code_ids", []):
                    if str(cid) not in self.code_index:
                        raise ValueError(f"review.json references missing SQL code id: {cid}")
                    _, code = self.code_index[str(cid)]
                    self.code(code, concise=True)

        self.heading("핵심 내용 체크리스트", 1, "review-checklist")
        if self.review.get("checklist"):
            for group in self.review["checklist"]:
                self.p(group.get("title", ""), "sub")
                self.bullets(group.get("items", []), check=True)
        else:
            for ch in self.chapters:
                if ch.get("checklist"):
                    self.p(self.ch_title(ch), "sub")
                    self.bullets(ch["checklist"], check=True)
        return self.story


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        raise ValueError(f"Unable to load valid JSON: {path}: {exc}") from exc


def load_inputs(chapter_dir, review_path):
    paths = sorted(chapter_dir.glob("*.json"))
    if not paths:
        raise FileNotFoundError(f"No chapter JSON files found: {chapter_dir}")
    chapters = [read_json(path) for path in paths]
    chapters.sort(key=lambda ch: (float(ch.get("order", 9999)), str(ch.get("id", ""))))
    ids = [str(ch.get("id", "")) for ch in chapters]
    if any(not v for v in ids) or len(ids) != len(set(ids)):
        raise ValueError("Every chapter must have a nonempty, unique id")
    for ch in chapters:
        if not ch.get("title"):
            raise ValueError(f"Chapter title is empty: {ch['id']}")
        if not ch.get("sections"):
            raise ValueError(f"Chapter has no detailed note sections: {ch['id']}")
    review = read_json(review_path)
    return chapters, review


def build(chapter_dir, review_path, output):
    register_fonts(Path("C:/Windows/Fonts"))
    chapters, review = load_inputs(chapter_dir, review_path)
    book = Book(chapters, review)
    story = book.compose()
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = NoteDocument(output)
    doc.multiBuild(story, maxPasses=5)
    # This report supports the caller's independent content and layout audit;
    # no PDF success claim is made until the caller opens and renders it.
    report = {
        "output": str(output), "pages": doc.page,
        "chapter_count": len(chapters), "chapters": [
            {"id": ch["id"], "title": ch["title"], "source_range": ch.get("source_range"),
             "sections": len(ch.get("sections", [])), "codes": len(ch.get("codes", [])),
             "comparisons": len(ch.get("comparisons", []))} for ch in chapters],
        "headings": doc.heading_pages, "code_ids": list(book.code_index),
        "unknown_glyphs": dict(MISSING), "wrapped_sql_lines_across_build_passes": WRAP_EVENTS,
        "embedded_fonts": ["Malgun", "Malgun-Bold", "Consolas", "Consolas-Bold"],
    }
    report_path = output.with_suffix(".build_report.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output), "pages": doc.page, "chapters": len(chapters),
                      "code_count": len(book.code_index), "report": str(report_path),
                      "unknown_glyphs": dict(MISSING)}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chapters", type=Path, default=HERE / "chapters")
    parser.add_argument("--review", type=Path, default=HERE / "review.json")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build(args.chapters, args.review, args.output)


if __name__ == "__main__":
    main()
