# Spooltenna BNC Cap — Design

A 3D-printed protective cap for the BNC connector on the
[KO4HUI Spooltenna](https://github.com/modulo8/KO4HUI-Spooltenna) end-fed
half-wave wire spool antenna. Printed in PETG, parameterized in OpenSCAD,
held in place by the bongo tie that already ships with the antenna.

## Problem

The Spooltenna is a two-PCB wire spool: two identical disks separated by
~15 mm of M3 standoffs, with the radiating wire wound around the outer
rim in the gap between them. A horizontal PCB-mount BNC (Molex 73100 /
Winconn 364A2x95 family) is mounted on one PCB's inside face, with its
bayonet barrel pointing radially outward through a slot in both disks.
The slot is 18.5 mm wide × ~5.9 mm deep on Ultra v1.5/v1.6, and the
bayonet face protrudes ~8 mm beyond the disk's outer edge.

In a bag, that exposed BNC takes side hits. One has already been broken
off the PCB. We want a low-bulk cover that:

- Sits over the BNC body and barrel
- Provides lateral (left/right, in the slot's width direction) impact
  buffering before a hit reaches the connector
- Drops into the existing slot rather than wrapping over the wire-wound
  rim (no added bulk on the perimeter)
- Stays on with the bongo tie that already retains the wound wire — no
  extra fasteners

## Target hardware

- **Primary:** Spooltenna Ultra v1.6 (and v1.5, which has identical
  slot/BNC geometry)
- **Stretch:** Spooltenna v1.3 (larger 120 mm disk, 18 mm slot, ~9.6 mm
  slot depth)
- Both use the Molex 73100 / Winconn 364A2x95 horizontal BNC

The OpenSCAD file exposes a `model` parameter with presets for the
supported variants; geometry is otherwise parameterized so any deviation
from the spec is one number to retune.

## Non-goals

- Cap that stays on while the antenna is in use (cable plugged in)
- Strain relief for the coax cable
- Weather sealing of the BNC
- Compatibility with non-Spooltenna BNC connectors

## Geometry

The cap is an open-back rectangular bumper that drops into the
existing PCB slot. Coordinate frame, cap-local:

- **X** = circumferential (along the slot's width / lateral direction)
- **Y** = radial (outward from the spool center; the install-push direction)
- **Z** = axial (along the spool's rotation axis, perpendicular to the PCBs)

```
                    spool axis (Z)
                        │
                        ▼
   ┌───────────────────────────────────────────┐
   │                                           │
   │  ┌─────────PCB 1 (inside face)─────────┐  │
   │  │                                     │  │
   │  │     ┌──── slot in PCB ────┐         │  │
   │  │     │                     │         │  │
   │  │     │   ┌── cap ──┐       │         │
   │  │     │   │  BNC    │       │         │   ← cap fits in slot,
   │  │     │   │ pocket  │       │         │     between PCBs
   │  │     │   └─────────┘       │         │
   │  │     └─────────────────────┘         │  │
   │  │                                     │  │
   │  └─────────PCB 2 (inside face)─────────┘  │
   │                                           │
   └───────────────────────────────────────────┘
              ↑ wire wound around rim ↑
```

### Outer dimensions (Ultra v1.6 defaults)

| Axis | Value | Source |
|---|---|---|
| X (circumferential length) | 17.5 mm | slot 18.5 − 1.0 mm clearance |
| Z (axial width) | 20.6 mm | 15.0 mm inter-PCB gap + 2 × (1.6 mm PCB thickness + 1.2 mm outer wall); spans both disks with slots around their edges |
| Y (total radial extent) | 18.3 mm | inner 5.9 mm sits in slot, outer 12.4 mm past disk OD; derived from 8.5 mm BNC protrusion + 1.5 mm air gap + 2.4 mm front wall |

### Closed faces (walls)

- Radially outward (front bumper): 2.4 mm wall
- Both circumferential sides: 2.5 mm walls — these transfer side hits
  into the slot walls in the disk material
- Side glance armor: triangular fairing material on each leg's outer face,
  starting near the PCB disk-edge slots and ramping upward toward the cap
  top so side hits glance into the disk wall instead of catching a square
  leg

### Open faces

- Radially inward: BNC enters here
- Both axial faces: open. The printed part has side/front wall material
  spanning the outside-to-outside PCB stack, but no printed top/bottom
  skins closing the BNC pocket. The two PCB disks sit inside this span and
  help locate the cap axially

### Internal features

- **BNC pocket:** 12 mm (X) rectangular cavity, full-through in Z, 15.9 mm
  deep, centered. The BNC body is ~9.65 mm wide and ~13 mm tall in the
  15 mm inter-PCB gap; the full-through axial opening avoids thin printed
  skins and lets the PCB faces provide the axial constraint. Bayonet face
  is round, but a square pocket prints cleaner and the corners are unused
  space — fine.
- **Lead-in chamfer:** 1.0 mm × 45° on the four radially-inward edges,
  for self-alignment on installation.
- **PCB edge slots:** Two Y-running slots cut into the legs at the two
  disk Z positions. Each slot is `pcb_thickness + 0.3 mm` tall and
  extends `slot_depth + 0.5 mm` inward from the open side, with 1.2 mm of
  printed plastic outside each disk edge. The white disk edges locate the
  cap axially.
- **Tie groove:** 4 mm diameter × 1.5 mm deep circular-segment channel on
  the front (+Y) face, running circumferentially across X from prong to
  prong at Z=0, centered in the open space between the two spool disks.

### Stopping behavior

The cap is a single 17.5 × 20.6 × 18.3 mm block — no distinct "lip" or
step, since the cap and any tongue we'd cut for it would both end up at
the same 17.5 mm width to fit the slot. The cap bottoms when its
radially-inward face seats against the slot's inner wall (5.9 mm into
the disk). The slot's side walls hold X; the two PCB disks sit within the
cap's Z span; the bongo tie holds Y inward.

## Parameters (OpenSCAD)

```scad
model                = "ULTRA_V1_6";   // ULTRA_V1_5 | ULTRA_V1_6 | V1_3

// stack
inter_pcb_gap        = 15.0;   // standoff length
pcb_thickness        = 1.6;    // each PCB disk thickness
pcb_slot_clear       = 0.3;    // extra Z clearance for disk-edge slots
disk_outer_wall      = 1.2;    // plastic outside each PCB edge slot

// disk / slot
slot_width           = 18.5;   // notch width
slot_depth           = 5.9;    // notch radial depth
disk_radius          = 38.1;   // reference

// BNC
bnc_body_w           = 9.65;
bnc_body_h           = 13.0;
bnc_protrusion       = 8.5;    // past disk OD

// cap
clearance            = 0.5;     // X per-side clearance
wall                 = 2.4;
side_wall            = 2.5;
lead_in_chamfer      = 1.0;
tie_groove_w         = 4.0;
tie_groove_d         = 1.5;
front_air_gap        = 1.5;    // BNC tip to inside of front wall
disk_slot_depth      = slot_depth + 0.5;
side_glance_w        = 3.0;    // side fairing width outside each leg
```

## Install / use flow

1. Wind the antenna wire onto the spool as usual.
2. Lower the cap onto the bottom of the spool with the open
   (radially-inward) face toward the disk and the cap's axial direction
   aligned with the spool axis. The chamfered leading edges find the
   slot; the BNC barrel enters the pocket as the cap slides in.
   Cap bottoms when its radially-inward face seats against the slot's
   inner wall.
3. Wrap the bongo tie around the spool's center as today. The tie
   crosses the cap's front (+Y) face and seats in the prong-to-prong
   groove. Pull tight.
4. Removal: unhook tie, lift cap straight off radially.

## Tolerances

| Interface | Nominal | Clearance | Why |
|---|---|---|---|
| Cap X vs. slot X | 17.5 / 18.5 mm | 0.5 mm/side | FDM lateral overprint + slot wall variance |
| Cap Z vs. PCB stack | 20.6 mm cap over 18.2 mm nominal PCB stack | 1.2 mm outside each disk edge | Spans both white PCB disks and provides outer material for the edge slots |
| Pocket vs. BNC body | 12 mm wide, full-through Z / 9.65 × ~13 mm body | ~1 mm/side X; full-through Z | Body fits without forcing; PCB disks constrain axial movement |
| Front wall to BNC tip | ≥ 1.5 mm | — | Air-gap so cable plugged in (cap removed) doesn't damage front wall |
| Lead-in chamfer | 1.0 × 45° | — | Self-aligning insertion |

The main slot clearance is driven from `clearance` for retuning per-printer
in X. The axial span is driven by `inter_pcb_gap` and `pcb_thickness`.

## Print profile

- Material: PETG
- Nozzle: 0.4 mm
- Layer: 0.2 mm
- Perimeters: 4
- Infill: 30 % gyroid
- Temps: 240 °C nozzle / 75 °C bed
- Cooling: ~30 %
- Orientation: **front face on the build plate** (open inner face up).
  Layers stack radially. Lateral impacts hit layers in shear, which
  PETG handles well. No supports needed.

## Fitment plan

1. Print the Ultra v1.6 default.
2. Dry-fit on a Spooltenna Ultra (no wire, no tie). Confirm cap drops
   into slot with chamfer self-aligning, BNC enters pocket, no force
   required.
3. Wind wire and add bongo tie. Confirm tie seats in groove, cap stays
   put under shaking.
4. Bag-test: stow spool in bag for normal use; check for cap movement,
   BNC integrity, and slot wall wear.
5. If too tight/loose, bump `clearance` ±0.2 mm and reprint.
6. Once dialed, regenerate v1.5 (identical) and v1.3 variants via
   `model` parameter; reprint and validate.

## Layout in this repo

```
models/ham_radio/spooltenna_bnc_cap/
├── spooltenna_bnc_cap.scad
└── README.md
```

## Pre-print measurements (do these once on the physical antenna)

The defaults below assume an Ultra v1.6 with 15 mm M3 standoffs and the
stock Molex 73100 horizontal BNC. Confirm with calipers; override the
matching OpenSCAD parameter if any value disagrees by more than ~0.3 mm.

| Measurement | Default | Parameter to override |
|---|---|---|
| Standoff length (clear gap between PCB inside faces) | 15.0 mm | `inter_pcb_gap` |
| Slot opening width (between the two slot side walls in the disk) | 18.5 mm | `slot_width` |
| Slot depth (radial, from disk OD inward to slot's inner wall) | 5.9 mm | `slot_depth` |
| BNC body width (the rectangular footprint, circumferential direction) | 9.65 mm | `bnc_body_w` |
| BNC body height above PCB inside face (axial) | 13.0 mm | `bnc_body_h` |
| BNC bayonet face protrusion past disk OD (radial) | 8.5 mm | `bnc_protrusion` |

If unsure on the BNC numbers, check the Molex 73100 / Winconn 364A2x95
datasheet — these are stock parts and the body dimensions are the same
across all units.

## Source references

All dimensions in this spec were derived from the local
`/Users/rwjblue/src/github/modulo8/KO4HUI-Spooltenna` checkout of the
[KO4HUI Spooltenna](https://github.com/modulo8/KO4HUI-Spooltenna) KiCad
sources at commit `3699ed0` (current `main` as of 2026-05-12).

| Spec value | Source file | Geometry |
|---|---|---|
| Ultra disk OD 76.2 mm | `ULTRA v1.6/Wire Spool Antenna Ultra V1.6.kicad_pcb` | `gr_arc` Edge.Cuts: center (150, 100), radius 38.1 mm |
| Ultra slot 18.5 × 5.9 mm | same | Edge.Cuts lines (140.75/159.25, 132.2 → 134.4) + 1 mm fillets |
| Ultra BNC at (150, 119.7) on B.Cu | same | `(footprint "footprints:BNC_MOLEX_73100_PIPE_WIDE")` |
| BNC body 9.65 × ~13 × ~22 mm | `footprints/BNC_MOLEX_73100.kicad_mod` | F.Fab outline (-4.825 .. 4.825) × (-4.75 .. -26.55) |
| BNC protrusion 8.15 mm past disk | derived | BNC tip (Y=146.25 from J2 at Y=119.7 plus footprint F.Fab end 26.55) − disk OD chord (Y=138.1) |
| V1.3 disk OD 120 mm | `v1.3/Wire Spool Antenna V1.3/Wire Spool Antenna V1.3.kicad_pcb` | `gr_arc` center (100, 100), radius 60 mm |
| V1.3 slot 18 × 9.6 mm | same | Edge.Cuts lines (91/109, 150.4 → 156.975) + 2 mm fillets |
| V1.3 BNC at (100, 138, 180°) on F.Cu | same | `(footprint "footprints:BNC_MOLEX_73100_PIPE")`; derived protrusion ~4.55 mm, rounded to 5.0 mm |

Inter-PCB standoff length was *not* found in the KiCad sources — the
boards have three 8.5 mm holes at 120° (centers (118.5, 100), (181.5, 100),
(150, 69.5) on Ultra) for M3 standoffs. The standoff length is a build
choice; 15 mm is a common Spooltenna choice but **must be measured on
the actual antenna before final print**.

## Open questions deferred to first print

- Bongo tie cross-section on this antenna's specific tie. The 4 mm
  diameter × 1.5 mm deep circular-segment groove fits a typical ~3 mm
  rubber loop; if the loop is
  thicker, bump `tie_groove_w` and/or `tie_groove_d`.
- Whether the front face needs a small text/label (e.g., "BNC") — out of
  scope for v1, easy add later via `linear_extrude(text(...))`.
