/*
  models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad

  Parameterized BNC protective cap for the KO4HUI Spooltenna
  (Ultra v1.5/v1.6 primary, v1.3 stretch). Drops into the existing
  PCB slot at the bottom of the spool; held in place by the bongo tie.

  See docs/superpowers/specs/2026-05-12-spooltenna-bnc-cap-design.md
*/

$fn = 64;

// ---------------------------------------------------------------
// Model preset
// ---------------------------------------------------------------
//   "ULTRA_V1_6"  - Spooltenna Ultra v1.6 (default, identical to v1.5)
//   "ULTRA_V1_5"  - alias for ULTRA_V1_6
//   "V1_3"        - Spooltenna v1.3 (larger 120 mm disk)
model = "ULTRA_V1_6";

// ---------------------------------------------------------------
// Per-model geometry. Edit `model` above to switch presets.
// Override individual values below the preset block to customize.
// ---------------------------------------------------------------
preset_slot_width =
    (model == "V1_3")        ? 18.0  :
                               18.5;  // ULTRA_V1_5/V1_6

preset_slot_depth =
    (model == "V1_3")        ? 9.6   :
                               5.9;   // ULTRA_V1_5/V1_6

preset_disk_radius =
    (model == "V1_3")        ? 60.0  :
                               38.1;  // ULTRA_V1_5/V1_6

// All supported variants use the same horizontal Molex 73100 /
// Winconn 364A2x95 BNC family.
preset_bnc_protrusion =
    (model == "V1_3")        ? 5.0   :
                               8.5;

// ---------------------------------------------------------------
// Parameters (override per-print as needed)
// ---------------------------------------------------------------

// Stack
inter_pcb_gap   = 15.0;    // standoff length between the two PCBs

// Slot (resolved from preset)
slot_width      = preset_slot_width;
slot_depth      = preset_slot_depth;
disk_radius     = preset_disk_radius;

// BNC body (Molex 73100 / Winconn 364A2x95 family)
bnc_body_w      = 9.65;    // X (circumferential)
bnc_body_h      = 13.0;    // Z (axial height inside the inter-PCB gap)
bnc_protrusion  = preset_bnc_protrusion;

// Cap geometry
clearance       = 0.5;     // X per-side clearance; Z total clearance
wall            = 2.4;     // front wall (radial-outermost)
side_wall       = 2.5;     // circumferential side walls
lead_in_chamfer = 1.0;     // chamfer on radially-inward edges
front_air_gap   = 1.5;     // BNC tip to inside of front wall
pocket_x_clear  = 1.0;     // each-side clearance around BNC body in X

// Bongo tie groove
tie_groove_w    = 4.0;
tie_groove_d    = 1.5;

// ---------------------------------------------------------------
// Derived dimensions (do not edit; expressed for readability)
// ---------------------------------------------------------------

// Cap outer footprint (X = circumferential, Y = radial, Z = axial)
cap_x = slot_width - 2 * clearance;                         // 17.5 mm @ Ultra defaults
cap_z = inter_pcb_gap - clearance;                          // 14.5 mm @ 15 mm gap
cap_y = slot_depth + bnc_protrusion + front_air_gap + wall;  // 18.3 mm @ Ultra defaults
tie_groove_y = cap_y / 2;

// BNC pocket (interior cavity)
pocket_x = bnc_body_w + 2 * pocket_x_clear;  // 11.65 mm
pocket_y = cap_y - wall;                     // depth from inner face

// Sanity asserts (OpenSCAD will halt with these messages on bad params)
assert(cap_x > 0, "cap_x must be positive");
assert(cap_z > 0, "cap_z must be positive");
assert(cap_y > 0, "cap_y must be positive");
assert(pocket_x < cap_x - 2 * side_wall,
       "BNC pocket too wide for cap_x given side_wall");
assert(bnc_body_h < cap_z,
       "BNC body too tall for cap_z (axial)");
assert(pocket_y > slot_depth,
       "Pocket must reach past the slot into the body");

// ---------------------------------------------------------------
// Modules
// ---------------------------------------------------------------

// Solid outer block, before any cavities or chamfers.
// Centered: X on 0, Z on 0. Y=0 is the radially-inward (open) face.
module cap_solid() {
    translate([-cap_x / 2, 0, -cap_z / 2])
        cube([cap_x, cap_y, cap_z]);
}

// BNC pocket: a rectangular cavity that opens on the radially-inward
// face (Y = 0), extends Y forward to within `wall` of the front face,
// and cuts fully through Z so the PCB faces act as the axial walls.
// Centered on X.
module bnc_pocket() {
    eps = 0.01;  // overlap into the open face so the boolean is clean
    translate([-pocket_x / 2, -eps, -cap_z / 2 - eps])
        cube([pocket_x, pocket_y + eps, cap_z + 2 * eps]);
}

// Bongo tie groove: circular-segment channel across the front Y face,
// running across X from prong to prong.
module tie_groove() {
    eps = 0.01;
    r = tie_groove_w / 2;
    translate([-cap_x / 2 - eps,
               cap_y + r - tie_groove_d,
               0])
        rotate([0, 90, 0])
            cylinder(r = r, h = cap_x + 2 * eps);
}

// One triangular-prism cutter: a c x c right triangle extruded along its
// own +X axis for `length` mm. The hypotenuse is the chamfer surface.
module _chamfer_prism(length, c) {
    rotate([0, 90, 0])
        linear_extrude(height = length)
            polygon([[0, 0], [c, 0], [0, c]]);
}

// Triangular-prism cutter extruded along +Z for the vertical mouth edges.
module _right_edge_chamfer_prism(length, c) {
    linear_extrude(height = length)
        polygon([[0, 0], [-c, 0], [0, c]]);
}

module _left_edge_chamfer_prism(length, c) {
    linear_extrude(height = length)
        polygon([[0, 0], [c, 0], [0, c]]);
}

// Lead-in chamfer on the four edges of the radially-inward (Y=0) face.
module lead_in_chamfers() {
    c = lead_in_chamfer;
    eps = 0.01;
    L_x = cap_x + 2 * eps;
    L_z = cap_z + 2 * eps;

    // Y=0 / +Z edge (top of mouth, runs along +X)
    translate([-cap_x / 2 - eps, 0, cap_z / 2 - c])
        _chamfer_prism(L_x, c);

    // Y=0 / -Z edge (bottom of mouth, runs along +X)
    translate([-cap_x / 2 - eps, 0, -cap_z / 2])
        mirror([0, 0, 1])
            translate([0, 0, -c])
                _chamfer_prism(L_x, c);

    // Y=0 / +X edge (right side of mouth, runs along +Z)
    translate([cap_x / 2, 0, -cap_z / 2 - eps])
        _right_edge_chamfer_prism(L_z, c);

    // Y=0 / -X edge (left side of mouth, runs along +Z)
    translate([-cap_x / 2, 0, -cap_z / 2 - eps])
        _left_edge_chamfer_prism(L_z, c);
}

// ---------------------------------------------------------------
// Top-level cap
// ---------------------------------------------------------------
module cap() {
    difference() {
        cap_solid();
        bnc_pocket();
        tie_groove();
        lead_in_chamfers();
    }
}

cap();
