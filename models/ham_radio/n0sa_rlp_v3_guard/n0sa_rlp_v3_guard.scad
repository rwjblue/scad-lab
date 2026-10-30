/*
 * N0SA RLP V3 magnetic paddle nose guard — fit-test prototype
 *
 * Single-piece, tapered, closed-nose PETG shell protecting the finger pieces.
 * The whole shell (top, sides, and continuous magnetic underside) ends at
 * the SAME rear plane, just past the front pair of the RLP's four base
 * magnets. No underside projection, notch, or U-shaped cutout.
 *
 * Coordinates: +Y points toward the paddle tips. The front edge of the rigid
 * body is at Y=0; the underside of its bottom plate is at Z=0.
 *
 * Owner print fit report October 30: overall envelope and magnet alignment
 * looked good; the front nose was too short. Paddle tip projection is now
 * measured from the same fixed-body front edge as the key shell: 27.11 mm.
 * The far edge of the front magnets was measured 8.24 mm behind that edge.
 * Existing pocket centers are intentionally UNCHANGED because they aligned
 * in the first printed trial. Check all clearances before gluing magnets.
 *
 * PRINT ORIENTATION: by default, guard exports nose-down with the closed
 * face against the build plate and the open rear end facing upward.
 * This avoids a ~38 mm unsupported PETG roof bridge. A small ~6 mm
 * magnet-pocket overhang and stop pads remain: check slicer preview.
 * Coupons/gauges always export flat with their bottom against the bed.
 */

// PART SELECTION
part = "guard";                    // [guard,fit_coupon,magnet_gauge]
print_orientation = "nose_down";   // [nose_down,as_used] (guard only)

// DIMENSIONS FROM OWNER'S CALIPER PHOTOS (mm)
key_width = 36.77;
key_height = 28.92;
paddle_projection = 27.11;          // owner-measured from body front edge to paddle tips

// OWNER'S OCT 30 CALIPER MEASUREMENTS: the pair nearest the paddles.
// Span = from outside edge of one magnet to outside edge of the other.
// The edge margin is from the key's *front plastic edge* to the nearer
// circumferential edge of each magnet. Confirm this coordinate datum on
// the physical key before gluing the magnets.
key_magnet_diameter = 6.0;
key_magnet_outer_span = 21.51;
key_magnet_front_margin = 1.5;
// Derived front-pair magnet centers, relative to fixed-body front edge Y=0
magnet_spacing = key_magnet_outer_span - key_magnet_diameter; // 15.51 mm
magnet_y = -(key_magnet_front_margin + key_magnet_diameter/2); // -4.50 mm

// CLEARANCES AND WALLS (adjust after test fit)
body_side_clearance = 0.65;          // each side at the key-body overlap
body_top_clearance = 0.60;
underbody_gap = 0.25;               // continuous floor to key underside
floor_thickness = 3.30;
side_wall = 1.80;
roof_wall = 2.00;
nose_wall = 2.00;
tip_clearance = 2.00;               // paddle ends to inside nose wall

// GEOMETRY — uniform rear extent for roof, sides, and magnetic underside.
// Owner's October 30 measurement: 8.24 mm from fixed-body front edge to
// FAR edge of the existing front magnet. Add a 2 mm rearward shell margin.
// Intentionally do NOT infer new pocket centers from this: the actual V5
// magnet pockets were reported to line up. Previous near-edge measurement
// was approximate and differs from this far-edge measurement by 0.74 mm.
measured_magnet_far_edge = 8.24;
magnet_rear_margin = 2.00;
back_overlap = measured_magnet_far_edge + magnet_rear_margin;  // 10.24 mm
taper_start = 5.5;                  // full-size enclosure over lever roots
tip_outer_width = 32.4;            // outer cross-section at front bumper
tip_outer_top = 26.0;              // relative to underside of key
nose_extra = tip_clearance + nose_wall;  // 27.11 + 2 + 2 = 31.11 mm from front
corner_radius = 1.6;               // rounded cross-sections, mm

// ADD-ON MAGNETS: owner has N48 6 x 1.5 mm and 6 x 2.0 mm discs.
// Default is 6 x 1.5 mm. Use -D 'insert_thickness=2.0' for 6 x 2 mm.
// Pocket depth is magnet thickness + 0.15 mm for glue/print tolerance.
insert_diameter = 6.0;
insert_thickness = 1.5;
pocket_diameter_extra = 0.20;       // 6.20 mm opening for 6 mm discs
pocket_depth_extra = 0.15;         // 1.65 mm or 2.15 mm pocket
// At floor_thickness=3.30, remaining floor = 1.65 mm / 1.15 mm.
// Both inserts have the same face recess when fully seated.


// STOPS: shoulders on the outer edges of the stationary lower plate.
// Carry impact into the rigid body, not the moving paddles.
enable_stop_pads = true;
stop_pad_width = 3.3;
stop_pad_height = 3.2;
stop_pad_depth = 1.6;
stop_pad_back_y = 0.15; // 0.15 mm seating travel from the nominal body datum

// SIDE GUIDES are shallow and deliberately loose; no clip-on force
side_guide_height = 2.2;
side_guide_length = 10.0;

$fn = 48;
eps = 0.03;
slice_depth = 0.12; // thickness of loft boundary slices

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
shroud_y = back_y;                  // entire shell shares the same rear plane

pocket_d = insert_diameter + pocket_diameter_extra;
pocket_depth = insert_thickness + pocket_depth_extra;

assert(back_y < magnet_y - pocket_d/2 - 1,
    "Back overlap too short for magnet pockets");
assert(outer_tip_y - nose_wall - paddle_projection >= tip_clearance - 0.01,
    "Nose does not clear measured paddle projection");
assert(magnet_y + pocket_d/2 < 0,
    "Front magnet pocket extends past the fixed body front edge");
assert(insert_thickness > 0 && pocket_depth_extra >= 0,
    "Magnet thickness and clearance must be nonnegative");
assert(pocket_depth < floor_thickness - 0.8,
    "Maintain at least 0.8 mm floor below magnet pockets");
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

module coupon_floor(front_y = 0) {
    // Flat, straight-edged underside plate for the fit-test coupon ONLY.
    // The full guard already has a continuous floor across its whole length.
    // Coupon extends to Y=0 so magnet pockets remain fully enclosed.
    translate([-outer_root_width/2, back_y, floor_bottom])
        cube([outer_root_width, front_y-back_y, floor_thickness]);
}

module coupon_side_guides(front_limit = 0) {
    // Coupon-only side guides check the fit against the fixed bottom plate.
    // The full guard has continuous, full-height side walls instead.
    guide_start_y = back_y + 2.0;
    guide_length = min(side_guide_length, front_limit-guide_start_y);
    assert(guide_length > 0, "Side guide length too small");
    for (side = [-1,1]) {
        translate([side*(inner_root_width/2 + side_wall/2),
                   guide_start_y + guide_length/2,
                   floor_top + side_guide_height/2-0.08])
            cube([side_wall,guide_length,side_guide_height],center=true);
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
    // Blind pockets accessible from the key-facing surface of the common floor.
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
            // No projecting underside tongue: shroud floor, walls and roof
            // all terminate at back_y. Keep only impact stops here.
            fixed_body_stop_pads();
        }
        magnet_pockets();
    }
}

module fit_coupon() {
    // Same full-width floor overlap and magnet seats,
    // and same shallow side guides, but omits all paddle-enclosing material.
    difference() {
        union() {
            coupon_floor(front_y=0);
            coupon_side_guides(front_limit=0);
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

if (part=="guard") printable_guard();
else if (part=="fit_coupon") translate([0,0,-floor_bottom]) fit_coupon();
else if (part=="magnet_gauge") translate([0,0,-floor_bottom]) magnet_gauge();
else assert(false,"Unknown part");
