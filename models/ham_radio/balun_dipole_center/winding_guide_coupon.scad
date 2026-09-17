// Small printer qualification section of the original .100 mm-gap guide.
// Exact channel/wall geometry, same covered-face-down orientation as full STL.
// A successful slice does not prove a .100 mm physical enamel surface gap.
use <winding_guide.scad>
$fn=128;
coupon_width=4;

translate([-(wg_diameter()/2+(19/2-.15-.724228))/2,0,wg_top()])
    rotate([180,0,0]) rotate([0,0,-wg_angle(1)]) intersection() {
        winding_guide();
        rotate([0,0,wg_angle(1)]) translate([0,-coupon_width/2,-1])
            cube([wg_diameter()/2+2,coupon_width,wg_top()+2]);
    }
