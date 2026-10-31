#!/usr/bin/env python3
"""Render the actual default printable part and schematic assembly references."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
VIEWS = [
    ("preview.png", "toroid_dipole_winder.scad", [], "150,-220,290,0,0,0"),
    ("assembly.png", "mockups.scad", [], "150,-220,290,0,0,0"),
    ("front.png", "mockups.scad", [], "0,0,300,0,0,0"),
    ("side.png", "mockups.scad", [], "280,0,7,0,0,7"),
    ("loaded.png", "mockups.scad", ['view="loaded"'], "150,-220,290,0,0,0"),
    ("winding.png", "mockups.scad", ['view="core"'], "40,-55,75,0,0,0"),
]

def render(config):
    filename, source, definitions, camera = config
    command = ["openscad", "--hardwarnings", "-o", str(HERE / filename),
               "--imgsize=1400,1600", f"--camera={camera}", "--projection=o",
               "--viewall", "--autocenter", "--colorscheme=Tomorrow"]
    for definition in definitions:
        command += ["-D", definition]
    if source == "toroid_dipole_winder.scad":
        command += ["--render=true"]
    process = subprocess.run(command + [str(HERE / source)], capture_output=True, text=True)
    if process.returncode or "WARNING:" in process.stderr or "ERROR:" in process.stderr:
        raise RuntimeError(process.stdout + process.stderr)
    return filename

if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=3) as pool:
        for filename in pool.map(render, VIEWS):
            print(filename, flush=True)
