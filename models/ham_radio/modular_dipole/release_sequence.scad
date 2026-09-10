// The second end rises around the first head tops, then the carrier lifts clear.
use <modular_dipole.scad>
preset="40m";
park_angle=4.7; // Render script supplies the measured contact angle.
bulge=preset=="80m" ? 8 : 5;
seat=5+bulge+3;
$fn=96;
support_lift=4*tan(park_angle)+2*(1/cos(park_angle)-1);
color([0.90,0.47,0.19]) render()
    translate([36,0,seat+6]) rotate([0,park_angle,0]) translate([-36,0,-seat-6])
        peel_center(side=1,angle=park_angle,lift=support_lift,release=[3.15,0]);
for(s=[-1,1]) color(s==1 ? [0.12,0.57,0.70] : [0.33,0.65,0.43])
    render() placed_winder(s);
