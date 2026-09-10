#!/usr/bin/env python3
"""Independently test modular dipole parked-state play and sequential leveling release.

Run with the same uv dependencies as the modular model validator. Exports fresh
meshes from the current CAD, records input hashes, and rejects changes mid-run.
This is a sampled geometric audit, not a physical one-hand or fatigue test.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

import manifold3d
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
MODEL = HERE.parent
ROOT = MODEL.parents[2]
SOURCE = MODEL / "modular_dipole.scad"
INPUTS = [Path(__file__).resolve(), SOURCE, MODEL / "native_profile.scad",
          MODEL.parent / "dipole_winder/frame_bevel.scad",
          MODEL.parent / "dipole_center/dipole_center.scad"]
INTERFERENCE_TOL = 0.001
SUPPORT_MIN = 0.0001
PARK_ANGLE = 4.7
CLOSURE = 0.2
LEVEL_STEPS = np.linspace(0, PARK_ANGLE, 20).tolist()
LIFT_STEPS = [0, 0.25, 0.5, 0.75, 1, 2, 4, 8, 10]


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def hashes():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in INPUTS}


def run_scad(source, output, preset):
    command = ["openscad", "--backend=Manifold", "--hardwarnings",
               "-D", f'preset="{preset}"', "-D", 'part="center"',
               "-o", str(output), str(source)]
    if output.suffix == ".stl":
        command[1:1] = ["--export-format=binstl"]
    result = subprocess.run(command, text=True, capture_output=True)
    require(result.returncode == 0 and output.exists(),
            f"Export failed: {command}\n{result.stderr}")
    require("WARNING:" not in result.stderr and "ERROR:" not in result.stderr,
            result.stderr)
    return result.stderr


def config(directory, preset):
    wrapper = directory / f"config-{preset}.scad"
    names = ["winder_offset", "seat_z", "dock_x", "dock_y", "guide_x", "guide_y",
             "head_top_z", "snap_release", "center_y_offset", "center_plate_t"]
    wrapper.write_text(f"include <{SOURCE}>\n"
                       f'echo(["PINCH_AUDIT_CONFIG",{",".join(names)},'
                       f"peel_clearance_lift({PARK_ANGLE})]);\n")
    stderr = run_scad(wrapper, wrapper.with_suffix(".csg"), preset)
    line = next(s.removeprefix("ECHO: ") for s in stderr.splitlines()
                if s.startswith('ECHO: ["PINCH_AUDIT_CONFIG",'))
    values = json.loads(line)[1:]
    return dict(zip(names + ["peel_lift"], values))


def export(directory, preset, name, expression):
    wrapper = directory / f"{preset}-{name}.scad"
    wrapper.write_text(f"use <{SOURCE}>\n$fn=96;\n{expression}\n")
    output = wrapper.with_suffix(".stl")
    run_scad(wrapper, output, preset)
    mesh = trimesh.load_mesh(output)
    require(mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0,
            f"Invalid raw mesh: {name}, {preset}")
    require(len(mesh.split(only_watertight=False)) == 1,
            f"Not one connected solid: {name}, {preset}")
    require(np.all(mesh.area_faces >= 1e-10), f"Degenerate faces: {name}, {preset}")
    solid = manifold3d.Manifold(manifold3d.Mesh(
        np.asarray(mesh.vertices, dtype=np.float32),
        np.asarray(mesh.faces, dtype=np.uint32)))
    require(solid.status() == manifold3d.Error.NoError, f"Manifold error: {name}")
    return solid, {"sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                   "triangles": len(mesh.faces), "watertight": True,
                   "connected_solids": 1, "bounds_mm": mesh.bounds.tolist()}


def rotate(solid, degrees, axis, point):
    matrix = trimesh.transformations.rotation_matrix(np.radians(degrees), axis, point)
    return solid.transform(matrix[:3, :])


def intersection(a, b):
    value = a ^ b
    require(value.status() == manifold3d.Error.NoError, "Boolean operation failed")
    return abs(float(value.volume()))


def crop_head(winder, end, row, cfg, top_only):
    height = 0.4 if top_only else 2.0
    z = cfg["seat_z"] + cfg["head_top_z"] - (0.1 if top_only else 0.8)
    box = manifold3d.Manifold.cube([10, 10, height], center=True).translate(
        [end * cfg["dock_x"], row * cfg["dock_y"], z])
    return winder ^ box


def candidates(winder, row, cfg):
    for dx in [-0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4]:
        for dy in [-0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4]:
            yield {"dx_mm": dx, "dy_mm": dy, "yaw_deg": 0}, winder.translate([dx, dy, 0])
    pivot = [row * cfg["guide_x"], row * cfg["guide_y"], 0]
    for yaw in [-0.5, -0.3, -0.15, 0.15, 0.3, 0.5]:
        yield {"dx_mm": 0, "dy_mm": 0, "yaw_deg": yaw}, rotate(winder, yaw, [0, 0, 1], pivot)
    for yaw in [-0.3, 0.3]:
        rotated = rotate(winder, yaw, [0, 0, 1], pivot)
        for dx, dy in [(-0.2, 0), (0.2, 0), (0, -0.2), (0, 0.2),
                       (-0.1, -0.1), (-0.1, 0.1), (0.1, -0.1), (0.1, 0.1)]:
            yield {"dx_mm": dx, "dy_mm": dy, "yaw_deg": yaw}, rotated.translate([dx, dy, 0])


def audit_end(center, second_open, winder, end, cfg):
    placement = [0, cfg["center_y_offset"], cfg["seat_z"]]
    first_pivot = [-end * cfg["dock_x"], 0,
                   cfg["seat_z"] + cfg["center_plate_t"] / 2]

    def parked(solid):
        return rotate(solid.translate(placement), -end * PARK_ANGLE, [0, 1, 0],
                      first_pivot).translate([0, 0, cfg["peel_lift"]])

    rest = parked(center)
    opened = parked(second_open)
    level_pivot = [end * cfg["dock_x"], 0, cfg["seat_z"] + cfg["head_top_z"]]
    leveling = [rotate(opened, end * angle, [0, 1, 0], level_pivot)
                for angle in LEVEL_STEPS]
    lifted = [leveling[-1].translate([0, 0, dz]) for dz in LIFT_STEPS]
    unpressed_attempt = rotate(rest, end * 1.0, [0, 1, 0], level_pivot)
    report = {"parking_angle_deg": PARK_ANGLE, "parking_lift_mm": cfg["peel_lift"],
              "leveling_pivot_mm": level_pivot, "rows": {}}
    for row in [1, -1]:
        placed = winder if row > 0 else winder.rotate([0, 0, 180])
        placed = placed.translate([0, row * cfg["winder_offset"], 0])
        accepted, excluded = [], []
        for description, pose in candidates(placed, row, cfg):
            initial = intersection(rest, pose)
            if initial > INTERFERENCE_TOL:
                excluded.append({**description, "rest_interference_mm3": initial})
                continue
            cap = crop_head(pose, end, row, cfg, True)
            retained = crop_head(pose, -end, row, cfg, False)
            support = intersection(rest.translate([0, 0, -CLOSURE]), cap)
            blocking = intersection(unpressed_attempt, retained)
            lev = [intersection(state, pose) for state in leveling]
            lift = [intersection(state, pose) for state in lifted]
            accepted.append({**description, "rest_interference_mm3": initial,
                             "parking_support_under_closure_mm3": support,
                             "unpressed_opposite_head_block_mm3": blocking,
                             "leveling_intersections_mm3": lev,
                             "final_lift_intersections_mm3": lift,
                             "passed": support > SUPPORT_MIN and blocking > SUPPORT_MIN
                             and max(lev + lift) <= INTERFERENCE_TOL})
        require(len(accepted) >= 10, "Too few admissible parked poses")
        require(not any(x["yaw_deg"] == 0 and
                        (abs(x["dx_mm"]) >= 0.4 or abs(x["dy_mm"]) >= 0.4)
                        for x in accepted),
                "Admitted translation reaches the probe boundary; expand the parked-pose grid")
        report["rows"][str(row)] = {"admissible": accepted, "excluded": excluded,
                                      "passed": all(x["passed"] for x in accepted)}
    report["passed"] = all(x["passed"] for x in report["rows"].values())
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "parked_audit.json")
    parser.add_argument("--expected-source-sha256")
    args = parser.parse_args()
    inputs = hashes()
    source_hash = inputs[str(SOURCE.relative_to(ROOT))]
    if args.expected_source_sha256:
        require(source_hash == args.expected_source_sha256, "Source hash differs from required revision")
    report = {"status": "running", "input_sha256": inputs,
              "source_sha256": source_hash, "presets": {},
              "method": "Fresh STL exports; independent Manifold Boolean tests of sampled parked poses",
              "limits": "CAD only. The 4.7-degree near-contact pose is allowed to settle up to 0.2 mm. "
                        "Virtual blocking volume is not contact area or retention force. "
                        "No exhaustive motion, flexible torsion, friction, one-hand or glove claim.",
              "interference_tolerance_mm3": INTERFERENCE_TOL,
              "virtual_parking_closure_mm": CLOSURE,
              "leveling_angles_deg": LEVEL_STEPS, "final_level_lifts_mm": LIFT_STEPS}
    with tempfile.TemporaryDirectory(prefix="pinch-parked-audit-") as temp:
        directory = Path(temp)
        for preset in ["40m", "80m"]:
            cfg = config(directory, preset)
            definitions = {"rest": "dock_center();", "winder": "single_winder();",
                           "left_open": f'dock_center([{cfg["snap_release"]},0]);',
                           "right_open": f'dock_center([0,{cfg["snap_release"]}]);'}
            solids, meshes = {}, {}
            for name, expression in definitions.items():
                solids[name], meshes[name] = export(directory, preset, name, expression)
            checks = {"configuration": cfg, "fresh_meshes": meshes, "ends": {}}
            for end, name in [(1, "right_first"), (-1, "left_first")]:
                second = solids["left_open" if end > 0 else "right_open"]
                checks["ends"][name] = audit_end(solids["rest"], second, solids["winder"], end, cfg)
                print(f'{preset} {name}: {"passed" if checks["ends"][name]["passed"] else "FAILED"}', flush=True)
            report["presets"][preset] = checks
    require(hashes() == inputs, "Audit inputs changed during the run")
    report["status"] = "passed" if all(
        end["passed"] for preset in report["presets"].values()
        for end in preset["ends"].values()) else "failed"
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    require(report["status"] == "passed", f"Parked-motion audit failed; see {args.output}")
    print(f"Saved {args.output}", flush=True)


if __name__ == "__main__":
    main()
