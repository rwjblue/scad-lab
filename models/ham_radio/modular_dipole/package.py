#!/usr/bin/env python3
"""Build curated prints and individual editable-source uploads from validated CAD."""
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
PUBLIC_IMAGES = ["assembled", "exploded", "print_layout", "release_explainer"]
PRINT_FILES = ["center.stl", "winder.stl", "print_layout.stl"]
MARKDOWN_LINK = re.compile(r"\]\(([^)]+)\)")
REPOSITORY_ONLY = {
    (DOCS / "DESIGN.md").resolve(),
    (HERE / "validation.json").resolve(),
    (HERE / "fit_coupon.stl").resolve(),
    (HERE / "retention_coupon.stl").resolve(),
    (HERE / "bnc_fit_coupon.stl").resolve(),
    (HERE / "images/retention_coupon.png").resolve(),
}
REPOSITORY_URL = "https://github.com/rwjblue/scad-lab/blob/main/"
UPLOAD_DIRECTORY = ROOT / "output/printables/modular-dipole"


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


def binary_stl_triangle_count(path):
    """Reject an empty or truncated binary STL before comparing its geometry."""
    data = path.read_bytes()
    assert len(data) >= 84, f"Empty STL: {path}"
    count = struct.unpack_from("<I", data, 80)[0]
    assert count > 0 and len(data) == 84 + count * 50, f"Invalid binary STL: {path}"
    return count


def compile_source(source, output, definitions):
    command = ["openscad", "--backend=Manifold", "--hardwarnings", "--export-format", "binstl"]
    for definition in definitions:
        command += ["-D", definition]
    completed = subprocess.run(command + ["-o", str(output), str(source)],
                               capture_output=True, text=True)
    assert completed.returncode == 0 and "ERROR:" not in completed.stderr and \
        "WARNING:" not in completed.stderr, f"Editable source does not compile:\n{completed.stderr}"
    return binary_stl_triangle_count(output)


def check_direct_sources(payloads):
    """Compile only the flattened uploads and compare their surface to validated CAD."""
    with tempfile.TemporaryDirectory(prefix="modular-dipole-source-check-") as directory:
        work = Path(directory)
        for name, data in payloads.items():
            (work / name).write_bytes(data)
        source = work / "modular_dipole.scad"
        output = work / "print-layout.stl"
        triangles = compile_source(source, output, ['part="print_layout"'])
        # Manifold can triangulate identical CAD differently between runs. Use
        # the validator's 0.001 mm³ Boolean tolerance, not binary facet identity.
        comparison = """
import json, sys
import numpy as np
import trimesh
a, b = [trimesh.load_mesh(path) for path in sys.argv[1:]]
assert a.is_watertight and a.is_winding_consistent and a.volume > 0
assert len(a.split(only_watertight=False)) == 3
def volume(mesh):
    return 0 if mesh is None or len(mesh.faces) == 0 else abs(float(mesh.volume))
difference = sum(volume(trimesh.boolean.difference(pair, engine="manifold"))
                 for pair in [[a, b], [b, a]])
bound_error = float(np.max(np.abs(a.bounds - b.bounds)))
assert difference < 0.001, f"Direct-source geometry changed by {difference} mm³"
assert bound_error < 0.001, f"Direct-source bounds changed by {bound_error} mm"
print(json.dumps({"symmetric_difference_mm3": difference, "maximum_bound_error_mm": bound_error}))
"""
        completed = subprocess.run([
            "uv", "run", "--no-project", "--with", "trimesh", "--with", "manifold3d",
            "--with", "networkx", "python", "-c", comparison, str(output), str(HERE / "print_layout.stl"),
        ], capture_output=True, text=True)
        assert completed.returncode == 0, f"Direct-source geometry comparison failed:\n{completed.stderr}"
        measured = json.loads(completed.stdout)
        print(f"Isolated direct sources match the validated layout ({triangles:,} triangles): {measured}")


def direct_source_payloads():
    payloads = {source.name: source.read_bytes() for source in CORE_SOURCE}
    assert len(payloads) == len(CORE_SOURCE), "Source filenames collide after flattening"
    main = payloads["modular_dipole.scad"].decode()
    for old, new in [
        ("use <../dipole_winder/frame_bevel.scad>", "use <frame_bevel.scad>"),
        ("use <../dipole_center/dipole_center.scad>", "use <dipole_center.scad>"),
    ]:
        assert main.count(old) == 1, f"Unexpected source dependency: {old}"
        main = main.replace(old, new)
    payloads["modular_dipole.scad"] = main.encode()
    notices = []
    for notice in NOTICES:
        def plain_link(match):
            label, link = match.group(1), match.group(2)
            if local_link(link):
                path, separator, fragment = link.partition("#")
                resolved = (notice.parent / path).resolve()
                assert resolved.is_file(), f"Missing attribution link: {link}"
                link = f"{REPOSITORY_URL}{resolved.relative_to(ROOT)}{separator}{fragment}"
            return f"{label} ({link})"
        content = re.sub(r"\[([^]]+)\]\(([^)]+)\)", plain_link, notice.read_text())
        content = content.replace("**", "").replace("`", "")
        notices.append(f"SOURCE: {REPOSITORY_URL}{notice.relative_to(ROOT)}\n\n{content}")
    payloads["NOTICE.txt"] = ("MODULAR DIPOLE — SOURCE ATTRIBUTION AND LICENSE\n\n" +
                              "\n\n".join(notices)).encode()
    return payloads


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

    source_payloads = direct_source_payloads()
    check_direct_sources(source_payloads)
    # Compilation takes time. Recheck the source/output guard before publishing
    # the printable bundle so a concurrent CAD edit cannot silently slip through.
    checked_validation()
    UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
    for name, data in source_payloads.items():
        (UPLOAD_DIRECTORY / name).write_bytes(data)
    (HERE / "modular-dipole-editable-source.zip").unlink(missing_ok=True)
    print_bundle = HERE / "modular-dipole-STLs.zip"
    write_archive(print_bundle, print_payloads)
    print(print_bundle)
    for name in source_payloads:
        print(UPLOAD_DIRECTORY / name)


if __name__ == "__main__":
    main()
