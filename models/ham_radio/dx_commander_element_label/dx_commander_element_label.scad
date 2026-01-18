// DX Commander Radiating Element Labels
// Rounded tag with through-hole and raised text.

use <../../../lib/rounded_cube.scad>;

// ---------------------
// Parameters
// ---------------------

// Body size (final, after rounding)
body_length   = 30;  // mm (along the wire / writing side)
body_width    = 12;  // mm (left-right when viewing the text)
body_height   = 12;  // mm (bottom to top when viewing the text)
corner_radius = 1.5; // mm (fillet radius on all edges)

// Wire size
wire_awg                = 19;  // used if wire_outer_d_mm <= 0
wire_outer_d_mm          = 0;   // mm, set to measured OD to override AWG
insulation_thickness_mm  = 0.5; // mm, added to bare diameter on each side
hole_clearance_mm        = 0.4; // mm, extra clearance for easy threading

// Label text
label_index  = 1;    // 0-based index into labels[]
show_all     = true;  // render all labels in a grid
columns      = 3;    // layout columns when show_all = true

text_size    = 9;     // mm, text height in the XY plane
layer_height = 0.2;   // mm, slicer layer height
text_height  = layer_height * 5; // mm, raised text thickness
text_embed   = 0.3;   // mm, sink into body so it bonds to rounded top
text_font    = "DejaVu Sans:style=Bold";

labels = [
    "10m", "12m", "15m", "17m", "20m",
    "30m", "40m", "60m", "80m"
];

// ---------------------
// Helpers
// ---------------------

function awg_bare_d_mm(awg) = 0.127 * pow(92, (36 - awg) / 39);

function wire_outer_d() =
    (wire_outer_d_mm > 0)
        ? wire_outer_d_mm
        : (awg_bare_d_mm(wire_awg) + 2 * insulation_thickness_mm);

function hole_d() = wire_outer_d() + hole_clearance_mm;

module rounded_body_centered() {
    assert(body_length > 2 * corner_radius, "body_length must be > 2 * corner_radius");
    assert(body_width  > 2 * corner_radius, "body_width must be > 2 * corner_radius");
    assert(body_height > 2 * corner_radius, "body_height must be > 2 * corner_radius");

    // Fully rounded edges (no flat/sharp edges).
    rounded_cube(
        size = [
            body_length - 2 * corner_radius,
            body_width - 2 * corner_radius,
            body_height - 2 * corner_radius
        ],
        r = corner_radius,
        center = true
    );
}

module wire_hole_centered() {
    rotate([0, 90, 0])
        cylinder(d = hole_d(), h = body_length + 0.4, center = true, $fn = 48);
}

module label_text_centered(text_value) {
    translate([0, 0, body_height / 2 - text_embed])
        linear_extrude(height = text_height)
            text(
                text = text_value,
                size = text_size,
                font = text_font,
                halign = "center",
                valign = "center"
            );
}

module label_block_centered(text_value) {
    difference() {
        rounded_body_centered();
        wire_hole_centered();
    }

    label_text_centered(text_value);
}

module label_block(text_value) {
    // Keep the model anchored in +X/+Y/+Z for easy layout and STL export.
    translate([body_length / 2, body_width / 2, body_height / 2])
        label_block_centered(text_value);
}

// ---------------------
// Render
// ---------------------

if (show_all) {
    spacing_x = body_length + 4;
    spacing_y = body_width + 4;

    for (i = [0 : len(labels) - 1]) {
        x = (i % columns) * spacing_x;
        y = floor(i / columns) * spacing_y;
        translate([x, y, 0])
            label_block(labels[i]);
    }
} else {
    label_block(labels[label_index]);
}
