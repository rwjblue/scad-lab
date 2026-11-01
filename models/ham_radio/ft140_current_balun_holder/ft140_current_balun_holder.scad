/*
  models/ham_radio/ft140_current_balun_holder/
  ft140_current_balun_holder.scad

  Compact, support-free enclosure for a radio-end FT-140-size current balun.
  Radio and coax-output BNCs occupy opposing end walls. Two M5 balanced-output
  studs occupy opposing side walls, keeping their permanent wiring enclosed and
  giving both wing nuts unrestricted access.

  Print the box and lid separately, open sides upward. See README.md for fit
  checks, hardware, winding, wiring, and assembly.
*/

$fn = 64;
eps = 0.02;

// ---------------------------------------------------------------
// Output
// ---------------------------------------------------------------
// "box"                    - enclosure base and walls
// "lid"                    - removable cap, already oriented for printing
// "print_layout"           - box and lid side by side
// "assembly_preview"       - separated lid plus reference hardware/core
// "bnc_bulkhead_fit_test"  - upright 9.4, 9.7, and 10.0 mm holes
// "m5_fit_test"            - upright 5.2, 5.4, and 5.6 mm holes
render_mode = "box";

// ---------------------------------------------------------------
// Enclosure
// ---------------------------------------------------------------
box_outer_length       = 76.0;
box_outer_width        = 52.0;
box_height             = 22.5;
base_thickness         = 1.8;
wall_thickness         = 1.8;
box_corner_radius      = 4.0;
minimum_edge_wall      = 2.5;

box_inner_length = box_outer_length - 2 * wall_thickness;
box_inner_width = box_outer_width - 2 * wall_thickness;
box_inner_height = box_height - base_thickness;
box_inner_corner_radius = box_corner_radius - wall_thickness;

// ---------------------------------------------------------------
// FT-140-size toroid support
// ---------------------------------------------------------------
// Fair-Rite 2631805302 nominal dimensions are 35.55 x 23.00 x 15.00 mm.
// Winding bulk is represented separately from the bare-core tolerance.
toroid_nominal_od       = 35.55;
toroid_od_tolerance     = 0.75;
toroid_nominal_id       = 23.00;
toroid_id_tolerance     = 0.55;
wound_toroid_max_od     = 42.0;
wound_toroid_max_height = 18.5;
toroid_side_clearance   = 2.5;
toroid_top_clearance    = 1.5;

toroid_support_od       = 42.0;
toroid_support_id       = 20.0;
toroid_support_height   = 0.8;

// Four low internal bridges accept two 2.5 mm ties. The ties never pass
// through the floor, so the enclosure bottom remains closed and flat.
strap_anchor_x          = 6.0;
strap_anchor_y          = 18.5;
strap_anchor_width      = 6.0;
strap_anchor_depth      = 4.5;
strap_anchor_height     = 4.0;
strap_opening_width     = 3.2;
strap_opening_height    = 1.8;
strap_opening_floor     = 0.7;

// ---------------------------------------------------------------
// Single-hole threaded bulkhead BNCs
// ---------------------------------------------------------------
// Both ports point outward, parallel to the floor. Local inner bosses produce
// a 4 mm mounting section without making every enclosure wall 4 mm thick.
bnc_axis_z              = 11.0;
bnc_bulkhead_hole_d     = 9.7;
bnc_hole_facets         = 48;
bnc_body_od             = 14.0;
bnc_boss_depth          = 2.2;
bnc_boss_width          = 24.0;
bnc_boss_bottom_z       = 2.3;
bnc_boss_height         = 18.0;

// ---------------------------------------------------------------
// Opposing balanced-output M5 studs
// ---------------------------------------------------------------
// Both studs share an x/z station but point through opposite long walls. The
// permanent pigtail ring remains inside; the removable feedline ring and wing
// nut remain outside. This removes all wing-nut/BNC sweep interference.
m5_nominal_d            = 5.0;
m5_hole_clearance       = 0.4;
m5_hole_d               = m5_nominal_d + m5_hole_clearance;
terminal_x              = 24.0;
terminal_axis_z         = 11.0;
terminal_boss_d         = 17.0;
terminal_boss_depth     = 2.2;
terminal_hardware_od    = 26.0;

// ---------------------------------------------------------------
// Removable cap
// ---------------------------------------------------------------
// The lid is a slip cap. Increase lid_clearance for a looser fit. Its long-side
// finger scallops make removal possible without prying against a connector.
lid_clearance           = 0.30;
lid_top_thickness       = 1.6;
lid_skirt_thickness     = 1.4;
lid_skirt_depth         = 3.5;
lid_grip_notch_d        = 12.0;

// Small tactile ribs identify ports without relying on tiny printed text:
// one rib marks RADIO / terminal A, and two ribs mark COAX OUT / terminal B.
marker_depth            = 0.6;
marker_width            = 1.8;
marker_height           = 4.0;
marker_bottom_z         = 3.0;
marker_spacing          = 3.2;

lid_inner_length = box_outer_length + 2 * lid_clearance;
lid_inner_width = box_outer_width + 2 * lid_clearance;
lid_outer_length = lid_inner_length + 2 * lid_skirt_thickness;
lid_outer_width = lid_inner_width + 2 * lid_skirt_thickness;
lid_inner_corner_radius = box_corner_radius + lid_clearance;
lid_outer_corner_radius = lid_inner_corner_radius + lid_skirt_thickness;
lid_total_height = lid_top_thickness + lid_skirt_depth;

// ---------------------------------------------------------------
// Fit-test layouts
// ---------------------------------------------------------------
bnc_bulkhead_fit_ds     = [9.4, 9.7, 10.0];
m5_fit_hole_ds          = [5.2, 5.4, 5.6];
fit_test_wall_thickness = wall_thickness + bnc_boss_depth;
fit_test_base_depth     = 10.0;
fit_test_pitch          = 18.0;
fit_test_width          = 56.0;
fit_test_height         = 20.0;
fit_test_axis_z         = 10.5;
fit_test_notch_d        = 5.0;

toroid_max_od = toroid_nominal_od + toroid_od_tolerance;
toroid_min_id = toroid_nominal_id - toroid_id_tolerance;

module rounded_rectangle_2d(width, height, radius) {
    assert(width >= 2 * radius,
           "rounded rectangle width must be at least twice the radius");
    assert(height >= 2 * radius,
           "rounded rectangle height must be at least twice the radius");

    hull()
        for (x = [-width / 2 + radius, width / 2 - radius])
            for (y = [-height / 2 + radius, height / 2 - radius])
                translate([x, y])
                    circle(r = radius);
}

module tray_shell() {
    difference() {
        linear_extrude(height = box_height)
            rounded_rectangle_2d(
                box_outer_length,
                box_outer_width,
                box_corner_radius
            );

        translate([0, 0, base_thickness])
            linear_extrude(height = box_inner_height + eps)
                rounded_rectangle_2d(
                    box_inner_length,
                    box_inner_width,
                    box_inner_corner_radius
                );
    }
}

module bnc_bosses() {
    for (side = [-1, 1])
        translate(
            [
                side * (
                    box_outer_length / 2
                        - wall_thickness
                        - bnc_boss_depth / 2
                ),
                0,
                bnc_boss_bottom_z + bnc_boss_height / 2
            ]
        )
            cube(
                [bnc_boss_depth + 2 * eps, bnc_boss_width, bnc_boss_height],
                center = true
            );
}

module terminal_bosses() {
    for (side = [-1, 1])
        translate(
            [
                terminal_x,
                side * (
                    box_outer_width / 2
                        - wall_thickness
                        - terminal_boss_depth / 2
                ),
                terminal_axis_z
            ]
        )
            rotate([90, 0, 0])
                cylinder(
                    d = terminal_boss_d,
                    h = terminal_boss_depth + 2 * eps,
                    center = true
                );
}

module tactile_markers() {
    // End-wall port markers.
    translate(
        [
            -box_outer_length / 2 - marker_depth,
            -marker_width / 2,
            marker_bottom_z
        ]
    )
        cube([marker_depth + eps, marker_width, marker_height]);

    for (y = [-marker_spacing / 2, marker_spacing / 2])
        translate(
            [
                box_outer_length / 2 - eps,
                y - marker_width / 2,
                marker_bottom_z
            ]
        )
            cube([marker_depth + eps, marker_width, marker_height]);

    // Side-wall terminal markers, placed toward the toroid side of each stud.
    translate(
        [
            terminal_x - 10,
            box_outer_width / 2 - eps,
            marker_bottom_z
        ]
    )
        cube([marker_width, marker_depth + eps, marker_height]);

    for (x = [
        terminal_x - 10 - marker_spacing / 2,
        terminal_x - 10 + marker_spacing / 2
    ])
        translate(
            [
                x - marker_width / 2,
                -box_outer_width / 2 - marker_depth,
                marker_bottom_z
            ]
        )
            cube([marker_width, marker_depth + eps, marker_height]);
}

module toroid_support() {
    translate([0, 0, base_thickness - eps])
        linear_extrude(height = toroid_support_height + eps)
            difference() {
                circle(d = toroid_support_od);
                circle(d = toroid_support_id);
            }
}

module strap_anchor(x, y) {
    translate(
        [
            x - strap_anchor_width / 2,
            y - strap_anchor_depth / 2,
            base_thickness - eps
        ]
    )
        difference() {
            cube(
                [
                    strap_anchor_width,
                    strap_anchor_depth,
                    strap_anchor_height + eps
                ]
            );

            translate(
                [
                    (strap_anchor_width - strap_opening_width) / 2,
                    -eps,
                    strap_opening_floor
                ]
            )
                cube(
                    [
                        strap_opening_width,
                        strap_anchor_depth + 2 * eps,
                        strap_opening_height
                    ]
                );
        }
}

module strap_anchors() {
    for (x = [-strap_anchor_x, strap_anchor_x])
        for (y = [-strap_anchor_y, strap_anchor_y])
            strap_anchor(x, y);
}

module bnc_through_holes() {
    translate(
        [
            -box_outer_length / 2 - bnc_boss_depth - eps,
            0,
            bnc_axis_z
        ]
    )
        rotate([0, 90, 0])
            cylinder(
                d = bnc_bulkhead_hole_d,
                h = box_outer_length + 2 * bnc_boss_depth + 2 * eps,
                $fn = bnc_hole_facets
            );
}

module terminal_through_holes() {
    translate(
        [
            terminal_x,
            -box_outer_width / 2 - terminal_boss_depth - eps,
            terminal_axis_z
        ]
    )
        rotate([-90, 0, 0])
            cylinder(
                d = m5_hole_d,
                h = box_outer_width + 2 * terminal_boss_depth + 2 * eps,
                $fn = 40
            );
}

module validate_box() {
    assert(base_thickness >= 1.6,
           "base is too thin for a portable PETG enclosure");
    assert(wall_thickness >= 1.6,
           "walls are too thin for a portable PETG enclosure");
    assert(box_inner_corner_radius > 0,
           "wall thickness consumes the inner corner radius");
    assert(box_inner_width >= wound_toroid_max_od + 2 * toroid_side_clearance,
           "insufficient side clearance for the wound toroid");
    assert(box_inner_height >= wound_toroid_max_height + toroid_top_clearance,
           "insufficient height for the wound toroid and lid clearance");
    assert(toroid_support_od > toroid_max_od,
           "toroid support must extend beyond the maximum bare-core OD");
    assert(toroid_support_id < toroid_min_id,
           "toroid support must overlap the minimum bare-core ID");
    assert(bnc_axis_z - bnc_bulkhead_hole_d / 2 >= minimum_edge_wall,
           "insufficient wall below the BNC holes");
    assert(box_height - bnc_axis_z - bnc_bulkhead_hole_d / 2
           >= minimum_edge_wall,
           "insufficient wall above the BNC holes");
    assert(bnc_boss_width - bnc_bulkhead_hole_d
           >= 2 * minimum_edge_wall,
           "insufficient BNC boss material beside the hole");
    assert(wall_thickness + bnc_boss_depth <= 5.5,
           "BNC mounting section exceeds the documented comparison connector");
    assert(box_height - lid_skirt_depth
           >= bnc_axis_z + bnc_body_od / 2 + 0.3,
           "lid skirt reaches the connected BNC body keep-out");
    assert(terminal_axis_z - terminal_boss_d / 2 >= base_thickness,
           "terminal boss reaches below the enclosure floor");
    assert(box_height - terminal_axis_z - terminal_boss_d / 2 >= 1.5,
           "terminal boss is too close to the lid edge");
    assert(terminal_boss_d - m5_hole_d >= 2 * minimum_edge_wall,
           "insufficient material around an M5 hole");
    assert(terminal_x + terminal_boss_d / 2
           < box_inner_length / 2,
           "terminal boss reaches the COAX OUT end wall");
    assert(strap_anchor_y + strap_anchor_depth / 2
           < box_inner_width / 2,
           "strap anchor reaches a side wall");
    assert(strap_opening_width > 2.5,
           "strap opening is too narrow for the documented tie");
    assert(strap_opening_floor + strap_opening_height
           < strap_anchor_height,
           "strap anchor has no printable roof");
}

module balun_box() {
    validate_box();

    difference() {
        union() {
            tray_shell();
            bnc_bosses();
            terminal_bosses();
            tactile_markers();
            toroid_support();
            strap_anchors();
        }

        bnc_through_holes();
        terminal_through_holes();
    }
}

module validate_lid() {
    assert(lid_clearance >= 0,
           "lid clearance cannot be negative");
    assert(lid_top_thickness >= 1.2,
           "lid top is too thin");
    assert(lid_skirt_thickness >= 1.2,
           "lid skirt is too thin");
    assert(lid_skirt_depth >= 3.0,
           "lid skirt is too shallow to remain aligned");
    assert(lid_grip_notch_d < lid_outer_length / 3,
           "lid grip notch is too large");
}

module balun_lid() {
    validate_lid();

    difference() {
        linear_extrude(height = lid_total_height)
            rounded_rectangle_2d(
                lid_outer_length,
                lid_outer_width,
                lid_outer_corner_radius
            );

        translate([0, 0, lid_top_thickness])
            linear_extrude(height = lid_skirt_depth + eps)
                rounded_rectangle_2d(
                    lid_inner_length,
                    lid_inner_width,
                    lid_inner_corner_radius
                );

        // Opposing half-round scallops at the skirt's open edge provide a
        // fingertip purchase. They do not interrupt the top shell.
        for (side = [-1, 1])
            translate(
                [
                    0,
                    side * (lid_outer_width / 2 + eps),
                    lid_total_height
                ]
            )
                rotate([90, 0, 0])
                    cylinder(
                        d = lid_grip_notch_d,
                        h = lid_skirt_thickness + 2 * eps,
                        center = true
                    );
    }
}

module upright_fit_test(hole_ds, label) {
    count = len(hole_ds);

    assert(count == 3,
           str(label, " fit test must contain three samples"));
    assert(fit_test_width >= (count - 1) * fit_test_pitch
           + max(hole_ds) + 2 * minimum_edge_wall,
           str(label, " fit-test holes are too close to the ends"));

    for (i = [0 : count - 1])
        echo(
            str(
                label, " sample ", i + 1,
                ": hole_d=", hole_ds[i], " mm"
            )
        );

    difference() {
        union() {
            translate(
                [
                    -fit_test_base_depth / 2,
                    -fit_test_width / 2,
                    0
                ]
            )
                cube(
                    [fit_test_base_depth, fit_test_width, base_thickness]
                );

            translate(
                [
                    -fit_test_wall_thickness / 2,
                    -fit_test_width / 2,
                    0
                ]
            )
                cube(
                    [
                        fit_test_wall_thickness,
                        fit_test_width,
                        fit_test_height
                    ]
                );
        }

        for (i = [0 : count - 1])
            translate(
                [
                    -fit_test_wall_thickness / 2 - eps,
                    (i - (count - 1) / 2) * fit_test_pitch,
                    fit_test_axis_z
                ]
            )
                rotate([0, 90, 0])
                    cylinder(
                        d = hole_ds[i],
                        h = fit_test_wall_thickness + 2 * eps,
                        $fn = bnc_hole_facets
                    );

        // The clipped base corner identifies sample 1 / the smallest hole.
        translate(
            [
                -fit_test_base_depth / 2,
                -fit_test_width / 2,
                -eps
            ]
        )
            cylinder(
                d = fit_test_notch_d,
                h = base_thickness + 2 * eps
            );
    }
}

module toroid_preview() {
    color([0.16, 0.22, 0.18])
        translate([0, 0, base_thickness + wound_toroid_max_height / 2])
            rotate_extrude($fn = 96)
                translate(
                    [
                        (toroid_nominal_od + toroid_nominal_id) / 4,
                        0
                    ]
                )
                    circle(
                        d = (toroid_nominal_od - toroid_nominal_id) / 2,
                        $fn = 36
                    );
}

module connector_preview() {
    color([0.72, 0.72, 0.74]) {
        // Simplified BNC barrels.
        translate([-box_outer_length / 2 - 8, 0, bnc_axis_z])
            rotate([0, 90, 0])
                cylinder(d = 14, h = 16, center = true);
        translate([box_outer_length / 2 + 8, 0, bnc_axis_z])
            rotate([0, 90, 0])
                cylinder(d = 14, h = 16, center = true);

        // Simplified opposing M5 studs and wing-nut keep-out discs.
        for (side = [-1, 1]) {
            translate(
                [
                    terminal_x,
                    side * (box_outer_width / 2 + 7),
                    terminal_axis_z
                ]
            )
                rotate([90, 0, 0])
                    cylinder(d = m5_nominal_d, h = 14, center = true);

            color([0.82, 0.68, 0.20, 0.55])
                translate(
                    [
                        terminal_x,
                        side * (box_outer_width / 2 + 8),
                        terminal_axis_z
                    ]
                )
                    rotate([90, 0, 0])
                        cylinder(
                            d = terminal_hardware_od,
                            h = 2,
                            center = true,
                            $fn = 48
                        );
        }
    }
}

module assembly_preview() {
    color([0.94, 0.38, 0.08])
        balun_box();
    toroid_preview();
    connector_preview();

    // The lid is exploded upward and flipped from its print orientation.
    color([0.94, 0.38, 0.08, 0.75])
        translate([0, 0, box_height + lid_top_thickness + 12])
            rotate([180, 0, 0])
                balun_lid();
}

module print_layout() {
    translate([-45, 0, 0])
        balun_box();
    translate([45, 0, 0])
        balun_lid();
}

assert(
    render_mode == "box"
        || render_mode == "lid"
        || render_mode == "print_layout"
        || render_mode == "assembly_preview"
        || render_mode == "bnc_bulkhead_fit_test"
        || render_mode == "m5_fit_test",
    str(
        "render_mode must be box, lid, print_layout, assembly_preview, ",
        "bnc_bulkhead_fit_test, or m5_fit_test"
    )
);

if (render_mode == "box")
    balun_box();
else if (render_mode == "lid")
    balun_lid();
else if (render_mode == "print_layout")
    print_layout();
else if (render_mode == "assembly_preview")
    assembly_preview();
else if (render_mode == "bnc_bulkhead_fit_test")
    upright_fit_test(bnc_bulkhead_fit_ds, "BNC bulkhead");
else
    upright_fit_test(m5_fit_hole_ds, "M5");
