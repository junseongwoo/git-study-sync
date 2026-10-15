#!/usr/bin/env python3
"""Render source-grounded C++ chapter JSON files as a searchable A4 PDF.

No C++ instructional content lives in this module. The caller records the PDF
artifact-operation marker once before invoking this renderer.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import re
import unicodedata
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Flowable, Frame, LongTable, NextPageTemplate, PageBreak,
    PageTemplate, Paragraph, Spacer, TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE.parents[2] / "output" / "pdf" / "A_Tour_Of_CPP_요약_정리.pdf"
PAGE_W, PAGE_H = A4
LEFT = RIGHT = 46
TOP, BOTTOM = 53, 43
TEXT_W = PAGE_W - LEFT - RIGHT
INK = colors.HexColor("#202C38")
ACCENT = colors.HexColor("#173F68")
MUTED = colors.HexColor("#65717C")
RULE = colors.HexColor("#D5DFE4")
FONT_CHARS = {}
MISSING_PROSE_GLYPHS = collections.Counter()
WRAP_EVENTS = 0


def register_fonts(font_dir):
    for name, filename in (
        ("Malgun", "malgun.ttf"), ("Malgun-Bold", "malgunbd.ttf"),
        ("Consolas", "consola.ttf"), ("Consolas-Bold", "consolab.ttf"),
    ):
        path = Path(font_dir) / filename
        if not path.exists():
            raise FileNotFoundError(f"Required embedded font missing: {path}")
        pdfmetrics.registerFont(TTFont(name, str(path)))
        FONT_CHARS[name] = set(pdfmetrics.getFont(name).face.charWidths)
    pdfmetrics.registerFontFamily("Malgun", normal="Malgun", bold="Malgun-Bold",
                                  italic="Malgun", boldItalic="Malgun-Bold")
    pdfmetrics.registerFontFamily("Consolas", normal="Consolas", bold="Consolas-Bold",
                                  italic="Consolas", boldItalic="Consolas-Bold")


TRANSLATE = {
    "\u00a0": " ", "\u2007": " ", "\u202f": " ", "\u200b": "",
    "\ufeff": "", "\u00ad": "", "\u2010": "-", "\u2011": "-",
    "\u2012": "-", "\u2013": "-", "\u2014": "-", "\u2212": "-",
    "\ufb01": "fi", "\ufb02": "fl", "\u2610": "[ ]", "\u2713": "v",
}


def clean(value):
    """Normalize prose typography only. Never call this on source code."""
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        value = ", ".join(str(x) for x in value)
    value = unicodedata.normalize("NFC", str(value)).replace("\r\n", "\n").replace("\r", "\n")
    valid = set().union(*FONT_CHARS.values()) if FONT_CHARS else set()
    out = []
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
            name = f"U+{ord(char):04X} {unicodedata.name(char, 'UNKNOWN')}"
            MISSING_PROSE_GLYPHS[name] += 1
            out.append(f"[문자 U+{ord(char):04X}]")
    return "".join(out)


def validate_code_glyphs(value, context):
    valid = set().union(*FONT_CHARS.values())
    missing = sorted({ord(c) for c in value if c not in "\n\r\t" and ord(c) not in valid})
    controls = sorted({ord(c) for c in value if c not in "\n\r\t" and unicodedata.category(c) in ("Cc", "Cs")})
    if missing or controls:
        descriptions = [f"U+{n:04X} {unicodedata.name(chr(n), 'UNKNOWN')}" for n in sorted(set(missing + controls))]
        raise ValueError(f"Source code has unrenderable characters; not modified: {context}: {descriptions}")


def font_runs(value, mono=False, bold=False):
    preferred = ("Consolas" if mono else "Malgun") + ("-Bold" if bold else "")
    fallback = "Malgun-Bold" if bold else "Malgun"
    last, run = None, ""
    for char in value:
        font = preferred if ord(char) in FONT_CHARS[preferred] else fallback
        if ord(char) not in FONT_CHARS[font]:
            font = next((f for f in FONT_CHARS if ord(char) in FONT_CHARS[f]), fallback)
        if font != last and run:
            yield last, run
            run = ""
        run += char
        last = font
    if run:
        yield last, run


def plain_inline(value, mono=False, bold=False):
    return "".join(escape(run) if not mono and not bold and font == "Malgun"
                   else f'<font name="{font}">{escape(run)}</font>'
                   for font, run in font_runs(value, mono=mono, bold=bold))


def inline(value, markdown=True):
    value = clean(value)
    if not markdown:
        return plain_inline(value).replace("\n", "<br/>")
    result = []
    for piece in re.split(r"(`[^`\n]+`|\*\*[^*\n]+\*\*)", value):
        if piece.startswith("`") and piece.endswith("`") and len(piece) > 1:
            result.append(plain_inline(piece[1:-1], mono=True))
        elif piece.startswith("**") and piece.endswith("**") and len(piece) > 3:
            result.append(plain_inline(piece[2:-2], bold=True))
        else:
            result.append(plain_inline(piece))
    return "".join(result).replace("\n", "<br/>")


def code_inline(value, context="inline code"):
    value = str(value or "")
    validate_code_glyphs(value, context)
    return plain_inline(value, mono=True).replace("\n", "<br/>")


def page_ranges(values):
    """Compress confirmed page numbers, retaining noncontiguous ranges."""
    values = sorted(set(int(v) for v in values or []))
    runs = []
    for n in values:
        if runs and n == runs[-1][-1] + 1:
            runs[-1].append(n)
        else:
            runs.append([n])
    return ", ".join(str(r[0]) if len(r) == 1 else f"{r[0]}-{r[-1]}" for r in runs)


def source_text(source, prefix="출처"):
    if not source:
        return f"{prefix}: [페이지 번호 확인 불가]"
    if not isinstance(source, dict):
        return f"{prefix}: {clean(source)}"
    parts = []
    if source.get("printed"):
        parts.append(f"책 {page_ranges(source['printed'])}쪽")
    if source.get("pdf"):
        parts.append(f"원문 PDF {page_ranges(source['pdf'])}쪽")
    return f"{prefix}: " + (" / ".join(parts) or "[페이지 번호 확인 불가]")


def make_styles():
    common = dict(fontName="Malgun", textColor=INK, wordWrap="CJK", allowWidows=0, allowOrphans=0)
    return {
        "body": ParagraphStyle("body", fontSize=10.3, leading=16.0, spaceAfter=6, **common),
        "small": ParagraphStyle("small", fontSize=8.2, leading=12.5, spaceAfter=6,
                                 **{**common, "textColor": MUTED}),
        "source": ParagraphStyle("source", fontSize=7.6, leading=11.2, spaceAfter=6,
                                  keepWithNext=True, **{**common, "textColor": MUTED}),
        "section": ParagraphStyle("section", fontName="Malgun-Bold", fontSize=20.0, leading=29,
                                   spaceAfter=15, textColor=ACCENT, wordWrap="CJK", keepWithNext=True),
        "chapter": ParagraphStyle("chapter", fontName="Malgun-Bold", fontSize=16.0, leading=23,
                                   spaceBefore=18, spaceAfter=8, textColor=ACCENT, wordWrap="CJK", keepWithNext=True),
        "sub": ParagraphStyle("sub", fontName="Malgun-Bold", fontSize=11.8, leading=18,
                               spaceBefore=11, spaceAfter=5, textColor=INK, wordWrap="CJK", keepWithNext=True),
        "label": ParagraphStyle("label", fontName="Malgun-Bold", fontSize=9.8, leading=15.2,
                                 spaceBefore=7, spaceAfter=3, textColor=ACCENT, wordWrap="CJK", keepWithNext=True),
        "bullet": ParagraphStyle("bullet", fontSize=10.3, leading=16.0, leftIndent=11,
                                  firstLineIndent=-10, spaceAfter=4.0, **common),
        "table": ParagraphStyle("table", fontSize=9.0, leading=13.4, spaceAfter=0, **common),
        "table_head": ParagraphStyle("table_head", fontName="Malgun-Bold", fontSize=9.0,
                                      leading=13.4, textColor=INK, wordWrap="CJK", spaceAfter=0),
        "cover": ParagraphStyle("cover", fontName="Malgun-Bold", fontSize=28.0, leading=39,
                                 alignment=TA_CENTER, textColor=INK, wordWrap="CJK"),
        "subtitle": ParagraphStyle("subtitle", fontName="Malgun", fontSize=17, leading=25,
                                    alignment=TA_CENTER, textColor=ACCENT),
        "toc0": ParagraphStyle("toc0", fontName="Malgun-Bold", fontSize=10.2, leading=17,
                                textColor=ACCENT, spaceBefore=10, spaceAfter=3, rightIndent=26, wordWrap="CJK"),
        "toc1": ParagraphStyle("toc1", fontName="Malgun", fontSize=9.4, leading=15.6,
                                textColor=INK, leftIndent=14, spaceAfter=2, rightIndent=26, wordWrap="CJK"),
    }


def text_width(value, size=8.8):
    return sum(pdfmetrics.stringWidth(run, font, size) for font, run in font_runs(value, mono=True))


def visual_wrap(line, max_width, font_size):
    """Change presentation whitespace only; never replace source-code tokens."""
    global WRAP_EVENTS
    line = line.expandtabs(4)
    if not line or text_width(line, font_size) <= max_width:
        return [line]
    WRAP_EVENTS += 1
    indent = re.match(r"\s*", line).group(0)
    continuation = indent + "    "
    while text_width(continuation, font_size) > max_width * .28:
        continuation = continuation[2:]
    result, rest = [], line
    while text_width(rest, font_size) > max_width:
        width, cut, last_break = 0, 0, 0
        for i, char in enumerate(rest):
            width += text_width(char, font_size)
            if width > max_width:
                break
            cut = i + 1
            if char.isspace():
                last_break = i + 1
        if last_break >= max(1, int(cut * .40)):
            cut = last_break
        cut = max(1, cut)
        result.append(rest[:cut].rstrip())
        rest = continuation + rest[cut:].lstrip()
    result.append(rest)
    return result


class CodeBlock(Flowable):
    """Splittable code panel; source data is retained without normalization."""
    def __init__(self, code="", *, lines=None, continued=False, font_size=8.8, leading=12.1):
        super().__init__()
        self.raw, self.lines = str(code), lines
        self.continued = continued
        self.font_size, self.leading = font_size, leading
        self.pad, self.head = 10, 12
        self.spaceBefore, self.spaceAfter = 3, 9
        self.keepWithNext = True

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        if self.lines is None:
            self.lines = []
            for line in self.raw.splitlines() or [""]:
                self.lines.extend(visual_wrap(line, availWidth - 2 * self.pad, self.font_size))
        self.height = 2 * self.pad + self.head + len(self.lines) * self.leading
        return self.width, self.height

    def split(self, availWidth, availHeight):
        self.wrap(availWidth, availHeight)
        # Short examples stay intact; long examples retain continued panels.
        if len(self.lines) <= 20:
            return []
        count = math.floor((availHeight - 2 * self.pad - self.head) / self.leading)
        if count < 3 or count >= len(self.lines):
            return []
        if len(self.lines) - count == 1 and count > 3:
            count -= 1
        return [CodeBlock(lines=self.lines[:count], continued=self.continued,
                          font_size=self.font_size, leading=self.leading),
                CodeBlock(lines=self.lines[count:], continued=True,
                          font_size=self.font_size, leading=self.leading)]

    def draw(self):
        c = self.canv
        c.setFillColor(colors.HexColor("#F5F7FA"))
        c.setStrokeColor(RULE)
        c.setLineWidth(.45)
        c.roundRect(0, 0, self.width, self.height, 3, fill=1, stroke=1)
        c.setFont("Malgun", 7.3)
        c.setFillColor(MUTED)
        c.drawString(self.pad, self.height - self.pad - 5.5,
                     "C++ 원문 (계속)" if self.continued else "C++ 원문")
        y = self.height - self.pad - self.head - self.font_size
        for line in self.lines:
            x = self.pad
            for font, run in font_runs(line, mono=True):
                c.setFont(font, self.font_size)
                c.setFillColor(INK)
                c.drawString(x, y, run)
                x += pdfmetrics.stringWidth(run, font, self.font_size)
            y -= self.leading


class Cover(Flowable):
    def __init__(self, title, styles):
        super().__init__()
        self.title, self.styles = title, styles

    def wrap(self, availWidth, availHeight):
        self.width, self.height = availWidth, availHeight - .1
        return self.width, self.height

    def draw(self):
        title = Paragraph(inline(self.title, markdown=False), self.styles["cover"])
        subtitle = Paragraph("요약 정리", self.styles["subtitle"])
        _, th = title.wrap(self.width, self.height)
        _, sh = subtitle.wrap(self.width, self.height)
        gap = 17
        # Frame vertical midpoint corrected to the actual A4-page midpoint.
        mid = PAGE_H / 2 - BOTTOM
        y = mid + (th + gap + sh) / 2
        title.drawOn(self.canv, 0, y - th)
        subtitle.drawOn(self.canv, 0, y - th - gap - sh)


class NoteDocument(BaseDocTemplate):
    def __init__(self, output, title, **kwargs):
        self.book_title = title
        super().__init__(str(output), pagesize=A4, leftMargin=LEFT, rightMargin=RIGHT,
                         topMargin=TOP, bottomMargin=BOTTOM, title=title,
                         author="", subject="제공된 원문에 근거한 C++ 학습 교재", **kwargs)
        self.heading_pages, self.anchor_pages = [], {}
        frame = Frame(LEFT, BOTTOM, TEXT_W, PAGE_H - TOP - BOTTOM,
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="body")
        cover_frame = Frame(LEFT, BOTTOM, TEXT_W, PAGE_H - TOP - BOTTOM,
                            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="cover")
        self.addPageTemplates([
            PageTemplate(id="cover", frames=[cover_frame], onPage=self.cover_page),
            PageTemplate(id="normal", frames=[frame], onPage=self.normal_page),
        ])

    def beforeDocument(self):
        self.heading_pages, self.anchor_pages = [], {}

    def cover_page(self, canvas, doc):
        canvas.setTitle(self.book_title)
        canvas.setAuthor("")

    def normal_page(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(.45)
        canvas.line(LEFT, PAGE_H - 34, PAGE_W - RIGHT, PAGE_H - 34)
        canvas.setFont("Malgun", 7.4)
        canvas.setFillColor(MUTED)
        running_title = "C++ 학습 노트" if self.book_title == "[원문에서 확인할 수 없음]" else self.book_title
        canvas.drawString(LEFT, PAGE_H - 26, running_title)
        canvas.setFont("Malgun", 8)
        canvas.drawRightString(PAGE_W - RIGHT, 25, str(doc.page))
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if not hasattr(flowable, "anchor_key"):
            return
        key = flowable.anchor_key
        self.canv.bookmarkPage(key)
        self.anchor_pages[key] = self.page
        if getattr(flowable, "outline_level", None) is not None:
            self.canv.addOutlineEntry(flowable.anchor_title, key,
                                     level=flowable.outline_level,
                                     closed=(flowable.outline_level <= 1))
        if getattr(flowable, "toc_level", None) is not None:
            self.notify("TOCEntry", (flowable.toc_level,
                         inline(flowable.anchor_title, markdown=False), self.page, key))
            self.heading_pages.append({"level": flowable.toc_level,
                "title": flowable.anchor_title, "key": key, "page": self.page})


def section_key(chapter, number):
    return "section-" + str(chapter) + "-" + re.sub(r"[^A-Za-z0-9_-]", "-", str(number))


class Book:
    def __init__(self, chapters, info, known_pages=None):
        self.chapters, self.info, self.pages = chapters, info, known_pages or {}
        self.s, self.story = make_styles(), []
        self.code_index = {}
        self.section_index = {}
        for ch in chapters:
            for sec in ch["sections"]:
                self.section_index[(ch["id"], str(sec.get("number", "")))] = section_key(ch["id"], sec.get("number", ""))
            for code in ch.get("codes", []):
                self.code_index[code["id"]] = (ch, code)
        self.rendered_codes = collections.Counter()

    def p(self, text, style="body", raw_markup=False):
        if text is not None and str(text).strip():
            p = Paragraph(str(text) if raw_markup else inline(text), self.s[style])
            self.story.append(p)
            return p

    def heading(self, text, level, key, toc=True, style=None):
        style = style or ("section" if level == 0 else "chapter" if level == 1 else "sub")
        p = self.p(text, style)
        p.anchor_key, p.anchor_title, p.outline_level = key, clean(text), level
        p.toc_level = level if toc else None
        return p

    def bullets(self, items, numbered=False):
        for i, item in enumerate(items or [], 1):
            self.p((f"{i}. " if numbered else "- ") + str(item), "bullet")

    def source(self, source, prefix="출처"):
        self.p(source_text(source, prefix), "source")

    def table(self, headers, rows, widths=None, markup_columns=None, mono_columns=None, compact=False):
        if not headers and not rows:
            return
        n = len(headers) if headers else max(len(r) for r in rows)
        headers = headers or [""] * n
        data = []
        for ri, row in enumerate([headers] + list(rows or [])):
            row = list(row)[:n] + [""] * max(0, n - len(row))
            cells = []
            for ci, cell in enumerate(row):
                style = self.s["table_head" if ri == 0 else "table"]
                if ri and ci in (markup_columns or set()):
                    text = str(cell)
                elif ri and ci in (mono_columns or set()):
                    text = code_inline(cell, "syntax table")
                else:
                    text = inline(cell)
                cells.append(Paragraph(text, style))
            data.append(cells)
        if widths is None:
            weights = []
            for ci in range(n):
                samples = sorted(min(len(str(r[ci])), 110) for r in [headers] + list(rows or []) if ci < len(r))
                typical = samples[min(len(samples) - 1, int(len(samples) * .7))] if samples else 8
                weights.append(max(9, math.sqrt(typical + 3) * 3))
            widths = [TEXT_W * w / sum(weights) for w in weights]
        elif abs(sum(widths) - TEXT_W) > 1:
            widths = [TEXT_W * float(w) / sum(widths) for w in widths]
        table = LongTable(data, colWidths=widths, repeatRows=1, hAlign="LEFT", splitByRow=1,
                          splitInRow=1, spaceBefore=4, spaceAfter=10)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAF0F6")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 4 if compact else 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4 if compact else 6),
            ("LINEBELOW", (0, 0), (-1, 0), .6, colors.HexColor("#AABDC8")),
            ("LINEBELOW", (0, 1), (-1, -1), .35, RULE),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFBFC")]),
            ("NOSPLIT", (0, 0), (-1, 0)),
        ]))
        self.story.append(table)

    def code(self, code, concise=False):
        cid = str(code["id"])
        p = self.p(code.get("title", cid), "sub")
        if not self.rendered_codes[cid]:
            p.anchor_key, p.anchor_title, p.outline_level, p.toc_level = "code-" + cid, clean(code.get("title", cid)), None, None
        self.rendered_codes[cid] += 1
        self.source(code.get("source"), "코드 출처")
        if code.get("excerpt"):
            note = self.p(code.get("excerpt_note") or "원문 코드의 일부를 발췌했으며, 나머지 부분은 생략했습니다.", "small")
            note.keepWithNext = True
        if str(code.get("code", "")).strip():
            self.story.append(CodeBlock(code["code"]))
        if code.get("meaning"):
            self.p("코드의 의미", "label")
            self.p(code["meaning"])
        if not concise and code.get("process"):
            self.p("동작 과정", "label")
            self.bullets(code["process"], numbered=True)
        self.p("원문 실행 결과", "label")
        self.p(code.get("output") or "[원문에 실행 결과 미제시]")
        if code.get("cautions"):
            self.p("원문 주의 사항", "label")
            self.bullets(code["cautions"])

    def blocks(self, blocks):
        for b in blocks or []:
            if b.get("source"):
                self.source(b["source"])
            kind = b.get("type", "p")
            if kind == "p":
                self.p(b.get("text", ""))
            elif kind in ("bullets", "list"):
                self.bullets(b.get("items", []), numbered=bool(b.get("numbered")))
            elif kind == "table":
                self.table(b.get("headers", []), b.get("rows", []), widths=b.get("widths"))
            elif kind in ("heading", "subheading"):
                self.p(b.get("text", b.get("title", "")), "sub")
            elif kind == "code_ref":
                self.code(self.code_index[str(b["id"])][1])
            elif kind == "code":
                raw = b.get("code", b.get("text", ""))
                validate_code_glyphs(str(raw), "inline block")
                self.story.append(CodeBlock(raw))
            else:
                raise ValueError(f"Unknown block type: {kind}")

    def start(self, title, key):
        self.story.append(PageBreak())
        self.heading(title, 0, key)

    def linked_page(self, key):
        label = str(self.pages.get(key, "쪽수 계산 중"))
        return f'<a href="#{escape(key)}" color="#173F68">{label}</a>'

    def concept_index(self):
        terms = collections.defaultdict(set)
        for ch in self.chapters:
            for entry in ch.get("index_terms", []):
                term = str(entry.get("term", "")).strip()
                sec = str(entry.get("section", ""))
                key = self.section_index.get((ch["id"], sec))
                if term and key:
                    terms[term].add(key)
        rows = []
        for term in sorted(terms, key=lambda t: (unicodedata.normalize("NFKC", t).casefold(), t)):
            keys = sorted(terms[term], key=lambda k: (self.pages.get(k, 999999), k))
            links, seen_pages = [], set()
            for key in keys:
                page = self.pages.get(key)
                if page is None or page not in seen_pages:
                    links.append(self.linked_page(key))
                if page is not None:
                    seen_pages.add(page)
            rows.append([term, ", ".join(links)])
        if rows:
            paired = []
            for i in range(0, len(rows), 2):
                paired.append(rows[i] + (rows[i + 1] if i + 1 < len(rows) else ["", ""]))
            self.table(["개념", "교재 쪽", "개념", "교재 쪽"], paired,
                       [TEXT_W * .38, TEXT_W * .12, TEXT_W * .38, TEXT_W * .12],
                       markup_columns={1, 3}, compact=True)

    def compose(self):
        self.story.extend([Cover(self.info["confirmed_title"], self.s), NextPageTemplate("normal"), PageBreak()])
        self.p("목차", "section")
        toc = TableOfContents()
        toc.levelStyles = [self.s["toc0"], self.s["toc1"]]
        toc.dotsMinLevel = 0
        self.story.append(toc)

        self.start("책 정보 및 정리 범위", "book-scope")
        self.p("원문에서 확인한 책 정보", "sub")
        self.p("책 제목: " + self.info["confirmed_title"])
        if self.info.get("author"):
            self.p("저자: " + str(self.info["author"]))
        self.p(self.info["scope_note"])
        if self.info.get("source_pages"):
            self.p("제공된 PDF의 전체 쪽수: " + str(self.info["source_pages"]))
        if self.info.get("available_range"):
            self.p("확인 가능한 범위: " + str(self.info["available_range"]))
        if self.info.get("limitations"):
            self.p("원문 확인 범위와 제한", "sub")
            self.bullets(self.info["limitations"])
        if self.info.get("pagination_note"):
            self.p(self.info["pagination_note"], "small")

        self.start("전체 학습 내용 개요", "book-overview")
        if self.info.get("overview"):
            if isinstance(self.info["overview"][0], dict):
                self.blocks(self.info["overview"])
            else:
                self.bullets(self.info["overview"])
        self.table(["장", "원문 범위"], [[ch["title"], source_text(ch.get("source"))] for ch in self.chapters],
                   [TEXT_W * .55, TEXT_W * .45])

        self.start("장별 요약 및 상세 정리", "book-notes")
        for ch in self.chapters:
            self.heading(ch["title"], 1, "chapter-" + ch["id"])
            self.source(ch.get("source"))
            if ch.get("overview"):
                self.p("학습 내용 개요", "sub")
                self.bullets(ch["overview"])
            if ch.get("flow"):
                self.p("설명의 흐름", "label")
                self.bullets(ch["flow"], numbered=True)
            for sec in ch["sections"]:
                number, title = str(sec.get("number", "")), str(sec.get("title", ""))
                text = title if title.startswith(number + " ") else (number + " " + title).strip()
                self.heading(text, 2, section_key(ch["id"], number), toc=False)
                self.source(sec.get("source"))
                self.blocks(sec.get("blocks", []))
            # Unreferenced codes must remain visible; a report flags them for
            # the author to move beside the most relevant source section.
            unplaced = [code for code in ch.get("codes", []) if not self.rendered_codes[code["id"]]]
            if unplaced:
                self.p("문법 및 원문 코드 정리", "sub")
                for code in unplaced:
                    self.code(code)
            if ch.get("key_points"):
                self.p("중요 내용 요약", "sub")
                self.bullets(ch["key_points"])
            if ch.get("comparisons"):
                self.p("혼동하기 쉬운 내용", "sub")
                for comp in ch["comparisons"]:
                    self.p(comp.get("title", ""), "label")
                    self.source(comp.get("source"))
                    self.table(comp.get("headers", []), comp.get("rows", []))
            if ch.get("review"):
                self.p("장 마무리 복습", "sub")
                self.bullets(ch["review"])
            if ch.get("limitations"):
                self.p("원문 확인 메모", "sub")
                self.bullets(ch["limitations"])

        self.start("핵심 문법 및 코드 모음", "book-syntax-code")
        if self.info.get("syntax"):
            self.p("핵심 문법", "sub")
            for entry in self.info["syntax"]:
                self.p(entry.get("title", ""), "label")
                self.source(entry.get("source"))
                if entry.get("form"):
                    self.story.append(CodeBlock(entry["form"]))
                self.p(entry.get("meaning", ""))
        if self.info.get("code_collection"):
            self.p("주요 원문 코드", "sub")
            for group in self.info["code_collection"]:
                self.p(group.get("title", ""), "sub")
                for cid in group.get("ids", []):
                    self.code(self.code_index[str(cid)][1], concise=True)
        else:
            self.p("원문 코드 찾아보기", "sub")
            for ch in self.chapters:
                if ch.get("codes"):
                    self.p(ch["title"], "label")
                    self.table(["코드", "출처", "학습 교재 쪽"], [[code.get("title", code["id"]),
                        source_text(code.get("source")), self.linked_page("code-" + code["id"])]
                        for code in ch["codes"]], [TEXT_W * .44, TEXT_W * .40, TEXT_W * .16], markup_columns={2}, compact=True)

        self.start("주요 개념 복습", "book-review")
        for ch in self.chapters:
            if ch.get("review") or ch.get("key_points"):
                self.p(ch["title"], "sub")
                self.source(ch.get("source"))
                self.bullets(ch.get("review") or ch.get("key_points"))

        self.start("개념 색인", "book-index")
        self.concept_index()
        return self.story


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except Exception as exc:
        raise ValueError(f"Unable to load JSON: {path}: {exc}") from exc


def load_inputs(chapter_dir, info_path):
    paths = sorted(Path(chapter_dir).glob("*.json"))
    if not paths:
        raise FileNotFoundError(f"No chapter JSON files: {chapter_dir}")
    chapters = [read_json(path) for path in paths]
    chapters.sort(key=lambda ch: (float(ch.get("order", 9999)), str(ch.get("id", ""))))
    ids = [ch.get("id") for ch in chapters]
    if any(not v for v in ids) or len(ids) != len(set(ids)):
        raise ValueError("Chapter IDs must be nonempty and unique")
    code_ids, refs = set(), []
    for ch in chapters:
        if not ch.get("title") or not ch.get("sections"):
            raise ValueError(f"Chapter title and detailed sections required: {ch['id']}")
        numbers = [str(sec.get("number", "")) for sec in ch["sections"]]
        if any(not n for n in numbers) or len(numbers) != len(set(numbers)):
            raise ValueError(f"Section numbers must be nonempty and unique within {ch['id']}")
        for sec in ch["sections"]:
            for b in sec.get("blocks", []):
                if b.get("type") == "code_ref":
                    refs.append(str(b.get("id", "")))
        for code in ch.get("codes", []):
            cid = str(code.get("id", ""))
            if not cid or cid in code_ids:
                raise ValueError(f"Code ID missing or duplicate: {cid}")
            code_ids.add(cid)
            validate_code_glyphs(str(code.get("code", "")), cid)
        for term in ch.get("index_terms", []):
            if str(term.get("section", "")) not in numbers:
                raise ValueError(f"Unknown index section in {ch['id']}: {term}")
    unknown = sorted(set(refs) - code_ids)
    if unknown:
        raise ValueError(f"Unknown code references: {unknown}")
    info = read_json(info_path)
    if not str(info.get("confirmed_title", "")).strip() or not info.get("scope_note"):
        raise ValueError("book_info.json requires confirmed_title and scope_note")
    for entry in info.get("syntax", []):
        validate_code_glyphs(str(entry.get("form", "")), "syntax: " + str(entry.get("title", "")))
    for group in info.get("code_collection", []):
        for cid in group.get("ids", []):
            if str(cid) not in code_ids:
                raise ValueError(f"Unknown code collection ID: {cid}")
    return chapters, info, sorted(code_ids - set(refs))


def build(chapter_dir, info_path, output):
    register_fonts(Path("C:/Windows/Fonts"))
    chapters, info, unplaced = load_inputs(chapter_dir, info_path)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    known_pages = {}
    for index_pass in range(1, 5):
        book = Book(chapters, info, known_pages)
        doc = NoteDocument(output, info["confirmed_title"])
        doc.multiBuild(book.compose(), maxPasses=6)
        actual = dict(doc.anchor_pages)
        if actual == known_pages:
            break
        known_pages = actual
    else:
        raise RuntimeError("Index/page cross references did not converge after 4 full builds")
    report = {
        "output": str(output), "pages": doc.page, "index_builds": index_pass,
        "confirmed_title": info["confirmed_title"], "chapter_count": len(chapters),
        "chapters": [{"id": ch["id"], "title": ch["title"], "source": ch.get("source"),
            "sections": len(ch["sections"]), "codes": len(ch.get("codes", [])),
            "coverage": len(ch.get("coverage", [])), "limitations": ch.get("limitations", [])} for ch in chapters],
        "headings": doc.heading_pages, "anchor_pages": doc.anchor_pages,
        "unplaced_code_refs": unplaced, "code_ids": list(book.code_index),
        "code_hashes": {cid: hashlib.sha256(str(code.get("code", "")).encode("utf-8")).hexdigest()
                        for cid, (_, code) in book.code_index.items()},
        "unknown_prose_glyphs": dict(MISSING_PROSE_GLYPHS),
        "code_character_replacements": [],
        "visual_code_line_wraps_across_build_passes": WRAP_EVENTS,
        "embedded_fonts": list(FONT_CHARS),
    }
    report_path = output.with_suffix(".build_report.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output), "pages": doc.page, "chapters": len(chapters),
        "code_count": len(book.code_index), "report": str(report_path),
        "unknown_prose_glyphs": dict(MISSING_PROSE_GLYPHS), "unplaced_code_refs": unplaced}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chapters", type=Path, default=HERE / "chapters")
    parser.add_argument("--info", type=Path, default=HERE / "book_info.json")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if args.validate_only:
        register_fonts(Path("C:/Windows/Fonts"))
        chapters, info, unplaced = load_inputs(args.chapters, args.info)
        print(json.dumps({"valid": True, "chapters": len(chapters), "title": info["confirmed_title"],
                          "unplaced_code_refs": unplaced}, ensure_ascii=False))
    else:
        build(args.chapters, args.info, args.output)


if __name__ == "__main__":
    main()
