#!/usr/bin/env python3
"""Regenerate the labeled release drawing from actual OpenSCAD projections.

python models/ham_radio/modular_dipole/review/generate_explainer.py

Add --png on macOS to render a PNG with Quick Look and ImageMagick.

Requires OpenSCAD. No raster tracing, downloaded image, or third-party Python
package is used. The side-view sequence is explicitly schematic.
"""
from concurrent.futures import ThreadPoolExecutor
import argparse
import hashlib
from html import escape
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
MODEL = HERE.parent
CAD = MODEL / "modular_dipole.scad"
MOCKUP = MODEL / "mockups.scad"
HARDWARE = MODEL / "hardware_mockups.scad"
OUTPUT = MODEL / "images/release_explainer.svg"
W, H = 1600, 1300

EXPRESSIONS = {
    "center": "projection(cut=false) placed_center();",
    "upper": "projection(cut=false) intersection() { placed_winder(1); translate([-200,-200,-0.1]) cube([400,400,5.2]); }",
    "lower": "projection(cut=false) intersection() { placed_winder(-1); translate([-200,-200,-0.1]) cube([400,400,5.2]); }",
    "upper_heads": "projection(cut=false) intersection() { placed_winder(1); translate([-200,-200,17.01]) cube([400,400,5]); }",
    "lower_heads": "projection(cut=false) intersection() { placed_winder(-1); translate([-200,-200,17.01]) cube([400,400,5]); }",
    "hardware": "projection(cut=false) hardware();",
    "ties": "projection(cut=false) for(r=[-1,1]) winder_strap(r);",
}


def project(task):
    name, expression = task
    with tempfile.TemporaryDirectory(prefix=f"pinch-outline-{name}-") as directory:
        source = Path(directory) / "view.scad"
        output = Path(directory) / "view.svg"
        source.write_text(f"use <{CAD}>\nuse <{MOCKUP}>\nuse <{HARDWARE}>\n"
                          '$fn=96;\npreset="40m";\n' + expression + "\n")
        command = ["openscad", "--backend=Manifold", "--hardwarnings", "-o", str(output), str(source)]
        result = subprocess.run(command, text=True, capture_output=True)
        if result.returncode or "WARNING:" in result.stderr or "ERROR:" in result.stderr:
            raise RuntimeError(result.stdout + result.stderr)
        root = ET.fromstring(output.read_text())
        return name, [p.attrib["d"] for p in root.iter() if p.tag.endswith("}path")]


def text(x, y, content, size=22, color="#203642", weight=400, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
            f'font-weight="{weight}" text-anchor="{anchor}" {extra}>{escape(content)}</text>')


def line(x1, y1, x2, y2, color="#8497a1", width=2, extra=""):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" {extra}/>'


def side_card(x, number, title, mode):
    top, width = 959, 448
    o = [f'<g transform="translate({x} {top})">',
         '<rect width="448" height="248" rx="18" fill="#fff" stroke="#dce6ea"/>',
         '<circle cx="30" cy="32" r="15" fill="#e9f1f4"/>',
         text(30, 38, str(number), 18, weight=700, anchor="middle"),
         text(56, 39, title, 22, weight=650)]
    # Two rows of winders overlap in this schematic side view.
    o += ['<rect x="64" y="171" width="320" height="14" rx="6" fill="#4f8b72"/>',
          '<rect x="70" y="184" width="308" height="6" rx="3" fill="#d0ded7"/>']
    for sx in (125, 323):
        o += [f'<rect x="{sx-5}" y="118" width="10" height="55" fill="#4f8b72"/>',
              f'<rect x="{sx-12}" y="111" width="24" height="8" rx="1" fill="#4f8b72"/>']
    # The parked end rests on the head TOP; the locked end remains lower.
    bottom_left, bottom_right = (136, 111) if mode == "park" else (111, 111) if mode == "level" else (83, 83)
    slope = (bottom_right-bottom_left) / (323-125)
    xa, xb = 99, 349
    ya, yb = bottom_left+(xa-125)*slope, bottom_left+(xb-125)*slope
    o += [f'<path d="M {xa},{ya-11} L {xb},{yb-11} L {xb},{yb} L {xa},{ya} Z" fill="#cb7637" stroke="#ad5e2b" stroke-width="1.5"/>']
    if mode == "park":
        o += [line(342, 150, 342, 121, "#b8423a", 3, 'marker-end="url(#arrow-red)"'),
              '<circle cx="323" cy="111" r="17" fill="none" stroke="#188075" stroke-width="2" stroke-dasharray="3 3"/>',
              text(224, 219, "Let the teeth rest on the head tops.", 17, "#546975", anchor="middle")]
    elif mode == "level":
        o += [line(107, 155, 107, 122, "#426bb2", 3, 'marker-end="url(#arrow-blue)"'),
              line(99, 111, 349, 111, "#a9babf", 1.5, 'stroke-dasharray="4 5"'),
              text(224, 219, "Raise the other end until level.", 17, "#546975", anchor="middle")]
    else:
        o += [line(99, 111, 349, 111, "#a9babf", 1.5, 'stroke-dasharray="4 5"')]
        for sx in (125, 323):
            o += [line(sx, 103, sx, 89, "#188075", 3, 'marker-end="url(#arrow-teal)"')]
        o += [text(224, 219, "Keep it level and lift straight clear.", 17, "#546975", anchor="middle")]
    return "\n".join(o + ["</g>"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--png", action="store_true")
    args = parser.parse_args()
    with ThreadPoolExecutor(max_workers=3) as pool:
        outlines = dict(pool.map(project, EXPRESSIONS.items()))
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         '<title>Modular dipole — sequential end pinches and fixed lifting bridges</title>',
         '<desc>The top view uses actual OpenSCAD-projected part outlines. Two inward arrows identify each upper/lower pinch pair. A schematic side view shows parking the first end, leveling the second, and lifting clear. Hardware and silicone ties are layout proxies.</desc>',
         '<metadata>' + escape("CAD SHA256 " + hashlib.sha256(CAD.read_bytes()).hexdigest()
            + "; Winder geometry derives from K6ARK UL Wireframe Winder by Adam Kimmerly (K6ARK). "
            + "See models/ham_radio/modular_dipole/NOTICE.md for source and CC BY-NC-SA 4.0 terms.") + '</metadata>',
         '<defs>']
    for name, color in (("red", "#b8423a"), ("blue", "#426bb2"), ("teal", "#188075")):
        s += [f'<marker id="arrow-{name}" markerWidth="8" markerHeight="8" refX="6.7" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L7,3 L0,6 Z" fill="{color}"/></marker>']
    s += ['</defs>', '<g font-family="Arial, Helvetica, sans-serif">',
          f'<rect width="{W}" height="{H}" fill="#f3f6f7"/>',
          text(64, 54, "MODULAR DIPOLE  /  RELEASE SEQUENCE", 17, "#627985", 650, extra='letter-spacing="2"'),
          text(64, 111, "Pinch one end. Then the other.", 42, "#172f3a", 700),
          text(64, 147, "Intended one-hand sequence · both coil ties stay closed", 23, "#546c78"),
          '<rect x="64" y="178" width="1472" height="699" rx="24" fill="#fff" stroke="#dce6ea"/>',
          text(96, 217, "TOP VIEW", 16, "#708691", 700, extra='letter-spacing="1.4"')]
    # OpenSCAD's SVG already flips world Y: suspension eye is up, BNC down.
    cx, cy, scale = 800, 523, 4.35
    s += [f'<g transform="translate({cx} {cy}) scale({scale})">']
    for name, fill, stroke in (("upper", "#28758a", "#155d70"), ("lower", "#5a9278", "#397157"),
                               ("ties", "#303c43", "#303c43"), ("center", "#cb7637", "#a45a2d"),
                               ("upper_heads", "#28758a", "#155d70"), ("lower_heads", "#5a9278", "#397157"),
                               ("hardware", "#8b969c", "#69767e")):
        for path in outlines[name]:
            s += [f'<path d="{escape(path)}" fill="{fill}" fill-rule="evenodd" stroke="{stroke}" stroke-width="0.23" stroke-linejoin="round"/>']
    s += ['</g>']
    # Identify both moving pairs, using arrows outside their contact faces.
    for end, color, marker in ((1, "#b8423a", "red"), (-1, "#426bb2", "blue")):
        ax = cx + end*46*scale
        for row in (-1, 1):
            ya, yb = cy-row*29*scale, cy-row*19*scale
            s += [line(ax, ya, ax, yb, "#fff", 10, 'stroke-linecap="round"'),
                  line(ax, ya, ax, yb, color, 4.5, f'marker-end="url(#arrow-{marker})" stroke-linecap="round"')]
        # A teal outline calls out the fixed bridge separately from the pads.
        bx = cx + (48 if end > 0 else -52)*scale
        s += [f'<rect x="{bx-2}" y="{cy-8.4*scale-2}" width="{4*scale+4}" height="{16.8*scale+4}" rx="4" fill="none" stroke="#188075" stroke-width="2.5"/>']
    s += [text(1170, 404, "1  RIGHT END", 25, "#b8423a", 700),
          text(1170, 440, "Pinch the two paddles", 22),
          text(1170, 470, "toward each other.", 22),
          '<path d="M1150,430 L1108,430 L1030,450" fill="none" stroke="#b8423a" stroke-width="2"/>',
          text(1170, 561, "LIFT HERE", 17, "#188075", 700, extra='letter-spacing="1"'),
          text(1170, 591, "Fixed lifting bridge", 22, "#203642", 650),
          '<path d="M1150,570 L1100,570 L1029,525" fill="none" stroke="#188075" stroke-width="2"/>',
          text(126, 404, "2  LEFT END", 25, "#426bb2", 700),
          text(126, 440, "Repeat this pinch.", 22),
          text(126, 470, "Lift this end to level.", 22),
          '<path d="M402,430 L464,430 L570,450" fill="none" stroke="#426bb2" stroke-width="2"/>',
          text(126, 561, "MATCHING BRIDGE", 17, "#188075", 700, extra='letter-spacing="1"'),
          text(126, 591, "Lift fixed plastic.", 22, "#203642", 650),
          '<path d="M398,570 L466,570 L570,525" fill="none" stroke="#188075" stroke-width="2"/>',
          text(850, 377, "Hoist eye", 16, "#627985"),
          '<path d="M848,386 L835,428 L819,467" fill="none" stroke="#94a5ae" stroke-width="1.3"/>',
          text(850, 671, "BNC", 16, "#627985", 700),
          line(840, 665, 818, 655, "#94a5ae", 1.3),
          text(800, 838, "Silicone ties stay closed until the winders are in hand.", 21, "#425d69", 500, "middle"),
          text(96, 908, "SIDE VIEW", 16, "#708691", 700, extra='letter-spacing="1.4"'),
          text(225, 908, "Sequence schematic · motion exaggerated", 17, "#708691")]
    s += [side_card(64, 1, "Park the first end", "park"),
          side_card(576, 2, "Bring the carrier level", "level"),
          side_card(1088, 3, "Lift clear", "clear"),
          text(64, 1250, "Top outlines: current printable CAD. Hardware and ties: layout proxies. Physical one-hand use still needs the first-print test.", 17, "#627985"),
          '</g></svg>']
    OUTPUT.write_text("\n".join(s) + "\n")
    ET.parse(OUTPUT)
    print(OUTPUT)
    if args.png:
        # Quick Look fits SVG thumbnails to a square. Use a square viewport,
        # then crop its blank lower margin without resampling the vector render.
        with tempfile.TemporaryDirectory(prefix="pinch-explainer-render-") as directory:
            source = Path(directory) / "view.svg"
            source.write_text(OUTPUT.read_text().replace(
                f'height="{H}" viewBox="0 0 {W} {H}"',
                f'height="{W}" viewBox="0 0 {W} {W}"', 1))
            subprocess.run(["qlmanage", "-t", "-s", str(W), "-o", directory, str(source)],
                           check=True, capture_output=True)
            png = OUTPUT.with_suffix(".png")
            subprocess.run(["magick", str(source)+".png", "-crop", f"{W}x{H}+0+0", "+repage", str(png)],
                           check=True, capture_output=True)
            print(png)


if __name__ == "__main__":
    main()
