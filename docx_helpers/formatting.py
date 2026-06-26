"""
docx_helpers/formatting.py
===========================
Helper level-rendah untuk styling dokumen Word (python-docx):
font sel, lebar kolom tabel, border, shading, margin sel.
Fungsi di sini murni memanipulasi objek python-docx / OOXML dan
TIDAK mengandung logika bisnis surat apa pun.
"""

from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def set_cell_font(cell, font_name="Arial", font_size=11, bold=False):
    for para in cell.paragraphs:
        for run in para.runs:
            run.font.name = font_name
            run.font.size = Pt(font_size)
            run.bold = bold
        pPr = para._p.get_or_add_pPr()
        rPr = OxmlElement('w:rPr')
        rFonts = OxmlElement('w:rFonts')
        rFonts.set(qn('w:ascii'), font_name)
        rFonts.set(qn('w:hAnsi'), font_name)
        rPr.append(rFonts)
        sz = OxmlElement('w:sz')
        sz.set(qn('w:val'), str(font_size * 2))
        rPr.append(sz)
        pPr.append(rPr)


def set_table_fixed_widths(table, col_widths_twips):
    tbl = table._tbl
    tblPr = tbl.find(qn('w:tblPr'))
    if tblPr is None:
        tblPr = OxmlElement('w:tblPr')
        tbl.insert(0, tblPr)

    total_w = sum(col_widths_twips)
    tblW = tblPr.find(qn('w:tblW'))
    if tblW is None:
        tblW = OxmlElement('w:tblW')
        tblPr.append(tblW)
    tblW.set(qn('w:w'), str(total_w))
    tblW.set(qn('w:type'), 'dxa')

    tblLayout = tblPr.find(qn('w:tblLayout'))
    if tblLayout is None:
        tblLayout = OxmlElement('w:tblLayout')
        tblPr.append(tblLayout)
    tblLayout.set(qn('w:type'), 'fixed')

    tblGrid = tbl.find(qn('w:tblGrid'))
    if tblGrid is not None:
        tbl.remove(tblGrid)
    tblGrid = OxmlElement('w:tblGrid')
    for w in col_widths_twips:
        gridCol = OxmlElement('w:gridCol')
        gridCol.set(qn('w:w'), str(w))
        tblGrid.append(gridCol)
    tbl.insert(list(tbl).index(tblPr) + 1, tblGrid)

    for row in table.rows:
        for i, cell in enumerate(row.cells):
            if i < len(col_widths_twips):
                tc = cell._tc
                tcPr = tc.find(qn('w:tcPr'))
                if tcPr is None:
                    tcPr = OxmlElement('w:tcPr')
                    tc.insert(0, tcPr)
                tcW = tcPr.find(qn('w:tcW'))
                if tcW is None:
                    tcW = OxmlElement('w:tcW')
                    tcPr.append(tcW)
                tcW.set(qn('w:w'), str(col_widths_twips[i]))
                tcW.set(qn('w:type'), 'dxa')


def set_all_cell_borders(table, border_style="single", border_size=4, border_color="000000"):
    border_xml = {
        'top': (border_style, border_size, border_color),
        'bottom': (border_style, border_size, border_color),
        'left': (border_style, border_size, border_color),
        'right': (border_style, border_size, border_color),
        'insideH': (border_style, border_size, border_color),
        'insideV': (border_style, border_size, border_color),
    }
    for row in table.rows:
        for cell in row.cells:
            tc = cell._tc
            tcPr = tc.find(qn('w:tcPr'))
            if tcPr is None:
                tcPr = OxmlElement('w:tcPr')
                tc.insert(0, tcPr)
            tcBorders = tcPr.find(qn('w:tcBorders'))
            if tcBorders is not None:
                tcPr.remove(tcBorders)
            tcBorders = OxmlElement('w:tcBorders')
            for side, (style, size, color) in border_xml.items():
                border_el = OxmlElement(f'w:{side}')
                border_el.set(qn('w:val'), style)
                border_el.set(qn('w:sz'), str(size))
                border_el.set(qn('w:space'), '0')
                border_el.set(qn('w:color'), color)
                tcBorders.append(border_el)
            tcPr.append(tcBorders)


def shade_cell(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)


def set_cell_margins(cell, top=60, bottom=60, left=80, right=80):
    tc = cell._tc
    tcPr = tc.find(qn('w:tcPr'))
    if tcPr is None:
        tcPr = OxmlElement('w:tcPr')
        tc.insert(0, tcPr)
    tcMar = tcPr.find(qn('w:tcMar'))
    if tcMar is not None:
        tcPr.remove(tcMar)
    tcMar = OxmlElement('w:tcMar')
    for side, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        el = OxmlElement(f'w:{side}')
        el.set(qn('w:w'), str(val))
        el.set(qn('w:type'), 'dxa')
        tcMar.append(el)
    tcPr.append(tcMar)
