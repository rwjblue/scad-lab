// Modular dipole engineering views, using actual printable geometry.
use <modular_dipole.scad>
use <hardware_mockups.scad>

view="assembled";
preset="40m";
bulge=preset=="80m" ? 8 : 5;
seat=5+bulge+3;
$fn=96;

// These release poses are set from the measured swept path in validate.py.
peel_angle=5.6;
park_angle=4.7;
peel_lift=undef;
park_lift=4*tan(park_angle)+2*(1/cos(park_angle)-1);
release_travel=3.15;

module carrier_pose() {
    if(view=="pinch_right") placed_center(release=[0,release_travel]);
    else if(view=="peel_right") peel_center(side=1,angle=peel_angle,lift=peel_lift,release=[0,release_travel]);
    else if(view=="parked_right") peel_center(side=1,angle=park_angle,lift=park_lift,release=[0,0]);
    else if(view=="pinch_left") peel_center(side=1,angle=park_angle,lift=park_lift,release=[release_travel,0]);
    else if(view=="removed") translate([0,0,18]) placed_center();
    else placed_center();
}

module winder_strap(row) {
    // Reuse the unchanged upper-brace route, shifted with the V3 winder.
    translate([0,row*7,0]) coil_strap(row);
}

module service_tails() {
    // Flexible service-tail suggestion, not a printed routing channel. Keep the
    // bridge crossing inside the pinch faces and 3 mm below the carrier; drop
    // the outer return below the thumb/index approach before entering its bay.
    // The winding-end approach follows the new 26 mm winder offset.
    // Capsule ends extend 0.03 mm to avoid coincident joint seams in STL unions.
    diameter=1.02;
    joint_overlap=0.03;
    for(s=[-1,1]) let(points=[
        [s*39,1.5,seat-0.8],[s*43,-s*12.5,seat-3],
        [s*58,-s*12.5,seat-3],[s*74,-s*17,seat-10],
        [s*74,-s*34,seat-10],[s*53,-s*43,5+bulge]
    ]) color(s==1 ? [0.9,0.22,0.18] : [0.95,0.65,0.12]) union() {
        for(i=[0:len(points)-2]) let(
            a=points[i],b=points[i+1],v=(b-a)/norm(b-a)
        ) hull() {
            translate(a-v*joint_overlap) sphere(d=diameter,$fn=24);
            translate(b+v*joint_overlap) sphere(d=diameter,$fn=24);
        }
    }
}

module crop() { translate([28,-22,seat-2]) cube([29,44,14]); }

if(view=="detail_locked" || view=="detail_squeezed") {
    color([0.90,0.47,0.19]) render() intersection() {
        placed_center(release=view=="detail_squeezed" ? [0,release_travel] : [0,0]);
        crop();
    }
    for(s=[-1,1]) color(s==1 ? [0.12,0.57,0.70] : [0.33,0.65,0.43])
        render() intersection() { placed_winder(s); crop(); }
} else {
    color([0.90,0.47,0.19]) render() carrier_pose();
    for(s=[-1,1]) color(s==1 ? [0.12,0.57,0.70] : [0.33,0.65,0.43])
        render() placed_winder(s,view=="exploded" ? 30 : 0);
    if(view=="assembled" || view=="loaded") {
        hardware();
        service_tails();
    }
    if(view=="loaded") for(s=[-1,1]) {
        %color([0.85,0.15,0.18,0.18]) wire_envelope(s);
        winder_strap(s);
    }
}
