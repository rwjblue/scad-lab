#!/usr/bin/env python3
"""Export and measure the four-catch pinch carrier. CAD evidence, not a print test."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

import numpy as np
import trimesh
from shapely.geometry import box

from validation_helpers import (HERE, ROOT, ORIGINAL, TOL, require, export, mesh_report,
                      volume, intersection_volume, translated, bounds_mesh,
                      sections, check_center_holes, check_bnc_cutout)
from parameter_validation import (DEFAULTS, seat_height,
                                  run as check_parameter_variants)
from review.retention_audit import run as check_retention_margin

SCAD = HERE / "modular_dipole.scad"
MOCKUPS = HERE / "mockups.scad"
OFFSET = 26
EPS_VOLUME = 0.001
EXPORT_CACHE = {}
DOCS = HERE / "review"
PRINT_FILES = ["center.stl", "winder.stl", "print_layout.stl",
               "fit_coupon.stl", "retention_coupon.stl", "bnc_fit_coupon.stl"]


@lru_cache(maxsize=1)
def _mechanism_configuration(source_sha256):
    """Evaluate dimensions in OpenSCAD so passage and motion checks follow the CAD."""
    expressions = {name: name for name in [
        "snap_release", "snap_stop", "snap_head_d", "snap_throat_d", "snap_throat_x_d",
        "throat_flat", "head_under_z", "head_top_z", "dock_x", "dock_y",
        "center_y_offset", "center_plate_t", "shoulder_d", "guide_d", "guide_clearance", "guide_x", "guide_y",
    ]}
    expressions["pad_y"] = "tab_outer_y-paddle_inset"
    with tempfile.TemporaryDirectory(prefix="dipole-mechanism-config-") as directory:
        source = Path(directory) / "configuration.scad"
        source.write_text(f"include <{SCAD}>\n"
                          f'echo(["VALIDATOR_CONFIG",{",".join(expressions.values())}]);\n')
        completed = subprocess.run([
            "openscad", "--backend=Manifold", "--hardwarnings", "-D", 'part="center"',
            "-o", str(source.with_suffix(".csg")), str(source),
        ], capture_output=True, text=True)
        require(completed.returncode == 0 and "ERROR:" not in completed.stderr and
                "WARNING:" not in completed.stderr, completed.stderr)
        value = next((line[6:] for line in completed.stderr.splitlines()
                      if line.startswith('ECHO: ["VALIDATOR_CONFIG",')), None)
        require(value is not None, "Missing validator configuration echo")
        require(hashlib.sha256(SCAD.read_bytes()).hexdigest() == source_sha256,
                "CAD changed while reading mechanism configuration")
        return dict(zip(expressions, json.loads(value)[1:]))


def mechanism_configuration():
    return _mechanism_configuration(hashlib.sha256(SCAD.read_bytes()).hexdigest())


def expression_export(directory, name, expression, preset="40m", source=SCAD, definitions=()):
    # The local carrier and its tongues are identical for both winding-space
    # presets. Cache their repeated poses; the two wire reserves still receive
    # separate loaded-fit checks. Hardware, ties and winders keep preset keys.
    carrier_only = source == SCAD and (
        expression.startswith("dock_center(") or "snap_tab(" in expression)
    cache_preset = "shared-center" if carrier_only else preset
    key = (str(source), hashlib.sha256(source.read_bytes()).hexdigest(), expression, cache_preset, tuple(definitions))
    if key in EXPORT_CACHE:
        return EXPORT_CACHE[key].copy()
    wrapper = directory / f"{name}.scad"
    wrapper.write_text(f'use <{source}>\n$fn=96;\n{expression}\n')
    mesh = export(directory / f"{name}.stl", wrapper, [f'preset="{preset}"', *definitions])
    EXPORT_CACHE[key] = mesh.copy()
    return mesh


def placed_winder(mesh, row):
    placed = mesh.copy()
    if row < 0:
        placed.apply_transform(np.diag([-1., -1., 1., 1.]))
    placed.apply_translation([0, row * OFFSET, 0])
    return placed


def clear(a, b, description):
    measured = intersection_volume(a, b)
    require(measured < EPS_VOLUME, f"{description}: {measured:.6f} mm³")
    return measured


def wire_reserve(row, bulge):
    limits = [-68.5, -21] if row < 0 else [21, 68.5]
    return bounds_mesh([-75, limits[0], -bulge], [75, limits[1], 5 + bulge])


def original_geometry(original, center):
    cfg = mechanism_configuration()
    removed = trimesh.boolean.difference([original, center], engine="manifold")
    # Only four new D openings and two guide bores may subtract plate material.
    # Preserve the existing 0.001 mm aperture allowance as the passage grows.
    radius_y = cfg["snap_throat_d"] / 2 + 0.001
    radius_x = cfg["snap_throat_x_d"] / 2 + 0.001
    thickness = cfg["center_plate_t"]
    tools = []
    for end in [-1, 1]:
        for row in [-1, 1]:
            circle = trimesh.creation.cylinder(radius=radius_y, height=thickness + 0.04, sections=192)
            circle.apply_scale([radius_x / radius_y, 1, 1])
            circle.apply_translation([0, 0, thickness / 2])
            # Upper flat faces outward (+Y), opposite the inward-moving tongue.
            clip = bounds_mesh([-radius_x - 0.1, -radius_y - 0.1, -0.03],
                               [radius_x + 0.1, cfg["throat_flat"] + 0.001, thickness + 0.03])
            opening = trimesh.boolean.intersection([circle, clip], engine="manifold")
            if row < 0:
                opening.apply_transform(np.diag([-1., -1., 1., 1.]))
            opening.apply_translation([end * cfg["dock_x"],
                                       -cfg["center_y_offset"] + row * cfg["dock_y"], 0])
            tools.append(opening)
    for row in [-1, 1]:
        guide = trimesh.creation.cylinder(
            radius=cfg["guide_d"] / 2 + cfg["guide_clearance"] + 0.001,
            height=thickness + 0.04, sections=192)
        guide.apply_translation([row * cfg["guide_x"],
                                 -cfg["center_y_offset"] + row * cfg["guide_y"], thickness / 2])
        tools.append(guide)
    allowed = trimesh.boolean.union(tools, engine="manifold")
    unexpected = volume(trimesh.boolean.difference([removed, allowed], engine="manifold"))
    require(unexpected < EPS_VOLUME, f"Original center cut outside new sockets: {unexpected}")
    # The actual inherited panel occupies Y=0..3. Expanded side rails
    # project in front of its extreme X edges; that is outside the panel.
    panel = bounds_mesh([-13, 0, -0.02], [13, 3, 24])
    old = trimesh.boolean.intersection([original, panel], engine="manifold")
    new = trimesh.boolean.intersection([center, panel], engine="manifold")
    difference = sum(volume(trimesh.boolean.difference(pair, engine="manifold"))
                     for pair in [[old, new], [new, old]])
    require(difference < EPS_VOLUME, "Inherited BNC panel changed")
    return {"unexpected_removed_volume_mm3": unexpected,
            "removed_for_docking_sockets_mm3": volume(removed),
            "bnc_panel_symmetric_difference_mm3": difference,
            "original_holes": check_center_holes(original, center),
            "bnc_cutout": check_bnc_cutout(center)}


def capture_and_release(center, released, winders):
    result = []
    for row, winder in zip([-1, 1], winders):
        clear(winder, center, f"Seated row {row}")
        captured = intersection_volume(translated(winder, [0, 0, -1.1]), center)
        require(captured > 0.05, f"Row {row} has no positive capture")
        path = []
        for drop in [0, 0.25, 0.5, 0.8, 1.1, 2, 3, 4, 5, 6, 7, 12, 30]:
            v = clear(translated(winder, [0, 0, -drop]), released,
                      f"Released straight withdrawal, row {row}, drop {drop}")
            path.append({"drop_mm": drop, "intersection_mm3": v})
        result.append({"row": row, "locked_intersection_after_1p1mm_pull_mm3": captured,
                       "both_ends_pinched_straight_path": path})
    return result


def load_proxies(directory, preset, center, reserves, seat, *, standoff, require_clearance):
    definitions = [f"standoff={standoff}"]
    hardware = expression_export(directory, f"hardware-{preset}-{standoff}", "hardware();", preset,
                                 HERE / "hardware_mockups.scad", definitions)
    ties = expression_export(directory, f"ties-{preset}",
                             "for(r=[-1,1]) winder_strap(r);", preset, MOCKUPS, definitions)
    tails = expression_export(directory, f"tails-{preset}-{standoff}", "service_tails();", preset,
                              MOCKUPS, definitions)
    overlaps = {
        "center_to_wire_reserve_mm3": [intersection_volume(center, reserve) for reserve in reserves],
        "tie_to_center_mm3": intersection_volume(ties, center),
        "tie_to_hardware_mm3": intersection_volume(ties, hardware),
        "hardware_to_wire_reserve_mm3": [intersection_volume(hardware, reserve) for reserve in reserves],
        "tail_to_center_mm3": intersection_volume(tails, center),
    }
    values = [v for value in overlaps.values() for v in (value if isinstance(value, list) else [value])]
    max_overlap = max(values)
    # This is the former global height reserve, not a local clearance measure:
    # tie and plate can share Z while occupying different XY positions.
    height_reserve = float(seat - ties.bounds[1, 2])
    if require_clearance:
        require(max_overlap < EPS_VOLUME,
                f"Standoff {standoff} mm loaded reference proxy intersects: {overlaps}")
        require(height_reserve >= 1 - TOL, "Reference has less than 1 mm above tie proxy")
    results = {
        **overlaps, "maximum_intersection_mm3": max_overlap,
        "standoff_mm": standoff,
        "loaded_fit_status": ("clear_in_static_proxies" if max_overlap < EPS_VOLUME and height_reserve >= 1 - TOL
                              else "requires_physical_check"),
        "remaining_gap_above_tie_mm": height_reserve,
        "height_reserve_interpretation": "Global tie-top versus seat-plane offset; a negative value alone does not prove an XY-local collision",
        "evidence_limit": "Schematic connector and tie dimensions; flexible tails are a static route, not a dynamics model",
    }
    return results, hardware, ties


def loaded_motion_measurements(carrier, hardware, winders, reserves, ties, reference, peaks):
    """Measure compact fit and preserve strict original-height proxy checks.

    The two carriers follow the same relative peel/level path. Translate the
    compact poses by the shoulder-height difference to obtain the original
    reference, whose winders are independently exported at the former height.
    """
    for label, moved_center, moved_hardware, fixed_winders, fixed_ties, strict in [
        ("current", carrier, hardware, winders, ties, False),
        ("original_height_reference",
         translated(carrier, [0, 0, reference["height_delta_mm"]]),
         translated(hardware, [0, 0, reference["height_delta_mm"]]),
         reference["winders"], reference["ties"], True),
    ]:
        pairs = [("hardware_to_winder_mm3", moved_hardware, w) for w in fixed_winders]
        pairs += [(name, moving, reserve) for reserve in reserves for name, moving in [
            ("center_to_wire_reserve_mm3", moved_center),
            ("hardware_to_wire_reserve_mm3", moved_hardware)]]
        pairs += [("center_to_tie_mm3", moved_center, fixed_ties),
                  ("hardware_to_tie_mm3", moved_hardware, fixed_ties)]
        for name, a, b in pairs:
            measured = intersection_volume(a, b)
            peaks[label][name] = max(peaks[label].get(name, 0), measured)
            if strict:
                require(measured < EPS_VOLUME,
                        f"Original-height loaded motion {name}: {measured:.6f} mm³")


def finger_clearance_report(preset, output, *, standoff=None, require_clearance=False):
    cfg = mechanism_configuration()
    command = [sys.executable, str(DOCS / "hand_clearance.py"),
               "--pad-y", str(cfg["pad_y"]), "--pad-stroke", str(cfg["snap_release"]),
               "--winder-offset", str(OFFSET), "--preset", preset, "--output", str(output)]
    if standoff is not None:
        command += ["--standoff", str(standoff)]
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL)
    hand = json.loads(output.read_text())
    raised = hand["contact_modes"]["raised_face"]
    tail_gap = min(x["closest_wire"]["clearance_mm"] for x in raised)
    coil_gap = min(c["clearance_mm"] for x in raised for c in x["wire_reserve_clearances"])
    if require_clearance:
        require(tail_gap > 0 and coil_gap > 0,
                "Original-height raised-face fingertip proxy intersects wire")
    return {
        "assumptions": hand["assumptions"], "minimum_tail_gap_mm": tail_gap,
        "minimum_wire_reserve_gap_mm": coil_gap,
        "loaded_fit_status": ("clear_in_finger_proxy" if tail_gap > 0 and coil_gap > 0
                              else "requires_physical_check"),
        "evidence_limit": hand["evidence"],
    }


def lateral_capture(center, states, winder, row, seat):
    """Probe a broad grid, accepting only poses clear in the actual seated CAD.

    This includes the enlarged X play left by removing the tight plain locator.
    Samples are evidence of capture, not an exhaustive configuration-space proof.
    """
    import manifold3d
    cfg = mechanism_configuration()

    def solid(mesh):
        result = manifold3d.Manifold(manifold3d.Mesh(
            np.asarray(mesh.vertices, dtype=np.float32),
            np.asarray(mesh.faces, dtype=np.uint32)))
        require(result.status() == manifold3d.Error.NoError,
                "Invalid input solid during lateral capture")
        return result

    def overlap(a, b):
        result = a ^ b
        require(result.status() == manifold3d.Error.NoError,
                "Lateral capture Boolean failed")
        return abs(float(result.volume()))

    centered = solid(center)
    state_solids = {key: solid(mesh) for key, mesh in states.items()}
    winder_solid = solid(winder)
    angles = np.linspace(0, 5.6, 113)
    # Carrier motion and retained-head crops are independent of the candidate.
    # Keep the original crop/conversion once, rather than repeating it per pose.
    end_cache = {}
    head_crop_radius = cfg["snap_head_d"] / 2 + 0.1
    for end, key in [(-1, "left"), (1, "right")]:
        head_x, head_y = -end * cfg["dock_x"], row * cfg["dock_y"]
        retained_head = solid(trimesh.boolean.intersection([
            winder, bounds_mesh([head_x - head_crop_radius, head_y - head_crop_radius,
                                 seat + cfg["head_under_z"]],
                                [head_x + head_crop_radius, head_y + head_crop_radius,
                                 seat + cfg["head_top_z"] + 0.01])], engine="manifold"))
        carriers = []
        for angle in angles:
            radians = np.radians(angle)
            lift = cfg["shoulder_d"] / 2 * np.tan(radians) + 2 * (1 / np.cos(radians) - 1) + 0.04
            matrix = trimesh.transformations.rotation_matrix(
                -end * radians, [0, 1, 0], [-end * 36, 0, seat + 2])
            matrix[:3, 3] += [0, 0, lift]
            carrier = state_solids[key].transform(matrix[:3, :])
            carriers.append((carrier, carrier.translate([0, 0, 1.1])))
        end_cache[key] = {"head": retained_head, "carriers": carriers,
                          "centered_samples": {},
                          "returned": centered.transform(matrix[:3, :])}

    candidates = []
    for dx in [-1.3, -0.6, -0.3, -0.2, 0, 0.2, 0.3, 0.6, 1.3]:
        for dy in [-0.3, -0.2, -0.15, 0, 0.15, 0.2, 0.3]:
            candidates.append(({"translation_mm": [dx, row * dy]},
                               winder_solid.translate([dx, row * dy, 0])))
    for angle in [-0.4, -0.3, -0.2, -0.1, 0.1, 0.2, 0.3, 0.4]:
        matrix = trimesh.transformations.rotation_matrix(
            np.radians(angle), [0, 0, 1], [0, row * 15, 0])
        pose = winder_solid.transform(matrix[:3, :])
        candidates.append(({"rotation_about_midpoint_deg": angle}, pose))
    accepted, excluded = [], []
    for description, pose in candidates:
        at_rest = overlap(pose, centered)
        if at_rest > 0.0001:
            excluded.append({**description, "seated_intersection_mm3": at_rest})
            continue
        pull = overlap(pose.translate([0, 0, -1.1]), centered)
        require(pull > 0.05, f"Capture fails during lateral play: {description}")
        path = [overlap(pose.translate([0, 0, -d]), state_solids["both"])
                for d in [0, 0.8, 1.1, 2, 4, 6, 7]]
        # The supported use is one end at a time. A simultaneous four-catch,
        # perfectly vertical withdrawal is a separate path, recorded here
        # without claiming it as the operating procedure.
        peel_paths = {}
        for end, key in [(-1, "left"), (1, "right")]:
            initial = overlap(state_solids[key], pose)
            require(initial < EPS_VOLUME,
                    f"Initial end squeeze during admissible seated play: {initial:.6f} mm³")
            cached = end_cache[key]
            measurements, capture_samples = [], []
            for index, angle in enumerate(angles):
                # Contact at an extreme guide clearance can require a tiny
                # lateral adjustment. Keep the actual initial pose, then test
                # a continuous path to centered alignment in the first degree.
                # This proves space for that adjustment, not friction/forces.
                remaining = 1 - min(float(angle), 1.0)
                carrier, pulled_carrier = cached["carriers"][index]
                # Every candidate follows exactly the same centered path
                # after one degree. Reuse those identical Boolean results;
                # retain all 113 samples in each candidate's extrema/checks.
                if remaining == 0:
                    if index not in cached["centered_samples"]:
                        cached["centered_samples"][index] = (
                            overlap(carrier, winder_solid),
                            overlap(pulled_carrier, cached["head"]))
                    contact, captured = cached["centered_samples"][index]
                    measurements.append(contact)
                    capture_samples.append(captured)
                    continue
                transform = np.eye(4)
                if "translation_mm" in description:
                    transform[:2, 3] = np.asarray(description["translation_mm"]) * remaining
                else:
                    transform = trimesh.transformations.rotation_matrix(
                        np.radians(description["rotation_about_midpoint_deg"] * remaining),
                        [0, 0, 1], [0, row * 15, 0])
                adjusted = winder_solid.transform(transform[:3, :])
                head = cached["head"].transform(transform[:3, :])
                measurements.append(overlap(carrier, adjusted))
                capture_samples.append(overlap(pulled_carrier, head))
            require(max(measurements) < EPS_VOLUME,
                    f"Continuous {key}-first alignment/peel jams from {description}: {max(measurements)}")
            require(min(capture_samples) > 0.001,
                    f"Opposite head loses capture during alignment/peel from {description}")
            if "returned_overlap" not in cached:
                cached["returned_overlap"] = overlap(cached["returned"], winder_solid)
            require(cached["returned_overlap"] < EPS_VOLUME,
                    "Returned first-end tabs above heads after alignment: "
                    f"{cached['returned_overlap']:.6f} mm³")
            peel_paths[key] = {"maximum_intersection_mm3": max(measurements),
                               "minimum_opposite_head_capture_mm3": min(capture_samples)}
        accepted.append({**description, "pull_intersection_mm3": pull,
                         "unused_four_catch_vertical_path_max_intersection_mm3": max(path),
                         "actual_first_end_peel_max_intersections_mm3": peel_paths})
    require(len(accepted) >= 7, "Insufficient admissible lateral capture samples")
    return {"admissible_poses": accepted, "excluded_colliding_poses": excluded,
            "alignment_path": "Each admitted initial translation/yaw relaxes continuously to centered over the first 1 degree of peel",
            "angle_step_deg": 0.05,
            "evidence_limit": "Feasible continuous clearance path; friction, automatic centering, print tolerances and one-hand forces are not simulated"}


def peel_pose(mesh, side, angle, seat, padding=0.04):
    """Independent rigid transform; keeps opposite shoulder rim below the plate.

    At padding=0 the configured shoulder's outside tangent is an actual
    support contact with the inclined plate underside, not a hover pose.
    """
    cfg = mechanism_configuration()
    radians = np.radians(angle)
    lift = cfg["shoulder_d"] / 2 * np.tan(radians) + 2 * (1 / np.cos(radians) - 1) + padding
    matrix = trimesh.transformations.rotation_matrix(
        -side * radians, [0, 1, 0], [-side * 36, 0, seat + 2])
    matrix[:3, 3] += [0, 0, lift]
    result = mesh.copy()
    result.apply_transform(matrix)
    return result


def flexure_clearance(directory, preset, center):
    cfg = mechanism_configuration()
    original_tabs = expression_export(directory, f"tabs-{preset}-0",
                                      "for(s=[-1,1],r=[-1,1]) snap_tab(s,r,0);", preset)
    fixed = trimesh.boolean.difference([center, original_tabs], engine="manifold")
    wings = trimesh.boolean.union([
        bounds_mesh([-60, -10, -1], [-14.6, 60, 11]),
        bounds_mesh([14.6, -10, -1], [60, 60, 11])], engine="manifold")
    samples = []
    cases = [(finger, float(travel)) for finger in [41, 46, 51]
             for travel in [*np.linspace(0, cfg["snap_release"], 9), cfg["snap_stop"]]]
    def build(case):
        finger, travel = case
        return expression_export(directory, f"tabs-{preset}-{finger}-{travel:.3f}",
                                 f"for(s=[-1,1],r=[-1,1]) snap_tab(s,r,{travel});", preset,
                                 definitions=[f"finger_x={finger}"])
    with ThreadPoolExecutor(max_workers=3) as pool:
        meshes = list(pool.map(build, cases))
    for (finger, travel), tabs in zip(cases, meshes):
        mesh_report(tabs, 4)
        free = trimesh.boolean.intersection([tabs, wings], engine="manifold")
        collision = clear(free, fixed, "Free flexures collide with fixed carrier")
        samples.append({"finger_load_x_mm": finger, "paddle_travel_mm": travel,
                        "fixed_intersection_mm3": collision})
    return {"outside_root_fillet_abs_x_mm": 14.6, "samples": samples}


def sequential_release(directory, preset, centered, states, winders, reserves, hardware, ties, seat, reference):
    """Both end orders: release, peel, return, settle on heads, release other end.

    Contact is found numerically from exported solids. Tests do not infer that
    a floating, noncolliding pose will remain open under gravity.
    """
    cfg = mechanism_configuration()
    release = cfg["snap_release"]
    results = []
    for side, key, other_key in [(1, "right", "left"), (-1, "left", "right")]:
        print(f"Checking {preset} {key}-first peel and parking", flush=True)
        loaded_peaks = {"current": {}, "original_height_reference": {}}
        # Test each stud's capture separately at both lateral ends.
        end_regions = {end: bounds_mesh([end * 36 - 5, -23, seat - 0.1],
                                       [end * 36 + 5, 23, seat + 7]) for end in [-1, 1]}
        studs = {(end, row): trimesh.boolean.intersection([winder, end_regions[end]], engine="manifold")
                 for row, winder in zip([-1, 1], winders) for end in [-1, 1]}
        capture = {}
        for end in [-1, 1]:
            for row in [-1, 1]:
                moved = translated(studs[(end, row)], [0, 0, -1.1])
                locked_v = intersection_volume(moved, centered)
                require(locked_v > 0.05, f"Stud {end,row} is not individually captured")
                one_end_v = intersection_volume(moved, states[key])
                if end == side:
                    require(one_end_v < EPS_VOLUME, "Pinch does not free BOTH studs at selected end")
                else:
                    require(one_end_v > 0.05, "Pinching one end frees the other end")
                capture[f"{end},{row}"] = {"locked_mm3": locked_v, "one_end_pinched_mm3": one_end_v}
        peak = 0.0
        angles = np.linspace(0, 5.6, 57)
        for angle in angles:
            carrier = peel_pose(states[key], side, float(angle), seat)
            metal = peel_pose(hardware, side, float(angle), seat)
            for winder in winders:
                peak = max(peak, clear(carrier, winder, f"{key} peel {angle:.2f} deg"))
            loaded_motion_measurements(carrier, metal, winders, reserves, ties, reference, loaded_peaks)
        # Return the squeezed pair while held above its heads. This checks all
        # intermediate tongue poses, not merely the open and closed endpoints.
        travels = np.linspace(release, 0, 9)
        def carrier_for_first(travel):
            values = [0, float(travel)] if side > 0 else [float(travel), 0]
            return expression_export(directory, f"return-{preset}-{side}-{travel:.3f}",
                                     f"dock_center(release={values});", preset)
        with ThreadPoolExecutor(max_workers=3) as pool:
            intermediate = list(pool.map(carrier_for_first, travels))
        for travel, local in zip(travels, intermediate):
            mesh_report(local)
            local_placed = translated(local, [0, -19.5, seat])
            for w in winders:
                clear(local_placed, w, "Initial first-end squeeze against seated studs")
            carrier = peel_pose(local_placed, side, 5.6, seat)
            for w in winders:
                clear(carrier, w, "Returning first-end tongues above stud tops")
        # Locate the first head-top contact while lowering the returned tabs.
        # The zero-padding transform simultaneously rests on opposite shoulders.
        released_end_studs = [studs[(side, row)] for row in [-1, 1]]
        def first_end_interference(angle):
            carrier = peel_pose(centered, side, angle, seat, padding=0)
            return sum(intersection_volume(carrier, stud) for stud in released_end_studs)
        low, high = 3.5, 5.6
        require(first_end_interference(low) > 0.05, "No first-side parking stop at lower angle")
        require(first_end_interference(high) < EPS_VOLUME, "Peel does not clear first-side heads")
        for _ in range(26):
            middle = (low + high) / 2
            if first_end_interference(middle) > 1e-7:
                low = middle
            else:
                high = middle
        parked_angle = high + 0.0001
        parked = peel_pose(centered, side, parked_angle, seat, padding=0)
        for angle in np.linspace(5.6, parked_angle, 20):
            carrier = peel_pose(centered, side, float(angle), seat, padding=0)
            for w in winders:
                clear(carrier, w, "Settling first end onto head tops")
        closure_block = first_end_interference(parked_angle - 0.05)
        require(closure_block > 0.001, "First end can reclose instead of parking")
        # Confirm actual tangent support at BOTH ends. At a tilted edge, the
        # initial intersection grows from a line contact, so an arbitrary
        # volume minimum at only 0.02 mm can reject real contact. Record the
        # growth over four tiny virtual penetrations and require measurable
        # blocking by 0.05 mm, without relaxing any clearance tolerance.
        supports = {}
        for end in [-1, 1]:
            for row in [-1, 1]:
                samples = []
                for down in [0.005, 0.01, 0.02, 0.05]:
                    lowered = translated(parked, [0, 0, -down])
                    contact = intersection_volume(lowered, studs[(end, row)])
                    samples.append({"down_mm": down, "blocking_mm3": contact})
                values = [sample["blocking_mm3"] for sample in samples]
                require(values[0] > 1e-6 and values[-1] > 0.001,
                        f"No actual parked support at stud {end,row}: {values}")
                require(all(b > a for a, b in zip(values, values[1:])),
                        f"Support contact does not grow with closure at stud {end,row}")
                supports[f"{end},{row}"] = samples
        still_captured = sum(intersection_volume(translated(parked, [0, 0, 1.1]), studs[(-side, row)])
                             for row in [-1, 1])
        require(still_captured > 0.05, "Opposite end lost capture during first-end parking")
        # Hand changes ends with first pair closed. Then release only other pair.
        travels = np.linspace(0, release, 9)
        def carrier_for_second(travel):
            values = [float(travel), 0] if side > 0 else [0, float(travel)]
            return expression_export(directory, f"second-{preset}-{side}-{travel:.3f}",
                                     f"dock_center(release={values});", preset)
        with ThreadPoolExecutor(max_workers=3) as pool:
            intermediate = list(pool.map(carrier_for_second, travels))
        for travel, local in zip(travels, intermediate):
            mesh_report(local)
            carrier = peel_pose(translated(local, [0, -19.5, seat]), side, parked_angle, seat, padding=0)
            for w in winders:
                clear(carrier, w, "Squeezing second end with first end parked")
        freed = peel_pose(states[other_key], side, parked_angle, seat, padding=0)
        parked_metal = peel_pose(hardware, side, parked_angle, seat, padding=0)
        # Raise the newly released end until the carrier is level, pivoting
        # about the first end's head-top region. A purely vertical pull while
        # still tilted can jam a head against the passage at allowed offsets.
        leveling_peak = 0.0
        for angle in np.linspace(0, parked_angle, 25):
            rotation = trimesh.transformations.rotation_matrix(
                side * np.radians(angle), [0, 1, 0],
                [side * cfg["dock_x"], 0, seat + cfg["head_top_z"]])
            leveled = freed.copy()
            leveled.apply_transform(rotation)
            metal_leveled = parked_metal.copy()
            metal_leveled.apply_transform(rotation)
            for w in winders:
                leveling_peak = max(leveling_peak, clear(leveled, w, "Leveling the second end"))
            loaded_motion_measurements(leveled, metal_leveled, winders, reserves, ties, reference, loaded_peaks)
        exit_peak = 0.0
        for lift in np.linspace(0, 12, 49):
            moving = translated(leveled, [0, 0, float(lift)])
            metal = translated(metal_leveled, [0, 0, float(lift)])
            for w in winders:
                exit_peak = max(exit_peak, clear(moving, w, "Second-end exit"))
            loaded_motion_measurements(moving, metal, winders, reserves, ties, reference, loaded_peaks)
        results.append({"first_end": key, "individual_stud_capture": capture,
                        "peel_angle_samples_deg": angles.tolist(), "peel_max_intersection_mm3": peak,
                        "parked_angle_deg": parked_angle,
                        "park_support_contact_growth": supports,
                        "reclosing_0p05deg_blocked_mm3": closure_block,
                        "opposite_end_capture_after_1p1mm_lift_mm3": still_captured,
                        "second_end_leveling_max_intersection_mm3": leveling_peak,
                        "leveling_pivot_mm": [side * cfg["dock_x"], 0, seat + cfg["head_top_z"]],
                        "leveling_rotation_samples_deg": np.linspace(0, parked_angle, 25).tolist(),
                        "second_end_exit_max_intersection_mm3": exit_peak,
                        "loaded_motion_peak_intersections_mm3": loaded_peaks,
                        "loaded_fit_status": ("clear_in_sampled_motion_proxies"
                                              if max(loaded_peaks["current"].values()) < EPS_VOLUME
                                              else "requires_physical_check"),
                        "second_end_exit_samples_mm": np.linspace(0, 12, 49).tolist()})
    return {"status": "passed", "dry_mechanism_status": "passed", "orders": results,
            "loaded_fit_status": ("requires_physical_check" if any(
                result["loaded_fit_status"] == "requires_physical_check" for result in results)
                else "clear_in_sampled_motion_proxies"),
            "original_height_loaded_reference_status": "passed",
            "evidence_limit": "Dry mechanism uses strict collision assertions. Compact loaded proxies are measured separately; original-height loaded reference retains strict assertions. No physical hand, force or fatigue test"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path)
    args = parser.parse_args()
    input_paths = [SCAD, MOCKUPS, HERE / "hardware_mockups.scad", HERE / "native_profile.scad",
                   HERE / "winder_profile.scad", HERE / "parameter_validation.py",
                   DOCS / "hand_clearance.py", DOCS / "parked_audit.py", DOCS / "retention_audit.py",
                   HERE.parent / "dipole_winder/frame_bevel.scad", ORIGINAL, Path(__file__), HERE / "validation_helpers.py"]
    initial_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in input_paths}
    cfg = mechanism_configuration()
    release = cfg["snap_release"]
    report = {"status": "running", "revision": "retention-r3-standoff-mm-modular-dipole-bnc-10p1",
              "evidence": "Revision 1 printed with comfortable springs but failed retention. Revision 2's larger heads improved retention in the physical print but still pulled free. Revision 3 is CAD-checked only; compact loaded-fit caveats remain separate from dry mechanism checks",
              "mechanism_configuration_mm": cfg,
              "presets": {}}
    with tempfile.TemporaryDirectory(prefix="pinch-dipole-check-") as directory:
        temporary = Path(directory)
        original = export(temporary / "original.stl", ORIGINAL, ['bnc_clearance=0.20'])
        shared_meshes = {}
        for preset, bulge in [("40m", 5), ("80m", 8)]:
            print(f"Checking {preset} meshes and preserved geometry", flush=True)
            params = [f'preset="{preset}"']
            meshes = {}
            for part in ["center", "winder", "print_layout"]:
                output = (HERE / f"{part}.stl" if preset == "40m"
                          else temporary / f"{part}-{preset}.stl")
                meshes[part] = export(output, SCAD, params + [f'part="{part}"'])
            center, winder, plate = (meshes[part] for part in ["center", "winder", "print_layout"])
            checks = {"center": mesh_report(center), "winder": mesh_report(winder),
                      "preserved_geometry": original_geometry(original, center)}
            if preset == "40m":
                shared_meshes = {part: mesh.copy() for part, mesh in meshes.items()}
            else:
                differences = {}
                for part, mesh in meshes.items():
                    baseline = shared_meshes[part]
                    same = sum(volume(trimesh.boolean.difference(pair, engine="manifold"))
                               for pair in [[baseline, mesh], [mesh, baseline]])
                    require(same < EPS_VOLUME,
                            f"Wire presets unexpectedly use different {part} geometry")
                    differences[part] = same
                checks["printed_mesh_symmetric_difference_from_40m_mm3"] = differences
            checks["free_flexure_clearance"] = flexure_clearance(temporary, preset, center)
            seat = seat_height({**DEFAULTS, "preset": preset})
            # Before the compact revision, the seat reserved the preset's face
            # buildup plus a fixed 3 mm allowance. Retain that independent
            # historical reference without coupling the current standoff to wire.
            original_standoff = bulge + 3
            original_seat = seat_height({**DEFAULTS, "standoff": original_standoff})
            checks["standoff"] = {"height_above_winder_mm": DEFAULTS["standoff"],
                                   "seat_above_table_mm": seat,
                                   "original_height_above_winder_mm": original_seat - 5}
            centered = translated(center, [0, -19.5, seat])
            winders = [placed_winder(winder, row) for row in [-1, 1]]
            reserves = [wire_reserve(row, bulge) for row in [-1, 1]]
            clear(*winders, "Winder pair")
            states = {}
            for key, values in [("left", [release, 0]), ("right", [0, release]),
                                ("both", [release, release])]:
                local = expression_export(temporary, f"center-{preset}-{key}",
                                          f"dock_center(release={values});", preset)
                mesh_report(local)
                states[key] = translated(local, [0, -19.5, seat])
                for w in winders:
                    clear(w, states[key], f"{key} squeeze against seated studs")
            checks["capture_and_release"] = capture_and_release(centered, states["both"], winders)
            print(f"Checking {preset} enlarged lateral play", flush=True)
            checks["lateral_capture"] = [lateral_capture(centered, states, w, row, seat)
                                         for row, w in zip([-1, 1], winders)]
            checks["load_proxies"], hardware, ties = load_proxies(
                temporary, preset, centered, reserves, seat,
                standoff=DEFAULTS["standoff"],
                require_clearance=DEFAULTS["standoff"] >= original_standoff)
            reference_centered = translated(center, [0, -19.5, original_seat])
            reference_proxies, reference_hardware, reference_ties = load_proxies(
                temporary, preset, reference_centered, reserves, original_seat,
                standoff=original_standoff, require_clearance=True)
            reference_winder = export(temporary / f"reference-winder-{preset}.stl", SCAD,
                                      params + ['part="winder"', f'standoff={original_standoff}'])
            reference = {"height_delta_mm": original_seat - seat,
                         "winders": [placed_winder(reference_winder, row) for row in [-1, 1]],
                         "ties": reference_ties}
            # Verify that translating attached hardware produces exactly the
            # independently exported reference used by the loaded motion check.
            moved_hardware = translated(hardware, [0, 0, original_seat - seat])
            reference_difference = sum(volume(trimesh.boolean.difference(pair, engine="manifold"))
                                       for pair in [[moved_hardware, reference_hardware],
                                                    [reference_hardware, moved_hardware]])
            require(reference_difference < EPS_VOLUME, "Reference hardware is not a pure seat-height translation")
            checks["original_height_loaded_reference"] = {
                "standoff_mm": original_standoff, "load_proxies": reference_proxies,
                "hardware_translation_difference_mm3": reference_difference,
                "raised_finger_proxy": finger_clearance_report(
                    preset, temporary / f"hand-reference-{preset}.json",
                    standoff=original_standoff, require_clearance=True)}
            checks["raised_finger_proxy"] = finger_clearance_report(
                preset, DOCS / f"hand_clearance_{preset}.json")
            checks["sequential_release"] = sequential_release(
                temporary, preset, centered, states, winders, reserves, hardware, ties, seat, reference)
            checks["loaded_fit_status"] = ("requires_physical_check" if any(
                checks[name]["loaded_fit_status"] == "requires_physical_check"
                for name in ["load_proxies", "raised_finger_proxy", "sequential_release"])
                else "clear_in_sampled_proxies")
            combined = trimesh.util.concatenate([centered, *winders])
            checks["bare_packet_size_mm"] = combined.extents.tolist()
            checks["wire_reserve_packet_size_without_hardware_mm"] = [150, 137, float(combined.bounds[1, 2] + bulge)]
            checks["estimated_three_parts_solid_PETG_g"] = float((center.volume + 2 * winder.volume) * 0.00127)
            checks["print_layout"] = mesh_report(plate, 3)
            report["presets"][preset] = checks
        coupon = export(HERE / "fit_coupon.stl", SCAD, ['part="fit_coupon"'])
        report["fit_coupon"] = mesh_report(coupon, 2)
        retention_coupon = export(HERE / "retention_coupon.stl", SCAD, ['part="retention_coupon"'])
        report["retention_coupon"] = mesh_report(retention_coupon, 3)
        bnc_coupon = export(HERE / "bnc_fit_coupon.stl", ORIGINAL, ['part="coupon"'])
        report["bnc_fit_coupon"] = mesh_report(bnc_coupon)
        if args.source:
            from shapely.affinity import translate
            sys.path.insert(0, str(HERE.parent / "dipole_winder"))
            from generate_reference_profile import load_silhouette
            source, _ = load_silhouette(args.source)
            reference = translate(source, xoff=-62.5)
            produced = sections(trimesh.load_mesh(HERE / "winder.stl"), 2.5)
            region = box(-100, 0, 100, 60)
            error = reference.intersection(region).symmetric_difference(produced.intersection(region)).area
            require(error < 0.02, f"Native winding region changed: {error}")
            report["native_winding_region"] = {
                "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
                "symmetric_difference_area_mm2": error}
        report["parameter_variants"] = check_parameter_variants(temporary)
        retention = check_retention_margin(temporary)
        (DOCS / "retention_audit.json").write_text(json.dumps(retention, indent=2) + "\n")
        require(retention["status"] == "passed", "Printed-fit assumption screen failed; see review/retention_audit.json")
        report["retention_margin"] = {
            "status": retention["status"], "report": str((DOCS / "retention_audit.json").relative_to(ROOT)),
            "scope": "Actual bearing footprints under explicit geometric loss assumptions; not measured pull force"}
    report["input_sha256"] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in input_paths}
    require(report["input_sha256"] == initial_hashes, "Source changed during validation; rerun the checks")
    parked_path = DOCS / "parked_audit.json"
    parked = json.loads(parked_path.read_text()) if parked_path.exists() else {}
    current = parked.get("status") == "passed" and parked.get("input_sha256") and all(
        (ROOT / relative).is_file() and hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
        for relative, digest in parked.get("input_sha256", {}).items())
    if not current:
        subprocess.run([sys.executable, str(DOCS / "parked_audit.py"),
                        "--expected-source-sha256", hashlib.sha256(SCAD.read_bytes()).hexdigest()], check=True)
        parked = json.loads(parked_path.read_text())
    require(parked["status"] == "passed", "Independent parked-pose audit did not pass")
    require({str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in input_paths} == initial_hashes,
            "Source changed during the independent audit; rerun the checks")
    report["independent_parked_pose_audit"] = {
        "status": parked["status"], "report": str(parked_path.relative_to(ROOT)),
        "source_sha256": parked["source_sha256"]}
    for p in [parked_path, DOCS / "parked_audit.py", DOCS / "hand_clearance.py"]:
        report["input_sha256"][str(p.relative_to(ROOT))] = hashlib.sha256(p.read_bytes()).hexdigest()
    report["output_sha256"] = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                               for name in PRINT_FILES}
    report["dry_mechanism_status"] = "passed"
    report["loaded_fit_status"] = ("requires_physical_check" if any(
        c["loaded_fit_status"] == "requires_physical_check" for c in report["presets"].values())
        or report["parameter_variants"]["status"] == "passed_with_fit_caveats" else "clear_in_sampled_proxies")
    report["status"] = ("passed_with_fit_caveats" if report["loaded_fit_status"] == "requires_physical_check"
                        else "passed")
    (HERE / "validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Wrote validation.json ({report['status']})", flush=True)


if __name__ == "__main__":
    main()
