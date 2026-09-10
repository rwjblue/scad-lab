#!/usr/bin/env python3
"""Export and measure representative non-default dipole-winder settings.

Run from the repository root (OpenSCAD must be on PATH):

    uv run --no-project --with trimesh --with shapely --with scipy \
      --with networkx python models/ham_radio/dipole_winder/validate_parameters.py

Exports live in a temporary directory. This checks actual mesh cross-sections,
hole axes and topology, and verifies that unsuitable parameter combinations
stop at a useful SCAD assertion. Use validate.py for the default/source-profile
regression. The default report is parameter-validation.json beside this script.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile

import numpy as np
import trimesh
from shapely.geometry import Point, Polygon, box

from validate import (check_clear_axis, digest, embedded_profile,
                      ergonomic_profile, hole_at, require, section)


HERE = Path(__file__).resolve().parent
SCAD = HERE / "dipole_winder.scad"
UPPER_SWEEP = math.radians(26.40465549589185)
# These expectations deliberately remain independent of evaluated SCAD values.
DEFAULTS = {
    "arm_length": 37.5, "frame_t": 5.0, "relief_pitch": 7.0,
    "relief_start_x": 20.0, "wire_hole_d": 3.2, "wire_chamfer": 0.5,
    "hang_hole_d": 6.0, "hang_chamfer": 0.5, "eye_y": 63.0,
    "bnc_hole_d": 10.1, "bnc_flat_depth": 0.85,
    "shelf_t": 3.0, "shelf_w": 26.0, "bnc_axis_from_frame": 10.0,
    "bnc_rear_projection": 12.0, "hardware_keepout_d": 18.0,
    "rib_t": 3.0, "rib_run": 10.0, "frame_edge_bevel": 0.5,
    "close_snag_windows": True,
}
VALID_VARIANTS = {
    "longer_arms_and_wider_relief": {"arm_length": 42, "relief_pitch": 8},
    "thin_frame_small_holes": {
        "frame_t": 4, "wire_hole_d": 2.6, "wire_chamfer": 0.3,
        "hang_hole_d": 5, "hang_chamfer": 0.3, "eye_y": 62,
    },
    "round_bnc_and_larger_mount": {
        "bnc_hole_d": 10.2, "bnc_flat_depth": 0,
        "bnc_axis_from_frame": 12, "bnc_rear_projection": 14,
        "shelf_t": 3.2, "shelf_w": 29, "hardware_keepout_d": 20,
        "rib_t": 3.5, "rib_run": 8,
    },
    "shifted_relief_and_long_arms": {
        "arm_length": 45, "relief_pitch": 9, "relief_start_x": 21,
    },
}
INVALID_VARIANTS = {
    "relief_past_arm_tip": {"arm_length": 35, "relief_pitch": 12},
    "thin_web_between_relief_mouths": {
        "wire_hole_d": 4, "wire_chamfer": 1, "relief_pitch": 6.5,
    },
    "hardware_hits_frame": {"hardware_keepout_d": 20, "bnc_axis_from_frame": 10},
}
COUPON_VARIANTS = {
    "adaptive_bnc_coupon": {
        "part": "coupon", "bnc_hole_d": 10.2, "bnc_flat_depth": 0.9,
        "frame_t": 6, "shelf_t": 3.2,
    },
    "adaptive_relief_coupon": {
        "part": "relief_coupon", "arm_length": 45, "relief_pitch": 9,
        "relief_start_x": 21, "frame_t": 4,
        "wire_hole_d": 2.6, "wire_chamfer": 0.3,
    },
}


def export(executable: str, destination: Path, parameters: dict) -> subprocess.CompletedProcess:
    command = [executable, "--hardwarnings", "--backend", "Manifold",
               "--export-format", "binstl"]
    for name, value in parameters.items():
        command.extend(["-D", f"{name}={json.dumps(value)}"])
    command.extend(["-o", str(destination), str(SCAD)])
    return subprocess.run(command, capture_output=True, text=True, timeout=180)


def measure(stl: Path, overrides: dict) -> dict:
    p = DEFAULTS | overrides
    mesh = trimesh.load(stl, force="mesh")
    require(mesh.is_watertight, "Variant is not watertight")
    require(mesh.is_winding_consistent, "Variant winding is inconsistent")
    require(mesh.volume > 0, "Variant has no positive volume")
    components = len(mesh.split(only_watertight=False))
    require(components == 1, f"Variant contains {components} disconnected bodies")
    windows = 6 if p["close_snag_windows"] else 11
    through_openings = windows + 8  # Seven frame holes and the BNC mounting hole.
    require(mesh.euler_number == 2 - 2 * through_openings,
            "Variant has extra/missing through holes or merged windows")
    require(np.allclose(mesh.bounds[:, 0], [-p["arm_length"], p["arm_length"]], atol=0.0001),
            "Arm reach was not applied to both mirrored sides")
    require(abs(mesh.bounds[0, 2]) < 0.0001, "Variant does not sit on Z=0")

    thickness = p["frame_t"]
    waist_xz = section(mesh, 1, 0, allow_disconnected=True)
    require(abs(waist_xz.bounds[3] - thickness) < 0.0001,
            "Frame thickness was not applied at the waist")
    start_y = 55.050156773381225 + (p["relief_start_x"] - 20) * math.tan(UPPER_SWEEP)
    rows = [[
        [side * (p["relief_start_x"] + i * p["relief_pitch"] * math.cos(UPPER_SWEEP)),
         start_y + i * p["relief_pitch"] * math.sin(UPPER_SWEEP)]
        for i in range(3)] for side in [-1, 1]]
    centers = rows[0] + rows[1] + [[0, p["eye_y"]]]
    bores = [p["wire_hole_d"]] * 6 + [p["hang_hole_d"]]
    chamfers = [p["wire_chamfer"]] * 6 + [p["hang_chamfer"]]
    max_hole_error, min_ligament, min_web = 0.0, float("inf"), float("inf")
    measured_centers = []
    for z in [0.001, thickness / 2, thickness - 0.001]:
        material = section(mesh, 2, z)
        require(len(material.interiors) == windows + 7, "Frame slice lost a window or hole")
        holes = []
        for center, diameter, chamfer in zip(centers, bores, chamfers):
            actual = hole_at(material, center)
            radius = diameter / 2 + max(0, chamfer - min(z, thickness - z))
            expected = Point(center).buffer(radius, quad_segs=256)
            error = actual.boundary.hausdorff_distance(expected.boundary)
            require(error < 0.006, f"Incorrect bore/chamfer at {center}, Z={z}")
            require(actual.centroid.distance(Point(center)) < 0.0001,
                    f"Hole location did not follow its parameter: {center}")
            max_hole_error = max(max_hole_error, error)
            min_ligament = min(min_ligament, actual.boundary.distance(material.exterior))
            holes.append(actual)
            if z == thickness / 2:
                measured_centers.append(list(actual.centroid.coords[0]))
        for row_start in [0, 3]:
            for i in range(2):
                min_web = min(min_web, holes[row_start+i].distance(holes[row_start+i+1]))
    require(min_ligament >= 1.998, "A chamfer mouth has less than 2 mm exterior material")
    require(min_web >= 1.998, "Less than 2 mm remains between relief chamfer mouths")
    pitches = [float(np.linalg.norm(np.subtract(measured_centers[i+1], measured_centers[i])))
               for i in [0, 1, 3, 4]]
    require(all(abs(value - p["relief_pitch"]) < 0.0001 for value in pitches),
            "Measured relief pitch does not match the parameter")
    for center in centers:
        check_clear_axis(mesh, center, 2, -0.001, thickness + 0.001)

    # Changing arm reach must not scale the waist or move its native openings.
    native = embedded_profile(HERE / "reference_profile.scad")
    central = ergonomic_profile(native) if p["close_snag_windows"] else native
    waist = box(-17, -38, 17, 22)
    waist_error = section(mesh, 2, thickness/2).intersection(waist).boundary.hausdorff_distance(
        central.intersection(waist).boundary)
    require(waist_error < 0.0001, "Arm adjustment changed the original waist geometry")

    axis_z = thickness + p["bnc_axis_from_frame"]
    top = start_y - p["bnc_rear_projection"]
    bottom = top - p["shelf_t"]
    depth = axis_z + p["hardware_keepout_d"] / 2
    require(abs(mesh.bounds[1, 2] - depth) < 0.0001,
            "Panel depth did not follow the BNC axis and hardware allowance")
    panel_tip = section(mesh, 2, depth - 1)
    require(np.allclose([panel_tip.bounds[1], panel_tip.bounds[3]], [bottom, top], atol=0.0001),
            "Shelf thickness or position did not follow its parameter")
    radius = p["bnc_hole_d"] / 2
    expected_d = Point(0, axis_z).buffer(radius, quad_segs=256).intersection(
        box(-20, -20, 20, axis_z + radius - p["bnc_flat_depth"]))
    max_bnc_error = 0.0
    for y in [bottom + 0.001, (bottom + top) / 2, top - 0.001]:
        material = section(mesh, 1, y)
        require(np.allclose([material.bounds[0], material.bounds[2]],
                            [-p["shelf_w"]/2, p["shelf_w"]/2], atol=0.0001),
                "Shelf width did not follow its parameter")
        actual = hole_at(material, [0, axis_z])
        error = actual.boundary.hausdorff_distance(expected_d.boundary)
        require(error < 0.006, "BNC diameter, flat or position ignored its parameter")
        max_bnc_error = max(max_bnc_error, error)
    require(abs(actual.bounds[2] - actual.bounds[0] - p["bnc_hole_d"]) < 0.0001,
            "BNC horizontal bore dimension is wrong")
    require(abs(actual.bounds[3] - actual.bounds[1] -
                (p["bnc_hole_d"] - p["bnc_flat_depth"])) < 0.0001,
            "BNC flat-to-opposite dimension is wrong")
    check_clear_axis(mesh, [0, axis_z], 1, bottom, top)
    return {
        "parameters": overrides,
        "mesh": {"watertight": True, "consistent_winding": True,
                 "connected_bodies": components, "through_openings": through_openings,
                 "bounds_mm": mesh.bounds.tolist(), "volume_mm3": float(mesh.volume)},
        "frame": {"measured_thickness_mm": waist_xz.bounds[3],
                  "measured_hole_centers_mm": measured_centers,
                  "relief_pitch_mm": pitches, "minimum_exterior_ligament_mm": min_ligament,
                  "minimum_relief_web_mm": min_web, "maximum_bore_chamfer_error_mm": max_hole_error,
                  "unchanged_waist_error_mm": waist_error, "all_hole_axes_clear": True},
        "bnc": {"measured_diameter_mm": actual.bounds[2] - actual.bounds[0],
                "measured_flat_to_opposite_mm": actual.bounds[3] - actual.bounds[1],
                "panel_y_mm": [bottom, top], "axis_z_mm": axis_z,
                "measured_shelf_width_mm": material.bounds[2] - material.bounds[0],
                "maximum_boundary_error_mm": max_bnc_error, "hole_axis_clear": True},
    }


def measure_coupon(stl: Path, overrides: dict) -> dict:
    p = DEFAULTS | overrides
    mesh = trimesh.load(stl, force="mesh")
    require(mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0,
            "Coupon is not a closed, consistently oriented positive solid")
    require(len(mesh.split(only_watertight=False)) == 1,
            "Coupon must remain one connected solid")
    require(mesh.euler_number == -4, "Coupon must have exactly three through openings")
    result = {"parameters": overrides,
              "mesh": {"watertight": True, "consistent_winding": True,
                       "connected_bodies": 1, "through_openings": 3,
                       "bounds_mm": mesh.bounds.tolist(), "volume_mm3": float(mesh.volume)}}
    maximum_error = 0.0
    if p["part"] == "coupon":
        axis_z = p["frame_t"] + p["bnc_axis_from_frame"]
        diameters = [p["bnc_hole_d"] - 0.4 + i*0.2 for i in range(3)]
        centers = [[x, axis_z] for x in [-22, 0, 22]]
        measured = []
        for y in [0.001, p["shelf_t"]/2, p["shelf_t"] - 0.001]:
            # At the engraved face, number counters are islands within this
            # slice even though they join the single solid farther back.
            material = section(mesh, 1, y, allow_disconnected=True)
            pieces = list(material.geoms) if material.geom_type == "MultiPolygon" else [material]
            for center, diameter in zip(centers, diameters):
                support = next(piece for piece in pieces
                               if Polygon(piece.exterior).covers(Point(center)))
                actual = hole_at(support, center)
                expected = Point(center).buffer(diameter/2, quad_segs=256).intersection(
                    box(center[0]-10, -20, center[0]+10,
                        axis_z + diameter/2 - p["bnc_flat_depth"]))
                error = actual.boundary.hausdorff_distance(expected.boundary)
                require(error < 0.006, "Coupon BNC cutout ignored diameter, flat or axis settings")
                maximum_error = max(maximum_error, error)
                width = actual.bounds[2] - actual.bounds[0]
                height = actual.bounds[3] - actual.bounds[1]
                require(abs(width-diameter) < 0.0001 and
                        abs(height-(diameter-p["bnc_flat_depth"])) < 0.0001,
                        "Coupon comparison cutout dimensions are incorrect")
                if y == p["shelf_t"]/2:
                    measured.append({"diameter_mm": width, "flat_to_opposite_mm": height})
        for center in centers:
            check_clear_axis(mesh, center, 1, 0, p["shelf_t"])
        result["cutouts"] = {"centers_xz_mm": centers, "measured": measured,
                              "all_axes_clear": True, "maximum_boundary_error_mm": maximum_error}
    else:
        start_y = 55.050156773381225 + (p["relief_start_x"]-20)*math.tan(UPPER_SWEEP)
        crop_x = min(12, p["relief_start_x"]-8)
        crop_y = min(48, start_y-7)
        centers = [[p["relief_start_x"] + i*p["relief_pitch"]*math.cos(UPPER_SWEEP)-crop_x,
                    start_y + i*p["relief_pitch"]*math.sin(UPPER_SWEEP)-crop_y]
                   for i in range(3)]
        require(abs(mesh.bounds[1, 0] - (p["arm_length"]-crop_x)) < 0.0001,
                "Relief coupon crop chopped off the extended wing tip")
        require(mesh.extents[0] > 25.5 and mesh.extents[1] > 19.541,
                "Relief coupon did not expand beyond the original 25.5 × 19.541 mm crop")
        require(np.allclose(mesh.bounds[:, 2], [0, p["frame_t"]], atol=0.0001),
                "Relief coupon thickness ignored the frame setting")
        for z in [0.001, p["frame_t"]/2, p["frame_t"]-0.001]:
            material = section(mesh, 2, z)
            require(len(material.interiors) == 3, "Crop must preserve all three relief holes")
            for center in centers:
                actual = hole_at(material, center)
                radius = p["wire_hole_d"]/2 + max(0, p["wire_chamfer"]-min(z, p["frame_t"]-z))
                expected = Point(center).buffer(radius, quad_segs=256)
                error = actual.boundary.hausdorff_distance(expected.boundary)
                require(error < 0.006, "Relief coupon bore/chamfer/position does not match the full part")
                maximum_error = max(maximum_error, error)
        for center in centers:
            check_clear_axis(mesh, center, 2, 0, p["frame_t"])
        result["cutouts"] = {"centers_xy_mm": centers, "all_axes_clear": True,
                              "maximum_bore_chamfer_error_mm": maximum_error,
                              "expanded_crop_preserves_wing_tip": True}
    return result


def validate() -> dict:
    executable = shutil.which("openscad")
    require(executable is not None, "OpenSCAD must be on PATH")
    result = {"status": "passed", "scad_sha256": digest(SCAD),
              "reference_profile_sha256": digest(HERE / "reference_profile.scad"),
              "valid_variants": {}, "coupon_variants": {}, "rejected_variants": {}}
    with tempfile.TemporaryDirectory(prefix="dipole-winder-parameters-") as directory:
        for name, overrides in VALID_VARIANTS.items():
            destination = Path(directory) / f"{name}.stl"
            process = export(executable, destination, overrides)
            require(process.returncode == 0 and destination.exists(),
                    f"{name} failed to export: {process.stderr[-3000:]}")
            result["valid_variants"][name] = measure(destination, overrides)
            print(f"PASS: {name}", flush=True)
        for name, overrides in COUPON_VARIANTS.items():
            destination = Path(directory) / f"{name}.stl"
            process = export(executable, destination, overrides)
            require(process.returncode == 0 and destination.exists(),
                    f"{name} failed to export: {process.stderr[-3000:]}")
            result["coupon_variants"][name] = measure_coupon(destination, overrides)
            print(f"PASS: {name}", flush=True)
        for name, overrides in INVALID_VARIANTS.items():
            destination = Path(directory) / f"{name}.stl"
            process = export(executable, destination, overrides)
            output = process.stdout + process.stderr
            require(process.returncode != 0 and "Assertion" in output,
                    f"{name} must stop at a SCAD assertion, got: {output[-2000:]}")
            require(not destination.exists(), f"{name} unexpectedly produced an STL")
            assertion = next(line for line in output.splitlines() if "Assertion" in line)
            result["rejected_variants"][name] = {"parameters": overrides,
                                                  "assertion": assertion}
            print(f"PASS: rejected {name}", flush=True)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "parameter-validation.json")
    args = parser.parse_args()
    try:
        report = validate()
    except Exception as error:
        args.output.write_text(json.dumps({"status": "failed", "error": str(error)}, indent=2) + "\n")
        raise
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
