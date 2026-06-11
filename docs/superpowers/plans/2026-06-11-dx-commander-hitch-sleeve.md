# DX Commander Hitch Sleeve Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a parameterized OpenSCAD sleeve adapter for a DX Commander Expedition mast in a 59 mm hitch-mounted flag pole holder.

**Architecture:** Add one focused model directory under `models/ham_radio/`. The OpenSCAD model uses a rotationally symmetric union of lower insert, stop flange, and upper guide, then subtracts a close mast bore with lead-in chamfers.

**Tech Stack:** OpenSCAD, Markdown documentation, existing `openscad` CLI render workflow.

---

## File Structure

- Create `models/ham_radio/dx_commander_hitch_sleeve/dx_commander_hitch_sleeve.scad`: parameterized sleeve model and render call.
- Create `models/ham_radio/dx_commander_hitch_sleeve/README.md`: dimensions, print orientation, and fit-tuning notes.
- Modify `README.md`: add the new model directory to the repo catalog.

## Task 1: Add the OpenSCAD Sleeve Model

**Files:**
- Create: `models/ham_radio/dx_commander_hitch_sleeve/dx_commander_hitch_sleeve.scad`

- [ ] **Step 1: Create the model directory**

Run:

```bash
mkdir -p models/ham_radio/dx_commander_hitch_sleeve
```

Expected: command exits 0.

- [ ] **Step 2: Add the OpenSCAD model**

Create `models/ham_radio/dx_commander_hitch_sleeve/dx_commander_hitch_sleeve.scad` with:

```scad
/*
  models/ham_radio/dx_commander_hitch_sleeve/dx_commander_hitch_sleeve.scad

  Sleeve adapter for a DX Commander Expedition mast in a hitch-mounted
  flag pole holder.
*/

holder_inner_d = 59;   // measured ID of hitch-mounted holder tube
body_outer_d   = 58.5; // sleeve OD below/above the flange
mast_outer_d   = 47;   // measured mast OD
mast_bore_d    = 47.6; // close sliding fit for mast

lower_insert_h = 76.2; // 3 in below holder rim
upper_guide_h  = 20;   // guide above holder rim
flange_outer_d = 68;   // stop flange OD
flange_h       = 5;    // stop flange height

chamfer = 1;
$fn = 160;

eps = 0.02;
total_h = lower_insert_h + flange_h + upper_guide_h;

assert(body_outer_d < holder_inner_d, "body_outer_d must be smaller than holder_inner_d");
assert(mast_bore_d > mast_outer_d, "mast_bore_d must be larger than mast_outer_d");
assert(flange_outer_d > holder_inner_d, "flange_outer_d must be larger than holder_inner_d");
assert(lower_insert_h > 0, "lower_insert_h must be positive");
assert(upper_guide_h > 0, "upper_guide_h must be positive");
assert(flange_h > 0, "flange_h must be positive");
assert(chamfer > 0, "chamfer must be positive");
assert(chamfer * 2 < flange_h, "chamfer must be less than half flange_h");
assert(chamfer * 2 < total_h, "chamfer must be less than half total_h");
assert(mast_bore_d + 2 * chamfer < body_outer_d, "mast bore chamfer must fit within body wall");

module chamfered_cylinder(d, h, c) {
    cylinder(
        h = h,
        d1 = d - 2 * c,
        d2 = d,
        center = false
    );

    translate([0, 0, c])
        cylinder(
            h = h - 2 * c,
            d = d,
            center = false
        );

    translate([0, 0, h - c])
        cylinder(
            h = c,
            d1 = d,
            d2 = d - 2 * c,
            center = false
        );
}

module bore_with_leadins() {
    cylinder(d = mast_bore_d, h = total_h + 2 * eps, center = false);

    translate([0, 0, -eps])
        cylinder(
            h = chamfer + eps,
            d1 = mast_bore_d + 2 * chamfer,
            d2 = mast_bore_d,
            center = false
        );

    translate([0, 0, total_h - chamfer])
        cylinder(
            h = chamfer + eps,
            d1 = mast_bore_d,
            d2 = mast_bore_d + 2 * chamfer,
            center = false
        );
}

module sleeve_solid() {
    union() {
        chamfered_cylinder(d = body_outer_d, h = total_h, c = chamfer);

        translate([0, 0, lower_insert_h])
            chamfered_cylinder(d = flange_outer_d, h = flange_h, c = chamfer);
    }
}

module dx_commander_hitch_sleeve() {
    difference() {
        sleeve_solid();

        translate([0, 0, -eps])
            bore_with_leadins();
    }
}

dx_commander_hitch_sleeve();
```

- [ ] **Step 3: Render-check the SCAD file**

Run:

```bash
openscad -o /private/tmp/dx_commander_hitch_sleeve.stl models/ham_radio/dx_commander_hitch_sleeve/dx_commander_hitch_sleeve.scad
```

Expected: command exits 0 with no assertion failures and creates `/private/tmp/dx_commander_hitch_sleeve.stl`.

- [ ] **Step 4: Inspect the diff**

Run:

```bash
jj diff
```

Expected: diff only creates the new SCAD file.

- [ ] **Step 5: Commit**

Run:

```bash
jj commit -m "Add DX Commander hitch sleeve model"
```

Expected: commit succeeds and a new empty working copy is created.

## Task 2: Add Documentation and Catalog Entry

**Files:**
- Create: `models/ham_radio/dx_commander_hitch_sleeve/README.md`
- Modify: `README.md`

- [ ] **Step 1: Add the model README**

Create `models/ham_radio/dx_commander_hitch_sleeve/README.md` with:

```markdown
# DX Commander Hitch Sleeve

Sleeve adapter for using a DX Commander Expedition mast in a hitch-mounted
flag pole holder.

## Default Dimensions

| Feature | Value |
| --- | ---: |
| Holder tube ID | 59 mm |
| Sleeve body OD | 58.5 mm |
| Mast measured OD | 47 mm |
| Mast bore ID | 47.6 mm |
| Lower insertion height | 76.2 mm |
| Upper guide height | 20 mm |
| Stop flange OD | 68 mm |
| Stop flange height | 5 mm |
| Total height | 101.2 mm |

When installed, the 68 mm flange rests on the holder rim. The sleeve extends
76.2 mm into the holder and 20 mm above the rim.

## Printing

Print upright in PETG. The model uses chamfers at the entry edges and should not
need supports.

## Fit Tuning

The main fit parameters are at the top of
`dx_commander_hitch_sleeve.scad`.

- If the holder fit is too tight, reduce `body_outer_d`.
- If the holder fit is too loose, increase `body_outer_d`, keeping it below
  `holder_inner_d`.
- If the mast fit is too tight, increase `mast_bore_d` toward 47.8 mm.
- If the mast fit is too loose, reduce `mast_bore_d` toward 47.4 mm.
```

- [ ] **Step 2: Add the new model to the root README catalog**

In `README.md`, add this bullet under "Models in this repo":

```markdown
- `models/ham_radio/dx_commander_hitch_sleeve/` - sleeve adapter for a
  DX Commander Expedition mast in a hitch-mounted flag pole holder
```

Place it near the other `models/ham_radio/` entries.

- [ ] **Step 3: Render-check after documentation changes**

Run:

```bash
openscad -o /private/tmp/dx_commander_hitch_sleeve.stl models/ham_radio/dx_commander_hitch_sleeve/dx_commander_hitch_sleeve.scad
```

Expected: command exits 0 with no assertion failures.

- [ ] **Step 4: Inspect status and diff**

Run:

```bash
jj st
jj diff
```

Expected: diff only includes the new README and root README catalog update.

- [ ] **Step 5: Commit**

Run:

```bash
jj commit -m "Document DX Commander hitch sleeve"
```

Expected: commit succeeds and a new empty working copy is created.

## Task 3: Final Verification

**Files:**
- Verify: `models/ham_radio/dx_commander_hitch_sleeve/dx_commander_hitch_sleeve.scad`
- Verify: `models/ham_radio/dx_commander_hitch_sleeve/README.md`
- Verify: `README.md`

- [ ] **Step 1: Render the final STL to a temporary path**

Run:

```bash
openscad -o /private/tmp/dx_commander_hitch_sleeve.stl models/ham_radio/dx_commander_hitch_sleeve/dx_commander_hitch_sleeve.scad
```

Expected: command exits 0 with no assertion failures.

- [ ] **Step 2: Confirm final working copy state**

Run:

```bash
jj st
```

Expected: working copy has no changes.

- [ ] **Step 3: Report the result**

Report:

```text
Created the DX Commander hitch sleeve OpenSCAD model and README.
Render verification passed with OpenSCAD using /private/tmp/dx_commander_hitch_sleeve.stl.
```
