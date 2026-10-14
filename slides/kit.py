"""The slide kit: colours, type scale and the few shapes every slide is built from.

Same look as the Aria deck: white canvas, the four Google colours used with
intent, a four colour strip along the bottom of every slide.
"""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

HERE = Path(__file__).parent
ASSETS = HERE / "assets"

# ---------- design tokens ----------
BLUE = RGBColor(0x1A, 0x73, 0xE8)
BLUE_D = RGBColor(0x17, 0x4E, 0xA6)
BLUE_L = RGBColor(0xE8, 0xF0, 0xFE)
RED = RGBColor(0xD9, 0x30, 0x25)
RED_L = RGBColor(0xFC, 0xE8, 0xE6)
YEL = RGBColor(0xF9, 0xAB, 0x00)
YEL_L = RGBColor(0xFE, 0xF7, 0xE0)
GRN = RGBColor(0x1E, 0x8E, 0x3E)
GRN_L = RGBColor(0xE6, 0xF4, 0xEA)
INK = RGBColor(0x20, 0x21, 0x24)
INK2 = RGBColor(0x5F, 0x63, 0x68)
INK3 = RGBColor(0x9A, 0xA0, 0xA6)
GREY_L = RGBColor(0xF1, 0xF3, 0xF4)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

FONT = "Arial"       # guaranteed on Windows and Mac Office, same grotesque family as Roboto
MONO = "Consolas"
# strict scale, in points
T_DISPLAY, T_H1, T_H2, T_BODY, T_SMALL, T_MICRO = 40, 32, 24, 16, 12, 9.5

SW, SH = Inches(13.333), Inches(7.5)
MARGIN = Inches(0.72)


def E(v):
    """EMU must be an integer. Any arithmetic with / produces floats, and a
    float in the XML makes PowerPoint reject the whole file."""
    return Emu(int(round(v)))


def txt(slide, x, y, w, h, text, size=T_BODY, color=INK, bold=False,
        align=PP_ALIGN.LEFT, spacing=1.0, anchor=MSO_ANCHOR.TOP, caps=False):
    """A plain text box. Returns the frame so callers can add more runs."""
    tb = slide.shapes.add_textbox(E(x), E(y), E(w), E(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        r = p.add_run()
        r.text = line.upper() if caps else line
        f = r.font
        f.name, f.size, f.bold, f.color.rgb = FONT, Pt(size), bold, color
    return tb


def rich(slide, x, y, w, h, parts, size=T_BODY, spacing=1.4, align=PP_ALIGN.LEFT):
    """parts = list of lines; each line is a list of (text, bold, color)."""
    tb = slide.shapes.add_textbox(E(x), E(y), E(w), E(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, line in enumerate(parts):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        for text, bold, color in line:
            r = p.add_run()
            r.text = text
            r.font.name, r.font.size, r.font.bold = FONT, Pt(size), bold
            r.font.color.rgb = color
    return tb


def box(slide, x, y, w, h, fill=None, line=None, radius=True, lw=1.5):
    shp = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
        E(x), E(y), E(w), E(h))
    if radius:
        try:
            shp.adjustments[0] = 0.16
        except Exception:
            pass
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(lw)
    shp.shadow.inherit = False
    return shp


def oval(slide, cx, cy, r, fill, line=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.OVAL, E(cx - r), E(cy - r), E(r * 2), E(r * 2))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(1.5)
    shp.shadow.inherit = False
    return shp


def label(shape, title, sub=None, tcol=INK, scol=INK2, tsize=T_H2, ssize=T_SMALL):
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = Inches(0.02)
    tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.line_spacing = 1.0
    r = p.add_run(); r.text = title
    r.font.name, r.font.size, r.font.bold, r.font.color.rgb = FONT, Pt(tsize), True, tcol
    if sub:
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        p2.line_spacing = 1.0
        r2 = p2.add_run(); r2.text = sub
        r2.font.name, r2.font.size, r2.font.color.rgb = FONT, Pt(ssize), scol


def arrow(slide, x1, y1, x2, y2, col=INK3, w=1.75):
    """A straight connector with an arrow head."""
    from pptx.enum.shapes import MSO_CONNECTOR
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, E(x1), E(y1), E(x2), E(y2))
    c.line.color.rgb = col
    c.line.width = Pt(w)
    el = c.line._get_or_add_ln()
    from pptx.oxml.ns import qn
    tail = el.makeelement(qn('a:tailEnd'), {'type': 'triangle', 'w': 'med', 'len': 'med'})
    el.append(tail)
    return c


def plainline(slide, x1, y1, x2, y2, col=RGBColor(0xDA, 0xDC, 0xE0), w=2.0):
    from pptx.enum.shapes import MSO_CONNECTOR
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, E(x1), E(y1), E(x2), E(y2))
    c.line.color.rgb = col
    c.line.width = Pt(w)
    return c


def gstrip(slide, thickness=Inches(0.07)):
    """The Google four colour strip along the bottom edge."""
    seg = SW / 4
    for i, col in enumerate([BLUE, RED, YEL, GRN]):
        s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                   E(seg * i), E(SH - thickness), E(seg), E(thickness))
        s.fill.solid(); s.fill.fore_color.rgb = col
        s.line.fill.background(); s.shadow.inherit = False


def gdots(slide, x, y, d=Inches(0.19), gap=Inches(0.07)):
    for i, col in enumerate([BLUE, RED, YEL, GRN]):
        cx = x + (d + gap) * (i % 2)
        cy = y + (d + gap) * (i // 2)
        s = slide.shapes.add_shape(MSO_SHAPE.OVAL, E(cx), E(cy), E(d), E(d))
        s.fill.solid(); s.fill.fore_color.rgb = col
        s.line.fill.background(); s.shadow.inherit = False


def eyebrow(slide, x, y, text, col=BLUE):
    tb = txt(slide, x, y, Inches(8), Inches(0.3), text, size=T_MICRO, color=col,
             bold=True, caps=True)
    for p in tb.text_frame.paragraphs:
        for r in p.runs:
            r.font._rPr.set('spc', '160')
    return tb


def footer(slide, n, total):
    txt(slide, MARGIN, SH - Inches(0.62), Inches(4), Inches(0.28),
        "Kiruthika Subramani", size=T_MICRO, color=INK3)
    txt(slide, SW - MARGIN - Inches(2), SH - Inches(0.62), Inches(2), Inches(0.28),
        f"{n} / {total}", size=T_MICRO, color=INK3, align=PP_ALIGN.RIGHT)


def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text
