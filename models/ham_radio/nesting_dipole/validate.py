#!/usr/bin/env python3
"""Verify original-station parts and their spine-to-spine packing orientation."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

import numpy as np
from shapely.geometry import Point, Polygon, box as shape_box
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SCAD = HERE / "nesting_dipole.scad"
ORIGINAL = HERE.parent / "dipole_center/dipole_center.scad"
EPS_VOLUME = 0.001
TOL = 0.025
PRINT_FILES = ["center.stl", "winder.stl", "winder_80m.stl", "print_layout.stl",
               "print_layout_80m.stl", "fit_coupon.stl"]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def export(path, source=SCAD, definitions=()):
    command = ["openscad", "--backend=Manifold", "--hardwarnings", "--export-format=binstl"]
    for definition in definitions:
        command += ["-D", definition]
    result = subprocess.run(command + ["-o", str(path), str(source)],
                            text=True, capture_output=True)
    require(result.returncode == 0 and path.exists(),
            f"OpenSCAD export failed: {path.name}\n{result.stdout}\n{result.stderr}")
    require("ERROR:" not in result.stderr and "WARNING:" not in result.stderr, result.stderr)
    return trimesh.load_mesh(path)


def rejected_export(directory, name, definitions, expected_message):
    path = directory / f"{name}.stl"
    command = ["openscad", "--backend=Manifold", "--hardwarnings", "-D", 'part="center"']
    for definition in definitions:
        command += ["-D", definition]
    result = subprocess.run(command+["-o", str(path), str(SCAD)], text=True, capture_output=True)
    require("Assertion" in result.stderr and expected_message in result.stderr,
            f"Invalid coupled parameters were not rejected for the intended reason: {name}\n{result.stderr}")
    return {"definitions": definitions, "rejected": True, "expected_assertion": expected_message}


def expression_export(directory, name, expression, definitions=()):
    wrapper = directory / f"{name}.scad"
    wrapper.write_text(f"use <{SCAD}>\n$fn=96;\n{expression}\n")
    return export(directory / f"{name}.stl", wrapper, definitions)


def volume(mesh):
    if mesh is None or len(mesh.faces) == 0:
        return 0.0
    with np.errstate(divide="ignore", invalid="ignore"):
        return abs(float(mesh.volume))


def overlap(a, b):
    return volume(trimesh.boolean.intersection([a, b], engine="manifold"))


def clear(a, b, description):
    value = overlap(a, b)
    require(value < EPS_VOLUME, f"{description}: {value:.6f} mm³ intersection")
    return value


def moved(mesh, translation):
    result = mesh.copy()
    result.apply_translation(translation)
    return result


def block(low, high):
    low, high = np.asarray(low), np.asarray(high)
    return moved(trimesh.creation.box(extents=high-low), (low+high)/2)


def mesh_report(mesh, components=1):
    count = len(mesh.split(only_watertight=False))
    require(mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0,
            "Mesh must be watertight, have consistent normals and positive volume")
    require(count == components, f"Expected {components} separate solids; got {count}")
    require(abs(mesh.bounds[0, 2]) < TOL, "Printable part must start at Z=0")
    return {"watertight": True, "connected_solids": count,
            "bounds_mm": mesh.bounds.tolist(), "size_mm": mesh.extents.tolist(),
            "volume_mm3": float(mesh.volume)}


def section_material(mesh, value, axis=2):
    origin, normal = np.zeros(3), np.zeros(3)
    origin[axis], normal[axis] = value, 1
    section = mesh.section(plane_origin=origin, plane_normal=normal)
    require(section is not None, f"Missing section on axis {axis} at {value}")
    dimensions = [i for i in range(3) if i != axis]
    material = Polygon()
    for contour in section.discrete:
        require(np.linalg.norm(contour[0]-contour[-1]) < TOL, "Open section contour")
        polygon = Polygon(contour[:, dimensions])
        require(polygon.is_valid, "Invalid section polygon")
        material = material.symmetric_difference(polygon)
    return material


def interior_holes(material):
    shapes = [material] if material.geom_type == "Polygon" else list(material.geoms)
    return [Polygon(ring) for shape in shapes for ring in shape.interiors]


def expected_plate_holes(z, terminal_x=7, wire_inner=25, wire_pitch=5.5,
                         wire_d=3.2, chamfer=.5, hang_d=8):
    mouths = max(chamfer-z, z-(4-chamfer), 0)
    holes = [("hoist", [0, 32], hang_d+2*mouths)]
    for side in [-1, 1]:
        holes.append(("terminal", [side*terminal_x, 21], 3.4))
        holes.extend(("wire", [side*(wire_inner+i*wire_pitch), 21], wire_d+2*mouths)
                     for i in range(3))
    return holes


def preserved_center(original, center, **options):
    """Rebuild the changed plate independently, retaining inherited raised geometry."""
    require(np.allclose(center.extents, [90, 39, 23], atol=TOL),
            "Center must remain within the original 90 x 39 x 23 mm envelope")
    samples = []
    for z in [.025, .1, .3, .6, 2, 3.4, 3.7, 3.9, 3.975]:
        inherited = section_material(original, z)
        original_holes = interior_holes(inherited)
        require(len(original_holes) == 9, "Expected nine holes in the original center")
        expected = inherited
        for hole in original_holes:
            expected = expected.union(hole)
        for side in [-1, 1]:
            x = side*40
            pad = shape_box(x-3, 13, x+3, 29).buffer(2, quad_segs=24)
            expected = expected.union(pad)
            x = side*41
            slot = shape_box(x-1, 14.5, x+1, 27.5).buffer(.5, quad_segs=24)
            expected = expected.difference(slot)
        specifications = expected_plate_holes(z, **options)
        for kind, axis, diameter in specifications:
            expected = expected.difference(Point(*axis).buffer(diameter/2, quad_segs=24))
        actual = section_material(center, z)
        difference = expected.symmetric_difference(actual).area
        require(difference < .01,
                f"Center plate differs outside intended holes/end pads at Z={z}: {difference:.6f} mm²")
        holes = interior_holes(actual)
        require(len(holes) == 11, "Center must contain exactly nine round holes and two strap slots")
        measurements = []
        for kind, axis, diameter in specifications:
            matching = [hole for hole in holes if hole.covers(Point(*axis))]
            require(len(matching) == 1, f"Missing {kind} hole at {axis}")
            hole = matching[0]
            size = np.array(hole.bounds)[2:]-np.array(hole.bounds)[:2]
            require(np.allclose(size, diameter, atol=TOL), f"Incorrect {kind} hole diameter")
            require(np.linalg.norm(np.asarray(hole.centroid.coords[0])-axis) < TOL,
                    f"The {kind} hole axis moved")
            measurements.append({"kind": kind, "axis_xy_mm": axis,
                                 "diameter_xy_mm": size.tolist()})
        samples.append({"z_mm": z, "plate_symmetric_difference_mm2": difference,
                        "holes": measurements})
    upper_region = block([-50, -1, 4.02], [50, 40, 24])
    old = trimesh.boolean.intersection([original, upper_region], engine="manifold")
    new = trimesh.boolean.intersection([center, upper_region], engine="manifold")
    upper_difference = symmetric_difference(old, new)
    require(upper_difference < EPS_VOLUME, "Inherited BNC shelf, ribs or root reinforcement changed")
    terminal_x = options.get("terminal_x", 7)
    wire_inner = options.get("wire_inner", 25)
    wire_pitch = options.get("wire_pitch", 5.5)
    wire_d = options.get("wire_d", 3.2)
    chamfer = options.get("chamfer", .5)
    hang_d = options.get("hang_d", 8)
    face_radius = wire_d/2+chamfer
    ring_gap = wire_inner-terminal_x-face_radius-11.176
    wire_web = wire_pitch-2*face_radius
    strap_web = 39.5-(wire_inner+2*wire_pitch+face_radius)
    require(ring_gap >= 4-.00001, "Panduit barrel entry needs at least 4 mm to the inner wire mouth")
    require(wire_web >= 1.2-.00001, "Adjacent wire-hole mouths need at least 1.2 mm of material")
    require(strap_web >= 1.2-.00001, "Outer wire-hole mouth needs at least 1.2 mm before the strap slot")
    return {"overall_size_mm": center.extents.tolist(),
            "new_hoist_diameter_mm": hang_d,
            "terminal_to_inner_wire_center_distance_mm": wire_inner-terminal_x,
            "panduit_maximum_ring_center_to_barrel_entry_mm": 11.176,
            "panduit_barrel_to_inner_wire_mouth_gap_mm": ring_gap,
            "adjacent_wire_face_web_mm": wire_web,
            "outer_wire_mouth_to_strap_web_mm": strap_web,
            "hoist_mouth_outer_wall_mm": 7-hang_d/2-chamfer,
            "raised_inherited_geometry_symmetric_difference_mm3": upper_difference,
            "cross_sections": samples}


def symmetric_difference(a, b):
    return sum(volume(trimesh.boolean.difference(pair, engine="manifold"))
               for pair in [[a, b], [b, a]])


def rotated(mesh, axis, angle):
    result = mesh.copy()
    result.apply_transform(trimesh.transformations.rotation_matrix(np.radians(angle), axis))
    return result


def placed_winders(winder):
    return [moved(winder, [0, 11, 0]),
            moved(rotated(winder, [0, 0, 1], 180), [0, -11, 5])]


def packing_height(bulge, protrusion):
    return max(10+bulge+2, 10+protrusion+.5)


def placed_center(center, bulge, protrusion=3):
    return moved(rotated(moved(center, [0, -21, 0]), [0, 0, 1], 90),
                 [18, 7, packing_height(bulge, protrusion)])


def preserved_winder_frame(directory, name, winder, definitions):
    """Reconstruct the previous two-post frame, then exclude only the new bore."""
    expression = f"""
use <{HERE / 'winder_profile.scad'}>
use <{HERE.parent / 'dipole_winder/frame_bevel.scad'}>
wing_length=37.5;
winding_span=140;
beveled_frame(height=5,bevel=0.5) union() {{
    adjustable_winder_frame_2d(wing_length,winding_span);
    for(station=[-36,36]) translate([station,-11])
        hull() for(x=[-1,1]) translate([x,0]) circle(d=10);
}}
"""
    reference = expression_export(directory, f"{name}-original-frame", expression, definitions)
    frame = trimesh.boolean.intersection([winder, block([-250, -100, 0], [250, 100, 5])],
                                         engine="manifold")
    socket_region = moved(trimesh.creation.cylinder(radius=4.1, height=5.2, sections=96),
                          [-36, -11, 2.5])
    reference_without_socket = trimesh.boolean.difference([reference, socket_region], engine="manifold")
    frame_without_socket = trimesh.boolean.difference([frame, socket_region], engine="manifold")
    difference = symmetric_difference(reference_without_socket, frame_without_socket)
    require(difference < .02, "Winder frame changed outside the original post-to-hole conversion")
    require(np.allclose(frame.bounds[:,:2], reference.bounds[:,:2], atol=TOL),
            "Original winder outline bounds changed")
    return {"original_post_stations_xy_mm": [[-36, -11], [36, -11]],
            "original_pad_dimensions_xy_mm": [12, 10],
            "frame_thickness_mm": 5,
            "new_socket_excluded_radius_mm": 4.1,
            "frame_outside_socket_symmetric_difference_mm3": difference,
            "original_outline_bounds_xy_mm": reference.bounds[:,:2].tolist()}


def socket_dimensions(winder, clearance=.25):
    """Measure the receiver at the original negative-X post station."""
    diameter, lower_chamfer, upper_relief, thickness = 6+2*clearance, .4, .6, 5
    result = []
    for z in [.025, .15, .3, .425, 2.5, 4.375, 4.425, 4.5, 4.75, 4.975]:
        material = section_material(winder, z)
        holes = interior_holes(material)
        matching = [hole for hole in holes if hole.covers(Point(-36, -11))]
        require(len(matching) == 1, "Missing winder socket at the original X=-36, Y=-11 post station")
        hole = matching[0]
        expected = diameter+2*max(lower_chamfer-z, z-(thickness-upper_relief), 0)
        bounds = hole.bounds
        size = [bounds[2]-bounds[0], bounds[3]-bounds[1]]
        require(np.allclose(size, expected, atol=TOL), f"Incorrect socket diameter at Z={z}")
        require(np.linalg.norm(np.array(hole.centroid.coords[0])-[-36, -11]) < TOL,
                "Winder receiver axis moved")
        shapes = [material] if material.geom_type == "Polygon" else list(material.geoms)
        wall = min(shape.exterior.distance(hole) for shape in shapes)
        require(wall >= .5-TOL, f"Winder receiver has less than 0.5 mm exterior wall at Z={z}")
        result.append({"z_mm": z, "diameter_xy_mm": size, "minimum_exterior_wall_mm": wall})
    return {"axis_xy_mm": [-36, -11], "bore_diameter_mm": diameter,
            "radial_clearance_mm": clearance, "bottom_entry_chamfer_mm": lower_chamfer,
            "top_root_relief_depth_mm": upper_relief, "cross_sections": result}


def post_dimensions(winder, protrusion):
    """Check the single solid stud, its fillet, and exposed tip independently."""
    frame_top, frame_thickness, diameter, chamfer, fillet = 5, 5, 6, .6, .6
    height = frame_thickness+protrusion
    require(abs(winder.bounds[1, 2]-(frame_top+height)) < TOL,
            "Stud height must equal mating frame thickness plus protrusion")
    result = []
    samples = [(z, diameter+2*(fillet-np.sqrt(fillet**2-(z-fillet)**2)), "root_fillet")
               for z in [.025, .1, .2, .3, .45, .575]]
    samples += [(.625, diameter, "shaft"),
                (height-chamfer-.025, diameter, "shaft"),
                (height-chamfer/2, diameter-chamfer, "tip_chamfer")]
    for relative_z, expected, kind in samples:
        z = frame_top+relative_z
        shaft = section_material(winder, z)
        require(shaft.geom_type == "Polygon" and not shaft.interiors,
                "Exactly one solid stud may extend above each winder frame")
        require(np.linalg.norm(np.array(shaft.centroid.coords[0])-[36, -11]) < TOL,
                "Stud axis must remain at the original X=36, Y=-11 post station")
        bounds = shaft.bounds
        size = [bounds[2]-bounds[0], bounds[3]-bounds[1]]
        require(np.allclose(size, expected, atol=TOL),
                f"Expected {expected:.4f} mm {kind} diameter at Z={z}")
        area = np.pi*(expected/2)**2
        require(abs(shaft.area-area) < .005*area, "Stud section must be circular")
        result.append({"z_mm": z, "profile_region": kind,
                       "expected_diameter_mm": expected, "diameter_xy_mm": size})
    return {"axis_xy_mm": [36, -11], "height_above_frame_mm": height,
            "shaft_diameter_mm": diameter, "root_fillet_radius_mm": fillet,
            "protrusion_beyond_mating_winder_mm": protrusion,
            "tip_chamfer_mm": chamfer, "cross_sections": result}


def center_slots(center, slot_x=41):
    require(abs(center.extents[0]-90) < TOL, "Center must preserve the original 90 mm width")
    result = []
    for z in [.1, 2, 3.9]:
        material = section_material(center, z)
        holes = interior_holes(material)
        require(len(holes) == 11, "Center must contain nine original holes and two tie slots only")
        measured = []
        for side in [-1, 1]:
            x = side*slot_x
            matching = [hole for hole in holes if hole.covers(Point(x, 21))]
            require(len(matching) == 1, f"Missing center-end tie slot at X={x}")
            hole = matching[0]
            bounds = hole.bounds
            size = [bounds[2]-bounds[0], bounds[3]-bounds[1]]
            require(np.allclose(size, [3, 14], atol=TOL), "Tie slot must measure 3 x 14 mm")
            require(np.linalg.norm(np.array(hole.centroid.coords[0])-[x, 21]) < TOL,
                    "Tie slot center moved")
            wall = material.exterior.distance(hole)
            require(wall >= 2-TOL, "Tie slot must retain at least 2 mm of surrounding material")
            measured.append({"center_xy_mm": [x, 21], "aperture_xy_mm": size,
                             "minimum_exterior_wall_mm": wall})
        result.append({"z_mm": z, "slots": measured})
    # These were the four old receivers. None should survive the redesign.
    section = section_material(center, 2)
    for x in [-36, 36]:
        for y in [4.5, 34.5]:
            require(not any(hole.covers(Point(x, y)) for hole in interior_holes(section)),
                    "An obsolete center-to-winder receiver remains")
    return {"count": 2, "center_width_mm": float(center.extents[0]),
            "old_alignment_receivers_removed": True,
            "nominal_tie_width_mm": 12.7, "nominal_tie_thickness_mm": 2,
            "cross_sections": result}


def layout_parts(layout, center, winder):
    """Match all three exported parts to their standalone meshes after placement."""
    unmatched = list(layout.split(only_watertight=False))
    errors = []
    for reference in [center, winder, winder]:
        match = None
        for index, candidate in enumerate(unmatched):
            if abs(candidate.volume-reference.volume) > TOL:
                continue
            for angle in [0, 90, 180, 270]:
                aligned = rotated(candidate, [0, 0, 1], angle)
                aligned.apply_translation(reference.bounds[0]-aligned.bounds[0])
                if not np.allclose(aligned.extents, reference.extents, atol=TOL):
                    continue
                error = symmetric_difference(aligned, reference)
                if error < .02:
                    match = (index, error)
                    break
            if match is not None:
                break
        require(match is not None, "Print layout differs from standalone printable parts")
        index, error = match
        unmatched.pop(index)
        errors.append(error)
    require(not unmatched, "Unexpected extra print-layout components")
    return {"one_center_and_two_identical_winders": True,
            "part_symmetric_difference_mm3": errors}


def winder_joint(winder, protrusion, allow_root_interference=False):
    winders = placed_winders(winder)
    initial_overlap = overlap(*winders)
    bore = next(hole for hole in interior_holes(section_material(winder, 2.5))
                if hole.covers(Point(-36, -11)))
    root_clearance = (bore.bounds[2]-bore.bounds[0])/2+.4-3.6
    if not allow_root_interference:
        require(root_clearance >= -0.00001, "Stud root exceeds the bottom socket entry radius")
        require(initial_overlap < EPS_VOLUME,
                f"Spine-to-spine winders intersect: {initial_overlap:.6f} mm³")
    contact = overlap(winders[0], moved(winders[1], [0, 0, -.02]))
    require(contact > .1, "Docked winder frames have no face contact at Z=5")
    lateral = []
    for delta in [[.8, 0, 0], [-.8, 0, 0], [0, .8, 0], [0, -.8, 0]]:
        value = overlap(winders[0], moved(winders[1], delta))
        require(value > .1, "The engaged stud does not constrain lateral translation")
        lateral.append({"translation_mm": delta, "intersection_mm3": value})
    height = 5+protrusion
    samples = sorted(set([0, .025, .05, .1, .2, .4, .6, .8]+
                         list(np.arange(.25, height+.251, .25))))
    separation = []
    for distance in samples:
        value = overlap(winders[0], moved(winders[1], [0, 0, distance]))
        if not allow_root_interference:
            require(value < EPS_VOLUME, "Spine-to-spine winder separation blocked")
        separation.append({"separation_mm": float(distance), "intersection_mm3": value})
    for delta in [[.8, 0, height+.25], [-.8, 0, height+.25],
                  [0, .8, height+.25], [0, -.8, height+.25]]:
        clear(winders[0], moved(winders[1], delta), "Winders remain caught after disengagement")
    outward = []
    # After full vertical disengagement, translate the flipped winder in -Y.
    # This checks a complete extraction route rather than just the socket exit.
    # At 80 mm travel the unchanged profiles are fully separated in XY.
    for distance in [0, .25, .5, 1, 2, 4, 8, 12, 20, 40, 80]:
        delta = [0, -distance, height+.25]
        released = moved(winders[1], delta)
        value = clear(winders[0], released, "Outward winder extraction path blocked")
        outward.append({"translation_mm": delta, "intersection_mm3": value})
    require(released.bounds[1, 1] < winders[0].bounds[0, 1],
            "Final outward extraction sample must fully separate the winder footprints")
    # Verify the existing narrow tie opening remains available on each winder.
    opening = block([-7, -5.3, -.01], [7, -2.3, 5.01])
    clear(winder, opening, "New joint obstructs the native central tie opening")
    interference = [sample for sample in separation if sample["intersection_mm3"] >= EPS_VOLUME]
    has_interference = bool(interference) or root_clearance < -0.00001
    return {"status": "root_interference" if has_interference else "passed",
            "nominal_root_entry_radial_clearance_mm": root_clearance,
            "engaged_stud_count": 1,
            "engaged_stud_axis_xy_mm": [36, 0],
            "unused_upper_stud_axis_xy_mm": [-36, 0],
            "joint_behavior": "The lower stud enters the upper hole. The upper stud points away from the lower hole; the rear strap retains the bundle. One round stud does not constrain rotation about its axis.",
            "first_winder_translation_mm": [0, 11, 0],
            "second_winder_rotation_axis": "Z", "second_winder_rotation_degrees": 180,
            "second_winder_translation_mm": [0, -11, 5], "contact_plane_z_mm": 5,
            "seated_intersection_mm3": initial_overlap,
            "unsupported_fit_reason": ("The tight-clearance variant's bottom socket chamfer intersects the unchanged stud root in this packing orientation." if has_interference else None),
            "mating_frame_engagement_mm": 5, "post_protrusion_mm": protrusion,
            "contact_after_0p02mm_lowering_mm3": contact,
            "native_tie_opening_clearance_box_mm": [14, 3, 5],
            "lateral_alignment_samples": lateral, "separation_samples": separation,
            "outward_extraction_samples": outward,
            "outward_extraction_direction": "Translate the flipped winder in -Y after full vertical disengagement.",
            "full_disengagement_distance_mm": height+.25}


def coupon_interfaces(coupon, winder):
    pieces = sorted(coupon.split(only_watertight=False), key=lambda mesh: mesh.centroid[1])
    require(len(pieces) == 2, "Fit coupon must contain two identical original-station carriers")
    normalized = [moved(piece, [0, -y, 0]) for piece, y in zip(pieces, [0, 18])]
    identical = symmetric_difference(*normalized)
    require(identical < .02, "Coupon halves are not identical")
    comparisons = []
    for x, kind in [(36, "stud_root_and_frame"), (-36, "socket_and_relief")]:
        region = moved(trimesh.creation.cylinder(radius=4.4, height=13.2, sections=96),
                       [x, -11, 6.5])
        reference = trimesh.boolean.intersection([winder, region], engine="manifold")
        sample = trimesh.boolean.intersection([normalized[0], region], engine="manifold")
        difference = symmetric_difference(reference, sample)
        require(difference < .02, f"Coupon {kind} differs from production interface")
        comparisons.append({"interface": kind, "axis_xy_mm": [x, -11],
                            "symmetric_difference_mm3": difference})
    return {"identical_halves_symmetric_difference_mm3": identical,
            "matches_printed_interfaces": comparisons,
            "spine_joint": winder_joint(normalized[0], 3)}


def hardware_expression(seat, terminal_x=7):
    """Independent schematic BNC and M3 dimensions, in the crosswise center pose."""
    return f"""
module yc(d,h) {{ rotate([-90,0,0]) cylinder(d=d,h=h); }}
translate([18,7,{seat}]) rotate([0,0,90]) translate([0,-21,0]) {{
    translate([0,-11.9,14]) yc(12.7,11.9);
    translate([0,3,14]) yc(9.7,7);
    translate([0,10,14]) yc(2,5);
    translate([0,3,14]) yc(18,2);
    for(x=[{-terminal_x},{terminal_x}]) {{
        translate([x,21,-2.4]) cylinder(d=5.5,h=2.4);
        translate([x,21,4]) cylinder(d=3,h=9.6);
        translate([x,21,4]) cylinder(d=7,h=1);
        translate([x,21,7]) cylinder(d=6,h=2.4,$fn=6);
    }}
}}
"""


def strap_expression(seat, bottom, slot_x, wing_length):
    """Rear-only strap independently follows narrow slots and clears coil ends."""
    outside = 11+wing_length+5+2
    return f"""
for(side=[-1,1]) {{
    slot_y=7+side*{slot_x};
    outside_y=side*{outside};
    translate([11.65,slot_y-1,{seat-2}]) cube([12.7,2,8]);
    translate([11.65,min(slot_y,outside_y)-1,{seat-2}])
        cube([12.7,abs(slot_y-outside_y)+2,2]);
    translate([11.65,outside_y-1,{bottom}]) cube([12.7,2,{seat-bottom}]);
}}
translate([11.65,{-outside-1},{bottom}]) cube([12.7,{2*outside+2},2]);
"""


def coil_tie_expression(bulge):
    """Independent native-winder coil tie and its 8 mm closure button."""
    return f"""
module segment(a,b) {{
    hull() for(p=[a,b]) translate(p)
        rotate([0,90,0]) cylinder(d=2,h=12,center=true,$fn=24);
}}
loop=[[0,-3.6,{6+bulge}],[0,20,{6+bulge}],
      [0,20,{-bulge-1}],[0,-3.6,{-bulge-1}],[0,-3.6,{6+bulge}]];
for(i=[0:len(loop)-2]) segment(loop[i],loop[i+1]);
translate([0,17,{-bulge-3}]) cylinder(d=8,h=2);
"""


def wire_reserves(winder, bulge, wing_length, edge=5):
    native = block([winder.bounds[0, 0]-edge, -edge, -bulge],
                   [winder.bounds[1, 0]+edge, wing_length+edge, 5+bulge])
    return placed_winders(native)


def assembly_checks(directory, name, center, winder, definitions, bulge,
                    protrusion=3, wing_length=37.5, compare_modules=False,
                    allow_root_interference=False, terminal_x=7):
    slot_x = 41
    outside_y = 11+wing_length+5+2
    seat = packing_height(bulge, protrusion)
    strap_bottom = -max(bulge, protrusion)-6
    centered = placed_center(center, bulge, protrusion)
    winders = placed_winders(winder)
    for w in winders:
        clear(centered, w, "Crosswise center intersects a winder")
    # The center has no peg engagement. Its illustrated height leaves room for
    # the rear strap above the higher coil reserve. It can lift freely.
    lifts = []
    for lift in [0, .05, .25, 1, 3, 8, 15]:
        value = max(clear(moved(centered, [0, 0, lift]), w,
                          "Released center cannot lift clear") for w in winders)
        lifts.append({"lift_mm": lift, "maximum_winder_intersection_mm3": value})
    hardware = expression_export(directory, f"{name}-hardware", hardware_expression(seat, terminal_x))
    strap = expression_export(directory, f"{name}-strap", strap_expression(seat, strap_bottom, slot_x, wing_length))
    require(len(strap.split(only_watertight=False)) == 1, "Rear strap proxy must be one continuous rear route")
    strap_printed = {
        "center_mm3": clear(centered, strap, "Rear tie does not clear center-end slots"),
        "winders_mm3": [clear(w, strap, "Rear tie intersects a winder") for w in winders],
        "hardware_mm3": clear(hardware, strap, "Rear tie intersects schematic hardware")}
    native_coil_tie = expression_export(directory, f"{name}-coil-tie", coil_tie_expression(bulge))
    coil_ties = placed_winders(native_coil_tie)
    back_button_clearance = (-bulge-3)-(strap_bottom+2)
    require(back_button_clearance >= 1-TOL,
            "Rear strap must pass at least 1 mm below the lower coil-tie closure button")
    reserves = wire_reserves(winder, bulge, wing_length)
    reserve_overlap = clear(*reserves, "Opposite-side wire reserves overlap")
    reserve_xy_gap = float(reserves[0].bounds[0, 1]-reserves[1].bounds[1, 1])
    require(abs(reserve_xy_gap-12) < TOL, "Expected 12 mm between opposite-side wire reserves")
    proxies = {
        "wire_reserve_to_wire_reserve_mm3": [reserve_overlap],
        "center_to_wire_reserve_mm3": [overlap(centered, reserve) for reserve in reserves],
        "hardware_to_winders_mm3": [clear(hardware, w, "Schematic hardware overlaps a winder")
                                     for w in winders],
        "hardware_to_wire_reserve_mm3": [overlap(hardware, reserve) for reserve in reserves],
        "rear_tie_to_wire_reserve_mm3": [overlap(strap, reserve) for reserve in reserves],
        "rear_tie_to_coil_ties_mm3": [clear(strap, tie, "Rear strap intersects a coil tie or its closure button")
                                      for tie in coil_ties],
        "center_to_coil_ties_mm3": [overlap(centered, tie) for tie in coil_ties],
        "hardware_to_coil_ties_mm3": [overlap(hardware, tie) for tie in coil_ties],
        "assumptions": "Schematic BNC/M3 hardware and a 12.7 mm wide, 2 mm thick rear tie routed outward below the narrow center before passing behind both winders. Rectangular wire reserves describe packing space, not individual turns. The Z-axis half-turn nests the spines with winding sections on opposite sides and a 12 mm XY gap between reserves. Independent coil ties include a 12 mm wide, 2 mm thick loop and an 8 mm diameter, 2 mm thick closure button. Some nominal tie edges touch without intersecting; actual bending and closure clearance need a physical check. One lower stud engages the upper hole. The center is shown in a flat packing pose; nominal proxy clearance does not establish physical winding capacity, hardware fit, comfort or retention."}
    notes = []
    for key, values in proxies.items():
        if key == "assumptions":
            continue
        for index, value in enumerate(values):
            if value >= EPS_VOLUME:
                notes.append({"check": key, "winder": index+1, "intersection_mm3": value,
                              "meaning": "Schematic load overlap; check actual winding, tie routing and hardware."})
    proxies["status"] = "loaded_fit_not_passed" if notes else "no_proxy_intersections"
    proxies["fit_notes"] = notes
    module_comparisons = {}
    if compare_modules:
        placed = expression_export(directory, f"{name}-placed-center", "placed_center();", definitions)
        error = symmetric_difference(placed, centered)
        require(error < .02, "Placed center module differs from independent crosswise transform")
        module_comparisons["center_symmetric_difference_mm3"] = error
        placed_strap = expression_export(directory, f"{name}-model-strap", "rear_strap();", definitions)
        error = symmetric_difference(placed_strap, strap)
        require(error < .02, "Rear strap module differs from the independently checked rear route")
        module_comparisons["rear_strap_symmetric_difference_mm3"] = error
        module_comparisons["coil_tie_symmetric_difference_mm3"] = []
        for row, expected in zip([1, -1], coil_ties):
            placed = expression_export(directory, f"{name}-model-coil-tie-{row}",
                                       f"use <{HERE / 'mockups.scad'}>\ncoil_strap(row={row});", definitions)
            error = symmetric_difference(placed, expected)
            require(error < .02, "Coil-tie preview differs from independently checked geometry")
            module_comparisons["coil_tie_symmetric_difference_mm3"].append(error)
        module_comparisons["winder_symmetric_difference_mm3"] = []
        for row, expected in zip([1, -1], winders):
            placed = expression_export(directory, f"{name}-placed-winder-{row}",
                                       f"placed_winder(row={row});", definitions)
            error = symmetric_difference(placed, expected)
            require(error < .02, "Placed winder module differs from independent spine-to-spine transform")
            module_comparisons["winder_symmetric_difference_mm3"].append(error)
    combined = trimesh.util.concatenate([centered, *winders])
    return {"spine_winder_joint": winder_joint(winder, protrusion, allow_root_interference),
            "opposite_side_wire_reserve_gap_mm": reserve_xy_gap,
            "center_rotation_degrees": 90, "center_underside_z_mm": seat,
            "center_xy_translation_mm": [18, 7],
            "center_pose": "Representative flat packing pose with at least 2 mm for the rear strap over the higher wire reserve; no printed center-to-winder locating holes or asserted frame contacts.",
            "center_release_lift_samples": lifts,
            "rear_tie": {"route": "From each narrow center-end slot, outward under the center above the coils, around both coil ends, and across the back; no front wrap.",
                         "width_mm": 12.7, "thickness_mm": 2,
                         "nominal_centerline_length_before_closure_mm": (2*outside_y+2*(seat-strap_bottom-2)
                                                                                 +2*(outside_y-slot_x)+14),
                         "outside_turn_y_mm": [-outside_y, outside_y],
                         "under_center_horizontal_run_z_mm": seat-1,
                         "slot_axes_assembled_xy_mm": [[18, 7-slot_x], [18, 7+slot_x]],
                         "rear_centerline_z_mm": strap_bottom+1,
                         "lower_coil_tie_button_gap_mm": back_button_clearance,
                         "printed_part_intersections": strap_printed},
            "assembly_module_comparisons": module_comparisons,
            "load_proxies": proxies, "bare_assembly_size_mm": combined.extents.tolist()}


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    inputs = [SCAD, HERE / "mockups.scad", HERE / "native_profile.scad", HERE / "winder_profile.scad", ORIGINAL,
              HERE.parent / "dipole_winder/frame_bevel.scad", Path(__file__),
              ROOT / ".mise/tasks/nesting-dipole/check"]

    def hashes():
        return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in inputs}

    initial_hashes = hashes()
    report = {
        "status": "running",
        "passed_scope": "Printable meshes, independently checked center holes and end pads, preserved raised center geometry and original winder geometry, spine-to-spine packing with one engaged stud, opposite-side wire reserves, separation, two center-end tie slots, and a continuous rear-only tie route that clears individual coil ties and their buttons. Unsupported tight-clearance packing and load-proxy intersections are reported separately.",
        "evidence": "Nominal CAD checks only. No physical fit, printed strength, hand comfort, retention, or wire-capacity test.",
        "presets": {}, "parameter_samples": {}, "loaded_fit_by_preset": {}, "fit_notes": [],
        "unsupported_parameter_fits": [], "center_parameter_checks": {}}
    with tempfile.TemporaryDirectory(prefix="nesting-dipole-check-") as temporary:
        directory = Path(temporary)
        original = export(directory / "original.stl", ORIGINAL, ['bnc_clearance=.20'])
        for preset, bulge in [("40m", 5), ("80m", 8)]:
            print(f"Checking {preset} crosswise nesting dipole", flush=True)
            suffix = "" if preset == "40m" else "_80m"
            definitions = [f'preset="{preset}"']
            names = [f"center{suffix}.stl", f"winder{suffix}.stl", f"print_layout{suffix}.stl"]
            with ThreadPoolExecutor(max_workers=3) as pool:
                futures = [pool.submit(export, directory/name, SCAD,
                                       definitions+[f'part="{part}"'])
                           for name, part in zip(names, ["center", "winder", "print_layout"])]
                center, winder, layout = [future.result() for future in futures]
            checks = {"center": mesh_report(center), "winder": mesh_report(winder),
                      "print_layout": mesh_report(layout, 3),
                      "center_holes_and_structure": preserved_center(original, center),
                      "preserved_winder_frame": preserved_winder_frame(directory, preset, winder, definitions),
                      "winder_socket": socket_dimensions(winder),
                      "winder_stud": post_dimensions(winder, 3),
                      "center_tie_slots": center_slots(center),
                      "layout_parts": layout_parts(layout, center, winder),
                      "assembly": assembly_checks(directory, preset, center, winder,
                                                  definitions, bulge, compare_modules=True)}
            if preset == "40m":
                reference_center, reference_winder = center, winder
            else:
                difference = symmetric_difference(reference_center, center)
                require(difference < EPS_VOLUME, "Wire presets must share the same center")
                checks["center_difference_from_40m_mm3"] = difference
                difference = symmetric_difference(reference_winder, winder)
                require(difference < EPS_VOLUME, "Wire presets must share the same winder")
                checks["winder_difference_from_40m_mm3"] = difference
            report["presets"][preset] = checks
            proxies = checks["assembly"]["load_proxies"]
            report["loaded_fit_by_preset"][preset] = {
                "status": proxies["status"], "fit_notes": proxies["fit_notes"]}
            report["fit_notes"].extend({"preset": preset, **note} for note in proxies["fit_notes"])
        coupon = export(directory / "fit_coupon.stl", SCAD, ['part="fit_coupon"'])
        report["fit_coupon"] = {**mesh_report(coupon, 2), **coupon_interfaces(coupon, reference_winder)}
        variants = [
            ("minimum_post_protrusion", ['post_protrusion=2'], 5, 2, .25, 37.5),
            ("maximum_post_protrusion_80m", ['preset="80m"', 'post_protrusion=5'], 8, 5, .25, 37.5),
            ("maximum_winder_size", ['wing_length=60', 'winding_span=200'], 5, 3, .25, 60),
            ("thin_coil_long_stud", ['wire_face_bulge=2', 'post_protrusion=5'], 2, 5, .25, 37.5),
            ("tightest_docking_fit", ['alignment_clearance=.15'], 5, 3, .15, 37.5),
            ("loosest_docking_fit", ['alignment_clearance=.4'], 5, 3, .4, 37.5),
        ]
        for name, definitions, bulge, protrusion, clearance, wing_length in variants:
            print(f"Checking {name}", flush=True)
            center = export(directory / f"{name}-center.stl", SCAD, definitions+['part="center"'])
            winder = export(directory / f"{name}-winder.stl", SCAD, definitions+['part="winder"'])
            report["parameter_samples"][name] = {
                "definitions": definitions, "center": mesh_report(center), "winder": mesh_report(winder),
                "preserved_winder_frame": preserved_winder_frame(directory, name, winder, definitions),
                "winder_stud": post_dimensions(winder, protrusion),
                "winder_socket": socket_dimensions(winder, clearance),
                "center_tie_slots": center_slots(center),
                "assembly": assembly_checks(directory, name, center, winder, definitions,
                                            bulge, protrusion, wing_length,
                                            allow_root_interference=(clearance < .25))}
            joint = report["parameter_samples"][name]["assembly"]["spine_winder_joint"]
            if joint["status"] != "passed":
                report["unsupported_parameter_fits"].append({
                    "variant": name, "status": joint["status"],
                    "reason": joint["unsupported_fit_reason"],
                    "seated_intersection_mm3": joint["seated_intersection_mm3"]})
        print("Checking coupled center-hole parameters", flush=True)
        name = "alternative_terminal_and_wire_spacing"
        definitions = ['terminal_hole_x=10', 'wire_hole_inner_x=28', 'wire_hole_pitch=4',
                       'wire_hole_d=2.6', 'wire_chamfer=0', 'hang_hole_d=6']
        alternate = export(directory / f"{name}.stl", SCAD, definitions+['part="center"'])
        report["center_parameter_checks"][name] = {
            "definitions": definitions, "center": mesh_report(alternate),
            "center_holes_and_structure": preserved_center(original, alternate, terminal_x=10,
                                                            wire_inner=28, wire_pitch=4,
                                                            wire_d=2.6, chamfer=0, hang_d=6),
            "center_tie_slots": center_slots(alternate),
            "assembly": assembly_checks(directory, name, alternate, reference_winder,
                                        definitions, 5, terminal_x=10)}
        rejected = [
            ("wide_slot_without_wire_adjustment", ['strap_slot_thickness=4'],
             "outer wire-hole mouth and strap slot"),
            ("outward_terminal_without_wire_adjustment", ['terminal_hole_x=8'],
             "Panduit barrel entry and wire-hole chamfer"),
            ("outward_wire_group_without_slot_adjustment", ['wire_hole_inner_x=26'],
             "outer wire-hole mouth and strap slot"),
        ]
        for name, definitions, message in rejected:
            report["center_parameter_checks"][name] = rejected_export(directory, name, definitions, message)
        require(hashes() == initial_hashes, "Inputs changed during validation; rerun the check")
        report["print_file_updates"] = {}
        for name in PRINT_FILES:
            existing, generated = HERE / name, directory / name
            if existing.exists():
                old, fresh = trimesh.load_mesh(existing), trimesh.load_mesh(generated)
                difference = symmetric_difference(old, fresh)
                if (old.is_watertight and old.is_winding_consistent and old.volume > 0
                        and np.allclose(old.bounds, fresh.bounds, atol=TOL)
                        and difference < EPS_VOLUME):
                    report["print_file_updates"][name] = {
                        "status": "preserved_existing_bytes",
                        "fresh_export_symmetric_difference_mm3": difference}
                    continue
            shutil.copyfile(generated, existing)
            report["print_file_updates"][name] = {"status": "updated"}
    report["input_sha256"] = initial_hashes
    report["output_sha256"] = {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                               for name in PRINT_FILES}
    report["status"] = "passed"
    (HERE / "validation.json").write_text(json.dumps(report, indent=2)+"\n")
    print("Verified six printable STLs and wrote validation.json (passed)", flush=True)
    for note in report["unsupported_parameter_fits"]:
        print(f"Unsupported packed fit: {note['variant']} ({note['seated_intersection_mm3']:.6f} mm³ root interference)", flush=True)
    for preset, fit in report["loaded_fit_by_preset"].items():
        print(f"{preset} schematic loaded fit: {fit['status']}", flush=True)
        for note in fit["fit_notes"]:
            print(f"  {note['check']} (winder {note['winder']}): {note['intersection_mm3']:.3f} mm³", flush=True)


if __name__ == "__main__":
    main()
