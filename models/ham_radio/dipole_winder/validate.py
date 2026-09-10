#!/usr/bin/env python3
"""Check the ergonomic revision against the accepted A5 dimensions and fits.

From the repository root:

    uv run --no-project --with trimesh --with shapely --with scipy \
      --with networkx python models/ham_radio/dipole_winder/validate.py

Add --source /path/to/newWinder_wireframe.stl to compare with the original
supplied STL as well. Normal validation needs no external source STL. OpenSCAD
must be on PATH; isolated frame and reinforcement exports use a temporary folder.
The default output is validation.json beside this script. The revision fills
five small native windows and bevels the two frame faces by 0.5 mm; its middle
section must still preserve the original exterior and six larger openings.
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
FRAME_BEVEL_MM = 0.5
FILLED_NATIVE_WINDOW_IDS = (4, 5, 6, 9, 10)


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
    require(len(profile.interiors) == 11, "Expected all eleven native windows in the embedded source data")
    return profile


def ergonomic_profile(native: Polygon) -> Polygon:
    """Explicitly remove only the five reviewed small windows, by source ID."""
    return Polygon(native.exterior, [
        ring for index, ring in enumerate(native.interiors, 1)
        if index not in FILLED_NATIVE_WINDOW_IDS
    ])


def section(mesh: trimesh.Trimesh, axis: int, position: float,
            allow_disconnected: bool = False):
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
    allowed = ("Polygon", "MultiPolygon") if allow_disconnected else ("Polygon",)
    require(result.geom_type in allowed, "Section has disconnected material")
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


def check_reinforcement(profile: Polygon, a5: dict) -> tuple[dict, trimesh.Trimesh]:
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
            "profile_overrun_area_mm2": overrun}, ribs


def check_reinforcement_layer_support(mesh: trimesh.Trimesh, frame_t: float) -> dict:
    """Prevent rib bases from appearing outside the material below the top bevel.

    A base starting at the original top face produced a 0.299 mm ledge across
    a 0.2 mm print layer after the face was beveled. Across this transition the
    complete part's successive sections should only retreat, including where
    the frame disappears and the shelf/ribs continue upward.
    """
    planes = [frame_t + offset for offset in [-0.601, -0.401, -0.201, -0.001, 0.001, 0.199]]
    support_tolerance = 0.001
    sections = [section(mesh, 2, z) for z in planes]
    maximum_growth_area = 0.0
    for low, high, previous, following in zip(planes, planes[1:], sections, sections[1:]):
        growth = following.difference(previous)
        maximum_growth_area = max(maximum_growth_area, growth.area)
        unsupported = following.difference(previous.buffer(support_tolerance))
        require(unsupported.area < 1e-7,
                f"Rib/heel material starts beyond its supporting layer between Z={low} and Z={high}")
    return {"section_z_mm": planes,
            "outward_growth_tolerance_mm": support_tolerance,
            "maximum_unbuffered_growth_area_mm2": maximum_growth_area,
            "successive_sections_supported": True}


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
    native_profile = embedded_profile(HERE / "reference_profile.scad")
    profile = ergonomic_profile(native_profile)
    require(len(profile.interiors) == 6, "Expected six retained native windows")
    require(mesh.euler_number == -26, "Full winder must have fourteen through openings")
    top = a5["bnc_shelf_top_y_mm"]
    bottom = top - a5["bnc_shelf_thickness_mm"]
    # The A5 drawing adds a 26 mm perpendicular shelf to the native frame.
    # Its bed-supported base slightly widens the local outline; the horns and
    # the separate frame must retain the source dimensions and contours.
    shelf_profile = box(-13, bottom, 13, top)
    wire_centers = a5["left_relief_centers_mm"] + a5["right_relief_centers_mm"]
    centers = wire_centers + [a5["eye_center_mm"]]
    diameters = [a5["wire_bore_mm"]] * 6 + [a5["eye_bore_mm"]]
    frame_t = a5["frame_extent_mm"][2]
    chamfer = a5["chamfer_mm"]
    samples = [0.001, 0.25, 0.499, frame_t / 2, frame_t-0.499, frame_t-0.25, frame_t-0.001]
    maximum_hole_error, maximum_profile_error, maximum_frame_error = 0.0, 0.0, 0.0
    minimum_eye_ligament, minimum_relief_ligament = float("inf"), float("inf")
    restored_mid = None
    native_restored = None
    measured_centers = []
    reinforcement, ribs = check_reinforcement(profile, a5)
    reinforcement["base_layer_support"] = check_reinforcement_layer_support(mesh, frame_t)
    frame = temporary_export("frame")
    require(frame.is_watertight and frame.is_winding_consistent and frame.volume > 0,
            "Isolated frame is not a closed positive solid")
    require(len(frame.split(only_watertight=False)) == 1 and frame.euler_number == -24,
            "Isolated frame must be one body with thirteen through openings")
    for z in samples:
        material = section(mesh, 2, z)
        frame_material = section(frame, 2, z)
        require(len(material.interiors) == len(profile.interiors) + 7,
                "Frame contains extra or missing holes (including possible M3 holes)")
        require(len(frame_material.interiors) == 13, "Isolated frame has an extra or missing opening")
        new_holes = []
        frame_holes = []
        for center, diameter in zip(centers, diameters):
            actual = hole_at(material, center)
            frame_hole = hole_at(frame_material, center)
            radius = diameter / 2 + max(0, chamfer - min(z, frame_t - z))
            expected = Point(center).buffer(radius, quad_segs=256)
            error = max(actual.boundary.hausdorff_distance(expected.boundary),
                        frame_hole.boundary.hausdorff_distance(expected.boundary))
            require(error < 0.006, f"Incorrect bore or chamfer at {center}, Z={z}")
            require(actual.centroid.distance(Point(center)) < 0.0001,
                    f"Hole center differs from accepted A5 coordinates: {center}")
            maximum_hole_error = max(maximum_hole_error, error)
            new_holes.append(actual)
            frame_holes.append(frame_hole)
            ligament = frame_hole.boundary.distance(frame_material.exterior)
            if center == a5["eye_center_mm"]:
                minimum_eye_ligament = min(minimum_eye_ligament, ligament)
            else:
                minimum_relief_ligament = min(minimum_relief_ligament, ligament)
            if z == frame_t / 2:
                measured_centers.append(list(actual.centroid.coords[0]))
        restored = union_all([material] + new_holes)
        restored_frame = union_all([frame_material] + frame_holes)
        inset = max(0, FRAME_BEVEL_MM - min(z, frame_t-z))
        expected_frame = profile.buffer(-inset, quad_segs=256) if inset else profile
        frame_error = restored_frame.boundary.hausdorff_distance(expected_frame.boundary)
        require(frame_error < TOLERANCE_MM,
                f"Isolated frame differs from the intended 0.5 mm face bevel at Z={z}")
        maximum_frame_error = max(maximum_frame_error, frame_error)
        expected_composite = expected_frame.union(shelf_profile)
        # Structural roots begin in the full-width middle band, below the top
        # bevel. Their separately checked sections replace the local bevel.
        if ribs.bounds[0, 2] < z < ribs.bounds[1, 2]:
            expected_composite = expected_composite.union(section(ribs, 2, z, allow_disconnected=True))
        error = restored.boundary.hausdorff_distance(expected_composite.boundary)
        require(error < TOLERANCE_MM,
                f"Actual contour differs from the beveled frame, shelf and reinforcement at Z={z}")
        maximum_profile_error = max(maximum_profile_error, error)
        if z == frame_t / 2:
            restored_mid = restored
            native_restored = restored_frame
    require(minimum_eye_ligament >= 2.45, "Beveled eye has less than 2.45 mm of surrounding material")
    require(minimum_relief_ligament >= 2.30, "Beveled relief hole has less than 2.30 mm of exterior material")
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
    native_error = native_restored.boundary.hausdorff_distance(profile.boundary)
    require(native_error < TOLERANCE_MM, "Middle section differs from the native exterior and six retained windows")

    result = {
        "status": "passed",
        "stl_sha256": digest(stl),
        "scad_sha256": digest(HERE / "dipole_winder.scad"),
        "reference_profile_sha256": digest(HERE / "reference_profile.scad"),
        "frame_bevel_sha256": digest(HERE / "frame_bevel.scad"),
        "accepted_layout_sha256": digest(A5_PATH),
        "mesh": {"watertight": True, "consistent_winding": True,
                 "connected_bodies": components, "triangles": len(mesh.faces),
                 "through_openings": 14,
                 "bounds_mm": mesh.bounds.tolist(), "volume_mm3": float(mesh.volume)},
        "frame": {"native_windows": len(profile.interiors), "added_holes": 7,
                  "filled_native_window_ids": list(FILLED_NATIVE_WINDOW_IDS),
                  "filled_window_area_mm2": profile.area-native_profile.area,
                  "face_bevel_mm": FRAME_BEVEL_MM,
                  "m3_holes": 0, "section_z_mm": samples,
                  "maximum_native_frame_boundary_error_mm": native_error,
                  "maximum_beveled_frame_boundary_error_mm": maximum_frame_error,
                  "maximum_combined_frame_and_shelf_boundary_error_mm": maximum_profile_error,
                  "shelf_base_added_area_outside_native_frame_mm2": restored_mid.difference(profile).area,
                  "maximum_bore_or_chamfer_boundary_error_mm": maximum_hole_error,
                  "relief_pitch_measured_mm": pitches,
                  "measured_hole_centers_mm": measured_centers,
                  "minimum_eye_exterior_ligament_mm": minimum_eye_ligament,
                  "minimum_relief_exterior_ligament_mm": minimum_relief_ligament,
                  "all_seven_hole_axes_clear": True},
        "bnc": {"measured_diameter_mm": width, "measured_flat_height_mm": height,
                "measured_flat_bridge_mm": bridge, "panel_thickness_mm": top - bottom,
                "maximum_d_hole_boundary_error_mm": maximum_d_error,
                "connector_axis_clear_through_panel": True},
        "reinforcement": reinforcement,
    }
    if source is not None:
        original = raw_source_profile(source)
        filled_regions = [Polygon(native_profile.interiors[index-1])
                          for index in FILLED_NATIVE_WINDOW_IDS]
        kept_original_windows = [ring for ring in original.interiors
                                 if not any(region.covers(Polygon(ring).representative_point())
                                            for region in filled_regions)]
        require(len(original.interiors)-len(kept_original_windows) == 5,
                "Original source comparison must ignore exactly the five intentionally filled windows")
        revised_original = Polygon(original.exterior, kept_original_windows)
        outer_error = Polygon(native_restored.exterior).boundary.hausdorff_distance(original.exterior)
        all_error = native_restored.boundary.hausdorff_distance(revised_original.boundary)
        require(all_error < TOLERANCE_MM, "Retained native boundaries differ from the original source by over 0.02 mm")
        result["original_source"] = {"sha256": digest(source),
                                     "intentionally_filled_native_windows": 5,
                                     "maximum_outer_boundary_error_mm": outer_error,
                                     "maximum_retained_boundaries_error_mm": all_error}
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
