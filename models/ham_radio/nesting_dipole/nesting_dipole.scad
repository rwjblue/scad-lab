/*
  N1RWJ nesting dipole — nested spines and crosswise center.
  Print one LEFT and one RIGHT winder. The ORIGINAL stations at
  X=+/-36, Y=-11 stay fixed; the left part swaps the stud and socket.
  Flip the left part over its long spine axis so the stud-bearing faces
  meet. BOTH studs enter the opposite sockets and the winding bays extend
  to opposite sides. The two engagements locate the pair against pivoting;
  the rear strap keeps the parts together. The right part matches the
  previous winder, so one existing print can be reused.
  The center has no docking holes. A short hook-and-loop strap runs from one
  end slot, around the back of the pair, to the other slot; fold its ends
  back at the slots. The slots sit inline with the terminal and wire holes,
  so strap tension pulls through the main bar without offset wings.
  Actual seating depends on the wound wire and may tilt.
  Packing views are illustrative, not a fixed center-to-frame connection.
  Units mm. Broad backs print down. See README.md and NOTICE.md.
*/
use <winder_profile.scad>
use <../dipole_winder/frame_bevel.scad>
use <../dipole_center/dipole_center.scad>

/* [Output] */
part="print_layout"; // [center,winder_left,winder_right,winder,assembled,winders,print_layout,exploded,bnc_fit_coupon,bnc_fit_coupon_tight,fit_coupon,wire_envelopes]
// Used only by part="winder". The explicitly named left/right parts override it.
winder_hand="right"; // [left,right]
preset="40m"; // [40m,80m]
show_wire=false;

/* [Winder size] */
wing_length=37.5; // [37.5:0.5:60]
winding_span=140; // [140:1:200]

/* [Spine joint] */
// Exposed length beyond the OTHER winder's 5 mm frame.
post_protrusion=3; // [2:0.5:5]
// Sliding clearance on EACH side of the original 6 mm stud; never a press fit.
alignment_clearance=0.25; // [0.15:0.05:0.4]

/* [Rear strap] */
// Slot length accepts a roughly 12.7 mm (half-inch) hook-and-loop strap.
strap_slot_width=14; // [10:0.5:20]
strap_slot_thickness=3; // [2:0.5:4]

/* [Wire space] */
// Buildup on EACH face; affects packing views, not the spine joint.
wire_face_bulge=0; // [0:Preset,2:2 mm,3:3 mm,4:4 mm,5:5 mm,6:6 mm,7:7 mm,8:8 mm,9:9 mm,10:10 mm,11:11 mm,12:12 mm]
wire_edge_bulge=5; // [2:0.5:5]

/* [BNC connector fit] */
// D-hole diameter, NOT clearance per side. Print a BNC fit coupon first and
// use the smallest size that seats your connector without forcing it.
// 9.5 mm was selected after trying the finer printed fit coupon.
// If 9.7 still has play, bnc_fit_coupon_tight tests 9.5..9.7 in 0.05 mm steps.
// Sizes below the drawing's 9.7 mm panel cutout are empirical print-fit trials.
bnc_hole_d=9.5; // [9.5:0.05:10.2]

/* [Center holes] */
terminal_hole_x=7; // [7:0.5:10]
wire_hole_inner_x=25; // [24:0.1:30]
wire_hole_pitch=5.5; // [4:0.1:6.5]
wire_hole_d=3.2; // [2.6:0.1:3.6]
wire_chamfer=0.5; // [0:0.1:0.6]
terminal_hole_d=3.4; // [3.1:0.1:3.6]
hang_hole_d=8; // [6:0.5:8]

/* [Hidden] */
$fn=96;
eps=0.02;
frame_t=5;
frame_bevel=0.5;
center_plate_t=4;
dock_x=36;
native_dock_y=-11;
pad_d=10;
pad_x_extra=2;
pin_d=6;
pin_h=frame_t+post_protrusion;
pin_tip_chamfer=0.6;
post_root_fillet=0.6;
socket_root_relief=post_root_fillet;
socket_entry_chamfer=0.4;
face_bulge=wire_face_bulge==0 ? (preset=="80m" ? 8 : 5) : wire_face_bulge;
wire_positions=[for(i=[0:2]) wire_hole_inner_x+i*wire_hole_pitch];
bnc_clearance=(bnc_hole_d-9.7)/2;
winder_bounds=winder_profile_bounds(wing_length,winding_span);
print_min_y=winder_bounds[0][1];
profile_height=winder_bounds[1][1]-print_min_y;
layout_gap=8;
// Keep the 90 mm width and put the strap pulls on the main bar's centerline.
strap_slot_x=41;
strap_slot_y=21;
// Center remains independent of the winder-to-winder connection.
center_pack_x=18;
center_pack_y=7;
center_bar_y=21;
// Illustrative strapped pose: 2 mm for the strap above the higher coil face.
// This changes the preview placement only; there are no printed standoffs.
center_pack_z=max(2*frame_t+face_bulge+2,frame_t+pin_h+0.5);

assert(len([for(p=["center","winder_left","winder_right","winder","assembled","winders","print_layout",
    "exploded","bnc_fit_coupon","bnc_fit_coupon_tight","fit_coupon","wire_envelopes"]) if(p==part) 1])>0,"Unknown part");
assert(preset=="40m" || preset=="80m","Choose 40m or 80m wire-space preset");
assert(winder_hand=="left" || winder_hand=="right","Choose left or right winder");
assert(wing_length>=37.5 && wing_length<=60,"Wing reach must be 37.5..60 mm");
assert(winding_span>=140 && winding_span<=200,"Lower-tip span must be 140..200 mm");
assert(post_protrusion>=2 && post_protrusion<=5,"Exposed stud length must be 2..5 mm");
assert(alignment_clearance>=0.15 && alignment_clearance<=0.4,"Stud clearance must be 0.15..0.4 mm per side");
assert(strap_slot_width>=10 && strap_slot_width<=20,"Strap slot length must be 10..20 mm");
assert(strap_slot_thickness>=2 && strap_slot_thickness<=4,"Strap slot thickness must be 2..4 mm");
assert(wire_face_bulge==0 || (wire_face_bulge>=2 && wire_face_bulge<=12),"Wire face reserve must be 0 or 2..12 mm");
assert(wire_edge_bulge>=2 && wire_edge_bulge<=5,"Wire edge reserve must be 2..5 mm");
assert(bnc_hole_d>=9.5 && bnc_hole_d<=10.2,"BNC cutout diameter must be 9.5..10.2 mm");
assert(terminal_hole_x>=7 && terminal_hole_x<=10,"Terminal offset must be 7..10 mm");
assert(wire_hole_inner_x>=24 && wire_hole_inner_x<=30,"Inner wire hole must be 24..30 mm");
assert(wire_hole_pitch>=4 && wire_hole_pitch<=6.5,"Wire-hole pitch must be 4..6.5 mm");
assert(terminal_hole_d>=3.1 && terminal_hole_d<=3.6,"This layout is for M3 terminals");
assert(wire_hole_d>=2.6 && wire_hole_d<=3.6,"Wire holes must be 2.6..3.6 mm");
assert(hang_hole_d>=6 && hang_hole_d<=8,"Keep the larger suspension eye 6..8 mm");
assert(wire_chamfer>=0 && wire_chamfer<=0.6,"Keep chamfer at 0..0.6 mm");
assert(native_dock_y+pad_d/2<=-wire_edge_bulge-1,"Keep the original pads outside the winding reserve");
assert((pad_d-2*frame_bevel-pin_d-2*alignment_clearance-2*socket_root_relief)/2>=0.5-0.000001,
    "Keep at least 0.5 mm of bearing land around the relieved socket");

module docking_pad_2d() {
    hull() for(x=[-pad_x_extra/2,pad_x_extra/2]) translate([x,0]) circle(d=pad_d);
}

module coupon_outline() {
    hull() for(x=[-dock_x,dock_x]) translate([x,native_dock_y]) docking_pad_2d();
}

module winder_outline() {
    union() {
        adjustable_winder_frame_2d(wing_length,winding_span);
        for(x=[-dock_x,dock_x]) translate([x,native_dock_y]) docking_pad_2d();
    }
}

module post_root() {
    rotate_extrude(convexity=4) polygon(concat(
        [[0,-eps],[pin_d/2+post_root_fillet,-eps]],
        [for(a=[-90:-5:-180])
            [pin_d/2+post_root_fillet+post_root_fillet*cos(a),
             post_root_fillet+post_root_fillet*sin(a)]],
        [[0,post_root_fillet]]));
}

module alignment_post() {
    translate([0,0,frame_t-frame_bevel-eps])
        cylinder(d=pin_d,h=frame_bevel+pin_h-pin_tip_chamfer+eps);
    translate([0,0,frame_t+pin_h-pin_tip_chamfer])
        cylinder(d1=pin_d,d2=pin_d-2*pin_tip_chamfer,h=pin_tip_chamfer);
    translate([0,0,frame_t]) post_root();
}

module alignment_socket() {
    d=pin_d+2*alignment_clearance;
    translate([0,0,-eps]) cylinder(d=d,h=frame_t+2*eps);
    // Preserve the approved socket. Both mating roots enter the 0.6 mm
    // relief on the post-bearing top face; the bed-face chamfer is an exit.
    translate([0,0,frame_t-socket_root_relief])
        cylinder(d1=d,d2=d+2*(socket_root_relief+eps),h=socket_root_relief+eps);
    translate([0,0,-eps])
        cylinder(d1=d+2*(socket_entry_chamfer+eps),d2=d,h=socket_entry_chamfer+eps);
}

module spine_part(coupon=false,hand="right") {
    post_x=hand=="right" ? dock_x : -dock_x;
    difference() {
        union() {
            beveled_frame(height=frame_t,bevel=frame_bevel)
                if(coupon) coupon_outline(); else winder_outline();
            translate([post_x,native_dock_y,0]) alignment_post();
        }
        translate([-post_x,native_dock_y,0]) alignment_socket();
    }
}

module single_winder(hand="right") { spine_part(hand=hand); }

// The complete center comes from dipole_center; this adapter only forwards
// the nesting Customizer settings and enables the shared strap option.
module configured_center() {
    center(terminal_d=terminal_hole_d, wire_d=wire_hole_d,
           hang_d=hang_hole_d, wire_positions=wire_positions,
           chamfer=wire_chamfer, bnc_fit=bnc_clearance,
           terminal_offset=terminal_hole_x, with_strap_slots=true,
           slot_width=strap_slot_width, slot_thickness=strap_slot_thickness);
}

module winder_pose(row=1,lift=0) {
    if(row==1) translate([0,-native_dock_y,0]) children();
    // Face the two stud-bearing surfaces inward. X stays fixed while the
    // winding bay moves to the other side of the spine and the stud points down.
    else translate([0,native_dock_y,2*frame_t+lift]) rotate([180,0,0]) children();
}

module placed_winder(row=1,lift=0) {
    winder_pose(row,lift) single_winder(hand=row==1 ? "right" : "left");
}

module center_pose(lift=0) {
    translate([center_pack_x,center_pack_y,center_pack_z+lift]) rotate([0,0,90])
        translate([0,-center_bar_y,0]) children();
}

module placed_center(lift=0) { center_pose(lift) configured_center(); }

module wire_envelope(row=1) {
    winder_pose(row) translate([winder_bounds[0][0]-wire_edge_bulge,
        -wire_edge_bulge,-face_bulge])
        cube([winder_bounds[1][0]-winder_bounds[0][0]+2*wire_edge_bulge,
            winder_bounds[1][1]+2*wire_edge_bulge,frame_t+2*face_bulge]);
}

// Open U, with two independent ends through the center slots; no front loop.
// Schematic 12.7 x 2 mm strap. End foldbacks/overlap are not dimensioned.
module rear_strap() {
    // Leave 1 mm below the independent coil tie's button for this 2 mm strip.
    z_bottom=-max(face_bulge,post_protrusion)-6;
    z_top=center_pack_z+center_plate_t+2;
    strap_x=center_pack_x-(strap_slot_y-center_bar_y);
    outside_y=-native_dock_y+wing_length+wire_edge_bulge+2;
    for(side=[-1,1]) {
        slot_y=center_pack_y+side*strap_slot_x;
        // Ends through slots, then outward below the plate and above the coils.
        translate([strap_x-6.35,slot_y-1,center_pack_z-2])
            cube([12.7,2,z_top-center_pack_z+2]);
        translate([strap_x-6.35,min(slot_y,side*outside_y)-1,center_pack_z-2])
            cube([12.7,abs(side*outside_y-slot_y)+2,2]);
        translate([strap_x-6.35,side*outside_y-1,z_bottom])
            cube([12.7,2,center_pack_z-z_bottom]);
    }
    translate([strap_x-6.35,-outside_y-1,z_bottom])
        cube([12.7,2*outside_y+2,2]);
}

module alignment_coupon() {
    for(i=[0:1]) translate([0,18*i,0])
        spine_part(coupon=true,hand=i==0 ? "right" : "left");
}

module bnc_fit_coupon() {
    // Reuse the upright 3 mm shelf and D-hole profile at five labeled fits.
    coupon(diameters=[9.7,9.8,9.9,10.0,10.1]);
}

module bnc_fit_coupon_tight() {
    // Retain 9.7 as a control; explore the 3/8-inch (9.525 mm) thread size.
    coupon(diameters=[9.5,9.55,9.6,9.65,9.7]);
}

module print_layout() {
    for(i=[0:1]) translate([0,i*(profile_height+layout_gap)-print_min_y,0])
        single_winder(hand=i==0 ? "right" : "left");
    translate([0,2*(profile_height+layout_gap)+0.5,0]) configured_center();
}

if(part=="center") configured_center();
else if(part=="winder") single_winder(hand=winder_hand);
else if(part=="winder_left") single_winder(hand="left");
else if(part=="winder_right") single_winder(hand="right");
else if(part=="print_layout") print_layout();
else if(part=="bnc_fit_coupon") bnc_fit_coupon();
else if(part=="bnc_fit_coupon_tight") bnc_fit_coupon_tight();
else if(part=="fit_coupon") alignment_coupon();
else if(part=="wire_envelopes") for(row=[-1,1]) wire_envelope(row);
else {
    exploded=part=="exploded";
    if(part!="winders") color([0.90,0.48,0.20]) placed_center(lift=exploded ? 38 : 0);
    for(row=[-1,1]) color(row==1 ? [0.15,0.57,0.71] : [0.35,0.66,0.45])
        placed_winder(row,lift=exploded && row==-1 ? 18 : 0);
    if($preview && show_wire) for(row=[-1,1])
        %color([0.85,0.15,0.18,0.15]) wire_envelope(row);
}
