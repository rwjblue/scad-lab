/*
  N1RWJ open-mount 1:1 current-balun winder, September 2026.
  PRINT orientation: back at Z=0; +Y up, +Z forward in service.
  K6ARK-derived winding outline; see NOTICE.md and ../dipole_winder/.
  Default core: Fair-Rite 2631801202, 29 x 19 x 13.85 mm, mix 31.
  Wound/shrunk envelope is a fit allowance, not a measured assembly.
  Antenna load goes through the six original holes, never through the core.
*/

use <../dipole_winder/dipole_winder.scad>
use <../dipole_winder/frame_bevel.scad>
use <../dipole_winder/reference_profile.scad>

/* [Output] */
part = "winder"; // [winder,mount_coupon]
show_package = false; // F5 only; this reference never enters an STL

/* [Finished toroid package] */
// Measure AFTER winding and heatshrinking. Includes all insulation.
package_d = 36; // [32:0.5:38]
package_h = 20; // [16:0.5:22]
foam_t = 1; // [0.5:0.5:2]

/* [BNC fit] */
bnc_hole_d = 10.1; // [9.7:0.05:10.3]
bnc_flat_depth = 0.85; // [0:0.05:1.2]
// Estimated projection ABOVE shelf, including the solder cup; measure yours.
bnc_rear_projection = 12; // [8:0.5:16]

/* [Hidden] */
$fn=96;
eps=0.02;
frame_t=5;
core_y=31;
tie_x=4;
tie_y=package_d/2+4;
tie_slot_w=3.4;
tie_slot_h=2.4;
tie_chamfer=0.3;
spine_w=18;
shelf_t=3;
shelf_w=26;
bnc_z=15;
hardware_r=9;
shelf_depth=24;
// Reserve 3.8 mm from rear contact to the nearest tie-slot mouth.
shelf_top=core_y-tie_y-tie_slot_h/2-tie_chamfer-3.8-bnc_rear_projection;
shelf_bottom=shelf_top-shelf_t;
spine_bottom=shelf_bottom-12;
spine_top=core_y+tie_y+4;

assert(part=="winder" || part=="mount_coupon", "Unknown part");
assert(package_d>=32 && package_d<=38, "Package diameter must be 32–38 mm");
assert(package_h>=16 && package_h<=22, "Package thickness must be 16–22 mm");
assert(foam_t>=0.5 && foam_t<=2, "Use 0.5–2 mm cushioning");
assert(bnc_hole_d>=9.7 && bnc_hole_d<=10.3, "BNC hole must be 9.7–10.3 mm");
assert(bnc_flat_depth>=0 && bnc_flat_depth<=1.2, "BNC flat depth must be 0–1.2 mm");
assert(bnc_rear_projection>=8 && bnc_rear_projection<=16, "Rear projection must be 8–16 mm");
assert(core_y+package_d/2 <= 51, "Keep package below antenna strain relief");
assert(spine_top < 59, "Keep strap support below the hoisting eye");
assert(spine_w/2-tie_x-tie_slot_w/2-tie_chamfer-0.5 >= 2,
       "Keep 2 mm of material outside tie-slot chamfers");

module round_rectangle(w,h,r=2) {
    offset(r=r) square([w-2*r,h-2*r],center=true);
}

module tie_slot() {
    translate([0,0,-eps]) linear_extrude(frame_t+2*eps)
        square([tie_slot_w,tie_slot_h],center=true);
    for(top=[false,true])
        translate([0,0,top ? frame_t : 0]) scale([1,1,top ? -1 : 1])
            hull() {
                translate([0,0,-eps]) linear_extrude(eps)
                    square([tie_slot_w+2*tie_chamfer,tie_slot_h+2*tie_chamfer],center=true);
                translate([0,0,tie_chamfer]) linear_extrude(eps)
                    square([tie_slot_w,tie_slot_h],center=true);
            }
}

module base_outline() {
    // Union in 2D BEFORE beveling. Uniting already-beveled plates creates
    // near-coincident triangles at the mount roots in binary STL export.
    native_paths=reference_paths();
    suppressed=[2,4,5,6,8,9,10];
    union() {
        polygon(points=reference_points(),paths=[for(i=[0:len(native_paths)-1])
            if(len(search(i,suppressed))==0) native_paths[i]],convexity=12);
        translate([0,(spine_bottom+spine_top)/2])
            round_rectangle(spine_w,spine_top-spine_bottom);
        translate([-12,shelf_bottom-10]) square([24,10+eps]);
        translate([-13,shelf_bottom]) square([26,shelf_t]);
    }
}

module base_frame() {
    difference() {
        beveled_frame(height=frame_t,bevel=0.5) base_outline();
        translate([0,63,0]) plate_hole(6,0.5);
        for(side=[-1,1],i=[0:2]) {
            p=relief_center(i,side);
            translate([p[0],p[1],0]) plate_hole(3.2,0.5);
        }
    }
}

module panel_profile() {
    polygon([[-13,0],[13,0],[13,22],[11,24],[-11,24],[-13,22]]);
}

module connector_hole() {
    intersection() {
        circle(d=bnc_hole_d);
        translate([-20,-20]) square([40,20+bnc_hole_d/2-bnc_flat_depth]);
    }
}

module connector_mount() {
    translate([0,shelf_bottom,0]) difference() {
        extrude_y(shelf_t) panel_profile();
        translate([0,-eps,bnc_z]) extrude_y(shelf_t+2*eps) connector_hole();
    }
    // The joined base includes the rib feet. Start ribs in its full-thickness
    // middle band, below the bevel, and keep the back root inside that foot.
    difference() {
        for(side=[-1,1]) translate([side*10.5-1.5,0,0]) extrude_x(3)
            polygon([[shelf_bottom+eps,4],[shelf_bottom-9.4,4],
                     [shelf_bottom+eps,15]]);
        translate([0,shelf_bottom-10-eps,bnc_z]) extrude_y(10+2*eps)
            circle(r=hardware_r/cos(180/$fn));
    }
}

module toroid_winder() {
    difference() {
        union() {
            base_frame(); // Original horns and seven chamfered holes.
            connector_mount();
        }
        for(x=[-tie_x,tie_x], y=[core_y-tie_y,core_y+tie_y])
            translate([x,y,0]) tie_slot();
    }
}

module mount_coupon() {
    // Full real mounting area, cropped through broad frame; tests connector,
    // straps and finished packet fit together before the whole winder print.
    translate([0,-spine_bottom,0]) intersection() {
        toroid_winder();
        translate([-14,spine_bottom,-eps])
            cube([28,spine_top-spine_bottom,40]);
    }
}

if(part=="mount_coupon") mount_coupon();
else {
    color([0.9,0.47,0.2]) toroid_winder();
    if(show_package && $preview)
        %translate([0,core_y,frame_t+foam_t]) cylinder(d=package_d,h=package_h);
}
