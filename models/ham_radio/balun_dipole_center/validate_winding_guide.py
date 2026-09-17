#!/usr/bin/env python3
"""Validate the exported winding paths and printable mesh, independently of labels.

All lengths are millimetres. Polyline distances use segment interiors as well
as endpoints; the 13-turn test counts signed crossings of an aperture disk.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import subprocess
import tempfile

import numpy as np
import trimesh
from shapely.geometry import LineString, Point, Polygon

HERE = Path(__file__).resolve().parent
SCAD = HERE / "winding_guide.scad"
MOCKUPS = HERE / "mockups.scad"
PARAM_NAMES = ["core_od", "core_id", "core_height", "core_fit_clearance", "wire_od",
               "wire_surface_gap", "groove_fit_clearance", "groove_depth",
               "supporting_wall_thickness", "edge_rounding", "crossover_clearance"]
METRIC_NAMES = ["wire_center_spacing", "groove_radius", "wall_thickness", "guide_ro",
                "guide_ri", "guide_top", "flat_surface_ridge", "cutter_separation",
                "package_d", "package_h", "rear_z"]
TOL = 0.00025  # OpenSCAD's echo rounds coordinates to six significant figures.


def openscad(output, params=None, expected_error=None, source=SCAD):
    command = ["openscad", "--hardwarnings", "--backend=Manifold"]
    if output.suffix == ".stl":
        command += ["--export-format", "binstl"]
    for key, value in (params or {}).items():
        command += ["-D", f"{key}={json.dumps(value)}"]
    result = subprocess.run(command + ["-o", str(output), str(source)],
                            capture_output=True, text=True)
    log = result.stdout + result.stderr
    if output.suffix == ".echo" and output.exists():
        log += output.read_text()
    if expected_error:
        assert "ERROR: Assertion" in log and expected_error in log, log[:1600]
        return None
    # ECHO'd manufacturing advisories are intentional output; actual OpenSCAD
    # engine warnings still fail the export.
    engine_errors = [line for line in log.splitlines()
                     if line.startswith(("ERROR:", "WARNING:"))]
    assert result.returncode == 0 and not engine_errors, log
    return log


def data(path, params=None):
    log = openscad(path, {**(params or {}), "view": "data"})
    result = {"turns": {}, "routes": {}}
    for line in log.splitlines():
        if not line.startswith('ECHO: "'):
            continue
        row = ast.literal_eval("[" + line[6:] + "]")
        if row[0] == "PARAMS":
            result["params"] = dict(zip(PARAM_NAMES, row[1]))
        elif row[0] == "METRICS":
            result["metrics"] = dict(zip(METRIC_NAMES, row[1]))
        elif row[0] == "TURN":
            result["turns"][row[1], row[2]] = np.asarray(row[3], dtype=float)
        elif row[0] == "ROUTE":
            result["routes"][row[1]] = np.asarray(row[2], dtype=float)
    assert len(result["turns"]) == 26 and len(result["routes"]) == 2
    return result


def segments(points):
    a, b = points[:-1], points[1:]
    keep = np.linalg.norm(b-a, axis=1) > 1e-7
    return a[keep], b[keep]


def distance_matrix(a, b, c, d):
    """Exact shortest segment-to-segment distances for every A/B combination."""
    u, v = b-a, d-c
    w = a[:, None, :]-c[None, :, :]
    aa = np.sum(u*u, axis=1)[:, None]
    bb = u @ v.T
    cc = np.sum(v*v, axis=1)[None, :]
    dd = np.einsum("ijk,ik->ij", w, u)
    ee = np.einsum("ijk,jk->ij", w, v)
    denom = aa*cc-bb*bb
    safe = np.where(np.abs(denom) > 1e-15, denom, 1)
    ss, tt = (bb*ee-cc*dd)/safe, (aa*ee-bb*dd)/safe
    interior = np.linalg.norm(w+ss[..., None]*u[:, None]-tt[..., None]*v[None], axis=2)
    interior[(np.abs(denom) < 1e-15) | (ss < 0) | (ss > 1) | (tt < 0) | (tt > 1)] = np.inf
    result = interior
    for s in [0, 1]:
        t = np.clip((ee+s*bb)/cc, 0, 1)
        result = np.minimum(result, np.linalg.norm(w+s*u[:, None]-t[..., None]*v[None], axis=2))
    for t in [0, 1]:
        s = np.clip((t*bb-dd)/aa, 0, 1)
        result = np.minimum(result, np.linalg.norm(w+s[..., None]*u[:, None]-t*v[None], axis=2))
    return result


def minimum_distance(first, second, local_exclusion=0):
    a, b = segments(first)
    c, d = segments(second)
    arc = np.r_[0, np.cumsum(np.linalg.norm(b-a, axis=1))]
    best, where = float("inf"), None
    for start in range(0, len(a), 96):
        stop = min(start+96, len(a))
        distances = distance_matrix(a[start:stop], b[start:stop], c, d)
        if local_exclusion:
            # Exclude one connected wire neighbourhood by arclength, not by
            # a fixed number of segments (wall segments can be 13 mm long).
            gap = np.maximum(arc[start:stop, None]-arc[None, 1:],
                             arc[None, :-1]-arc[start+1:stop+1, None])
            distances[gap < local_exclusion] = np.inf
        flat = np.argmin(distances)
        value = float(distances.flat[flat])
        if value < best:
            i, j = np.unravel_index(flat, distances.shape)
            best, where = value, [int(i+start), int(j)]
    return best, where


def aperture_crossings(points, height, radius):
    a, b = segments(points)
    mask = ((a[:, 2] < height) & (b[:, 2] >= height)) | ((b[:, 2] < height) & (a[:, 2] >= height))
    a, b = a[mask], b[mask]
    f = (height-a[:, 2])/(b[:, 2]-a[:, 2])
    hits = a+(b-a)*f[:, None]
    inside = np.linalg.norm(hits[:, :2], axis=1) < radius
    return [{"point_mm": p.tolist(), "direction": int(np.sign(dz))}
            for p, dz in zip(hits[inside], (b-a)[inside, 2])]


def inspect_paths(raw):
    p, m, turns, routes = (raw[k] for k in ["params", "metrics", "turns", "routes"])
    spacing = p["wire_od"]+p["wire_surface_gap"]
    assert abs(m["wire_center_spacing"]-spacing) < TOL
    signed = []
    for strand in range(2):
        hits = aperture_crossings(routes[strand], p["core_height"]/2, p["core_id"]/2)
        assert len(hits) == 13 and all(h["direction"] == -1 for h in hits), hits
        signed.append(hits)
    pair_values = np.concatenate([np.linalg.norm(turns[t, 0]-turns[t, 1], axis=1)
                                  for t in range(1, 14)])
    assert np.max(np.abs(pair_values-spacing)) < TOL
    turn_hits = []
    for turn in range(1, 14):
        hits = aperture_crossings(turns[turn, 0], p["core_height"]/2, p["core_id"]/2)
        assert len(hits) == 1 and hits[0]["direction"] == -1, (turn, hits)
        turn_hits.append(hits[0])
    assert np.linalg.norm(turn_hits[6]["point_mm"][:2]) < p["core_id"]/4
    assert all(np.linalg.norm(h["point_mm"][:2]) > p["core_id"]/4
               for i, h in enumerate(turn_hits) if i != 6)
    pair_min, pair_where = minimum_distance(routes[0], routes[1])
    assert pair_min >= p["wire_od"]-TOL, ("Conductors intersect", pair_min, pair_where)
    self_min = []
    for s in range(2):
        distance, where = minimum_distance(routes[s], routes[s], p["wire_od"]*2)
        assert distance >= p["wire_od"]-TOL, ("Self-intersection", s, distance, where)
        self_min.append(distance)
    cross_min, unrelated_min = float("inf"), float("inf")
    for t in range(1, 14):
        for u in range(t+1, 14):
            for s in range(2):
                for q in range(2):
                    distance, where = minimum_distance(turns[t, s], turns[u, q])
                    unrelated_min = min(unrelated_min, distance)
                    if t == 7 or u == 7:
                        cross_min = min(cross_min, distance)
                    assert distance >= 2*m["groove_radius"]-TOL, ("Channel intersection", t, u, s, q, distance, where)
    assert cross_min-p["wire_od"] >= p["crossover_clearance"]-TOL, ("Crossover interference", cross_min)
    assert m["flat_surface_ridge"] > 0 and m["cutter_separation"] > 0
    # The cutters are hulls of spheres along each segment. Densely sampling
    # segment interiors and using full smooth spheres conservatively bounds
    # their clearance to the square annular cavity (including its top edges).
    # This catches a groove cutting too deeply at a rounded bottom mouth.
    dense = np.concatenate([np.concatenate([np.linspace(a, b, 81)
                            for a, b in zip(path[:-1], path[1:])])
                            for path in turns.values()])
    radii = np.linalg.norm(dense[:, :2], axis=1)
    cavity_ri = p["core_id"]/2-p["core_fit_clearance"]
    cavity_ro = p["core_od"]/2+p["core_fit_clearance"]
    cavity_top = p["core_height"]+p["core_fit_clearance"]
    dr = np.maximum.reduce([cavity_ri-radii, radii-cavity_ro, np.zeros(len(radii))])
    dz = np.maximum.reduce([-dense[:, 2], dense[:, 2]-cavity_top, np.zeros(len(radii))])
    backing = np.hypot(dr, dz)-m["groove_radius"]
    upper = dense[:, 2] >= .65
    mouth = (dense[:, 2] >= 0) & (dense[:, 2] < .65)
    min_backing, min_mouth = float(backing[upper].min()), float(backing[mouth].min())
    lip = np.abs(dense[:, 2]) <= m["groove_radius"]
    # At the open Z=0 lip, even spheres centred BELOW the cup remove material.
    # Their effective cross-sectional cutter radius is sqrt(r²-z²).
    lip_backing = dr[lip]-np.sqrt(m["groove_radius"]**2-dense[lip, 2]**2)
    min_lip = float(lip_backing.min())
    assert min_backing >= p["supporting_wall_thickness"]-TOL, ("Insufficient upper backing", min_backing)
    assert min_mouth >= p["supporting_wall_thickness"]-TOL, ("Insufficient groove-mouth backing", min_mouth)
    assert min_lip >= p["supporting_wall_thickness"]-TOL, ("Insufficient Z=0 lip backing", min_lip)
    # Independently derive the flat-top mouth from the exported top centerline.
    top_axis = float(turns[1, 0][:, 2].max())
    groove_r = p["wire_od"]/2+p["groove_fit_clearance"]
    mouth_width = 2*np.sqrt(groove_r**2-(top_axis-m["guide_top"])**2)
    assert abs(spacing-mouth_width-m["flat_surface_ridge"]) < TOL
    all_points = np.concatenate(list(routes.values()))
    max_radius = np.linalg.norm(all_points[:, :2], axis=1).max()+p["wire_od"]/2
    actual_h = float(np.ptp(all_points[:, 2])+p["wire_od"])
    assert abs(2*max_radius-m["package_d"]) < TOL
    assert abs(actual_h-m["package_h"]) < TOL
    assert 2*max_radius <= 34 and actual_h <= 18
    unsupported_pair = np.linalg.norm(routes[0]-routes[1], axis=1)
    # Rear links are explicitly free spans. Report their gap instead of
    # pretending every point of a free wire follows the ideal preview.
    rear = np.maximum(routes[0][:, 2], routes[1][:, 2]) < 0
    return {"parameters": p, "signed_aperture_passages_per_conductor": [len(x) for x in signed],
            "aperture_passage_direction": "all top to bottom",
            "numbered_passages_A": turn_hits,
            "supported_pair_center_spacing_range_mm": [float(pair_values.min()), float(pair_values.max())],
            "unsupported_rear_corresponding_spacing_range_mm": [float(unsupported_pair[rear].min()), float(unsupported_pair[rear].max())],
            "minimum_any_A_B_surface_gap_mm": pair_min-p["wire_od"],
            "minimum_nonlocal_self_surface_gap_mm": [v-p["wire_od"] for v in self_min],
            "minimum_unrelated_channel_gap_mm": unrelated_min-2*m["groove_radius"],
            "minimum_crossover_to_unrelated_wire_surface_gap_mm": cross_min-p["wire_od"],
            "flat_surface_ridge_mm": m["flat_surface_ridge"],
            "minimum_full_cutter_separation_mm": m["cutter_separation"],
            "minimum_conservative_upper_groove_backing_mm": min_backing,
            "minimum_conservative_bottom_mouth_backing_mm": min_mouth,
            "minimum_conservative_Z0_lip_backing_mm": min_lip,
            "package_diameter_mm": float(2*max_radius), "package_height_mm": actual_h,
            "allowance_mm": [34, 18], "allowance_change_required": False}


def inspect_leads(raw, echo_path):
    log = openscad(echo_path, {"view": "lead_data"}, source=MOCKUPS)
    leads = {}
    for line in log.splitlines():
        if line.startswith(('ECHO: "INPUT"', 'ECHO: "OUTPUT"')):
            row = ast.literal_eval("["+line[6:]+"]")
            leads[row[0], row[1]] = np.asarray(row[2], dtype=float)
    assert len(leads) == 4
    routes, p = raw["routes"], raw["params"]
    full = []
    for s in range(2):
        assert np.allclose(leads["INPUT", s][0], routes[s][0], atol=TOL)
        assert np.allclose(leads["OUTPUT", s][0], routes[s][-1], atol=TOL)
        full.append(np.concatenate([leads["INPUT", s][::-1], routes[s], leads["OUTPUT", s]]))
        hits = aperture_crossings(full[-1], p["core_height"]/2, p["core_id"]/2)
        assert len(hits) == 13 and all(h["direction"] == -1 for h in hits)
    pair_min, where = minimum_distance(full[0], full[1])
    assert pair_min >= p["wire_od"]-TOL, ("Assembly leads intersect winding", pair_min, where)
    self_gaps = []
    for s in range(2):
        distance, where = minimum_distance(full[s], full[s], p["wire_od"]*2)
        assert distance >= p["wire_od"]-TOL, ("Assembly lead self-intersection", s, distance, where)
        self_gaps.append(distance-p["wire_od"])
    return {"continuous_endpoint_connections": True,
            "signed_aperture_passages_including_leads": [13, 13],
            "minimum_full_assembly_A_B_surface_gap_mm": pair_min-p["wire_od"],
            "minimum_full_assembly_nonlocal_self_surface_gap_mm": self_gaps,
            "minimum_input_pair_surface_gap_mm": minimum_distance(leads["INPUT", 0], leads["INPUT", 1])[0]-p["wire_od"],
            "minimum_output_pair_surface_gap_mm": minimum_distance(leads["OUTPUT", 0], leads["OUTPUT", 1])[0]-p["wire_od"]}


def inspect_mesh(path, raw):
    mesh = trimesh.load(path, force="mesh")
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0, "Invalid guide STL topology"
    assert len(mesh.split(only_watertight=False)) == 1, "Guide STL contains disconnected shells"
    assert mesh.euler_number == 0, "Guide must retain its open central aperture"
    p, m = raw["params"], raw["metrics"]
    print_bounds = mesh.bounds.tolist()
    assert np.allclose(mesh.bounds, [[-m["guide_ro"], -m["guide_ro"], 0],
                                    [m["guide_ro"], m["guide_ro"], m["guide_top"]]], atol=.002)
    # Return the top-down printable STL to the source/installed coordinates.
    mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
    mesh.apply_translation([0, 0, m["guide_top"]])
    # The swept insertion envelope extends the core down through the open
    # underside. Any solid bottom lip or crossover obstruction would collide.
    core_outer = trimesh.creation.cylinder(radius=p["core_od"]/2, height=2*p["core_height"]+2, sections=192)
    core_inner = trimesh.creation.cylinder(radius=p["core_id"]/2, height=2*p["core_height"]+4, sections=192)
    for part in [core_outer, core_inner]:
        part.apply_translation([0, 0, -1])
    insertion = trimesh.boolean.difference([core_outer, core_inner], engine="manifold")
    collision = trimesh.boolean.intersection([mesh, insertion], engine="manifold")
    collision_volume = float(abs(collision.volume)) if len(collision.faces) else 0.0
    assert collision_volume < .0001, collision_volume
    # Inspect a slice of the exported STL immediately below the annular top.
    # A line across each ordinary groove pair measures the actual ridge that
    # remains in the tessellated print, rather than just its design formula.
    section = mesh.section(plane_origin=[0, 0, m["guide_top"]-.001], plane_normal=[0, 0, 1])
    assert section is not None
    material = Polygon()
    for ring in section.discrete:
        polygon = Polygon(ring[:, :2])
        assert polygon.is_valid
        material = material.symmetric_difference(polygon)
    ridge_widths = []
    for turn in range(1, 14):
        pair = raw["turns"][turn, 0], raw["turns"][turn, 1]
        highest = np.where(pair[0][:, 2] >= pair[0][:, 2].max()-TOL)[0]
        centers = (pair[0][highest, :2]+pair[1][highest, :2])/2
        center = centers.mean(axis=0)
        tangent = pair[1][highest[0], :2]-pair[0][highest[0], :2]
        tangent /= np.linalg.norm(tangent)
        across = material.intersection(LineString([center-tangent, center+tangent]))
        pieces = list(across.geoms) if hasattr(across, "geoms") else [across]
        middle = [piece for piece in pieces if piece.distance(Point(center)) < .0001]
        assert len(middle) == 1, ("Missing or split top ridge", turn)
        width = float(middle[0].length)
        assert m["flat_surface_ridge"]-.003 <= width <= m["flat_surface_ridge"]+.025, (turn, width)
        ridge_widths.append(width)
    return {"watertight": True, "connected_solids": 1, "volume_mm3": float(mesh.volume),
            "print_bounds_mm": print_bounds, "euler_number": int(mesh.euler_number),
            "swept_core_insertion_collision_mm3": collision_volume,
            "actual_STL_top_ridge_range_mm": [min(ridge_widths), max(ridge_widths)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paths-only", action="store_true", help="Fast path checks without STL regeneration")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as temp:
        temp = Path(temp)
        default = data(temp/"default.echo")
        result = {"scope": "paths_only" if args.paths_only else "paths_and_exported_meshes",
                  "default": inspect_paths(default)}
        result["assembly_leads"] = inspect_leads(default, temp/"leads.echo")
        if not args.paths_only:
            openscad(HERE/"winding_guide.stl")
            result["mesh"] = inspect_mesh(HERE/"winding_guide.stl", default)
        result["parameter_cases"] = []
        for params in [{"core_od": 29.75, "core_id": 18.5, "core_height": 14.25},
                       {"wire_od": .7, "wire_surface_gap": .15},
                       {"groove_fit_clearance": .03},
                       {"core_fit_clearance": .25}]:
            case = data(temp/"case.echo", params)
            report = inspect_paths(case)
            if not args.paths_only:
                openscad(temp/"case.stl", params)
                try:
                    report["mesh"] = inspect_mesh(temp/"case.stl", case)
                except AssertionError as error:
                    raise AssertionError(f"Mesh failed for parameters {params}: {error}") from error
            result["parameter_cases"].append(report)
        invalid = [({"core_id": 30}, "Invalid core dimensions"),
                   ({"core_fit_clearance": -.1}, "Clearance must be nonnegative"),
                   ({"wire_od": 0}, "Invalid wire dimensions"),
                   ({"groove_depth": .4}, "Use an open, shallow groove"),
                   ({"supporting_wall_thickness": 0}, "Backing/rounding must be positive"),
                   ({"edge_rounding": 10}, "Rounding or wire size"),
                   ({"output_angle": 80}, "Input and output must remain opposite"),
                   ({"lead_reserve_angle": 10}, "Lead reserve out of range"),
                   ({"groove_fit_clearance": .06}, "Paired channel cutters intersect"),
                   ({"minimum_printable_ridge": .45, "strict_print_checks": True}, "Ridge below selected printing threshold"),
                   ({"supporting_wall_thickness": .3, "strict_print_checks": True}, "Backing below selected printing threshold")]
        for params, error in invalid:
            openscad(temp/"invalid.echo", {**params, "view": "data"}, error)
        result["invalid_parameter_cases_rejected"] = len(invalid)
        advisory = openscad(temp/"advisory.echo", {"view": "data", "minimum_printable_ridge": .45})
        assert 'PRINT WARNING: ridge too narrow' in advisory
        result["ordinary_0_4_mm_nozzle_ridge_warning_verified"] = True
        result["source_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in [SCAD, MOCKUPS, Path(__file__)]}
        result["limits"] = ["CAD geometry checks only; not physical printing, enamel integrity or RF validation",
                            "Free rear links and crossover are nominal paths; unsupported wire spacing is not mechanically enforced",
                            "A 0.264 mm nominal ridge requires fine printing and is below a normal 0.4 mm nozzle width"]
        (HERE/"winding-guide-validation.json").write_text(json.dumps(result, indent=2)+"\n")
        print(f"PASS: 13 same-sense turns per conductor; {1+len(result['parameter_cases'])} parameter cases; "
              f"{len(invalid)} invalid configurations rejected")
        print(f"Package: {result['default']['package_diameter_mm']:.3f} mm diameter x "
              f"{result['default']['package_height_mm']:.3f} mm; allowance 34 x 18 mm")
        print(f"Minimum backing: {result['default']['minimum_conservative_upper_groove_backing_mm']:.3f} mm; "
              f"ridge: {result['default']['flat_surface_ridge_mm']:.3f} mm")
        print(f"Full results: {HERE/'winding-guide-validation.json'}")


if __name__ == "__main__":
    main()
