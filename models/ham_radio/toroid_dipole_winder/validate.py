#!/usr/bin/env python3
"""Export and measure the toroid winder and its supported fit parameters.

Run `mise run toroid-winder:check` from the repository root. This verifies CAD
geometry and explicitly reserved assembly envelopes; it does not certify
printed strength, wire storage capacity, electrical performance, or power.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

import numpy as np
import trimesh
from shapely import union_all
from shapely.geometry import MultiPoint, Point, Polygon, box


HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parent / "dipole_winder"
SCAD = HERE / "toroid_dipole_winder.scad"
PETG_G_CM3 = 1.27
TOL = 0.02

# Reuse geometric readers, not the original model's pass/fail assumptions.
spec = importlib.util.spec_from_file_location("original_geometry", ORIGINAL / "validate.py")
original_geometry = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(original_geometry)
section = original_geometry.section
require = original_geometry.require
check_clear_axis = original_geometry.check_clear_axis


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export(path: Path, parameters: dict | None = None, error: str | None = None) -> dict:
    command = [shutil.which("openscad") or "openscad", "--hardwarnings", "--export-format", "binstl"]
    for key, value in (parameters or {}).items():
        command.extend(["-D", f"{key}={json.dumps(value)}"])
    command.extend(["-o", str(path), str(SCAD)])
    result = subprocess.run(command, capture_output=True, text=True)
    output = result.stdout + result.stderr
    if error:
        require(result.returncode != 0 and "ERROR: Assertion" in output and error in output,
                f"Invalid settings did not fail with '{error}': {output}")
        return {"parameters": parameters, "expected_assertion": error, "rejected": True}
    require(result.returncode == 0 and "ERROR:" not in output and "WARNING:" not in output,
            f"OpenSCAD export failed: {output}")
    require(path.exists(), "OpenSCAD did not create its output")
    return {"parameters": parameters or {}, "hardwarnings_passed": True}


def dimensions(parameters: dict) -> dict:
    diameter = parameters.get("package_d", 36)
    thickness = parameters.get("package_h", 20)
    foam = parameters.get("foam_t", 1)
    projection = parameters.get("bnc_rear_projection", 12)
    offset = diameter / 2 + 4
    # Independent design requirements: 3.8 mm from rear contact to slot mouth.
    lower_slot, upper_slot = 31 - offset, 31 + offset
    top = lower_slot - 1.2 - 0.3 - 3.8 - projection
    return {"package_d": diameter, "package_h": thickness, "foam_t": foam,
            "projection": projection, "lower_slot": lower_slot, "upper_slot": upper_slot,
            "shelf_top": top, "shelf_bottom": top - 3,
            "spine_bottom": top - 15, "spine_top": upper_slot + 4,
            "bnc_hole_d": parameters.get("bnc_hole_d", 10.1),
            "bnc_flat_depth": parameters.get("bnc_flat_depth", 0.85)}


def polygons(geometry):
    return [geometry] if isinstance(geometry, Polygon) else list(geometry.geoms)


def hole_at(material, center) -> Polygon:
    matches = [Polygon(ring) for polygon in polygons(material) for ring in polygon.interiors
               if Polygon(ring).covers(Point(center))]
    require(len(matches) == 1, f"Expected one open hole at {center}")
    return matches[0]


def inspect_mesh(path: Path, coupon: bool = False, dims: dict | None = None) -> tuple:
    mesh = trimesh.load(path, force="mesh")
    bodies = len(mesh.split(only_watertight=False))
    require(mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0,
            f"{path.name}: expected a closed, consistently oriented positive mesh; "
            f"watertight={mesh.is_watertight}, winding={mesh.is_winding_consistent}, volume={mesh.volume}")
    require(bodies == 1, f"{path.name}: expected one connected body, found {bodies}")
    if coupon:
        expected = [[-14, 0, 0], [14, dims["spine_top"] - dims["spine_bottom"], 24]]
    else:
        expected = [[-37.5, -70, 0], [37.5, 70, 24]]
    require(np.allclose(mesh.bounds, expected, atol=0.0001),
            f"{path.name}: unexpected bounds {mesh.bounds.tolist()}")
    return mesh, {"watertight": True, "consistent_winding": True,
                  "connected_bodies": bodies, "triangles": len(mesh.faces),
                  "bounds_mm": mesh.bounds.tolist(), "volume_mm3": float(mesh.volume),
                  "solid_PETG_mass_g_at_1p27_g_cm3": float(mesh.volume / 1000 * PETG_G_CM3)}


def check_horns_and_original_holes(mesh) -> dict:
    profile = original_geometry.ergonomic_profile(
        original_geometry.embedded_profile(ORIGINAL / "reference_profile.scad"))
    layout = json.loads(original_geometry.A5_PATH.read_text())
    centers = layout["left_relief_centers_mm"] + layout["right_relief_centers_mm"] + [layout["eye_center_mm"]]
    diameters = [3.2] * 6 + [6]
    # New parts are contained inside |X| <= 13 and below Y59. This checks all
    # four horns, the outer native spine contours, and the whole hoisting eye.
    preserved = union_all([box(-100, -100, -14, 100), box(14, -100, 100, 100),
                           box(-100, 59, 100, 100)])
    samples = [0.001, 0.25, 0.499, 2.5, 4.501, 4.75, 4.999]
    max_outline, max_hole = 0.0, 0.0
    for z in samples:
        actual = section(mesh, 2, z)
        inset = max(0, 0.5 - min(z, 5-z))
        expected = profile.buffer(-inset, quad_segs=256) if inset else profile
        for center, diameter in zip(centers, diameters):
            bore = Point(center).buffer(diameter/2 + inset, quad_segs=256)
            expected = expected.difference(bore)
            actual_hole = hole_at(actual, center)
            error = actual_hole.boundary.hausdorff_distance(bore.boundary)
            require(error < 0.006, f"Original hole/chamfer changed at {center}, Z={z}")
            require(actual_hole.centroid.distance(Point(center)) < 0.0001,
                    "Original antenna or hanging-hole center moved")
            max_hole = max(max_hole, error)
        error = actual.intersection(preserved).boundary.hausdorff_distance(
            expected.intersection(preserved).boundary)
        require(error < TOL, f"Native horns/eye silhouette changed at Z={z}")
        max_outline = max(max_outline, error)
    for center in centers:
        check_clear_axis(mesh, center, 2, -0.001, 5.001)
    return {"four_horns_retained": True, "original_seven_holes_clear": True,
            "section_z_mm": samples, "maximum_preserved_boundary_error_mm": max_outline,
            "maximum_bore_or_chamfer_error_mm": max_hole,
            "hole_centers_mm": centers}


def check_tie_slots(mesh, dims: dict) -> dict:
    centers = [[x, y] for x in [-4, 4] for y in [dims["lower_slot"], dims["upper_slot"]]]
    errors, dimensions_at_mid = [], []
    # The subtractive chamfer is sampled near both faces and in the straight bore.
    samples = [0.001, 0.15, 0.301, 2.5, 4.699, 4.85, 4.999]
    for z in samples:
        material = section(mesh, 2, z)
        for x, y in centers:
            actual = hole_at(material, [x, y])
            # The hull deliberately extends 0.02 mm beyond its nominal 0.3 mm
            # inner chamfer plane. Account for that small transition, but bound
            # the error to the intended dimensions rather than assuming a mesh.
            expansion = max(0, 0.3 - min(z, 5-z))
            expected = box(x-1.7-expansion, y-1.2-expansion,
                           x+1.7+expansion, y+1.2+expansion)
            error = actual.boundary.hausdorff_distance(expected.boundary)
            require(error <= 0.029, f"Tie slot dimensions/chamfer incorrect at {[x,y]}, Z={z}")
            errors.append(error)
            if z == 2.5:
                dimensions_at_mid.append([actual.bounds[2]-actual.bounds[0], actual.bounds[3]-actual.bounds[1]])
                require(np.allclose(dimensions_at_mid[-1], [3.4, 2.4], atol=0.0001),
                        "Tie bore is not 3.4 by 2.4 mm")
            require(actual.centroid.distance(Point(x, y)) < 0.0001, "Tie slot moved")
    for center in centers:
        check_clear_axis(mesh, center, 2, -0.001, 5.001)
    # Actual nearest material edge around each slot; this includes any nearby
    # native windows rather than assuming that the added spine filled them.
    face = section(mesh, 2, 4.999)
    ligaments = []
    for center in centers:
        hole = hole_at(face, center)
        candidates = [face.exterior] + [ring for ring in face.interiors
                                       if not Polygon(ring).covers(Point(center))]
        ligaments.append(min(hole.boundary.distance(edge) for edge in candidates))
    require(min(ligaments) >= 2, "Tie-slot mouth leaves less than 2 mm actual material")
    return {"four_slots_clear": True, "centers_mm": centers,
            "straight_bore_dimensions_mm": dimensions_at_mid,
            "section_z_mm": samples, "maximum_boundary_error_mm": max(errors),
            "minimum_actual_face_ligament_mm": min(ligaments)}


def check_connector(mesh, dims: dict) -> dict:
    bottom, top = dims["shelf_bottom"], dims["shelf_top"]
    diameter, flat = dims["bnc_hole_d"], dims["bnc_flat_depth"]
    expected = Point(0, 15).buffer(diameter/2, quad_segs=256).intersection(
        box(-20, -20, 20, 15+diameter/2-flat))
    errors, measured = [], None
    for y in [bottom+0.001, (bottom+top)/2, top-0.001]:
        actual = hole_at(section(mesh, 1, y, allow_disconnected=True), [0, 15])
        error = actual.boundary.hausdorff_distance(expected.boundary)
        require(error < 0.006, "BNC D-cutout dimensions or flat orientation are incorrect")
        errors.append(error)
        measured = actual
    check_clear_axis(mesh, [0, 15], 1, bottom-0.001, top+0.001)
    # Triangle projections test complete surfaces, not vertices alone. Exclude
    # the intentional mounting annulus but include the original frame/spine.
    distances = []
    for low, high in [(bottom-11.9, bottom-0.0001),
                      (top+0.0001, top+dims["projection"])]:
        clipped = mesh.slice_plane([0, low, 0], [0, 1, 0], cap=False)
        clipped = clipped.slice_plane([0, high, 0], [0, -1, 0], cap=False)
        nearest = min(Point(0, 15).distance(MultiPoint(triangle[:, [0, 2]]).convex_hull)
                      for triangle in clipped.triangles)
        require(nearest >= 9-0.0001, "Mesh intrudes into the 18 mm hardware envelope")
        distances.append(nearest)
    return {"shelf_bottom_y_mm": bottom, "shelf_top_y_mm": top,
            "panel_thickness_mm": 3, "measured_cutout_width_mm": measured.bounds[2]-measured.bounds[0],
            "measured_cutout_height_mm": measured.bounds[3]-measured.bounds[1],
            "maximum_cutout_boundary_error_mm": max(errors),
            "hardware_radius_mm": 9, "minimum_axis_distance_front_and_rear_mm": distances,
            "mounting_panel_excluded_from_hardware_keepout": True}


def check_foot_support(mesh, dims: dict) -> dict:
    # The new foot is meant to print from the bed, with ribs retreating inward
    # as Z increases. Keep the scope local; the top of the D-hole is a separate,
    # intentionally short bridge, not a claim of zero overhang everywhere.
    region = box(-12.49, dims["shelf_bottom"]-9.99, 12.49, dims["shelf_bottom"]-0.05)
    heights = [0.001, 0.2, 0.499, 0.501, 4.399, 4.499, 4.501, 4.599, 4.601,
               4.699, 4.899, 4.999, 5.001, 5.199, 7.199, 9.199, 12.199, 14.9]
    slices = [section(mesh, 2, z, allow_disconnected=True).intersection(region) for z in heights]
    max_growth = 0.0
    for low, high, previous, following in zip(heights, heights[1:], slices, slices[1:]):
        # The intentionally beveled underside grows at 45 degrees through
        # Z0.5. Above it, newly appearing shelf/rib material is forbidden.
        bevel_growth = max(0, 0.5-low) - max(0, 0.5-high)
        growth = following.difference(previous.buffer(bevel_growth+0.001)).area
        max_growth = max(max_growth, growth)
        require(growth < 1e-6,
                f"Connector foot/rib develops unsupported material between Z={low} and Z={high}")
    require(slices[0].area >= 210, "The connector foot does not start broadly on the print bed")
    return {"section_z_mm": heights, "successive_foot_and_rib_sections_supported": True,
            "maximum_growth_beyond_0p001_mm_tolerance_mm2": max_growth,
            "foot_bed_section_area_mm2": slices[0].area,
            "allowed_bed_bevel_growth": "45 degrees through Z0.5 only",
            "scope": "Foot/ribs below mounting panel; D-hole top bridge requires slicer inspection"}


def check_assembly_envelopes(mesh, dims: dict) -> dict:
    radius = dims["package_d"] / 2
    packet = Point(0, 31).buffer(radius, quad_segs=256)
    corridors = union_all([box(22, 13, 32, 49), box(-32, 13, -22, 49)])
    foam = box(-7, 16, 7, 46)
    top_frame = section(mesh, 2, 4.999)
    require(top_frame.covers(foam), "The 14 by 30 mm foam strip is not supported by solid frame")
    # Cut the real printable mesh above its frame: no bracket may enter the
    # reserved packet, padded underside, or wire corridors at any raised Z.
    raised = mesh.slice_plane([0, 0, 5.001], [0, 0, 1], cap=False)
    projection = union_all([MultiPoint(triangle[:, :2]).convex_hull for triangle in raised.triangles])
    require(projection.intersection(packet).area < 1e-6, "A raised print feature intersects the packet envelope")
    require(projection.intersection(corridors).area < 1e-6, "Raised print feature enters winding corridors")
    packet_clearance = packet.distance(corridors)
    require(packet_clearance >= 3-1e-5, "Packet leaves less than 3 mm to winding corridors")
    contact_y = dims["shelf_top"] + dims["projection"]
    slot_mouth_y = dims["lower_slot"] - 1.2 - 0.3
    require(abs(slot_mouth_y-contact_y-3.8) < 1e-6, "Rear contact does not clear tie mouth by 3.8 mm")
    packet_contact_gap = 31-radius-contact_y
    require(packet_contact_gap > 0, "BNC rear contact reaches the packet")
    upper_relief_y = 55.050156773381225
    relief_gap = upper_relief_y - (31+radius)
    require(relief_gap >= 5, "Packet occupies upper wire-tail relief area")
    strap_projection = union_all([box(x-1.25, dims["lower_slot"], x+1.25, dims["upper_slot"])
                                  for x in [-4, 4]])
    require(not strap_projection.intersects(corridors), "Straps enter wire corridors")
    bnc_projection = box(-9, dims["shelf_bottom"]-11.9, 9, contact_y)
    require(not bnc_projection.intersects(corridors), "Connector envelope enters wire corridors")
    return {"packet_bounds_mm": [[-radius, 31-radius, 5+dims["foam_t"]],
                                [radius, 31+radius, 5+dims["foam_t"]+dims["package_h"]]],
            "foam_strip_xy_bounds_mm": list(foam.bounds), "foam_supported_by_measured_mesh": True,
            "raised_mesh_clear_of_packet": True,
            "rear_contact_to_lower_tie_mouth_mm": slot_mouth_y-contact_y,
            "rear_contact_to_packet_mm": packet_contact_gap,
            "packet_to_inner_relief_center_y_gap_mm": relief_gap,
            "winding_corridors_xy_mm": [[-32, 13, -22, 49], [22, 13, 32, 49]],
            "packet_to_winding_corridor_mm": packet_clearance,
            "reserved_connector_and_straps_clear_of_corridors": True,
            "limits": "Assembly envelopes are allowances, not measured hardware. Hand-routed leads must stay inside |X|<22 through Y13–49. Corridors do not prove storage capacity."}


def check_winder(path: Path, parameters: dict) -> dict:
    dims = dimensions(parameters)
    mesh, mesh_result = inspect_mesh(path)
    result = {"parameters": parameters, "mesh": mesh_result,
              "tie_slots": check_tie_slots(mesh, dims),
              "connector": check_connector(mesh, dims),
              "connector_foot_support": check_foot_support(mesh, dims),
              "assembly_envelopes": check_assembly_envelopes(mesh, dims)}
    if not parameters:
        result["preserved_frame"] = check_horns_and_original_holes(mesh)
    return result


def check_loaded_mockup(temp: Path, printable_path: Path) -> dict:
    """Intersect the actual rendered bundle mesh with the printable part.

    Projecting electronics meshes into XY gives a stronger, all-Z exclusion
    proof where their footprints are disjoint from the bundle footprint.
    """
    def module_export(name: str):
        wrapper = temp / f"{name}.scad"
        path = temp / f"{name}.stl"
        wrapper.write_text(f"use <{HERE / 'mockups.scad'}>\n{name}();\n")
        command = [shutil.which("openscad") or "openscad", "--hardwarnings", "--export-format", "binstl",
                   "-o", str(path), str(wrapper)]
        result = subprocess.run(command, capture_output=True, text=True)
        require(result.returncode == 0 and "WARNING:" not in result.stderr and "ERROR:" not in result.stderr,
                f"Mockup module {name} export failed: {result.stderr}")
        mesh = trimesh.load(path, force="mesh")
        require(len(mesh.faces) > 0, f"Mockup module {name} has no measured surface")
        if name == "storage_corridors":
            require(mesh.is_watertight and mesh.volume > 0, "Loaded bundle is not a closed mesh")
        return mesh

    bundles = module_export("storage_corridors")
    printable = trimesh.load(printable_path, force="mesh")
    collision = trimesh.boolean.intersection([bundles, printable], engine="manifold")
    volume = 0.0 if collision.is_empty else float(collision.volume)
    require(volume < 1e-6, f"Loaded bundle geometry intersects printable part by {volume} mm³")
    bundle_xy = union_all([MultiPoint(triangle[:, :2]).convex_hull for triangle in bundles.triangles])
    clearances = {}
    for name in ["packet", "straps", "leads", "hardware"]:
        obstacle = module_export(name)
        obstacle_xy = union_all([MultiPoint(triangle[:, :2]).convex_hull for triangle in obstacle.triangles])
        clearance = bundle_xy.distance(obstacle_xy)
        require(clearance > 0.5, f"Mocked {name} enters or approaches loaded bundles within 0.5 mm")
        clearances[name] = clearance
    return {"actual_loaded_bundle_bounds_mm": bundles.bounds.tolist(),
            "printable_intersection_volume_mm3": volume,
            "projected_all_z_electronics_clearances_mm": clearances,
            "scope": "Illustrated bundle geometry only; actual winding capacity and placement require a loaded-winder check"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "validation.json")
    args = parser.parse_args()
    stl = HERE / "toroid_dipole_winder.stl"
    coupon = HERE / "toroid_mount_test.stl"
    export(stl)
    default = check_winder(stl, {})
    print("Default mesh, original horns/holes, slots, BNC, foot support and assembly envelopes passed.", flush=True)
    export(coupon, {"part": "mount_coupon"})
    _, coupon_result = inspect_mesh(coupon, coupon=True, dims=dimensions({}))
    variants, rejected = [], []
    with tempfile.TemporaryDirectory(prefix="toroid-winder-validation-") as folder:
        temp = Path(folder)
        loaded = check_loaded_mockup(temp, stl)
        print("Actual loaded bundle mesh clears printable model and mocked electronics.", flush=True)
        for index, parameters in enumerate([
            {"package_d": 32, "bnc_rear_projection": 8, "package_h": 16, "foam_t": 0.5},
            {"package_d": 32, "bnc_rear_projection": 16},
            {"package_d": 38, "bnc_rear_projection": 8},
            {"package_d": 38, "bnc_rear_projection": 16, "package_h": 22, "foam_t": 2},
            {"bnc_hole_d": 9.7}, {"bnc_hole_d": 10.3},
        ]):
            path = temp / f"variant-{index}.stl"
            export(path, parameters)
            variants.append(check_winder(path, parameters))
            print(f"Parameter geometry passed: {parameters}", flush=True)
        for index, (parameters, expected) in enumerate([
            ({"package_d": 31.9}, "Package diameter"),
            ({"package_d": 38.1}, "Package diameter"),
            ({"package_h": 22.1}, "Package thickness"),
            ({"foam_t": 0.4}, "cushioning"),
            ({"bnc_rear_projection": 7.9}, "Rear projection"),
            ({"bnc_rear_projection": 16.1}, "Rear projection"),
            ({"bnc_hole_d": 10.4}, "BNC hole"),
            ({"bnc_flat_depth": 1.3}, "BNC flat depth"),
            ({"part": "missing"}, "Unknown part"),
        ]):
            rejected.append(export(temp / f"invalid-{index}.stl", parameters, expected))
    old_mesh = trimesh.load(ORIGINAL / "dipole_winder.stl", force="mesh")
    old_volume = float(old_mesh.volume)
    added = default["mesh"]["volume_mm3"] - old_volume
    inputs = [SCAD, HERE / "validate.py", ORIGINAL / "dipole_winder.scad",
              ORIGINAL / "reference_profile.scad", ORIGINAL / "frame_bevel.scad",
              ORIGINAL / "validate.py", original_geometry.A5_PATH, HERE / "mockups.scad"]
    report = {"status": "passed", "scope": "Measured CAD geometry and explicit assembly allowances; physical and RF validation remains necessary",
              "source_sha256": {str(path.relative_to(HERE.parents[2])): digest(path) for path in inputs},
              "artifacts": {stl.name: digest(stl), coupon.name: digest(coupon)},
              "default": default, "mount_coupon": coupon_result,
              "loaded_mockup": loaded,
              "parameter_variants": variants, "rejected_parameters": rejected,
              "weight_comparison": {"PETG_density_g_cm3": PETG_G_CM3,
                                    "original_stl_sha256": digest(ORIGINAL / "dipole_winder.stl"),
                                    "original_volume_mm3": old_volume, "added_volume_mm3": added,
                                    "added_solid_PETG_mass_g": added / 1000 * PETG_G_CM3,
                                    "excludes": "Core, windings, heatshrink, foam, straps, BNC, wire and slicer extrusion variation"}}
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Passed: {len(variants)} parameter variants, {len(rejected)} rejected settings; wrote {args.output}")


if __name__ == "__main__":
    main()
