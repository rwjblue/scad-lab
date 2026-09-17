#!/usr/bin/env python3
"""Render actual nesting-dipole geometry for assembly and printing previews."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
VIEWS = [
    ("center", "nesting_dipole.scad", 'part="center"', "0,21,180,0,21,0"),
    ("winder", "nesting_dipole.scad", 'part="winder"', "80,-120,160,0,0,0"),
    ("assembled", "mockups.scad", 'view="assembled"', "190,-240,240,0,0,10"),
    ("exploded", "mockups.scad", 'view="exploded"', "190,-240,250,0,0,20"),
    ("side", "mockups.scad", 'view="loaded"', "175,-240,75,0,0,10"),
    ("loaded", "mockups.scad", 'view="loaded"', "190,-240,240,0,0,10"),
    ("joint", "mockups.scad", 'view="joint"', "140,-200,240,0,0,5"),
    ("back", "mockups.scad", 'view="back"', "170,-230,-240,0,0,5"),
    ("print_layout", "nesting_dipole.scad", 'part="print_layout"', "0,30,300,0,30,0"),
    ("fit_coupon", "nesting_dipole.scad", 'part="fit_coupon"', "70,-100,130,0,0,0"),
]


def render(config):
    name, source, definition, camera = config
    output = HERE / "images" / f"{name}.png"
    output.parent.mkdir(exist_ok=True)
    command = ["openscad", "--backend=Manifold", "--hardwarnings",
               "--imgsize=1400,1000", f"--camera={camera}", "--projection=o",
               "--viewall", "--autocenter", "--colorscheme=Tomorrow",
               "-D", definition, "-o", str(output)]
    if source == "nesting_dipole.scad":
        command.insert(1, "--render")
    result = subprocess.run(command + [str(HERE / source)], text=True, capture_output=True)
    if result.returncode or "ERROR:" in result.stderr or "WARNING:" in result.stderr:
        raise RuntimeError(result.stdout + result.stderr)
    return output.relative_to(HERE)


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=3) as pool:
        for output in pool.map(render, VIEWS):
            print(output, flush=True)
