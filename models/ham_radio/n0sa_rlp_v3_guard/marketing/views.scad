// Publication images from the actual V6 source. No unmeasured key-body or
// lever mockup is represented as a verified fit. CLI supplies insert_thickness.
use <../n0sa_rlp_v3_guard.scad>

view = "hero"; // [hero,nose,print_orientation]
$fn = 48; // Match the source's facet count; use<> does not import special variables.

module guard_color() {
    color([0.78,0.35,0.16]) children();
}

if (view == "hero" || view == "nose") {
    guard_color() full_guard();
} else if (view == "print_orientation") {
    guard_color() printable_guard();
} else assert(false,"Unknown publication view");
