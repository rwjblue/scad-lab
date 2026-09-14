// Assembly illustrations, not printable hardware or a connector fit model.
// The printed body and optional flush contrasting letters are the actual CAD.
// Black wire: DXE-SANTW nominal 1.04 mm OD; ties and connectors are schematic.
use <dipole_link.scad>

view = "in_use"; // [in_use,print_layout,all_bands]
$fn = 64;

wire_d = 1.04;
plate_t = link_thickness();
tie_w = link_tie_width();
tie_t = 1.0;
tie_head = [4.45,4.8,3.7];

module cord(points, diameter=wire_d) {
    for (i = [0:len(points)-2]) hull() {
        translate(points[i]) sphere(d=diameter, $fn=16);
        translate(points[i+1]) sphere(d=diameter, $fn=16);
    }
}

function bezier(a,b,c,d,t) =
    a*pow(1-t,3) + b*3*t*pow(1-t,2) + c*3*t*t*(1-t) + d*t*t*t;

function curve(a,b,c,d,steps=18) =
    [for(i=[0:steps]) bezier(a,b,c,d,i/steps)];

module colored_link(label) {
    color([0.94,0.36,0.075]) render(convexity=8)
        dipole_link(label, component="body");
    // These are the model's genuine second-color components. In a one-color
    // recessed print the letters are left empty instead.
    color([0.12,0.16,0.17]) render(convexity=8)
        dipole_link(label, component="labels");
}

module tie(label, side) {
    tx = link_tie_x(label, side);
    half_neck = link_neck_width()/2;
    head_y = link_width()/2+0.05;
    module wrapped_section() {
        hull() {
            translate([-plate_t/2,0]) offset(r=0.2) offset(delta=-0.2)
                square([plate_t,half_neck*2],center=true);
            translate([-(plate_t+wire_d/2),0]) circle(d=wire_d,$fn=32);
        }
    }
    // Rectangular strap cross-section, rounded around the wire on top.
    // The side head stays clear of the lower connector loop.
    color([0.17,0.20,0.22]) {
        translate([tx-tie_w/2,0,0]) rotate([0,90,0])
            linear_extrude(height=tie_w) difference() {
                // Local 2D coordinates are [-world_Z, world_Y].
                offset(r=tie_t+0.03,$fn=24) wrapped_section();
                offset(r=0.03,$fn=24) wrapped_section();
            }
        // T18R-sized head envelope; keep it clear of the wider shoulders.
        translate([tx-tie_head[0]/2,head_y,(plate_t-tie_head[2])/2])
            cube(tie_head);
        // Short flush-trimmed tail at the head, rather than a snagging whisker.
        translate([tx-tie_w/2,head_y+tie_head[1]-0.1,(plate_t-tie_t)/2])
            cube([tie_w,0.4,tie_t]);
    }
}

module wire_side(label, side, open=false) {
    outer = link_hole_x(label, side, false);
    inner = link_hole_x(label, side, true);
    zfront = plate_t + wire_d/2;
    zback = -wire_d/2 - 0.25;
    endpoint = [side*(open ? 12.0 : 9.0), open ? -14.0 : -12.0, zback];
    // Pass up the OUTER hole, run across the front under the zip tie, and
    // pass down the INNER hole. All straight wire outside the plate is below it.
    points = concat(
        [[side*35,0,zback],[outer+side*1.7,0,zback]],
        curve([outer+side*1.7,0,zback], [outer,0,zback], [outer,0,-0.1], [outer,0,0.65]),
        [[outer,0,plate_t-0.55]],
        curve([outer,0,plate_t-0.55], [outer,0,zfront],
              [outer-side*0.35,0,zfront], [outer-side*1.2,0,zfront]),
        [[inner+side*1.2,0,zfront]],
        curve([inner+side*1.2,0,zfront], [inner,0,zfront],
              [inner,0,plate_t+0.2], [inner,0,plate_t-0.55]),
        [[inner,0,0.4]],
        curve([inner,0,0.4], [inner,0,zback], [inner,-0.4,zback], [inner,-1.3,zback]),
        curve([inner,-1.3,zback], [side*16,-6,zback],
              [side*15,-12,zback], endpoint)
    );
    color([0.08,0.095,0.11]) cord(points);
}

module axial_cylinder(x,length,diameter) {
    translate([x,0,0]) rotate([0,90,0]) cylinder(h=length,d=diameter);
}

module connector_half(side, open=false) {
    // An illustrative 18 x 4 mm joined insulated package; the 2 mm value is
    // the bullet contact, not the outside diameter of heat-shrink insulation.
    outward = open ? 3.0 : 0;
    translate([side*outward,open ? -14 : -12,-wire_d/2-0.25])
        scale([side,1,1]) {
            color([0.10,0.12,0.135]) hull() {
                axial_cylinder(2.0,4.3,3.6);
                axial_cylinder(8.2,0.8,1.8);
            }
            color([0.13,0.15,0.17]) axial_cylinder(0.75,2.0,4.0);
            color([0.70,0.53,0.25]) {
                if(side<0) axial_cylinder(open ? -3.5 : -0.8,open ? 4.25 : 1.55,2.0);
                else difference() {
                    axial_cylinder(open ? -0.8 : 0.05,open ? 1.55 : 0.7,2.6);
                    axial_cylinder(-0.9,1.7,2.05);
                }
            }
        }
}

module assembled_link(label, open=false) {
    colored_link(label);
    for(side=[-1,1]) {
        wire_side(label,side,open);
        tie(label,side);
        connector_half(side,open);
    }
}

module print_set() {
    // Use the actual model's layout and spacing, including the full-band set.
    color([0.94,0.36,0.075]) render(convexity=8)
        dipole_link_layout(component="body");
    color([0.12,0.16,0.17]) render(convexity=8)
        dipole_link_layout(component="labels");
}

if(view=="in_use") {
    translate([0,20,0]) assembled_link("40m");
    translate([0,-20,0]) assembled_link("20m",open=true);
} else if(view=="print_layout") print_set();
else if(view=="all_bands") print_set();
