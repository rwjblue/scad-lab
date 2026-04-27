/*
Ham radio kneeboard assembly in OpenSCAD.

Attribution:
- Original design based on "Ham Radio Kneeboard" by KYFriedHam:
  https://www.printables.com/model/874685-ham-radio-kneeboard
- Magnetic bottom-plate variant based on "Ham Radio Kneeboard Magnetic Mod" by Jason T:
  https://www.printables.com/model/1168939-ham-radio-kneeboard-magnetic-mod

This OpenSCAD file is a clean parametric model derived from STL files,
reference images, and other provided assets. It is not the original source model.

Local source assets inspected from:
- /Users/rwjblue/Downloads/ham-radio-kneeboard-model_files
*/

$fn = 48;

// ---------------------
// Render selection
// ---------------------

// Options: "bottom", "bottom_original", "bottom_magnetic", "top", "hinge",
// "hinge_flange", "assembly"
render_part = "assembly";

// ---------------------
// Shared dimensions
// ---------------------

plate_length = 200;       // X dimension measured from STL bounding boxes
plate_width  = 139.7;     // Y dimension measured from STL bounding boxes
plate_thick  = 6;
plate_corner_radius = 14;

// The source plates use a comb-like hinge edge. The separate hinge pieces slide
// over these rectangular fingers and are pinned with a 1/16 in rod.
hinge_edge_finger_depth = 6.3;
hinge_edge_finger_width = 18.18;
hinge_edge_gap_width = 18.18;
hinge_edge_gap_starts = [18.18, 54.54, 90.90, 127.26, 163.62];
hinge_edge_tooth_starts = [0, 36.36, 72.72, 109.08, 145.44, 181.80];
hinge_edge_barrel_radius = plate_thick / 2;

edge_hole_d = 7;
top_edge_hole_d = 6;

side_slot_width = 5;
side_slot_length = 38.5;
top_strap_relief_depth = plate_thick / 2;
top_cord_groove_width = 9.5;
top_cord_groove_depth = 4;
top_edge_groove_depth = 3;
top_cord_groove_margin = 12;

hinge_gap = 0.3;
assembly_plate_gap = 4;
hinge_segment_length = 17.9;
hinge_segment_width = 12.3;
hinge_segment_height = 6;
hinge_pin_d = 1.8;       // 1/16 in rod plus clearance
hinge_pin_offset_y = 3.15;
hinge_lobe_radius = plate_thick / 2;
hinge_web_width = 3;
hinge_flange_extra_width = 6;
hinge_flange_drop = 2;

// Magnetic bottom-plate inset. Enabled by default because this maintained
// version targets the magnetic mod; set false to render the original base.
enable_magnetic_plate_inset = true;
metal_plate_length = 65.45;
metal_plate_width = 45.45;
metal_plate_depth = 0.75;
metal_plate_offset_x = 34.23;    // pocket center from bottom-plate left edge
metal_plate_offset_y = 34.72;    // pocket center from bottom-plate lower edge
metal_plate_corner_radius = 7;

far_edge_slot_length = 108;
far_edge_slot_width = 6;

// ---------------------
// Helpers
// ---------------------

module rounded_rect_2d(size, r) {
    assert(size[0] > 2 * r, "rounded_rect_2d: X size must exceed diameter");
    assert(size[1] > 2 * r, "rounded_rect_2d: Y size must exceed diameter");

    offset(r = r)
        square([size[0] - 2 * r, size[1] - 2 * r], center = true);
}

module rounded_prism(size, r, center = false) {
    translate(center ? [0, 0, -size[2] / 2] : [size[0] / 2, size[1] / 2, 0])
        linear_extrude(height = size[2])
            rounded_rect_2d([size[0], size[1]], r);
}

module selective_corner_2d(pos, size, r, rounded) {
    if (rounded)
        translate(pos)
            circle(r = r);
    else
        translate([
            pos[0] < size[0] / 2 ? 0 : size[0] - r,
            pos[1] < size[1] / 2 ? 0 : size[1] - r
        ])
            square([r, r]);
}

module selective_rounded_rect_2d(size, r, round_bottom = true, round_top = true) {
    assert(size[0] > 2 * r, "size X must exceed corner diameter");
    assert(size[1] > 2 * r, "size Y must exceed corner diameter");

    union() {
        translate([r, 0])
            square([size[0] - 2 * r, size[1]]);
        translate([0, r])
            square([size[0], size[1] - 2 * r]);

        selective_corner_2d([r, r], size, r, round_bottom);
        selective_corner_2d([size[0] - r, r], size, r, round_bottom);
        selective_corner_2d([r, size[1] - r], size, r, round_top);
        selective_corner_2d([size[0] - r, size[1] - r], size, r, round_top);
    }
}

module plate_outline_2d(hinge_edge = "none") {
    if (hinge_edge == "bottom") {
        translate([0, hinge_edge_finger_depth])
            selective_rounded_rect_2d(
                [plate_length, plate_width - hinge_edge_finger_depth],
                plate_corner_radius,
                round_bottom = false,
                round_top = true
            );
    } else if (hinge_edge == "top") {
        selective_rounded_rect_2d(
            [plate_length, plate_width - hinge_edge_finger_depth],
            plate_corner_radius,
            round_bottom = true,
            round_top = false
        );
    } else {
        selective_rounded_rect_2d([plate_length, plate_width], plate_corner_radius);
    }
}

module hinge_edge_tooth_3d(x, width, edge = "bottom") {
    y_center = edge == "bottom"
        ? hinge_edge_finger_depth / 2
        : plate_width - hinge_edge_finger_depth / 2;

    // Rectangular back half gives a strong attachment to the plate body.
    if (edge == "bottom") {
        translate([x, y_center, 0])
            cube([width, hinge_edge_finger_depth / 2 + 0.2, plate_thick]);
    } else {
        translate([x, plate_width - hinge_edge_finger_depth - 0.2, 0])
            cube([width, hinge_edge_finger_depth / 2 + 0.2, plate_thick]);
    }

    // Rounded outer half-barrel around the pin line. The Y radius is scaled
    // to match the tooth depth while the Z radius matches plate thickness.
    translate([x, y_center, plate_thick / 2])
        scale([1, hinge_edge_finger_depth / plate_thick, 1])
            rotate([0, 90, 0])
                cylinder(r = hinge_edge_barrel_radius, h = width, center = false);
}

module hinge_edge_teeth_3d(edge = "bottom") {
    for (x = hinge_edge_tooth_starts) {
        w = min(hinge_edge_finger_width, plate_length - x);
        hinge_edge_tooth_3d(x, w, edge);
    }
}

module plate_prism(hinge_edge = "none") {
    union() {
        linear_extrude(height = plate_thick)
            plate_outline_2d(hinge_edge);

        if (hinge_edge == "bottom")
            hinge_edge_teeth_3d("bottom");
        else if (hinge_edge == "top")
            hinge_edge_teeth_3d("top");
    }
}

module rounded_slot(size, h, center = true) {
    // size is [long axis, short axis] in XY.
    linear_extrude(height = h, center = center)
        hull() {
            translate([-(size[0] - size[1]) / 2, 0])
                circle(d = size[1]);
            translate([(size[0] - size[1]) / 2, 0])
                circle(d = size[1]);
        }
}

module through_hole(pos, d) {
    translate([pos[0], pos[1], plate_thick / 2])
        cylinder(d = d, h = plate_thick + 0.4, center = true);
}

module side_bungee_slot(pos, length = side_slot_length) {
    translate([pos[0], pos[1], plate_thick / 2])
        rotate([0, 0, 90])
            rounded_slot([length, side_slot_width], plate_thick + 0.4);
}

module cord_groove(pos, length, width, depth, angle = 0) {
    translate([pos[0], pos[1], plate_thick - depth])
        rotate([0, 0, angle])
            rounded_slot([length, width], depth + 0.2, center = false);
}

module edge_open_vertical_groove(pos, length, width, depth) {
    x = pos[0];
    y = pos[1];
    z = plate_thick - depth;

    cord_groove(pos, length, width, depth, 90);

    if (x < plate_length / 2) {
        translate([-0.2, y - length / 2, z])
            cube([x + width / 2 + 0.2, length, depth + 0.2]);
    } else {
        translate([x - width / 2, y - length / 2, z])
            cube([plate_length - x + width / 2 + 0.2, length, depth + 0.2]);
    }
}

module rectangular_recess(center_xy, size_xy, depth, r) {
    translate([center_xy[0], center_xy[1], plate_thick - depth])
        linear_extrude(height = depth + 0.2)
            rounded_rect_2d(size_xy, r);
}

module plate_blank(hinge_edge = "none") {
    plate_prism(hinge_edge);
}

module hinge_pin_bore(edge = "bottom") {
    y = edge == "bottom"
        ? hinge_edge_finger_depth / 2
        : plate_width - hinge_edge_finger_depth / 2;

    translate([plate_length / 2, y, plate_thick / 2])
        rotate([0, 90, 0])
            cylinder(d = hinge_pin_d, h = plate_length + 0.4, center = true);
}

// ---------------------
// Bottom plate
// ---------------------

module bottom_plate_holes_and_slots() {
    // Hinge-edge hole row from kneeboard_bottom_plate.stl.
    for (x = [15, 49, 83, 117, 151, 185])
        through_hole([x, plate_width - 12.30], edge_hole_d);

    // Left and right edge bungee holes and slots.
    for (x = [7, plate_length - 7]) {
        for (y = [18.60, 70.80, 123.00])
            through_hole([x, plate_width - y], edge_hole_d);

        side_bungee_slot([x, plate_width - 44.70]);
        side_bungee_slot([x, plate_width - 96.90]);
    }
}

module bottom_plate(enable_magnetic_inset = enable_magnetic_plate_inset) {
    // Corresponds to files/kneeboard_bottom_plate.stl.
    // With enable_magnetic_inset=true, corresponds to KFH_KneeBoardMod_BottomPlate.stl.
    difference() {
        plate_blank("top");
        hinge_pin_bore("top");
        bottom_plate_holes_and_slots();

        if (enable_magnetic_inset)
            rectangular_recess(
                [metal_plate_offset_x, metal_plate_offset_y],
                [metal_plate_width, metal_plate_length],
                metal_plate_depth,
                metal_plate_corner_radius
            );
    }
}

// ---------------------
// Top plate
// ---------------------

module top_plate_holes_and_slots() {
    // Hinge-edge row, aligned with the bottom plate.
    for (x = [15, 49, 83, 117, 151, 185])
        through_hole([x, plate_width - 127.40], top_edge_hole_d);

    // Far-edge holes and shallow cord groove.
    for (x = [15, 49, 83, 117, 151, 185])
        through_hole([x, plate_width - 6.00], top_edge_hole_d);

    cord_groove(
        [plate_length / 2, plate_width - 6.00],
        plate_length - 2 * top_cord_groove_margin,
        far_edge_slot_width,
        top_edge_groove_depth
    );

    // Side bungee holes and shallow cord grooves. These grooves let the shock
    // cord stay installed while the kneeboard closes; they are not through-slots.
    for (x = [7, plate_length - 7])
        for (y = [18.60, 70.80, 123.00])
            through_hole([x, plate_width - y], top_edge_hole_d);

    for (x = [7, plate_length - 7])
        edge_open_vertical_groove(
            [x, plate_width / 2],
            plate_width - 2 * top_cord_groove_margin,
            top_cord_groove_width,
            top_cord_groove_depth
        );

    // Half-depth reliefs matching the bottom plate's leg-strap slots. These
    // let the wider elastic straps remain installed when the board closes.
    for (x = [7, plate_length - 7]) {
        edge_open_vertical_groove(
            [x, plate_width - 44.70],
            side_slot_length,
            side_slot_width,
            top_strap_relief_depth
        );
        edge_open_vertical_groove(
            [x, plate_width - 96.90],
            side_slot_length,
            side_slot_width,
            top_strap_relief_depth
        );
    }

    // Hinge-side cord groove.
    cord_groove(
        [plate_length / 2, plate_width - 127.40],
        plate_length - 2 * top_cord_groove_margin,
        far_edge_slot_width,
        top_edge_groove_depth
    );
}

module top_plate() {
    // Corresponds to files/kneeboard_top_plate_v2.stl.
    // The original tray/pad recess is intentionally omitted in this remix.
    difference() {
        plate_blank("bottom");
        hinge_pin_bore("bottom");
        top_plate_holes_and_slots();
    }
}

// ---------------------
// Hinge components
// ---------------------

module hinge_body(length = hinge_segment_length, width = hinge_segment_width, height = hinge_segment_height) {
    // Corresponds to files/kneeboard_hinge.stl.
    // Simplified as a double-barrel hinge block with two 1/16 in rod bores:
    // one lobe for the bottom-plate teeth and one for the top-plate teeth.
    difference() {
        union() {
            for (y = [hinge_pin_offset_y, width - hinge_pin_offset_y])
                translate([0, y, height / 2])
                    rotate([0, 90, 0])
                        cylinder(r = hinge_lobe_radius, h = length, center = false);

            translate([0, hinge_pin_offset_y, 0])
                cube([
                    length,
                    width - 2 * hinge_pin_offset_y,
                    height
                ]);

            translate([0, width / 2 - hinge_web_width / 2, 0])
                cube([length, hinge_web_width, height]);
        }

        for (y = [hinge_pin_offset_y, width - hinge_pin_offset_y])
            translate([length / 2, y, height / 2])
                rotate([0, 90, 0])
                    cylinder(d = hinge_pin_d, h = length + 0.4, center = true);
    }
}

module hinge_with_flange() {
    // Corresponds to files/kneeboard_hinge_with_flange.stl.
    union() {
        hinge_body();

        translate([1, -hinge_flange_extra_width / 2, -hinge_flange_drop])
            rounded_prism(
                [
                    hinge_segment_length - 2,
                    hinge_segment_width + hinge_flange_extra_width,
                    hinge_flange_drop
                ],
                1
            );
    }
}

module hinge_row(with_flange = false) {
    // The source assembly uses five hinge knuckles across the shared edge:
    // two regular hinges and three hinges with flange.
    for (x = [15, 49, 83, 117, 151])
        translate([x - hinge_segment_length / 2, 0, 0])
            if (with_flange)
                hinge_with_flange();
            else
                hinge_body();
}

module mixed_hinge_row() {
    hinge_xs = [
        for (x = hinge_edge_gap_starts)
            x + hinge_edge_gap_width / 2
    ];

    for (i = [0 : len(hinge_xs) - 1])
        translate([hinge_xs[i] - hinge_segment_length / 2, 0, 0])
            if (i == 1 || i == 3)
                hinge_body();
            else
                hinge_with_flange();
}

// ---------------------
// Layout / render
// ---------------------

module assembly_layout() {
    bottom_plate(enable_magnetic_inset = true);

    translate([0, plate_width + assembly_plate_gap, 0])
        top_plate();
}

if (render_part == "bottom") {
    bottom_plate();
} else if (render_part == "bottom_original") {
    bottom_plate(enable_magnetic_inset = false);
} else if (render_part == "bottom_magnetic") {
    bottom_plate(enable_magnetic_inset = true);
} else if (render_part == "top") {
    top_plate();
} else if (render_part == "hinge") {
    hinge_body();
} else if (render_part == "hinge_flange") {
    hinge_with_flange();
} else {
    assembly_layout();
}
