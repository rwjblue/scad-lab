#!/usr/bin/env bash
set -euo pipefail

# Example: render the M3 spacer to STL using the OpenSCAD CLI.
# Adjust or expand this script as you add more models.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

openscad \
  -o "${REPO_ROOT}/models/mechanical/spacer_m3/spacer_m3.stl" \
  "${REPO_ROOT}/models/mechanical/spacer_m3/spacer_m3.scad"
