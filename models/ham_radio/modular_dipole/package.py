#!/usr/bin/env python3
"""Package current modular dipole CAD checks with explicit print names and fit caveats."""
from pathlib import Path
import hashlib
import json
import posixpath
import re
from zipfile import ZipFile, ZIP_DEFLATED

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DOCS = HERE / "review"


def main():
    report = json.loads((HERE / "validation.json").read_text())
    assert report["status"] in {"passed", "passed_with_fit_caveats"}, "Do not package unfinished CAD checks"
    if report["status"] == "passed_with_fit_caveats":
        assert report.get("loaded_fit_status") == "requires_physical_check", "Missing loaded-fit caveat"
    for relative, digest in report["input_sha256"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest, f"Stale validation: {relative}"
    for filename, digest in report["output_sha256"].items():
        assert hashlib.sha256((HERE / filename).read_bytes()).hexdigest() == digest, f"STL changed since validation: {filename}"
    files = {
        "START-HERE/independent-stud-retention-coupon.stl": HERE / "retention_coupon.stl",
        "START-HERE/paired-pinch-coupon.stl": HERE / "fit_coupon.stl",
        "PRINT/center-bnc-10p1-print-one.stl": HERE / "center.stl",
        "PRINT/winder-4mm-standoff-print-two-identical.stl": HERE / "winder.stl",
        "PRINT/OR-complete-three-piece-plate.stl": HERE / "print_layout.stl",
        "optional-bnc-fit-coupon.stl": HERE / "bnc_fit_coupon.stl",
        "READ-ME-FIRST.md": HERE / "README.md",
        "validation.json": HERE / "validation.json",
        "NOTICE.md": HERE / "NOTICE.md",
        "review/DESIGN.md": DOCS / "DESIGN.md",
        "review/parked_audit.json": DOCS / "parked_audit.json",
        "review/retention_audit.json": DOCS / "retention_audit.json",
        "review/hand_clearance_40m.json": DOCS / "hand_clearance_40m.json",
        "review/hand_clearance_80m.json": DOCS / "hand_clearance_80m.json",
    }
    for path in sorted((HERE / "images").iterdir()):
        if path.suffix in {".png", ".svg"}:
            files[f"images/{path.name}"] = path
    for path in [HERE / "modular_dipole.scad", HERE / "native_profile.scad", HERE / "winder_profile.scad",
                 HERE / "mockups.scad", HERE / "hardware_mockups.scad",
                 HERE / "release_sequence.scad", HERE / "validate.py",
                 HERE / "validation_helpers.py", HERE / "parameter_validation.py", DOCS / "parked_audit.py",
                 DOCS / "retention_audit.py",
                 DOCS / "hand_clearance.py",
                 HERE.parent / "dipole_winder/NOTICE.md",
                 HERE.parent / "dipole_winder/frame_bevel.scad",
                 HERE.parent / "dipole_center/dipole_center.scad"]:
        files[f"source/{path.relative_to(ROOT)}"] = path
    checksum = {target: hashlib.sha256(source.read_bytes()).hexdigest() for target, source in files.items()}
    destinations = {source.resolve(): target for target, source in files.items()}
    bundle = HERE / "modular-dipole-STLs.zip"
    with ZipFile(bundle, "w", ZIP_DEFLATED) as archive:
        for name, source in files.items():
            if name.endswith(".md"):
                guide = source.read_text()
                def rewrite(match):
                    link = match.group(1)
                    if "://" in link or link.startswith("#"):
                        return match.group(0)
                    path, separator, fragment = link.partition("#")
                    target = destinations.get((source.parent / path).resolve())
                    assert target is not None, f"Missing bundled link from {source.name}: {link}"
                    relative = posixpath.relpath(target, posixpath.dirname(name) or ".")
                    return f"]({relative}{separator}{fragment})"
                guide = re.sub(r"\]\(([^)]+)\)", rewrite, guide)
                archive.writestr(name, guide)
                checksum[name] = hashlib.sha256(guide.encode()).hexdigest()
            else:
                archive.write(source, name)
        print_guide = """MODULAR DIPOLE — REVISION-2 RETENTION, COMPACT STANDOFFS

COMPACT LOADED FIT IS EXPERIMENTAL. The default supports are 4 mm high for both
wire-space presets, measured from the winder's top surface to the center's
underside. The unchanged wire reservation overlaps the lowered center and
finger clearance is reduced.
The planned static tie route remains clear. Completed dry CAD checks do not
establish actual loaded clearance, comfortable grip or glove access.

Test your actual wound wire and ties. If the center cannot seat freely or the
grip is cramped, increase standoff in the included OpenSCAD source. Its value
is the support height in millimeters, with default 4 and allowed range 2.5–25.
Try 5.5 or 8 mm for more room; the earlier taller 40m/80m supports used 8/11 mm.
Wire-space presets change only the displayed coil and tie reservations. They
do not change the printed parts or the chosen support height.
Print TWO winders with matching settings.
Source: source/models/ham_radio/modular_dipole/modular_dipole.scad

The first print had comfortable springs but failed retention. Use the MATCHED
revision-2 center and TWO revision-2 winders. Do not mix with first-print parts.
The compact setting changes only the supports: an existing revision-2 center
can be reused with the shorter winders.

1. Print START-HERE/independent-stud-retention-coupon.stl. With fingers clear
   of the tabs, shift EACH loose stud outward and pull/rock it. It must stay
   captured, then release freely when pinched. The paired-pinch coupon is
   optional for testing both springs together with a connected stud foot.
2. Use either the three-piece plate OR the separate center plus TWO winders
   from PRINT/. Both wire-space presets use this same print set.
3. Custom support heights still use the SAME center. Do not mix winder heights.
4. BNC hole is 10.1 mm diameter, with the anti-rotation D-flat retained.
5. These parts are separately printed and assembled, not print-in-place.

RELEASE: pinch one end, lift by the fixed bridge, let its catches rest on
the flat stud tops; move the SAME hand to the other end, pinch, raise that end
until the center is level, then lift clear. Allow the supported winders to
settle slightly along their guides during the first lift; do not clamp them
immovably or force the tilted center straight off all posts.
DOCK: pinch each end while seating; flat parking heads require pinch-to-seat.

Revision 2 has not yet passed a physical retention test. Digital checks include
explicit edge/fit loss assumptions; they do not establish holding force.
Test with the actual wire and ties, first on a supported surface, then under
your intended field conditions. Read READ-ME-FIRST.md and the reviews.
"""
        for name in ["PRINT-ORDER.txt", "START-HERE/READ-ME.txt"]:
            archive.writestr(name, print_guide)
            checksum[name] = hashlib.sha256(print_guide.encode()).hexdigest()
        archive.writestr("SHA256.json", json.dumps(checksum, indent=2) + "\n")
    print(bundle)


if __name__ == "__main__":
    main()
