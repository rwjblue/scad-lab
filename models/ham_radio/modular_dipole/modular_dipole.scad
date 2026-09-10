/*
  N1RWJ modular dipole — FOUR true snap studs, two per identical winder.
  Retention revision 2, 2026-09-10. The first print had comfortable springs
  but failed retention. Larger heads and redistributed flexure sections
  increase engagement with only 0.15 mm more travel at each paddle.
  The right upper/lower paddles pinch together to
  release both RIGHT studs; the left pair does the same on the LEFT.
  Broad flat head tops are intended as a parked-open support after peeling
  one carrier end upward. Compact standoffs preserve the dry snap mechanism;
  reduced loaded wire/tie/finger clearance needs a physical fit check.
  Print fit, release force, glove use and fatigue still need physical trials.
  Docking requires pinching: the flat parking tops deliberately lack an
  automatic push-in funnel. See review/DESIGN.md for the tradeoff.
  Units mm. Broad backs print down. Flat head undersides overhang 1.5 mm:
  print the independent-stud retention coupon before full winders. No fatigue rating.
*/
use <winder_profile.scad>
use <../dipole_winder/frame_bevel.scad>
use <../dipole_center/dipole_center.scad>

/* [Output] */
part="print_layout"; // [center,winder,assembled,print_layout,exploded,coupon,fit_coupon,retention_coupon,released,peel,parked,wire_envelopes]
preset="40m"; // [40m,80m]
show_wire=false;

/* [Winder size] */
// Reach from the winding datum to the horn tips; stock size is 37.5 mm.
wing_length=37.5; // [37.5:0.5:60]
// Distance between the lower outer tips; longer horns can project beyond this.
winding_span=140; // [140:1:200]

/* [Wire space] */
// Coil buildup on EACH face. Zero selects the preset: 5 mm for 40m, 8 for 80m.
wire_face_bulge=0; // [0:Preset,2:2 mm,3:3 mm,4:4 mm,5:5 mm,6:6 mm,7:7 mm,8:8 mm,9:9 mm,10:10 mm,11:11 mm,12:12 mm]
// Wire overhang around the frame edge; affects the displayed clearance reserve.
wire_edge_bulge=5; // [2:0.5:5]
/* [Packed height] */
// Gap in millimeters from the winder's top face to the center's underside.
// Independent of the wire-space preset and coil buildup; check loaded fit.
standoff=4; // [2.5:0.5:25]

/* [Center holes] */
// Centerline to the innermost hole in each three-hole strain-relief group.
wire_hole_inner_x=28; // [27:0.1:30]
// Center-to-center pitch within each group. Hole size and edge guards also apply.
wire_hole_pitch=5.5; // [4:0.1:6.5]
wire_hole_d=3.2; // [2.6:0.1:3.6]
// Entry chamfer on the wire holes and hoist eye; larger mouths need more spacing.
wire_chamfer=0.5; // [0:0.1:0.6]
terminal_hole_d=3.4; // [3.1:0.1:3.6]
hang_hole_d=6; // [4:0.5:6]

/* [BNC fit] */
// Finished cutout diameter. Anti-rotation flat depth remains 0.85 mm.
bnc_hole_d=10.1; // [9.7:0.05:10.2]

/* [Hidden] */
// Mechanism invariants: edit only with fresh motion/retention validation.
pose_angle=5.5;
park_angle=4.7;
bnc_clearance=(bnc_hole_d-9.7)/2;
face_bulge=wire_face_bulge==0 ? (preset=="80m" ? 8 : 5) : wire_face_bulge;
wire_positions=[for(i=[0:2]) wire_hole_inner_x+i*wire_hole_pitch];
winder_bounds=winder_profile_bounds(wing_length,winding_span);
layout_height_delta=(winder_bounds[1][1]-winder_bounds[0][1])-54.043564;
snap_head_d=7.0;
snap_top_d=6.8; // Broad FLAT top supports a released, returned tongue
snap_throat_clearance=0.30;
snap_throat_x_extra=0.15; // Extra X-only tilt/yaw allowance; Y flat is unchanged
snap_flat_extra=0.05; // Small yaw allowance for the rigid head's flat corners
snap_neck_clearance=0.20;
neck_notch_x_extra=0.80; // Wider X sweep clears tilted heads; preserve inner Y edge
snap_release=3.30; // Actual travel at the OUTER paddle edge, not at the catch
snap_stop=3.50;
finger_x=51; // Load location; 41..51 spans the usable paddle
beam_t=1.50;
beam_inner_reinforcement=1.20;
axial_gap=0.80;

$fn=96;
eps=0.02;
frame_t=5;
frame_bevel=0.5;
center_plate_t=4;
paddle_height=10; // Raised finger face; compact-height wire clearance is a fit test
paddle_inset=0.1; // Raised face sits inside base; avoids coincident side facets
center_y_offset=-19.5;
winder_offset=26;
dock_x=36;
native_dock_y=-11;
dock_y=winder_offset+native_dock_y;
seat_z=frame_t+standoff;
pad_d=10;
shoulder_d=8;
neck_d=4;
neck_passage_d=neck_d+2*snap_neck_clearance;
snap_throat_d=snap_head_d+2*snap_throat_clearance;
snap_throat_x_d=snap_throat_d+2*snap_throat_x_extra;
head_flat=2.0; // OUTER flat; latch tongue lies inward, toward Y=0
throat_flat=head_flat+snap_throat_clearance+snap_flat_extra;
head_under_z=center_plate_t+axial_gap;
head_band_h=1.0;
head_bevel_h=0.2;
head_top_z=head_under_z+head_band_h+head_bevel_h;
receiver_d=12;
beam_root_x=13; // Stay outside the inherited raised BNC ribs at X=9..12
beam_catch_x=dock_x;
beam_length=beam_catch_x-beam_root_x;
beam_y=dock_y-2.6;
beam_end_x=44;
beam_fillet=1.5;
tab_inner_y=beam_y-beam_t/2;
tab_outer_y=dock_y+2;
tab_inner_x=41;
tab_outer_x=51;
stop_inner_y=tab_inner_y-snap_stop;
root_min_y=stop_inner_y-2;
root_max_y=dock_y+6;
guide_x=20;
guide_native_y=-8.5;
guide_y=winder_offset+guide_native_y;
guide_d=4;
guide_h=7; // Stays engaged through the 5.6-degree clearance lift and parking
guide_clearance=0.3;
guide_entry_chamfer=0.4; // Lead-in for small guided settling during the first peel
guide_pad_d=6;
guide_shoulder_d=4.8; // Avoid coincident bevel/shoulder facets at the pad edge
guide_receiver_d=8;
capture_offset=neck_passage_d/2;
neck_away_play=throat_flat-neck_d/2;
capture_nominal=snap_head_d/2-capture_offset;
capture_after_play=capture_nominal-neck_away_play;
parking_capture=snap_top_d/2-capture_offset-neck_away_play;
integration_step=0.25;

assert(len([for(p=["center","winder","assembled","print_layout","exploded",
    "coupon","fit_coupon","retention_coupon","released","peel","parked","wire_envelopes"]) if(p==part) 1])>0,"Unknown part");
assert(preset=="40m" || preset=="80m","Choose a known clearance preset");
assert(bnc_hole_d>=9.7 && bnc_hole_d<=10.2,"BNC finished diameter must be 9.7..10.2 mm");
assert(wing_length>=37.5 && wing_length<=60,"Wing reach must be 37.5..60 mm");
assert(winding_span>=140 && winding_span<=200,"Lower-tip span must be 140..200 mm");
assert(wire_hole_inner_x>=27 && wire_hole_inner_x<=30,"Inner wire hole must be 27..30 mm from centerline");
assert(wire_hole_pitch>=4 && wire_hole_pitch<=6.5,"Wire-hole pitch must be 4..6.5 mm; check face-web guard");
assert(wire_face_bulge==0 || (wire_face_bulge>=2 && wire_face_bulge<=12),
    "Face buildup must be zero for the preset, or 2..12 mm per face");
assert(wire_edge_bulge>=2 && wire_edge_bulge<=5,"Wire edge reserve must be 2..5 mm to clear guide pads");
assert(standoff>=2.5 && standoff<=25,"Standoff height must be 2.5..25 mm; check loaded fit");
assert(native_dock_y+pad_d/2<=-wire_edge_bulge-0.5,"Dry pads enter winding reserve");
assert(snap_head_d==7.0 && snap_top_d==6.8,"Use the matched revision-2 head and passage");
assert(snap_throat_clearance>=0.2 && snap_throat_clearance<=0.3,"Throat allowance 0.2..0.3 per side");
assert(snap_throat_x_extra>=0.15 && snap_throat_x_extra<=0.25,"X-only peel allowance 0.15..0.25 mm per side");
assert(snap_flat_extra>=0.05 && snap_flat_extra<=0.10,"Extra outer-flat yaw allowance 0.05..0.10 mm");
assert(neck_notch_x_extra>=0.7 && neck_notch_x_extra<=0.8,"Revision-2 neck sweep 0.7..0.8 mm each X side");
assert(snap_neck_clearance>=0.15 && snap_neck_clearance<=0.25,"Neck notch allowance 0.15..0.25 per side");
assert(capture_after_play>=0.9 && parking_capture>=0.8,"Insufficient latch or flat-top parking overlap");
assert(beam_t>=1.5 && beam_t<=1.8,"Beam thickness 1.5..1.8 mm");
assert(snap_release>=3.0 && snap_release<=snap_stop,"Paddle release travel 3.0 mm or more");
assert(snap_stop>=3.3 && snap_stop<=3.5,"Actual outer-paddle stop travel 3.3..3.5 mm");
assert(finger_x>=tab_inner_x && finger_x<=tab_outer_x,"Load must lie on the paddle");
assert(tab_inner_y-snap_stop>7.5+0.5,"Inward beam travel would touch original wire bar");
assert(axial_gap>=0.7 && axial_gap<=1.0,"Peel candidate axial clearance 0.7..1.0 mm");
assert(guide_native_y+guide_pad_d/2<=-wire_edge_bulge-0.5,"Guide pad enters winding reserve");
assert(min([for(f=[41,46,51]) actuator_displacement(dock_x,snap_release,f)])>=1.6,
    "Actual paddle motion must open catch at least 1.6 mm for all finger positions");
assert(max([for(f=[41,46,51]) actuator_peak_strain(snap_stop,f)])<0.009,
    "Variable-section elementary strain screen must remain below 0.9%");

// Imported by views so their hardware and head crops follow the actual seat.
function dock_seat_height()=seat_z;
function clamp(v,a,b)=min(b,max(a,v));
function total(values,i=0)=i>=len(values) ? 0 : values[i]+total(values,i+1);
function root_extra(x)=x<beam_root_x+beam_fillet ?
    beam_fillet-sqrt(max(0,pow(beam_fillet,2)-pow(max(x,beam_root_x)-beam_root_x-beam_fillet,2))) : 0;
function notch_top(x)=
    let(dx=max(0,abs(x-dock_x)-neck_notch_x_extra))
    dx<neck_passage_d/2 ?
        min(beam_y+beam_t/2,dock_y-sqrt(pow(neck_passage_d/2,2)-dx*dx)) : beam_y+beam_t/2;
// Keep the root flexible and stiffen the span around the catch INWARD in XY.
// This transfers more of the same paddle stroke to the catch. A tall rib here
// would foul the head underside; this reinforcement stays within the plate.
function beam_inner(x)=tab_inner_y-beam_inner_reinforcement*
    min(clamp((x-23)/2,0,1),clamp((41-x)/2,0,1));
function section_width(x)=x>=tab_inner_x ? tab_outer_y-tab_inner_y :
    notch_top(x)-beam_inner(x)+2*root_extra(x);
function section_inertia(x)=pow(section_width(x),3)+
    (x>=tab_inner_x+paddle_inset && x<=tab_outer_x-paddle_inset ?
        (paddle_height-center_plate_t)/center_plate_t*pow(section_width(x)-2*paddle_inset,3) : 0);
// Euler-Bernoulli screening with the real varying in-plane section. Common
// E and plate thickness cancel when normalizing to outer-paddle displacement.
// This is a deformation estimate, not FEA or a fatigue/force prediction.
function beam_integral(x,f,slope=false)=x<=beam_root_x ? 0 :
    total([for(s=[beam_root_x+integration_step/2:integration_step:min(x,f)])
        integration_step*(f-s)*(slope ? 1 : x-s)/section_inertia(s)]);
// Cache the SAME direct quadrature sums at the contour's 0.25 mm samples.
// Four tongues otherwise recompute each sum and normalization at every point.
actuation_samples=[for(x=[beam_root_x:integration_step:tab_outer_x])
    [beam_integral(x,finger_x),beam_integral(x,finger_x,true)]];
actuation_norm=actuation_samples[len(actuation_samples)-1][0];
function sampled_integral(x,f,slope=false)=
    let(i=round((x-beam_root_x)/integration_step))
    f==finger_x && i>=0 && i<len(actuation_samples) &&
        abs(x-(beam_root_x+i*integration_step))<0.0000001 ?
            actuation_samples[i][slope ? 1 : 0] : beam_integral(x,f,slope);
function normalization(f)=f==finger_x ? actuation_norm : beam_integral(tab_outer_x,f);
function actuator_displacement(x,travel,f=finger_x)=
    travel*sampled_integral(x,f)/normalization(f);
function actuator_slope(x,travel,f=finger_x)=
    travel*sampled_integral(x,f,true)/normalization(f);
function actuator_peak_strain(travel,f=finger_x)=
    max([for(s=[beam_root_x+integration_step/2:integration_step:f])
        travel*(f-s)*section_width(s)/(2*section_inertia(s)*normalization(f))]);
function deformed_point(x,y,travel,f=finger_x)=
    let(theta=atan(actuator_slope(x,travel,f)), dy=y-beam_y)
    [x+dy*sin(theta),beam_y-actuator_displacement(x,travel,f)+dy*cos(theta)];
// Conservative vertical lift to keep the retained side's flat shoulder out
// of the tilted 4 mm backplate. It is a starting kinematic model, not proof.
function peel_clearance_lift(angle)=
    shoulder_d/2*tan(abs(angle))+center_plate_t/2*(1/cos(angle)-1)+0.04;

module station_transform(side=1,row=1) {
    scale([side,row,1]) children();
}
module d_profile(diameter,flat) {
    intersection() {
        circle(d=diameter);
        translate([-20,-40]) square([40,40+flat]);
    }
}
module winder_outline() {
    union() {
        adjustable_winder_frame_2d(wing_length,winding_span);
        for(x=[-dock_x,dock_x]) translate([x,native_dock_y]) circle(d=pad_d);
        translate([guide_x,guide_native_y]) circle(d=guide_pad_d);
    }
}
module headed_pin() {
    translate([0,0,-eps]) cylinder(d=neck_d,h=head_under_z+2*eps);
    // Construct common round band and top bevel before one shared D clip.
    translate([0,0,head_under_z]) intersection() {
        union() {
            cylinder(d=snap_head_d,h=head_band_h+eps);
            translate([0,0,head_band_h])
                cylinder(d1=snap_head_d,d2=snap_top_d,h=head_bevel_h);
        }
        translate([-20,-40,-eps]) cube([40,40+head_flat,head_band_h+head_bevel_h+2*eps]);
    }
}
module single_winder() {
    union() {
        beveled_frame(height=frame_t,bevel=frame_bevel) winder_outline();
        for(x=[-dock_x,dock_x]) translate([x,native_dock_y,0]) {
            translate([0,0,frame_t-frame_bevel-eps])
                cylinder(d=shoulder_d,h=seat_z-frame_t+frame_bevel+eps);
            translate([0,0,seat_z]) headed_pin();
        }
        translate([guide_x,guide_native_y,0]) {
            translate([0,0,frame_t-frame_bevel-eps])
                cylinder(d=guide_shoulder_d,h=seat_z-frame_t+frame_bevel+eps);
            translate([0,0,seat_z-eps]) cylinder(d=guide_d,h=guide_h+eps);
        }
    }
}
module station_fixed_2d() {
    union() {
        translate([dock_x,dock_y]) circle(d=receiver_d);
        translate([beam_root_x-3,root_min_y]) square([3,root_max_y-root_min_y]);
        // Outer rail connects the fixed D-flat/back wall around the tongue.
        translate([beam_root_x-3,dock_y+4]) square([45-beam_root_x,2]);
        // Inner rail is a hard stop, clear of original wire-hole mouths.
        translate([beam_root_x-3,root_min_y]) square([55-beam_root_x,2]);
    }
}
module station_cutouts_2d() {
    translate([dock_x,dock_y]) scale([snap_throat_x_d/snap_throat_d,1])
        d_profile(snap_throat_d,throat_flat);
    // Isolate beam without cutting original bar (whose top is Y=7.5).
    translate([beam_root_x+beam_fillet,stop_inner_y])
        square([40.5-beam_root_x-beam_fillet,beam_y+1.5-stop_inner_y]);
    // Clear full finger paddle sweep outside the fixed socket back wall.
    translate([40.5,stop_inner_y]) square([12,tab_outer_y+0.7-stop_inner_y]);
}
module root_fillets_2d() {
    for(s=[-1,1]) translate([beam_root_x,beam_y+s*beam_t/2])
        scale([1,s]) difference() {
            square([beam_fillet,beam_fillet]);
            translate([beam_fillet,beam_fillet]) circle(r=beam_fillet);
        }
}
module moving_tongue_2d(release=0) {
    assert(release>=0 && release<=snap_stop,"Release exceeds mechanical stop");
    polygon(concat(
        [deformed_point(beam_root_x-eps,beam_inner(beam_root_x)-root_extra(beam_root_x),release)],
        [for(x=[beam_root_x:integration_step:tab_outer_x]) deformed_point(x,beam_inner(x)-root_extra(x),release)],
        [for(x=[tab_outer_x:-integration_step:tab_inner_x]) deformed_point(x,tab_outer_y,release)],
        [for(x=[tab_inner_x:-integration_step:beam_root_x]) deformed_point(x,notch_top(x)+root_extra(x),release)],
        [deformed_point(beam_root_x-eps,notch_top(beam_root_x)+root_extra(beam_root_x),release)]));
}
module moving_paddle_2d(release=0) {
    polygon(concat(
        [for(x=[tab_inner_x:integration_step:tab_outer_x]) deformed_point(x,tab_inner_y,release)],
        [for(x=[tab_outer_x:-integration_step:tab_inner_x]) deformed_point(x,tab_outer_y,release)]));
}
module center_plate_holes() {
    plate_holes(terminal_d=terminal_hole_d,wire_d=wire_hole_d,
        hang_d=hang_hole_d,wire_positions=wire_positions,chamfer=wire_chamfer);
}

module guide_hole() {
    diameter=guide_d+2*guide_clearance;
    translate([0,0,-eps]) cylinder(d=diameter,h=center_plate_t+2*eps);
    translate([0,0,-eps])
        cylinder(d1=diameter+2*guide_entry_chamfer,d2=diameter,
            h=guide_entry_chamfer+eps);
    translate([0,0,center_plate_t-guide_entry_chamfer])
        cylinder(d1=diameter,d2=diameter+2*guide_entry_chamfer,
            h=guide_entry_chamfer+eps);
}
module fixed_lift_bridges_2d() {
    // Fixed edge purchase in the central gap: lift here, never on a flexure.
    for(s=[-1,1]) station_transform(s,1)
        translate([48,-stop_inner_y]) square([4,2*stop_inner_y]);
}
module snap_tab(side=1,row=1,release=0) {
    // Isolated tongue in CENTER PRINT coordinates.
    translate([0,-center_y_offset,0]) station_transform(side,row) union() {
        linear_extrude(height=center_plate_t) moving_tongue_2d(release);
        translate([0,0,center_plate_t-eps])
            linear_extrude(height=paddle_height-center_plate_t+eps)
                offset(delta=-paddle_inset) moving_paddle_2d(release);
    }
}
module dock_center(release=[0,0]) {
    // Array order is [LEFT end, RIGHT end]; each value moves BOTH row tabs.
    releases=is_list(release) ? release : [release,release];
    union() {
        difference() {
            union() {
                center(terminal_d=terminal_hole_d,wire_d=wire_hole_d,
                    hang_d=hang_hole_d,wire_positions=wire_positions,
                    chamfer=wire_chamfer,bnc_fit=bnc_clearance);
                translate([0,-center_y_offset,0]) linear_extrude(height=center_plate_t)
                    union() {
                        for(s=[-1,1],r=[-1,1]) station_transform(s,r) station_fixed_2d();
                        fixed_lift_bridges_2d();
                        for(r=[-1,1]) rotate(r==1 ? 0 : 180)
                            translate([guide_x,guide_y]) circle(d=guide_receiver_d);
                    }
            }
            center_plate_holes();
            bnc_hole(bnc_clearance);
            for(r=[-1,1]) translate([r*guide_x,-center_y_offset+r*guide_y,0]) guide_hole();
            translate([0,-center_y_offset,-eps]) linear_extrude(height=center_plate_t+2*eps)
                for(s=[-1,1],r=[-1,1]) station_transform(s,r) station_cutouts_2d();
        }
        for(i=[0:1],r=[-1,1]) snap_tab(i==0 ? -1 : 1,r,releases[i]);
    }
}
module placed_winder(side=1,drop=0,row=undef) {
    r=is_undef(row) ? side : row;
    translate([0,r*winder_offset,-drop]) rotate([0,0,r==1 ? 0 : 180]) single_winder();
}
module placed_center(release=[0,0]) {
    translate([0,center_y_offset,seat_z]) dock_center(release);
}
module peel_center(side=1,angle=pose_angle,lift=undef,release=[0,snap_release]) {
    pivot=[-side*dock_x,0,seat_z+center_plate_t/2];
    dz=is_undef(lift) ? peel_clearance_lift(angle) : lift;
    translate([0,0,dz]) translate(pivot) rotate([0,-side*angle,0])
        translate(-pivot) placed_center(release);
}
module parked_center(side=1,angle=park_angle,lift=undef) {
    peel_center(side,angle,lift,[0,0]);
}
function wire_envelope_bounds(side=1) =
    let(lo=[winder_bounds[0][0]-wire_edge_bulge,-wire_edge_bulge,-face_bulge],
        hi=[winder_bounds[1][0]+wire_edge_bulge,winder_bounds[1][1]+wire_edge_bulge,frame_t+face_bulge])
    side==1 ? [[lo[0],winder_offset+lo[1],lo[2]],[hi[0],winder_offset+hi[1],hi[2]]] :
        [[-hi[0],-winder_offset-hi[1],lo[2]],[-lo[0],-winder_offset-lo[1],hi[2]]];
module wire_envelope(side=1) {
    bounds=wire_envelope_bounds(side);
    translate(bounds[0]) cube(bounds[1]-bounds[0]);
}
module fit_coupon(separate_feet=false) {
    // One COMPLETE right pinch group: both real flexures, both D-throats,
    // the fixed lifting bridge, and their true 30 mm stud-row spacing.
    translate([-11,0,0]) intersection() {
        dock_center();
        translate([beam_root_x-3,-3,-eps])
            cube([55-beam_root_x+eps,45,paddle_height+2*eps]);
    }
    // A joined foot checks paired ergonomics; independent feet expose the
    // outward retreat of each actual winder during a retention pull test.
    translate([-18,19.5,0]) {
        linear_extrude(height=frame_t)
            if(separate_feet)
                for(y=[-dock_y,dock_y]) translate([0,y]) circle(d=pad_d);
            else hull() for(y=[-dock_y,dock_y]) translate([0,y]) circle(d=pad_d);
        for(r=[-1,1]) translate([0,r*dock_y,0]) {
            translate([0,0,frame_t-eps]) cylinder(d=shoulder_d,h=seat_z-frame_t+eps);
            translate([0,0,seat_z]) rotate([0,0,r==1 ? 0 : 180]) headed_pin();
        }
    }
}
if(part=="center") dock_center();
else if(part=="winder") single_winder();
else if(part=="coupon" || part=="fit_coupon") fit_coupon();
else if(part=="retention_coupon") fit_coupon(separate_feet=true);
else if(part=="wire_envelopes") for(r=[-1,1]) wire_envelope(r);
else if(part=="print_layout") {
    translate([0,-50,0]) single_winder();
    translate([0,15+layout_height_delta,0]) single_winder();
    translate([0,72+2*layout_height_delta,0]) dock_center();
} else {
    color([0.88,0.48,0.20])
        if(part=="peel") peel_center();
        else if(part=="parked") parked_center();
        else placed_center(part=="released" ? [0,snap_release] : [0,0]);
    for(r=[-1,1]) color(r==1 ? [0.15,0.57,0.71] : [0.35,0.66,0.45])
        placed_winder(r,part=="exploded" ? 24 : 0);
    if($preview && show_wire && part=="assembled")
        for(r=[-1,1]) %color([0.8,0.12,0.16,0.12]) wire_envelope(r);
}
