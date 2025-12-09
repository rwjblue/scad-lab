//
// 6m Vertical Dipole Center Insulator
// For dual-banana-to-BNC adapter + wire elements
// N1RWJ helper
//

// ---------------------
// Parameters
// ---------------------

plate_width      = 30;   // mm
plate_height     = 80;   // mm
plate_thickness  = 5;    // mm

// Wire holes
wire_hole_d      = 3;    // diameter for 22 AWG with insulation
wire_margin      = 8;    // distance from top/bottom edge to hole center

// Banana adapter slot (approx; tweak if needed)
banana_slot_width  = 22; // left-right opening for adapter body
banana_slot_height = 12; // up-down opening for adapter body
banana_slot_depth  = 4;  // how deep the recess is (into plate thickness)

// Vertical position of slot center (in mm from bottom)
banana_slot_center_y = plate_height / 2;

// Zip-tie holes
zip_hole_d         = 4;  // for typical small zip ties
zip_hole_offset_y  = 10; // vertical spacing above/below slot
zip_hole_edge_margin = 3; // distance from plate side edge

// Optional: mast lash holes (for lashing to mast)
// Turn off if you don't need them
enable_mast_holes = true;
mast_hole_d       = 4;
// Keep these farther from the zip holes to avoid overlap
mast_hole_offset_y = 18;

// ---------------------
// Main model
// ---------------------

difference() {
    // Base plate
    cube([plate_width, plate_height, plate_thickness], center = false);

    // -----------------
    // Wire holes
    // -----------------
    // Top wire hole (upper element)
    translate([plate_width/2, plate_height - wire_margin, plate_thickness/2])
        cylinder(d = wire_hole_d, h = plate_thickness + 0.2, center = true, $fn=32);

    // Bottom wire hole (lower element)
    translate([plate_width/2, wire_margin, plate_thickness/2])
        cylinder(d = wire_hole_d, h = plate_thickness + 0.2, center = true, $fn=32);

    // -----------------
    // Banana adapter slot
    // -----------------
    translate([
        (plate_width - banana_slot_width)/2,
        banana_slot_center_y - banana_slot_height/2,
        0
    ])
        cube([banana_slot_width, banana_slot_height, banana_slot_depth + 0.1], center = false);

    // Through-cut for adapter posts (optional, in case you want them to poke fully through)
    // Centered horizontally, narrower in height
    translate([
        (plate_width - banana_slot_width)/2,
        banana_slot_center_y - banana_slot_height/4,
        0
    ])
        cube([banana_slot_width, banana_slot_height/2, plate_thickness + 0.2], center = false);

    // -----------------
    // Zip-tie holes: one pair above, one pair below the slot
    // -----------------
    // Above slot
    translate([zip_hole_edge_margin, banana_slot_center_y + banana_slot_height/2 + zip_hole_offset_y, plate_thickness/2])
        cylinder(d = zip_hole_d, h = plate_thickness + 0.2, center = true, $fn=24);

    translate([plate_width - zip_hole_edge_margin, banana_slot_center_y + banana_slot_height/2 + zip_hole_offset_y, plate_thickness/2])
        cylinder(d = zip_hole_d, h = plate_thickness + 0.2, center = true, $fn=24);

    // Below slot
    translate([zip_hole_edge_margin, banana_slot_center_y - banana_slot_height/2 - zip_hole_offset_y, plate_thickness/2])
        cylinder(d = zip_hole_d, h = plate_thickness + 0.2, center = true, $fn=24);

    translate([plate_width - zip_hole_edge_margin, banana_slot_center_y - banana_slot_height/2 - zip_hole_offset_y, plate_thickness/2])
        cylinder(d = zip_hole_d, h = plate_thickness + 0.2, center = true, $fn=24);

    // -----------------
    // Mast lash holes (optional)
    // -----------------
    if (enable_mast_holes) {
        // Upper mast lash holes
        translate([zip_hole_edge_margin, plate_height - mast_hole_offset_y, plate_thickness/2])
            cylinder(d = mast_hole_d, h = plate_thickness + 0.2, center = true, $fn=24);

        translate([plate_width - zip_hole_edge_margin, plate_height - mast_hole_offset_y, plate_thickness/2])
            cylinder(d = mast_hole_d, h = plate_thickness + 0.2, center = true, $fn=24);

        // Lower mast lash holes
        translate([zip_hole_edge_margin, mast_hole_offset_y, plate_thickness/2])
            cylinder(d = mast_hole_d, h = plate_thickness + 0.2, center = true, $fn=24);

        translate([plate_width - zip_hole_edge_margin, mast_hole_offset_y, plate_thickness/2])
            cylinder(d = mast_hole_d, h = plate_thickness + 0.2, center = true, $fn=24);
    }
}
