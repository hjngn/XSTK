#!/usr/bin/env python3
"""Dựng báo cáo Word từ các chương Markdown.

Chạy (trong thư mục gốc repository):
    python report/build_report.py              -> report/output/BaoCao_XSTK.docx
    python report/build_report.py --only 1 2   -> chỉ dựng Chương 1, 2 (kèm tài liệu tham khảo)

Định dạng (theo quy chuẩn trình bày báo cáo thường dùng ở các trường đại học Việt Nam):
    khổ A4; lề trái 3 cm, phải 2 cm, trên 2 cm, dưới 2 cm; Times New Roman 13; giãn dòng 1,5;
    đề mục cấp 1 in hoa, đậm, căn giữa, sang trang mới; chú thích hình dưới hình, chú thích bảng trên bảng;
    số trang ở giữa chân trang; mục lục tự động (bấm F9 / "Update field" trong Word để cập nhật số trang).

Yêu cầu: pandoc (hoặc gói pypandoc-binary) và python-docx.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CHAPTERS = HERE / "chapters"
OUT = HERE / "output"
FONT = "Times New Roman"

ORDER = {
    0: "00_loi_mo_dau.md",
    1: "01_gioi_thieu.md",
    2: "02_co_so_ly_thuyet.md",
    3: "03_ket_qua.md",
    4: "04_ket_luan.md",
    5: "05_tai_lieu_tham_khao.md",
    6: "06_phu_luc.md",
}

METADATA = """---
title: "BÁO CÁO BÀI TẬP LỚN MÔN XÁC SUẤT – THỐNG KÊ"
subtitle: "Phân tích các yếu tố ảnh hưởng đến giá xe ô tô đã qua sử dụng: dữ liệu CarDekho"
author:
  - "Nhóm: Khoa · Uyên · Sang · Nguyên"
  - "Giảng viên hướng dẫn: ……………………"
  - "Lớp: ……… · Học kỳ: ………"
date: "{date}"
lang: vi-VN
toc-title: "MỤC LỤC"
---
"""


def pandoc_bin() -> str:
    exe = shutil.which("pandoc")
    if exe:
        return exe
    try:
        import pypandoc  # type: ignore
        return pypandoc.get_pandoc_path()
    except Exception as exc:  # pragma: no cover
        raise SystemExit("Không tìm thấy pandoc. Cài: pip install pypandoc-binary") from exc


# ------------------------------------------------------------------ reference.docx
def set_font(style, size=None, bold=None, italic=None, color_black=True):
    style.font.name = FONT
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), FONT)
    for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        if rfonts.get(qn(attr)) is not None:
            del rfonts.attrib[qn(attr)]
    if size:
        style.font.size = Pt(size)
    if bold is not None:
        style.font.bold = bold
    if italic is not None:
        style.font.italic = italic
    if color_black:
        style.font.color.rgb = RGBColor(0, 0, 0)


def build_reference(pandoc: str, path: Path) -> None:
    subprocess.run([pandoc, "-o", str(path), "--print-default-data-file", "reference.docx"], check=True)
    doc = Document(path)
    sec = doc.sections[0]
    sec.orientation = WD_ORIENT.PORTRAIT
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.left_margin, sec.right_margin = Cm(3), Cm(2)
    sec.top_margin, sec.bottom_margin = Cm(2), Cm(2)

    by_name = {st.name: st for st in doc.styles}

    class _Styles:
        def __getitem__(self, key):
            return by_name[key]

        def __iter__(self):
            return iter(by_name.values())

    styles = _Styles()
    for name in ("Normal", "Body Text", "First Paragraph", "Compact", "Block Text"):
        if name not in [s.name for s in styles]:
            continue
        st = styles[name]
        set_font(st, 13)
        pf = st.paragraph_format
        pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        pf.space_before, pf.space_after = Pt(0), Pt(6)
        if name in ("Body Text", "First Paragraph"):
            pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if "Compact" in [s.name for s in styles]:
        styles["Compact"].paragraph_format.space_after = Pt(2)

    heading_spec = {"Heading 1": (16, True, False), "Heading 2": (14, True, False),
                    "Heading 3": (13, True, True), "Heading 4": (13, False, True)}
    for name, (size, bold, italic) in heading_spec.items():
        st = styles[name]
        set_font(st, size, bold, italic)
        pf = st.paragraph_format
        pf.space_before, pf.space_after = Pt(12 if name != "Heading 1" else 0), Pt(6)
        pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        pf.keep_with_next = True
    styles["Heading 1"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    styles["Heading 1"].paragraph_format.page_break_before = True

    for name in ("Title", "Subtitle", "Author", "Date"):
        if name in [s.name for s in styles]:
            st = styles[name]
            set_font(st, {"Title": 18, "Subtitle": 15}.get(name, 13), name in ("Title", "Subtitle"))
            st.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for name in ("Image Caption", "Table Caption", "Caption"):
        if name in [s.name for s in styles]:
            st = styles[name]
            set_font(st, 12, name == "Table Caption", name != "Table Caption")
            st.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            st.paragraph_format.space_before, st.paragraph_format.space_after = Pt(3), Pt(9)
    if "Captioned Figure" in [s.name for s in styles]:
        styles["Captioned Figure"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for name in ("Source Code", "Verbatim Char"):
        if name in [s.name for s in styles]:
            styles[name].font.size = Pt(10)
    doc.save(path)


# ------------------------------------------------------------------ hậu xử lý
def add_page_number_footer(doc: Document) -> None:
    for sec in doc.sections:
        p = sec.footer.paragraphs[0] if sec.footer.paragraphs else sec.footer.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        for tag, text in (("begin", None), (None, "PAGE"), ("end", None)):
            if tag:
                el = OxmlElement("w:fldChar")
                el.set(qn("w:fldCharType"), tag)
            else:
                el = OxmlElement("w:instrText")
                el.set(qn("xml:space"), "preserve")
                el.text = text
            run._r.append(el)


def style_tables(doc: Document) -> None:
    for table in doc.tables:
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl_pr = table._tbl.tblPr
        borders = OxmlElement("w:tblBorders")
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            el = OxmlElement(f"w:{edge}")
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), "4")
            el.set(qn("w:color"), "000000")
            borders.append(el)
        old = tbl_pr.find(qn("w:tblBorders"))
        if old is not None:
            tbl_pr.remove(old)
        tbl_pr.append(borders)
        for r_i, row in enumerate(table.rows):
            for cell in row.cells:
                for par in cell.paragraphs:
                    par.paragraph_format.line_spacing = 1.15
                    par.paragraph_format.space_after = Pt(2)
                    par.paragraph_format.alignment = par.paragraph_format.alignment
                    for run in par.runs:
                        run.font.size = Pt(11)
                        run.font.name = FONT
                        if r_i == 0:
                            run.font.bold = True


# ------------------------------------------------------------------ ghép Markdown
def demote(md: str, by: int) -> str:
    lines = []
    for line in md.splitlines():
        m = re.match(r"^(#+)\s", line)
        lines.append(("#" * by + line) if m else line)
    return "\n".join(lines)


def inline_appendix(md: str) -> str:
    for doc_name in ("tu_dien_du_lieu.md", "nhat_ky_lam_sach.md"):
        path = ROOT / "docs" / doc_name
        pattern = re.compile(rf"Xem tệp `docs/{doc_name}`[^\n]*\n")
        if path.exists() and pattern.search(md):
            body = path.read_text(encoding="utf-8")
            body = re.sub(r"^# .*\n", "", body, count=1)              # bỏ tiêu đề cấp 1 của tài liệu
            body = demote(body, 2)
            body = re.sub(r"^(#{3,}) (.*)$", r"\1 \2 {.unnumbered}", body, flags=re.M)
            md = pattern.sub(lambda _: body + "\n", md)
    return md


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=int, nargs="*", help="chỉ dựng các chương này (ví dụ: --only 1 2)")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--date", default="Tháng 11/2026")
    args = ap.parse_args()

    pandoc = pandoc_bin()
    keys = sorted(ORDER) if not args.only else sorted(set(args.only) | {5})
    out = args.out or (OUT / ("BaoCao_XSTK.docx" if not args.only
                              else "BaoCao_Chuong_" + "_".join(str(k) for k in args.only) + ".docx"))
    out.parent.mkdir(parents=True, exist_ok=True)

    parts = [METADATA.format(date=args.date)]
    for k in keys:
        text = (CHAPTERS / ORDER[k]).read_text(encoding="utf-8")
        parts.append(inline_appendix(text) if k == 6 else text)
    combined = "\n\n".join(parts)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        src = tmp / "report.md"
        src.write_text(combined, encoding="utf-8")
        ref = tmp / "reference.docx"
        build_reference(pandoc, ref)
        subprocess.run([pandoc, str(src), "-o", str(out), "--from", "markdown+pipe_tables+tex_math_dollars",
                        "--reference-doc", str(ref), "--toc", "--toc-depth=3",
                        "--resource-path", f"{CHAPTERS}:{ROOT}"], check=True)

    doc = Document(out)
    style_tables(doc)
    add_page_number_footer(doc)
    doc.save(out)
    print("Đã tạo:", out.relative_to(ROOT) if out.is_relative_to(ROOT) else out)


if __name__ == "__main__":
    main()
