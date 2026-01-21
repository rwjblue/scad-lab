#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/generate_luggage_tag.sh --first "First" --last "Last" --phone "+123" --email "you@example.com" [--stl-out path.stl]

Generates models/luggage_tag/luggage_tag_user.scad with your personal info and includes the base model.
Also renders an STL via the OpenSCAD CLI.
EOF
}

first=""
last=""
phone=""
email=""
out="models/luggage_tag/luggage_tag_user.scad"
stl_out=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --first) first="${2:-}"; shift 2;;
    --last) last="${2:-}"; shift 2;;
    --phone) phone="${2:-}"; shift 2;;
    --email) email="${2:-}"; shift 2;;
    --out) out="${2:-}"; shift 2;;
    --stl-out) stl_out="${2:-}"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1;;
  esac
done

if [[ -z "$first" || -z "$last" || -z "$phone" || -z "$email" ]]; then
  echo "All fields are required." >&2
  usage
  exit 1
fi

FIRST="$first" LAST="$last" PHONE="$phone" EMAIL="$email" OUT="$out" python - <<'PY'
import json
import os
import sys

first = os.environ["FIRST"]
last = os.environ["LAST"]
phone = os.environ["PHONE"]
email = os.environ["EMAIL"]
out = os.environ["OUT"]

def scad_str(value: str) -> str:
    # JSON encoding gives us a safely-escaped double-quoted string.
    return json.dumps(value)

os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    f.write("// Auto-generated. Do not edit.\n")
    f.write("LUGGAGE_TAG_NO_AUTORUN = true;\n")
    f.write('include <luggage_tag.scad>;\n')
    f.write("luggage_tag(\n")
    f.write(f"  first_name={scad_str(first)},\n")
    f.write(f"  last_name={scad_str(last)},\n")
    f.write(f"  phone_number={scad_str(phone)},\n")
    f.write(f"  email_address={scad_str(email)}\n")
    f.write(");\n")
PY

if ! command -v openscad >/dev/null 2>&1; then
  echo "openscad is not installed or not on PATH. Install OpenSCAD CLI first." >&2
  exit 1
fi

if [[ -z "$stl_out" ]]; then
  stl_out="${out%.scad}.stl"
fi

mkdir -p "$(dirname "$stl_out")"
openscad -o "$stl_out" "$out"
