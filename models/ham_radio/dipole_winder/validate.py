#!/usr/bin/env python3
"""Check the exported default winder against the accepted A5 geometry.

From the repository root:

    uv run --no-project --with trimesh --with shapely --with scipy \
      --with networkx python models/ham_radio/dipole_winder/validate.py

Add --source /path/to/newWinder_wireframe.stl to compare with the original
supplied STL as well. Normal validation needs no external source STL. OpenSCAD
must be on PATH; isolated frame and reinforcement exports use a temporary folder.
The default output is validation.json beside this script.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

import numpy as np
import trimesh
from shapely import affinity, union_all
from shapely.geometry import MultiPoint, Point, Polygon, box


HERE = Path(__file__).resolve().parent
A5_PATH = HERE.parents[2] / "docs/concepts/2026-09-09-dipole-winder/layout-a5.json"
TOLERANCE_MM = 0.02


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def embedded_profile(path: Path) -> Polygon:
    """Read the portable outline's data, independently of the main SCAD model."""
    text = re.sub(r"//[^\n]*", "", path.read_text())

    def array(name: str) -> list:
        start = text.index("[", text.index(name + " ="))
        depth = 0
        for index in range(start, len(text)):
            depth += (text[index] == "[") - (text[index] == "]")
            if depth == 0:
                return ast.literal_eval(text[start:index + 1])
        raise ValueError(f"Unclosed {name} array in reference profile")

    points, paths = array("points"), array("paths")
    rings = [[points[index] for index in path] for path in paths]
    profile = Polygon(rings[0], rings[1:])
    require(profile.is_valid, "Embedded reference profile is invalid")
    return profile


def section(mesh: trimesh.Trimesh, axis: int, position: float) -> Polygon:
    origin, normal = np.zeros(3), np.zeros(3)
    origin[axis], normal[axis] = position, 1
    path = mesh.section(plane_origin=origin, plane_normal=normal)
    require(path is not None, f"Missing section at axis {axis}, {position} mm")
    axes = [index for index in range(3) if index != axis]
    rings = []
    for vertices in path.discrete:
        require(np.allclose(vertices[0], vertices[-1]), "A section contour is open")
        ring = Polygon(vertices[:, axes])
        require(ring.is_valid, "A section contour crosses itself")
        rings.append(ring)
    # XOR nested contours to recover material without depending on winding or
    # loop order chosen by the mesh section library.
    result = Polygon()
    for ring in sorted(rings, key=lambda polygon: polygon.area, reverse=True):
        result = result.symmetric_difference(ring)
    require(result.geom_type == "Polygon", "Section has disconnected material")
    return result


def hole_at(material: Polygon, center: list[float]) -> Polygon:
    matches = [Polygon(ring) for ring in material.interiors if Polygon(ring).covers(Point(center))]
    require(len(matches) == 1, f"Expected one open hole at {center}")
    return matches[0]


def check_clear_axis(mesh: trimesh.Trimesh, center: list[float], axis: int,
                     low: float, high: float) -> None:
    """Intersect an axis-aligned line with triangles without an R-tree dependency."""
    axes = [index for index in range(3) if index != axis]
    triangles = mesh.triangles
    a = triangles[:, 0, axes]
    ab = triangles[:, 1, axes] - a
    ac = triangles[:, 2, axes] - a
    p = np.asarray(center) - a
    determinant = ab[:, 0] * ac[:, 1] - ab[:, 1] * ac[:, 0]
    usable = np.abs(determinant) > 1e-12
    b = np.zeros(len(triangles))
    c = np.zeros(len(triangles))
    b[usable] = (p[:, 0] * ac[:, 1] - p[:, 1] * ac[:, 0])[usable] / determinant[usable]
    c[usable] = (ab[:, 0] * p[:, 1] - ab[:, 1] * p[:, 0])[usable] / determinant[usable]
    inside = usable & (b >= -1e-9) & (c >= -1e-9) & (b + c <= 1 + 1e-9)
    height = (triangles[:, 0, axis] + b * (triangles[:, 1, axis] - triangles[:, 0, axis])
              + c * (triangles[:, 2, axis] - triangles[:, 0, axis]))
    require(not np.any(inside & (height >= low) & (height <= high)),
            f"Obstruction along hole axis {axis} at {center}")


def raw_source_profile(source: Path) -> Polygon:
    from generate_reference_profile import load_silhouette
    silhouette, _ = load_silhouette(source)
    one_side = affinity.affine_transform(silhouette, [0, 1, 1, 0, 0, -62.5])
    native = union_all([one_side, affinity.scale(one_side, xfact=-1, yfact=1, origin=(0, 0))])
    accepted = union_all([native, Polygon(native.exterior).intersection(box(-40, 25, 40, 75))])
    # Exclude only floating-point overlay holes, not genuine native windows.
    return Polygon(accepted.exterior, [ring for ring in accepted.interiors if Polygon(ring).area >= 1e-8])


def temporary_export(part: str) -> trimesh.Trimesh:
    executable = shutil.which("openscad")
    require(executable is not None, "OpenSCAD must be on PATH")
    with tempfile.TemporaryDirectory(prefix="dipole-winder-validation-") as directory:
        exported = Path(directory) / f"{part}.stl"
        if part == "frame":
            command = [executable, "-D", 'part="frame"', "-o", str(exported),
                       str(HERE / "dipole_winder.scad")]
        else:
            wrapper = Path(directory) / "reinforcement.scad"
            # `use` imports modules but not the caller's dynamic special $fn.
            # Match the default model's 96 facets for its circumscribed keepout.
            wrapper.write_text(f"use <{HERE / 'dipole_winder.scad'}>\n$fn=96;\nreinforcement();\n")
            command = [executable, "-o", str(exported), str(wrapper)]
        process = subprocess.run(command,
                                 capture_output=True, text=True, timeout=120)
        require(process.returncode == 0 and exported.exists(),
                f"{part} export failed: " + process.stderr[-2000:])
        return trimesh.load(exported, force="mesh")


def check_reinforcement(profile: Polygon, a5: dict) -> dict:
    ribs = temporary_export("reinforcement")
    require(ribs.is_watertight and ribs.volume > 0, "Reinforcement is not a closed positive solid")
    axis = Point(0, a5["bnc_axis_z_proposed_mm"])
    panel_bottom = a5["bnc_shelf_top_y_mm"] - a5["bnc_shelf_thickness_mm"]
    # Reinforcement intentionally overlaps the shelf for a reliable union.
    # The mounting panel uses its D-hole, not the larger hardware keepout.
    below_panel = ribs.slice_plane([0, panel_bottom - 0.0001, 0], [0, -1, 0], cap=False)
    # Project complete triangles, not just vertices: a facet can intrude into
    # a circular keepout even when each of its vertices clears the circle.
    nearest = min(axis.distance(MultiPoint(triangle[:, [0, 2]]).convex_hull) for triangle in below_panel.triangles)
    radius = a5["bnc_hardware_keepout_diameter_mm"] / 2
    require(nearest >= radius - 0.0001, "Reinforcement intrudes into the Ø18 hardware envelope")
    xy = union_all([MultiPoint(triangle[:, :2]).convex_hull for triangle in ribs.triangles])
    overrun = xy.difference(profile.buffer(0.0001)).area
    require(overrun < 0.001, "Reinforcement extends outside the accepted winding profile")
    return {"minimum_distance_to_bnc_axis_mm": nearest,
            "hardware_keepout_radius_mm": radius,
            "clearance_checked_below_panel_y_mm": panel_bottom - 0.0001,
            "profile_overrun_area_mm2": overrun}


def validate(stl: Path, source: Path | None) -> dict:
    a5 = json.loads(A5_PATH.read_text())
    mesh = trimesh.load(stl, force="mesh")
    require(mesh.is_watertight, "STL is not watertight")
    require(mesh.is_winding_consistent, "STL winding is inconsistent")
    require(mesh.volume > 0, "STL volume must be positive")
    components = len(mesh.split(only_watertight=False))
    require(components == 1, f"STL has {components} disconnected bodies")
    require(np.allclose(mesh.bounds, [[-37.5, -70, 0], [37.5, 70, 24]], atol=0.0001),
            "STL bounds differ from the accepted 75 × 140 × 24 mm print orientation")
    profile = embedded_profile(HERE / "reference_profile.scad")
    top = a5["bnc_shelf_top_y_mm"]
    bottom = top - a5["bnc_shelf_thickness_mm"]
    # The A5 drawing adds a 26 mm perpendicular shelf to the native frame.
    # Its bed-supported base slightly widens the local outline; the horns and
    # the separate frame must retain the source dimensions and contours.
    composite_profile = profile.union(box(-13, bottom, 13, top))
    wire_centers = a5["left_relief_centers_mm"] + a5["right_relief_centers_mm"]
    centers = wire_centers + [a5["eye_center_mm"]]
    diameters = [a5["wire_bore_mm"]] * 6 + [a5["eye_bore_mm"]]
    frame_t = a5["frame_extent_mm"][2]
    chamfer = a5["chamfer_mm"]
    samples = [0.001, frame_t / 2, frame_t - 0.001]
    maximum_hole_error, maximum_profile_error = 0.0, 0.0
    restored_mid = None
    measured_centers = []
    for z in samples:
        material = section(mesh, 2, z)
        require(len(material.interiors) == len(profile.interiors) + 7,
                "Frame contains extra or missing holes (including possible M3 holes)")
        new_holes = []
        for center, diameter in zip(centers, diameters):
            actual = hole_at(material, center)
            radius = diameter / 2 + max(0, chamfer - min(z, frame_t - z))
            expected = Point(center).buffer(radius, quad_segs=256)
            error = actual.boundary.hausdorff_distance(expected.boundary)
            require(error < 0.006, f"Incorrect bore or chamfer at {center}, Z={z}")
            require(actual.centroid.distance(Point(center)) < 0.0001,
                    f"Hole center differs from accepted A5 coordinates: {center}")
            maximum_hole_error = max(maximum_hole_error, error)
            new_holes.append(actual)
            if z == frame_t / 2:
                measured_centers.append(list(actual.centroid.coords[0]))
        restored = union_all([material] + new_holes)
        error = restored.boundary.hausdorff_distance(composite_profile.boundary)
        require(error < TOLERANCE_MM, "Actual contour differs from the native frame plus the A5 shelf")
        maximum_profile_error = max(maximum_profile_error, error)
        if z == frame_t / 2:
            restored_mid = restored
    pitches = [float(np.linalg.norm(np.subtract(row[i + 1], row[i])))
               for row in (measured_centers[:3], measured_centers[3:6]) for i in range(2)]
    require(all(abs(pitch - 7) < 0.0001 for pitch in pitches), "Relief pitch differs from 7 mm")
    for center in centers:
        check_clear_axis(mesh, center, 2, -0.001, frame_t + 0.001)

    axis_z = a5["bnc_axis_z_proposed_mm"]
    expected_d = Point(0, axis_z).buffer(4.95, quad_segs=256).intersection(box(-10, 0, 10, axis_z + 4.1))
    maximum_d_error, d_hole = 0.0, None
    for y in [bottom + 0.001, (bottom + top) / 2, top - 0.001]:
        actual = hole_at(section(mesh, 1, y), [0, axis_z])
        error = actual.boundary.hausdorff_distance(expected_d.boundary)
        require(error < 0.006, "BNC D-hole does not match 9.9 mm diameter / 9.05 mm flat height")
        maximum_d_error = max(maximum_d_error, error)
        d_hole = actual
    check_clear_axis(mesh, [0, axis_z], 1, bottom, top)
    width = d_hole.bounds[2] - d_hole.bounds[0]
    height = d_hole.bounds[3] - d_hole.bounds[1]
    flat_points = np.asarray(d_hole.exterior.coords)
    flat_points = flat_points[np.abs(flat_points[:, 1] - d_hole.bounds[3]) < 0.0001]
    bridge = float(np.ptp(flat_points[:, 0]))
    require(abs(bridge - 5.55) < 0.02, "The D-hole top bridge differs from 5.55 mm")
    reinforcement = check_reinforcement(profile, a5)
    frame = temporary_export("frame")
    require(frame.is_watertight and frame.is_winding_consistent and frame.volume > 0,
            "Isolated frame is not a closed positive solid")
    frame_section = section(frame, 2, frame_t / 2)
    native_restored = union_all([frame_section] + [hole_at(frame_section, center) for center in centers])
    native_error = native_restored.boundary.hausdorff_distance(profile.boundary)
    require(native_error < TOLERANCE_MM, "Isolated frame differs from the native mirrored profile")

    result = {
        "status": "passed",
        "stl_sha256": digest(stl),
        "scad_sha256": digest(HERE / "dipole_winder.scad"),
        "reference_profile_sha256": digest(HERE / "reference_profile.scad"),
        "accepted_layout_sha256": digest(A5_PATH),
        "mesh": {"watertight": True, "consistent_winding": True,
                 "connected_bodies": components, "triangles": len(mesh.faces),
                 "bounds_mm": mesh.bounds.tolist(), "volume_mm3": float(mesh.volume)},
        "frame": {"native_windows": len(profile.interiors), "added_holes": 7,
                  "m3_holes": 0, "section_z_mm": samples,
                  "maximum_native_frame_boundary_error_mm": native_error,
                  "maximum_combined_frame_and_shelf_boundary_error_mm": maximum_profile_error,
                  "shelf_base_added_area_outside_native_frame_mm2": restored_mid.difference(profile).area,
                  "maximum_bore_or_chamfer_boundary_error_mm": maximum_hole_error,
                  "relief_pitch_measured_mm": pitches,
                  "measured_hole_centers_mm": measured_centers,
                  "all_seven_hole_axes_clear": True},
        "bnc": {"measured_diameter_mm": width, "measured_flat_height_mm": height,
                "measured_flat_bridge_mm": bridge, "panel_thickness_mm": top - bottom,
                "maximum_d_hole_boundary_error_mm": maximum_d_error,
                "connector_axis_clear_through_panel": True},
        "reinforcement": reinforcement,
    }
    if source is not None:
        original = raw_source_profile(source)
        outer_error = Polygon(native_restored.exterior).boundary.hausdorff_distance(original.exterior)
        all_error = native_restored.boundary.hausdorff_distance(original.boundary)
        require(all_error < TOLERANCE_MM, "Actual frame differs from the original source by over 0.02 mm")
        result["original_source"] = {"sha256": digest(source),
                                     "maximum_outer_boundary_error_mm": outer_error,
                                     "maximum_all_boundaries_error_mm": all_error}
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stl", nargs="?", type=Path, default=HERE / "dipole_winder.stl")
    parser.add_argument("--source", type=Path)
    parser.add_argument("--output", type=Path, default=HERE / "validation.json")
    args = parser.parse_args()
    try:
        report = validate(args.stl, args.source)
    except Exception as error:
        report = {"status": "failed", "error": str(error)}
        args.output.write_text(json.dumps(report, indent=2) + "\n")
        raise
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
