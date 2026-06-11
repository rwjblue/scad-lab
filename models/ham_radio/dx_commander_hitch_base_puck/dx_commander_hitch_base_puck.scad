/*
  models/ham_radio/dx_commander_hitch_base_puck/dx_commander_hitch_base_puck.scad

  Soft bottom puck for protecting the DX Commander Expedition mast base
  inside a hitch-mounted flag pole holder.
*/

cup_inner_d       = 50.56; // measured ID of the bottom cup
lower_plug_d      = 50.2;  // TPU plug OD for the bottom cup
holder_inner_d    = 59;    // larger flag pole holder tube ID
upper_guide_d     = 58.5;  // guide OD above the bottom cup
mast_base_outer_d = 50.85; // measured mast base OD
mast_base_bore_d  = 51.2;  // shallow pocket for mast base

lower_plug_h  = 5;
floor_h       = 1.2;
upper_guide_h = 10;

chamfer = 1;
$fn = 160;

eps = 0.02;
pocket_start_h = lower_plug_h + floor_h;
total_h = pocket_start_h + upper_guide_h;

assert(lower_plug_d < cup_inner_d, "lower_plug_d must be smaller than cup_inner_d");
assert(upper_guide_d < holder_inner_d, "upper_guide_d must be smaller than holder_inner_d");
assert(mast_base_bore_d > mast_base_outer_d, "mast_base_bore_d must be larger than mast_base_outer_d");
assert(mast_base_bore_d < upper_guide_d, "mast_base_bore_d must be smaller than upper_guide_d");
assert(lower_plug_h > 0, "lower_plug_h must be positive");
assert(floor_h > 0, "floor_h must be positive");
assert(upper_guide_h > 0, "upper_guide_h must be positive");
assert(chamfer > 0, "chamfer must be positive");
assert(chamfer * 2 < lower_plug_h, "chamfer must be less than half lower_plug_h");
assert(chamfer * 2 < upper_guide_h, "chamfer must be less than half upper_guide_h");

module bottom_chamfered_cylinder(d, h, c) {
    cylinder(h = c, d1 = d - 2 * c, d2 = d, center = false);

    translate([0, 0, c])
        cylinder(h = h - c, d = d, center = false);
}

module top_chamfered_cylinder(d, h, c) {
    cylinder(h = h - c, d = d, center = false);

    translate([0, 0, h - c])
        cylinder(h = c, d1 = d, d2 = d - 2 * c, center = false);
}

module mast_base_pocket() {
    translate([0, 0, pocket_start_h])
        cylinder(d = mast_base_bore_d, h = upper_guide_h + eps, center = false);

    translate([0, 0, total_h - chamfer])
        cylinder(
            h = chamfer + eps,
            d1 = mast_base_bore_d,
            d2 = mast_base_bore_d + 2 * chamfer,
            center = false
        );
}

module puck_solid() {
    union() {
        bottom_chamfered_cylinder(d = lower_plug_d, h = lower_plug_h, c = chamfer);

        translate([0, 0, lower_plug_h])
            cylinder(h = floor_h, d = upper_guide_d, center = false);

        translate([0, 0, pocket_start_h])
            top_chamfered_cylinder(d = upper_guide_d, h = upper_guide_h, c = chamfer);
    }
}

module dx_commander_hitch_base_puck() {
    difference() {
        puck_solid();
        mast_base_pocket();
    }
}

dx_commander_hitch_base_puck();
