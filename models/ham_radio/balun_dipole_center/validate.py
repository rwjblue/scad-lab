#!/usr/bin/env python3
"""Export real meshes and check mounting interfaces and parameter limits."""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile

import numpy as np
import trimesh
from shapely import affinity
from shapely.geometry import Point, Polygon, box

HERE = Path(__file__).resolve().parent
SCAD = HERE / "balun_dipole_center.scad"
BASE = HERE.parent / "dipole_center/dipole_center.scad"


def volume(mesh):
    # Empty successful intersections have no mass properties to integrate.
    return float(mesh.volume) if len(mesh.faces) else 0.0


def export(path, params=None, source=SCAD, expected_error=None):
    command = ["openscad", "--hardwarnings", "--export-format", "binstl"]
    for key, value in (params or {}).items():
        command += ["-D", f"{key}={json.dumps(value)}"]
    result = subprocess.run(command + ["-o", str(path), str(source)],
                            capture_output=True, text=True)
    output = result.stdout + result.stderr
    if expected_error:
        assert "ERROR: Assertion" in output and expected_error in output, output
        return None
    assert result.returncode == 0 and "ERROR:" not in output and "WARNING:" not in output, output
    mesh = trimesh.load(path, force="mesh")
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
    assert len(mesh.split(only_watertight=False)) == 1
    return mesh


def section(mesh, axis, position):
    origin, normal = np.zeros(3), np.zeros(3)
    origin[axis] = position
    normal[axis] = 1
    path = mesh.section(plane_origin=origin, plane_normal=normal)
    assert path is not None
    axes = [i for i in range(3) if i != axis]
    rings = []
    for vertices in path.discrete:
        assert np.allclose(vertices[0], vertices[-1])
        polygon = Polygon(vertices[:, axes])
        assert polygon.is_valid
        rings.append(polygon)
    result = Polygon()
    for polygon in sorted(rings, key=lambda p: p.area, reverse=True):
        result = result.symmetric_difference(polygon)
    return result


def hole_at(material, x, y):
    polygons = [material] if material.geom_type == "Polygon" else list(material.geoms)
    holes = [Polygon(ring) for p in polygons for ring in p.interiors
             if Polygon(ring).covers(Point(x, y))]
    assert len(holes) == 1, (x, y, len(holes))
    return holes[0]


def inspect(mesh, diameter=34, rear=13, straps=False, input_gap=12, post_gap=20):
    low = 3 + rear + input_gap - 4
    cy = low + 4 + diameter / 2
    high = low + 8 + diameter
    bar = cy + diameter / 2 + post_gap
    height = bar + 18
    assert np.allclose(mesh.bounds, [[-45, 0, 0], [45, height, 23]], atol=.001)
    # Read the actual openings in the mesh at both faces and the middle.
    minimum_ligament = 100
    for z in [.01, .31, 2, 3.69, 3.99]:
        material = section(mesh, 2, z)
        assert material.geom_type == "Polygon" and len(material.interiors) == 13+2*straps
        for x in [-5.5, 5.5]:
            for y in [low, high]:
                actual = hole_at(material, x, y)
                expansion = max(0, .3 - min(z, 4-z))
                expected = box(x-1.7-expansion, y-1.2-expansion,
                               x+1.7+expansion, y+1.2+expansion)
                assert actual.boundary.hausdorff_distance(expected.boundary) < .04
                boundaries = [material.exterior] + [ring for ring in material.interiors
                              if not Polygon(ring).covers(Point(x, y))]
                minimum_ligament = min(minimum_ligament, *(actual.distance(r) for r in boundaries))
        for sign in [-1, 1]:
            for x, d in [(7 if straps else 10, 3.4),
                         (25 if straps else 28, 3.2),
                         (30.5 if straps else 33.5, 3.2),
                         (36 if straps else 39, 3.2)]:
                bore = hole_at(material, sign*x, bar)
                allowance = max(0, .5-min(z, 4-z)) if d == 3.2 else 0
                circle = Point(sign*x, bar).buffer(d/2+allowance, quad_segs=128)
                assert bore.boundary.hausdorff_distance(circle.boundary) < .01
        eye = hole_at(material, 0, bar+11)
        assert eye.centroid.distance(Point(0,bar+11)) < .001
    assert minimum_ligament > 3, minimum_ligament
    # D-hole is measured in a plane through the shelf, independently of SCAD.
    shelf = section(mesh, 1, 1.5)
    d_hole = hole_at(shelf, 0, 14)
    expected_d = Point(0,14).buffer(4.75, quad_segs=192).intersection(box(-10,0,10,17.9))
    assert d_hole.boundary.hausdorff_distance(expected_d.boundary) < .01
    # Reserved 18 mm diameter hardware corridor from shelf to estimated tip.
    for y in np.linspace(3.03, 3+rear-.01, 12):
        material = section(mesh, 1, y)
        circle = Point(0,14).buffer(8.98, quad_segs=128)
        assert material.intersection(circle).area < .001, y
    # A solid cylinder bounds the wound toroid; there must be no printed part
    # intruding into it above the backplate/pads. Allows no hidden collision.
    envelope = trimesh.creation.cylinder(radius=diameter/2, height=18, sections=128)
    envelope.apply_translation([0,cy,14])  # envelope z=5..23
    collision = trimesh.boolean.intersection([mesh,envelope], engine="manifold")
    assert volume(collision) < .001
    # Independent physical layout checks (actual barrel max from drawing).
    wire_entry_gap = 18 - 11.176 - 2.1
    assert wire_entry_gap >= 4
    assert bar-3.5-(cy+diameter/2) >= 16.49
    ring_gap = bar-11.176-(cy+diameter/2)
    assert ring_gap >= 8
    assert (cy-diameter/2)-(3+rear) >= 10
    # Front projections conservatively ignore any helpful depth separation.
    # Downward winding terminals occupy a maximum-width rectangular envelope.
    wound = Point(0, cy).buffer(diameter/2, quad_segs=192)
    for x in [-7 if straps else -10, 7 if straps else 10]:
        ring = box(x-5.461/2, bar-11.176, x+5.461/2, bar+5.461/2)
        assert wound.distance(ring) >= ring_gap-.001
    assert low-1.5-(3+rear) >= 3.49
    return dict(bounds_mm=mesh.bounds.tolist(), volume_mm3=float(mesh.volume),
                solid_PETG_mass_g=float(mesh.volume/1000*1.27),
                watertight=True, connected_solids=1, plate_openings=13+2*straps,
                bnc_D_hole_mm=9.5, minimum_tie_ligament_mm=minimum_ligament,
                wire_entry_gap_mm=wire_entry_gap, core_to_washer_mm=post_gap-3.5,
                wound_top_to_post_center_mm=post_gap,
                winding_ring_to_wound_vertical_gap_mm=ring_gap,
                bnc_hardware_envelope_above_shelf_mm=rear,
                bnc_envelope_to_wound_bottom_mm=input_gap,
                rear_tip_to_tie_mouth_mm=input_gap-5.5, package_print_collision_mm3=volume(collision))


def main():
    mesh = export(HERE / "balun_dipole_center.stl")
    result = {"default": inspect(mesh)}
    coupon = export(HERE / "mount_fit_coupon.stl", {"part": "mount_coupon"})
    assert np.allclose(coupon.bounds, [[-13,0,0],[13,88,23]], atol=.001)
    result["mount_coupon"] = dict(watertight=True, connected_solids=1,
                                   bounds_mm=coupon.bounds.tolist())
    mount_hole = hole_at(section(coupon, 1, 1.5), 0, 14)
    center_hole = hole_at(section(mesh, 1, 1.5), 0, 14)
    assert mount_hole.boundary.hausdorff_distance(center_hole.boundary) < .001
    result["mount_coupon"]["bnc_D_hole_mm"] = 9.5
    bnc = export(HERE / "bnc_fit_coupon.stl", {"part": "coupon"})
    bnc_slice = section(bnc, 1, 1.5)
    for x, diameter in [(-22,9.5),(0,9.7),(22,9.9)]:
        hole = hole_at(bnc_slice, x, 14)
        assert abs((hole.bounds[2]-hole.bounds[0])-diameter) < .002
        if diameter == 9.5:
            shifted = affinity.translate(hole, xoff=-x)
            assert shifted.boundary.hausdorff_distance(center_hole.boundary) < .001
    result["bnc_coupon"] = {"watertight":True,"diameters_mm":[9.5,9.7,9.9]}
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp)
        original = export(path / "base.stl", {"bnc_clearance":-.10}, source=BASE)
        # Shelf/root/ribs below Y14 and complete terminal bar/eye above Y76
        # must match the original at the same tested BNC fit; the new toroid
        # spine is the region between.
        bottom_box = trimesh.creation.box([120,14,40])
        bottom_box.apply_translation([0,7,20])
        a = trimesh.boolean.intersection([original,bottom_box],engine="manifold")
        b = trimesh.boolean.intersection([mesh,bottom_box],engine="manifold")
        difference = (volume(trimesh.boolean.difference([a,b],engine="manifold"))
                      + volume(trimesh.boolean.difference([b,a],engine="manifold")))
        assert difference < .02, difference
        max_bar_error = 0
        for z in [.01,.25,2,3.75,3.99]:
            a = affinity.translate(section(original,2,z),yoff=61).intersection(box(-50,76,50,112))
            b = section(mesh,2,z).intersection(box(-50,76,50,112))
            error = a.symmetric_difference(b).area
            assert error < .02, error
            max_bar_error = max(max_bar_error,error)
        result["base_preservation"] = {"shelf_root_rib_difference_mm3":float(difference),
                                       "max_translated_bar_eye_difference_mm2":max_bar_error}
        result["parameter_extremes"] = []
        for diameter, rear in [(32,10),(38,20)]:
            params = {"package_d":diameter,"bnc_rear_projection":rear}
            m = export(path / f"case-{diameter}.stl",params)
            result["parameter_extremes"].append({"parameters":params,
                                                 "mesh":inspect(m,diameter,rear)})
        for params, error in [({"package_d":39},"Wound OD"),
                              ({"bnc_rear_projection":9},"Rear projection"),
                              ({"bnc_clearance":.3},"BNC clearance"),
                              ({"bnc_clearance":-.15},"BNC clearance"),
                              ({"bnc_to_toroid_gap":9},"BNC wire gap"),
                              ({"toroid_to_post_gap":19},"Toroid-to-post gap"),
                              ({"part":"bad"},"Unknown part")]:
            export(path / "invalid.stl",params,expected_error=error)
        result["invalid_parameter_cases_rejected"] = 7
    result["source_sha256"] = {p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in [SCAD,BASE,Path(__file__)]}
    result["limits"] = ["CAD-only checks; no physical fit, printed load or RF power qualification",
                        "34x18 mm wound package; catalog-based ~12 mm BNC projection rounded to a 13 mm design envelope",
                        "Hardware, pads and ties in images are schematic and not exported"]
    (HERE / "validation.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__ == "__main__":
    main()
