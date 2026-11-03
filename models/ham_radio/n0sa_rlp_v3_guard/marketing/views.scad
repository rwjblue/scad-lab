// CAD illustrations of the guard, using the same source as the STL exports.
use <../n0sa_rlp_v3_guard.scad>

view = "hero"; // [hero,nose,print_orientation,height_coupon]
$fn = 48;

module guard_color() {
    color([0.78,0.35,0.16]) children();
}

if (view == "hero" || view == "nose") {
    guard_color() full_guard();
} else if (view == "print_orientation") {
    guard_color() printable_guard();
} else if (view == "height_coupon") {
    guard_color() printable_height_coupon();
} else assert(false,"Unknown publication view");
