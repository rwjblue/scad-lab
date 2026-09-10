"""Sample advertised modular-dipole settings in exported CAD.

These checks exercise coordinated parameter endpoints and one large combined
configuration. They are distinct from the full release-motion audit of the two
default presets, and do not establish arbitrary combinations or wire capacity.
Variant meshes live only in the caller's temporary directory.
"""
from __future__ import annotations

from pathlib import Path
import json
import subprocess

import numpy as np
import trimesh
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

from validation_helpers import (HERE, TOL, bounds_mesh, export,
                                intersection_volume, mesh_report, require,
                                sections, translated, volume)

SCAD = HERE / "modular_dipole.scad"
EPS_VOLUME = 0.001
DEFAULTS = {
    "preset": "40m", "wing_length": 37.5, "winding_span": 140,
    "wire_face_bulge": 0, "wire_edge_bulge": 5, "standoff": 4,
    "wire_hole_inner_x": 28, "wire_hole_pitch": 5.5,
    "wire_hole_d": 3.2, "wire_chamfer": 0.5,
    "terminal_hole_d": 3.4, "hang_hole_d": 6, "bnc_hole_d": 10.1,
}

# Individual hole limits interact through the barrel clearance, mouth-to-mouth
# web, and outer edge distance. Exercise their endpoints in valid combinations.
VARIANTS = {
    "minimum_standoff": {"standoff": 2.5},
    "intermediate_standoff": {"standoff": 5.5},
    "original_40m_standoff": {"standoff": 8},
    "original_80m_standoff": {"preset": "80m", "standoff": 11},
    "maximum_standoff": {"preset": "80m", "standoff": 25},
    "long_wings_low_buildup": {
        "wing_length": 60, "wire_face_bulge": 2, "wire_edge_bulge": 2,
    },
    "wide_span_deep_buildup": {
        "winding_span": 200, "wire_face_bulge": 12,
        "wire_edge_bulge": 5, "standoff": 4,
    },
    "small_outward_holes": {
        "wire_hole_inner_x": 30, "wire_hole_pitch": 4,
        "wire_hole_d": 2.6, "wire_chamfer": 0,
        "terminal_hole_d": 3.1, "hang_hole_d": 4, "bnc_hole_d": 9.7,
    },
    "wide_hole_pitch": {
        "wire_hole_inner_x": 27, "wire_hole_pitch": 6.5,
        "wire_hole_d": 2.6, "wire_chamfer": 0,
        "terminal_hole_d": 3.6, "bnc_hole_d": 10.2,
    },
    "large_wire_holes": {
        # Simultaneous 1.2 mm mouth web and 3 mm outer edge distance.
        "wire_hole_inner_x": 27.6, "wire_hole_d": 3.6,
        "wire_hole_pitch": 6, "wire_chamfer": 0.6,
    },
    "combined_large_packet": {
        "preset": "80m", "wing_length": 60, "winding_span": 200,
        "wire_face_bulge": 12, "wire_edge_bulge": 5, "standoff": 25,
        "wire_hole_pitch": 5.6, "wire_chamfer": 0.6,
        "terminal_hole_d": 3.6, "bnc_hole_d": 10.2,
    },
}

INVALID = {
    "insufficient_barrel_clearance": {
        "wire_hole_inner_x": 27, "wire_hole_d": 3.6, "wire_chamfer": 0.6,
    },
    "insufficient_hole_web": {
        "wire_hole_pitch": 4, "wire_hole_d": 3.6, "wire_chamfer": 0.6,
    },
    "insufficient_outer_edge": {"wire_hole_inner_x": 30, "wire_hole_pitch": 6.5},
    "undersized_face_reserve": {"wire_face_bulge": 1},
    "oversized_edge_reserve": {"wire_edge_bulge": 5.5},
    "overlong_wings": {"wing_length": 61},
    "undersized_span": {"winding_span": 139},
    "undersized_bnc": {"bnc_hole_d": 9.6},
    "undersized_standoff": {"standoff": 2.49},
    "oversized_standoff": {"standoff": 25.01},
}


def seat_height(parameters):
    return 5 + parameters["standoff"]


def definitions(parameters, part):
    return [f"part={json.dumps(part)}"] + [
        f"{key}={json.dumps(value)}" for key, value in parameters.items()
    ]


def material_holes(material):
    shapes = [material] if material.geom_type == "Polygon" else list(material.geoms)
    return [Polygon(ring) for shape in shapes for ring in shape.interiors]


def hole_at(material, x, y):
    matches = [hole for hole in material_holes(material) if hole.covers(Point(x, y))]
    require(len(matches) == 1, f"Expected one enclosed hole at ({x}, {y})")
    return matches[0]


def hole_locations(parameters):
    result = [(0, 32, parameters["hang_hole_d"], parameters["wire_chamfer"])]
    for side in [-1, 1]:
        result.append((side * 10, 21, parameters["terminal_hole_d"], 0))
        for index in range(3):
            x = parameters["wire_hole_inner_x"] + index * parameters["wire_hole_pitch"]
            result.append((side * x, 21, parameters["wire_hole_d"],
                           parameters["wire_chamfer"]))
    return result


def plate_hole_checks(center, baseline, parameters):
    measurements = []
    restored_area = 0.0
    for z in [0.1, 0.3, 0.6, 2, 3.4, 3.7, 3.9]:
        material = sections(center, z)
        current_holes = []
        for x, y, diameter, chamfer in hole_locations(parameters):
            hole = hole_at(material, x, y)
            actual = np.asarray(hole.bounds)
            radius = diameter / 2 + max(0, chamfer - min(z, 4 - z))
            expected = np.asarray([x - radius, y - radius, x + radius, y + radius])
            require(np.max(np.abs(actual - expected)) < TOL,
                    f"Hole at ({x}, {y}), Z={z} differs from requested size/location: "
                    f"{actual.tolist()} vs {expected.tolist()}")
            current_holes.append(hole)
            measurements.append({"center_mm": [x, y], "section_z_mm": z,
                                 "measured_bounds_mm": actual.tolist(),
                                 "expected_diameter_mm": 2 * radius})
        # Test restoration directly: portions of inherited holes which no longer
        # belong to the requested openings must become solid again.
        old_material = sections(baseline, z)
        old_holes = unary_union([hole_at(old_material, x, y)
                                 for x, y, _, _ in hole_locations(DEFAULTS)])
        restored = old_holes.difference(unary_union(current_holes))
        missing = restored.difference(material).area
        require(missing < 0.001, f"An old hole remains at Z={z}: {missing} mm²")
        restored_area += restored.area
    return {"holes_checked": 9, "sections_checked": 7,
            "restored_inherited_void_area_sum_mm2": restored_area,
            "measurements": measurements}


def bnc_checks(center, diameter):
    measured = []
    for y in [0.1, 1.5, 2.9]:
        section = center.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
        require(section is not None, "Missing BNC panel section")
        material = Polygon()
        for contour in section.discrete:
            require(np.linalg.norm(contour[0] - contour[-1]) < TOL,
                    "Open BNC section contour")
            polygon = Polygon(contour[:, [0, 2]])
            require(polygon.is_valid, "Invalid BNC panel section")
            material = material.symmetric_difference(polygon)
        opening = hole_at(material, 0, 14)
        x0, z0, x1, z1 = opening.bounds
        require(abs(x1 - x0 - diameter) < TOL, "Requested BNC diameter not exported")
        require(abs(z1 - z0 - (diameter - 0.85)) < TOL,
                "Requested BNC D-flat span not exported")
        require(abs(z1 - (14 + diameter / 2 - 0.85)) < TOL,
                "BNC anti-rotation flat moved from the top")
        measured.append({"panel_y_mm": y, "diameter_mm": x1 - x0,
                         "flat_to_opposite_edge_mm": z1 - z0,
                         "top_flat_z_mm": z1})
    return {"requested_diameter_mm": diameter, "section_measurements": measured}


def symmetric_volume(a, b):
    return sum(volume(trimesh.boolean.difference(pair, engine="manifold"))
               for pair in [[a, b], [b, a]])


def fixed_center_checks(center, baseline):
    # These generous exclusion regions cover every allowed plate-hole mouth
    # and the BNC bore; all structural surfaces and four flexures stay outside.
    tools = [bounds_mesh([-42.1, 18.5, -0.02], [42.1, 23.5, 4.02]),
             bounds_mesh([-3.7, 28.3, -0.02], [3.7, 35.7, 4.02]),
             bounds_mesh([-5.2, -0.02, 8.8], [5.2, 3.02, 19.2])]
    permitted = trimesh.boolean.union(tools, engine="manifold")
    a = trimesh.boolean.difference([center, permitted], engine="manifold")
    b = trimesh.boolean.difference([baseline, permitted], engine="manifold")
    difference = symmetric_volume(a, b)
    require(difference < EPS_VOLUME,
            f"Parameter changed center outside antenna/BNC openings: {difference} mm³")
    return {"difference_outside_opening_regions_mm3": difference}


def fixed_winder_checks(winder, baseline, seat):
    # The central tie brace and dry docking base lie inside the fixed |X|<=44
    # core. Growing wings must not stretch the interface or the captive tie.
    core = bounds_mesh([-43.5, -20, -0.02], [43.5, 5, 5.001])
    a = trimesh.boolean.intersection([winder, core], engine="manifold")
    b = trimesh.boolean.intersection([baseline, core], engine="manifold")
    core_difference = symmetric_volume(a, b)
    require(core_difference < EPS_VOLUME,
            f"Winder central brace/dry base changed: {core_difference} mm³")
    # The standoff changes shoulder length, but the heads and smooth guide
    # retain their local geometry relative to the seating plane.
    tip_regions = [bounds_mesh([x - 4.1, -15.1, 0], [x + 4.1, -6.9, 6.05])
                   for x in [-36, 36]]
    tip_regions.append(bounds_mesh([17.5, -11, 0], [22.5, -6, 7.05]))
    tips = trimesh.boolean.union(tip_regions, engine="manifold")
    a = trimesh.boolean.intersection([translated(winder, [0, 0, -seat]), tips],
                                     engine="manifold")
    b = trimesh.boolean.intersection([translated(baseline, [0, 0, -seat_height(DEFAULTS)]), tips],
                                     engine="manifold")
    tip_difference = symmetric_volume(a, b)
    require(tip_difference < EPS_VOLUME,
            f"Dock heads/guide changed relative to seating plane: {tip_difference} mm³")
    return {"central_tie_brace_and_dry_base_difference_mm3": core_difference,
            "heads_and_guide_difference_at_seat_mm3": tip_difference}


def layout_checks(layout, center, winder):
    components = layout.split(only_watertight=False)
    expected_volumes = sorted([float(center.volume), float(winder.volume), float(winder.volume)])
    actual_volumes = sorted(float(component.volume) for component in components)
    require(len(components) == 3, "Variant layout does not contain three separate parts")
    require(np.max(np.abs(np.asarray(expected_volumes) - actual_volumes)) < 0.02,
            "Layout parts do not match the separate center and two winders")
    overlaps = [intersection_volume(components[a], components[b])
                for a, b in [(0, 1), (0, 2), (1, 2)]]
    require(max(overlaps) < EPS_VOLUME, "Variant print layout parts overlap")
    return {"component_volumes_mm3": actual_volumes,
            "pair_intersections_mm3": overlaps,
            "bed_footprint_mm": layout.extents[:2].tolist()}


def seated_and_envelope_checks(center, winder, envelopes, parameters):
    face = parameters["wire_face_bulge"] or (8 if parameters["preset"] == "80m" else 5)
    seat = seat_height(parameters)
    expected_yz_bounds = np.asarray([[-16.543564, 0], [parameters["wing_length"], seat + 7]])
    require(np.max(np.abs(winder.bounds[:, 1:] - expected_yz_bounds)) < TOL,
            f"Winder size does not follow requested wing length/seat: {winder.bounds}")
    # The span controls the lower tips; extending the swept upper horns can
    # make overall width larger. Measure both instead of assuming a rectangle.
    lower_tips = sections(winder, 2.5).intersection(
        Polygon([[-200, -3], [200, -3], [200, 0], [-200, 0]]))
    require(abs(lower_tips.bounds[0] + parameters["winding_span"] / 2) < TOL and
            abs(lower_tips.bounds[2] - parameters["winding_span"] / 2) < TOL,
            "Lower outer-tip span does not follow winding_span")
    edge = parameters["wire_edge_bulge"]
    overall_x = max(abs(winder.bounds[0, 0]), abs(winder.bounds[1, 0]))
    expected_bounds = np.asarray([
        [-overall_x - edge, -26 - parameters["wing_length"] - edge, -face],
        [overall_x + edge, 26 + parameters["wing_length"] + edge, 5 + face],
    ])
    require(envelopes.is_watertight and envelopes.is_winding_consistent and envelopes.volume > 0,
            "Wire reserve mesh is invalid")
    require(len(envelopes.split(only_watertight=False)) == 2,
            "Wire reserves must remain two separate volumes")
    require(np.max(np.abs(envelopes.bounds - expected_bounds)) < TOL,
            "Wire reserve does not follow requested winding dimensions")
    expected_volume = (2 * (winder.extents[0] + 2 * edge) *
                       (parameters["wing_length"] + 2 * edge) * (5 + 2 * face))
    require(abs(envelopes.volume - expected_volume) < 0.1,
            "Wire reserve volume does not follow requested winding dimensions")
    placed_center = translated(center, [0, -19.5, seat])
    winders = []
    seated = []
    for row in [-1, 1]:
        placed = winder.copy()
        if row < 0:
            placed.apply_transform(np.diag([-1., -1., 1., 1.]))
        placed.apply_translation([0, row * 26, 0])
        winders.append(placed)
        overlap = intersection_volume(placed, placed_center)
        require(overlap < EPS_VOLUME, f"Variant seated winder row {row} interferes: {overlap}")
        captured = intersection_volume(translated(placed, [0, 0, -1.1]), placed_center)
        require(captured > 0.05, f"Variant row {row} has no positive headed retention")
        seated.append({"row": row, "intersection_mm3": overlap,
                       "capture_after_1p1mm_pull_mm3": captured})
    winder_overlap = intersection_volume(*winders)
    reserve_overlap = intersection_volume(envelopes, placed_center)
    require(winder_overlap < EPS_VOLUME, "Stored winders intersect each other")
    # A compact shoulder is a packing experiment with the SAME wire reserve.
    # Preserve the former height's clearance assertion, and expose a compact
    # reserve collision rather than silently reducing the claimed coil size.
    if parameters["standoff"] >= face + 3:
        require(reserve_overlap < EPS_VOLUME, "Variant reserved wire intersects the center")
    return {"seat_height_mm": seat, "resolved_wire_face_bulge_mm": face,
            "standoff_above_winder_mm": seat - 5,
            "loaded_fit_status": ("clear_in_static_wire_proxy" if reserve_overlap < EPS_VOLUME
                                  else "requires_physical_check"),
            "measured_lower_tip_span_mm": lower_tips.bounds[2] - lower_tips.bounds[0],
            "overall_winder_width_mm": float(winder.extents[0]),
            "wire_reserve_bounds_mm": envelopes.bounds.tolist(),
            "wire_reserve_volume_mm3": float(envelopes.volume),
            "center_to_wire_reserve_mm3": reserve_overlap,
            "winder_to_winder_mm3": winder_overlap, "seated_rows": seated}


def rejected_parameters(directory):
    result = []
    for name, parameters in INVALID.items():
        output = directory / f"invalid-{name}.stl"
        command = ["openscad", "--backend=Manifold", "--hardwarnings"]
        for definition in definitions(parameters, "center"):
            command += ["-D", definition]
        command += ["-o", str(output), str(SCAD)]
        completed = subprocess.run(command, text=True, capture_output=True)
        require("ERROR: Assertion" in completed.stderr,
                f"Invalid settings were not rejected by an assertion: {name}\n{completed.stderr}")
        require(not output.exists() or output.stat().st_size == 0,
                f"Invalid settings produced an STL: {name}")
        result.append({"case": name, "parameters": parameters,
                       "assertion": next(line for line in completed.stderr.splitlines()
                                         if "ERROR: Assertion" in line)})
    return result


def customizer_checks(directory):
    output = directory / "customizer.param"
    completed = subprocess.run(["openscad", "--hardwarnings", "-o", str(output), str(SCAD)],
                               text=True, capture_output=True)
    require(completed.returncode == 0 and output.exists() and
            "ERROR:" not in completed.stderr and "WARNING:" not in completed.stderr,
            f"Customizer export failed: {completed.stderr}")
    parameters = json.loads(output.read_text())["parameters"]
    actual = {parameter["name"]: parameter for parameter in parameters}
    expected = {"part": "print_layout", "show_wire": False, **DEFAULTS}
    require(set(actual) == set(expected),
            f"Unexpected exposed Customizer controls: {sorted(set(actual) ^ set(expected))}")
    for name, value in expected.items():
        require(actual[name]["initial"] == value, f"Wrong Customizer default for {name}")
    ranges = {
        "wing_length": [37.5, 60], "winding_span": [140, 200],
        "wire_edge_bulge": [2, 5], "standoff": [2.5, 25],
        "wire_hole_inner_x": [27, 30], "wire_hole_pitch": [4, 6.5],
        "wire_hole_d": [2.6, 3.6], "wire_chamfer": [0, 0.6],
        "terminal_hole_d": [3.1, 3.6], "hang_hole_d": [4, 6],
        "bnc_hole_d": [9.7, 10.2],
    }
    for name, limits in ranges.items():
        require([actual[name]["min"], actual[name]["max"]] == limits,
                f"Customizer range differs from tested settings for {name}")
    face_options = [option["value"] for option in actual["wire_face_bulge"]["options"]]
    require(face_options == [0, *range(2, 13)], "Missing preset or explicit face-buildup options")
    return {"exposed_controls": len(parameters), "parameters": parameters,
            "snap_engineering_controls_hidden": True}


def run(directory: Path):
    directory = Path(directory) / "parameter-variants"
    directory.mkdir(parents=True, exist_ok=True)
    baseline_center = export(directory / "baseline-center.stl", SCAD,
                             definitions({}, "center"))
    baseline_winder = export(directory / "baseline-winder.stl", SCAD,
                             definitions({}, "winder"))
    report = {
        "status": "running",
        "scope": f"{len(VARIANTS)} coordinated endpoint/combined configurations, measured in exported CAD",
        "limits": [
            "Sampled parameter configurations, not every combination in the advertised ranges",
            "Seated capture and static wire-reserve measurements; full sequential release proof covers default presets separately",
            "Compact shoulder settings keep the same coil reserves; measured reserve overlap is a fit caveat, not a dry-mechanism pass",
            "No wire capacity, printed strength, durability, or human-operation rating",
        ],
        "variants": {},
    }
    for name, changes in VARIANTS.items():
        print(f"Checking parameter variant {name}", flush=True)
        parameters = {**DEFAULTS, **changes}
        meshes = {part: export(directory / f"{name}-{part}.stl", SCAD,
                               definitions(changes, part))
                  for part in ["center", "winder", "print_layout", "fit_coupon", "wire_envelopes"]}
        center, winder = meshes["center"], meshes["winder"]
        checks = {
            "parameters": parameters,
            "meshes": {part: mesh_report(meshes[part], count)
                       for part, count in [("center", 1), ("winder", 1),
                                           ("print_layout", 3), ("fit_coupon", 2)]},
            "plate_holes": plate_hole_checks(center, baseline_center, parameters),
            "bnc_cutout": bnc_checks(center, parameters["bnc_hole_d"]),
            "fixed_center_geometry": fixed_center_checks(center, baseline_center),
            "print_layout": layout_checks(meshes["print_layout"], center, winder),
            "storage_clearance": seated_and_envelope_checks(
                center, winder, meshes["wire_envelopes"], parameters),
        }
        checks["fixed_winder_geometry"] = fixed_winder_checks(
            winder, baseline_winder, checks["storage_clearance"]["seat_height_mm"])
        report["variants"][name] = checks
    report["rejected_invalid_settings"] = rejected_parameters(directory)
    report["customizer"] = customizer_checks(directory)
    report["status"] = ("passed_with_fit_caveats" if any(
        checks["storage_clearance"]["loaded_fit_status"] == "requires_physical_check"
        for checks in report["variants"].values()) else "passed")
    return report
