/*
 * N0SA RLP V3 magnetic paddle nose guard — V7 production-print candidate
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
 * November 1: owner selected 2.95 mm pockets for measured 2.96 mm discs.
 * V7 adds blind glue dimples, a thicker floor and a net 2.5 mm reduction
 * in external floor-to-roof height. Proven length, stops and centers stay.
 * Coupons export floor-down; the depth strip defaults to edge-down.
 */

// PART SELECTION
part = "guard";                    // [guard,fit_coupon,magnet_gauge,floor_coupon,depth_gauge,fit_test_plate]
print_orientation = "nose_down";   // [nose_down,as_used] (guard only)
design_revision = "v7";            // [v7,v6] v6 reproduces historical fit parts

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
// Thicken only the bottom, outward from the unchanged key-facing plane.
// The 1.20 mm minimum is measured BELOW the deepest glue dimple.
production_pocket_depth = 2.95;     // owner-selected seating depth, not including dimple
magnet_min_floor = 1.20;
glue_relief_diameter = 2.50;
glue_relief_depth = 0.10;           // shallow reservoir, preserves flat seating annulus
floor_thickness = design_revision == "v7"
    ? production_pocket_depth + glue_relief_depth + magnet_min_floor : 3.30;
shell_height_reduction = 2.50;      // NET external reduction from tested V6
// Extra floor thickness must also be offset by lowering the ceiling.
roof_lowering = design_revision == "v7"
    ? shell_height_reduction + floor_thickness - 3.30 : 0;
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

// ADD-ON MAGNETS: V7 uses the physically selected 2.95 mm pocket depth.
// Measured 2.96 mm discs can be nominally 0.01 mm proud before adhesive;
// do not automatically add a glue allowance to the selected seating depth.
// Set design_revision="v6" and insert_thickness=1.5/2.0 for legacy exports.
insert_diameter = 6.0;
insert_thickness = design_revision == "v7" ? 2.96 : 1.5;
pocket_diameter_extra = 0.20;       // 6.20 mm opening for 6 mm discs
pocket_depth_extra = 0.15;         // 1.65 mm or 2.15 mm pocket
// V6 at floor_thickness=3.30 leaves 1.65 mm / 1.15 mm below its pockets.

// OPEN FLOOR FIT TEST (November 1): the owner reported good magnet diameter,
// alignment and stop contact, but slightly proud magnets and ~2.5 mm excess
// shell height. Length fit then passed, and the owner selected 2.95 mm depth.
// V7 floor coupon uses that seat; V6 reproduces the earlier 2.40 mm trial.
// These controls affect floor_coupon ONLY.
floor_coupon_depth_increase = design_revision == "v7" ? 0 : 0.25;
floor_coupon_marks = true;         // solid: inside nose; dashed: measured tips
floor_coupon_mark_depth = 0.30;
floor_coupon_mark_width = 0.60;

// DEPTH LADDER: owner measured 2.96 mm magnets and confirmed length fit.
// Keep the proven diameter. A separate thicker base leaves at least 1 mm
// of seating annulus. Edge-down puts depth in XY, matching the guard.
depth_gauge_depths = [2.50,2.65,2.80,2.95,3.00];
depth_gauge_base_thickness = 4.00;
depth_gauge_min_floor = 1.00;
depth_gauge_orientation = "edge_down"; // [edge_down,floor_down]
depth_gauge_pitch = 13.0;
depth_gauge_length = 16.0;
depth_gauge_label_height = 0.50;

// TEST PARTS ONLY: push a pin through the underside to recover trial magnets.
// The full guard never receives these holes. Set 0 to disable them in tests.
test_pushout_diameter = 2.0;

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
// Keep the original photo measurement as history; apply the owner's later
// physical height correction separately, at root AND nose to retain taper.
inner_root_top = key_height + body_top_clearance - roof_lowering;
outer_root_top = inner_root_top + roof_wall;
floor_bottom = -underbody_gap - floor_thickness;
floor_top = -underbody_gap;
outer_tip_top = tip_outer_top - roof_lowering;
inner_tip_top = outer_tip_top - roof_wall;
inner_tip_width = tip_outer_width - 2 * side_wall;
outer_tip_y = paddle_projection + nose_extra;
inner_tip_y = outer_tip_y - nose_wall;
back_y = -back_overlap;
shroud_y = back_y;                  // entire shell shares the same rear plane

pocket_d = insert_diameter + pocket_diameter_extra;
pocket_depth = design_revision == "v7"
    ? production_pocket_depth : insert_thickness + pocket_depth_extra;

assert(design_revision == "v7" || design_revision == "v6",
    "Unknown design_revision");
assert(back_y < magnet_y - pocket_d/2 - 1,
    "Back overlap too short for magnet pockets");
assert(outer_tip_y - nose_wall - paddle_projection >= tip_clearance - 0.01,
    "Nose does not clear measured paddle projection");
assert(magnet_y + pocket_d/2 < 0,
    "Front magnet pocket extends past the fixed body front edge");
assert(insert_thickness > 0 && pocket_depth_extra >= 0,
    "Magnet thickness and clearance must be nonnegative");
assert(part=="depth_gauge" || pocket_depth < floor_thickness - 0.8,
    "Maintain at least 0.8 mm floor below magnet pockets");
assert(design_revision != "v7" || part != "guard" ||
       (production_pocket_depth > 0 && magnet_min_floor >= 1.2 &&
        glue_relief_depth >= 0 && glue_relief_diameter > 0 &&
        glue_relief_diameter <= insert_diameter - 2 &&
        floor_thickness - pocket_depth - glue_relief_depth >= magnet_min_floor - 0.001),
    "Maintain the seating annulus and minimum floor below the glue relief");
assert(roof_lowering >= 0 && inner_root_top > stop_pad_height,
    "Height correction leaves insufficient root clearance");
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

module test_magnet_pushout(x,y,bottom=floor_bottom,thickness=floor_thickness) {
    assert(test_pushout_diameter >= 0 &&
           test_pushout_diameter < insert_diameter - 2,
           "Leave at least a 1 mm wide magnet seating ring");
    if (test_pushout_diameter > 0)
        translate([x,y,bottom-eps])
            cylinder(d=test_pushout_diameter,h=thickness+2*eps);
}

module magnet_pockets(depth = pocket_depth, with_pushouts = false,
                      with_glue_relief = false) {
    // Guard pockets are blind; coupons explicitly request underside pin holes.
    // Install magnets with polarities individually matched to attract key magnets.
    for (x = [-magnet_spacing/2,magnet_spacing/2]) {
        translate([x,magnet_y,
                   floor_top - depth])
            cylinder(d=pocket_d,h=depth + eps);
        if (with_glue_relief && glue_relief_depth > 0)
            translate([x,magnet_y,floor_top-depth-glue_relief_depth])
                cylinder(d=glue_relief_diameter,h=glue_relief_depth+eps);
        if (with_pushouts) test_magnet_pushout(x,magnet_y);
    }
}

module floor_coupon_references() {
    if (floor_coupon_marks) {
        assert(floor_coupon_mark_depth > 0 &&
               floor_coupon_mark_depth < floor_thickness - 0.8,
               "Floor reference engraving is too deep");
        // The cavity's last centered loft slice ends 0.06 mm beyond its
        // nominal Y coordinate. Mark the actual central inside nose plane.
        translate([-inner_tip_width/2,
                   inner_tip_y + slice_depth/2 - floor_coupon_mark_width/2,
                   floor_top - floor_coupon_mark_depth])
            cube([inner_tip_width, floor_coupon_mark_width,
                  floor_coupon_mark_depth + eps]);
        // Dashed line is a measured datum, not an assertion of seated fit.
        // Actual tip position shifts when the key seats against the stops.
        for (fraction = [-0.8,-0.4,0,0.4,0.8])
            translate([fraction*inner_tip_width/2 - 1.5,
                       paddle_projection - floor_coupon_mark_width/2,
                       floor_top - floor_coupon_mark_depth])
                cube([3.0, floor_coupon_mark_width,
                      floor_coupon_mark_depth + eps]);
    }
}

module floor_coupon() {
    trial_depth = pocket_depth + floor_coupon_depth_increase;
    assert(floor_coupon_depth_increase >= 0,
           "Floor coupon pocket increase must be nonnegative");
    assert(trial_depth < floor_thickness - 0.8,
           "Maintain at least 0.8 mm below the trial pockets");
    difference() {
        union() {
            // Exact exterior floor from the guard, clipped at its mating
            // surface. No roof, side guides or raised front bumper.
            intersection() {
                shroud_outer();
                translate([-outer_root_width, back_y-1, floor_bottom-eps])
                    cube([2*outer_root_width, outer_tip_y-back_y+2,
                          floor_thickness+eps]);
            }
            fixed_body_stop_pads();
        }
        magnet_pockets(depth=trial_depth,with_pushouts=true);
        floor_coupon_references();
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
        magnet_pockets(with_glue_relief=design_revision=="v7");
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
        magnet_pockets(with_pushouts=true);
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
            test_magnet_pushout(x,0);
        }
        // Small semicircular edge notch identifies the looser (+X) pocket.
        translate([gauge_x/2,0,floor_bottom-eps])
            cylinder(r=1.2,h=floor_thickness+2*eps);
    }
}

function depth_gauge_label(depth) =
    let(hundredths=round(depth*100), fraction=hundredths%100)
        str(floor(hundredths/100),".",fraction<10 ? "0" : "",fraction);

module magnet_depth_gauge() {
    count = len(depth_gauge_depths);
    gauge_width = count * depth_gauge_pitch;
    assert(count > 0 && depth_gauge_pitch > pocket_d + 4,
           "Depth gauge pockets need adequate spacing");
    assert(depth_gauge_length >= pocket_d + 8,
           "Depth gauge needs room for the labels");
    assert(depth_gauge_min_floor >= 0.8,
           "Depth gauge needs at least 0.8 mm of seating material");
    for (depth = depth_gauge_depths)
        assert(depth > 0 &&
               depth <= depth_gauge_base_thickness-depth_gauge_min_floor+0.001,
               "Depth gauge base is too thin for the requested pockets");
    union() {
        difference() {
            linear_extrude(height=depth_gauge_base_thickness)
                round_rect(gauge_width,depth_gauge_length,1.0);
            for (index = [0:count-1]) {
                x = (index-(count-1)/2)*depth_gauge_pitch;
                translate([x,-2,
                           depth_gauge_base_thickness-depth_gauge_depths[index]])
                    cylinder(d=pocket_d,h=depth_gauge_depths[index]+eps);
                test_magnet_pushout(x,-2,bottom=0,
                                    thickness=depth_gauge_base_thickness);
            }
            // Notch identifies the shallow end without relying on the labels.
            translate([-gauge_width/2,0,-eps])
                cylinder(r=1,h=depth_gauge_base_thickness+2*eps);
        }
        for (index = [0:count-1])
            translate([(index-(count-1)/2)*depth_gauge_pitch,3,
                       depth_gauge_base_thickness-eps])
                linear_extrude(height=depth_gauge_label_height+eps)
                    text(depth_gauge_label(depth_gauge_depths[index]),size=2.8,
                         font="Liberation Sans:style=Bold",halign="center");
    }
}

module printable_depth_gauge() {
    if (depth_gauge_orientation == "edge_down") {
        // Upright numbers above the pockets; depth is horizontal print Y.
        translate([0,depth_gauge_base_thickness+depth_gauge_label_height,
                   depth_gauge_length/2])
            rotate([90,0,0]) magnet_depth_gauge();
    } else if (depth_gauge_orientation == "floor_down") {
        magnet_depth_gauge();
    } else assert(false,"Unknown depth_gauge_orientation");
}

module fit_test_plate() {
    // Two separate, flat parts in one STL. A 6 mm gap leaves room for slicing
    // them as individual objects, without breakaway tabs or extra fit surfaces.
    translate([0,0,-floor_bottom]) floor_coupon();
    translate([outer_root_width/2 + 6 +
               len(depth_gauge_depths)*depth_gauge_pitch/2,
               back_y-slice_depth/2+
               (depth_gauge_orientation=="floor_down" ? depth_gauge_length/2 : 0),0])
        printable_depth_gauge();
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
else if (part=="floor_coupon") translate([0,0,-floor_bottom]) floor_coupon();
else if (part=="depth_gauge") printable_depth_gauge();
else if (part=="fit_test_plate") fit_test_plate();
else assert(false,"Unknown part");
