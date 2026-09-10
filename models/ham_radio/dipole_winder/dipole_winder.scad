/*
  N1RWJ mirrored dipole winder — accepted A5 layout, 2026-09-09.
  Units: mm. Default export is PRINT orientation: broad back at Z=0.
  In service +Y is up, +Z is forward, and the BNC mates toward -Y.
  Frame: 75 W x 140 H x 5 thick. Default overall depth: 24.

  K6ARK source-derived profile by Adam Kimmerly; see NOTICE.md.
  reference_profile.scad embeds the measured outline: no external STL needed.
  The source horns remain at scale 1 in their original positions.

  Three chamfered wire holes per arm; direct solder to the BNC cup/tag.
  No M3 terminals. Thread wire through the relief before soldering.
  Owned connector: Amphenol RF 31-221-RFX, 9.70 mm D-hole,
  8.85 mm flat-to-opposite edge, maximum panel thickness 3.30 mm.
  The 12 mm rear projection is an estimate; adjust to the actual stack.
*/

use <reference_profile.scad>

/* [Output] */
part = "winder"; // [winder,coupon,frame]
show_hardware = false; // Translucent reference in F5 only; never in an STL

/* [Fits] */
bnc_clearance = 0.10; // [0:0.05:0.25] Extra clearance PER SIDE
wire_hole_d = 3.2; // [2.6:0.1:3.6] Check actual insulated wire diameter
wire_chamfer = 0.5; // [0.2:0.1:0.6] 45-degree chamfer, both faces
hang_hole_d = 6.0; // [4:0.5:6]

/* [Connector position] */
bnc_rear_projection = 12.0; // [8:0.5:16] Measured above the installed panel
bnc_axis_from_frame = 10.0; // [10:0.5:14] Axis distance from the front face
shelf_t = 3.0; // [2.8:0.1:3.3] Independent of the 5 mm frame

/* [Hidden] */
$fn = 96;
eps = 0.02;
frame_t = 5;
eye_y = 63;
relief_pitch = 7;
relief_sweep = 26.40465549589185;
relief_inner = [20,55.050156773381225];
shelf_w = 26;
bnc_z = frame_t+bnc_axis_from_frame;
shelf_depth = bnc_z+9;
contact_y = relief_inner[1];
shelf_top_y = contact_y-bnc_rear_projection;
shelf_bottom_y = shelf_top_y-shelf_t;
hardware_keepout_r = 9;
rib_x = 10.5;
rib_t = 3;
rib_run = 10;
rib_rise = 10;
root_ramp = 2;

function relief_center(i, side=1) =
    [side*(relief_inner[0]+i*relief_pitch*cos(relief_sweep)),
     relief_inner[1]+i*relief_pitch*sin(relief_sweep)];

assert(part == "winder" || part == "coupon" || part == "frame", "Unknown part");
assert(bnc_clearance >= 0 && bnc_clearance <= 0.25, "Use 0–0.25 mm per-side allowance");
assert(shelf_t >= 2.8 && shelf_t <= 3.3, "Connector panel must be 2.8–3.3 mm");
assert(bnc_rear_projection >= 8 && bnc_rear_projection <= 16, "Rear projection outside head layout");
assert(bnc_axis_from_frame >= 10 && bnc_axis_from_frame <= 14, "Retain hardware-to-frame clearance");
assert(wire_hole_d >= 2.6 && wire_hole_d <= 3.6, "Use 2.6–3.6 mm wire holes");
assert(wire_chamfer >= 0.2 && wire_chamfer <= 0.6, "Use 0.2–0.6 mm wire chamfers");
assert(hang_hole_d >= 4 && hang_hole_d <= 6, "Keep the suspension eye 4–6 mm");
assert(relief_pitch-wire_hole_d-2*wire_chamfer >= 2, "Keep material between chamfer mouths");
assert(bnc_z-hardware_keepout_r-frame_t >= 1, "Keep 1 mm behind the hardware envelope");
assert(shelf_bottom_y-rib_run >= 25, "Ribs must attach to the filled upper frame");

module plate_hole(d, chamfer) {
    translate([0,0,-eps]) cylinder(d=d,h=frame_t+2*eps);
    translate([0,0,-eps])
        cylinder(d1=d+2*(chamfer+eps),d2=d,h=chamfer+eps);
    translate([0,0,frame_t-chamfer])
        cylinder(d1=d,d2=d+2*(chamfer+eps),h=chamfer+eps);
}

module frame() {
    difference() {
        linear_extrude(height=frame_t,convexity=30) reference_frame_2d();
        translate([0,eye_y,0]) plate_hole(hang_hole_d,wire_chamfer);
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

module bnc_d_profile(clearance) {
    // Top flat gives a short printable bridge: 5.55 mm at default clearance.
    intersection() {
        circle(r=4.85+clearance);
        translate([-20,-20]) square([40,24+clearance]);
    }
}

module shelf_profile(width=shelf_w) {
    polygon([[-width/2,0],[width/2,0],
             [width/2,shelf_depth-2],[width/2-2,shelf_depth],
             [-width/2+2,shelf_depth],[-width/2,shelf_depth-2]]);
}

module shelf(clearance=bnc_clearance) {
    translate([0,shelf_bottom_y,0]) difference() {
        extrude_y(shelf_t) shelf_profile();
        translate([0,-eps,bnc_z]) extrude_y(shelf_t+2*eps)
            bnc_d_profile(clearance);
    }
}

// Cross-section coordinates are [Y,Z]; extrusion runs in X.
module extrude_x(thickness) {
    multmatrix([[0,0,1,0],[1,0,0,0],[0,1,0,0],[0,0,0,1]])
        linear_extrude(height=thickness) children();
}

module reinforcement() {
    difference() {
        intersection() {
            // Every rib/heel layer starts over the native footprint; avoid a
            // 1.3 mm unsupported heel lip beside the narrowing spine.
            linear_extrude(height=shelf_depth,convexity=30) reference_frame_2d();
            union() {
                // Flanking ribs BELOW the shelf, not across the connector axis.
                for(x=[-rib_x,rib_x])
                    translate([x-rib_t/2,0,0]) extrude_x(rib_t)
                        polygon([[shelf_bottom_y+eps,frame_t-eps],
                                 [shelf_bottom_y-rib_run,frame_t-eps],
                                 [shelf_bottom_y+eps,frame_t+rib_rise]]);
                // Continuous heel; the keepout below trims its central part.
                translate([-shelf_w/2,0,0]) extrude_x(shelf_w)
                    polygon([[shelf_bottom_y+eps,frame_t-eps],
                             [shelf_bottom_y-root_ramp,frame_t-eps],
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
    // Left to right: nominal 9.7, default 9.9, loose 10.1 mm.
    difference() {
        union() {
            translate([-33,0,0]) cube([66,8,frame_t]);
            for(x=[-22,0,22]) translate([x,0,0])
                extrude_y(shelf_t) shelf_profile(18);
        }
        for(i=[0:2]) {
            translate([(i-1)*22,-eps,bnc_z])
                extrude_y(shelf_t+2*eps) bnc_d_profile(i*0.10);
            translate([(i-1)*22,-eps,6.8]) extrude_y(0.4+eps)
                text(str(9.7+i*0.2),size=2.5,font="Liberation Sans",
                     halign="center",valign="center");
        }
    }
}

module hardware_reference() {
    // Schematic only: body, barrel, rear pin and reserved mounting stack.
    // The actual shell tag must point away from the plate; it is not modeled.
    color([0.65,0.70,0.72,0.6]) {
        translate([0,shelf_bottom_y-11.9,bnc_z])
            extrude_y(11.9) circle(d=12.7);
        translate([0,shelf_top_y,bnc_z]) extrude_y(7) circle(d=9.7);
        translate([0,shelf_top_y+7,bnc_z])
            extrude_y(max(0.1,bnc_rear_projection-7)) circle(d=2);
    }
    color([0.2,0.7,0.8,0.3])
        translate([0,shelf_top_y,bnc_z]) extrude_y(3)
            difference() { circle(d=18); circle(d=9.7); }
}

if(part == "coupon") fit_coupon();
else if(part == "frame") frame();
else {
    color([0.85,0.46,0.24]) winder();
    if(show_hardware && $preview) %hardware_reference();
}
