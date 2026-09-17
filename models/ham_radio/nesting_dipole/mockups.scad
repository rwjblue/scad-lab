// Engineering previews. Wire, hardware and hook-and-loop strap are schematic.
// The spines lap with the winding bays on opposite sides. Coil turns show a
// representative packing arrangement, not a measured wire-capacity claim.
use <nesting_dipole.scad>
use <winder_profile.scad>

view="assembled"; // [assembled,loaded,exploded,joint,back]
preset="40m";
wire_face_bulge=0;
wing_length=37.5;
winding_span=140;
terminal_hole_x=7;
bulge=wire_face_bulge==0 ? (preset=="80m" ? 8 : 5) : wire_face_bulge;
$fn=96;

module y_cylinder(d,h) { rotate([-90,0,0]) cylinder(d=d,h=h); }

module hardware() {
    center_pose() {
        color([0.65,0.69,0.73]) {
            translate([0,-11.9,14]) y_cylinder(12.7,11.9);
            translate([0,3,14]) y_cylinder(9.7,7);
            translate([0,10,14]) y_cylinder(2,5);
        }
        color([0.8,0.76,0.48]) translate([0,3,14]) y_cylinder(18,2);
        for(x=[-terminal_hole_x,terminal_hole_x]) color([0.65,0.69,0.73]) {
            translate([x,21,-2.4]) cylinder(d=5.5,h=2.4);
            translate([x,21,4]) cylinder(d=3,h=9.6);
            translate([x,21,4]) cylinder(d=7,h=1);
            translate([x,21,7]) cylinder(d=6,h=2.4,$fn=6);
        }
    }
}

module strap_segment(a,b) {
    hull() for(p=[a,b]) translate(p)
        rotate([0,90,0]) cylinder(d=2,h=12,center=true,$fn=24);
}

module coil_strap(row) {
    // Independent coil tie; the rear bundle strap is a different open U.
    winder_pose(row) color([0.30,0.32,0.34]) {
        loop=[[0,-3.6,6+bulge],[0,20,6+bulge],
              [0,20,-bulge-1],[0,-3.6,-bulge-1],[0,-3.6,6+bulge]];
        for(i=[0:len(loop)-2]) strap_segment(loop[i],loop[i+1]);
        translate([0,17,-bulge-3]) cylinder(d=8,h=2);
    }
}

module rounded_loop(w,h,r) {
    difference() {
        offset(r=r) square([w-2*r,h-2*r],center=true);
        offset(r=r-1.2) square([w-2*r,h-2*r],center=true);
    }
}

module wire_turns(row) {
    winder_pose(row) color([0.16,0.18,0.19])
        for(y=[2:1.6:wing_length-7])
            translate([0,y,2.5]) rotate([90,0,0])
                linear_extrude(height=1.15,center=true)
                    rounded_loop(winding_span+4-0.4*y,5+2*bulge,min(6,bulge+1));
}

loaded=view=="loaded" || view=="back";
if(view!="joint") color([0.90,0.48,0.20]) render()
    placed_center(lift=view=="exploded" ? 38 : 0);
for(row=[-1,1]) color(row==1 ? [0.15,0.57,0.71] : [0.35,0.66,0.45]) render()
    placed_winder(row,lift=view=="exploded" && row==-1 ? 18 : 0);
if(loaded) {
    hardware();
    for(row=[-1,1]) {
        wire_turns(row);
        coil_strap(row);
    }
    color([0.45,0.25,0.55]) rear_strap();
}
