#!/usr/bin/env python3
"""Measure each latch's retained bearing footprint under explicit fit assumptions.

Uses fresh STL sections, not the nominal diameter-minus-clearance expression.
The sweep screens geometric margin only: its dimensional losses are assumptions,
not measurements of this printer, and area/depth do not predict retention force.
Run with the same uv dependencies as the main modular-dipole validator.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import numpy as np
from shapely import affinity
from shapely.geometry import Polygon, box
import trimesh

HERE = Path(__file__).resolve().parent
MODEL = HERE.parent
SOURCE = MODEL / "modular_dipole.scad"
sys.path.insert(0, str(MODEL))
from validation_helpers import export, require, sections

CONFIG_NAMES = ["seat_z", "center_plate_t", "center_y_offset", "winder_offset",
                "dock_x", "dock_y", "native_dock_y", "guide_x", "guide_y",
                "head_under_z", "head_band_h", "snap_head_d", "neck_d"]
LOSSES = {"head_edge_loss_mm": [0, 0.1, 0.2],
          "catch_edge_setback_mm": [0, 0.075, 0.15],
          "spring_set_mm": [0, 0.05, 0.1],
          "extra_radial_play_mm": [0, 0.05, 0.1]}
COLLISION_AREA_TOL = 0.00001
MIN_DEPTH = 0.35
MIN_AREA = 0.5


def config(directory, source=SOURCE, preset="40m", definitions=()):
    """Ask OpenSCAD to evaluate configuration, including derived expressions."""
    wrapper = Path(directory) / f"retention-config-{preset}.scad"
    wrapper.write_text(f"include <{Path(source).resolve()}>\n"
                       f'echo(["RETENTION_CONFIG",{",".join(CONFIG_NAMES)}]);\n')
    command = ["openscad", "--backend=Manifold", "--hardwarnings",
               "-D", 'part="center"', "-D", f'preset="{preset}"']
    for definition in definitions:
        command += ["-D", definition]
    command += ["-o", str(wrapper.with_suffix(".csg")), str(wrapper)]
    result = subprocess.run(command, text=True, capture_output=True)
    require(result.returncode == 0 and "WARNING:" not in result.stderr
            and "ERROR:" not in result.stderr, result.stderr)
    value = next((line[6:] for line in result.stderr.splitlines()
                  if line.startswith('ECHO: ["RETENTION_CONFIG",')), None)
    require(value is not None, "Missing retention configuration echo")
    return dict(zip(CONFIG_NAMES, json.loads(value)[1:]))


def engagement_depth(footprint):
    """Deepest contiguous bearing chord in the local inward/outward Y direction.

    A curved overlap goes to zero at its lateral tips, so a minimum over all X
    would always be zero. Measure its deepest actual chord, then minimize that
    useful engagement depth over all admitted poses and all four studs. Polygon
    chord lengths are piecewise linear; probing both sides of every vertex X
    captures their extrema without interpreting a bounding box as bearing land.
    """
    if footprint.is_empty or footprint.area < 1e-12:
        return 0.0
    polygons = [footprint] if footprint.geom_type == "Polygon" else [
        part for part in footprint.geoms if part.geom_type == "Polygon"]
    deepest = 0.0
    for polygon in polygons:
        rings = [np.asarray(polygon.exterior.coords)] + [
            np.asarray(ring.coords) for ring in polygon.interiors]
        start = np.concatenate([ring[:-1] for ring in rings])
        end = np.concatenate([ring[1:] for ring in rings])
        delta = end - start
        nonvertical = np.abs(delta[:, 0]) > 1e-12
        start, end, delta = start[nonvertical], end[nonvertical], delta[nonvertical]
        if len(start) == 0:
            continue
        xs = np.unique(np.concatenate([start[:, 0], end[:, 0]]))
        xs = np.concatenate([xs - 1e-8, xs + 1e-8])[:, None]
        crosses = (xs >= np.minimum(start[:, 0], end[:, 0])) & (
            xs < np.maximum(start[:, 0], end[:, 0]))
        ys = start[:, 1] + (xs - start[:, 0]) * delta[:, 1] / delta[:, 0]
        ys = np.sort(np.where(crosses, ys, np.nan), axis=1)
        # Every regular vertical line enters/exits a polygon in pairs.
        columns = (ys.shape[1] // 2) * 2
        chords = ys[:, 1:columns:2] - ys[:, :columns:2]
        if chords.size and np.any(np.isfinite(chords)):
            deepest = max(deepest, float(np.nanmax(chords)))
    return deepest


def pose_candidates(row, cfg):
    """Sample rigid XY translation and small yaw about the winder's guide."""
    translations = np.round(np.arange(-0.6, 0.6001, 0.05), 4)
    for yaw, dx, outward in itertools.product(
            [-0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75], translations, translations):
        yield {"dx_mm": float(dx), "dy_mm": float(row * outward),
               "yaw_deg": yaw}


def moved(shape, pose, row, cfg):
    rotated = affinity.rotate(shape, pose["yaw_deg"], origin=(
        row * cfg["guide_x"], row * cfg["guide_y"]))
    return affinity.translate(rotated, pose["dx_mm"], pose["dy_mm"])


def local(shape, end, row, cfg):
    shifted = affinity.translate(shape, -end * cfg["dock_x"], -row * cfg["dock_y"])
    return affinity.scale(shifted, xfact=end, yfact=row, origin=(0, 0))


def audit_retention(center_mesh, winder_mesh, cfg, *, losses=None,
                    min_depth=MIN_DEPTH, min_area=MIN_AREA):
    """Audit raw print-coordinate center/winder meshes; return JSON-safe results.

    Admitted play is derived from neck/guide sections versus the full center
    section. Additional radial mating clearance is modeled by eroding those
    neck/guide footprints. Head/catch losses are planar erosions; spring set
    translates the catch inward. All tolerances compound in the adverse sense.
    """
    losses = LOSSES if losses is None else losses
    require(all(name in losses and len(losses[name]) for name in LOSSES),
            "Each dimensional-loss sweep needs at least one value")
    require(all(value >= 0 for values in losses.values() for value in values),
            "Dimensional losses must be nonnegative")
    center = affinity.translate(sections(center_mesh, cfg["center_plate_t"] - 0.05),
                                yoff=cfg["center_y_offset"])
    center_constraint = affinity.translate(sections(center_mesh, cfg["center_plate_t"] / 2),
                                           yoff=cfg["center_y_offset"])
    necks_native = sections(winder_mesh, cfg["seat_z"] + cfg["center_plate_t"] / 2)
    head_z = cfg["seat_z"] + cfg["head_under_z"] + min(0.05, cfg["head_band_h"] / 2)
    heads_native = sections(winder_mesh, head_z)
    radius = cfg["snap_head_d"] / 2
    report = {"section_z_mm": {"center": cfg["center_plate_t"] - 0.05,
                               "winder_neck": cfg["seat_z"] + cfg["center_plate_t"] / 2,
                               "winder_head_bearing_band": head_z},
              "thresholds": {"minimum_engagement_depth_mm": min_depth,
                             "minimum_area_mm2": min_area},
              "dimensional_loss_sweep": losses, "studs": {}, "rows": {}}
    for row in [1, -1]:
        def place(shape):
            return affinity.translate(affinity.rotate(shape, 0 if row == 1 else 180,
                                                       origin=(0, 0)),
                                      yoff=row * cfg["winder_offset"])
        necks, heads = place(necks_native), place(heads_native)
        # Include the center's complete material footprint so admission cannot
        # silently ignore the opposite stud or plain guide's alignment limit.
        admitted = {extra: [] for extra in losses["extra_radial_play_mm"]}
        neck_options = {extra: necks.buffer(-extra) for extra in admitted}
        for pose in pose_candidates(row, cfg):
            for extra, neck_shape in neck_options.items():
                collision = moved(neck_shape, pose, row, cfg).intersection(center_constraint).area
                if collision <= COLLISION_AREA_TOL:
                    admitted[extra].append(pose)
        for extra, poses in admitted.items():
            require(len(poses) >= 10, f"Too few admitted poses at row {row}, extra play {extra}")
            require(not any(abs(p["dx_mm"]) >= 0.6 or abs(p["dy_mm"]) >= 0.6
                            for p in poses),
                    "Admitted translation reaches sweep boundary; expand the grid")
        report["rows"][str(row)] = {str(extra): {
            "admitted_pose_count": len(poses),
            "maximum_outward_translation_mm": max(row * p["dy_mm"] for p in poses),
            "admitted_poses": poses} for extra, poses in admitted.items()}
        for end in [-1, 1]:
            crop = box(end * cfg["dock_x"] - radius - 0.1,
                       row * cfg["dock_y"] - radius - 0.1,
                       end * cfg["dock_x"] + radius + 0.1,
                       row * cfg["dock_y"] + radius + 0.1)
            head = heads.intersection(crop)
            require(head.geom_type == "Polygon" and head.area > 1,
                    f"Could not isolate head {end,row}")
            # This local inward half-plane excludes the rigid outer socket wall.
            catch = local(center, end, row, cfg).intersection(
                box(-radius - 1, -radius - 3, radius + 1, 0))
            require(catch.area > 1, f"Missing catch {end,row}")
            initial = head.intersection(center)
            nominal = {"area_mm2": float(initial.area),
                       "engagement_depth_mm": engagement_depth(local(initial, end, row, cfg))}
            sweeps = []
            for edge_loss, setback, spring_set, extra in itertools.product(
                    *(losses[name] for name in LOSSES)):
                worn_head = head.buffer(-edge_loss)
                worn_catch = affinity.translate(catch.buffer(-setback), yoff=-spring_set)
                outcomes = []
                for pose in admitted[extra]:
                    contact = local(moved(worn_head, pose, row, cfg), end, row, cfg).intersection(worn_catch)
                    outcomes.append({"pose": pose, "area_mm2": float(contact.area),
                                     "engagement_depth_mm": engagement_depth(contact)})
                area_case = min(outcomes, key=lambda case: case["area_mm2"])
                depth_case = min(outcomes, key=lambda case: case["engagement_depth_mm"])
                sweeps.append({"head_edge_loss_mm": edge_loss,
                               "catch_edge_setback_mm": setback, "spring_set_mm": spring_set,
                               "extra_radial_play_mm": extra,
                               "minimum_area_mm2": area_case["area_mm2"],
                               "minimum_engagement_depth_mm": depth_case["engagement_depth_mm"],
                               "worst_area_pose": area_case["pose"],
                               "worst_depth_pose": depth_case["pose"],
                               "passed": area_case["area_mm2"] >= min_area
                               and depth_case["engagement_depth_mm"] >= min_depth})
            report["studs"][f"{end},{row}"] = {"centered_nominal": nominal,
                "sweep": sweeps, "passed": all(case["passed"] for case in sweeps)}
    cases = [case for stud in report["studs"].values() for case in stud["sweep"]]
    report.update({"minimum_area_mm2": min(case["minimum_area_mm2"] for case in cases),
                   "minimum_engagement_depth_mm": min(case["minimum_engagement_depth_mm"] for case in cases),
                   "passed": all(stud["passed"] for stud in report["studs"].values())})
    return report


def run(directory, *, source=SOURCE, presets=("40m", "80m"), definitions=(),
        min_depth=MIN_DEPTH, min_area=MIN_AREA):
    """Export and audit current CAD, suitable for the main validator to call."""
    source = Path(source).resolve()
    inputs = [Path(__file__).resolve(), MODEL / "validation_helpers.py", source,
              MODEL / "native_profile.scad", MODEL / "winder_profile.scad",
              MODEL.parent / "dipole_winder/frame_bevel.scad",
              MODEL.parent / "dipole_center/dipole_center.scad"]
    def hashes():
        return {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs}
    before = hashes()
    report = {"method": "Actual STL head/catch section intersections over admitted XY/yaw poses",
              "limits": "Assumed dimensional losses, not printer measurements. Deepest local bearing chord "
              "is minimized over sampled poses; corner-tip overlap necessarily tends to zero. "
              "No force, friction, cam-out, out-of-plane flexure, layer adhesion, or durability prediction. "
              "The sampled yaw range is +/-0.75 degrees; this is not an exhaustive motion proof.",
              "assumptions": "Head/catch planar erosion plus inward spring set; extra mating radial play "
              "erodes actual neck/guide sections. All stated losses compound adversely.",
              "input_sha256": before, "source_sha256": before[str(source)],
              "definitions": list(definitions), "presets": {}}
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for preset in presets:
        cfg = config(directory, source, preset, definitions)
        paths = {part: directory / f"retention-{preset}-{part}.stl" for part in ["center", "winder"]}
        def render(part):
            mesh = export(paths[part], source, [f'part="{part}"', f'preset="{preset}"', *definitions])
            require(mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0,
                    f"Invalid retention mesh: {preset}, {part}")
            return mesh
        with ThreadPoolExecutor(max_workers=2) as pool:
            center, winder = list(pool.map(render, ["center", "winder"]))
        result = audit_retention(center, winder, cfg, min_depth=min_depth, min_area=min_area)
        result["configuration"] = cfg
        result["mesh_sha256"] = {part: hashlib.sha256(path.read_bytes()).hexdigest()
                                 for part, path in paths.items()}
        report["presets"][preset] = result
        print(f"Retention {preset}: depth {result['minimum_engagement_depth_mm']:.3f} mm, "
              f"area {result['minimum_area_mm2']:.3f} mm²: "
              f"{'passed' if result['passed'] else 'FAILED'}", flush=True)
    require(hashes() == before, "Retention audit inputs changed during the run")
    report["status"] = "passed" if all(result["passed"] for result in report["presets"].values()) else "failed"
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=HERE / "retention_audit.json")
    parser.add_argument("--preset", action="append", choices=["40m", "80m"])
    parser.add_argument("-D", "--define", action="append", default=[])
    parser.add_argument("--min-depth", type=float, default=MIN_DEPTH)
    parser.add_argument("--min-area", type=float, default=MIN_AREA)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="dipole-retention-") as directory:
        report = run(directory, source=args.source, presets=args.preset or ["40m", "80m"],
                     definitions=args.define, min_depth=args.min_depth, min_area=args.min_area)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Saved {args.output}", flush=True)
    if report["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
