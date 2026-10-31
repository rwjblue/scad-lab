#!/usr/bin/env python3
"""Export and inspect all four combinations of the shared dipole center."""
from pathlib import Path
import hashlib
import importlib.util
import json
import tempfile

import numpy as np
import trimesh
from shapely import affinity
from shapely.geometry import Point, box

HERE = Path(__file__).resolve().parent
SCAD = HERE / "dipole_center.scad"
HELPER = HERE.parent / "balun_dipole_center/validate.py"
spec = importlib.util.spec_from_file_location("balun_checks", HELPER)
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


def difference(a, b):
    return sum(checks.volume(trimesh.boolean.difference(pair, engine="manifold"))
               for pair in ([a, b], [b, a]))


def inspect(mesh, balun, straps):
    bar = 82 if balun else 21
    assert np.allclose(mesh.bounds, [[-45, 0, 0], [45, bar+18, 23]], atol=.001)
    for z in [.01, .31, 2, 3.69, 3.99]:
        material = checks.section(mesh, 2, z)
        assert material.geom_type == "Polygon"
        assert len(material.interiors) == 9+4*balun+2*straps
        for side in [-1, 1]:
            xs = [7, 25, 30.5, 36] if straps else [10, 28, 33.5, 39]
            for x, d in zip(xs, [3.4, 3.2, 3.2, 3.2]):
                chamfer = max(0, .5-min(z, 4-z)) if d == 3.2 else 0
                hole = checks.hole_at(material, side*x, bar)
                circle = Point(side*x, bar).buffer(d/2+chamfer, quad_segs=128)
                assert hole.boundary.hausdorff_distance(circle.boundary) < .01
            if straps:
                hole = checks.hole_at(material, side*41, bar)
                expected = box(side*41-1, bar-6.5, side*41+1, bar+6.5).buffer(.5)
                assert hole.boundary.hausdorff_distance(expected.boundary) < .01
                wire = checks.hole_at(material, side*36, bar)
                assert hole.distance(wire) >= 1.39
                assert hole.distance(material.exterior) >= 1.99
        eye = checks.hole_at(material, 0, bar+11)
        chamfer = max(0, .5-min(z, 4-z))
        expected = Point(0, bar+11).buffer((4 if straps else 3)+chamfer, quad_segs=128)
        assert eye.boundary.hausdorff_distance(expected.boundary) < .01
    hole = checks.hole_at(checks.section(mesh, 1, 1.5), 0, 14)
    expected = Point(0, 14).buffer(4.75, quad_segs=192).intersection(box(-10, 0, 10, 17.9))
    assert hole.boundary.hausdorff_distance(expected.boundary) < .01
    if balun:
        checks.inspect(mesh, straps=straps)
    return {"balun_mount": balun, "strap_slots": straps,
            "bounds_mm": mesh.bounds.tolist(), "watertight": True,
            "connected_solids": 1, "plate_openings": 9+4*balun+2*straps,
            "bnc_D_hole_mm": 9.5, "volume_mm3": float(mesh.volume)}


def main():
    result, meshes = {}, {}
    for balun, straps, suffix in [(False, False, ""), (False, True, "_with_straps"),
                                  (True, False, "_with_balun"),
                                  (True, True, "_with_balun_and_straps")]:
        name = "dipole_center"+suffix
        mesh = checks.export(HERE / (name+".stl"),
                             {"balun_mount": balun, "strap_slots": straps}, source=SCAD)
        result[name] = inspect(mesh, balun, straps)
        meshes[balun, straps] = mesh
        print(f"Verified {name}", flush=True)
    # The complete terminal bar/eye translates without changing either layout.
    for straps in [False, True]:
        for z in [.01, 2, 3.99]:
            old = affinity.translate(checks.section(meshes[False, straps], 2, z), yoff=61)
            new = checks.section(meshes[True, straps], 2, z)
            region = box(-50, 76, 50, 112)
            if straps:
                region = region.union(box(-50, 72, -14, 76)).union(box(14, 72, 50, 76))
            assert old.intersection(region).symmetric_difference(new.intersection(region)).area < .02
    with tempfile.TemporaryDirectory() as temp:
        temp = Path(temp)
        preset = checks.export(temp / "preset.stl")
        assert difference(preset, meshes[True, False]) < .02
        nested = checks.export(temp / "nested.stl", {"part": "center"},
                               source=HERE.parent / "nesting_dipole/nesting_dipole.scad")
        assert difference(nested, meshes[False, True]) < .02
        for diameter, rear in [(32, 10), (38, 20)]:
            variant = checks.export(temp / "extreme.stl",
                                    {"balun_mount": True, "strap_slots": True,
                                     "package_d": diameter, "bnc_rear_projection": rear}, source=SCAD)
            checks.inspect(variant, diameter, rear, straps=True)
        expanded = checks.export(temp / "wire-clearance-extreme.stl",
                                 {"balun_mount": True, "strap_slots": True,
                                  "bnc_to_toroid_gap": 20, "toroid_to_post_gap": 28}, source=SCAD)
        checks.inspect(expanded, straps=True, input_gap=20, post_gap=28)
    result["compatibility"] = {"balun_preset_matches": True,
                               "nesting_center_matches": True,
                               "terminal_bar_translation_mm": 61,
                               "combined_mount_parameter_extremes_pass": True}
    result["source_sha256"] = {str(p.relative_to(HERE.parent)): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in [SCAD, HELPER, Path(__file__)]}
    result["limits"] = ["CAD checks only; no load or RF rating",
                        "Balun with strap slots does not establish loaded nesting-winder packing fit"]
    (HERE / "validation.json").write_text(json.dumps(result, indent=2)+"\n")


if __name__ == "__main__":
    main()
