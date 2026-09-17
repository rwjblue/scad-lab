#!/usr/bin/env python3
"""Build a one-page Nesting Dipole flyer from the actual product CAD renders."""
from pathlib import Path
from math import atan2, cos, sin, pi
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader

HERE = Path(__file__).resolve().parent
MODEL = HERE.parent
ROOT = HERE.parents[3]
OUTPUT = ROOT / "output/pdf/nesting-dipole-flyer.pdf"
W, H = 612, 792  # US Letter; also scales comfortably to A4.
PAPER = "#F7F7F7"
INK = "#163E39"
MUTED = "#536661"
ORANGE = "#D4682E"
TEAL = "#268FA7"
GREEN = "#569D70"
RULE = "#D7DFD9"


def register_fonts():
    fonts = Path("/System/Library/Fonts/Supplemental")
    names = {}
    for name, filename, fallback in [
        ("Display", "DIN Alternate Bold.ttf", "Helvetica-Bold"),
        ("Body", "Arial.ttf", "Helvetica"),
        ("Bold", "Arial Bold.ttf", "Helvetica-Bold"),
    ]:
        if (fonts / filename).exists():
            pdfmetrics.registerFont(TTFont(name, str(fonts / filename)))
            names[name] = name
        else:
            names[name] = fallback
    return names


FONT = register_fonts()


def text(c, value, x, y, size=11, font="Body", color=INK, tracking=0):
    c.setFillColor(HexColor(color))
    obj = c.beginText(x, y)
    obj.setFont(FONT[font], size)
    obj.setCharSpace(tracking)
    obj.textOut(value)
    c.drawText(obj)


def paragraph(c, value, x, top, width, size=10.7, leading=14.2, color=MUTED,
              font="Body", max_height=None):
    style = ParagraphStyle("flyer", fontName=FONT[font], fontSize=size,
                           leading=leading, textColor=HexColor(color))
    p = Paragraph(value, style)
    _, height = p.wrap(width, H)
    if max_height is not None:
        assert height <= max_height, (value, height, max_height)
    p.drawOn(c, x, top-height)
    return height


def line(c, x1, y1, x2, y2, color=RULE, width=0.8):
    c.setStrokeColor(HexColor(color))
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)


def arrow(c, x1, y1, x2, y2, color, width=1.8, head=5):
    line(c, x1, y1, x2, y2, color, width)
    angle = atan2(y2-y1, x2-x1)
    path = c.beginPath()
    path.moveTo(x2, y2)
    path.lineTo(x2-head*cos(angle-pi/6), y2-head*sin(angle-pi/6))
    path.lineTo(x2-head*cos(angle+pi/6), y2-head*sin(angle+pi/6))
    path.close()
    c.setFillColor(HexColor(color))
    c.drawPath(path, fill=1, stroke=0)


def cropped_render(c, filename, source_crop, x, y, width, height):
    """Crop only the PDF viewport; leave original CAD raster unchanged."""
    img = ImageReader(str(HERE / filename))
    iw, ih = img.getSize()
    # Crop coordinates use the original 1400 x 1000 preview as a datum.
    left, top, right, bottom = [v*s for v,s in zip(source_crop,
                                                [iw/1400, ih/1000, iw/1400, ih/1000])]
    scale = min(width/(right-left), height/(bottom-top))
    px = x+(width-(right-left)*scale)/2
    py = y+(height-(bottom-top)*scale)/2
    c.saveState()
    clip = c.beginPath()
    clip.rect(x, y, width, height)
    c.clipPath(clip, stroke=0, fill=0)
    c.drawImage(img, px-left*scale, py-(ih-bottom)*scale,
                iw*scale, ih*scale, mask="auto")
    c.restoreState()


def winder_icon(c, x, y, color, scale=1):
    # Schematic winding silhouette; an icon, not a fabrication drawing.
    c.saveState()
    c.translate(x, y)
    c.scale(scale, scale)
    c.setStrokeColor(HexColor(color))
    c.setLineWidth(3)
    c.setLineCap(1)
    p = c.beginPath()
    for a, b in [((-15,-5),(15,-5)), ((-15,-5),(-20,4)),
                 ((15,-5),(20,4)), ((-15,-5),(-20,-13)),
                 ((15,-5),(20,-13))]:
        p.moveTo(*a)
        p.lineTo(*b)
    c.drawPath(p)
    c.restoreState()


def station(c, x, y, color=ORANGE):
    c.setFillColor(HexColor(color))
    c.roundRect(x-8, y-4, 16, 8, 2, fill=1, stroke=0)
    line(c, x, y+6, x, y+36, "#9EB6AC", 1.4)
    line(c, x, y+36, x-12, y+4, "#557A6D", 0.65)
    line(c, x, y+36, x+12, y+4, "#557A6D", 0.65)


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=(W,H), pageCompression=1)
    c.setTitle("Nesting Dipole | Pack together. Deploy separately.")
    c.setAuthor("Robert Jackson (N1RWJ)")
    c.setSubject("Why and how the clip-free three-piece dipole carrier is intended to work")
    c.setFillColor(HexColor(PAPER))
    c.rect(0,0,W,H,stroke=0,fill=1)

    # Top identity: outdoor field gear, with the product name clearly visible.
    winder_icon(c, 47, 753, ORANGE, .52)
    text(c,"N1RWJ  /  FIELD GEAR",67,748,8.5,"Bold",INK,1.1)
    text(c,"NESTING DIPOLE",428,748,10,"Bold",INK,.7)
    line(c,36,733,576,733)

    text(c,"Pack together.",36,683,47,"Display")
    text(c,"Deploy separately.",36,632,47,"Display",ORANGE)
    text(c,"A three-piece dipole carrier for hike-in activations.",38,607,12)

    # Product geometry comes from CAD; its packing pose remains illustrative.
    cropped_render(c,"hero.png",(260,285,1140,805),
                   20,377,391,219)
    text(c,"ONE STUD.",422,562,16,"Display")
    text(c,"ONE HOLE.",422,544,16,"Display")
    paragraph(c,"One stud locates the overlapping spines. The wire stays on opposite sides.",
              422,526,150,10.7,14.5,max_height=60)
    line(c,422,472,576,472)
    paragraph(c,"Slots in the center bar anchor a short rear strap that holds the three pieces together.",
              422,456,150,10.7,14.5,max_height=60)
    text(c,"Separate coils. Compact center. Short rear strap. CAD packing illustration.",
         38,371,7.1,"Body",MUTED)

    # The why, in plain language, without promising measured field results.
    line(c,36,355,576,355)
    text(c,"Why separate the winders?",36,329,21,"Display")
    paragraph(c,
        "A combined center and winder packs neatly, but paying out a leg can be awkward. "
        "Separate winders let you unwind as you walk. Nesting brings the three pieces "
        "back together when it is time to pack.",
        36,316,535,10.8,14.8,max_height=30)

    # A restrained dark instructional panel: deployment is the product benefit.
    c.setFillColor(HexColor(INK))
    c.rect(0,87,W,178,stroke=0,fill=1)
    text(c,"AT THE MAST",36,245,8.3,"Bold","#D8E6DD",1.4)
    text(c,"One leg at a time. Unwind as you walk.",36,220,21,"Display",PAPER)
    station(c,306,176)
    # The left leg is already laid out; only the active right leg is paying out.
    line(c,91,176,298,176,GREEN,2.1)
    c.setFillColor(HexColor(GREEN))
    c.circle(91,176,3,fill=1,stroke=0)
    winder_icon(c,86,146,GREEN,.63)
    line(c,314,176,450,176,TEAL,2.1)
    winder_icon(c,464,180,TEAL,.72)
    arrow(c,496,176,553,176,"#E7A678",2,7)
    text(c,"FIRST LEG LAID OUT",42,123,7.5,"Bold","#B7D3C1",.7)
    text(c,"CENTER AT MAST BASE",232,137,7.4,"Bold","#D8E6DD",.4)
    text(c,"WALK OUT THE NEXT LEG",407,123,7.5,"Bold","#BCE0E9",.6)
    text(c,"Unstrap, lift apart, and walk out each leg. Then hoist the center.",
         36,100,9.4,"Body",PAPER)

    # Pack-down completes the story and says exactly what retains the parts.
    text(c,"WIND. NEST. STRAP. GO.",36,63,14,"Display")
    text(c,"Rewind each leg, join the spines, add the center and fasten the rear strap.",
         36,47,9.1,"Body",MUTED)
    line(c,36,36,576,36)
    text(c,"N1RWJ  /  Clip-free prototype",36,22,7.3,"Bold",MUTED)
    text(c,"K6ARK-derived winder profile  |  CC BY-NC-SA 4.0",350,22,6.8,"Body",MUTED)
    c.linkURL("https://creativecommons.org/licenses/by-nc-sa/4.0/",
              (350,19,576,30),relative=0,thickness=0)
    c.showPage()
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    main()
