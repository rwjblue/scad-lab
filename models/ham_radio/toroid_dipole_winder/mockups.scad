// Default assembly references only: not printable or fit-exact hardware.
use <toroid_dipole_winder.scad>
use <../dipole_winder/dipole_winder.scad>
view="assembly"; // [assembly,loaded,core]
$fn=72;

module tube(points,d=0.9) {
    for(i=[0:len(points)-2]) hull() {
        translate(points[i]) sphere(d=d,$fn=12);
        translate(points[i+1]) sphere(d=d,$fn=12);
    }
}

module packet() {
    // Conservative filled shrink envelope; retention needs no open aperture.
    color([0.12,0.15,0.18]) translate([0,31,6]) cylinder(d=36,h=20);
}

module straps() {
    for(x=[-4,4]) color([0.75,0.78,0.72]) {
        // Side profile extruded to 2.5 mm width. Schematic tie route follows
        // the whole packet; the actual tie conforms to its rounded shoulders.
        translate([x-1.25,0,0]) extrude_x(2.5) difference() {
            polygon([[8,-0.8],[54,-0.8],[54,7],[49,26.8],[13,26.8],[8,7]]);
            polygon([[8.8,0],[53.2,0],[53.2,6.8],[48.4,26],[13.6,26],[8.8,6.8]]);
        }
        translate([x-2,49,-2.5]) cube([4,4,2.5]);
    }
}

module hardware() {
    color([0.66,0.70,0.73]) {
        translate([0,-23.2,15]) extrude_y(11.9) circle(d=12.7);
        translate([0,-8.3,15]) extrude_y(7) circle(d=9.7);
        translate([0,-1.3,15]) extrude_y(5) circle(d=2);
        translate([0,-8.3,15]) extrude_y(2.4) difference() {
            circle(d=18,$fn=6); circle(d=9.7);
        }
        translate([0,-7.9,15]) extrude_y(0.5) difference() {
            hull() { circle(d=12.7); translate([0,12.7]) circle(d=4.8); }
            circle(d=9.7); translate([0,12.7]) circle(d=2.5);
        }
    }
    // Short coax reference. Disconnect coax before winding/stowing antenna.
    color([0.2,0.24,0.27]) translate([0,-43,15]) extrude_y(14) circle(d=3);
    color([0.66,0.7,0.73]) translate([0,-29,15]) extrude_y(6) circle(d=14);
}

module leads() {
    // Routes illustrate slack and splice positions, not winding lengths.
    color([0.8,0.18,0.05]) {
        tube([[0,3.7,15],[8,7,17],[12,16,18]]);
        tube([[10,45,18],[12,51,15],[16,53,8],[20,55.05,5.5]]);
    }
    color([0.1,0.35,0.85]) {
        tube([[0,-7.6,27.7],[-8,3,25],[-12,16,18]]);
        tube([[-10,45,18],[-12,51,15],[-16,53,8],[-20,55.05,5.5]]);
    }
}

module storage_corridors() {
    // 10 mm wide illustrative bundles centred at X ±27. Exact winding
    // placement and capacity require winding the user's actual wire.
    for(x=[-27,27]) color([0.13,0.46,0.66,0.55])
        tube(concat(
            [for(a=[0:10:180]) [x,70+10*sin(a),2.5+10*cos(a)]],
            [for(a=[180:10:360]) [x,-70+10*sin(a),2.5+10*cos(a)]],
            [[x,70,12.5]]),d=10);
}

module winding_reference() {
    color([0.23,0.25,0.28]) difference() {
        cylinder(d=29,h=13.85,center=true);
        cylinder(d=19,h=15,center=true);
    }
    // Two continuous conductors, each making twelve complete passes around
    // the core section while advancing around its circumference. Four ends.
    function winding_point(t,strand) =
        let(phase=4*(t-floor(t)), angle=20+t*27+strand*5,
            radius=phase<1 ? 8.7+6.6*phase : phase<2 ? 15.3 :
                   phase<3 ? 15.3-6.6*(phase-2) : 8.7,
            z=phase<1 ? -7.8 : phase<2 ? -7.8+15.6*(phase-1) :
              phase<3 ? 7.8 : 7.8-15.6*(phase-3))
        [radius*cos(angle),radius*sin(angle),z];
    for(strand=[0,1]) {
        color(strand==0 ? [0.82,0.24,0.07] : [0.15,0.38,0.8]) {
            tube([for(j=[0:384]) winding_point(j/32,strand)],d=0.65);
            tube([winding_point(0,strand),[19,7+strand*2,-9],[25,7+strand*2,-9]],d=0.65);
            tube([winding_point(12,strand),[19,-7+strand*2,-9],[25,-7+strand*2,-9]],d=0.65);
        }
    }
}

if(view=="core") winding_reference();
else {
    color([0.9,0.47,0.2]) toroid_winder();
    color([0.34,0.37,0.38]) translate([-7,16,5]) cube([14,30,1]);
    packet();
    straps();
    hardware();
    leads();
    if(view=="loaded") storage_corridors();
}
