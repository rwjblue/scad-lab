/*
  N1RWJ dipole center - 2026-09-09
  Imported from the ChatGPT-generated linked_dipole_center_v2 prototype.
  Original print succeeded; wider wire spacing and revised root are untested.
  Units: millimetres. No imported third-party mesh.

  Default export is already in PRINT orientation: broad back flat on bed.
  In service +Y is up; the BNC mating end points toward -Y (down).
  Main plate: 90 W x 39 H x 4 thick; overall printed depth: 23.
  Two M3 terminals; three horizontally aligned wire holes on each side.
  Optional inline strap slots share the nesting carrier's center geometry.
  Enabling them moves the terminal and wire groups inward together, keeping
  18 mm from the terminal post to the innermost wire-hole center.
  Panduit P22-6R-M maximum ring-center-to-barrel-entry length is 11.176 mm;
  the default layout leaves 4.724 mm from the barrel end to the hole chamfer.
  Optional balun mount extends the spine and adds four toroid tie slots.
  Balun mount and packing strap slots can be selected independently.
  Ferrite, winding and pads are separate hardware; no enclosure is printed.

  The original shelf/backplate already formed one fused solid. The reported
  exterior line coincides with the plate ending at Z=4, not a modeled crack.
  The internal root ramp reinforces the joint; it is not a proven cure for
  layer-transition marks. An 18 mm hardware keepout protects the BNC space.

  Connector: Amphenol RF 31-221-RFX.
  Drawing B6351D4-ND3G-50, rev L:
  https://www.amphenolrf.com/en-us/assets/file/4065787961/
  Nominal cutout: D=9.70; flat to opposite edge=8.85.
  Maximum panel thickness=3.30. BNC shelf is 3.00, independent of backplate.
  Selected printed fit: -0.10 mm PER SIDE gives D=9.50 / flat-to-edge=8.65.
  Flat is at TOP of the hole in print orientation, creating a short bridge.
  Print the upright fit coupon first, with the same material/profile.

  Copyright (c) 2026 Robert Jackson (N1RWJ).
  License: CC BY-NC-SA 4.0 (Attribution-NonCommercial-ShareAlike).
  https://creativecommons.org/licenses/by-nc-sa/4.0/
  No physical load rating, weatherproofing claim or RF power rating is made.
*/

/* [Output] */
part = "center"; // [center,coupon,operating,mount_coupon]

/* [Packing strap] */
// Enable the nesting carrier's inline strap slots and compact hole layout.
strap_slots = false;
strap_slot_width = 14; // [10:0.5:20] Length for a roughly half-inch strap
strap_slot_thickness = 3; // [2:0.5:4] Opening for the strap thickness

/* [Balun mount] */
balun_mount = false;
package_d = 34; // [32:1:38] Wound toroid OD, including protection
package_h = 18; // [16:1:22] Wound thickness; preview envelope only
pad_t = 1; // [0.5:0.5:2] Separate compliant pads, not printed
// Catalog nominal is about 12 mm above a 3 mm panel; reserve 13 mm.
bnc_rear_projection = 13; // [10:1:20] Installed hardware envelope above shelf
bnc_to_toroid_gap = 12; // [10:1:20] Free space beyond hardware envelope for input leads
toroid_to_post_gap = 20; // [20:1:28] Wound top to post center; includes downward ring barrel
show_fit_envelope = false; // F5 only; never included in the STL

/* [Fits] */
bnc_clearance = -0.10; // Per-side fit adjustment; selected 9.50 mm opening
terminal_hole_d = 3.4; // M3 clearance, not a printed thread
wire_hole_d = 3.2; // For small insulated antenna wire; check jacket diameter
// Automatic: 6 mm without strap slots, 8 mm with strap slots.
hang_hole_d = 0; // [0:Automatic,4:4 mm,4.5:4.5 mm,5:5 mm,5.5:5.5 mm,6:6 mm,6.5:6.5 mm,7:7 mm,7.5:7.5 mm,8:8 mm]

/* [Structure] */
plate_t = 4.0;
shelf_t = 3.0; // Do not exceed 3.3 mm for this connector
wire_chamfer = 0.5;
root_ramp = 2.0; // Internal 45-degree root reinforcement; 0 disables the ramp

/* [Hidden] */
$fn = 96;
eps = 0.02;
terminal_x = 10;
wire_x = [28, 33.5, 39];
bar_w = 90;
shelf_w = 26;
shelf_depth = 23;
bnc_z = 14;
rib_x = 10.5;
rib_t = 3;
bnc_hardware_keepout_r = rib_x-rib_t/2; // Preserve original 18 mm clear circle
minimum_wire_face_web = 1.2;
panduit_terminal_reach_max = (0.42+0.02)*25.4; // Drawing N41227BB-DC, M maximum
minimum_wire_entry_gap = 4.0; // Prototype wire-bend allowance; verify physically
strap_slot_x = 41;
tie_x = 5.5;
tie_slot_w = 3.4;
tie_slot_h = 2.4;
tie_chamfer = 0.3;

// Ties sit 4 mm outside the wound circle; keep routing space independent.
function lower_tie_y() = shelf_t+bnc_rear_projection+bnc_to_toroid_gap-4;
function toroid_y() = lower_tie_y()+4+package_d/2;
function terminal_bar_y(with_balun_mount) = with_balun_mount ? toroid_y()+package_d/2+toroid_to_post_gap : 21;


assert(plate_t >= 3.6 && plate_t <= 4.4, "Use a 3.6-4.4 mm backplate");
assert(shelf_t >= 2.8 && shelf_t <= 3.3, "BNC panel must be 2.8-3.3 mm");
assert(bnc_clearance >= -0.10 && bnc_clearance <= 0.25, "BNC clearance out of range");
assert(terminal_hole_d >= 3.1 && terminal_hole_d <= 3.6, "This layout is for M3 terminals");
assert(wire_hole_d >= 2.6 && wire_hole_d <= 3.6, "Wire holes too small or weaken the webs");
assert(hang_hole_d == 0 || (hang_hole_d >= 4 && hang_hole_d <= 8),
       "Suspension eye must be automatic (0) or 4-8 mm");
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

module back_outline(with_balun_mount=balun_mount) {
    bar_y=terminal_bar_y(with_balun_mount);
    hang_y=bar_y+11;
    union() {
        // Horizontal wire/terminal bar: x=-45..45; raised for the balun.
        // Preserve the original 6 mm from outer wire-hole center to bar end.
        translate([0,bar_y]) rounded_rect(bar_w,12,5);
        // Extend the tongue continuously to the raised terminal bar.
        translate([0,(bar_y+4)/2]) rounded_rect(26,bar_y+4,1.5);
        // Suspension eye with a broad neck follows the terminal bar.
        hull() {
            translate([-7,bar_y+4]) circle(r=5);
            translate([ 7,bar_y+4]) circle(r=5);
            translate([0,hang_y]) circle(r=7);
        }
    }
}

module tie_slot() {
    translate([-tie_slot_w/2,-tie_slot_h/2,-eps])
        cube([tie_slot_w,tie_slot_h,plate_t+2*eps]);
    // Small edge breaks protect nylon straps; no recessed backs to bridge.
    for(z=[0,plate_t-tie_chamfer])
        translate([0,0,z]) hull() {
            translate([-tie_slot_w/2,-tie_slot_h/2,
                       z==0 ? tie_chamfer : 0])
                cube([tie_slot_w,tie_slot_h,eps]);
            translate([-tie_slot_w/2-tie_chamfer,-tie_slot_h/2-tie_chamfer,
                       z==0 ? -eps : tie_chamfer])
                cube([tie_slot_w+2*tie_chamfer,tie_slot_h+2*tie_chamfer,eps]);
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

module strap_slot_2d(width, thickness) {
    offset(r=0.5) square([thickness-1,width-1],center=true);
}

module strap_bar_ends_2d(width, bar_y=21) {
    // End pads stay inside the 90 mm body and center the strap's pull on the bar.
    for(side=[-1,1]) translate([side*40,bar_y])
        offset(r=2) square([6,width+2],center=true);
}

// Explicit arguments let derived models move or shrink openings without
// retaining a second set of holes from this module's default configuration.
// Validate arguments here as imported module calls do not run top-level checks.
module plate_holes(terminal_d=terminal_hole_d, wire_d=wire_hole_d,
                   hang_d=hang_hole_d, wire_positions=undef,
                   chamfer=wire_chamfer, terminal_offset=undef,
                   with_strap_slots=strap_slots,
                   slot_width=strap_slot_width, slot_thickness=strap_slot_thickness,
                   with_balun_mount=balun_mount) {
    bar_y=terminal_bar_y(with_balun_mount);
    hang_y=bar_y+11;
    terminal_at=is_undef(terminal_offset) ? (with_strap_slots ? 7 : terminal_x) : terminal_offset;
    wires=is_undef(wire_positions) ? (with_strap_slots ? [25,30.5,36] : wire_x) : wire_positions;
    hang_diameter=hang_d==0 ? (with_strap_slots ? 8 : 6) : hang_d;
    assert(terminal_d >= 3.1 && terminal_d <= 3.6, "This layout is for M3 terminals");
    assert(wire_d >= 2.6 && wire_d <= 3.6, "Wire holes must be 2.6-3.6 mm");
    assert(hang_diameter >= 4 && hang_diameter <= 8, "Keep the suspension eye 4-8 mm");
    assert(chamfer >= 0 && chamfer <= 0.6, "Keep chamfer at 0-0.6 mm");
    assert(terminal_at >= 7 && terminal_at <= 10, "Terminal offset must be 7-10 mm");
    assert(len(wires) == 3, "Use three wire holes on each side");
    assert(wires[0]-terminal_at-wire_d/2-chamfer-panduit_terminal_reach_max
           >= minimum_wire_entry_gap,
           "Leave at least 4 mm between the Panduit barrel entry and wire-hole chamfer");
    for(i=[0:len(wires)-2])
        assert(wires[i+1]-wires[i]-wire_d-2*chamfer
               >= minimum_wire_face_web,
               "Wire holes and chamfers must leave at least 1.2 mm between faces");
    assert(wires[len(wires)-1]+wire_d/2+chamfer <= bar_w/2-3,
           "Leave at least 3 mm between the outer wire-hole mouth and the bar end");
    assert(7-hang_diameter/2-chamfer >= 2.4,
           "Keep at least 2.4 mm at the suspension-eye crown");
    if(with_strap_slots) {
        assert(slot_width >= 10 && slot_width <= 20, "Strap slot length must be 10-20 mm");
        assert(slot_thickness >= 2 && slot_thickness <= 4, "Strap slot thickness must be 2-4 mm");
        assert(strap_slot_x-slot_thickness/2-(wires[2]+wire_d/2+chamfer) >= 1.2,
               "Leave at least 1.2 mm between the outer wire-hole mouth and strap slot");
        assert(bar_w/2-strap_slot_x-slot_thickness/2 >= 2,
               "Leave at least 2 mm outside the strap slot");
    }

    if(with_balun_mount)
        for(x=[-tie_x,tie_x]) for(y=[lower_tie_y(),lower_tie_y()+8+package_d])
            translate([x,y,0]) tie_slot();
    translate([0,hang_y,0]) round_plate_hole(hang_diameter,chamfer);
    for(s=[-1,1]) {
        translate([s*terminal_at,bar_y,0]) round_plate_hole(terminal_d);
        for(x=wires)
            translate([s*x,bar_y,0]) round_plate_hole(wire_d,chamfer);
    }
}

module backplate(terminal_d=terminal_hole_d, wire_d=wire_hole_d,
                 hang_d=hang_hole_d, wire_positions=undef,
                 chamfer=wire_chamfer, terminal_offset=undef,
                 with_strap_slots=strap_slots,
                 slot_width=strap_slot_width, slot_thickness=strap_slot_thickness,
                   with_balun_mount=balun_mount) {
    bar_y=terminal_bar_y(with_balun_mount);
    difference() {
        linear_extrude(height=plate_t) union() {
            back_outline(with_balun_mount);
            if(with_strap_slots) strap_bar_ends_2d(slot_width,bar_y);
        }
        plate_holes(terminal_d=terminal_d, wire_d=wire_d, hang_d=hang_d,
                    wire_positions=wire_positions, chamfer=chamfer,
                    terminal_offset=terminal_offset, with_strap_slots=with_strap_slots,
                    slot_width=slot_width, slot_thickness=slot_thickness,
                    with_balun_mount=with_balun_mount);
        if(with_strap_slots) for(side=[-1,1]) translate([side*strap_slot_x,bar_y,-eps])
            linear_extrude(height=plate_t+2*eps) strap_slot_2d(slot_width,slot_thickness);
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

module shelf(clearance=bnc_clearance) {
    // Negative adjustment is an empirical printed fit below the nominal cutout.
    assert(clearance >= -0.10 && clearance <= 0.25, "BNC clearance out of range");
    difference() {
        extrude_toward_y(shelf_t) shelf_outline();
        bnc_hole(clearance);
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

module center(terminal_d=terminal_hole_d, wire_d=wire_hole_d,
              hang_d=hang_hole_d, wire_positions=undef,
              chamfer=wire_chamfer, bnc_fit=bnc_clearance,
              terminal_offset=undef, with_strap_slots=strap_slots,
              slot_width=strap_slot_width, slot_thickness=strap_slot_thickness,
                   with_balun_mount=balun_mount) {
    // Module-level checks also run for presets and models that import with use.
    if(with_balun_mount) {
        assert(package_d>=32 && package_d<=38,"Wound OD must be 32-38 mm");
        assert(package_h>=16 && package_h<=22,"Wound thickness must be 16-22 mm");
        assert(pad_t>=0.5 && pad_t<=2,"Use 0.5-2 mm separate pads");
        assert(bnc_rear_projection>=10 && bnc_rear_projection<=20,
               "Rear projection must be 10-20 mm; measured above shelf");
        assert(bnc_to_toroid_gap>=10 && bnc_to_toroid_gap<=20,
               "BNC wire gap must be 10-20 mm");
        assert(toroid_to_post_gap>=20 && toroid_to_post_gap<=28,
               "Toroid-to-post gap must be 20-28 mm");
        assert(toroid_to_post_gap-panduit_terminal_reach_max>=8,
               "Reserve at least 8 mm beyond a downward-facing winding ring");
        assert(lower_tie_y()-tie_slot_h/2-tie_chamfer-(shelf_t+bnc_rear_projection)>=3.49,
               "Reserve solder and tie-threading access above BNC");
    }
    union() {
        backplate(terminal_d=terminal_d, wire_d=wire_d, hang_d=hang_d,
                  wire_positions=wire_positions, chamfer=chamfer,
                  terminal_offset=terminal_offset, with_strap_slots=with_strap_slots,
                  slot_width=slot_width, slot_thickness=slot_thickness,
                    with_balun_mount=with_balun_mount);
        shelf(clearance=bnc_fit);
        for(x=[-rib_x,rib_x]) rib_at(x);
        shelf_root();
    }
    if(with_balun_mount && show_fit_envelope && $preview)
        %color([0.2,0.4,0.8,0.3]) translate([0,toroid_y(),plate_t+pad_t])
            cylinder(d=package_d,h=package_h);
}

module coupon(diameters=[9.7,9.9,10.1]) {
    // Upright D-holes reproduce the final shelf's orientation and thickness.
    // Legacy wider coupon, left-to-right: 9.7, 9.9, 10.1.
    // The nesting variant's tighter coupon includes the selected 9.5 mm fit.
    // Each tab is attached to a common foot. No supports intended.
    assert(len(diameters)>0,"Choose at least one BNC coupon diameter");
    for(d=diameters) assert(d>=9.5 && d<=10.2,"Coupon diameters must be 9.5..10.2 mm");
    stations=[for(i=[0:len(diameters)-1]) (i-(len(diameters)-1)/2)*22];
    difference() {
        union() {
            translate([0,4,0]) linear_extrude(height=plate_t)
                rounded_rect(len(diameters)*22,8,1);
            for(x=stations)
                translate([x,0,0]) extrude_toward_y(shelf_t)
                    polygon([[-9,0],[9,0],[9,shelf_depth-2],
                             [7,shelf_depth],[-7,shelf_depth],[-9,shelf_depth-2]]);
        }
        for(i=[0:len(diameters)-1]) {
            translate([stations[i],0,0]) bnc_hole((diameters[i]-9.7)/2);
            // Debossed on front face, below each hole.
            translate([stations[i],-eps,6.6]) extrude_toward_y(0.4+eps)
                text(str(diameters[i],diameters[i]==floor(diameters[i]) ? ".0" : ""),
                     size=2.5,font="Liberation Sans",
                     halign="center",valign="center");
        }
    }
}

module mount_coupon(with_balun_mount=balun_mount, with_strap_slots=strap_slots) {
    // Keep the exact shelf, central spine, terminals and any toroid ties.
    intersection() {
        center(with_balun_mount=with_balun_mount, with_strap_slots=with_strap_slots);
        translate([-13,-eps,-eps])
            cube([26,terminal_bar_y(with_balun_mount)+6+eps,shelf_depth+2*eps]);
    }
}

module dipole_center_part(output=part, with_balun_mount=balun_mount,
                          with_strap_slots=strap_slots,
                          coupon_diameters=[9.7,9.9,10.1]) {
    assert(output=="center" || output=="coupon" || output=="operating" || output=="mount_coupon",
           "Unknown part");
    if(output=="coupon") coupon(coupon_diameters);
    else if(output=="mount_coupon") mount_coupon(with_balun_mount,with_strap_slots);
    else if(output=="operating") rotate([90,0,0])
        center(with_balun_mount=with_balun_mount,with_strap_slots=with_strap_slots);
    else center(with_balun_mount=with_balun_mount,with_strap_slots=with_strap_slots);
}

dipole_center_part();
