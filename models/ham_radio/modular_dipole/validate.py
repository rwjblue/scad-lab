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

import numpy as np
import trimesh
from shapely.geometry import box

from validation_helpers import (HERE, ROOT, ORIGINAL, TOL, require, export, mesh_report,
                      volume, intersection_volume, translated, bounds_mesh,
                      sections, check_center_holes, check_bnc_cutout)

SCAD = HERE / "modular_dipole.scad"
MOCKUPS = HERE / "mockups.scad"
OFFSET = 26
RELEASE = 3.15
EPS_VOLUME = 0.001
EXPORT_CACHE = {}
DOCS = HERE / "review"
PRINT_FILES = ["center.stl", "winder.stl", "print_layout.stl", "winder_80m.stl",
               "print_layout_80m.stl", "fit_coupon.stl", "bnc_fit_coupon.stl"]


def expression_export(directory, name, expression, preset="40m", source=SCAD):
    # The local carrier and its tongues are identical for both winding-space
    # presets. Cache their repeated poses; placements still get checked at
    # each actual preset height. Hardware, ties and winders keep preset keys.
    carrier_only = source == SCAD and (
        expression.startswith("dock_center(") or "snap_tab(" in expression)
    cache_preset = "shared-center" if carrier_only else preset
    key = (str(source), hashlib.sha256(source.read_bytes()).hexdigest(), expression, cache_preset)
    if key in EXPORT_CACHE:
        return EXPORT_CACHE[key].copy()
    wrapper = directory / f"{name}.scad"
    wrapper.write_text(f'use <{source}>\n$fn=96;\n{expression}\n')
    mesh = export(directory / f"{name}.stl", wrapper, [f'preset="{preset}"'])
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
    removed = trimesh.boolean.difference([original, center], engine="manifold")
    # Only four new D openings and two guide bores may subtract plate material.
    tools = []
    for end in [-1, 1]:
        for row in [-1, 1]:
            circle = trimesh.creation.cylinder(radius=3.301, height=4.04, sections=192)
            circle.apply_scale([3.451 / 3.301, 1, 1])
            circle.apply_translation([0, 0, 2])
            # Upper flat faces outward (+Y), opposite the inward-moving tongue.
            clip = bounds_mesh([-4, -4, -0.03], [4, 2.351, 4.03])
            opening = trimesh.boolean.intersection([circle, clip], engine="manifold")
            if row < 0:
                opening.apply_transform(np.diag([-1., -1., 1., 1.]))
            opening.apply_translation([end * 36, 19.5 + row * 15, 0])
            tools.append(opening)
    for row in [-1, 1]:
        guide = trimesh.creation.cylinder(radius=2.301, height=4.04, sections=192)
        guide.apply_translation([row * 20, 19.5 + row * 17.5, 2])
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


def load_proxies(directory, preset, center, reserves, seat):
    hardware = expression_export(directory, f"hardware-{preset}", "hardware();", preset, HERE / "hardware_mockups.scad")
    ties = expression_export(directory, f"ties-{preset}",
                             "for(r=[-1,1]) winder_strap(r);", preset, MOCKUPS)
    tails = expression_export(directory, f"tails-{preset}", "service_tails();", preset, MOCKUPS)
    results = {
        "tie_to_center_mm3": clear(ties, center, "Tie/center"),
        "tie_to_hardware_mm3": clear(ties, hardware, "Tie/hardware"),
        "hardware_to_wire_reserve_mm3": [clear(hardware, reserve, "Hardware/coil") for reserve in reserves],
        "tail_to_center_mm3": clear(tails, center, "Suggested tail/center"),
        "remaining_gap_above_tie_mm": float(seat - ties.bounds[1, 2]),
        "evidence_limit": "Schematic connector and tie dimensions; flexible tails are a static route, not a dynamics model",
    }
    require(results["remaining_gap_above_tie_mm"] >= 1 - TOL, "Less than 1 mm above tie proxy")
    return results, hardware, ties


def lateral_capture(center, states, winder, row, seat):
    """Probe a broad grid, accepting only poses clear in the actual seated CAD.

    This includes the enlarged X play left by removing the tight plain locator.
    Samples are evidence of capture, not an exhaustive configuration-space proof.
    """
    import manifold3d

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
    for end, key in [(-1, "left"), (1, "right")]:
        retained_head = solid(trimesh.boolean.intersection([
            winder, bounds_mesh([-end * 36 - 4, row * 15 - 4, seat + 4.8],
                                [-end * 36 + 4, row * 15 + 4, seat + 6.01])], engine="manifold"))
        carriers = []
        for angle in angles:
            radians = np.radians(angle)
            lift = 4 * np.tan(radians) + 2 * (1 / np.cos(radians) - 1) + 0.04
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

    At padding=0 the opposite D8 shoulder's outside tangent is an actual
    support contact with the inclined plate underside, not a hover pose.
    """
    radians = np.radians(angle)
    lift = 4 * np.tan(radians) + 2 * (1 / np.cos(radians) - 1) + padding
    matrix = trimesh.transformations.rotation_matrix(
        -side * radians, [0, 1, 0], [-side * 36, 0, seat + 2])
    matrix[:3, 3] += [0, 0, lift]
    result = mesh.copy()
    result.apply_transform(matrix)
    return result


def flexure_clearance(directory, preset, center):
    original_tabs = expression_export(directory, f"tabs-{preset}-0",
                                      "for(s=[-1,1],r=[-1,1]) snap_tab(s,r,0);", preset)
    fixed = trimesh.boolean.difference([center, original_tabs], engine="manifold")
    wings = trimesh.boolean.union([
        bounds_mesh([-60, -10, -1], [-16.6, 60, 11]),
        bounds_mesh([16.6, -10, -1], [60, 60, 11])], engine="manifold")
    samples = []
    travels = np.linspace(0, RELEASE, 9)
    def build(travel):
        return expression_export(directory, f"tabs-{preset}-{travel:.3f}",
                                 f"for(s=[-1,1],r=[-1,1]) snap_tab(s,r,{travel});", preset)
    with ThreadPoolExecutor(max_workers=3) as pool:
        meshes = list(pool.map(build, travels))
    for travel, tabs in zip(travels, meshes):
        mesh_report(tabs, 4)
        free = trimesh.boolean.intersection([tabs, wings], engine="manifold")
        collision = clear(free, fixed, "Free flexures collide with fixed carrier")
        samples.append({"paddle_travel_mm": float(travel), "fixed_intersection_mm3": collision})
    return {"outside_root_fillet_abs_x_mm": 16.6, "samples": samples}


def sequential_release(directory, preset, centered, states, winders, reserves, hardware, ties, seat):
    """Both end orders: release, peel, return, settle on heads, release other end.

    Contact is found numerically from exported solids. Tests do not infer that
    a floating, noncolliding pose will remain open under gravity.
    """
    results = []
    for side, key, other_key in [(1, "right", "left"), (-1, "left", "right")]:
        print(f"Checking {preset} {key}-first peel and parking", flush=True)
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
                clear(metal, winder, "Peeling hardware/winder")
            for reserve in reserves:
                clear(carrier, reserve, "Peeling center/coil")
                clear(metal, reserve, "Peeling hardware/coil")
            clear(carrier, ties, "Peeling center/ties")
            clear(metal, ties, "Peeling hardware/ties")
        # Return the squeezed pair while held above its heads. This checks all
        # intermediate tongue poses, not merely the open and closed endpoints.
        travels = np.linspace(RELEASE, 0, 9)
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
        travels = np.linspace(0, RELEASE, 9)
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
                side * np.radians(angle), [0, 1, 0], [side * 36, 0, seat + 6])
            leveled = freed.copy()
            leveled.apply_transform(rotation)
            metal_leveled = parked_metal.copy()
            metal_leveled.apply_transform(rotation)
            for w in winders:
                leveling_peak = max(leveling_peak, clear(leveled, w, "Leveling the second end"))
                clear(metal_leveled, w, "Leveling hardware/winder")
            for reserve in reserves:
                clear(leveled, reserve, "Leveling center/coil")
                clear(metal_leveled, reserve, "Leveling hardware/coil")
            clear(leveled, ties, "Leveling center/ties")
            clear(metal_leveled, ties, "Leveling hardware/ties")
        exit_peak = 0.0
        for lift in np.linspace(0, 12, 49):
            moving = translated(leveled, [0, 0, float(lift)])
            metal = translated(metal_leveled, [0, 0, float(lift)])
            for w in winders:
                exit_peak = max(exit_peak, clear(moving, w, "Second-end exit"))
                clear(metal, w, "Exiting hardware/winder")
            for reserve in reserves:
                clear(moving, reserve, "Exiting center/coil")
                clear(metal, reserve, "Exiting hardware/coil")
            clear(moving, ties, "Exiting center/ties")
            clear(metal, ties, "Exiting hardware/ties")
        results.append({"first_end": key, "individual_stud_capture": capture,
                        "peel_angle_samples_deg": angles.tolist(), "peel_max_intersection_mm3": peak,
                        "parked_angle_deg": parked_angle,
                        "park_support_contact_growth": supports,
                        "reclosing_0p05deg_blocked_mm3": closure_block,
                        "opposite_end_capture_after_1p1mm_lift_mm3": still_captured,
                        "second_end_leveling_max_intersection_mm3": leveling_peak,
                        "leveling_pivot_mm": [side * 36, 0, seat + 6],
                        "leveling_rotation_samples_deg": np.linspace(0, parked_angle, 25).tolist(),
                        "second_end_exit_max_intersection_mm3": exit_peak,
                        "second_end_exit_samples_mm": np.linspace(0, 12, 49).tolist()})
    return {"status": "passed", "orders": results,
            "evidence_limit": "Nominal sampled rigid poses plus modeled elastic deflection; no physical hand, force or fatigue test"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path)
    args = parser.parse_args()
    input_paths = [SCAD, MOCKUPS, HERE / "hardware_mockups.scad", HERE / "native_profile.scad",
                   HERE.parent / "dipole_winder/frame_bevel.scad", ORIGINAL, Path(__file__), HERE / "validation_helpers.py"]
    initial_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in input_paths}
    report = {"status": "running", "revision": "modular-dipole-bnc-10p1",
              "evidence": "CAD only; printing, hand use, gloves, fatigue and loaded payout untested",
              "presets": {}}
    with tempfile.TemporaryDirectory(prefix="pinch-dipole-check-") as directory:
        temporary = Path(directory)
        original = export(temporary / "original.stl", ORIGINAL, ['bnc_clearance=0.20'])
        for preset, bulge in [("40m", 5), ("80m", 8)]:
            print(f"Checking {preset} meshes and preserved geometry", flush=True)
            suffix = "" if preset == "40m" else "_80m"
            params = [f'preset="{preset}"']
            center_path = HERE / "center.stl" if preset == "40m" else temporary / "center_80m.stl"
            center = export(center_path, SCAD, params + ['part="center"'])
            winder = export(HERE / f"winder{suffix}.stl", SCAD, params + ['part="winder"'])
            checks = {"center": mesh_report(center), "winder": mesh_report(winder),
                      "preserved_geometry": original_geometry(original, center)}
            if preset == "40m":
                reference_center = center.copy()
            else:
                same = sum(volume(trimesh.boolean.difference(pair, engine="manifold"))
                           for pair in [[reference_center, center], [center, reference_center]])
                require(same < EPS_VOLUME, "Presets unexpectedly use different center geometry")
                checks["center_symmetric_difference_from_40m_mm3"] = same
            checks["free_flexure_clearance"] = flexure_clearance(temporary, preset, center)
            seat = 5 + bulge + 3
            centered = translated(center, [0, -19.5, seat])
            winders = [placed_winder(winder, row) for row in [-1, 1]]
            reserves = [wire_reserve(row, bulge) for row in [-1, 1]]
            clear(*winders, "Winder pair")
            for reserve in reserves:
                clear(reserve, centered, "Loaded wire space")
            states = {}
            for key, values in [("left", [RELEASE, 0]), ("right", [0, RELEASE]),
                                ("both", [RELEASE, RELEASE])]:
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
                temporary, preset, centered, reserves, seat)
            subprocess.run([sys.executable, str(DOCS / "hand_clearance.py"),
                            "--pad-y", "16.9", "--pad-stroke", str(RELEASE),
                            "--winder-offset", str(OFFSET), "--preset", preset],
                           check=True, stdout=subprocess.DEVNULL)
            hand = json.loads((DOCS / f"hand_clearance_{preset}.json").read_text())
            raised = hand["contact_modes"]["raised_face"]
            tail_gap = min(x["closest_wire"]["clearance_mm"] for x in raised)
            coil_gap = min(c["clearance_mm"] for x in raised for c in x["wire_reserve_clearances"])
            require(tail_gap > 0 and coil_gap > 0, "Raised-face fingertip proxy intersects wire")
            checks["raised_finger_proxy"] = {
                "assumptions": hand["assumptions"], "minimum_tail_gap_mm": tail_gap,
                "minimum_wire_reserve_gap_mm": coil_gap, "evidence_limit": hand["evidence"]}
            checks["sequential_release"] = sequential_release(
                temporary, preset, centered, states, winders, reserves, hardware, ties, seat)
            combined = trimesh.util.concatenate([centered, *winders])
            checks["bare_packet_size_mm"] = combined.extents.tolist()
            checks["wire_reserve_packet_size_without_hardware_mm"] = [150, 137, float(combined.bounds[1, 2] + bulge)]
            checks["estimated_three_parts_solid_PETG_g"] = float((center.volume + 2 * winder.volume) * 0.00127)
            plate = export(HERE / f"print_layout{suffix}.stl", SCAD, params + ['part="print_layout"'])
            checks["print_layout"] = mesh_report(plate, 3)
            report["presets"][preset] = checks
        coupon = export(HERE / "fit_coupon.stl", SCAD, ['part="fit_coupon"'])
        report["fit_coupon"] = mesh_report(coupon, 2)
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
    report["independent_parked_pose_audit"] = {
        "status": parked["status"], "report": str(parked_path.relative_to(ROOT)),
        "source_sha256": parked["source_sha256"]}
    for p in [parked_path, DOCS / "parked_audit.py", DOCS / "hand_clearance.py"]:
        report["input_sha256"][str(p.relative_to(ROOT))] = hashlib.sha256(p.read_bytes()).hexdigest()
    report["output_sha256"] = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                               for name in PRINT_FILES}
    report["status"] = "incomplete" if any(c["sequential_release"]["status"] == "pending"
                                           for c in report["presets"].values()) else "passed"
    (HERE / "validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Wrote validation.json ({report['status']})", flush=True)


if __name__ == "__main__":
    main()
