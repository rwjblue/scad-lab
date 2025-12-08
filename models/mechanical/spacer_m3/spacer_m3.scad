/*
  models/mechanical/spacer_m3/spacer_m3.scad

  Configurable M3 spacer.
*/

use <../../../lib/rounded_cube.scad>;

hole_d = 3.2;      // clearance for M3
outer_d = 7;       // outer diameter of spacer
height = 10;       // overall height
base_height = 1.5; // optional anti-roll foot height
$fn = 128;         // smooth cylinders

module spacer(hole_d = 3.2, outer_d = 7, height = 10) {
    difference() {
        union() {
            cylinder(d = outer_d, h = height);
            translate([-outer_d / 2, -outer_d / 2, 0])
                rounded_cube([outer_d, outer_d, base_height], r = 1.5);
        }
        translate([0, 0, -1])
            cylinder(d = hole_d, h = height + 2);
    }
}

// Render the spacer
spacer(hole_d = hole_d, outer_d = outer_d, height = height);
