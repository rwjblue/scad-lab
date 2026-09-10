/*
  N1RWJ mirrored dipole winder — A5 ergonomic revision, 2026-09-09.
  Units: mm. Default export is PRINT orientation: broad back at Z=0.
  In service +Y is up, +Z is forward, and the BNC mates toward -Y.
  Frame: 75 W x 140 H x 5 thick. Default overall depth: 24.

  K6ARK source-derived profile by Adam Kimmerly; see NOTICE.md.
  reference_profile.scad embeds the measured outline: no external STL needed.
  Default horns match the source; arm length moves tips along their sweep.

  Three chamfered wire holes per arm; direct solder to the BNC cup/tag.
  No M3 terminals. Thread wire through the relief before soldering.
  Owned connector: Amphenol RF 31-221-RFX, 9.70 mm D-hole,
  8.85 mm flat-to-opposite edge, maximum panel thickness 3.30 mm.
  The 12 mm rear projection is an estimate; adjust to the actual stack.
*/

use <reference_profile.scad>
use <frame_bevel.scad>

/* [Output] */
part = "winder"; // [winder,coupon,relief_coupon,frame]
show_hardware = false; // Translucent reference in F5 only; never in an STL

/* [Winder] */
// Horizontal reach from the centerline to each wing tip; tips keep their radii.
arm_length = 37.5; // [35:0.5:55]
frame_t = 5; // [4:0.5:7]
// Bevel on both broad faces, including the retained window rims.
frame_edge_bevel = 0.5; // [0:0.1:0.5]
close_snag_windows = true; // Fill five tiny openings; retain six larger windows

/* [Wire strain relief] */
// Center-to-center distance along the arm. Longer rows may need longer arms.
relief_pitch = 7; // [6.5:0.5:12]
// X position of the innermost hole; its Y position follows the native sweep.
relief_start_x = 20; // [17:0.5:24]
wire_hole_d = 3.2; // [2:0.1:4]
// Chamfer depth at each face. Check the actual insulated wire diameter.
wire_chamfer = 0.5; // [0:0.1:1]

/* [Hoisting eye] */
hang_hole_d = 6.0; // [3:0.5:8]
hang_chamfer = 0.5; // [0:0.1:1]
eye_y = 63; // [60:0.5:65]

/* [BNC cutout] */
// Finished cutout diameter, including print allowance. Nominal hardware: 9.7.
bnc_hole_d = 10.1; // [9.7:0.05:10.2]
// Cap removed from the circle: flat-to-opposite = diameter minus this depth.
// Zero makes a round hole. The owned connector's nominal cap depth is 0.85.
bnc_flat_depth = 0.85; // [0:0.05:1.2]
shelf_t = 3.0; // [2.8:0.1:3.3]

/* [Connector position and support] */
// Installed rear projection above the shelf; 12 mm is still an estimate.
bnc_rear_projection = 12.0; // [8:0.5:16]
bnc_axis_from_frame = 10.0; // [10:0.5:14]
// Reserved diameter for hardware and access, also sets shelf depth.
hardware_keepout_d = 18; // [16:0.5:20]
shelf_w = 26; // [24:1:32]
rib_t = 3; // [2.5:0.5:4]
rib_run = 10; // [8:1:14]

/* [Hidden] */
$fn = 96;
eps = 0.02;
arm_extension = arm_length-37.5;
relief_sweep = reference_arm_sweep(1);
relief_inner = [relief_start_x,
    55.050156773381225+(relief_start_x-20)*tan(relief_sweep)];
bnc_z = frame_t+bnc_axis_from_frame;
hardware_keepout_r = hardware_keepout_d/2;
shelf_depth = bnc_z+hardware_keepout_r;
contact_y = relief_inner[1];
shelf_top_y = contact_y-bnc_rear_projection;
shelf_bottom_y = shelf_top_y-shelf_t;
rib_x = hardware_keepout_r+rib_t/2;
rib_rise = bnc_axis_from_frame;
root_ramp = 2;
outline_points = reference_points(arm_extension);
outline_paths = reference_paths(close_snag_windows);

function relief_center(i, side=1) =
    [side*(relief_inner[0]+i*relief_pitch*cos(relief_sweep)),
     relief_inner[1]+i*relief_pitch*sin(relief_sweep)];

function clamp(value, low, high) = min(high,max(low,value));
function segment_distance(p,a,b) =
    let(v=b-a, t=clamp(((p-a)*v)/(v*v),0,1)) norm(p-(a+t*v));
function inside_ring(p,path) = len([
    for(i=[0:len(path)-1])
        let(a=outline_points[path[i]], b=outline_points[path[(i+1)%len(path)]])
        if((a[1]>p[1]) != (b[1]>p[1]))
            if(p[0] < a[0]+(p[1]-a[1])*(b[0]-a[0])/(b[1]-a[1])) 1
    ]) % 2 == 1;
function inside_frame(p) = inside_ring(p,outline_paths[0]) &&
    len([for(i=[1:len(outline_paths)-1]) if(inside_ring(p,outline_paths[i])) 1]) == 0;
function contour_distance(p) = min([
    for(path=outline_paths, i=[0:len(path)-1])
        segment_distance(p,outline_points[path[i]],outline_points[path[(i+1)%len(path)]])
    ]);
// Allow for both the hole mouth and the retreat of the frame's face bevel.
function face_ligament(p,d,chamfer) = contour_distance(p)-d/2-chamfer-frame_edge_bevel;

assert(part == "winder" || part == "coupon" || part == "relief_coupon" || part == "frame", "Unknown part");
assert(arm_length >= 35 && arm_length <= 55, "Use 35–55 mm center-to-tip arm reach");
assert(frame_t >= 4 && frame_t <= 7, "Use a 4–7 mm frame thickness");
assert(relief_pitch >= 6.5 && relief_pitch <= 12, "Use 6.5–12 mm relief pitch");
assert(relief_start_x >= 17 && relief_start_x <= 24, "Use 17–24 mm for the inner hole's X position");
assert(bnc_hole_d >= 9.7 && bnc_hole_d <= 10.2, "Use a 9.7–10.2 mm BNC cutout for this connector");
assert(bnc_flat_depth >= 0 && bnc_flat_depth <= 1.2, "Use 0–1.2 mm BNC flat depth; zero is round");
assert(shelf_t >= 2.8 && shelf_t <= 3.3, "Connector panel must be 2.8–3.3 mm");
assert(shelf_w >= 24 && shelf_w <= 32, "Use a 24–32 mm shelf width");
assert(bnc_rear_projection >= 8 && bnc_rear_projection <= 16, "Rear projection outside head layout");
assert(bnc_axis_from_frame >= 10 && bnc_axis_from_frame <= 14, "Use 10–14 mm axis distance from the frame");
assert(hardware_keepout_d >= 16 && hardware_keepout_d <= 20, "Use a 16–20 mm hardware envelope");
assert(rib_t >= 2.5 && rib_t <= 4 && rib_run >= 8 && rib_run <= 14, "Use 2.5–4 mm rib thickness and 8–14 mm run");
assert(wire_hole_d >= 2 && wire_hole_d <= 4, "Use 2–4 mm wire holes");
assert(wire_chamfer >= 0 && wire_chamfer <= 1, "Use 0–1 mm wire chamfers");
assert(hang_hole_d >= 3 && hang_hole_d <= 8, "Use a 3–8 mm hoisting hole");
assert(hang_chamfer >= 0 && hang_chamfer <= 1, "Use 0–1 mm hoisting chamfers");
assert(eye_y >= 60 && eye_y <= 65, "Keep the hoisting eye between Y60 and Y65");
assert(frame_edge_bevel >= 0 && frame_edge_bevel <= 0.5, "Keep edge bevel at 0–0.5 mm");
assert(2*max(wire_chamfer,hang_chamfer,frame_edge_bevel) < frame_t,
       "Chamfers and bevels must leave a straight bore and full-thickness middle band");
assert(relief_pitch-wire_hole_d-2*wire_chamfer >= 2,
       "Keep at least 2 mm between wire-hole mouths: increase pitch or reduce hole/chamfer size");
assert(bnc_z-hardware_keepout_r-frame_t >= 1,
       "Increase BNC axis distance to leave 1 mm behind the hardware envelope");
assert(shelf_w >= hardware_keepout_d+2*rib_t+2,
       "Widen the shelf for the hardware envelope and ribs (diameter + 2*rib thickness + 2 mm)");
assert(hardware_keepout_r-bnc_hole_d/2+bnc_flat_depth >= 3,
       "Keep at least 3 mm above the BNC cutout");
assert(shelf_bottom_y-rib_run >= 25, "Shorten ribs or raise the shelf to attach to the filled upper frame");
assert(eye_y-hang_hole_d/2-hang_chamfer-contact_y >= 2,
       "Keep 2 mm between the hoisting-hole mouth and the estimated BNC contact height");
for(side=[-1,1], i=[0:2]) {
    p = relief_center(i,side);
    assert(inside_frame(p) && face_ligament(p,wire_hole_d,wire_chamfer) >= 2,
           str("Relief hole ",i+1," needs 2 mm to the beveled frame/window edge: lengthen arms, shorten the row, or reduce hole/chamfer size"));
}
assert(inside_frame([0,eye_y]) && face_ligament([0,eye_y],hang_hole_d,hang_chamfer) >= 2,
       "Hoisting hole needs 2 mm to the beveled edge: reduce hole/chamfer size or move the eye inward");

module plate_hole(d, chamfer) {
    translate([0,0,-eps]) cylinder(d=d,h=frame_t+2*eps);
    translate([0,0,-eps])
        cylinder(d1=d+2*(chamfer+eps),d2=d,h=chamfer+eps);
    translate([0,0,frame_t-chamfer])
        cylinder(d1=d,d2=d+2*(chamfer+eps),h=chamfer+eps);
}

module frame_outline() {
    reference_frame_2d(fill_small_windows=close_snag_windows,arm_extension=arm_extension);
}

module frame() {
    difference() {
        beveled_frame(height=frame_t,bevel=frame_edge_bevel) frame_outline();
        translate([0,eye_y,0]) plate_hole(hang_hole_d,hang_chamfer);
        for(side=[-1,1], i=[0:2]) {
            p = relief_center(i,side);
            translate([p[0],p[1],0]) plate_hole(wire_hole_d,wire_chamfer);
        }
    }
}

// Map an X/Z profile into a solid extruded toward +Y.
module extrude_y(thickness) {
    rotate([-90,0,0]) linear_extrude(height=thickness,convexity=10)
        mirror([0,1,0]) children();
}

module bnc_d_profile(diameter=bnc_hole_d) {
    // Top flat gives a short printable bridge: approximately 5.61 mm by default.
    intersection() {
        circle(d=diameter);
        translate([-20,-20]) square([40,20+diameter/2-bnc_flat_depth]);
    }
}

module shelf_profile(width=shelf_w) {
    polygon([[-width/2,0],[width/2,0],
             [width/2,shelf_depth-2],[width/2-2,shelf_depth],
             [-width/2+2,shelf_depth],[-width/2,shelf_depth-2]]);
}

module shelf() {
    translate([0,shelf_bottom_y,0]) difference() {
        extrude_y(shelf_t) shelf_profile();
        translate([0,-eps,bnc_z]) extrude_y(shelf_t+2*eps)
            bnc_d_profile();
    }
}

// Cross-section coordinates are [Y,Z]; extrusion runs in X.
module extrude_x(thickness) {
    multmatrix([[0,0,1,0],[1,0,0,0],[0,1,0,0],[0,0,0,1]])
        linear_extrude(height=thickness) children();
}

module reinforcement() {
    // Start inside the unchanged middle band, so the front-face bevel cannot
    // leave the rib/heel bases suspended over an inset preceding layer.
    base_z = frame_t-frame_edge_bevel-eps;
    difference() {
        intersection() {
            // Every rib/heel layer starts over the native footprint; avoid a
            // 1.3 mm unsupported heel lip beside the narrowing spine.
            linear_extrude(height=shelf_depth,convexity=30) frame_outline();
            union() {
                // Flanking ribs BELOW the shelf, not across the connector axis.
                for(x=[-rib_x,rib_x])
                    translate([x-rib_t/2,0,0]) extrude_x(rib_t)
                        polygon([[shelf_bottom_y+eps,base_z],
                                 [shelf_bottom_y-rib_run,base_z],
                                 [shelf_bottom_y+eps,frame_t+rib_rise]]);
                // Continuous heel; the keepout below trims its central part.
                translate([-shelf_w/2,0,0]) extrude_x(shelf_w)
                    polygon([[shelf_bottom_y+eps,base_z],
                             [shelf_bottom_y-root_ramp,base_z],
                             [shelf_bottom_y+eps,frame_t+root_ramp]]);
            }
        }
        // Circumscribed facets protect the entire nominal circular envelope.
        // Only NEW reinforcement is cut, never the shelf's mounting annulus.
        translate([0,shelf_bottom_y-rib_run-eps,bnc_z])
            extrude_y(rib_run+2*eps)
                circle(r=hardware_keepout_r/cos(180/$fn));
    }
}

module winder() {
    union() {
        frame();
        shelf();
        reinforcement();
    }
}

module fit_coupon() {
    // Same upright D-hole, shelf thickness, and print orientation as the part.
    // Left to right: selected diameter minus 0.4, minus 0.2, and selected size.
    // Defaults remain 9.7, 9.9, and 10.1 mm; all share the selected flat depth.
    difference() {
        union() {
            translate([-33,0,0]) cube([66,8,frame_t]);
            for(x=[-22,0,22]) translate([x,0,0])
                extrude_y(shelf_t) shelf_profile(18);
        }
        for(i=[0:2]) {
            translate([(i-1)*22,-eps,bnc_z])
                extrude_y(shelf_t+2*eps) bnc_d_profile(bnc_hole_d-0.4+i*0.2);
            translate([(i-1)*22,-eps,frame_t+1.8]) extrude_y(0.4+eps)
                text(str(bnc_hole_d-0.4+i*0.2),size=2.5,font="Liberation Sans",
                     halign="center",valign="center");
        }
    }
}

module relief_coupon() {
    // A literal upper-arm section: same holes, edge bevel and wire-bearing edge.
    // The two straight crop edges are held by hand, not used to anchor the wire.
    // Follow longer tips and shifted relief rows without scaling the sample.
    crop_x = min(12,relief_inner[0]-8);
    crop_y = min(48,relief_inner[1]-7);
    crop_top = max(72,max([for(p=outline_points) p[1]])+2);
    crop_right = max(40,arm_length+2.5);
    translate([-crop_x,-crop_y,0]) intersection() {
        frame();
        translate([crop_x,crop_y,-eps])
            cube([crop_right-crop_x,crop_top-crop_y,frame_t+2*eps]);
    }
}

module hardware_reference() {
    // Schematic only: body, barrel, rear pin and reserved mounting stack.
    // Tag points away from the frame. Lug width/hole and wire paths illustrate
    // orientation, not a fit-verified manufacturer model or fixed wire lengths.
    color([0.65,0.70,0.72,0.6]) {
        translate([0,shelf_bottom_y-11.9,bnc_z])
            extrude_y(11.9) circle(d=12.7);
        translate([0,shelf_top_y,bnc_z]) extrude_y(7) circle(d=9.7);
        translate([0,shelf_top_y+7,bnc_z])
            extrude_y(max(0.1,bnc_rear_projection-7)) circle(d=2);
    }
    color([0.2,0.7,0.8,0.3])
        translate([0,shelf_top_y,bnc_z]) extrude_y(3)
            difference() { circle(d=hardware_keepout_d); circle(d=9.7); }
    color([0.75,0.75,0.7,0.85])
        translate([0,shelf_top_y+0.4,bnc_z]) extrude_y(0.5)
            difference() {
                hull() {
                    circle(d=12.7);
                    translate([0,12.7]) circle(d=4.8);
                }
                circle(d=9.7);
                translate([0,12.7]) circle(d=2.5);
            }
    color([0.8,0.15,0.08,0.85])
        relaxed_lead([relief_inner[0],contact_y,frame_t+0.5], [12,contact_y-3,bnc_z-5],
                     [5,contact_y+3,bnc_z+1], [0,contact_y,bnc_z]);
    color([0.12,0.25,0.55,0.85])
        relaxed_lead([-relief_inner[0],contact_y,frame_t+0.5], [-12,contact_y-3,bnc_z-2],
                     [-7,shelf_top_y+6,bnc_z+7], [0,shelf_top_y+0.7,bnc_z+12.7]);
}

module relaxed_lead(a,b,c,d) {
    function point(t) = (1-t)*(1-t)*(1-t)*a + 3*(1-t)*(1-t)*t*b
                       + 3*(1-t)*t*t*c + t*t*t*d;
    for(i=[0:15]) hull() {
        translate(point(i/16)) sphere(d=1,$fn=12);
        translate(point((i+1)/16)) sphere(d=1,$fn=12);
    }
}

if(part == "coupon") fit_coupon();
else if(part == "relief_coupon") relief_coupon();
else if(part == "frame") frame();
else {
    color([0.85,0.46,0.24]) winder();
    if(show_hardware && $preview) %hardware_reference();
}
