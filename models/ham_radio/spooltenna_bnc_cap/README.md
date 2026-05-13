# Spooltenna BNC Cap

A 3D-printed protective cap for the BNC connector on the
[KO4HUI Spooltenna](https://github.com/modulo8/KO4HUI-Spooltenna) end-fed
half-wave wire spool antenna. Drops into the existing PCB slot at the
bottom of the spool and is retained by the bongo tie that already ships
with the antenna.

## Why

The Spooltenna is a two-PCB wire spool with a horizontal PCB-mount BNC
(Molex 73100 / Winconn 364A2x95 family) whose bayonet barrel pokes out
through a slot in both PCBs. On Ultra v1.5/v1.6 it sticks about 8 mm past
the disk edge, exposed enough that one BNC has already been broken off in
a bag. This cap adds an open-back rectangular bumper over the BNC without
widening the spool over the wire winding.

## How it fits

- Drops into the existing 18.5 mm x 5.9 mm slot at the bottom of the
  Ultra disk, or 18 mm x 9.6 mm on V1.3.
- Spans both PCB disks outside-to-outside. The BNC pocket is open through
  the axial faces, so the two disks sit inside the cap's span. Default
  15 mm standoff gap and 1.6 mm PCB thickness; tunable.
- Bongo tie wraps around the spool's center as today and seats in the
  front groove that runs from prong to prong, pulling the cap radially
  inward.
- Side fairings flare outward near the open disk side and taper back into
  the front wall, giving side hits a sloped face instead of a square leg.

## Print

- **Material:** PETG
- **Nozzle:** 0.4 mm
- **Layer:** 0.2 mm
- **Perimeters:** 4
- **Infill:** 30 % gyroid
- **Temps:** 240 C nozzle / 75 C bed
- **Cooling:** about 30 %
- **Orientation:** Front face, the closed Y=cap_y face that takes bag
  hits, on the build plate; open inner face up. Layers stack radially.
  No supports needed.

## Models supported

Set the `model` parameter at the top of `spooltenna_bnc_cap.scad`:

| Value | Description |
|---|---|
| `"ULTRA_V1_6"` (default) | Ultra v1.6, 76.2 mm disk, 18.5 x 5.9 mm slot |
| `"ULTRA_V1_5"` | Identical geometry to v1.6 |
| `"V1_3"` | Larger 120 mm disk, 18 x 9.6 mm slot |

## Parameters

Edit at the top of the SCAD file. The defaults work for an Ultra v1.6
with 15 mm M3 standoffs.

| Parameter | Default | Notes |
|---|---|---|
| `model` | `"ULTRA_V1_6"` | preset switch |
| `inter_pcb_gap` | 15.0 | standoff length between PCBs |
| `pcb_thickness` | 1.6 | each PCB disk thickness |
| `pcb_slot_clear` | 0.3 | extra Z clearance for disk-edge slots |
| `disk_outer_wall` | 1.2 | plastic outside each PCB edge slot |
| `bnc_protrusion` | 8.5 | bayonet length past disk OD |
| `bnc_body_w` | 9.65 | BNC body width (X) |
| `bnc_body_h` | 13.0 | BNC body height (Z) |
| `clearance` | 0.5 | X per-side clearance to the slot |
| `wall` | 2.4 | front wall (radial-outermost) |
| `side_wall` | 2.5 | circumferential side walls |
| `lead_in_chamfer` | 1.0 | chamfer on the Y=0 open edges |
| `front_air_gap` | 1.5 | inside front wall to BNC tip |
| `disk_slot_depth` | `slot_depth + 0.5` | radial depth of the disk-edge slots |
| `side_glance_w` | 3.0 | side fairing flare width outside each leg |
| `tie_groove_w` | 4.0 | bongo tie channel width |
| `tie_groove_d` | 1.5 | bongo tie channel depth |

If the first print is slightly tight or loose at the slot or against the
PCB faces, bump `clearance` by 0.2 mm and reprint. That single parameter
drives both interfaces.

## Render

GUI:

1. Open `spooltenna_bnc_cap.scad` in OpenSCAD.
2. Tweak parameters at the top.
3. F6, then export STL.

CLI:

```bash
openscad -o spooltenna_bnc_cap.stl spooltenna_bnc_cap.scad

# V1.3 variant
openscad -D 'model="V1_3"' -o spooltenna_bnc_cap_v1_3.stl spooltenna_bnc_cap.scad
```

Or run `scripts/render_example.sh` from the repo root to regenerate both
default STLs.

## Install

1. Wind antenna wire as usual.
2. Lower the cap onto the bottom of the spool with the open face down and
   axial direction matching the spool axis. Chamfered edges find the slot;
   the BNC enters the pocket. Cap bottoms when its inner face seats
   against the slot's inner wall.
3. Wrap the bongo tie around the spool's center; it seats in the front
   groove running from prong to prong.

## Design rationale

See `../../../docs/superpowers/specs/2026-05-12-spooltenna-bnc-cap-design.md`.
