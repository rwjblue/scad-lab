"""Geometry checks shared by the modular dipole validator and audits.

These helpers inspect exported CAD; they do not predict printed forces or life.
"""
from __future__ import annotations

from pathlib import Path
import subprocess

import numpy as np
import trimesh
from shapely.geometry import Polygon, Point

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ORIGINAL = HERE.parent / "dipole_center/dipole_center.scad"
TOL = 0.025


def require(condition, explanation):
    if not condition:
        raise AssertionError(explanation)


def export(path, source, definitions=()):
    command = ["openscad", "--backend=Manifold", "--hardwarnings", "--export-format=binstl"]
    for definition in definitions:
        command += ["-D", definition]
    command += ["-o", str(path), str(source)]
    result = subprocess.run(command, text=True, capture_output=True)
    require(result.returncode == 0 and path.exists(),
            f"OpenSCAD export failed: {command}\n{result.stdout}\n{result.stderr}")
    require("ERROR:" not in result.stderr and "WARNING:" not in result.stderr,
            result.stderr)
    return trimesh.load_mesh(path)


def sections(mesh, z):
    section = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    require(section is not None, f"No cross section at Z={z}")
    material = Polygon()
    for contour in section.discrete:
        require(np.linalg.norm(contour[0] - contour[-1]) < TOL, "Open section contour")
        polygon = Polygon(contour[:, :2])
        require(polygon.is_valid, "Invalid section polygon")
        material = material.symmetric_difference(polygon)
    return material


def mesh_report(mesh, expected_components=1):
    count = len(mesh.split(only_watertight=False))
    require(mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0,
            "Mesh must have positive volume, consistent normals and be watertight")
    require(count == expected_components,
            f"Expected {expected_components} connected solids; got {count}")
    require(abs(mesh.bounds[0, 2]) < TOL, "Printable part does not start at Z=0")
    return {"watertight": bool(mesh.is_watertight), "connected_solids": count,
            "bounds_mm": mesh.bounds.tolist(), "size_mm": mesh.extents.tolist(),
            "volume_mm3": float(mesh.volume),
            "estimated_solid_petg_g_at_1p27": float(mesh.volume * 0.00127)}


def volume(mesh):
    if mesh is None or len(mesh.faces) == 0:
        return 0.0
    # A zero-volume Boolean boundary has an undefined center of mass; only
    # its volume is used here, never that derived center-of-mass value.
    with np.errstate(divide="ignore", invalid="ignore"):
        return abs(float(mesh.volume))


def intersection_volume(a, b):
    return volume(trimesh.boolean.intersection([a, b], engine="manifold"))


def translated(mesh, vector):
    result = mesh.copy()
    result.apply_translation(vector)
    return result


def bounds_mesh(low, high):
    low, high = np.asarray(low), np.asarray(high)
    result = trimesh.creation.box(extents=high-low)
    result.apply_translation((low+high)/2)
    return result


def check_center_holes(original, revised):
    """Additive geometry must not plug even the mouths of existing holes."""
    worst = 0.0
    for z in [0.1, 0.3, 0.6, 2, 3.4, 3.7, 3.9]:
        old = sections(original, z)
        new = sections(revised, z)
        require(old.geom_type == "Polygon", "Original center section disconnected")
        require(len(old.interiors) == 9, "Expected nine Z-axis holes in original center")
        for ring in old.interiors:
            occlusion = new.intersection(Polygon(ring)).area
            worst = max(worst, occlusion)
            require(occlusion < 0.001, f"Center addition plugs an original hole at Z={z}")
    return {"z_axis_holes_preserved": 9, "sections_checked": 7,
            "maximum_added_material_in_hole_mm2": worst}


def check_bnc_cutout(mesh):
    """Measure the requested 10.1 mm D-hole in actual exported X/Z sections."""
    measured=[]
    for y in [0.1,1.5,2.9]:
        section=mesh.section(plane_origin=[0,y,0],plane_normal=[0,1,0])
        require(section is not None,"Missing BNC panel section")
        material=Polygon()
        for contour in section.discrete:
            require(np.linalg.norm(contour[0]-contour[-1])<TOL,"Open BNC section contour")
            polygon=Polygon(contour[:,[0,2]])
            require(polygon.is_valid,"Invalid BNC section polygon")
            material=material.symmetric_difference(polygon)
        shapes=[material] if material.geom_type=="Polygon" else list(material.geoms)
        holes=[Polygon(ring) for shape in shapes for ring in shape.interiors
               if Polygon(ring).covers(Point(0,14))]
        require(len(holes)==1,"BNC cutout must be one enclosed hole")
        x0,z0,x1,z1=holes[0].bounds
        require(abs((x1-x0)-10.1)<TOL,"BNC diameter is not 10.1 mm")
        require(abs((z1-z0)-9.25)<TOL,"BNC flat-to-opposite-edge span is not 9.25 mm")
        require(abs(z1-18.2)<TOL,"BNC flat is not at the top of the hole")
        measured.append({"panel_y_mm":y,"diameter_mm":x1-x0,
                         "flat_to_opposite_edge_mm":z1-z0,"top_flat_z_mm":z1})
    return {"clearance_per_side_mm":0.2,"section_measurements":measured}
