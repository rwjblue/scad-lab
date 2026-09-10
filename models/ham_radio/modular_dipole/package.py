#!/usr/bin/env python3
"""Package only a current, fully passing modular dipole export with explicit print names."""
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
    assert report["status"] == "passed", "Do not package unfinished CAD checks"
    for relative, digest in report["input_sha256"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest, f"Stale validation: {relative}"
    for filename, digest in report["output_sha256"].items():
        assert hashlib.sha256((HERE / filename).read_bytes()).hexdigest() == digest, f"STL changed since validation: {filename}"
    files = {
        "START-HERE/paired-pinch-coupon.stl": HERE / "fit_coupon.stl",
        "40m/center-bnc-10p1-print-one.stl": HERE / "center.stl",
        "40m/winder-print-two-identical.stl": HERE / "winder.stl",
        "40m/OR-complete-three-piece-plate.stl": HERE / "print_layout.stl",
        "optional-80m/winder-print-two-identical.stl": HERE / "winder_80m.stl",
        "optional-80m/OR-complete-three-piece-plate.stl": HERE / "print_layout_80m.stl",
        "optional-bnc-fit-coupon.stl": HERE / "bnc_fit_coupon.stl",
        "READ-ME-FIRST.md": HERE / "README.md",
        "validation.json": HERE / "validation.json",
        "NOTICE.md": HERE / "NOTICE.md",
        "review/DESIGN.md": DOCS / "DESIGN.md",
        "review/parked_audit.json": DOCS / "parked_audit.json",
        "review/hand_clearance_40m.json": DOCS / "hand_clearance_40m.json",
        "review/hand_clearance_80m.json": DOCS / "hand_clearance_80m.json",
    }
    for path in sorted((HERE / "images").iterdir()):
        if path.suffix in {".png", ".svg"}:
            files[f"images/{path.name}"] = path
    for path in [HERE / "modular_dipole.scad", HERE / "native_profile.scad",
                 HERE / "mockups.scad", HERE / "hardware_mockups.scad",
                 HERE / "release_sequence.scad", HERE / "validate.py",
                 HERE / "validation_helpers.py", DOCS / "parked_audit.py",
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
                    target = destinations.get((source.parent / link).resolve())
                    assert target is not None, f"Missing bundled link from {source.name}: {link}"
                    relative = posixpath.relpath(target, posixpath.dirname(name) or ".")
                    return f"]({relative})"
                guide = re.sub(r"\]\(([^)]+)\)", rewrite, guide)
                archive.writestr(name, guide)
                checksum[name] = hashlib.sha256(guide.encode()).hexdigest()
            else:
                archive.write(source, name)
        archive.writestr("PRINT-ORDER.txt", """MODULAR DIPOLE — FOUR CATCHES, TWO IDENTICAL WINDERS

1. Print START-HERE/paired-pinch-coupon.stl and test the paired release.
2. Use either the three-piece plate OR the separate center plus TWO winders.
3. The optional 80m winders use the SAME center. Do not mix winder heights.
4. BNC hole is 10.1 mm diameter, with the anti-rotation D-flat retained.
5. These parts are separately printed and assembled, not print-in-place.

RELEASE: pinch one end, lift by the fixed bridge, let its catches rest on
the flat stud tops; move the SAME hand to the other end, pinch, raise that end
until the center is level, then lift clear. Allow the supported winders to
settle slightly along their guides during the first lift; do not clamp them
immovably or force the tilted center straight off all posts.
DOCK: pinch each end while seating; flat parking heads require pinch-to-seat.

The digital checks establish geometry, not a physical one-hand or glove test.
Test with the actual wire and ties, first on a supported surface, then under
your intended field conditions. Read READ-ME-FIRST.md and the reviews.
""")
        checksum["PRINT-ORDER.txt"] = hashlib.sha256(archive.read("PRINT-ORDER.txt")).hexdigest()
        archive.writestr("SHA256.json", json.dumps(checksum, indent=2) + "\n")
    print(bundle)


if __name__ == "__main__":
    main()
