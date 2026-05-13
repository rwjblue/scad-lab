# Spooltenna BNC Cap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a parameterized OpenSCAD model for a 3D-printed PETG protective cap that drops into the existing BNC slot on a Spooltenna Ultra (v1.5/v1.6) wire spool antenna and is retained by the antenna's bongo tie.

**Architecture:** Single-file OpenSCAD model under `models/ham_radio/spooltenna_bnc_cap/`, parameters at the top, a `model = "ULTRA_V1_6"` preset switch that resolves a small struct of stack/slot/BNC dimensions, then a `cap()` module that builds the part as one block with a subtractive full-through axial BNC pocket, front-face circular-segment tie groove, and lead-in chamfers. Stretch preset for v1.3 wired in at the end.

**Tech Stack:** OpenSCAD (CLI + GUI), bash for the render script, PETG / FDM for the print target. No external libraries beyond `lib/rounded_cube.scad` already in this repo (and only if useful — current design doesn't strictly need it).

**Spec:** See `docs/superpowers/specs/2026-05-12-spooltenna-bnc-cap-design.md`.

---

## Resuming on another machine

This plan is fully self-contained — every parameter, every code block,
every command is spelled out below. To pick up cold:

1. Clone or pull `scad-lab` (this repo) on the new machine.
2. Read `docs/superpowers/specs/2026-05-12-spooltenna-bnc-cap-design.md`
   end to end, including the "Source references" and "Pre-print
   measurements" appendices. The source Spooltenna checkout used for
   those measurements is `/Users/rwjblue/src/github/modulo8/KO4HUI-Spooltenna`
   at commit `3699ed0`.
3. Install OpenSCAD CLI:
   - macOS: `brew install --cask openscad` (puts the GUI app at
     `/Applications/OpenSCAD.app`); add the CLI to PATH with
     `export PATH="/Applications/OpenSCAD.app/Contents/MacOS:$PATH"`
     (or `brew install openscad` for a Homebrew-managed CLI).
   - Linux: `sudo apt install openscad` or equivalent.
   - Verify: `openscad --version` exits 0.
4. (Optional but recommended) Have the physical Spooltenna Ultra and a
   set of calipers handy to confirm the values listed in the spec's
   "Pre-print measurements" table before the first print.
5. Begin with Task 1 below.

If `openscad` CLI isn't available on the target machine and won't be
soon, you can still write the SCAD file by following the code blocks in
each task and skip the render-check / STL-export steps — but **do not
mark a task complete without rendering it at least once**, otherwise
geometry bugs (a chamfer cutting the wrong face, an off-by-one in pocket
depth) won't get caught until print time.

The repo uses **jj** (`jj` not `git`) for version control. Each task
ends with `jj describe -m "<msg>"` to label the current change and
`jj new` to start a fresh empty change for the next task.

---

## File Structure

| File | Responsibility |
|---|---|
| `models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad` | The model. Parameters, preset resolution, `cap()` module, top-level render call. |
| `models/ham_radio/spooltenna_bnc_cap/README.md` | Problem statement, parameters, render/print instructions. |
| `scripts/render_example.sh` | Modify: add a render line for the new model. |

No `lib/` additions are required — the cap is a small set of cubes and chamfers.

---

## Task 1: Scaffold the model folder

**Files:**
- Create: `models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad`

- [ ] **Step 1: Create the file with a header and an empty preview render**

Write `models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad`:

```scad
/*
  models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad

  Parameterized BNC protective cap for the KO4HUI Spooltenna
  (Ultra v1.5/v1.6 primary, v1.3 stretch). Drops into the existing
  PCB slot at the bottom of the spool; held in place by the bongo tie.

  See docs/superpowers/specs/2026-05-12-spooltenna-bnc-cap-design.md
*/

$fn = 64;

// Placeholder so OpenSCAD has something to render until the cap module exists.
cube([1, 1, 1]);
```

- [ ] **Step 2: Render-check that OpenSCAD parses the file**

Run:
```bash
openscad -o /tmp/spooltenna_cap_smoke.stl \
  /Users/rwjblue/src/github/rwjblue/scad-lab/models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad
```
Expected: command exits 0; `/tmp/spooltenna_cap_smoke.stl` exists and is non-empty.

- [ ] **Step 3: Commit (jj)**

```bash
cd /Users/rwjblue/src/github/rwjblue/scad-lab
jj describe -m "spooltenna_bnc_cap: scaffold model file"
jj new
```

(This repo uses `jj`. Each task ends with `jj describe -m "<msg>"` to label the current change, then `jj new` to start a fresh empty change for the next task. If preferred, the user can squash later.)

---

## Task 2: Define parameters and the model preset switch

**Files:**
- Modify: `models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad`

- [ ] **Step 1: Replace the placeholder with the full parameter block**

Replace the entire file body (everything after the header comment) with:

```scad
$fn = 64;

// ---------------------------------------------------------------
// Model preset
// ---------------------------------------------------------------
//   "ULTRA_V1_6"  - Spooltenna Ultra v1.6 (default, identical to v1.5)
//   "ULTRA_V1_5"  - alias for ULTRA_V1_6
//   "V1_3"        - Spooltenna v1.3 (larger 120 mm disk)
model = "ULTRA_V1_6";

// ---------------------------------------------------------------
// Per-model geometry. Edit `model` above to switch presets.
// Override individual values below the preset block to customize.
// ---------------------------------------------------------------
preset_slot_width =
    (model == "V1_3")        ? 18.0  :
                               18.5;  // ULTRA_V1_5/V1_6

preset_slot_depth =
    (model == "V1_3")        ? 9.6   :
                               5.9;   // ULTRA_V1_5/V1_6

preset_disk_radius =
    (model == "V1_3")        ? 60.0  :
                               38.1;  // ULTRA_V1_5/V1_6

// All variants observed in the repo use the same horizontal Molex 73100
// BNC, with ~8 mm of bayonet protruding past the disk edge on Ultra and
// ~4.5 mm on V1_3. Bigger of the two with margin keeps one number.
preset_bnc_protrusion =
    (model == "V1_3")        ? 5.0   :
                               8.5;

// ---------------------------------------------------------------
// Parameters (override per-print as needed)
// ---------------------------------------------------------------

// Stack
inter_pcb_gap   = 15.0;    // standoff length between the two PCBs
pcb_thickness   = 1.6;     // each PCB disk thickness
pcb_slot_clear  = 0.3;     // extra Z clearance for disk-edge slots
disk_outer_wall = 1.2;     // plastic outside each PCB edge slot

// Slot (resolved from preset)
slot_width      = preset_slot_width;
slot_depth      = preset_slot_depth;
disk_radius     = preset_disk_radius;

// BNC body (Molex 73100 / Winconn 364A2x95 family)
bnc_body_w      = 9.65;    // X (circumferential)
bnc_body_h      = 13.0;    // Z (axial height inside the inter-PCB gap)
bnc_protrusion  = preset_bnc_protrusion;

// Cap geometry
clearance       = 0.5;     // X per-side clearance to the slot
wall            = 2.4;     // front wall (radial-outermost)
side_wall       = 2.5;     // circumferential side walls
lead_in_chamfer = 1.0;     // chamfer on radially-inward edges
front_air_gap   = 1.5;     // BNC tip to inside of front wall
pocket_x_clear  = 1.0;     // each-side clearance around BNC body in X
disk_slot_depth = slot_depth + 0.5;
side_glance_w   = 3.0;     // side fairing width outside each leg

// Bongo tie groove
tie_groove_w    = 4.0;
tie_groove_d    = 1.5;

// ---------------------------------------------------------------
// Derived dimensions (do not edit; expressed for readability)
// ---------------------------------------------------------------

// Cap outer footprint (X = circumferential, Y = radial, Z = axial)
cap_x = slot_width      - 2 * clearance;                  // 17.5 mm @ Ultra defaults
cap_z = inter_pcb_gap + 2 * (pcb_thickness + disk_outer_wall);  // 20.6 mm @ defaults
cap_y = slot_depth + bnc_protrusion + front_air_gap + wall;  // 18.3 mm @ Ultra defaults

// BNC pocket (interior cavity)
pocket_x = bnc_body_w + 2 * pocket_x_clear;               // 11.65 mm
pocket_y = cap_y - wall;                                  // depth from inner face
pcb_slot_h = pcb_thickness + pcb_slot_clear;

// Sanity asserts (OpenSCAD will halt with these messages on bad params)
assert(cap_x > 0,            "cap_x must be positive");
assert(cap_z > 0,            "cap_z must be positive");
assert(cap_y > 0,            "cap_y must be positive");
assert(pocket_x < cap_x - 2 * side_wall,
       "BNC pocket too wide for cap_x given side_wall");
assert(bnc_body_h < inter_pcb_gap,
       "BNC body too tall for inter_pcb_gap (axial)");
assert(pocket_y > slot_depth,
       "Pocket must reach past the slot into the body");

// Placeholder render for now
cube([cap_x, cap_y, cap_z]);
```

- [ ] **Step 2: Render-check parameter resolution**

Run:
```bash
openscad -o /tmp/spooltenna_cap_params.stl \
  /Users/rwjblue/src/github/rwjblue/scad-lab/models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad
```
Expected: command exits 0, no assertion errors. The placeholder STL is a 17.5 × 18.3 × 20.6 mm box.

- [ ] **Step 3: Sanity-check the V1_3 preset**

Run:
```bash
openscad -D 'model="V1_3"' \
  -o /tmp/spooltenna_cap_v13.stl \
  /Users/rwjblue/src/github/rwjblue/scad-lab/models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad
```
Expected: exits 0. Placeholder box dimensions become 17.0 × 18.5 × 20.6 mm.

- [ ] **Step 4: Commit (jj)**

```bash
cd /Users/rwjblue/src/github/rwjblue/scad-lab
jj describe -m "spooltenna_bnc_cap: parameters and presets"
jj new
```

---

## Task 3: Build the solid outer block (no internal features yet)

**Files:**
- Modify: `models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad`

The cap will be built centered on X, with Y=0 at the radially-inward face (the open back) and Z centered on 0. This puts the BNC pocket opening on the Y=0 face and the front wall on the Y=cap_y face -- natural for the install direction.

- [ ] **Step 1: Add the `cap_solid()` module and replace the placeholder render**

In the file, replace the trailing `cube(...)` placeholder render block with:

```scad
// ---------------------------------------------------------------
// Modules
// ---------------------------------------------------------------

// Solid outer block, before any cavities or chamfers.
// Centered: X on 0, Z on 0. Y=0 is the radially-inward (open) face.
module cap_solid() {
    translate([-cap_x / 2, 0, -cap_z / 2])
        cube([cap_x, cap_y, cap_z]);
}

// Side armor fairings on the outer faces of the two legs. In plan view
// these flare out at the disk side, then taper into the front wall so a
// side impact glances into the stronger body instead of the straight leg.
module side_glance_armor() {
    right_profile = [
        [cap_x / 2, 0],
        [cap_x / 2, cap_y],
        [cap_x / 2 + side_glance_w, 0]
    ];
    left_profile = [
        [-cap_x / 2, 0],
        [-cap_x / 2 - side_glance_w, 0],
        [-cap_x / 2, cap_y]
    ];

    translate([0, 0, -cap_z / 2])
        linear_extrude(height = cap_z) {
            polygon(right_profile);
            polygon(left_profile);
        }
}

// Top-level render
cap_solid();
```

- [ ] **Step 2: Render and visually inspect**

Run:
```bash
openscad -o /tmp/spooltenna_cap_t3.stl \
  /Users/rwjblue/src/github/rwjblue/scad-lab/models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad

openscad --camera=0,0,0,55,0,25,80 --imgsize=800,600 \
  -o /tmp/spooltenna_cap_t3.png \
  /Users/rwjblue/src/github/rwjblue/scad-lab/models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad
```
Expected: exits 0; STL is a 17.5 × 18.3 × 20.6 mm box centered on X and Z at 0, Y from 0 to 18.3.

- [ ] **Step 3: Commit (jj)**

```bash
cd /Users/rwjblue/src/github/rwjblue/scad-lab
jj describe -m "spooltenna_bnc_cap: solid outer block"
jj new
```

---

## Task 4: Subtract the BNC pocket

**Files:**
- Modify: `models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad`

- [ ] **Step 1: Add the `bnc_pocket()` module**

After the `cap_solid()` module and before the top-level render, add:

```scad
// BNC pocket: a rectangular cavity that opens on the radially-inward
// face (Y = 0), extends Y forward to within `wall` of the front face,
// and cuts fully through Z so the PCB faces act as the axial walls.
// Centered on X.
module bnc_pocket() {
    eps = 0.01;  // overlap into the open face so the boolean is clean
    translate([-pocket_x / 2, -eps, -cap_z / 2 - eps])
        cube([pocket_x, pocket_y + eps, cap_z + 2 * eps]);
}
```

- [ ] **Step 2: Wrap the top-level render in a difference**

Replace the trailing `cap_solid();` line with:

```scad
difference() {
    cap_solid();
    bnc_pocket();
}
```

- [ ] **Step 3: Render and verify**

Run:
```bash
openscad -o /tmp/spooltenna_cap_t4.stl \
  /Users/rwjblue/src/github/rwjblue/scad-lab/models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad
```
Expected: exits 0. Open the STL in OpenSCAD GUI (or `open /tmp/spooltenna_cap_t4.stl`) and confirm:
- A roughly 18 mm tall block.
- A rectangular cavity about 12 mm wide opens on the Y=0 face, cuts fully through Z, goes about 15.9 mm deep, and leaves about 2.4 mm of front wall.

- [ ] **Step 4: Commit (jj)**

```bash
cd /Users/rwjblue/src/github/rwjblue/scad-lab
jj describe -m "spooltenna_bnc_cap: subtract BNC pocket"
jj new
```

---

## Task 5: Subtract the bongo tie groove

**Files:**
- Modify: `models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad`

A circular-segment channel running circumferentially (X direction) across the front face (Y=cap_y), centered at Z=0 in the open space between the two spool disks. The groove uses a 4 mm diameter cylinder offset so it cuts 1.5 mm into the front face; this matches the bongo tie path from prong to prong without adding support requirements.

- [ ] **Step 1: Add the `tie_groove()` module**

After `bnc_pocket()`, add:

```scad
// Bongo tie groove: circular-segment channel across the front Y face,
// running across X from prong to prong.
module tie_groove() {
    eps = 0.01;
    r = tie_groove_w / 2;
    translate([-cap_x / 2 - side_glance_w - eps,
               cap_y + r - tie_groove_d,
               0])
        rotate([0, 90, 0])
            cylinder(r = r, h = cap_x + 2 * side_glance_w + 2 * eps);
}
```

## Task 5a: Add the PCB disk-edge slots

**Files:**
- Modify: `models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad`

The cap spans both white PCB disks, so the legs need slots that fit the
disk edges. Cut two Y-running channels from the open side, one for each
disk, sized to `pcb_thickness + pcb_slot_clear`.

- [ ] **Step 1: Add the `pcb_edge_slots()` module**

After `tie_groove()`, add:

```scad
// Slots that let the two PCB disk edges slide into the side legs. These
// are what locate the cap axially while the bongo tie holds it inward.
module pcb_edge_slots() {
    eps = 0.01;
    y_depth = disk_slot_depth + eps;

    translate([-cap_x / 2 - side_glance_w - eps,
               -eps,
               inter_pcb_gap / 2 - pcb_slot_clear / 2])
        cube([cap_x + 2 * side_glance_w + 2 * eps,
              y_depth,
              pcb_slot_h + eps]);

    translate([-cap_x / 2 - side_glance_w - eps,
               -eps,
               -inter_pcb_gap / 2 - pcb_thickness - pcb_slot_clear / 2])
        cube([cap_x + 2 * side_glance_w + 2 * eps,
              y_depth,
              pcb_slot_h + eps]);
}
```

- [ ] **Step 2: Add the slots to the top-level difference**

Update the top-level render block to include `pcb_edge_slots()`:

```scad
difference() {
    cap_solid();
    bnc_pocket();
    pcb_edge_slots();
    tie_groove();
}
```

- [ ] **Step 3: Render and verify**

Run:
```bash
openscad -o /tmp/spooltenna_cap_t5a.stl \
  /Users/rwjblue/src/github/rwjblue/scad-lab/models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad
```
Expected: exits 0. Open the STL; confirm each side leg has two
Y-running slots from the open side, aligned with the two PCB disk
positions.

- [ ] **Step 2: Add the groove to the top-level difference**

Update the top-level render block to:

```scad
difference() {
    cap_solid();
    bnc_pocket();
    tie_groove();
}
```

- [ ] **Step 3: Render and verify**

Run:
```bash
openscad -o /tmp/spooltenna_cap_t5.stl \
  /Users/rwjblue/src/github/rwjblue/scad-lab/models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad
```
Expected: exits 0. Open the STL; confirm a rounded groove about `tie_groove_w` (4 mm) wide × `tie_groove_d` (1.5 mm) deep is recessed into the Y=cap_y front face, running across X from prong to prong.

- [ ] **Step 4: Commit (jj)**

```bash
cd /Users/rwjblue/src/github/rwjblue/scad-lab
jj describe -m "spooltenna_bnc_cap: bongo tie groove"
jj new
```

---

## Task 6: Add the lead-in chamfer on the radially-inward edges

**Files:**
- Modify: `models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad`

The cap should self-align as it drops into the slot. Chamfer the four edges of the Y=0 face (the four edges of the cap's open mouth that approach the disk first). Each chamfer is a triangular prism subtracted from one edge.

A small helper module makes the four placements obvious. Each chamfer is a triangular prism of cross-section `c × c` running along the edge.

- [ ] **Step 1: Add the `lead_in_chamfers()` module**

After `tie_groove()`, add:

```scad
// One triangular-prism cutter: a c × c right triangle extruded along its
// own +X axis for `length` mm. The two short sides of the triangle are
// aligned with +X (length) and a perpendicular face; the hypotenuse is
// the chamfer surface.
module _chamfer_prism(length, c) {
    rotate([0, 90, 0])  // make the extrude axis lie along +X
        linear_extrude(height = length)
            polygon([[0, 0], [c, 0], [0, c]]);
}

// Triangular-prism cutter extruded along +Z for the vertical mouth edges.
module _right_edge_chamfer_prism(length, c) {
    linear_extrude(height = length)
        polygon([[0, 0], [-c, 0], [0, c]]);
}

module _left_edge_chamfer_prism(length, c) {
    linear_extrude(height = length)
        polygon([[0, 0], [c, 0], [0, c]]);
}

// Lead-in chamfer on the four edges of the radially-inward (Y=0) face.
// At each edge, place a chamfer prism so the triangle's right-angle
// corner sits exactly on the cap edge and the hypotenuse cuts inward.
module lead_in_chamfers() {
    c = lead_in_chamfer;
    eps = 0.01;
    L_x = cap_x + 2 * eps;
    L_z = cap_z + 2 * eps;

    // Y=0 / +Z edge (top of mouth, runs along +X)
    translate([-cap_x / 2 - eps, 0, cap_z / 2 - c])
        _chamfer_prism(L_x, c);

    // Y=0 / -Z edge (bottom of mouth, runs along +X) -- mirror across X-Y
    translate([-cap_x / 2 - eps, 0, -cap_z / 2])
        mirror([0, 0, 1])
            translate([0, 0, -c])
                _chamfer_prism(L_x, c);

    // Y=0 / +X edge (right side of mouth, runs along +Z)
    translate([cap_x / 2, 0, -cap_z / 2 - eps])
        _right_edge_chamfer_prism(L_z, c);

    // Y=0 / -X edge (left side of mouth, runs along +Z) -- mirror across Y-Z
    translate([-cap_x / 2, 0, -cap_z / 2 - eps])
        _left_edge_chamfer_prism(L_z, c);
}
```

- [ ] **Step 2: Add the chamfers to the top-level difference**

Update the top-level render block to:

```scad
difference() {
    cap_solid();
    bnc_pocket();
    tie_groove();
    lead_in_chamfers();
}
```

- [ ] **Step 3: Render and visually verify**

Run:
```bash
openscad -o /tmp/spooltenna_cap_t6.stl \
  /Users/rwjblue/src/github/rwjblue/scad-lab/models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad
```
Open the STL. Confirm:
- All four edges around the open Y=0 mouth have a 1.0 mm × 45° chamfer.
- No other edges are chamfered.
- The chamfer cuts the cap exterior, not the BNC pocket interior.

If the chamfer ends up on the wrong face (e.g., it cuts the Y=cap_y / front face instead of Y=0 / back), the most likely cause is an off-by-one in the `mirror` / `translate` pair -- flip the sign on the inner `translate` and re-render. Iterate until the visual matches.

- [ ] **Step 4: Commit (jj)**

```bash
cd /Users/rwjblue/src/github/rwjblue/scad-lab
jj describe -m "spooltenna_bnc_cap: lead-in chamfers"
jj new
```

---

## Task 7: Wrap the renderable in a `cap()` module

**Files:**
- Modify: `models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad`

Convention in this repo (`spacer_m3.scad`) is to define a top-level module and call it once. Match the pattern.

- [ ] **Step 1: Wrap the difference in a `cap()` module and call it**

Replace the trailing top-level `difference() { ... }` block with:

```scad
// ---------------------------------------------------------------
// Top-level cap
// ---------------------------------------------------------------
module cap() {
    difference() {
        union() {
            cap_solid();
            side_glance_armor();
        }
        bnc_pocket();
        tie_groove();
        lead_in_chamfers();
    }
}

cap();
```

- [ ] **Step 2: Render and verify nothing changed**

Run:
```bash
openscad -o /tmp/spooltenna_cap_t7.stl \
  /Users/rwjblue/src/github/rwjblue/scad-lab/models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad
```
Expected: exits 0; STL is byte-identical (or visually identical) to the Task 6 output.

Optional: `diff <(xxd /tmp/spooltenna_cap_t6.stl) <(xxd /tmp/spooltenna_cap_t7.stl) | head` — empty diff means byte-identical.

- [ ] **Step 3: Commit (jj)**

```bash
cd /Users/rwjblue/src/github/rwjblue/scad-lab
jj describe -m "spooltenna_bnc_cap: wrap in cap() module"
jj new
```

---

## Task 8: Render presets and confirm both Ultra and v1.3 builds are clean

**Files:** none — this is verification-only.

- [ ] **Step 1: Render the Ultra v1.6 default to a per-model STL**

Run:
```bash
openscad \
  -o /Users/rwjblue/src/github/rwjblue/scad-lab/models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap_ultra_v1_6.stl \
  /Users/rwjblue/src/github/rwjblue/scad-lab/models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad
```
Expected: exits 0; non-empty STL.

- [ ] **Step 2: Render the V1_3 variant**

Run:
```bash
openscad -D 'model="V1_3"' \
  -o /Users/rwjblue/src/github/rwjblue/scad-lab/models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap_v1_3.stl \
  /Users/rwjblue/src/github/rwjblue/scad-lab/models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad
```
Expected: exits 0; non-empty STL. The V1_3 variant should be ~16 mm radial (vs. ~18 mm for Ultra) and otherwise identical.

- [ ] **Step 3: Visual diff in the OpenSCAD GUI (optional but recommended)**

Open both STLs; confirm:
- Ultra: 17.5 × 18.3 × 20.6 mm bounding box.
- V1.3: 17.0 × 18.5 × 20.6 mm bounding box.
- Both have the BNC pocket on the Y=0 face, tie groove on the Y=cap_y front face running across X, and chamfers on the four Y=0 edges.

- [ ] **Step 4: Decide whether to keep the rendered STLs in the repo**

The repo already has `dx_commander_element_label.3mf` checked in alongside its `.scad`, so checking in the rendered artifacts matches existing convention. Keep both STLs.

- [ ] **Step 5: Commit (jj)**

```bash
cd /Users/rwjblue/src/github/rwjblue/scad-lab
jj describe -m "spooltenna_bnc_cap: render Ultra and V1.3 STLs"
jj new
```

---

## Task 9: Add a render entry to `scripts/render_example.sh`

**Files:**
- Modify: `scripts/render_example.sh`

- [ ] **Step 1: Append a render command for both Spooltenna variants**

Append to the bottom of `scripts/render_example.sh`:

```bash

openscad \
  -o "${REPO_ROOT}/models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap_ultra_v1_6.stl" \
  "${REPO_ROOT}/models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad"

openscad -D 'model="V1_3"' \
  -o "${REPO_ROOT}/models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap_v1_3.stl" \
  "${REPO_ROOT}/models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad"
```

- [ ] **Step 2: Run the script end to end**

Run:
```bash
/Users/rwjblue/src/github/rwjblue/scad-lab/scripts/render_example.sh
```
Expected: exits 0; the existing `spacer_m3.stl` and the two new STLs are produced.

- [ ] **Step 3: Commit (jj)**

```bash
cd /Users/rwjblue/src/github/rwjblue/scad-lab
jj describe -m "scripts: render spooltenna_bnc_cap variants"
jj new
```

---

## Task 10: Write the model README

**Files:**
- Create: `models/ham_radio/spooltenna_bnc_cap/README.md`

- [ ] **Step 1: Write the README**

Write `models/ham_radio/spooltenna_bnc_cap/README.md`:

```markdown
# Spooltenna BNC Cap

A 3D-printed protective cap for the BNC connector on the
[KO4HUI Spooltenna](https://github.com/modulo8/KO4HUI-Spooltenna) end-fed
half-wave wire spool antenna. Drops into the existing PCB slot at the
bottom of the spool and is retained by the bongo tie that already ships
with the antenna.

## Why

The Spooltenna is a two-PCB wire spool with a horizontal PCB-mount BNC
(Molex 73100 / Winconn 364A2x95 family) whose bayonet barrel pokes out
through a slot in both PCBs. On Ultra v1.5/v1.6 it sticks ~8 mm past
the disk edge — exposed enough that one BNC has already been broken off
in a bag. This cap adds an open-back rectangular bumper over the BNC
without widening the spool over the wire winding.

## How it fits

- Drops into the existing 18.5 mm × 5.9 mm slot at the bottom of the
  Ultra disk (or 18 × 9.6 mm on V1.3).
- Lands between the two PCBs (open on both axial faces — the PCB inside
  surfaces complete the box). Default 15 mm standoff gap; tunable.
- Bongo tie wraps around the spool's center as today and seats in the
  top groove that runs from prong to prong, pulling the cap radially
  inward.

## Print

- **Material:** PETG
- **Nozzle:** 0.4 mm
- **Layer:** 0.2 mm
- **Perimeters:** 4
- **Infill:** 30 % gyroid
- **Temps:** 240 °C nozzle / 75 °C bed
- **Cooling:** ~30 %
- **Orientation:** Front face (the closed Y=cap_y face, the part that takes
  bag hits) on the build plate; open inner face up. Layers stack
  radially. No supports needed.

## Models supported

Set the `model` parameter at the top of `spooltenna_bnc_cap.scad`:

| Value | Description |
|---|---|
| `"ULTRA_V1_6"` (default) | Ultra v1.6 — 76.2 mm disk, 18.5 × 5.9 mm slot |
| `"ULTRA_V1_5"` | Identical geometry to v1.6 |
| `"V1_3"` | Larger 120 mm disk, 18 × 9.6 mm slot |

## Parameters

Edit at the top of the SCAD file. The defaults work for an Ultra v1.6
with 15 mm M3 standoffs.

| Parameter | Default | Notes |
|---|---|---|
| `model` | `"ULTRA_V1_6"` | preset switch |
| `inter_pcb_gap` | 15.0 | standoff length between PCBs |
| `pcb_thickness` | 1.6 | each PCB disk thickness |
| `disk_outer_wall` | 1.2 | plastic outside each PCB edge slot |
| `bnc_protrusion` | 8.5 | bayonet length past disk OD |
| `bnc_body_w` | 9.65 | BNC body width (X) |
| `bnc_body_h` | 13.0 | BNC body height (Z) |
| `clearance` | 0.5 | X per-side clearance to the slot |
| `wall` | 2.4 | front wall (radial-outermost) |
| `side_wall` | 2.5 | circumferential side walls |
| `lead_in_chamfer` | 1.0 | chamfer on the Y=0 open edges |
| `front_air_gap` | 1.5 | inside front wall to BNC tip |
| `tie_groove_w` | 4.0 | bongo tie channel width |
| `tie_groove_d` | 1.5 | bongo tie channel depth |

If the first print is slightly tight or loose at the slot or against
the PCB faces, bump `clearance` by ±0.2 mm and reprint -- that single
parameter drives both interfaces.

## Render

GUI:
1. Open `spooltenna_bnc_cap.scad` in OpenSCAD.
2. Tweak parameters at the top.
3. F6 → Export STL.

CLI:
```bash
openscad -o spooltenna_bnc_cap.stl spooltenna_bnc_cap.scad

# V1.3 variant
openscad -D 'model="V1_3"' -o spooltenna_bnc_cap_v1_3.stl spooltenna_bnc_cap.scad
```

Or run `scripts/render_example.sh` from the repo root to regenerate
both default STLs.

## Install

1. Wind antenna wire as usual.
2. Lower the cap onto the bottom of the spool with the open face down
   and axial direction matching the spool axis. Chamfered edges find
   the slot; the BNC enters the pocket. Cap bottoms when its inner
   face seats against the slot's inner wall.
3. Wrap the bongo tie around the spool's center; it seats in the top
   groove running from prong to prong.

## Design rationale

See `../../../docs/superpowers/specs/2026-05-12-spooltenna-bnc-cap-design.md`.
```

- [ ] **Step 2: Render-spot-check the README**

Open the file in your editor or `glow` / `mdcat`; confirm tables render
and links are intact.

- [ ] **Step 3: Commit (jj)**

```bash
cd /Users/rwjblue/src/github/rwjblue/scad-lab
jj describe -m "spooltenna_bnc_cap: model README"
jj new
```

---

## Task 11: Update repo root README index

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add a "Models" subsection (or extend the existing layout section)**

Append to `README.md` under the "Layout" section (after the existing bullets):

```markdown
## Models in this repo

- `models/ham_radio/dx_commander_element_label/` – element label tags
- `models/ham_radio/spooltenna_bnc_cap/` – BNC connector protector for
  the KO4HUI Spooltenna (Ultra v1.5/v1.6 + V1.3)
- `models/ham_radio/vertical_dipole_spacer/` – 6 m vertical dipole center
- `models/luggage_tag/` – customizable QR luggage tag
- `models/mechanical/spacer_m3/` – configurable M3 spacer
```

- [ ] **Step 2: Verify**

Run:
```bash
cat /Users/rwjblue/src/github/rwjblue/scad-lab/README.md
```
Expected: index list visible at the bottom.

- [ ] **Step 3: Commit (jj)**

```bash
cd /Users/rwjblue/src/github/rwjblue/scad-lab
jj describe -m "README: index models including spooltenna_bnc_cap"
jj new
```

---

## Task 12: Final validation — full cycle from blank slate

**Files:** none — this is verification-only.

- [ ] **Step 1: Clean previous artifacts**

```bash
rm -f \
  /Users/rwjblue/src/github/rwjblue/scad-lab/models/ham_radio/spooltenna_bnc_cap/*.stl \
  /tmp/spooltenna_cap_*.stl /tmp/spooltenna_cap_*.png
```

- [ ] **Step 2: Run the render script**

```bash
/Users/rwjblue/src/github/rwjblue/scad-lab/scripts/render_example.sh
```
Expected: exits 0; both STLs present in `models/ham_radio/spooltenna_bnc_cap/`.

- [ ] **Step 3: Visually inspect both STLs in OpenSCAD GUI**

Open each STL and confirm by eye:
- Ultra (default): bounding box ~17.5 × 18.3 × 20.6 mm; pocket on one face; tie groove on the front face running across X; chamfers on the four pocket-side edges.
- V1.3: bounding box ~17.0 × 18.5 × 20.6 mm; same internal features.

- [ ] **Step 4: Sanity-check assertions trigger on bad inputs**

Run:
```bash
openscad -D 'inter_pcb_gap=5' \
  -o /tmp/spooltenna_cap_bad.stl \
  /Users/rwjblue/src/github/rwjblue/scad-lab/models/ham_radio/spooltenna_bnc_cap/spooltenna_bnc_cap.scad
```
Expected: non-zero exit. The output should mention an `assert` failure (likely "BNC body too tall for inter_pcb_gap (axial)" because the gap is too small for the BNC body).

- [ ] **Step 5: Final jj describe**

```bash
cd /Users/rwjblue/src/github/rwjblue/scad-lab
jj st
```
Expected: clean working copy (or only the most recent empty `jj new` change).

If everything looks right, the user can squash the per-task changes into a single tidy commit with:
```bash
jj squash --from <first-spooltenna-change> --into <last-spooltenna-change>
```
or use the `jj` skill workflow they prefer.

---

## Out-of-scope follow-ups (not in this plan)

- Print and bag-test (physical, requires the user).
- Tune `clearance` based on first print (one-parameter tweak).
- Variant for non-Spooltenna BNC connectors.
