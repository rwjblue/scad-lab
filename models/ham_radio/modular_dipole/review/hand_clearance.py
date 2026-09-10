#!/usr/bin/env python3
"""Analytic wire/fingertip proxies, not a hand or glove fit simulation.

python models/ham_radio/modular_dipole/review/hand_clearance.py \
  --pad-y 16.9 --pad-stroke 3.30 --finger-diameter 18 --preset 40m

Queries actual service-tail points and wire-reserve bounds from OpenSCAD. Reports minimum distances between
wire capsules and rounded rectangular fingertip sweeps, and emits a matching
OpenSCAD visualization. The chosen spherical fingertips are explicit assumptions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
MODELS = HERE.parent
ROOT = MODELS.parents[2]
MOCKUP = MODELS / "mockups.scad"
CAD = MODELS / "modular_dipole.scad"
INPUTS = [Path(__file__).resolve(), CAD, MOCKUP,
          MODELS / "winder_profile.scad", MODELS / "native_profile.scad"]
PARAMETERS = ("wing_length", "winding_span", "wire_face_bulge", "standoff",
              "wire_edge_bulge", "wire_hole_inner_x", "wire_hole_pitch", "winder_offset")


def add(a, b):
    return [x + y for x, y in zip(a, b)]


def sub(a, b):
    return [x - y for x, y in zip(a, b)]


def mul(a, s):
    return [x * s for x in a]


def norm(a):
    return math.sqrt(sum(x * x for x in a))


def clamp(x, lo, hi):
    return min(hi, max(lo, x))


def source_hashes():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in INPUTS}


def read_geometry(args):
    """Ask CAD for evaluated data, so custom routing and reserves share one source."""
    names = [*PARAMETERS, "frame_t", "face_bulge", "seat_z", "paddle_height",
             "center_plate_t", "snap_release", "tab_outer_y-paddle_inset",
             "winder_bounds", "service_tail_diameter()", "service_tail_joint_overlap()",
             "[for(s=[-1,1]) service_tail_points(s)]",
             "[for(s=[-1,1]) wire_envelope_bounds(s)]"]
    keys = [*PARAMETERS, "frame_t", "face_bulge", "seat_z", "paddle_height",
            "center_plate_t", "snap_release", "pad_y", "winder_bounds",
            "tail_diameter", "tail_overlap", "tails", "wire_reserves"]
    defines = {"preset": args.preset,
               **{name: getattr(args, name) for name in PARAMETERS
                  if getattr(args, name) is not None}}
    with tempfile.TemporaryDirectory(prefix="dipole-hand-config-") as temporary:
        source = Path(temporary) / "config.scad"
        output = source.with_suffix(".csg")
        source.write_text(f"include <{CAD}>\nuse <{MOCKUP}>\n"
                          f'echo(["HAND_CONFIG",{",".join(names)}]);\n')
        command = ["openscad", "--backend=Manifold", "--hardwarnings",
                   "-D", 'part="center"', "-o", str(output)]
        for name, value in defines.items():
            command += ["-D", f"{name}={json.dumps(value)}"]
        run = subprocess.run([*command, str(source)], capture_output=True, text=True)
        if run.returncode or not output.exists() or any(
                marker in run.stderr for marker in ("WARNING:", "ERROR:")):
            raise RuntimeError(f"Could not read actual CAD configuration:\n{run.stderr}")
        line = next((line.removeprefix("ECHO: ") for line in run.stderr.splitlines()
                     if line.startswith('ECHO: ["HAND_CONFIG",')), None)
        if line is None:
            raise RuntimeError("OpenSCAD did not emit HAND_CONFIG")
        config = dict(zip(keys, json.loads(line)[1:], strict=True))
    return config


def segment_box_distance(a, b, lo, hi):
    """Exact piecewise-quadratic minimum for segment versus an axis-aligned box.

    A zero-thickness box is the planar center sweep of a spherical fingertip.
    Subtracting both radii gives the capsule/swept-sphere surface clearance.
    """
    direction = sub(b, a)
    breaks = [0.0, 1.0]
    for i in range(3):
        if abs(direction[i]) > 1e-12:
            breaks.extend(t for edge in (lo[i], hi[i])
                          if 0 < (t := (edge - a[i]) / direction[i]) < 1)
    breaks = sorted(set(breaks))
    candidates = list(breaks)
    for left, right in zip(breaks, breaks[1:]):
        mid = (left + right) / 2
        ab, bb = 0.0, 0.0
        for i in range(3):
            p = a[i] + mid * direction[i]
            edge = lo[i] if p < lo[i] else hi[i] if p > hi[i] else None
            if edge is not None:
                ab += (a[i] - edge) * direction[i]
                bb += direction[i] ** 2
        if bb:
            candidates.append(clamp(-ab / bb, left, right))
    best = None
    for t in candidates:
        p = add(a, mul(direction, t))
        q = [clamp(p[i], lo[i], hi[i]) for i in range(3)]
        entry = (norm(sub(p, q)), t, p, q)
        if best is None or entry[0] < best[0]:
            best = entry
    return best


def box_distance(a0, a1, b0, b1):
    return norm([max(0, b0[i] - a1[i], a0[i] - b1[i]) for i in range(3)])


def proxy(name, corners, radius, role):
    return {"name": name, "role": role, "radius_mm": radius,
            "center_min_mm": [min(p[i] for p in corners) for i in range(3)],
            "center_max_mm": [max(p[i] for p in corners) for i in range(3)],
            "corners_mm": corners}


def fingertips(pad_y, stroke, diameter, seat, mode, paddle_height=10, plate_t=4):
    radius = diameter / 2
    # Preserve the original contact poses as standoff height changes. Clearance
    # is measured below; compact settings no longer imply wire below seat-3.
    z_offset = 2 if mode == "mid_face" else 8 if mode == "raised_face" else radius - 2
    pad_height = paddle_height if mode == "raised_face" else plate_t
    dz_above_edge = max(0, z_offset - pad_height)
    reach_y = math.sqrt(radius ** 2 - dz_above_edge ** 2)
    result = []
    for end in (-1, 1):
        result.append(proxy(f"{'left' if end < 0 else 'right'}_hook",
                            [[end*x, 0, seat-9] for x in (50, 76)], 9,
                            "18 mm middle-fingertip approach beneath fixed bridge"))
        for row in (-1, 1):
            corners = [[end*x, row*(pad_y+reach_y-t), seat+z_offset]
                       for x in (46, 76) for t in (0, stroke)]
            result.append(proxy(f"{'left' if end < 0 else 'right'}_{'lower' if row < 0 else 'upper'}",
                                corners, radius,
                                f"{mode} thumb/index approach and inward stroke"))
    return result


def assess(proxies, tails, diameter, overlap, reserves):
    result = []
    for finger in proxies:
        best = None
        for side, points in tails.items():
            for i, (a, b) in enumerate(zip(points, points[1:])):
                unit = mul(sub(b, a), 1 / norm(sub(b, a)))
                start, end = sub(a, mul(unit, overlap)), add(b, mul(unit, overlap))
                distance, t, p, q = segment_box_distance(
                    start, end, finger["center_min_mm"], finger["center_max_mm"])
                item = {"tail_exit_side": side, "segment_index": i,
                        "clearance_mm": distance-finger["radius_mm"]-diameter/2,
                        "wire_center_mm": p, "finger_center_mm": q}
                if best is None or item["clearance_mm"] < best["clearance_mm"]:
                    best = item
        reserve_gaps = []
        for row, (lower, upper) in zip((-1, 1), reserves, strict=True):
            gap = box_distance(finger["center_min_mm"], finger["center_max_mm"],
                               lower, upper) - finger["radius_mm"]
            reserve_gaps.append({"row": row, "clearance_mm": gap})
        result.append({**finger, "closest_wire": best,
                       "wire_reserve_clearances": reserve_gaps})
    return result


def write_scad(path, result, preset, geometry):
    lines = ["// Generated analytic fingertip assumptions; NOT glove validation.",
             "// Geometry snapshot queried from the same CAD configuration as the report.",
             f"include <{CAD}>",
             'part="assembled";', f'preset="{preset}";', "show_wire=false;",
             *[f"{name}={json.dumps(geometry[name])};" for name in PARAMETERS],
             "show_wire_reserve=true;",
             "active_end=1; // 1 right, -1 left, 0 overlays both approach alternatives",
             "// Parts render from the configured include above; tails use queried points."]
    for side, points in zip((-1, 1), geometry["tails"], strict=True):
        tint = [0.9, 0.22, 0.18] if side == 1 else [0.95, 0.65, 0.12]
        lines += [f"  color({json.dumps(tint)}) union() {{"]
        for a, b in zip(points, points[1:]):
            unit = mul(sub(b, a), 1 / norm(sub(b, a)))
            start = sub(a, mul(unit, geometry["tail_overlap"]))
            end = add(b, mul(unit, geometry["tail_overlap"]))
            lines += ["    hull() {",
                      *[f"      translate({json.dumps(p)}) sphere(d={geometry['tail_diameter']},$fn=24);"
                        for p in (start, end)], "    }"]
        lines += ["  }"]
    for lower, upper in geometry["wire_reserves"]:
        lines += ["  if(show_wire_reserve) %color([0.9,0.2,0.2,0.13])",
                  f"    translate({json.dumps(lower)}) cube({json.dumps(sub(upper, lower))});"]
    for item in result:
        end = -1 if item["name"].startswith("left") else 1
        tint = [0.15, 0.7, 0.65, 0.3] if item["name"].endswith("hook") else [0.3, 0.4, 0.9, 0.3]
        lines += [f"// {item['name']}: {item['role']}",
                  f"if(active_end==0 || active_end=={end}) %color({json.dumps(tint)}) hull() {{",
                  *[f"  translate({json.dumps(p)}) sphere(r={item['radius_mm']});" for p in item["corners_mm"]],
                  "}"]
    path.write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pad-y", type=float, help="Finger contact Y; defaults to the actual paddle face")
    parser.add_argument("--pad-stroke", type=float, help="Finger stroke; defaults to the CAD release travel")
    parser.add_argument("--finger-diameter", type=float, default=18)
    parser.add_argument("--preset", choices=["40m", "80m"], default="40m")
    for name in PARAMETERS:
        parser.add_argument("--" + name.replace("_", "-"), type=float,
                            help=f"Override CAD {name}; otherwise use its actual default")
    parser.add_argument("--output", type=Path, help="Report path; custom settings otherwise use a distinct filename")
    parser.add_argument("--emit-scad", action="store_true", help="Write optional fingertip views beside the report")
    args = parser.parse_args()
    for name, value in vars(args).items():
        if isinstance(value, float) and not math.isfinite(value):
            parser.error(f"{name} must be finite")
    if args.finger_diameter <= 0:
        parser.error("Finger diameter must be positive")
    inputs = source_hashes()
    geometry = read_geometry(args)
    pad_y = geometry["pad_y"] if args.pad_y is None else args.pad_y
    stroke = geometry["snap_release"] if args.pad_stroke is None else args.pad_stroke
    if pad_y <= 0 or stroke < 0:
        parser.error("Pad Y must be positive and stroke must be nonnegative")
    seat = geometry["seat_z"]
    tails = dict(zip((-1, 1), geometry["tails"], strict=True))
    diameter, overlap = geometry["tail_diameter"], geometry["tail_overlap"]
    custom = any(getattr(args, name) is not None for name in PARAMETERS if name != "winder_offset") or (
        geometry["winder_offset"] != 26 or args.finger_diameter != 18 or
        pad_y != geometry["pad_y"] or stroke != geometry["snap_release"])
    suffix = "_custom_" + hashlib.sha256(json.dumps(
        [geometry, pad_y, stroke, args.finger_diameter], sort_keys=True).encode()).hexdigest()[:8] if custom else ""
    output = args.output or HERE / f"hand_clearance_{args.preset}{suffix}.json"
    report = {"evidence": "Analytic spherical proxies only; no physical hand, glove or flexible-wire validation",
              "assumptions": {**vars(args), "output": str(output), "pad_y": pad_y, "pad_stroke": stroke},
              "cad_configuration": geometry, "seat_mm": seat,
              "tail_diameter_mm": diameter, "tail_joint_extension_mm": overlap,
              "source_sha256": inputs,
              "contact_modes": {}}
    for mode in ("mid_face", "upper_edge", "raised_face"):
        result = assess(fingertips(pad_y, stroke, args.finger_diameter, seat, mode,
                                  geometry["paddle_height"], geometry["center_plate_t"]),
                        tails, diameter, overlap, geometry["wire_reserves"])
        report["contact_modes"][mode] = result
        if args.emit_scad:
            generated = output.parent / (output.stem + "_views") if args.output or custom else HERE / "generated"
            generated.mkdir(parents=True, exist_ok=True)
            write_scad(generated / f"hand_{mode}_{args.preset}.scad", result, args.preset, geometry)
        print(mode, "minimum tail clearance mm:", round(min(p["closest_wire"]["clearance_mm"] for p in result), 3),
              "minimum wire-reserve clearance mm:", round(min(g["clearance_mm"] for p in result for g in p["wire_reserve_clearances"]), 3))
    if source_hashes() != inputs:
        raise RuntimeError("CAD or audit source changed during the hand-clearance check; rerun")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(output)


if __name__ == "__main__":
    main()
