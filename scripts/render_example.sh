#!/usr/bin/env bash
set -euo pipefail

# Example: render the M3 spacer to STL using the OpenSCAD CLI.
# Adjust or expand this script as you add more models.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if ! command -v openscad >/dev/null 2>&1; then
  echo "openscad is not installed or not on PATH. Install OpenSCAD CLI first." >&2
  exit 1
fi

openscad \
  -o "${REPO_ROOT}/models/mechanical/spacer_m3/spacer_m3.stl" \
  "${REPO_ROOT}/models/mechanical/spacer_m3/spacer_m3.scad"

openscad \
  -o "${REPO_ROOT}/models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap_ultra_v1_6.stl" \
  "${REPO_ROOT}/models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad"

openscad -D 'model="V1_3"' \
  -o "${REPO_ROOT}/models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap_v1_3.stl" \
  "${REPO_ROOT}/models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad"
