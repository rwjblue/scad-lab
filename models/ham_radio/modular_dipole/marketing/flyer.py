#!/usr/bin/env python3
"""Build the one-page modular dipole flyer from the current model render.

Requires ReportLab. Output: output/pdf/modular-dipole-flyer.pdf.
The product image remains unmodified; its viewport is clipped in the PDF.
"""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

HERE = Path(__file__).resolve().parent
MODEL = HERE.parent
ROOT = HERE.parents[3]
OUTPUT = ROOT / "output/pdf/modular-dipole-flyer.pdf"
WIDTH, HEIGHT = 612, 792
INK = "#173C38"
MUTED = "#547069"
PAPER = "#F5F3ED"
ORANGE = "#D97531"
BLUE = "#187D98"
GREEN = "#4D9970"
RULE = "#D8DFD8"


def fonts():
    collection = Path("/System/Library/Fonts/Avenir Next.ttc")
    if collection.exists():
        for name, index in [("Flyer", 7), ("FlyerMedium", 5), ("FlyerDemi", 2), ("FlyerBold", 0)]:
            pdfmetrics.registerFont(TTFont(name, str(collection), subfontIndex=index))
    else:
        from reportlab.pdfbase.pdfmetrics import Font
        for name, base in [("Flyer", "Helvetica"), ("FlyerMedium", "Helvetica"),
                           ("FlyerDemi", "Helvetica-Bold"), ("FlyerBold", "Helvetica-Bold")]:
            pdfmetrics.registerFont(Font(name, base, "WinAnsiEncoding"))
    pdfmetrics.registerFontFamily("Flyer", normal="Flyer", bold="FlyerDemi")


def color(value):
    return colors.HexColor(value)


def paragraph(c, content, x, top, width, size=11, leading=15, font="Flyer", ink=INK, max_height=100):
    style = ParagraphStyle("flyer", fontName=font, fontSize=size, leading=leading,
                           textColor=color(ink), spaceBefore=0, spaceAfter=0)
    p = Paragraph(content, style)
    _, height = p.wrap(width, HEIGHT)
    assert height <= max_height, f"Text exceeds its region: {content!r} ({height} > {max_height})"
    p.drawOn(c, x, HEIGHT - top - height)
    return height


def label(c, value, x, top, size=8.5, ink=MUTED, tracking=1, align="left", font="FlyerDemi"):
    c.saveState()
    width = pdfmetrics.stringWidth(value, font, size) + tracking * max(0, len(value) - 1)
    if align == "right":
        x -= width
    elif align == "center":
        x -= width / 2
    text = c.beginText(x, HEIGHT - top - size)
    text.setFont(font, size)
    text.setFillColor(color(ink))
    text.setCharSpace(tracking)
    text.textOut(value)
    c.drawText(text)
    c.restoreState()


def line(c, x1, y1, x2, y2, ink=RULE, weight=1):
    c.setStrokeColor(color(ink))
    c.setLineWidth(weight)
    c.line(x1, HEIGHT-y1, x2, HEIGHT-y2)


def rect(c, x, top, width, height, ink, radius=0):
    c.setFillColor(color(ink))
    c.roundRect(x, HEIGHT-top-height, width, height, radius, stroke=0, fill=1)


def arrow(c, x1, y, x2, ink):
    line(c, x1, y, x2, y, ink, 1.4)
    direction = 1 if x2 > x1 else -1
    line(c, x2, y, x2-direction*5, y-3, ink, 1.4)
    line(c, x2, y, x2-direction*5, y+3, ink, 1.4)


def winder_icon(c, x, y, ink):
    # Schematic figure-eight winding, not a dimensional drawing of the part.
    c.saveState()
    c.translate(x, HEIGHT-y)
    c.setStrokeColor(color(ink))
    c.setLineWidth(2.4)
    p = c.beginPath()
    p.moveTo(0, 0)
    p.curveTo(-25, 18, -25, -18, 0, 0)
    p.curveTo(25, 18, 25, -18, 0, 0)
    c.drawPath(p, stroke=1)
    c.setStrokeColor(color(PAPER))
    c.setLineWidth(5)
    c.line(-1.5, -4.5, 1.5, 4.5)
    c.setStrokeColor(color(ink))
    c.setLineWidth(3)
    c.line(-1.5, -4.5, 1.5, 4.5)
    c.restoreState()


def deployment(c):
    label(c, "HOW IT WORKS", 36, 538, size=8.5, ink=INK)
    label(c, "Deployment schematic", 576, 539, size=7.3, tracking=0,
          align="right", font="Flyer")
    label(c, "CENTER STAYS LOW AT THE MAST", 306, 557, size=7, tracking=0.35, align="center")
    line(c, 306, 572, 306, 617, MUTED, 1.8)
    line(c, 299, 617, 313, 617, MUTED, 1.4)
    line(c, 46, 619, 566, 619, RULE, 0.7)
    rect(c, 291, 584, 30, 13, ORANGE, 3)
    c.setFillColor(color(PAPER))
    c.circle(306, HEIGHT-590.5, 2.5, stroke=0, fill=1)
    for ink, endpoint, start in [(GREEN, 91, 291), (BLUE, 521, 321)]:
        c.setStrokeColor(color(ink))
        c.setLineWidth(1.6)
        p = c.beginPath()
        p.moveTo(start, HEIGHT-591)
        control = (start + endpoint) / 2
        p.curveTo(control, HEIGHT-611, control, HEIGHT-611, endpoint, HEIGHT-600)
        c.drawPath(p, stroke=1)
        winder_icon(c, endpoint, 599, ink)
    arrow(c, 225, 578, 125, GREEN)
    arrow(c, 387, 578, 487, BLUE)
    label(c, "ONE LEG OUT", 174, 562, size=7.3, ink=GREEN, tracking=0.6, align="center")
    label(c, "THEN THE OTHER", 438, 562, size=7.3, ink=BLUE, tracking=0.6, align="center")


def product(c):
    # The source is a 1600 x 1200 CAD render. A PDF clipping rectangle removes
    # empty margins without modifying or manufacturing product-image pixels.
    image = MODEL / "images/assembled.png"
    source_w, source_h = 1600, 1200
    crop_x, crop_y, crop_w, crop_h = 245, 300, 1115, 730
    x, top, width = 188, 187, 382
    scale = width / crop_w
    height = crop_h * scale
    c.saveState()
    clip = c.beginPath()
    clip.rect(x, HEIGHT-top-height, width, height)
    c.clipPath(clip, stroke=0)
    c.drawImage(str(image), x-crop_x*scale,
                HEIGHT-top-(source_h-crop_y)*scale,
                width=source_w*scale, height=source_h*scale)
    c.restoreState()


def build():
    fonts()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=(WIDTH, HEIGHT), pageCompression=1)
    c.setTitle("Walk it out. Pack it together. | Modular Dipole")
    c.setAuthor("Robert Jackson (N1RWJ)")
    c.setSubject("Why detachable leg winders make sense for portable dipole setups")
    rect(c, 0, 0, WIDTH, HEIGHT, PAPER)
    rect(c, 0, 0, 6, HEIGHT, INK)

    label(c, "N1RWJ / PORTABLE ANTENNA GEAR", 36, 28, size=8.3, tracking=1.1)
    label(c, "MODULAR DIPOLE", 576, 28, size=8.3, tracking=1.1, align="right", ink=INK)
    paragraph(c, "Walk it out.<br/><font color='#D97531'>Pack it together.</font>",
              34, 51, 548, size=43, leading=45, font="FlyerBold", max_height=90)
    paragraph(c, "A dipole center and two winders that travel as one.",
              36, 151, 536, size=12.4, leading=17, ink=MUTED, max_height=17)

    rect(c, 30, 181, 552, 261, "#F8F8F8", 13)
    product(c)
    rect(c, 48, 205, 17, 3, ORANGE)
    label(c, "THE IDEA", 72, 200, size=8, tracking=1, ink=INK)
    paragraph(c, "Three pieces.<br/>One bundle.", 48, 225, 137,
              size=20, leading=24, font="FlyerDemi", max_height=48)
    paragraph(c, "Each leg gets its own winder. Clip both winders to the center for packing.",
              48, 291, 120, size=10.2, leading=14, ink=MUTED, max_height=84)
    label(c, "CURRENT CAD MODEL", 48, 406, size=7.1, tracking=0.7)
    label(c, "Wire coils omitted", 48, 419, size=7.5, tracking=0, font="Flyer")

    label(c, "WHY SPLIT THE WINDERS?", 36, 454, size=8.5, ink=INK)
    paragraph(c, "With a shared center/winder, a whole leg can end up in loose coils before you place it. "
                 "Separate winders let you unwind as you walk, but leave three loose pieces to pack. "
                 "Clip them together for the hike.",
              36, 472, 540, size=11.2, leading=15.5, max_height=46.5)
    deployment(c)

    steps = [
        ("01", "Release", "Support the bundle. Pinch and lift each end of the center in turn. Keep the coil ties closed.", ORANGE),
        ("02", "Walk it out", "Secure the center low. Open one tie and unwind as you walk that leg out. Repeat, then hoist.", GREEN),
        ("03", "Pack it down", "Wind from each tip toward the center in a figure eight. Tie each coil, then pinch each end to reattach the center.", BLUE),
    ]
    for x, (number, title, body, ink) in zip([36, 222, 408], steps):
        rect(c, x, 640, 22, 20, ink, 5)
        label(c, number, x+11, 644, size=9, ink="#FFFFFF", tracking=0,
              align="center", font="FlyerDemi")
        paragraph(c, title, x+30, 639, 142, size=14, leading=20,
                  font="FlyerDemi", max_height=20)
        paragraph(c, body, x, 667, 166, size=9.8, leading=12.7,
                  ink=MUTED, max_height=63.5)
    line(c, 213, 642, 213, 724, RULE, 0.7)
    line(c, 399, 642, 399, 724, RULE, 0.7)

    line(c, 36, 742, 576, 742, RULE, 0.8)
    label(c, "Prototype design. Revised retention, loaded fit and field handling await testing.",
          36, 750, size=7.7, tracking=0, font="Flyer")
    credit_prefix = "N1RWJ  /  K6ARK-derived winder profile  /  "
    license_label = "CC BY-NC-SA 4.0"
    label(c, credit_prefix + license_label, 36, 765,
          size=7.4, tracking=0, font="Flyer")
    license_x = 36 + pdfmetrics.stringWidth(credit_prefix, "Flyer", 7.4)
    c.linkURL("https://creativecommons.org/licenses/by-nc-sa/4.0/",
              (license_x, 17, license_x+pdfmetrics.stringWidth(license_label, "Flyer", 7.4), 29),
              relative=0, thickness=0)
    c.showPage()
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()
