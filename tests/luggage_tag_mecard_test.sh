#!/usr/bin/env bash
set -euo pipefail

python3 - "$(cd "$(dirname "$0")/.." && pwd)" <<'PY'
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(sys.argv[1])
model = root / "models/luggage_tag/luggage_tag.scad"
cases = [
    (
        ["Ada", "Lovelace", "+1 (202) 555-0101", "ada@example.com", "+12025550101"],
        "MECARD:N:Lovelace,Ada;TEL:+12025550101;EMAIL:ada@example.com;;",
    ),
    (
        ["Grace", "Hopper", "+1 (202) 555-0102", "grace@example.net", "+12025550102"],
        "MECARD:N:Hopper,Grace;TEL:+12025550102;EMAIL:grace@example.net;;",
    ),
    (
        ["Ada", "Lovelace", "+12025550101", "", ""],
        "MECARD:N:Lovelace,Ada;TEL:+12025550101;;",
    ),
    (
        ["Ada;A", "Love:lace\\", "+12025550101", "ada@example.com", ""],
        "MECARD:N:Love\\:lace\\\\,Ada\\;A;TEL:+12025550101;EMAIL:ada@example.com;;",
    ),
    (
        ["Ada\n", "Lovelace\r", "+12025550101", "ada@example.com", ""],
        "MECARD:N:Lovelace,Ada;TEL:+12025550101;EMAIL:ada@example.com;;",
    ),
]


def run(command, **kwargs):
    result = subprocess.run(command, capture_output=True, text=True, **kwargs)
    diagnostics = result.stdout + result.stderr
    if result.returncode or any(
        line.startswith(("ERROR:", "WARNING:")) for line in diagnostics.splitlines()
    ):
        raise AssertionError(f"{command[0]} failed:\n{diagnostics}")
    return result


with tempfile.TemporaryDirectory(prefix="luggage-tag-mecard-") as directory:
    temp = Path(directory)
    probe = temp / "probe.scad"
    lines = [
        "LUGGAGE_TAG_NO_AUTORUN = true;",
        f"include <{model}>;",
    ]
    for index, (values, expected) in enumerate(cases):
        arguments = ", ".join(json.dumps(value) for value in values)
        lines += [
            f"message_{index} = luggage_tag_qr_message({arguments});",
            f"assert(message_{index} == {json.dumps(expected)}, "
            f'"Unexpected MeCard payload in case {index}");',
        ]
        if index < 2:
            first, last, phone, email, _ = map(json.dumps, values)
            lines += [
                f'size_{index} = qr_size(message_{index}, error_correction="L");',
                f'assert(size_{index} == 33, "Unexpected QR density");',
                f"vcard_{index} = qr_vcard(lastname={last}, firstname={first}, "
                f"phone={phone}, email={email});",
                f'assert(size_{index} < qr_size(vcard_{index}, error_correction="L"), '
                '"MeCard must use fewer modules than the previous vCard");',
            ]
    lines.append("cube([1, 1, 1]);")
    probe.write_text("\n".join(lines) + "\n")
    run(["openscad", "-o", str(temp / "probe.stl"), str(probe)])

    wrapper = temp / "generated.scad"
    output = temp / "tag.stl"
    env = os.environ.copy()
    env["OPENSCADPATH"] = str(model.parent) + os.pathsep + env.get("OPENSCADPATH", "")
    run(
        [
            "bash", str(root / "scripts/generate_luggage_tag.sh"),
            "--first", "Ada",
            "--last", "Lovelace",
            "--phone", "+1 (202) 555-0101",
            "--email", "ada@example.com",
            "--out", str(wrapper),
            "--stl-out", str(output),
        ],
        cwd=root,
        env=env,
    )
    generated = wrapper.read_text()
    assert 'phone_number="+1 (202) 555-0101"' in generated
    assert 'qr_phone_number="+12025550101"' in generated
    assert output.stat().st_size > 84, "The generated tag STL is empty"

print("PASS: five MeCard payload cases, smaller 33-module QR codes, and generated tag STL")
PY
