"""Slide patterns shared by the morning and afternoon decks."""

from kit import *


def head(s, kicker, title):
    """The top of a content slide: small blue kicker, then the title."""
    eyebrow(s, MARGIN, Inches(0.62), kicker)
    txt(s, MARGIN, Inches(0.98), SW - MARGIN * 2, Inches(0.6), title, size=T_H1, color=INK, bold=True)


def statement(s, kicker, lines, sub):
    """A slide that says one thing, large."""
    eyebrow(s, MARGIN, Inches(1.55), kicker)
    rich(s, MARGIN, Inches(2.05), Inches(11.8), Inches(2.0), lines, size=T_DISPLAY, spacing=1.14)
    txt(s, MARGIN, Inches(4.6), Inches(11.4), Inches(1.2), sub, size=T_H2, color=INK2, spacing=1.42)


def takeaway(s, parts):
    """The grey line near the bottom. parts = [(text, bold), ...]"""
    rich(s, MARGIN, Inches(6.3), SW - MARGIN * 2, Inches(0.45),
         [[(text, bold, INK if bold else INK2) for text, bold in parts]],
         size=T_H2, align=PP_ALIGN.CENTER)


def code(s, x, y, w, h, text, size=15, fill=GREY_L, color=INK):
    """Code or terminal output on a grey panel."""
    box(s, x, y, w, h, fill=fill)
    pad = Inches(0.3)
    tb = txt(s, x + pad, y + Inches(0.24), w - pad * 2, h - Inches(0.4), text, size=size, color=color, spacing=1.25)
    for p in tb.text_frame.paragraphs:
        for r in p.runs:
            r.font.name = MONO
    return tb


def card(s, x, y, w, h, title, body, fill=GREY_L, line=None, tcol=INK, tsize=T_H2, bsize=T_BODY):
    """A pastel card with a bold title and a few lines under it."""
    box(s, x, y, w, h, fill=fill, line=line, lw=1.25)
    pad = Inches(0.32)
    txt(s, x + pad, y + Inches(0.28), w - pad * 2, Inches(0.45), title, size=tsize, color=tcol, bold=True)
    txt(s, x + pad, y + Inches(0.28) + Pt(tsize) * 1.7, w - pad * 2, h - Inches(1.0), body,
        size=bsize, color=INK2, spacing=1.32)


def node(s, x, y, w, h, title, sub=None, fill=GREY_L, line=None, tcol=INK, tsize=T_BODY):
    """A labelled box for diagrams."""
    shape = box(s, x, y, w, h, fill=fill, line=line, lw=1.25)
    label(shape, title, sub, tcol=tcol, tsize=tsize, ssize=T_SMALL,
          scol=RGBColor(0xD2, 0xE3, 0xFC) if fill == BLUE else INK2)
    return shape


def picture(s, name, x, y, w):
    """A screenshot with a thin grey frame."""
    pic = s.shapes.add_picture(str(ASSETS / name), E(x), E(y), width=E(w))
    pic.line.color.rgb = RGBColor(0xDA, 0xDC, 0xE0)
    pic.line.width = Pt(1)
    return pic


def build_deck(path, slides, no_footer=()):
    """slides is a list of functions. Each draws on a blank slide and returns its speaker notes."""
    prs = Presentation()
    prs.slide_width, prs.slide_height = SW, SH
    for number, draw in enumerate(slides, start=1):
        s = blank(prs)
        spoken = draw(s)
        gstrip(s)
        if draw.__name__ not in no_footer:
            footer(s, number, len(slides))
        notes(s, spoken)
    prs.save(str(path))
    print("saved", path, len(slides), "slides")
