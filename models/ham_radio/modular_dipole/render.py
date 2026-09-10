#!/usr/bin/env python3
"""Render the modular dipole model and the verified sequential-release poses."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import json
import sys

HERE = Path(__file__).resolve().parent
VIEWS = [
    ("images/assembled.png", "mockups.scad", ['view="assembled"'], "170,-230,250,0,0,5"),
    ("images/loaded.png", "mockups.scad", ['view="loaded"'], "170,-230,210,0,0,5"),
    ("images/exploded.png", "mockups.scad", ['view="exploded"'], "170,-230,250,0,0,0"),
    ("images/print_layout.png", "modular_dipole.scad", ['part="print_layout"'], "170,-250,300,0,20,0"),
    ("images/retention_coupon.png", "modular_dipole.scad", ['part="retention_coupon"'], "80,-100,130,0,10,0"),
]


def render(config):
    filename, source, definitions, camera = config
    command = ["openscad", "--backend=Manifold", "--hardwarnings", "-o", str(HERE / filename),
               "--imgsize=1600,1200", f"--camera={camera}", "--projection=o",
               "--viewall", "--autocenter", "--colorscheme=Tomorrow"]
    if source == "modular_dipole.scad":
        command += ["--render"]
    for definition in definitions:
        command += ["-D", definition]
    validation = HERE / "validation.json"
    if validation.exists():
        report = json.loads(validation.read_text())
        if report.get("status") in ("passed", "passed_with_fit_caveats"):
            pose = report["presets"]["40m"]["sequential_release"]["orders"][0]
            command += ["-D", f'park_angle={pose["parked_angle_deg"]:.8f}']
    result = subprocess.run(command + [str(HERE / source)], text=True, capture_output=True)
    if result.returncode or "ERROR:" in result.stderr or "WARNING:" in result.stderr:
        raise RuntimeError(result.stdout + result.stderr)
    return filename


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=3) as pool:
        for filename in pool.map(render, VIEWS):
            print(filename, flush=True)
    # The annotated diagram uses actual projections and a schematic side view.
    command = [sys.executable, str(HERE / "review/generate_explainer.py")]
    if sys.platform == "darwin":
        command.append("--png")
    subprocess.run(command, check=True)
