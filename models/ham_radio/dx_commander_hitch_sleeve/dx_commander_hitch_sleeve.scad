/*
  models/ham_radio/dx_commander_hitch_sleeve/dx_commander_hitch_sleeve.scad

  Sleeve adapter for a DX Commander Expedition mast in a hitch-mounted
  flag pole holder.
*/

holder_inner_d = 59;   // measured ID of hitch-mounted holder tube
body_outer_d   = 58.5; // sleeve OD below/above the flange
mast_outer_d   = 47;   // measured mast OD
mast_bore_d    = 47.6; // close sliding fit for mast

lower_insert_h = 76.2; // 3 in below holder rim
upper_guide_h  = 20;   // guide above holder rim
flange_outer_d = 68;   // stop flange OD
flange_h       = 5;    // stop flange height

chamfer = 1;
$fn = 160;

eps = 0.02;
total_h = lower_insert_h + flange_h + upper_guide_h;

assert(body_outer_d < holder_inner_d, "body_outer_d must be smaller than holder_inner_d");
assert(mast_bore_d > mast_outer_d, "mast_bore_d must be larger than mast_outer_d");
assert(flange_outer_d > holder_inner_d, "flange_outer_d must be larger than holder_inner_d");
assert(lower_insert_h > 0, "lower_insert_h must be positive");
assert(upper_guide_h > 0, "upper_guide_h must be positive");
assert(flange_h > 0, "flange_h must be positive");
assert(chamfer > 0, "chamfer must be positive");
assert(chamfer * 2 < flange_h, "chamfer must be less than half flange_h");
assert(chamfer * 2 < total_h, "chamfer must be less than half total_h");
assert(mast_bore_d + 2 * chamfer < body_outer_d, "mast bore chamfer must fit within body wall");

module chamfered_cylinder(d, h, c) {
    cylinder(
        h = h,
        d1 = d - 2 * c,
        d2 = d,
        center = false
    );

    translate([0, 0, c])
        cylinder(
            h = h - 2 * c,
            d = d,
            center = false
        );

    translate([0, 0, h - c])
        cylinder(
            h = c,
            d1 = d,
            d2 = d - 2 * c,
            center = false
        );
}

module bore_with_leadins() {
    cylinder(d = mast_bore_d, h = total_h + 2 * eps, center = false);

    translate([0, 0, -eps])
        cylinder(
            h = chamfer + eps,
            d1 = mast_bore_d + 2 * chamfer,
            d2 = mast_bore_d,
            center = false
        );

    translate([0, 0, total_h - chamfer])
        cylinder(
            h = chamfer + eps,
            d1 = mast_bore_d,
            d2 = mast_bore_d + 2 * chamfer,
            center = false
        );
}

module sleeve_solid() {
    union() {
        chamfered_cylinder(d = body_outer_d, h = total_h, c = chamfer);

        translate([0, 0, lower_insert_h])
            chamfered_cylinder(d = flange_outer_d, h = flange_h, c = chamfer);
    }
}

module dx_commander_hitch_sleeve() {
    difference() {
        sleeve_solid();

        translate([0, 0, -eps])
            bore_with_leadins();
    }
}

dx_commander_hitch_sleeve();
