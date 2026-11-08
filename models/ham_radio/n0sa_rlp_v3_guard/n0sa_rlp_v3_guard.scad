/*
 * N0SA RLP V3 magnetic paddle nose guard
 *
 * Single-piece, tapered, closed-nose PETG shell protecting the finger pieces.
 * The whole shell (top, sides, and continuous magnetic underside) ends at
 * the SAME rear plane, just past the front pair of the RLP's four base
 * magnets. No underside projection, notch, or U-shaped cutout.
 *
 * Coordinates: +Y points toward the paddle tips. The front edge of the rigid
 * body is at Y=0; the underside of its bottom plate is at Z=0.
 *
 * Pocket centers match the key's front base magnets. Check paddle clearance
 * and magnet seating on the actual key before bonding the magnets.
 *
 * PRINT ORIENTATION: by default, guard exports nose-down with the closed
 * face against the build plate and the open rear end facing upward.
 * This avoids a ~38 mm unsupported PETG roof bridge. A small ~6 mm
 * magnet-pocket overhang and stop pads remain: check slicer preview.
 */

// PRINT AND INSPECTION ORIENTATION
print_orientation = "nose_down";   // [nose_down,as_used]

// INTERNAL ENVELOPE (mm): these are clearances in the guard, not key specs.
body_internal_width = 38.07;
body_internal_height = 27.07;        // includes clearance for the top screw heads

// MOVING PADDLES: references from the fixed-body front and key underside.
paddle_projection = 27.11;          // body front edge to paddle tips
paddle_top_above_key_base = 25.24;  // top edge of the finger pieces

// FRONT BASE MAGNETS: outside span and edge margin determine centers.
key_magnet_diameter = 6.0;
key_magnet_outer_span = 21.51;
key_magnet_front_margin = 1.5;
// Derived front-pair magnet centers, relative to fixed-body front edge Y=0
magnet_spacing = key_magnet_outer_span - key_magnet_diameter; // 15.51 mm
magnet_y = -(key_magnet_front_margin + key_magnet_diameter/2); // -4.50 mm

// CLEARANCES AND WALLS (mm)
underbody_gap = 0.25;               // continuous floor to key underside
// The thicker floor leaves 1.20 mm of backing below the deepest glue recess.
// Its key-facing surface stays at the underside clearance plane.
production_pocket_depth = 2.95;     // magnet seating depth, not including dimple
magnet_min_floor = 1.20;
glue_relief_diameter = 2.50;
glue_relief_depth = 0.10;           // shallow reservoir, preserves flat seating annulus
floor_thickness = production_pocket_depth + glue_relief_depth + magnet_min_floor;
side_wall = 1.80;
roof_wall = 2.00;
nose_wall = 2.00;
tip_clearance = 2.00;               // paddle ends to inside nose wall
paddle_roof_clearance = 0.50;       // nominal vertical headroom at nose centerline

// GEOMETRY — uniform rear extent for roof, sides, and magnetic underside.
// Rear opening extends 2 mm beyond the far edge of the front base magnets.
// Pocket positions and rear overlap are independent dimensions.
measured_magnet_far_edge = 8.24;
magnet_rear_margin = 2.00;
back_overlap = measured_magnet_far_edge + magnet_rear_margin;  // 10.24 mm
taper_start = 5.5;                  // full-size enclosure over lever roots
tip_outer_width = 32.4;            // outer cross-section at front bumper
tip_ceiling_above_key_base = paddle_top_above_key_base + paddle_roof_clearance;
nose_extra = tip_clearance + nose_wall;  // 27.11 + 2 + 2 = 31.11 mm from front
corner_radius = 1.6;               // rounded cross-sections, mm

// ADD-ON MAGNETS: physically selected 2.95 mm pocket depth.
// Measured 2.96 mm discs can be nominally 0.01 mm proud before adhesive;
// do not automatically add a glue allowance to the selected seating depth.
insert_diameter = 6.0;
pocket_diameter_extra = 0.20;       // 6.20 mm opening for 6 mm discs

// STOPS: shoulders on the outer edges of the stationary lower plate.
// Carry impact into the rigid body, not the moving paddles.
enable_stop_pads = true;
stop_pad_width = 3.3;
stop_pad_height = 3.2;
stop_pad_depth = 1.6;
stop_pad_back_y = 0.15; // 0.15 mm seating travel from the nominal body datum

$fn = 48;
eps = 0.03;
slice_depth = 0.12; // thickness of loft boundary slices

// Derived coordinates
inner_root_width = body_internal_width;
outer_root_width = inner_root_width + 2 * side_wall;
inner_root_top = body_internal_height - underbody_gap;
outer_root_top = inner_root_top + roof_wall;
floor_bottom = -underbody_gap - floor_thickness;
floor_top = -underbody_gap;
inner_tip_top = tip_ceiling_above_key_base;
outer_tip_top = inner_tip_top + roof_wall;
inner_tip_width = tip_outer_width - 2 * side_wall;
outer_tip_y = paddle_projection + nose_extra;
inner_tip_y = outer_tip_y - nose_wall;
back_y = -back_overlap;
shroud_y = back_y;                  // entire shell shares the same rear plane

pocket_d = insert_diameter + pocket_diameter_extra;
pocket_depth = production_pocket_depth;

assert(back_y < magnet_y - pocket_d/2 - 1,
    "Back overlap too short for magnet pockets");
assert(outer_tip_y - nose_wall - paddle_projection >= tip_clearance - 0.01,
    "Nose does not clear measured paddle projection");
assert(magnet_y + pocket_d/2 < 0,
    "Front magnet pocket extends past the fixed body front edge");
assert(pocket_depth > 0, "Magnet pocket depth must be positive");
assert(pocket_depth < floor_thickness - 0.8,
    "Maintain at least 0.8 mm floor below magnet pockets");
assert(production_pocket_depth > 0 && magnet_min_floor > 0 &&
       glue_relief_depth >= 0 && glue_relief_diameter > 0 &&
       glue_relief_diameter <= insert_diameter - 2 &&
       floor_thickness - pocket_depth - glue_relief_depth >= magnet_min_floor - 0.001,
    "Maintain the seating annulus and minimum floor below the glue relief");
assert(inner_root_top > stop_pad_height,
    "Rear opening leaves insufficient clearance above the stops");
assert(inner_tip_width > 0 && inner_tip_top > 0,
    "Tip dimensions must be positive");
assert(paddle_roof_clearance >= 0 &&
       min(inner_root_top,inner_tip_top) >=
           paddle_top_above_key_base + paddle_roof_clearance - 0.001,
    "Centerline roof must clear the paddle top throughout the taper");

module round_rect(w,h,r) {
    // r small enough not to change nominal envelope
    offset(r = r)
        square([w - 2*r, h - 2*r], center = true);
}

module xz_slice(w,z0,z1,y,r=corner_radius) {
    translate([0,y,(z0+z1)/2])
        rotate([90,0,0])
            linear_extrude(height = slice_depth, center = true)
                round_rect(w,z1-z0,min(r,(z1-z0)/3,w/3));
}

module loft_between(w1,z0_1,z1_1,y1,w2,z0_2,z1_2,y2,r=corner_radius) {
    hull() {
        xz_slice(w1,z0_1,z1_1,y1,r);
        xz_slice(w2,z0_2,z1_2,y2,r);
    }
}

module shroud_outer() {
    union() {
        loft_between(outer_root_width, floor_bottom, outer_root_top, shroud_y,
                     outer_root_width, floor_bottom, outer_root_top, taper_start);
        loft_between(outer_root_width, floor_bottom, outer_root_top, taper_start,
                     tip_outer_width, floor_bottom, outer_tip_top, outer_tip_y);
    }
}

module shroud_inner() {
    // Exit the back fully so guard can slide on; stop short of front to close nose.
    // Tapered lever clearance must be verified on the real key at full travel.
    union() {
        loft_between(inner_root_width, floor_top, inner_root_top, shroud_y-1,
                     inner_root_width, floor_top, inner_root_top, taper_start);
        loft_between(inner_root_width, floor_top, inner_root_top, taper_start,
                     inner_tip_width, floor_top, inner_tip_top, inner_tip_y);
    }
}

module fixed_body_stop_pads() {
    // Small end stops at the extreme outer corners of the *fixed* lower
    // plate; no tab crosses the central lever pathway.
    if (enable_stop_pads)
        for (side = [-1,1])
            translate([side*(inner_root_width/2 - stop_pad_width/2),
                       stop_pad_back_y + stop_pad_depth/2,
                       floor_top + stop_pad_height/2 - 0.04])
                cube([stop_pad_width,stop_pad_depth,stop_pad_height],center=true);
}

module magnet_pockets() {
    // Blind pockets retain the magnets, with a shallow center glue recess.
    // Install magnets with polarities individually matched to attract key magnets.
    for (x = [-magnet_spacing/2,magnet_spacing/2]) {
        translate([x,magnet_y,
                   floor_top - pocket_depth])
            cylinder(d=pocket_d,h=pocket_depth + eps);
        if (glue_relief_depth > 0)
            translate([x,magnet_y,floor_top-pocket_depth-glue_relief_depth])
                cylinder(d=glue_relief_diameter,h=glue_relief_depth+eps);
    }
}

module full_guard() {
    difference() {
        union() {
            difference() {
                shroud_outer();
                shroud_inner();
            }
            // No projecting underside tongue: shroud floor, walls and roof
            // all terminate at back_y. Keep only impact stops here.
            fixed_body_stop_pads();
        }
        magnet_pockets();
    }
}

module printable_guard() {
    if (print_orientation == "nose_down") {
        // Rotation about X: new Z = -old Y. Place maximum old Y at Z=0,
        // so the flat closed nose becomes the entire first layer. The big
        // roof now forms one of the vertical walls instead of a long bridge.
        // Translate old Z into nonnegative bed Y for easier slicing.
        translate([0, -floor_bottom, outer_tip_y + slice_depth/2])
            rotate([-90, 0, 0])
                full_guard();
    } else if (print_orientation == "as_used") {
        // Useful for dimensional inspection / visualizing attachment.
        // This orientation needs a ~38 mm roof bridge or supports to print.
        full_guard();
    } else {
        assert(false, "Unknown print_orientation");
    }
}

printable_guard();
