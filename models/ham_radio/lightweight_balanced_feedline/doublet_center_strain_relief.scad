/*
  models/ham_radio/lightweight_balanced_feedline/doublet_center_strain_relief.scad

  Lightweight center support and strain relief for a continuous-wire
  portable doublet. Each antenna conductor weaves through three chamfered
  holes, then exits downward at the balanced-feedline spacing.

  No electrical connection or splice is required at the center.
*/

$fn = 64;
eps = 0.02;

// ---------------------------------------------------------------
// Wire and feedline geometry
// ---------------------------------------------------------------
wire_od               = 1.02;  // nominal jacket OD; measure your own spool
wire_hole_clearance   = 0.80;  // diametral clearance for easy threading
feedline_spacing      = 12.7;  // exit-hole center-to-center spacing
wire_hole_chamfer     = 0.60;  // eases jacket contact on both plate faces
minimum_edge_wall     = 2.0;   // minimum wall outside face-side chamfers
minimum_hole_ligament = 2.0;  // minimum plastic between adjacent chamfers

// ---------------------------------------------------------------
// Center body
// ---------------------------------------------------------------
plate_thickness      = 4.0;
corner_radius        = 3.0;

crossbar_width       = 60.0;
crossbar_height      = 20.0;
crossbar_bottom_y    = 18.0;

stem_width           = 24.0;
stem_height          = 24.0;

// ---------------------------------------------------------------
// Suspension hole
// ---------------------------------------------------------------
hoist_hole_d         = 6.5;
hoist_hole_y         = 31.0;
hoist_hole_chamfer   = 0.70;

// ---------------------------------------------------------------
// Mirrored wire path, one set per conductor
// ---------------------------------------------------------------
radiator_hole_x      = 24.0;
radiator_hole_y      = 27.0;

relief_hole_x        = 13.5;
relief_hole_y        = 22.5;

feedline_hole_y      = 6.5;

wire_hole_d = wire_od + wire_hole_clearance;
crossbar_center_y = crossbar_bottom_y + crossbar_height / 2;
overall_height = max(stem_height, crossbar_bottom_y + crossbar_height);

function chamfered_hole_face_radius(diameter, chamfer) =
    diameter / 2 + chamfer;
function point_distance(a, b) =
    sqrt(pow(a[0] - b[0], 2) + pow(a[1] - b[1], 2));

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

// Through-hole plus a conical lead-in on both faces. The chamfer spreads
// jacket contact over a wider, shallower edge than a plain cylindrical hole.
module chamfered_hole(x, y, diameter, chamfer) {
    assert(diameter > 0, "hole diameter must be positive");
    assert(chamfer >= 0, "hole chamfer cannot be negative");
    assert(chamfer < plate_thickness / 2,
           "hole chamfer must be less than half the plate thickness");

    translate([x, y, -eps])
        cylinder(d = diameter, h = plate_thickness + 2 * eps);

    if (chamfer > 0) {
        translate([x, y, -eps])
            cylinder(
                d1 = diameter + 2 * chamfer,
                d2 = diameter,
                h = chamfer + eps
            );

        translate([x, y, plate_thickness - chamfer])
            cylinder(
                d1 = diameter,
                d2 = diameter + 2 * chamfer,
                h = chamfer + eps
            );
    }
}

module mirrored_wire_holes(side) {
    chamfered_hole(
        side * radiator_hole_x,
        radiator_hole_y,
        wire_hole_d,
        wire_hole_chamfer
    );

    chamfered_hole(
        side * relief_hole_x,
        relief_hole_y,
        wire_hole_d,
        wire_hole_chamfer
    );

    chamfered_hole(
        side * feedline_spacing / 2,
        feedline_hole_y,
        wire_hole_d,
        wire_hole_chamfer
    );
}

module doublet_center_strain_relief() {
    wire_face_r = chamfered_hole_face_radius(
        wire_hole_d,
        wire_hole_chamfer
    );
    hoist_face_r = chamfered_hole_face_radius(
        hoist_hole_d,
        hoist_hole_chamfer
    );

    assert(wire_od > 0, "wire_od must be positive");
    assert(wire_hole_clearance >= 0,
           "wire_hole_clearance cannot be negative");
    assert(feedline_spacing > wire_hole_d,
           "feedline_spacing must exceed the wire-hole diameter");
    assert(plate_thickness > 0, "plate_thickness must be positive");
    assert(minimum_edge_wall > 0, "minimum_edge_wall must be positive");
    assert(minimum_hole_ligament > 0,
           "minimum_hole_ligament must be positive");
    assert(crossbar_width > stem_width,
           "crossbar_width should be wider than stem_width");
    assert(crossbar_bottom_y < stem_height,
           "crossbar and stem must overlap");
    assert(radiator_hole_x > relief_hole_x
           && relief_hole_x > feedline_spacing / 2,
           "wire holes must progress inward toward the feedline exits");
    assert(radiator_hole_y > relief_hole_y
           && relief_hole_y > feedline_hole_y,
           "wire holes must progress downward toward the feedline exits");

    assert(overall_height - hoist_hole_y - hoist_face_r
           >= minimum_edge_wall,
           "insufficient wall above the hoist hole");
    assert(crossbar_width / 2 - radiator_hole_x - wire_face_r
           >= minimum_edge_wall,
           "insufficient wall outside a radiator hole");
    assert(relief_hole_y - wire_face_r - crossbar_bottom_y
           >= minimum_edge_wall,
           "insufficient wall below a relief hole");
    assert(stem_width / 2 - feedline_spacing / 2 - wire_face_r
           >= minimum_edge_wall,
           "insufficient wall outside a feedline exit hole");
    assert(feedline_hole_y - wire_face_r >= minimum_edge_wall,
           "insufficient wall below a feedline exit hole");
    assert(
        point_distance(
            [radiator_hole_x, radiator_hole_y],
            [relief_hole_x, relief_hole_y]
        ) - 2 * wire_face_r >= minimum_hole_ligament,
        "insufficient ligament between radiator and relief holes"
    );
    assert(
        point_distance(
            [relief_hole_x, relief_hole_y],
            [feedline_spacing / 2, feedline_hole_y]
        ) - 2 * wire_face_r >= minimum_hole_ligament,
        "insufficient ligament between relief and feedline holes"
    );
    assert(feedline_spacing - 2 * wire_face_r
           >= minimum_hole_ligament,
           "insufficient ligament between feedline exit holes");
    assert(
        point_distance(
            [0, hoist_hole_y],
            [relief_hole_x, relief_hole_y]
        ) - hoist_face_r - wire_face_r >= minimum_hole_ligament,
        "insufficient ligament between hoist and relief holes"
    );

    difference() {
        linear_extrude(height = plate_thickness)
            center_body_2d();

        chamfered_hole(
            0,
            hoist_hole_y,
            hoist_hole_d,
            hoist_hole_chamfer
        );

        mirrored_wire_holes(-1);
        mirrored_wire_holes(1);
    }
}

doublet_center_strain_relief();
