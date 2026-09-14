#!/usr/bin/env python3
"""Export the print sets and check real mesh sections and parameter variants.

Run with mise run dipole-link:check. Intermediate exports live in a temporary
directory; only the three downloadable STL sets and validation.json are kept.
"""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import tempfile

import numpy as np
from shapely.geometry import Polygon
import trimesh

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "dipole_link.scad"


def export(path, definitions):
    command = ["openscad", "--backend=Manifold", "--hardwarnings",
               "--export-format=binstl", "-o", str(path)]
    for key, value in definitions.items():
        command += ["-D", f"{key}={json.dumps(value)}"]
    result = subprocess.run(command + [str(SOURCE)], capture_output=True, text=True)
    if result.returncode or "ERROR:" in result.stderr or "WARNING:" in result.stderr:
        raise RuntimeError(result.stdout + result.stderr)
    return trimesh.load_mesh(path)


def solids(mesh, expected):
    assert mesh.is_watertight and mesh.is_winding_consistent, "Invalid mesh"
    parts = mesh.split(only_watertight=False)
    assert len(parts) == expected, (len(parts), expected)
    assert all(p.is_watertight and p.volume > 0 for p in parts)
    return parts


def section_polygons(mesh, z):
    section = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    assert section is not None, f"Missing section at Z={z}"
    flat, _ = section.to_2D()
    return list(flat.polygons_full)


def inspect_link(mesh, hole_d=1.8, thickness=2.6, expected_size=None):
    if expected_size is not None:
        assert np.allclose(mesh.extents, expected_size, atol=.02), mesh.extents
    mid = section_polygons(mesh, thickness / 2)
    assert len(mid) == 1, "Split plastic section"
    profile = mid[0]
    assert len(profile.interiors) == 4, "Expected four independent through holes"
    holes = [Polygon(ring) for ring in profile.interiors]
    for hole in holes:
        bounds = hole.bounds
        assert abs(bounds[2] - bounds[0] - hole_d) < .03
        assert abs(bounds[3] - bounds[1] - hole_d) < .03
        assert hole.distance(profile.exterior) >= 1.99, "Insufficient hole wall"
    # Sample above and below the label to check that the holes remain open,
    # including both chamfer faces. Recessed text must have a solid floor.
    for z in [.05, thickness - .05]:
        face = section_polygons(mesh, z)
        large_voids = [Polygon(r) for p in face for r in p.interiors
                       if Polygon(r).area > hole_d * hole_d * .6]
        assert len(large_voids) >= 4
    return {"size_mm": np.round(mesh.extents, 3).tolist(),
            "volume_mm3": round(float(mesh.volume), 2),
            "through_holes": len(holes)}


def main():
    reports = {}
    # Public defaults: each row is a matched pair; six and twenty separate
    # solids establish that the plate contains the requested quantities.
    for layout, count, filename, extent in [
        ("starter", 6, "links_40_30_20.stl", [80, 38, 2.6]),
        ("full", 20, "links_all_bands.stl", [80, 136, 2.6]),
        ("pair", 2, "links_40m_pair.stl", [80, 10, 2.6]),
    ]:
        mesh = export(HERE / filename, {"layout": layout})
        parts = solids(mesh, count)
        assert np.allclose(mesh.extents, extent, atol=.03), (layout, mesh.extents)
        for part in parts:
            inspect_link(part, expected_size=[38, 10, 2.6])
        reports[layout] = {"links": count, "size_mm": np.round(mesh.extents, 3).tolist(),
                           "volume_mm3": round(float(mesh.volume), 2)}

    cases = [
        ("small_holes", {"hole_d": 1.3}),
        ("larger_wire", {"hole_d": 2.6}),
        ("large_holes_and_ties", {"hole_d": 3.2, "tie_width": 4.8}),
        ("wider_ties", {"tie_width": 3.6}),
        ("thicker", {"thickness": 3.4}),
        ("custom_label", {"pair_label": "Portable 40m"}),
        ("wide_letters", {"pair_label": "WWWWWWWW"}),
        ("short_label", {"pair_label": "6m"}),
        ("raised", {"label_style": "raised"}),
        ("flush", {"label_style": "flush"}),
    ]
    with tempfile.TemporaryDirectory(prefix="dipole-link-check-") as directory:
        temp = Path(directory)

        def check_case(case):
            name, settings = case
            defs = {"layout": "single", **settings}
            mesh = export(temp / f"{name}.stl", defs)
            solids(mesh, 1)
            result = inspect_link(mesh, settings.get("hole_d", 1.8),
                                  settings.get("thickness", 2.6))
            if "label" in name or name == "wide_letters":
                # Separate letter geometry must be wholly inside the central
                # label region in XY, even for arbitrary wide/long text.
                letters = export(temp / f"{name}-letters.stl", {**defs, "part": "labels"})
                assert letters.is_watertight and letters.volume > 0
                assert letters.bounds[0, 0] > mesh.bounds[0, 0] + 10
                assert letters.bounds[1, 0] < mesh.bounds[1, 0] - 10
                assert letters.bounds[0, 1] > mesh.bounds[0, 1] + .5
                assert letters.bounds[1, 1] < mesh.bounds[1, 1] - .5
            return name, result

        with ThreadPoolExecutor(max_workers=3) as pool:
            reports["variants"] = dict(pool.map(check_case, cases))

        # Multicolor exports must partition the solid without overlapping
        # volumes or moving the letters to a different origin.
        defs = {"layout": "single", "label_style": "flush"}
        body = export(temp / "body.stl", {**defs, "part": "body"})
        letters = export(temp / "letters.stl", {**defs, "part": "labels"})
        complete = export(temp / "complete.stl", defs)
        assert abs(body.volume + letters.volume - complete.volume) < .02
        assert letters.bounds[0, 2] >= 2.19 and letters.bounds[1, 2] <= 2.61
        reports["flush_partition"] = "body + letters match complete volume"

        invalid = [{"hole_d": 0}, {"tie_width": 0}, {"thickness": 1},
                   {"label_depth": 3}, {"layout": "unknown"}]
        rejected = 0
        for index, settings in enumerate(invalid):
            try:
                export(temp / f"invalid-{index}.stl", {"layout": "single", **settings})
            except RuntimeError as error:
                assert "Assertion" in str(error), str(error)
                rejected += 1
            else:
                raise AssertionError(f"Accepted invalid parameters: {settings}")
        reports["invalid_settings_rejected"] = rejected
    (HERE / "validation.json").write_text(json.dumps(reports, indent=2) + "\n")
    print(json.dumps(reports, indent=2))


if __name__ == "__main__":
    main()
