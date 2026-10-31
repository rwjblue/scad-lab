#!/usr/bin/env python3
"""Render the four shared-center variants from their printable geometry."""
from pathlib import Path
import json
import subprocess

HERE = Path(__file__).resolve().parent
for balun, straps, suffix in [(False, False, ""), (False, True, "_with_straps"),
                              (True, False, "_with_balun"),
                              (True, True, "_with_balun_and_straps")]:
    path = HERE / ("preview"+suffix+".png")
    command = ["openscad", "--hardwarnings", "--render=true", "-o", str(path),
               "--imgsize=1300,1250", "--camera=135,-165,235,0,38,4",
               "--projection=o", "--viewall", "--autocenter", "--colorscheme=Tomorrow",
               "-D", f"balun_mount={json.dumps(balun)}",
               "-D", f"strap_slots={json.dumps(straps)}", str(HERE / "dipole_center.scad")]
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0 and "ERROR:" not in result.stderr and "WARNING:" not in result.stderr, result.stderr
    print(path.name, flush=True)
