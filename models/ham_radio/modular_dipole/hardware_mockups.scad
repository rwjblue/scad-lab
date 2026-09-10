/* Viewing and validation proxies only; no printable model or assembly.
   Hardware and silicone ties are explicit layout assumptions, not exact
   manufacturer solids or a wound-wire simulation. Units millimetres. */
preset = "40m"; // [40m,80m]
bulge = preset == "80m" ? 8 : 5;
seat = 5+bulge+3;
$fn = 96;
// Display allowances only: the seller does not dimension the strap section.
tie_width = 12;
tie_thickness = 2;

module y_cylinder(d,h) {
    rotate([-90,0,0]) cylinder(h=h,d=d);
}

module hardware() {
    // Existing Amphenol cutout/shelf position. Projection and tag are
    // deliberately schematic; actual assembled tag orientation is a fit test.
    translate([0,-19.5,seat]) {
        color([0.62,0.66,0.70]) {
            translate([0,-11.9,14]) y_cylinder(12.7,11.9);
            translate([0,3,14]) y_cylinder(9.7,7);
            translate([0,10,14]) y_cylinder(2,5);
        }
        color([0.80,0.76,0.48]) {
            translate([0,3,14]) y_cylinder(18,2);
            translate([0,3.3,14]) rotate([-90,0,0]) linear_extrude(height=0.5)
                hull() { circle(d=12.7); translate([0,-12.7]) circle(d=4.8); }
        }
        for(x=[-10,10]) {
            color([0.57,0.60,0.64]) translate([x,21,-2.4]) cylinder(d=5.5,h=2.4);
            color([0.64,0.67,0.70]) translate([x,21,4]) cylinder(d=3,h=9.6);
            color([0.70,0.72,0.74]) translate([x,21,4]) cylinder(d=7,h=1);
            color([0.70,0.72,0.74]) translate([x,21,7]) cylinder(d=6,h=2.4,$fn=6);
        }
    }
}

module strap_segment(a,b) {
    hull() for(p=[a,b]) translate(p)
        rotate([0,90,0]) cylinder(d=tie_thickness,h=tie_width,center=true,$fn=20);
}

module coil_strap(side) {
    // UMUST B0B5RM6NLP: short silicone tie, captive at the UPPER crossbrace.
    // Simplified routing proxy, not a measured tie or stretch/closure model.
    // Width/thickness and underside closure are provisional fit allowances.
    translate([0,side*19,0]) rotate([0,0,side<0 ? 180 : 0]) color([0.19,0.22,0.25]) {
        loop=[[0,-3,5+bulge+1],[0,20,5+bulge+1],
              [0,20,-bulge-1],[0,-3,-bulge-1],[0,-3,5+bulge+1]];
        for(i=[0:len(loop)-2]) strap_segment(loop[i],loop[i+1]);
        // Small captive path surrounds the existing 5-by-5 mm upper brace.
        anchor=[[0,-3,-1],[0,5,-1],[0,5,6],[0,-3,6],[0,-3,-1]];
        for(i=[0:len(anchor)-2]) strap_segment(anchor[i],anchor[i+1]);
        // Park the button below the coil, away from carrier and BNC.
        translate([0,17,-bulge-3]) cylinder(d=8,h=2);
    }
}
