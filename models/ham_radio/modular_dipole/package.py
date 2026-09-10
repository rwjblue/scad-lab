#!/usr/bin/env python3
"""Build curated print and editable-source downloads from current validated CAD."""
from pathlib import Path
import hashlib
import json
import posixpath
import re
import struct
import subprocess
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DOCS = HERE / "review"
CORE_SOURCE = [
    HERE / "modular_dipole.scad",
    HERE / "winder_profile.scad",
    HERE / "native_profile.scad",
    HERE.parent / "dipole_winder/frame_bevel.scad",
    HERE.parent / "dipole_center/dipole_center.scad",
]
NOTICES = [HERE / "NOTICE.md", HERE.parent / "dipole_winder/NOTICE.md"]
PUBLIC_IMAGES = ["assembled", "exploded", "print_layout", "retention_coupon",
                 "release_explainer"]
PRINT_FILES = ["center.stl", "winder.stl", "print_layout.stl",
               "retention_coupon.stl", "bnc_fit_coupon.stl"]
MARKDOWN_LINK = re.compile(r"\]\(([^)]+)\)")
REPOSITORY_ONLY = {
    (DOCS / "DESIGN.md").resolve(),
    (HERE / "validation.json").resolve(),
    (HERE / "fit_coupon.stl").resolve(),
}
REPOSITORY_URL = "https://github.com/rwjblue/scad-lab/blob/main/"


def checked_validation():
    report = json.loads((HERE / "validation.json").read_text())
    assert report["status"] in {"passed", "passed_with_fit_caveats"}, "Do not package unfinished CAD checks"
    if report["status"] == "passed_with_fit_caveats":
        assert report.get("loaded_fit_status") == "requires_physical_check", "Missing loaded-fit caveat"
    assert report["input_sha256"] and report["output_sha256"], "Missing validation hashes"
    for relative, digest in report["input_sha256"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest, f"Stale validation: {relative}"
    for filename, digest in report["output_sha256"].items():
        assert hashlib.sha256((HERE / filename).read_bytes()).hexdigest() == digest, f"STL changed since validation: {filename}"
    assert set(PRINT_FILES) <= set(report["output_sha256"]), "A distributed STL lacks validation"
    assert {str(path.relative_to(ROOT)) for path in CORE_SOURCE} <= set(report["input_sha256"]), \
        "An editable CAD dependency lacks validation"
    return report


def local_link(link):
    return not (re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", link) or link.startswith("#"))


def archive_payloads(files):
    """Resolve repository-relative Markdown links to the curated archive layout."""
    destinations = {source.resolve(): target for target, source in files.items()}
    flyer = destinations.get((ROOT / "output/pdf/modular-dipole-flyer.pdf").resolve())
    if flyer:
        # In the repository the flyer link opens its regeneration notes. A
        # printable download should open the bundled PDF directly instead.
        destinations[(HERE / "marketing/README.md").resolve()] = flyer
    payloads = {}
    for name, source in files.items():
        assert source.is_file(), f"Missing distribution input: {source}"
        if name.endswith(".md"):
            def rewrite(match):
                link = match.group(1)
                if not local_link(link):
                    return match.group(0)
                path, separator, fragment = link.partition("#")
                resolved = (source.parent / path).resolve()
                target = destinations.get(resolved)
                if target is None and resolved in REPOSITORY_ONLY:
                    assert resolved.is_file(), f"Missing repository-only link: {link}"
                    return f"]({REPOSITORY_URL}{resolved.relative_to(ROOT)}{separator}{fragment})"
                assert target is not None, f"Missing bundled link from {source.name}: {link}"
                relative = posixpath.relpath(target, posixpath.dirname(name) or ".")
                return f"]({relative}{separator}{fragment})"
            payloads[name] = MARKDOWN_LINK.sub(rewrite, source.read_text()).encode()
        else:
            payloads[name] = source.read_bytes()
    return payloads


def write_archive(path, payloads):
    checksum = {name: hashlib.sha256(data).hexdigest() for name, data in payloads.items()}
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        for name, data in payloads.items():
            archive.writestr(name, data)
        archive.writestr("SHA256.json", json.dumps(checksum, indent=2) + "\n")
    verify_archive(path)


def verify_archive(path):
    """Check the actual ZIP bytes, inventory, and every local Markdown target."""
    with ZipFile(path) as archive:
        names = archive.namelist()
        assert len(names) == len(set(names)), f"Duplicate ZIP members in {path.name}"
        checksums = json.loads(archive.read("SHA256.json"))
        assert set(checksums) == set(names) - {"SHA256.json"}, "Incomplete archive checksums"
        for name, digest in checksums.items():
            data = archive.read(name)
            assert hashlib.sha256(data).hexdigest() == digest, f"Archive hash mismatch: {name}"
            if name.endswith(".md"):
                for match in MARKDOWN_LINK.finditer(data.decode()):
                    link = match.group(1)
                    if local_link(link):
                        target = posixpath.normpath(posixpath.join(
                            posixpath.dirname(name), link.partition("#")[0]))
                        assert target in checksums, f"Broken archive link: {name} -> {link}"


def check_editable_archive(path):
    """Prove that the source download alone can export the complete print plate."""
    with tempfile.TemporaryDirectory(prefix="modular-dipole-source-check-") as directory:
        work = Path(directory)
        with ZipFile(path) as archive:
            archive.extractall(work)
        source = work / "models/ham_radio/modular_dipole/modular_dipole.scad"
        output = work / "print-layout.stl"
        completed = subprocess.run([
            "openscad", "--backend=Manifold", "--hardwarnings", "--export-format", "binstl",
            "-D", 'part="print_layout"', "-o", str(output), str(source),
        ], capture_output=True, text=True)
        assert completed.returncode == 0 and "ERROR:" not in completed.stderr and \
            "WARNING:" not in completed.stderr, f"Editable source does not compile:\n{completed.stderr}"
        data = output.read_bytes()
        assert len(data) >= 84, "Editable source produced an empty STL"
        triangles = struct.unpack_from("<I", data, 80)[0]
        assert triangles > 0 and len(data) == 84 + triangles * 50, "Invalid binary STL export"
        print(f"Editable source archive compiled successfully ({triangles:,} triangles).")


def main():
    checked_validation()
    files = {name: HERE / name for name in PRINT_FILES}
    files.update({
        "README.md": HERE / "README.md",
        "NOTICE.md": HERE / "NOTICE.md",
        "BUILD.md": DOCS / "BUILD.md",
        "modular-dipole-flyer.pdf": ROOT / "output/pdf/modular-dipole-flyer.pdf",
    })
    files.update({f"images/{name}.png": HERE / f"images/{name}.png" for name in PUBLIC_IMAGES})
    for path in [*CORE_SOURCE, NOTICES[1]]:
        files[f"source/{path.relative_to(ROOT)}"] = path
    print_payloads = archive_payloads(files)

    source_files = {str(path.relative_to(ROOT)): path for path in [*CORE_SOURCE, *NOTICES]}
    source_payloads = archive_payloads(source_files)
    source_payloads["README.txt"] = """MODULAR DIPOLE — EDITABLE OPENSCAD SOURCE

Open models/ham_radio/modular_dipole/modular_dipole.scad in OpenSCAD.
Keep the models/ folder structure intact: the main model uses the neighboring
dipole_center and dipole_winder source files. All required CAD files are here.

Choose part="print_layout" for one center and two identical winders, or export
part="center" once and part="winder" twice. The default BNC hole is 10.1 mm.
standoff=4 sets the gap above the winder in millimeters; its range is 2.5–25.
Both wire-space presets use the same printed parts. Wing length, winding span,
wire reserves, and center holes are exposed in the OpenSCAD Customizer.

This is an unverified physical prototype. Test part="retention_coupon" first.
The compact 4 mm standoff still needs a loaded wire/tie and hand-clearance check.
Read the print download's README and build guide before preparing full parts.

Attribution and license: models/ham_radio/modular_dipole/NOTICE.md and
models/ham_radio/dipole_winder/NOTICE.md. Preserve both notices when sharing.
SHA256.json records the exact contents of this editable-source download.
""".encode()

    source_bundle = HERE / "modular-dipole-editable-source.zip"
    write_archive(source_bundle, source_payloads)
    check_editable_archive(source_bundle)
    # Compilation takes time. Recheck the source/output guard before publishing
    # the printable bundle so a concurrent CAD edit cannot silently slip through.
    checked_validation()
    print_bundle = HERE / "modular-dipole-STLs.zip"
    write_archive(print_bundle, print_payloads)
    print(print_bundle)
    print(source_bundle)


if __name__ == "__main__":
    main()
