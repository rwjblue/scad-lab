#!/usr/bin/env python3
"""Generate the portable K6ARK-derived A5 OpenSCAD outline.

From the repository root:

    uv run --no-project --with shapely python \
      models/ham_radio/dipole_winder/generate_reference_profile.py \
      /path/to/newWinder_wireframe.stl

The generated SCAD file has no STL or Python dependency. This script reads the
unmodified binary source STL, projects every nondegenerate triangle, rotates and
mirrors that silhouette, and fills only its upper openings (Y >= 25 mm). The
native exterior, arm positions, and remaining genuine openings are retained.

Cleanup removes holes smaller than 1e-8 mm² caused by floating-point overlay,
simplifies collinear mesh noise within 0.00001 mm, and writes coordinates to
six decimal places. It does not smooth, scale, or relocate the original horns.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct

from shapely import affinity, union_all
from shapely.geometry import Polygon, box
from shapely.geometry.polygon import orient


SOURCE_URL = (
    "https://www.printables.com/model/"
    "383037-k6ark-wire-antenna-winder-ul-wireframe-model"
)
SOURCE_SHA256 = "d023e8ecb8b5e7718d9f2c8431a90b2c823550a700396df8e0421103dbf5ad0d"
SIMPLIFY_TOLERANCE_MM = 0.00001
MIN_HOLE_AREA_MM2 = 0.00000001
COORDINATE_DECIMALS = 6


def load_silhouette(path: Path) -> tuple[Polygon, dict]:
    data = path.read_bytes()
    if len(data) < 84:
        raise ValueError("The reference must be a binary STL.")
    facet_count = struct.unpack_from("<I", data, 80)[0]
    if len(data) != 84 + facet_count * 50:
        raise ValueError("The reference must be an intact binary STL.")
    digest = hashlib.sha256(data).hexdigest()
    if digest != SOURCE_SHA256:
        raise ValueError(
            "This generator targets the accepted K6ARK wireframe STL. "
            f"Expected SHA256 {SOURCE_SHA256}, got {digest}."
        )
    polygons = []
    z_values = []
    for index in range(facet_count):
        values = struct.unpack_from("<12f", data, 84 + index * 50)
        vertices = [values[offset:offset + 3] for offset in (3, 6, 9)]
        z_values.extend(point[2] for point in vertices)
        projected = Polygon([point[:2] for point in vertices])
        if projected.area > 1e-10:
            polygons.append(projected)
    silhouette = union_all(polygons)
    if silhouette.geom_type != "Polygon" or not silhouette.is_valid:
        raise ValueError("The source does not project to one valid polygon.")
    return silhouette, {
        "source_sha256": digest,
        "source_facets": facet_count,
        "source_thickness_mm": max(z_values) - min(z_values),
    }


def canonical_ring(ring, ccw: bool) -> list[tuple[float, float]]:
    """Give SCAD deterministic rounded vertices with the requested winding."""
    points = [
        tuple(round(value, COORDINATE_DECIMALS) for value in point)
        for point in list(ring.coords)[:-1]
    ]
    points = [tuple(0.0 if value == 0 else value for value in point) for point in points]
    # Simplification eliminates tiny consecutive edges before rounding. Check
    # rather than silently discarding any newly collapsed feature.
    if any(a == b for a, b in zip(points, points[1:] + points[:1])):
        raise ValueError("Coordinate rounding collapsed a polygon edge.")
    if Polygon(points).exterior.is_ccw != ccw:
        points.reverse()
    start = min(range(len(points)), key=lambda index: points[index])
    return points[start:] + points[:start]


def make_profile(silhouette: Polygon) -> tuple[list, dict]:
    # The STL's long-spine axis is X, with its midpoint at 62.5 mm.
    one_side = affinity.affine_transform(silhouette, [0, 1, 1, 0, 0, -62.5])
    mirrored = union_all([
        one_side,
        affinity.scale(one_side, xfact=-1, yfact=1, origin=(0, 0)),
    ])
    envelope = Polygon(mirrored.exterior)
    accepted = union_all([
        mirrored,
        envelope.intersection(box(-40, 25, 40, 75)),
    ])
    kept_holes = [
        hole for hole in accepted.interiors
        if Polygon(hole).area >= MIN_HOLE_AREA_MM2
    ]
    cleaned = Polygon(accepted.exterior, kept_holes).simplify(
        SIMPLIFY_TOLERANCE_MM, preserve_topology=True
    )
    cleaned = orient(cleaned, sign=1)
    holes = sorted(cleaned.interiors, key=lambda ring: Polygon(ring).bounds)
    rings = [canonical_ring(cleaned.exterior, ccw=True)]
    rings.extend(canonical_ring(hole, ccw=False) for hole in holes)
    generated = Polygon(rings[0], rings[1:])
    if not generated.is_valid:
        raise ValueError("The exported polygon is not valid.")
    assert generated.bounds == (-37.5, -70.0, 37.5, 70.0)
    outer_error = envelope.exterior.hausdorff_distance(generated.exterior)
    assert outer_error <= SIMPLIFY_TOLERANCE_MM + 0.000001
    assert len(generated.interiors) == 11
    reflected = affinity.scale(generated, xfact=-1, yfact=1, origin=(0, 0))
    symmetry_error = generated.boundary.hausdorff_distance(reflected.boundary)
    assert symmetry_error < 0.00002
    report = {
        "bounds_xy_mm": list(generated.bounds),
        "filled_region": "native upper openings at Y >= 25 mm",
        "simplification_tolerance_mm": SIMPLIFY_TOLERANCE_MM,
        "coordinate_decimal_places": COORDINATE_DECIMALS,
        "removed_numerical_holes": len(accepted.interiors) - len(kept_holes),
        "remaining_native_holes": len(generated.interiors),
        "smallest_native_hole_area_mm2": min(Polygon(r).area for r in rings[1:]),
        "outer_boundary_max_deviation_mm": outer_error,
        "area_symmetric_difference_mm2": accepted.symmetric_difference(generated).area,
        "mirror_boundary_max_deviation_mm": symmetry_error,
        "outer_vertices": len(rings[0]),
        "total_vertices": sum(len(ring) for ring in rings),
    }
    return rings, report


def format_number(value: float) -> str:
    return f"{value:.{COORDINATE_DECIMALS}f}".rstrip("0").rstrip(".")


def emit_scad(rings: list, metadata: dict) -> str:
    lines = [
        "// Generated by generate_reference_profile.py; do not edit coordinates by hand.",
        "// Source: K6ARK Wire Antenna Winder — UL Wireframe Model.",
        "// Original author: Adam Kimmerly (K6ARK). Attribution and terms: NOTICE.md.",
        f"// {SOURCE_URL}",
        "// Source file: newWinder_wireframe.stl (also supplied as K6ARK_Wire_Winder.stl).",
        f"// Source SHA256: {metadata['source_sha256']}",
        "// Derived profile: source_y -> X; source_x - 62.5 -> Y; mirror across X=0.",
        "// Scale 1:1; upper native openings at Y >= 25 mm filled for strain relief.",
        "// The generating script records source provenance and reproducible cleanup.",
        f"// Cleanup tolerance: {SIMPLIFY_TOLERANCE_MM:.5f} mm; coordinates: 6 decimals.",
        f"// Removed {metadata['removed_numerical_holes']} numerical holes smaller than 1e-8 mm^2.",
        f"// Retained {metadata['remaining_native_holes']} real native openings.",
        "// Maximum outer-boundary deviation: "
        f"{metadata['outer_boundary_max_deviation_mm']:.9f} mm.",
        "// Bounds: X +/-37.5, Y +/-70 mm. Reference extrusion thickness: 5 mm.",
        "",
        "module reference_frame_2d() {",
        "    polygon(",
        "        points = [",
    ]
    for index, ring in enumerate(rings):
        lines.append(f"            // {'Exterior' if index == 0 else f'Native opening {index}' }")
        for x, y in ring:
            lines.append(f"            [{format_number(x)}, {format_number(y)}],")
    lines.extend(["        ],", "        paths = ["])
    offset = 0
    for ring in rings:
        path = ", ".join(str(index) for index in range(offset, offset + len(ring)))
        lines.append(f"            [{path}],")
        offset += len(ring)
    lines.extend(["        ],", "        convexity = 12", "    );", "}", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Unmodified K6ARK wireframe binary STL")
    parser.add_argument(
        "--output", type=Path,
        default=Path(__file__).with_name("reference_profile.scad"),
    )
    args = parser.parse_args()
    silhouette, metadata = load_silhouette(args.source)
    rings, report = make_profile(silhouette)
    metadata.update(report)
    args.output.write_text(emit_scad(rings, metadata))
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
