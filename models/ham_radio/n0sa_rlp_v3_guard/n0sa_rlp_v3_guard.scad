/*
 * N0SA RLP V3 magnetic paddle nose guard — fit-test prototype
 *
 * Single-piece, tapered, closed-nose PETG shell protecting the finger pieces.
 * The underside extends as one continuous, STRAIGHT-EDGED tongue beneath the
 * front pair of the RLP's four base magnets. No U-shaped cutout.
 *
 * Coordinates: +Y points toward the paddle tips. The front edge of the rigid
 * body is at Y=0; the underside of its bottom plate is at Z=0.
 *
 * Only the overall envelope and lever projection were measured from photos.
 * Magnet sizes, X/Y positions, body-front location, and lever clearance are
 * provisional; FIRST test without installed magnets or with fit_coupon.
 *
 * Print with the continuous bottom floor on the build plate. In PETG, assess
 * bridging under the roof in your slicer; supports may be needed.
 */

// PART SELECTION
part = "guard";                    // [guard,fit_coupon,magnet_gauge]

// DIMENSIONS FROM OWNER'S CALIPER PHOTOS (mm)
key_width = 36.77;
key_height = 28.92;
paddle_projection = 18.72;

// CLEARANCES AND WALLS (adjust after test fit)
body_side_clearance = 0.65;          // each side at the key-body overlap
body_top_clearance = 0.60;
underbody_gap = 0.25;               // plastic tongue to key underside
floor_thickness = 3.30;
side_wall = 1.80;
roof_wall = 2.00;
nose_wall = 2.00;
tip_clearance = 2.00;               // paddle ends to inside nose wall

// GEOMETRY (only the underside tongue extends this far behind front edge)
back_overlap = 15.2;                // underside overlaps rigid body (Y negative)
shroud_body_overlap = 2.5;          // shroud begins slightly over fixed body
taper_start = 5.5;                  // full-size enclosure over lever roots
tip_outer_width = 32.4;            // outer cross-section at front bumper
tip_outer_top = 26.0;              // relative to underside of key
nose_extra = tip_clearance + nose_wall;
corner_radius = 1.6;               // rounded cross-sections, mm

// EXISTING FRONT-PAIR MAGNET LOCATIONS -- ESTIMATES FROM PHOTO; TUNE THESE
magnet_spacing = 23.0;              // across key, center to center (X)
magnet_y = -8.5;                    // from front edge of rigid plate
// ADD-ON MAGNETS in printed guard -- choose based on magnets you have
insert_diameter = 6.0;
insert_thickness = 2.0;
pocket_diameter_extra = 0.20;        // for PETG tolerance / glue
pocket_depth_extra = 0.15;         // also sets magnet face recess when seated
// keep ~1 mm material below magnet pocket at this thickness

// STOPS: shoulders on the outer edges of the stationary lower plate.
// Carry impact into the rigid body, not the moving paddles.
enable_stop_pads = true;
stop_pad_width = 3.3;
stop_pad_height = 3.2;
stop_pad_depth = 1.6;
stop_pad_back_y = 0.15; // front of body nominally Y=0

// SIDE GUIDES are shallow and deliberately loose; no clip-on force
side_guide_height = 2.2;
side_guide_length = 10.0;

$fn = 48;
eps = 0.03;

// Derived coordinates
inner_root_width = key_width + 2 * body_side_clearance;
outer_root_width = inner_root_width + 2 * side_wall;
inner_root_top = key_height + body_top_clearance;
outer_root_top = inner_root_top + roof_wall;
floor_bottom = -underbody_gap - floor_thickness;
floor_top = -underbody_gap;
outer_tip_top = tip_outer_top;
inner_tip_top = tip_outer_top - roof_wall;
inner_tip_width = tip_outer_width - 2 * side_wall;
outer_tip_y = paddle_projection + nose_extra;
inner_tip_y = outer_tip_y - nose_wall;
back_y = -back_overlap;
shroud_y = -shroud_body_overlap;

pocket_d = insert_diameter + pocket_diameter_extra;
pocket_depth = insert_thickness + pocket_depth_extra;

assert(back_y < magnet_y - pocket_d/2 - 1,
    "Back overlap too short for magnet pockets");
assert(magnet_y + pocket_d/2 < shroud_y + 1.5,
    "Magnet pockets would run into shroud");
assert(pocket_depth < floor_thickness - 0.4,
    "Floor not thick enough under magnet pockets");
assert(inner_tip_width > 0 && inner_tip_top > 0,
    "Tip dimensions must be positive");

module round_rect(w,h,r) {
    // r small enough not to change nominal envelope
    offset(r = r)
        square([w - 2*r, h - 2*r], center = true);
}

module xz_slice(w,z0,z1,y,r=corner_radius) {
    translate([0,y,(z0+z1)/2])
        rotate([90,0,0])
            linear_extrude(height = 0.12, center = true)
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
    // The internal cavity remains away from both levers and their travel.
    union() {
        loft_between(inner_root_width, floor_top, inner_root_top, shroud_y-1,
                     inner_root_width, floor_top, inner_root_top, taper_start);
        loft_between(inner_root_width, floor_top, inner_root_top, taper_start,
                     inner_tip_width, floor_top, inner_tip_top, inner_tip_y);
    }
}

module extension_floor() {
    // A flat, continuous magnetic tongue with a STRAIGHT rear edge.
    // It stops at the shoulder and shares the shroud's existing floor.
    translate([-outer_root_width/2, back_y, floor_bottom])
        cube([outer_root_width, shroud_y-back_y+0.2, floor_thickness]);
}

module loose_side_guides() {
    // Locate against fixed bottom plate edges; not primary retention.
    // Guides do not extend forward into the paddles.
    for (side = [-1,1]) {
        translate([side*(inner_root_width/2 + side_wall/2),
                   back_y + 2.0 + side_guide_length/2,
                   floor_top + side_guide_height/2-0.08])
            cube([side_wall,side_guide_length,side_guide_height],center=true);
    }
}

module fixed_body_stop_pads() {
    // Small end stops at the extreme outer corners of the *fixed* lower
    // plate; no tab crosses the central lever pathway. Check on real key!
    if (enable_stop_pads)
        for (side = [-1,1])
            translate([side*(inner_root_width/2 - stop_pad_width/2),
                       stop_pad_back_y + stop_pad_depth/2,
                       floor_top + stop_pad_height/2 - 0.04])
                cube([stop_pad_width,stop_pad_depth,stop_pad_height],center=true);
}

module magnet_pockets() {
    // Blind pockets accessible from key-facing top of underside tongue.
    // Install magnets with polarities individually matched to attract key magnets.
    for (x = [-magnet_spacing/2,magnet_spacing/2])
        translate([x,magnet_y,
                   floor_top - pocket_depth])
            cylinder(d=pocket_d,h=pocket_depth + eps);
}

module full_guard() {
    difference() {
        union() {
            difference() {
                shroud_outer();
                shroud_inner();
            }
            extension_floor();
            loose_side_guides();
            fixed_body_stop_pads();
        }
        magnet_pockets();
    }
}

module fit_coupon() {
    // Same full-width straight-edged underside tongue, same magnet seats,
    // and same shallow side guides, but omits all paddle-enclosing material.
    difference() {
        union() {
            extension_floor();
            loose_side_guides();
        }
        magnet_pockets();
    }
}

module magnet_gauge() {
    // Optional pocket-size gauge: same thickness, 2 holes with slightly
    // different tolerances for testing the exact magnets before using glue.
    gauge_x=28;
    gauge_y=14;
    difference() {
        translate([-gauge_x/2,-gauge_y/2,floor_bottom])
            cube([gauge_x,gauge_y,floor_thickness]);
        for (x=[-7,7]) { // left: tighter; right (notched edge): looser
            translate([x,0,floor_top - pocket_depth])
                cylinder(d=insert_diameter + pocket_diameter_extra +
                           (x>0 ? 0.20 : -0.10),
                         h=pocket_depth + eps);
        }
        // Small semicircular edge notch identifies the looser (+X) pocket.
        translate([gauge_x/2,0,floor_bottom-eps])
            cylinder(r=1.2,h=floor_thickness+2*eps);
    }
}

if (part=="guard") full_guard();
else if (part=="fit_coupon") fit_coupon();
else if (part=="magnet_gauge") magnet_gauge();
else assert(false,"Unknown part");
