/*
  N1RWJ dipole center - 2026-09-09
  Imported from the ChatGPT-generated linked_dipole_center_v2 prototype.
  Original print succeeded; wider wire spacing and revised root are untested.
  Units: millimetres. No imported third-party mesh.

  Default export is already in PRINT orientation: broad back flat on bed.
  In service +Y is up; the BNC mating end points toward -Y (down).
  Main plate: 90 W x 39 H x 4 thick; overall printed depth: 23.
  Two M3 terminals; three horizontally aligned wire holes on each side.
  Each wire-hole group is 10 mm farther out than the original prototype,
  leaving 18 mm from the terminal post to the innermost wire-hole center.
  Panduit P22-6R-M maximum ring-center-to-barrel-entry length is 11.176 mm;
  the default layout leaves 4.724 mm from the barrel end to the hole chamfer.
  No toroid housing. Use a separate feedpoint choke.

  The original shelf/backplate already formed one fused solid. The reported
  exterior line coincides with the plate ending at Z=4, not a modeled crack.
  The internal root ramp reinforces the joint; it is not a proven cure for
  layer-transition marks. An 18 mm hardware keepout protects the BNC space.

  Connector: Amphenol RF 31-221-RFX.
  Drawing B6351D4-ND3G-50, rev L:
  https://www.amphenolrf.com/en-us/assets/file/4065787961/
  Nominal cutout: D=9.70; flat to opposite edge=8.85.
  Maximum panel thickness=3.30. BNC shelf is 3.00, independent of backplate.
  +0.10 mm PER SIDE fit allowance gives D=9.90 / flat-to-edge=9.05.
  Flat is at TOP of the hole in print orientation, creating a short bridge.
  Print the upright fit coupon first, with the same material/profile.

  Copyright (c) 2026 Robert Jackson (N1RWJ).
  License: CC BY-NC-SA 4.0 (Attribution-NonCommercial-ShareAlike).
  https://creativecommons.org/licenses/by-nc-sa/4.0/
  No physical load rating, weatherproofing claim or RF power rating is made.
*/

/* [Output] */
part = "center"; // [center,coupon,operating]

/* [Fits] */
bnc_clearance = 0.10; // Extra clearance per side; coupon tests 0, 0.10, 0.20
terminal_hole_d = 3.4; // M3 clearance, not a printed thread
wire_hole_d = 3.2; // For small insulated antenna wire; check jacket diameter
hang_hole_d = 6.0;

/* [Structure] */
plate_t = 4.0;
shelf_t = 3.0; // Do not exceed 3.3 mm for this connector
wire_chamfer = 0.5;
root_ramp = 2.0; // Internal 45-degree root reinforcement; 0 disables the ramp

/* [Hidden] */
$fn = 96;
eps = 0.02;
bar_y = 21;
terminal_x = 10;
wire_x = [28, 33.5, 39];
bar_w = 90;
hang_y = 32;
shelf_w = 26;
shelf_depth = 23;
bnc_z = 14;
rib_x = 10.5;
rib_t = 3;
bnc_hardware_keepout_r = rib_x-rib_t/2; // Preserve original 18 mm clear circle
minimum_wire_face_web = 1.2;
panduit_terminal_reach_max = (0.42+0.02)*25.4; // Drawing N41227BB-DC, M maximum
minimum_wire_entry_gap = 4.0; // Prototype wire-bend allowance; verify physically

assert(part == "center" || part == "coupon" || part == "operating", "Unknown part");
assert(plate_t >= 3.6 && plate_t <= 4.4, "Use a 3.6-4.4 mm backplate");
assert(shelf_t >= 2.8 && shelf_t <= 3.3, "BNC panel must be 2.8-3.3 mm");
assert(bnc_clearance >= 0 && bnc_clearance <= 0.25, "BNC clearance out of range");
assert(terminal_hole_d >= 3.1 && terminal_hole_d <= 3.6, "This layout is for M3 terminals");
assert(wire_hole_d >= 2.6 && wire_hole_d <= 3.6, "Wire holes too small or weaken the webs");
assert(hang_hole_d >= 4 && hang_hole_d <= 6, "Keep the suspension eye 4-6 mm");
assert(wire_chamfer >= 0 && wire_chamfer <= 0.6, "Keep chamfer at 0-0.6 mm");
assert(root_ramp >= 0 && root_ramp <= 2, "Keep root reinforcement at 0-2 mm");
assert(wire_x[0]-terminal_x-wire_hole_d/2-wire_chamfer-panduit_terminal_reach_max
       >= minimum_wire_entry_gap,
       "Leave at least 4 mm between the Panduit barrel entry and wire-hole chamfer");
for(i=[0:len(wire_x)-2])
    assert(wire_x[i+1]-wire_x[i]-wire_hole_d-2*wire_chamfer >= minimum_wire_face_web,
           "Wire holes and chamfers must leave at least 1.2 mm between faces");

module rounded_rect(w,h,r) {
    offset(r=r) square([w-2*r,h-2*r], center=true);
}

module back_outline() {
    union() {
        // Horizontal wire/terminal bar: y=15..27, x=-45..45.
        // Preserve the original 6 mm from outer wire-hole center to bar end.
        translate([0,bar_y]) rounded_rect(bar_w,12,5);
        // Center tongue for shelf and reinforcing ribs: y=0..25.
        translate([0,12.5]) rounded_rect(26,25,1.5);
        // Suspension eye with a broad neck; uppermost point y=39.
        hull() {
            translate([-7,25]) circle(r=5);
            translate([ 7,25]) circle(r=5);
            translate([0,hang_y]) circle(r=7);
        }
    }
}

module round_plate_hole(d, chamfer=0) {
    translate([0,0,-eps]) cylinder(d=d, h=plate_t+2*eps);
    if(chamfer > 0) {
        translate([0,0,-eps])
            cylinder(d1=d+2*(chamfer+eps),d2=d,h=chamfer+eps);
        translate([0,0,plate_t-chamfer])
            cylinder(d1=d,d2=d+2*(chamfer+eps),h=chamfer+eps);
    }
}

module backplate() {
    difference() {
        linear_extrude(height=plate_t) back_outline();
        translate([0,hang_y,0]) round_plate_hole(hang_hole_d,wire_chamfer);
        for(s=[-1,1]) {
            translate([s*terminal_x,bar_y,0]) round_plate_hole(terminal_hole_d);
            for(x=wire_x)
                translate([s*x,bar_y,0]) round_plate_hole(wire_hole_d,wire_chamfer);
        }
    }
}

// Maps a 2-D X/Z profile into a solid extruded from y=0 toward +Y.
module extrude_toward_y(thickness) {
    rotate([-90,0,0]) linear_extrude(height=thickness)
        mirror([0,1,0]) children();
}

module shelf_outline() {
    // Chamfered outer corners; square bottom fuses into the backplate.
    polygon([[-shelf_w/2,0],[shelf_w/2,0],
             [shelf_w/2,shelf_depth-2],[shelf_w/2-2,shelf_depth],
             [-shelf_w/2+2,shelf_depth],[-shelf_w/2,shelf_depth-2]]);
}

module bnc_d_profile(clearance) {
    // Nominal radius 4.85, TOP flat at +4.00.
    // Rotated 180 degrees relative to the drawing's illustrated flat.
    intersection() {
        circle(r=4.85+clearance);
        translate([-20,-20]) square([40,24.00+clearance]);
    }
}

module bnc_hole(clearance,thickness=shelf_t) {
    translate([0,-eps,bnc_z])
        extrude_toward_y(thickness+2*eps) bnc_d_profile(clearance);
}

module shelf() {
    difference() {
        extrude_toward_y(shelf_t) shelf_outline();
        bnc_hole(bnc_clearance);
    }
}

module rib_at(x) {
    // Polygon coordinates are [Y,Z], extruded 3 mm in X.
    // Overlap shelf/backplate slightly so the union is a single solid.
    translate([x-rib_t/2,0,0])
        multmatrix([[0,0,1,0],[1,0,0,0],[0,1,0,0],[0,0,0,1]])
            linear_extrude(height=rib_t)
                polygon([[shelf_t-eps,plate_t-eps],
                         [13,plate_t-eps],
                         [shelf_t-eps,14]]);
}

module shelf_root() {
    if(root_ramp > 0) {
        difference() {
            // Add material only to the inside corner. Overlap the existing
            // shelf and plate so even a small ramp is volumetrically joined.
            translate([-shelf_w/2,0,0])
                multmatrix([[0,0,1,0],[1,0,0,0],[0,1,0,0],[0,0,0,1]])
                    linear_extrude(height=shelf_w)
                        polygon([[shelf_t-eps,plate_t-eps],
                                 [shelf_t+root_ramp,plate_t-eps],
                                 [shelf_t-eps,plate_t+root_ramp]]);

            // Cut the hardware envelope out of the NEW ramp only. The
            // original shelf, 3 mm mounting annulus and ribs stay intact.
            // Circumscribe the keepout polygon so its facets cannot intrude
            // inside the nominal clearance circle.
            translate([0,-eps,bnc_z])
                extrude_toward_y(shelf_t+root_ramp+2*eps)
                    circle(r=bnc_hardware_keepout_r/cos(180/$fn));
        }
    }
}

module center() {
    union() {
        backplate();
        shelf();
        for(x=[-rib_x,rib_x]) rib_at(x);
        shelf_root();
    }
}

module coupon() {
    // Upright D-holes reproduce the final shelf's orientation and thickness.
    // Left-to-right: nominal 9.7, default 9.9, loose 10.1.
    // Each tab is attached to a common foot. No supports intended.
    diameters=[9.7,9.9,10.1];
    clearances=[0,0.10,0.20];
    difference() {
        union() {
            translate([0,4,0]) linear_extrude(height=plate_t) rounded_rect(66,8,1);
            for(x=[-22,0,22])
                translate([x,0,0]) extrude_toward_y(shelf_t)
                    polygon([[-9,0],[9,0],[9,shelf_depth-2],
                             [7,shelf_depth],[-7,shelf_depth],[-9,shelf_depth-2]]);
        }
        for(i=[0:2]) {
            translate([(i-1)*22,0,0]) bnc_hole(clearances[i]);
            // Debossed on front face, below each hole.
            translate([(i-1)*22,-eps,6.6]) extrude_toward_y(0.4+eps)
                text(str(diameters[i]),size=2.5,font="Liberation Sans",
                     halign="center",valign="center");
        }
    }
}

if(part == "coupon") coupon();
else if(part == "operating") rotate([90,0,0]) center();
else center();
