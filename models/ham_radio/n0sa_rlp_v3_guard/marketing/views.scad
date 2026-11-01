// CAD illustrations of the guard, using the same source as the STL exports.
use <../n0sa_rlp_v3_guard.scad>

view = "hero"; // [hero,nose,print_orientation]
$fn = 48;

module guard_color() {
    color([0.78,0.35,0.16]) children();
}

if (view == "hero" || view == "nose") {
    guard_color() full_guard();
} else if (view == "print_orientation") {
    guard_color() printable_guard();
} else assert(false,"Unknown publication view");
