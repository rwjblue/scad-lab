/*
  models/ham_radio/lightweight_balanced_feedline/
  doublet_center_terminal_strain_relief.scad

  Modular center support for a lightweight portable doublet. Separate
  radiator and balanced-feedline conductors terminate on two electrically
  isolated #6-32 studs. Independent two-hole wire paths keep mechanical
  loads off the crimped ring terminals.

  Print flat. Install bolt heads on the back and terminal hardware on the
  front. See README.md for the exact hardware stack and assembly sequence.
*/

$fn = 64;
eps = 0.02;

// ---------------------------------------------------------------
// Output
// ---------------------------------------------------------------
// "center"            - complete modular center support
// "stud_fit_test"     - notched coupon with 3.8, 4.0, and 4.2 mm holes
// "radiator_fit_test" - notched coupon varying radiator snap throats
render_mode = "center";

// ---------------------------------------------------------------
// Wire and feedline geometry
// ---------------------------------------------------------------
wire_od               = 1.02;  // nominal jacket OD; measure your own spool
wire_hole_clearance   = 0.80;  // diametral clearance for easy threading
feedline_spacing      = 12.7;  // lower exit-hole center-to-center spacing
wire_hole_chamfer     = 0.60;  // eases jacket contact on both plate faces
radiator_slot_width   = 0.82;  // snap throat for removable radiator wires
radiator_mouth_width  = 1.20;  // tapered lead-in at the plate edge
radiator_slot_overlap = 0.04;  // joins each slot cleanly to its round hole
minimum_edge_wall     = 2.0;   // wall outside each face-side hole chamfer
minimum_hole_ligament = 2.0;   // plastic between adjacent face chamfers

// ---------------------------------------------------------------
// #6-32 terminal studs
// ---------------------------------------------------------------
stud_nominal_d         = 3.51;  // #6 screw major diameter, approximately
stud_hole_clearance    = 0.49;  // gives a 4.0 mm default printed hole
stud_hole_chamfer      = 0.35;  // insertion lead-in; not a countersink
terminal_spacing       = 22.0;  // room for two hand-tightened terminal nuts
terminal_y             = 27.0;
terminal_hardware_od   = 9.6;   // 3/8 inch washer/thumb-nut keep-out

// ---------------------------------------------------------------
// Center body
// ---------------------------------------------------------------
plate_thickness      = 5.0;
corner_radius        = 3.0;

crossbar_width       = 64.0;
crossbar_height      = 22.0;
crossbar_bottom_y    = 20.0;

stem_width           = 28.0;
stem_height          = 25.0;

// ---------------------------------------------------------------
// Suspension hole
// ---------------------------------------------------------------
hoist_hole_d         = 6.5;
hoist_hole_y         = 36.0;
hoist_hole_chamfer   = 0.70;

// ---------------------------------------------------------------
// Mirrored strain-relief paths, one set per electrical side
// ---------------------------------------------------------------
radiator_outer_x     = 28.0;
radiator_outer_y     = 31.0;

radiator_relief_x    = 21.0;
radiator_relief_y    = 26.0;

feedline_lower_y     = 5.5;
feedline_relief_y    = 13.5;

// ---------------------------------------------------------------
// Terminal-stud fit coupon
// ---------------------------------------------------------------
stud_fit_hole_ds     = [3.8, 4.0, 4.2];
stud_fit_pitch       = 10.0;
stud_fit_width       = 32.0;
stud_fit_height      = 12.0;
stud_fit_corner_r    = 2.0;
stud_fit_notch_d     = 3.0;

radiator_fit_slot_widths = [0.72, 0.82, 0.92];
radiator_fit_pitch       = 11.0;
radiator_fit_width       = 36.0;
radiator_fit_height      = 12.0;
radiator_fit_corner_r    = 2.0;
radiator_fit_notch_d     = 3.0;

wire_hole_d = wire_od + wire_hole_clearance;
stud_hole_d = stud_nominal_d + stud_hole_clearance;
crossbar_center_y = crossbar_bottom_y + crossbar_height / 2;
overall_height = max(stem_height, crossbar_bottom_y + crossbar_height);

function chamfered_hole_face_radius(diameter, chamfer) =
    diameter / 2 + chamfer;
function point_distance(a, b) =
    sqrt(pow(a[0] - b[0], 2) + pow(a[1] - b[1], 2));
function circle_chord(diameter, inset) =
    2 * sqrt(
        max(
            0,
            pow(diameter / 2, 2)
                - pow(diameter / 2 - inset, 2)
        )
    );

module rounded_rectangle_2d(width, height, radius) {
    assert(width >= 2 * radius,
           "rounded rectangle width must be at least twice the radius");
    assert(height >= 2 * radius,
           "rounded rectangle height must be at least twice the radius");

    hull() {
        for (x = [-width / 2 + radius, width / 2 - radius])
            for (y = [-height / 2 + radius, height / 2 - radius])
                translate([x, y])
                    circle(r = radius);
    }
}

module center_body_2d() {
    union() {
        translate([0, crossbar_center_y])
            rounded_rectangle_2d(
                crossbar_width,
                crossbar_height,
                corner_radius
            );

        translate([0, stem_height / 2])
            rounded_rectangle_2d(
                stem_width,
                stem_height,
                corner_radius
            );
    }
}

// Through-hole plus a conical lead-in on both faces. Wire holes use a broad
// chamfer for jacket protection; stud holes use only a small insertion lead-in.
module chamfered_hole(x, y, diameter, chamfer, thickness = plate_thickness) {
    assert(diameter > 0, "hole diameter must be positive");
    assert(chamfer >= 0, "hole chamfer cannot be negative");
    assert(chamfer < thickness / 2,
           "hole chamfer must be less than half the part thickness");

    translate([x, y, -eps])
        cylinder(d = diameter, h = thickness + 2 * eps);

    if (chamfer > 0) {
        translate([x, y, -eps])
            cylinder(
                d1 = diameter + 2 * chamfer,
                d2 = diameter,
                h = chamfer + eps
            );

        translate([x, y, thickness - chamfer])
            cylinder(
                d1 = diameter,
                d2 = diameter + 2 * chamfer,
                h = chamfer + eps
            );
    }
}

// Converts a closed through-hole into a C-shaped snap channel. The outer
// radiator hole opens upward and the inner hole opens downward, so neither
// opening points along the antenna-tension path.
module radiator_snap_slot(
    x,
    y,
    direction,
    edge_y,
    slot_width = radiator_slot_width,
    mouth_width = radiator_mouth_width,
    thickness = plate_thickness
) {
    neck_y = y + direction * (wire_hole_d / 2 - radiator_slot_overlap);

    assert(direction == -1 || direction == 1,
           "radiator slot direction must be -1 or 1");
    assert(slot_width > 0 && slot_width < wire_od,
           "radiator snap throat must be positive and retain the wire");
    assert(mouth_width >= wire_od,
           "radiator snap mouth must accept the nominal wire");
    assert(radiator_slot_overlap > 0,
           "radiator_slot_overlap must be positive");
    assert(radiator_slot_overlap + eps / 2 < wire_hole_d / 2,
           "radiator_slot_overlap must be smaller than the hole radius");
    assert(
        circle_chord(
            wire_hole_d,
            radiator_slot_overlap + eps / 2
        ) < slot_width,
        "radiator_slot_overlap is too large to preserve slot width"
    );

    translate([0, 0, -eps])
        linear_extrude(height = thickness + 2 * eps)
            hull() {
                translate([x, neck_y])
                    square([slot_width, eps], center = true);

                translate([x, edge_y])
                    square([mouth_width, eps], center = true);
            }
}

module mirrored_wire_holes(side) {
    chamfered_hole(
        side * radiator_outer_x,
        radiator_outer_y,
        wire_hole_d,
        wire_hole_chamfer
    );
    radiator_snap_slot(
        side * radiator_outer_x,
        radiator_outer_y,
        1,
        overall_height + eps
    );

    chamfered_hole(
        side * radiator_relief_x,
        radiator_relief_y,
        wire_hole_d,
        wire_hole_chamfer
    );
    radiator_snap_slot(
        side * radiator_relief_x,
        radiator_relief_y,
        -1,
        crossbar_bottom_y - eps
    );

    chamfered_hole(
        side * feedline_spacing / 2,
        feedline_lower_y,
        wire_hole_d,
        wire_hole_chamfer
    );

    chamfered_hole(
        side * feedline_spacing / 2,
        feedline_relief_y,
        wire_hole_d,
        wire_hole_chamfer
    );
}

module terminal_stud_holes() {
    for (side = [-1, 1])
        chamfered_hole(
            side * terminal_spacing / 2,
            terminal_y,
            stud_hole_d,
            stud_hole_chamfer
        );
}

module doublet_center_terminal_strain_relief() {
    wire_face_r = chamfered_hole_face_radius(
        wire_hole_d,
        wire_hole_chamfer
    );
    hoist_face_r = chamfered_hole_face_radius(
        hoist_hole_d,
        hoist_hole_chamfer
    );
    terminal_face_r = chamfered_hole_face_radius(
        stud_hole_d,
        stud_hole_chamfer
    );
    hardware_r = terminal_hardware_od / 2;

    assert(wire_od > 0, "wire_od must be positive");
    assert(wire_hole_clearance >= 0,
           "wire_hole_clearance cannot be negative");
    assert(feedline_spacing > wire_hole_d,
           "feedline_spacing must exceed the wire-hole diameter");
    assert(radiator_slot_width > 0,
           "radiator_slot_width must be positive");
    assert(radiator_slot_width < wire_od,
           "radiator_slot_width must retain the nominal wire");
    assert(radiator_mouth_width >= wire_od,
           "radiator_mouth_width must accept the nominal wire");
    assert(radiator_outer_x + radiator_mouth_width / 2
           <= crossbar_width / 2 - corner_radius,
           "outer radiator slot must meet the crossbar's flat top edge");
    assert(stud_nominal_d > 0, "stud_nominal_d must be positive");
    assert(stud_hole_clearance >= 0,
           "stud_hole_clearance cannot be negative");
    assert(terminal_spacing > terminal_hardware_od,
           "terminal hardware keep-outs must not overlap");
    assert(plate_thickness > 0, "plate_thickness must be positive");
    assert(minimum_edge_wall > 0, "minimum_edge_wall must be positive");
    assert(minimum_hole_ligament > 0,
           "minimum_hole_ligament must be positive");
    assert(crossbar_width > stem_width,
           "crossbar_width should be wider than stem_width");
    assert(crossbar_bottom_y < stem_height,
           "crossbar and stem must overlap");
    assert(radiator_outer_x > radiator_relief_x
           && radiator_relief_x > terminal_spacing / 2,
           "radiator holes must progress inward toward the terminal studs");
    assert(radiator_outer_y > radiator_relief_y,
           "radiator path should slope inward toward the terminal studs");
    assert(feedline_relief_y > feedline_lower_y,
           "feedline relief holes must be above the feedline exits");

    assert(overall_height - hoist_hole_y - hoist_face_r
           >= minimum_edge_wall,
           "insufficient wall above the hoist hole");
    assert(crossbar_width / 2 - radiator_outer_x - wire_face_r
           >= minimum_edge_wall,
           "insufficient wall outside a radiator entry hole");
    assert(radiator_relief_y - wire_face_r - crossbar_bottom_y
           >= minimum_edge_wall,
           "insufficient wall below a radiator relief hole");
    assert(stem_width / 2 - feedline_spacing / 2 - wire_face_r
           >= minimum_edge_wall,
           "insufficient wall outside a feedline hole");
    assert(feedline_lower_y - wire_face_r >= minimum_edge_wall,
           "insufficient wall below a feedline exit hole");
    assert(terminal_y - hardware_r - crossbar_bottom_y
           >= minimum_edge_wall,
           "terminal washer is too close to the crossbar bottom edge");
    assert(terminal_spacing - terminal_hardware_od
           >= minimum_hole_ligament,
           "insufficient space between terminal hardware stacks");

    assert(
        point_distance(
            [radiator_outer_x, radiator_outer_y],
            [radiator_relief_x, radiator_relief_y]
        ) - 2 * wire_face_r >= minimum_hole_ligament,
        "insufficient ligament between radiator strain-relief holes"
    );
    assert(
        point_distance(
            [radiator_relief_x, radiator_relief_y],
            [terminal_spacing / 2, terminal_y]
        ) - wire_face_r - hardware_r >= minimum_hole_ligament,
        "radiator relief hole is too close to terminal hardware"
    );
    assert(
        point_distance(
            [feedline_spacing / 2, feedline_relief_y],
            [terminal_spacing / 2, terminal_y]
        ) - wire_face_r - hardware_r >= minimum_hole_ligament,
        "feedline relief hole is too close to terminal hardware"
    );
    assert(
        point_distance(
            [0, hoist_hole_y],
            [terminal_spacing / 2, terminal_y]
        ) - hoist_face_r - hardware_r >= minimum_hole_ligament,
        "hoist hole is too close to terminal hardware"
    );
    assert(feedline_relief_y - feedline_lower_y - 2 * wire_face_r
           >= minimum_hole_ligament,
           "insufficient ligament between feedline strain-relief holes");
    assert(feedline_spacing - 2 * wire_face_r
           >= minimum_hole_ligament,
           "insufficient ligament between the two feedline paths");
    assert(terminal_face_r < hardware_r,
           "terminal hole must remain inside its hardware keep-out");

    difference() {
        linear_extrude(height = plate_thickness)
            center_body_2d();

        chamfered_hole(
            0,
            hoist_hole_y,
            hoist_hole_d,
            hoist_hole_chamfer
        );

        terminal_stud_holes();
        mirrored_wire_holes(-1);
        mirrored_wire_holes(1);
    }
}

module stud_fit_test() {
    count = len(stud_fit_hole_ds);

    assert(count == 3,
           "stud_fit_hole_ds must contain the documented three samples");
    assert(stud_fit_pitch > max(stud_fit_hole_ds)
           + minimum_hole_ligament,
           "stud-fit holes are too close together");
    assert(stud_fit_width >= (count - 1) * stud_fit_pitch
           + max(stud_fit_hole_ds) + 2 * minimum_edge_wall,
           "stud-fit coupon is too narrow");
    assert(stud_fit_height >= max(stud_fit_hole_ds)
           + 2 * stud_hole_chamfer + 2 * minimum_edge_wall,
           "stud-fit coupon is too short");

    for (i = [0 : count - 1])
        echo(
            str(
                "stud sample ", i + 1,
                ": hole_d=", stud_fit_hole_ds[i], " mm"
            )
        );

    difference() {
        linear_extrude(height = plate_thickness)
            rounded_rectangle_2d(
                stud_fit_width,
                stud_fit_height,
                stud_fit_corner_r
            );

        for (i = [0 : count - 1])
            chamfered_hole(
                (i - (count - 1) / 2) * stud_fit_pitch,
                0,
                stud_fit_hole_ds[i],
                stud_hole_chamfer
            );

        // The notched end identifies the 3.8 mm sample after printing.
        translate([-stud_fit_width / 2, stud_fit_height / 4, -eps])
            cylinder(d = stud_fit_notch_d, h = plate_thickness + 2 * eps);
    }
}

module radiator_fit_test() {
    count = len(radiator_fit_slot_widths);

    assert(count == 3,
           "radiator_fit_slot_widths must contain three samples");
    assert(radiator_fit_pitch > wire_hole_d + minimum_hole_ligament,
           "radiator-fit channels are too close together");
    assert(radiator_fit_width >= (count - 1) * radiator_fit_pitch
           + wire_hole_d + 2 * wire_hole_chamfer
           + 2 * minimum_edge_wall,
           "radiator-fit coupon is too narrow");
    assert(radiator_fit_height >= wire_hole_d
           + 2 * wire_hole_chamfer + 2 * minimum_edge_wall,
           "radiator-fit coupon is too short");

    for (i = [0 : count - 1])
        echo(
            str(
                "radiator sample ", i + 1,
                ": slot_width=", radiator_fit_slot_widths[i], " mm, ",
                "channel_d=", wire_hole_d, " mm"
            )
        );

    difference() {
        linear_extrude(height = plate_thickness)
            rounded_rectangle_2d(
                radiator_fit_width,
                radiator_fit_height,
                radiator_fit_corner_r
            );

        for (i = [0 : count - 1]) {
            x = (i - (count - 1) / 2) * radiator_fit_pitch;

            chamfered_hole(
                x,
                0,
                wire_hole_d,
                wire_hole_chamfer
            );
            radiator_snap_slot(
                x,
                0,
                1,
                radiator_fit_height / 2 + eps,
                radiator_fit_slot_widths[i]
            );
        }

        // The notched end identifies the 0.72 mm sample after printing.
        translate(
            [
                -radiator_fit_width / 2,
                -radiator_fit_height / 4,
                -eps
            ]
        )
            cylinder(
                d = radiator_fit_notch_d,
                h = plate_thickness + 2 * eps
            );
    }
}

assert(
    render_mode == "center"
        || render_mode == "stud_fit_test"
        || render_mode == "radiator_fit_test",
    str(
        "render_mode must be \"center\", \"stud_fit_test\", ",
        "or \"radiator_fit_test\""
    )
);

if (render_mode == "center")
    doublet_center_terminal_strain_relief();
else if (render_mode == "stud_fit_test")
    stud_fit_test();
else
    radiator_fit_test();
