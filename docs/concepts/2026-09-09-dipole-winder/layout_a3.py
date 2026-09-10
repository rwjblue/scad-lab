"""Draw the proposed A3 layout; this is a dimensional study, not printable CAD.

Run with: uv run --with matplotlib --with shapely --with numpy python layout_a3.py
"""
from pathlib import Path
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
from shapely.geometry import Point, LineString, box
from shapely.ops import unary_union

OUT = Path(__file__).parent
ANGLE = 26.41449
C, S = math.cos(math.radians(ANGLE)), math.sin(math.radians(ANGLE))
UPPER_Y, LOWER_Y, EYE_Y, SHELF_Y = 31.0, -42.0, 72.0, 27.0
STUD_X, ARM_TIP_X, ARM_R = 15.0, 52.3, 7.3
STUD_T = STUD_X / C
STUD_Y = UPPER_Y + STUD_T * S
WIRE_OFFSETS = [18.0, 23.5, 29.0]
ORANGE, INK, PAPER, BLUE = '#d87640', '#26353b', '#faf8f3', '#237e92'

parts = [LineString([(0, LOWER_Y), (0, EYE_Y)]).buffer(6),
         Point(0, EYE_Y).buffer(8.5), box(-13, 17, 13, 34)]
for side in [-1, 1]:
    for root_y, vertical in [(UPPER_Y, 1), (LOWER_Y, -1)]:
        parts.append(LineString([(0, root_y),
            (side * ARM_TIP_X, root_y + vertical * ARM_TIP_X * S / C)]).buffer(ARM_R))
body = unary_union(parts)

fig = plt.figure(figsize=(15, 10), facecolor=PAPER)
gs = fig.add_gridspec(2, 2, width_ratios=[1.1, 1], height_ratios=[1, .9],
                     left=.055, right=.97, top=.86, bottom=.08, wspace=.2, hspace=.28)
ax = fig.add_subplot(gs[:, 0]); detail = fig.add_subplot(gs[0, 1]); notes = fig.add_subplot(gs[1, 1])
for a in [ax, detail, notes]:
    a.set_facecolor(PAPER)
    a.axis('off')
fig.text(.055, .945, 'A3 / STRAIGHT ARMS + OPTIONAL STUDS', fontsize=24, weight='bold', color=INK)
fig.text(.055, .902, 'Dimensioned concept • front view • all dimensions in millimetres', fontsize=13, color=INK)
x, y = body.exterior.xy; ax.fill(x, y, color=ORANGE, zorder=1)
ax.add_patch(Circle((0, EYE_Y), 3, facecolor=PAPER, edgecolor=INK, lw=1.1, zorder=3))
for side in [-1, 1]:
    ax.add_patch(Circle((side * STUD_X, STUD_Y), 1.7, fc=PAPER, ec=INK, lw=1.2, zorder=4))
    for d in WIRE_OFFSETS:
        pos = (side * (STUD_X + C*d), STUD_Y + S*d)
        ax.add_patch(Circle(pos, 2.1, fc='#f2b88a', ec=INK, lw=.65, zorder=3))
        ax.add_patch(Circle(pos, 1.6, fc=PAPER, ec=INK, lw=.65, zorder=4))
# BNC and shelf are front-view envelopes, not a model of the manufacturer part.
ax.add_patch(Rectangle((-5, SHELF_Y), 10, 8, fc='#bbbfc0', ec=INK, lw=.8, zorder=4))
ax.add_patch(Rectangle((-7, SHELF_Y-20), 14, 20, fc='#d2d5d6', ec=INK, lw=.8, zorder=4))
ax.add_patch(Rectangle((-13, SHELF_Y-3), 26, 3, fc='#b85324', ec=INK, lw=.8, zorder=5))
ax.plot([-7, 7], [SHELF_Y-13]*2, color=INK, lw=.6, zorder=5)
ax.text(0, SHELF_Y-10, 'BNC', fontsize=8, ha='center', va='center', zorder=6, color=INK)
ax.annotate('', xy=(19, EYE_Y), xytext=(19, SHELF_Y), arrowprops=dict(arrowstyle='<->', color=BLUE, lw=1.2))
ax.plot([3, 21], [EYE_Y]*2, color=BLUE, lw=.7)
ax.plot([13, 21], [SHELF_Y]*2, color=BLUE, lw=.7)
ax.text(22, 63, '45 mm\neye center\nto shelf top', fontsize=10, color=BLUE, va='center')
ax.annotate('6 mm suspension hole', (0, EYE_Y), (-61, 82), fontsize=10, color=INK,
            arrowprops=dict(arrowstyle='-', color=INK, lw=.8))
ax.annotate('Optional M3 holes', (-STUD_X, STUD_Y), (-62, 18), fontsize=10, color=INK,
            arrowprops=dict(arrowstyle='-', color=INK, lw=.8))
ax.annotate('BNC envelope only', (0, SHELF_Y-18), (16, -7), fontsize=9, color=INK,
            arrowprops=dict(arrowstyle='-', color=INK, lw=.8))
ax.plot([0, 46], [LOWER_Y]*2, color=BLUE, lw=.8, ls='--')
ax.add_patch(Arc((0, LOWER_Y), 57, 57, theta1=-ANGLE, theta2=0, color=BLUE, lw=1.2))
ax.text(29, -49, '26.4°', fontsize=12, color=BLUE, weight='bold')
ax.text(0, -85, 'Four straight arms; same outward sweep on each.\nOpen sides and smooth, unslotted tips.', fontsize=10,
        ha='center', va='top', color=INK)
ax.set(xlim=(-68, 68), ylim=(-95, 92), aspect='equal')

detail.text(-5, 20, 'UPPER-ARM HOLE ROW', fontsize=14, weight='bold', color=INK)
detail.text(-5, 16, 'Shown horizontal for clarity; follows the arm at 26.4°.', fontsize=10, color=INK)
detail.add_patch(Rectangle((-5, -5), 41, 10, fc=ORANGE, ec='none', zorder=1))
detail.add_patch(Circle((0, 0), 1.7, fc=PAPER, ec=INK, zorder=4))
for d in WIRE_OFFSETS:
    detail.add_patch(Circle((d, 0), 2.1, fc='#f2b88a', ec=INK, lw=.8, zorder=3))
    detail.add_patch(Circle((d, 0), 1.6, fc=PAPER, ec=INK, lw=.8, zorder=4))
detail.plot([0, 0], [3, 12], color=INK, lw=.7)
detail.plot([18, 18], [3, 12], color=INK, lw=.7)
detail.annotate('', (0, 10), (18, 10), arrowprops=dict(arrowstyle='<->', color=INK))
detail.text(9, 11, '18 mm center to center', fontsize=10, ha='center', color=INK)
detail.annotate('', (23.5, 8), (29, 8), arrowprops=dict(arrowstyle='<->', color=BLUE))
detail.text(26.25, 10, '5.5 pitch', fontsize=9, ha='center', color=BLUE)
detail.annotate('', (1.7, -8), (15.9, -8), arrowprops=dict(arrowstyle='<->', color=BLUE))
detail.text(8.8, -12, '14.2 mm clear at face', fontsize=10, ha='center', color=BLUE)
detail.text(-1, -19, 'Ø3.4\nM3 clearance', fontsize=10, ha='center', color=INK)
detail.text(24, -19, '3 × Ø3.2 bores\nØ4.2 chamfer mouths', fontsize=10, ha='center', color=INK)
detail.set(xlim=(-6, 37), ylim=(-25, 24), aspect='equal')
notes.text(0, 1, 'DETAILS TO CARRY INTO SCAD', fontsize=14, weight='bold', color=INK, va='top')
lines = [
    '0.5 mm × 45° chamfers on both wire-hole faces.',
    '1.3 mm material between adjacent chamfer mouths.',
    '18 mm stud-to-relief spacing matches dipole_center.',
    '4.72 mm gap after the longest owned terminal barrel.',
    '3 mm BNC shelf; 4 mm proposed main plate.',
    'Studs can be omitted for direct solder connections.',
    'Closed relief holes retain already-crimped ring terminals.',
    'Final wire routing, capacity and hardware fit still need checking.',
]
for i, text in enumerate(lines):
    notes.text(0, .84-i*.105, text, fontsize=11, color=INK, va='top')
notes.set(xlim=(0, 1), ylim=(0, 1))
fig.text(.055, .033, 'Arm angle measured from supplied K6ARK meshes; other dimensions are proposed. BNC symbol is not dimensionally complete.',
         fontsize=10, color=INK)
for ext in ['png', 'svg']:
    fig.savefig(OUT / f'layout-a3.{ext}', dpi=180, facecolor=PAPER)
print({'angle_deg': ANGLE, 'stud_centers': [[-STUD_X, STUD_Y], [STUD_X, STUD_Y]],
       'right_wire_centers': [[STUD_X+C*d, STUD_Y+S*d] for d in WIRE_OFFSETS],
       'eye_to_shelf_mm': EYE_Y-SHELF_Y, 'outline_bounds': body.bounds,
       'stud_to_chamfer_clear_mm':18-1.7-2.1})
