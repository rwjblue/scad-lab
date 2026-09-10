#!/usr/bin/env python3
"""Measure and plot the supplied K6ARK meshes without modifying either STL.

Run from the repository root (paths to the user's supplied files are required):

  rtk proxy uv run --no-project --with matplotlib --with shapely --with numpy \
    python docs/concepts/2026-09-09-dipole-winder/analyze_reference.py \
    /path/to/newWinder_wireframe.stl /path/to/newWinder_noClip_5mm.stl

Angles describe the mesh geometry, not recovered native CAD parameters.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
from pathlib import Path
import struct

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, PathPatch
from matplotlib.path import Path as PlotPath
import numpy as np
from shapely import affinity, union_all
from shapely.geometry import Polygon


def load_stl(path: Path) -> dict:
    data = path.read_bytes()
    count = struct.unpack_from("<I", data, 80)[0]
    if len(data) != 84 + count * 50:
        raise ValueError(f"Expected a binary STL with {count} facets: {path}")
    records = np.array(
        [struct.unpack_from("<12f", data, 84 + i * 50) for i in range(count)]
    )
    vertices = records[:, 3:].reshape(-1, 3, 3)
    points = vertices.reshape(-1, 3)
    low, high = points.min(axis=0), points.max(axis=0)
    projected = []
    for triangle in vertices:
        polygon = Polygon(triangle[:, :2])
        if polygon.area > 1e-10:
            projected.append(polygon)
    # Union every nondegenerate projected facet; preserve genuine interior holes.
    silhouette = union_all(projected)
    return {
        "path": str(path.resolve()),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "facets": count,
        "bounds_min_mm": low.tolist(),
        "bounds_max_mm": high.tolist(),
        "extents_mm": (high - low).tolist(),
        "vertices": vertices,
        "normals": records[:, :3],
        "silhouette": silhouette,
    }


def measure_arms(mesh: dict) -> dict:
    """Use repeated long-side normals, then recover the external Z=0 runs.

    The source's long axis is X. Both prongs extend toward positive Y. Only
    long, steep segments in that part of the model are candidates. Repeated
    XY-projected side normals distinguish swept cylindrical arm surfaces from
    arbitrary triangulation diagonals on the solid model's planar faces.
    """
    triangles, normals = mesh["vertices"], mesh["normals"]
    x_mid = (mesh["bounds_min_mm"][0] + mesh["bounds_max_mm"][0]) / 2
    y_floor = mesh["bounds_max_mm"][1] - 32
    result = {}
    for side in ("left", "right"):
        groups = collections.defaultdict(list)
        for triangle, normal in zip(triangles, normals):
            nx, ny, nz = normal
            if abs(nz) >= 0.5 or abs(nx) < 0.3:
                continue
            if triangle[:, 1].min() < y_floor:
                continue
            if (triangle[:, 0].mean() < x_mid) != (side == "left"):
                continue
            span = max(
                np.linalg.norm(triangle[i, :2] - triangle[j, :2])
                for i, j in ((0, 1), (1, 2), (2, 0))
            )
            if span < 8:
                continue
            if nx < 0:
                nx, ny = -nx, -ny
            normal_angle = math.degrees(math.atan2(ny, nx))
            if not 5 < abs(normal_angle) < 45:
                continue
            groups[round(normal_angle, 2)].append((normal_angle, normal.tolist()))
        selected = max(groups.values(), key=len)
        normal_angle = float(np.median([value[0] for value in selected]))
        a = math.radians(normal_angle)
        normal_xy = np.array([math.cos(a), math.sin(a)])
        lines = collections.defaultdict(list)
        for triangle in triangles:
            for i, j in ((0, 1), (1, 2), (2, 0)):
                p, q = triangle[i], triangle[j]
                if max(abs(p[2]), abs(q[2])) > 1e-5:
                    continue
                if min(p[1], q[1]) < y_floor:
                    continue
                if ((p[0] + q[0]) / 2 < x_mid) != (side == "left"):
                    continue
                vector = q[:2] - p[:2]
                length = np.linalg.norm(vector)
                if length < 8 or abs(np.dot(vector / length, normal_xy)) > 1e-5:
                    continue
                # The parallel contour runs are separated by several mm;
                # 0.001 mm grouping absorbs only STL float-rounding noise.
                offset = round(float(np.dot(p[:2], normal_xy)), 3)
                lines[offset].extend([p, q])
        # Bay-facing exterior: rightmost parallel line at the left prong,
        # leftmost at the right. Interior frame-hole boundaries are excluded.
        offset = max(lines) if side == "left" else min(lines)
        points = np.array(lines[offset])
        root = points[np.argmin(points[:, 1])]
        tip = points[np.argmax(points[:, 1])]
        delta = tip[:2] - root[:2]
        heading = math.degrees(math.atan2(delta[1], delta[0]))
        angle_to_spine = min(heading, 180 - heading)
        assert abs(angle_to_spine - (90 - abs(normal_angle))) < 0.0001
        result[side] = {
            "angle_to_long_spine_deg": angle_to_spine,
            "sweep_from_perpendicular_deg": 90 - angle_to_spine,
            "root_to_tip_heading_from_positive_x_deg": heading,
            "external_straight_run_root_mm": root.tolist(),
            "external_straight_run_tip_mm": tip.tolist(),
            "external_straight_run_length_mm": float(np.linalg.norm(delta)),
            "projected_unit_side_normal_xy": normal_xy.tolist(),
            "supporting_long_side_facets": len(selected),
            "example_stl_face_normal_xyz": selected[0][1],
        }
    return result


def draw_polygon(ax, geometry, color):
    polygons = [geometry] if geometry.geom_type == "Polygon" else geometry.geoms
    for polygon in polygons:
        if polygon.geom_type != "Polygon" or polygon.area < 1e-6:
            continue
        vertices, codes = [], []
        # Explicit winding makes compound-path holes render correctly.
        exterior = list(polygon.exterior.coords)
        if not polygon.exterior.is_ccw:
            exterior.reverse()
        rings = [exterior]
        for interior in polygon.interiors:
            ring = list(interior.coords)
            if interior.is_ccw:
                ring.reverse()
            rings.append(ring)
        for ring in rings:
            vertices.extend(ring)
            codes.extend([PlotPath.MOVETO] + [PlotPath.LINETO] * (len(ring) - 2)
                         + [PlotPath.CLOSEPOLY])
        ax.add_patch(PathPatch(PlotPath(vertices, codes), facecolor=color,
                               edgecolor="#243e50", linewidth=0.9))


def plot_reference(meshes, report, output):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    fig = plt.figure(figsize=(13.2, 8.6), facecolor="white")
    grid = fig.add_gridspec(2, 2, width_ratios=(2.05, 1), left=0.055,
                           right=0.97, top=0.85, bottom=0.16,
                           wspace=0.13, hspace=0.26)
    fig.text(0.055, 0.945, "K6ARK retention-arm angles", fontsize=23,
             weight="bold", color="#183749")
    fig.text(0.055, 0.908,
             "Measured from the supplied STL geometry  ·  All dimensions in mm",
             fontsize=11, color="#4c6471")
    colors = {"left": "#bc4b35", "right": "#196c91"}
    for row, key, title in (
        (0, "wireframe", "UL wireframe — supplied mesh"),
        (1, "solid", "Solid, no clip — supplied mesh; translated +66 mm in Y"),
    ):
        mesh = meshes[key]
        dy = report["solid_alignment_translation_mm"][1] if key == "solid" else 0
        ax = fig.add_subplot(grid[row, 0])
        ax.set_title(title, loc="left", fontsize=11, weight="bold", pad=8)
        draw_polygon(ax, affinity.translate(mesh["silhouette"], yoff=dy), "#e5edf0")
        for side in ("left", "right"):
            arm = report["meshes"][key]["arms"][side]
            p, q = np.array(arm["external_straight_run_root_mm"]), np.array(
                arm["external_straight_run_tip_mm"])
            p[1] += dy
            q[1] += dy
            ax.plot([p[0], q[0]], [p[1], q[1]], color=colors[side],
                    linewidth=2.8, solid_capstyle="round", zorder=5)
            ax.plot([p[0], q[0]], [p[1], q[1]], "o", color=colors[side],
                    markersize=3, zorder=6)
            label_x = 43 if side == "left" else 82
            ax.annotate(f"{arm['angle_to_long_spine_deg']:.3f}°\nto long spine",
                        xy=(p[:2] + q[:2]) / 2, xytext=(label_x, 27),
                        ha="center", va="center", fontsize=10,
                        color=colors[side],
                        arrowprops={"arrowstyle": "-", "color": colors[side],
                                    "lw": 0.8, "shrinkA": 4, "shrinkB": 5})
        ax.annotate("", xy=(132.5, -25), xytext=(-7.5, -25),
                    arrowprops={"arrowstyle": "<->", "color": "#627883", "lw": 0.9})
        for x in (-7.5, 132.5):
            ax.plot([x, x], [-21, -28], color="#627883", linewidth=0.7)
        ax.text(62.5, -28.5, "140.000  ·  long-spine / X direction", ha="center",
                va="top", fontsize=9, color="#4c6471")
        ax.set_aspect("equal")
        ax.set_xlim(-14, 139)
        ax.set_ylim(-36, 44)
        ax.axis("off")

    ax = fig.add_subplot(grid[:, 1])
    ax.set_title("Rotated + mirrored interpretation", loc="left",
                 fontsize=11, weight="bold", pad=16)
    ax.set_aspect("equal")
    ax.set_xlim(-60, 62)
    ax.set_ylim(-77, 95)
    ax.axis("off")
    sweep = report["symmetric_average_sweep_from_perpendicular_deg"]
    rise = 45 * math.tan(math.radians(sweep))
    ax.plot([0, 0], [-33, 33], color="#294f65", linewidth=6,
            solid_capstyle="round")
    for sx in (-1, 1):
        for sy in (-1, 1):
            ax.plot([0, sx * 45], [sy * 33, sy * (33 + rise)],
                    color="#9bb6c6", linewidth=8, solid_capstyle="round")
    ax.plot([0, 55], [33, 33], "--", color="#b36140", linewidth=1)
    ax.add_patch(Arc((0, 33), 46, 46, theta1=0, theta2=sweep,
                     linewidth=1.5, color="#b36140"))
    ax.text(27, 39, "26.4°", color="#a7492e", fontsize=12, weight="bold")
    ax.text(14, 27, "horizontal reference", color="#805e4b", fontsize=8)
    ax.text(0, 8, "Long spine", ha="center", color="#294f65", fontsize=10,
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 3})
    ax.text(0, 1, "now vertical", ha="center", color="#4c6471", fontsize=9,
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 2})
    ax.text(0, 79, "Tips splay away from the center", ha="center", fontsize=10,
            color="#294f65")
    ax.annotate("", xy=(47, 62), xytext=(34, 56),
                arrowprops={"arrowstyle": "->", "color": "#294f65"})
    ax.annotate("", xy=(-47, 62), xytext=(-34, 56),
                arrowprops={"arrowstyle": "->", "color": "#294f65"})
    ax.text(0, -69, "Orientation schematic only\nNo dimensions transferred",
            ha="center", va="top", fontsize=9, color="#4c6471")
    fig.text(0.055, 0.102,
             "Highlighted runs are the straight external surfaces facing the winding bay. "
             "Both meshes have the same arm directions.", fontsize=10, color="#294f65")
    fig.text(0.055, 0.07,
             "The meshes differ slightly left to right: 26.424° / 26.405° from perpendicular. "
             "A symmetric 26.4° sweep is a design simplification.", fontsize=10, color="#294f65")
    fig.text(0.055, 0.038,
             "Source: user-supplied newWinder_wireframe.stl and newWinder_noClip_5mm.stl. "
             "Measurements are not claimed native CAD parameters.", fontsize=8.5, color="#647984")
    fig.savefig(output / "reference-angles.png", dpi=180, facecolor="white")
    fig.savefig(output / "reference-angles.svg", facecolor="white")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wireframe", type=Path)
    parser.add_argument("solid", type=Path)
    parser.add_argument("--local-download", type=Path,
                        default=Path.home() / "Downloads/K6ARK_Wire_Winder.stl")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    meshes = {"wireframe": load_stl(args.wireframe), "solid": load_stl(args.solid)}
    dy = meshes["wireframe"]["bounds_min_mm"][1] - meshes["solid"]["bounds_min_mm"][1]
    report = {
        "reference_listing": "https://www.printables.com/model/383037-k6ark-wire-antenna-winder-ul-wireframe-model",
        "provenance": "Measured from the two user-supplied STL meshes. The supplied "
                      "file identity is authoritative; angles are measured mesh geometry, "
                      "not recovered or claimed native CAD parameters.",
        "method": "Binary STL vertices and face normals; repeated long rounded-side "
                  "facet normals projected into XY identify the arm direction. "
                  "Collinear Z=0 exterior contour edges recover the bay-facing straight "
                  "run endpoints. All nondegenerate XY facet projections are unioned "
                  "for the plotted silhouettes, retaining interior holes.",
        "angle_convention": "Original long spine is parallel to X. The original arms "
                            "extend toward positive Y and splay away from the X midpoint: "
                            "left root-to-tip travels left/up, right travels right/up. "
                            "Angle to spine is the acute angle to X. Sweep is its "
                            "complement, measured from perpendicular to the spine.",
        "solid_alignment_translation_mm": [0, dy, 0],
        "meshes": {},
    }
    for name, mesh in meshes.items():
        report["meshes"][name] = {
            key: value for key, value in mesh.items()
            if key not in {"vertices", "normals", "silhouette"}
        }
        report["meshes"][name]["arms"] = measure_arms(mesh)
        report["meshes"][name]["projected_area_mm2"] = mesh["silhouette"].area
    arms = report["meshes"]["wireframe"]["arms"]
    report["symmetric_average_sweep_from_perpendicular_deg"] = sum(
        arm["sweep_from_perpendicular_deg"] for arm in arms.values()) / 2
    for side in ("left", "right"):
        assert abs(report["meshes"]["wireframe"]["arms"][side]["angle_to_long_spine_deg"]
                   - report["meshes"]["solid"]["arms"][side]["angle_to_long_spine_deg"]) < 0.0001
    if args.local_download.exists():
        local = args.local_download.read_bytes()
        report["local_download_identity"] = {
            "path": str(args.local_download.resolve()),
            "sha256": hashlib.sha256(local).hexdigest(),
            "bytes": len(local),
            "byte_identical_to_supplied_wireframe": local == args.wireframe.read_bytes(),
        }
    else:
        report["local_download_identity"] = {"path": str(args.local_download),
                                             "status": "not present"}
    (args.output_dir / "reference-angles.json").write_text(json.dumps(report, indent=2) + "\n")
    plot_reference(meshes, report, args.output_dir)
    print(json.dumps({"output_dir": str(args.output_dir.resolve()),
                      "wireframe_arms": arms,
                      "solid_alignment_translation_mm": [0, dy, 0],
                      "local_download_identity": report["local_download_identity"]}, indent=2))


if __name__ == "__main__":
    main()
