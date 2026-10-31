#!/usr/bin/env python3
"""Render the printable CAD, exact winding routes, and reference hardware."""
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
VIEWS = [
    ("preview.png", "balun_dipole_center.scad", "135,-165,235,0,38,4"),
    ("assembly.png", "mockups.scad", "135,-165,235,0,38,4"),
    ("assembly_cutaway.png", "mockups.scad", "135,-165,235,0,38,4"),
    ("front.png", "mockups.scad", "0,38,250,0,38,0"),
    ("side.png", "mockups.scad", "240,38,10,0,38,10"),
    ("winding_guide.png", "winding_guide.scad", "42,-60,64,0,0,7"),
    ("winding_debug.png", "winding_guide.scad", "0,0,110,0,0,0"),
    ("winding_side.png", "winding_guide.scad", "65,-85,40,0,0,7"),
    ("winding_cutaway.png", "winding_guide.scad", "65,-85,40,0,0,7"),
    ("winding_print.png", "winding_guide.scad", "45,-60,65,0,0,7"),
]

for name, source, camera in VIEWS:
    command = ["openscad", "--hardwarnings", "-o", str(HERE / name),
               "--imgsize=1300,1250", f"--camera={camera}", "--projection=o",
               "--viewall", "--autocenter", "--colorscheme=Tomorrow"]
    if source == "winding_guide.scad":
        view = {"winding_guide.png":"guide", "winding_debug.png":"debug",
                "winding_cutaway.png":"cutaway", "winding_print.png":"print"}.get(name,"wound")
        command += ["-D", f'view="{view}"']
    if name == "assembly_cutaway.png":
        command += ["-D", 'view="cutaway"']
    if name in {"preview.png", "winding_guide.png", "winding_print.png"}:
        command += ["--render=true", "--backend=Manifold"]
    result = subprocess.run(command + [str(HERE / source)], capture_output=True, text=True)
    if result.returncode or "WARNING:" in result.stderr or "ERROR:" in result.stderr:
        raise RuntimeError(result.stdout + result.stderr)
    print(name, flush=True)
