// Compatibility preset; all geometry lives in the standalone dipole_center.scad.
// Open ../dipole_center/dipole_center.scad for the full Customizer controls.
// N1RWJ / Robert Jackson, CC BY-NC-SA 4.0.
use <../dipole_center/dipole_center.scad>
$fn=96;

dipole_center_part(with_balun_mount=true, coupon_diameters=[9.5,9.7,9.9]);
