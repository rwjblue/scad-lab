// The second end rises around the first head tops, then the carrier lifts clear.
use <modular_dipole.scad>
preset="40m";
park_angle=4.7; // Render script supplies the measured contact angle.
wire_face_bulge=0;
standoff=4;
bulge=wire_face_bulge==0 ? (preset=="80m" ? 8 : 5) : wire_face_bulge;
seat=dock_seat_height();
$fn=96;
support_lift=dock_support_lift(park_angle);
color([0.90,0.47,0.19]) render()
    translate([36,0,seat+6]) rotate([0,park_angle,0]) translate([-36,0,-seat-6])
        peel_center(side=1,angle=park_angle,lift=support_lift,release=[dock_release_travel(),0]);
for(s=[-1,1]) color(s==1 ? [0.12,0.57,0.70] : [0.33,0.65,0.43])
    render() placed_winder(s);
