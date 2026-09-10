"""Source-derived A5 layout: direct solder, compact BNC shelf, no M3 studs.

uv run --with matplotlib --with shapely --with numpy python layout_a5.py INPUT.stl
"""
from pathlib import Path
import argparse, math, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Polygon as PatchPolygon
from shapely import affinity
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
from analyze_reference import load_stl, measure_arms

parser = argparse.ArgumentParser()
parser.add_argument('source', type=Path)
args = parser.parse_args()
out = Path(__file__).parent
mesh = load_stl(args.source)
arms = measure_arms(mesh)
# Exact rigid transform and reflection. The original long-spine axis is Y=0.
one_side = affinity.affine_transform(mesh['silhouette'], [0, 1, 1, 0, 0, -62.5])
native = unary_union([one_side, affinity.scale(one_side, xfact=-1, yfact=1, origin=(0, 0))])
envelope = Polygon(native.exterior)
# Fill only the upper head/arm openings for the new holes. Preserve native exterior.
body = unary_union([native, envelope.intersection(box(-40, 25, 40, 75))])
angle = arms['right']['sweep_from_perpendicular_deg']
c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
pitch = 7.0
right = [(20+pitch*i*c, 53.56064+3*s/c+pitch*i*s) for i in range(3)]
eye = (0.0, 63.0)
rear_projection, target_contact = 12.0, right[0][1]
shelf_top = target_contact-rear_projection
plate_t, bnc_axis_z, shelf_depth = 5.0, 15.0, 24.0
hardware_radius = 9.0  # Existing dipole_center's reserved envelope, not a measured OD.
hardware_to_plate = bnc_axis_z-hardware_radius-plate_t
ligaments = [Point(p).distance(envelope.boundary)-2.1 for p in right]
assert all(abs(a-b)<1e-6 for a,b in zip(envelope.bounds, [-37.5,-70,37.5,70]))
assert envelope.symmetric_difference(Polygon(body.exterior)).area < 1e-7
assert hardware_to_plate >= 1
for p in right:
    assert body.covers(Point(p).buffer(2.1))
assert body.covers(Point(eye).buffer(3))
assert all(abs(math.dist(a,b)-pitch)<1e-8 for a,b in zip(right, right[1:]))
assert target_contact >= right[0][1]
data = {
    'source_path':str(args.source.resolve()), 'source_sha256':mesh['sha256'],
    'transform':'new_x=source_y, new_y=source_x-62.5; union with reflection new_x=-new_x',
    'scale_factor':1, 'frame_extent_mm':[75,140,5], 'horns_relocated':False,
    'original_outer_boundary_preserved':True, 'filled_region':'upper native openings at new_y>=25',
    'eye_center_mm':eye, 'eye_bore_mm':6, 'right_relief_centers_mm':right,
    'left_relief_centers_mm':[(-x,y) for x,y in right],
    'termination':'direct solder to BNC center cup and shell tag',
    'stud_centers_mm':[],
    'wire_bore_mm':3.2, 'chamfer_mm':0.5, 'chamfer_mouth_mm':4.2,
    'relief_pitch_mm':pitch, 'inter_chamfer_web_mm':pitch-4.2,
    'relief_outer_ligaments_mm':ligaments,
    'bnc_shelf_top_y_mm':shelf_top, 'bnc_shelf_thickness_mm':3,
    'bnc_rear_projection_assumed_mm':rear_projection,
    'bnc_contact_target_y_mm':target_contact,
    'bnc_shelf_relation':'shelf_top_y = target_contact_y - measured_rear_projection',
    'bnc_axis_z_proposed_mm':bnc_axis_z, 'shelf_depth_proposed_mm':shelf_depth,
    'bnc_axis_to_front_plate_face_mm':bnc_axis_z-plate_t,
    'bnc_hardware_keepout_diameter_mm':2*hardware_radius,
    'bnc_hardware_keepout_to_front_plate_mm':hardware_to_plate,
    'bnc_barrel_diameter_for_clearance_mm':12.7,
    'bnc_barrel_to_front_plate_mm':bnc_axis_z-12.7/2-plate_t,
    'bnc_axis_reduction_from_a4_mm':21-bnc_axis_z,
    'shelf_depth_reduction_from_a4_mm':30-shelf_depth,
    'connector_status':'12 mm rear projection estimated from reference drawing, not directly dimensioned; verify actual part and hardware before CAD fit signoff',
    'strain_relief_status':'Geometry fits; grip must be checked with actual wire. 7 mm pitch is not a tested load rating.'
}
(out/'layout-a5.json').write_text(json.dumps(data,indent=2)+'\n')

PAPER, INK, ORANGE, BLUE = '#faf8f3','#26353b','#d87640','#247f91'
fig=plt.figure(figsize=(15,10),facecolor=PAPER)
gs=fig.add_gridspec(2,2,width_ratios=[.92,1.12],height_ratios=[1,.9],left=.05,right=.97,top=.86,bottom=.1,wspace=.18,hspace=.28)
main=fig.add_subplot(gs[:,0]); zoom=fig.add_subplot(gs[0,1]); side=fig.add_subplot(gs[1,1])
for a in [main,zoom,side]:a.set_facecolor(PAPER);a.axis('off')
fig.text(.05,.945,'A5 / DIRECT-SOLDER DIPOLE WINDER',fontsize=24,weight='bold',color=INK)
fig.text(.05,.902,'Original mirrored footprint • 7 mm relief-hole pitch • BNC brought 6 mm closer to the frame',fontsize=12,color=INK)

def frame(ax):
    x,y=body.exterior.xy;ax.fill(x,y,color=ORANGE,zorder=1)
    for h in body.interiors:
        x,y=h.xy;ax.fill(x,y,color=PAPER,zorder=2)
    x,y=envelope.exterior.xy;ax.plot(x,y,color=INK,lw=.7,zorder=3)
    ax.add_patch(Circle(eye,3,fc=PAPER,ec=INK,lw=.9,zorder=5))
    for sign in [-1,1]:
        for x,y in right:
            ax.add_patch(Circle((sign*x,y),2.1,fc='#f4ba90',ec=INK,lw=.7,zorder=4))
            ax.add_patch(Circle((sign*x,y),1.6,fc=PAPER,ec=INK,lw=.7,zorder=5))

frame(main)
# Front-view connector envelope. Specific rear projection is a fit assumption.
main.add_patch(Rectangle((-6.35,shelf_top-14.9),12.7,11.9,fc='#c9cecf',ec=INK,lw=.8,zorder=6))
main.add_patch(Rectangle((-4.85,shelf_top),9.7,7,fc='#c9cecf',ec=INK,lw=.8,zorder=6))
main.add_patch(Rectangle((-1,shelf_top+7),2,5,fc='#c9cecf',ec=INK,lw=.8,zorder=6))
main.add_patch(Rectangle((-13,shelf_top-3),26,3,fc='#b95829',ec=INK,lw=.8,zorder=7))
main.plot([-6.35,6.35],[shelf_top-10.5]*2,color=INK,lw=.6,zorder=7)
main.annotate('',(-46,-70),(-46,70),arrowprops=dict(arrowstyle='<->',color=BLUE))
main.text(-49,0,'140 mm — unchanged',rotation=90,ha='right',va='center',fontsize=11,color=BLUE)
main.annotate('',(-37.5,-80),(37.5,-80),arrowprops=dict(arrowstyle='<->',color=BLUE))
main.text(0,-85,'75 mm mirrored width',ha='center',fontsize=11,color=BLUE)
main.text(0,-94,'5 mm source thickness; 3 mm BNC mounting panel.',ha='center',fontsize=10,color=INK)
main.set(xlim=(-58,51),ylim=(-100,78),aspect='equal')

frame(zoom)
zoom.plot([0,22],[target_contact]*2,color=BLUE,lw=1,ls='--',zorder=8)
zoom.add_patch(Rectangle((-4.85,shelf_top),9.7,7,fc='none',ec=BLUE,lw=.8,ls='--',zorder=6))
zoom.add_patch(Rectangle((-1,shelf_top+7),2,5,fc='none',ec=BLUE,lw=.8,ls='--',zorder=6))
zoom.add_patch(Rectangle((-13,shelf_top-3),26,3,fc='#b95829',ec=INK,lw=.8,zorder=7))
zoom.annotate('Rear contact at inner relief level', (0,target_contact),(-15,76),fontsize=10,color=BLUE,
              arrowprops=dict(arrowstyle='-',color=BLUE,lw=.8))
zoom.text(-15,83,'UPPER HEAD — ORIGINAL ARM LOCATIONS',fontsize=13,weight='bold',color=INK)
zoom.annotate('7 mm pitch',right[1],(25,72),fontsize=10,color=INK,
              arrowprops=dict(arrowstyle='-',color=INK,lw=.8))
zoom.annotate('Direct solder to BNC\ncenter cup + shell tag', (0,target_contact-1),(18,33),fontsize=10,color=INK,
              arrowprops=dict(arrowstyle='-',color=INK,lw=.8))
zoom.set(xlim=(-17,40),ylim=(25,86),aspect='equal')

side.text(-3,77,'SIDE VIEW / COMPACT BNC SHELF',fontsize=13,weight='bold',color=INK)
side.add_patch(Rectangle((0,24),5,46,fc=ORANGE,ec=INK,lw=.8))
side.add_patch(Rectangle((0,shelf_top-3),shelf_depth,3,fc=ORANGE,ec=INK,lw=.8))
# Projected flanking ribs sit beside the connector, outside the reserved Ø18 space.
side.add_patch(PatchPolygon([[5,shelf_top-3],[15,shelf_top-3],[5,shelf_top-13]],closed=True,fc='#bd5f2e',alpha=.3,ec=INK,lw=.7,ls='--'))
side.add_patch(Rectangle((bnc_axis_z-6.35,shelf_top-14.9),12.7,11.9,fc='#c9cecf',ec=INK,lw=.8))
side.add_patch(Rectangle((bnc_axis_z-4.85,shelf_top),9.7,7,fc='#c9cecf',ec=INK,lw=.8))
side.add_patch(Rectangle((bnc_axis_z-1,shelf_top+7),2,5,fc='#c9cecf',ec=INK,lw=.8))
side.add_patch(Rectangle((bnc_axis_z-hardware_radius,shelf_top+.2),2*hardware_radius,3,fc='none',ec=BLUE,lw=1,ls='--'))
side.plot([bnc_axis_z,bnc_axis_z],[23,58],color=BLUE,ls=':',lw=.8)
side.plot([5,24],[target_contact]*2,color=BLUE,ls='--',lw=.8)
side.annotate('Contact height retained\nShelf top at y≈43', (bnc_axis_z,target_contact),(31,63),fontsize=10,color=INK,
              arrowprops=dict(arrowstyle='-',color=INK,lw=.8))
side.annotate('Ø18 hardware allowance\n1 mm clear of frame', (6,shelf_top+2),(31,47),fontsize=10,color=BLUE,
              arrowprops=dict(arrowstyle='-',color=BLUE,lw=.8))
side.annotate('Ribs beside the BNC', (6,shelf_top-10),(31,30),fontsize=9,color=INK,
              arrowprops=dict(arrowstyle='-',color=INK,lw=.8))
side.annotate('',(5,20),(bnc_axis_z,20),arrowprops=dict(arrowstyle='<->',color=BLUE))
side.text(0,15,'Axis 10 mm from frame face; shelf depth 24 mm overall.',fontsize=10,color=INK)
side.set(xlim=(-3,82),ylim=(12,80),aspect='equal')
fig.text(.05,.057,'Relief: Ø3.2 bores, 0.5 mm chamfers on both faces, 7 mm pitch. Weave each leg, then leave a slack tail to the BNC.',fontsize=11,color=INK)
fig.text(.05,.027,'Source outline at 1:1. Connector schematic; 12 mm rear projection remains estimated. Check actual hardware fit and wire grip.',fontsize=10,color=INK)
for ext in ['png','svg']:fig.savefig(out/f'layout-a5.{ext}',dpi=180,facecolor=PAPER)
print(json.dumps({k:data[k] for k in ['frame_extent_mm','original_outer_boundary_preserved','right_relief_centers_mm','stud_centers_mm','bnc_axis_z_proposed_mm','shelf_depth_proposed_mm','bnc_hardware_keepout_to_front_plate_mm','relief_outer_ligaments_mm']},indent=2))
