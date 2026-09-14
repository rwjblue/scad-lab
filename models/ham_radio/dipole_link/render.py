#!/usr/bin/env python3
"""Render actual link geometry and schematic wire/connector assemblies.

Requires OpenSCAD on PATH. The three PNGs are intended for documentation and
the Printables gallery; second-color lettering depicts the optional flush mode.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
VIEWS = [
    ("in_use.png", "in_use", "28,-58,155,0,-3,0", "1800,1400"),
    ("print_layout.png", "print_layout", "20,-60,180,0,0,0", "1600,1000"),
    ("all_bands.png", "all_bands", "12,-50,240,0,0,0", "1200,1600"),
]


def render(config):
    filename, view, camera, size = config
    layout = "full" if view == "all_bands" else "starter"
    output = HERE / "images" / filename
    command = [
        "openscad", "--backend=Manifold", "--hardwarnings",
        "-o", str(output), f"--imgsize={size}", f"--camera={camera}",
        "--projection=o", "--viewall", "--autocenter", "--colorscheme=Tomorrow",
        "-D", f'view="{view}"', "-D", f'layout="{layout}"',
        str(HERE / "mockups.scad"),
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=180)
    if result.returncode or "WARNING:" in result.stderr or "ERROR:" in result.stderr:
        raise RuntimeError(result.stdout + result.stderr)
    if not output.exists():
        raise RuntimeError(f"OpenSCAD did not produce {output}")
    return output.relative_to(HERE)


if __name__ == "__main__":
    (HERE / "images").mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        for filename in pool.map(render, VIEWS):
            print(filename, flush=True)
