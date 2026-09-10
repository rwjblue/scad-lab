#!/usr/bin/env python3
"""Analytic wire/fingertip proxies, not a hand or glove fit simulation.

python models/ham_radio/modular_dipole/review/hand_clearance.py \
  --pad-y 16.9 --pad-stroke 3.15 --finger-diameter 18 --preset 40m

Reads the actual service_tails() control points. Reports minimum distances between
wire capsules and rounded rectangular fingertip sweeps, and emits a matching
OpenSCAD visualization. The chosen spherical fingertips are explicit assumptions.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
MODELS = HERE.parent
ROOT = MODELS.parents[2]
MOCKUP = MODELS / "mockups.scad"
CAD = MODELS / "modular_dipole.scad"


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


def read_tail_points(seat, bulge):
    source = MOCKUP.read_text()
    body = re.search(r"module service_tails\(\) \{(.*?)\n\}", source, re.S).group(1)
    array = re.search(r"let\(points=(\[.*?\])\) color", body, re.S).group(1)
    tree = ast.parse(array, mode="eval")
    allowed = (ast.Expression, ast.List, ast.Load, ast.BinOp, ast.UnaryOp,
               ast.Add, ast.Sub, ast.Mult, ast.Div, ast.USub, ast.UAdd,
               ast.Constant, ast.Name)
    if any(not isinstance(node, allowed) for node in ast.walk(tree)):
        raise ValueError("Unexpected syntax in tail control points")
    if any(node.id not in {"s", "seat", "bulge"}
           for node in ast.walk(tree) if isinstance(node, ast.Name)):
        raise ValueError("Unexpected variable in tail control points")
    diameter = float(re.search(r"diameter=([\d.]+);", body).group(1))
    overlap = float(re.search(r"joint_overlap=([\d.]+);", body).group(1))
    return {s: eval(compile(tree, str(MOCKUP), "eval"), {"__builtins__": {}},
                    {"s": s, "seat": seat, "bulge": bulge}) for s in (-1, 1)}, diameter, overlap


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


def fingertips(pad_y, stroke, diameter, seat, mode):
    radius = diameter / 2
    # High edge pose leaves the entire spherical finger 1 mm above the wire-only
    # face reservation (whose top is seat-3). It contacts the paddle's top edge.
    z_offset = 2 if mode == "mid_face" else 8 if mode == "raised_face" else radius - 2
    pad_height = 10 if mode == "raised_face" else 4
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


def assess(proxies, tails, diameter, overlap, bulge, offset):
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
        for row in (-1, 1):
            y0, y1 = (offset-5, offset+42.5) if row > 0 else (-offset-42.5, -offset+5)
            gap = box_distance(finger["center_min_mm"], finger["center_max_mm"],
                               [-75, y0, -bulge], [75, y1, 5+bulge]) - finger["radius_mm"]
            reserve_gaps.append({"row": row, "clearance_mm": gap})
        result.append({**finger, "closest_wire": best,
                       "wire_reserve_clearances": reserve_gaps})
    return result


def write_scad(path, result, preset):
    lines = ["// Generated analytic fingertip assumptions; NOT glove validation.",
             f"use <{CAD}>", f"use <{MOCKUP}>", f'preset="{preset}";',
             "$fn=36;", "show_geometry=true;", "show_wire_reserve=true;",
             "active_end=1; // 1 right, -1 left, 0 overlays both approach alternatives",
             "if(show_geometry) {", "  color([0.9,0.47,0.19]) placed_center();",
             "  for(r=[-1,1]) color(r==1 ? [0.12,0.57,0.7] : [0.33,0.65,0.43]) placed_winder(r);",
             "  service_tails();", "  if(show_wire_reserve) for(r=[-1,1]) %color([0.9,0.2,0.2,0.13]) wire_envelope(r);", "}"]
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
    parser.add_argument("--pad-y", type=float, required=True)
    parser.add_argument("--pad-stroke", type=float, required=True)
    parser.add_argument("--finger-diameter", type=float, default=18)
    parser.add_argument("--preset", choices=["40m", "80m"], default="40m")
    parser.add_argument("--winder-offset", type=float, default=26)
    parser.add_argument("--emit-scad", action="store_true", help="Write optional fingertip views under review/generated")
    args = parser.parse_args()
    bulge = 8 if args.preset == "80m" else 5
    seat = 5 + bulge + 3
    tails, diameter, overlap = read_tail_points(seat, bulge)
    report = {"evidence": "Analytic spherical proxies only; no physical hand, glove or flexible-wire validation",
              "assumptions": vars(args), "seat_mm": seat,
              "tail_diameter_mm": diameter, "tail_joint_extension_mm": overlap,
              "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [CAD, MOCKUP]},
              "contact_modes": {}}
    for mode in ("mid_face", "upper_edge", "raised_face"):
        result = assess(fingertips(args.pad_y, args.pad_stroke, args.finger_diameter, seat, mode),
                        tails, diameter, overlap, bulge, args.winder_offset)
        report["contact_modes"][mode] = result
        if args.emit_scad:
            generated = HERE / "generated"
            generated.mkdir(exist_ok=True)
            write_scad(generated / f"hand_{mode}_{args.preset}.scad", result, args.preset)
        print(mode, "minimum tail clearance mm:", round(min(p["closest_wire"]["clearance_mm"] for p in result), 3),
              "minimum wire-reserve clearance mm:", round(min(g["clearance_mm"] for p in result for g in p["wire_reserve_clearances"]), 3))
    output = HERE / f"hand_clearance_{args.preset}.json"
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(output)


if __name__ == "__main__":
    main()
