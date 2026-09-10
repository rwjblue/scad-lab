/*
  N1RWJ modular dipole — FOUR true snap studs, two per identical winder.
  Prototype 2026-09-10. The right upper/lower paddles pinch together to
  release both RIGHT studs; the left pair does the same on the LEFT.
  Broad flat head tops are intended as a parked-open support after peeling
  one carrier end upward. This kinematic proposal requires swept validation.
  Docking requires pinching: the flat parking tops deliberately lack an
  automatic push-in funnel. See review/DESIGN.md for the tradeoff.
  Units mm. Broad backs print down. Flat head undersides overhang 1 mm:
  print the exact paired-end coupon before full winders. No fatigue rating.
*/
use <native_profile.scad>
use <../dipole_winder/frame_bevel.scad>
use <../dipole_center/dipole_center.scad>

/* [Output] */
part="print_layout"; // [center,winder,assembled,print_layout,exploded,coupon,fit_coupon,released,peel,parked,wire_envelopes]
preset="40m"; // [40m,80m]
show_wire=false;
pose_angle=5.5;
park_angle=4.7; // Near-contact preview; renders use the measured support angle

/* [BNC fit] */
bnc_clearance=0.20; // 10.1 mm D-hole; re-cut explicitly through inherited shelf

/* [Winding clearance] */
wire_face_bulge=preset=="80m" ? 8 : 5;
wire_edge_bulge=5;
wire_gap=3; // Provisional 2 mm silicone tie plus 1 mm air

/* [Snap fit] */
snap_head_d=6.0;
snap_top_d=5.8; // Broad FLAT top supports a released, returned tongue
snap_throat_clearance=0.30;
snap_throat_x_extra=0.15; // Extra X-only tilt/yaw allowance; Y flat is unchanged
snap_flat_extra=0.05; // Small yaw allowance for the rigid head's flat corners
snap_neck_clearance=0.20;
neck_notch_x_extra=0.40; // Sweep the neck notch in X; preserve its inner Y edge
snap_release=3.15; // Actual travel at the OUTER paddle edge, not at the catch
snap_stop=3.40;
finger_x=51; // Load location; 41..51 spans the usable paddle
beam_t=1.60;
axial_gap=0.80;

/* [Hidden] */
$fn=96;
eps=0.02;
frame_t=5;
frame_bevel=0.5;
center_plate_t=4;
paddle_height=10; // Raised finger face clears reserved wire beneath the pad
paddle_inset=0.1; // Raised face sits inside base; avoids coincident side facets
center_y_offset=-19.5;
winder_offset=26;
dock_x=36;
native_dock_y=-11;
dock_y=winder_offset+native_dock_y;
seat_z=frame_t+wire_face_bulge+wire_gap;
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
beam_root_x=15;
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
    "coupon","fit_coupon","released","peel","parked","wire_envelopes"]) if(p==part) 1])>0,"Unknown part");
assert(preset=="40m" || preset=="80m","Choose a known clearance preset");
assert(bnc_clearance>=0.1 && bnc_clearance<=0.25,"BNC per-side allowance 0.10..0.25");
assert(wire_face_bulge>=2 && wire_face_bulge<=12,"Face buildup reservation 2..12 mm");
assert(wire_edge_bulge>=2 && wire_edge_bulge<=5.5,"Widen dry pad clearance before more edge buildup");
assert(wire_gap>=3 && wire_gap<=5,"Keep provisional 2 mm strap plus >=1 mm air");
assert(native_dock_y+pad_d/2<=-wire_edge_bulge-0.5,"Dry pads enter winding reserve");
assert(snap_head_d==6 && snap_top_d>=5.7 && snap_top_d<=6,"Keep the proven size family");
assert(snap_throat_clearance>=0.2 && snap_throat_clearance<=0.3,"Throat allowance 0.2..0.3 per side");
assert(snap_throat_x_extra>=0.15 && snap_throat_x_extra<=0.25,"X-only peel allowance 0.15..0.25 mm per side");
assert(snap_flat_extra>=0.05 && snap_flat_extra<=0.10,"Extra outer-flat yaw allowance 0.05..0.10 mm");
assert(neck_notch_x_extra>=0.3 && neck_notch_x_extra<=0.5,"Neck articulation sweep 0.3..0.5 mm each X side");
assert(snap_neck_clearance>=0.15 && snap_neck_clearance<=0.25,"Neck notch allowance 0.15..0.25 per side");
assert(capture_after_play>=0.4 && parking_capture>=0.3,"Insufficient latch or flat-top parking overlap");
assert(beam_t>=1.5 && beam_t<=1.8,"Beam thickness 1.5..1.8 mm");
assert(snap_release>=3.0 && snap_release<=snap_stop,"Paddle release travel 3.0 mm or more");
assert(snap_stop>=3.3 && snap_stop<=3.4,"Actual outer-paddle stop travel 3.3..3.4 mm");
assert(finger_x>=tab_inner_x && finger_x<=tab_outer_x,"Load must lie on the paddle");
assert(tab_inner_y-snap_stop>7.5+0.5,"Inward beam travel would touch original wire bar");
assert(axial_gap>=0.7 && axial_gap<=1.0,"Peel candidate axial clearance 0.7..1.0 mm");
assert(guide_native_y+guide_pad_d/2<=-wire_edge_bulge-0.5,"Guide pad enters winding reserve");
assert(min([for(f=[41,46,51]) actuator_displacement(dock_x,snap_release,f)])>=1.2,
    "Actual paddle motion must open catch at least 1.2 mm for all finger positions");
assert(max([for(f=[41,46,51]) actuator_peak_strain(snap_stop,f)])<0.009,
    "Variable-section elementary strain screen must remain below 0.9%");

function clamp(v,a,b)=min(b,max(a,v));
function total(values,i=0)=i>=len(values) ? 0 : values[i]+total(values,i+1);
function root_extra(x)=x<beam_root_x+beam_fillet ?
    beam_fillet-sqrt(max(0,pow(beam_fillet,2)-pow(max(x,beam_root_x)-beam_root_x-beam_fillet,2))) : 0;
function notch_top(x)=
    let(dx=max(0,abs(x-dock_x)-neck_notch_x_extra))
    dx<neck_passage_d/2 ?
        min(beam_y+beam_t/2,dock_y-sqrt(pow(neck_passage_d/2,2)-dx*dx)) : beam_y+beam_t/2;
function section_width(x)=x>=tab_inner_x ? tab_outer_y-tab_inner_y :
    notch_top(x)-tab_inner_y+2*root_extra(x);
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
        native_frame_2d();
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
        translate([12,root_min_y]) square([3,root_max_y-root_min_y]);
        // Outer rail connects the fixed D-flat/back wall around the tongue.
        translate([12,dock_y+4]) square([30,2]);
        // Inner rail is a hard stop, clear of original wire-hole mouths.
        translate([12,root_min_y]) square([40,2]);
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
        [deformed_point(beam_root_x-eps,tab_inner_y-root_extra(beam_root_x),release)],
        [for(x=[beam_root_x:integration_step:tab_outer_x]) deformed_point(x,tab_inner_y-root_extra(x),release)],
        [for(x=[tab_outer_x:-integration_step:tab_inner_x]) deformed_point(x,tab_outer_y,release)],
        [for(x=[tab_inner_x:-integration_step:beam_root_x]) deformed_point(x,notch_top(x)+root_extra(x),release)],
        [deformed_point(beam_root_x-eps,notch_top(beam_root_x)+root_extra(beam_root_x),release)]));
}
module moving_paddle_2d(release=0) {
    polygon(concat(
        [for(x=[tab_inner_x:integration_step:tab_outer_x]) deformed_point(x,tab_inner_y,release)],
        [for(x=[tab_outer_x:-integration_step:tab_inner_x]) deformed_point(x,tab_outer_y,release)]));
}
module original_plate_holes() {
    translate([0,32,0]) round_plate_hole(6,0.5);
    for(s=[-1,1]) {
        translate([s*10,21,0]) round_plate_hole(3.4);
        for(x=[28,33.5,39]) translate([s*x,21,0]) round_plate_hole(3.2,0.5);
    }
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
                center();
                translate([0,-center_y_offset,0]) linear_extrude(height=center_plate_t)
                    union() {
                        for(s=[-1,1],r=[-1,1]) station_transform(s,r) station_fixed_2d();
                        fixed_lift_bridges_2d();
                        for(r=[-1,1]) rotate(r==1 ? 0 : 180)
                            translate([guide_x,guide_y]) circle(d=guide_receiver_d);
                    }
            }
            original_plate_holes();
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
module wire_envelope(side=1) {
    translate([0,side*winder_offset,0]) rotate([0,0,side==1 ? 0 : 180])
        translate([-70-wire_edge_bulge,-wire_edge_bulge,-wire_face_bulge])
            cube([140+2*wire_edge_bulge,37.5+2*wire_edge_bulge,frame_t+2*wire_face_bulge]);
}
module fit_coupon() {
    // One COMPLETE right pinch group: both real flexures, both D-throats,
    // the fixed lifting bridge, and their true 30 mm stud-row spacing.
    translate([-11,0,0]) intersection() {
        dock_center();
        translate([11,-3,-eps]) cube([42,45,10]);
    }
    // Two exact studs on a single test foot; no hand must hold two loose posts.
    translate([-18,19.5,0]) {
        linear_extrude(height=frame_t)
            hull() for(y=[-dock_y,dock_y]) translate([0,y]) circle(d=pad_d);
        for(r=[-1,1]) translate([0,r*dock_y,0]) {
            translate([0,0,frame_t-eps]) cylinder(d=shoulder_d,h=seat_z-frame_t+eps);
            translate([0,0,seat_z]) rotate([0,0,r==1 ? 0 : 180]) headed_pin();
        }
    }
}
if(part=="center") dock_center();
else if(part=="winder") single_winder();
else if(part=="coupon" || part=="fit_coupon") fit_coupon();
else if(part=="wire_envelopes") for(r=[-1,1]) wire_envelope(r);
else if(part=="print_layout") {
    translate([0,-50,0]) single_winder();
    translate([0,15,0]) single_winder();
    translate([0,72,0]) dock_center();
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
