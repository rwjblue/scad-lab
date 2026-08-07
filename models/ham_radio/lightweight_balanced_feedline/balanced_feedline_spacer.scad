/*
  models/ham_radio/lightweight_balanced_feedline/balanced_feedline_spacer.scad

  Lightweight snap-on spacer for a two-wire balanced HF feedline.
  Defaults target DXE-SANTW-500 26 AWG Poly-STEALTH wire and 12.7 mm
  (0.5 inch) conductor center spacing.

  Print flat. In service, each wire runs through one C-shaped channel,
  perpendicular to the face of the spacer.
*/

$fn = 48;
eps = 0.02;

// ---------------------------------------------------------------
// Output
// ---------------------------------------------------------------
// "spacer"           - one spacer using the normal parameters
// "channel_fit_test" - five hole-marked spacers varying channel diameter
// "slot_fit_test"    - five slot-marked spacers varying snap-throat width
render_mode = "spacer";

// ---------------------------------------------------------------
// Wire fit and electrical geometry
// ---------------------------------------------------------------
wire_od             = 1.02;  // nominal jacket OD; measure your own spool
wire_spacing        = 12.7;  // conductor center-to-center spacing
channel_clearance   = 0.18;  // diametral clearance added to wire OD
entry_slot_width    = 0.72;  // narrowest part of the snap-in opening
entry_mouth_width   = 1.10;  // lead-in opening at the outside edge

// ---------------------------------------------------------------
// Spacer body
// ---------------------------------------------------------------
body_height         = 3.8;
body_thickness      = 2.4;
end_margin          = 1.8;   // channel edge to outside edge
corner_radius       = 0.8;
cutout_overlap       = 0.04;  // keeps each slot joined cleanly to its channel
minimum_channel_wall = 1.0;

// ---------------------------------------------------------------
// Fit-test layouts
// ---------------------------------------------------------------
// Samples render left-to-right in the listed order. One through five round
// holes identify channel samples; rectangular slots identify throat samples.
fit_test_clearances = [0.08, 0.13, 0.18, 0.23, 0.28];
fit_test_slot_widths = [0.62, 0.67, 0.72, 0.77, 0.82];
fit_test_gap = 4.0;
fit_test_marker_spacing = 1.6;
fit_test_round_marker_d = 1.0;
fit_test_slot_marker_size = [0.9, 1.6];
fit_test_marker_clearance = 1.2;

function channel_d(clearance) = wire_od + clearance;
function body_width(clearance) =
    wire_spacing + channel_d(clearance) + 2 * end_margin;

// Width of the circular channel at a distance `inset` from its tangent.
// The overlap chord must be narrower than the requested throat so the
// `entry_slot_width` parameter remains the actual minimum opening.
function channel_chord(diameter, inset) =
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

// One C-shaped channel cutout. `side` is -1 for the left wire and
// +1 for the right wire, so both snap openings face outward.
module wire_channel_cutout_2d(
    x_center,
    side,
    clearance,
    width,
    slot_width,
    mouth_width
) {
    diameter = channel_d(clearance);
    neck_x = x_center
        + side * (diameter / 2 - cutout_overlap);

    assert(cutout_overlap > 0,
           "cutout_overlap must be positive");
    assert(cutout_overlap + eps / 2 < diameter / 2,
           "cutout_overlap must be smaller than the channel radius");
    assert(
        channel_chord(diameter, cutout_overlap + eps / 2) < slot_width,
        "cutout_overlap is too large to preserve entry_slot_width"
    );

    translate([x_center, 0])
        circle(d = diameter);

    // The small overlap avoids point-contact geometry at the circle tangent.
    // A full-wire-width mouth provides an easy lead-in while the narrower
    // throat supplies retention.
    hull() {
        translate([neck_x, 0])
            square([eps, slot_width], center = true);

        translate([side * (width / 2 + eps), 0])
            square([eps, mouth_width], center = true);
    }
}

module spacer_2d(
    clearance = channel_clearance,
    slot_width = entry_slot_width,
    mouth_width = entry_mouth_width
) {
    diameter = channel_d(clearance);
    width = body_width(clearance);
    channel_wall = (body_height - diameter) / 2;

    assert(wire_od > 0, "wire_od must be positive");
    assert(wire_spacing > diameter,
           "wire_spacing must exceed the channel diameter");
    assert(clearance >= 0, "channel_clearance cannot be negative");
    assert(slot_width > 0, "entry_slot_width must be positive");
    assert(slot_width < wire_od,
           "entry_slot_width must be smaller than wire_od for retention");
    assert(mouth_width >= wire_od,
           "entry_mouth_width must accept the nominal wire diameter");
    assert(mouth_width < body_height - 2 * corner_radius,
           "entry_mouth_width must fit between the rounded corners");
    assert(channel_wall >= minimum_channel_wall,
           "insufficient wall above/below the wire channel");
    assert(end_margin >= 1.2,
           "end_margin is too short for durable snap jaws");
    assert(corner_radius > 0, "corner_radius must be positive");

    difference() {
        rounded_rectangle_2d(width, body_height, corner_radius);

        wire_channel_cutout_2d(
            -wire_spacing / 2,
            -1,
            clearance,
            width,
            slot_width,
            mouth_width
        );

        wire_channel_cutout_2d(
            wire_spacing / 2,
            1,
            clearance,
            width,
            slot_width,
            mouth_width
        );
    }
}

module fit_test_markers(count, style, clearance) {
    diameter = channel_d(clearance);
    marker_width = style == "round"
        ? fit_test_round_marker_d
        : fit_test_slot_marker_size[0];
    marker_height = style == "round"
        ? fit_test_round_marker_d
        : fit_test_slot_marker_size[1];
    marker_span = (count - 1) * fit_test_marker_spacing + marker_width;
    channel_gap = wire_spacing - diameter;

    assert(count >= 1 && count <= 5,
           "fit-test marker count must be from one through five");
    assert(style == "round" || style == "slot",
           "fit-test marker style must be round or slot");
    assert(fit_test_marker_spacing > marker_width,
           "fit-test markers must not overlap");
    assert((body_height - marker_height) / 2 >= minimum_channel_wall,
           "insufficient wall above/below fit-test markers");
    assert((channel_gap - marker_span) / 2
           >= fit_test_marker_clearance,
           "fit-test markers are too close to the wire channels");

    for (i = [0 : count - 1]) {
        marker_x = (i - (count - 1) / 2) * fit_test_marker_spacing;

        if (style == "round")
            translate([marker_x, 0, -eps])
                cylinder(
                    d = fit_test_round_marker_d,
                    h = body_thickness + 2 * eps
                );
        else
            translate([marker_x, 0, body_thickness / 2])
                cube(
                    [
                        fit_test_slot_marker_size[0],
                        fit_test_slot_marker_size[1],
                        body_thickness + 2 * eps
                    ],
                    center = true
                );
    }
}

module balanced_feedline_spacer(
    clearance = channel_clearance,
    slot_width = entry_slot_width,
    mouth_width = entry_mouth_width,
    marker_count = 0,
    marker_style = "round"
) {
    assert(body_thickness > 0, "body_thickness must be positive");

    difference() {
        linear_extrude(height = body_thickness)
            spacer_2d(clearance, slot_width, mouth_width);

        if (marker_count > 0)
            fit_test_markers(marker_count, marker_style, clearance);
    }
}

module channel_fit_test() {
    count = len(fit_test_clearances);
    max_width = body_width(max(fit_test_clearances));
    pitch = max_width + fit_test_gap;

    assert(count > 0, "fit_test_clearances cannot be empty");

    for (i = [0 : count - 1]) {
        clearance = fit_test_clearances[i];
        diameter = channel_d(clearance);

        echo(
            str(
                "channel sample ", i + 1,
                ": channel_clearance=", clearance,
                " mm, channel_d=", diameter, " mm"
            )
        );

        translate([(i - (count - 1) / 2) * pitch, 0, 0])
            balanced_feedline_spacer(
                clearance = clearance,
                marker_count = i + 1,
                marker_style = "round"
            );
    }
}

module slot_fit_test() {
    count = len(fit_test_slot_widths);
    pitch = body_width(channel_clearance) + fit_test_gap;

    assert(count > 0, "fit_test_slot_widths cannot be empty");

    for (i = [0 : count - 1]) {
        slot_width = fit_test_slot_widths[i];

        echo(
            str(
                "slot sample ", i + 1,
                ": entry_slot_width=", slot_width,
                " mm, channel_d=", channel_d(channel_clearance), " mm"
            )
        );

        translate([(i - (count - 1) / 2) * pitch, 0, 0])
            balanced_feedline_spacer(
                slot_width = slot_width,
                marker_count = i + 1,
                marker_style = "slot"
            );
    }
}

assert(
    render_mode == "spacer"
        || render_mode == "channel_fit_test"
        || render_mode == "slot_fit_test",
    str(
        "render_mode must be \"spacer\", \"channel_fit_test\", ",
        "or \"slot_fit_test\""
    )
);

if (render_mode == "spacer")
    balanced_feedline_spacer();
else if (render_mode == "channel_fit_test")
    channel_fit_test();
else
    slot_fit_test();
