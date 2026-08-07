# Lightweight Balanced Feedline Parts

Three parameterized OpenSCAD parts for lightweight portable doublets:

- `balanced_feedline_spacer.scad` — snap-on spacer for two-wire open feedline
- `doublet_center_strain_relief.scad` — center support that redirects and
  strain-relieves each continuous antenna/feedline conductor without a splice
- `doublet_center_terminal_strain_relief.scad` — modular center with separate
  radiator and feedline conductors joined at two isolated #6-32 terminal studs

The defaults target **DX Engineering DXE-SANTW-500, 26 AWG Poly-STEALTH**
wire with a nominal jacket outside diameter of **1.02 mm** and **12.7 mm
(0.5 inch)** conductor center spacing. Measure the actual wire before
committing to a large print batch.

The 12.7 mm spacing is a mechanical geometry target, not a promise of an exact
characteristic impedance. Actual impedance depends on conductor diameter,
jacket dielectric, and how consistently the line hangs in use.

## Feedline Spacer

The spacer prints flat without supports and installs with its face
perpendicular to the feedline. Each conductor snaps sideways through a tapered
opening into a round channel. The default lead-in mouth is slightly wider than
the nominal wire, while the narrower throat supplies retention.

### Default Geometry

| Parameter | Default |
| --- | ---: |
| Nominal wire OD | 1.02 mm |
| Wire center spacing | 12.7 mm |
| Channel clearance | 0.18 mm |
| Resulting channel diameter | 1.20 mm |
| Entry-slot/throat width | 0.72 mm |
| Entry-mouth width | 1.10 mm |
| Body height | 3.8 mm |
| Body thickness | 2.4 mm |
| Approximate body width | 17.5 mm |

The 1.0 mm minimum wall assertion protects the material above and below each
channel. The default geometry leaves about 1.3 mm there and 1.8 mm from the
outside of each channel to the end of its snap jaw.

### Fit-Test Modes

Use the two-stage fit workflow before printing production spacers. Each test
renders five complete spacers with large through-cut markers that remain
readable on a rough, single-color PETG surface.

First set:

```scad
render_mode = "channel_fit_test";
```

Channel samples use **round holes**. One through five holes represent **1.10,
1.15, 1.20, 1.25, and 1.30 mm** respectively. Choose the smallest channel that
accepts the wire without shaving or crushing the jacket and still lets the
spacer be repositioned by hand. Set its difference from `wire_od` as
`channel_clearance`.

Then set:

```scad
render_mode = "slot_fit_test";
```

Slot samples use **rectangular through-slots**. One through five slots represent
**0.62, 0.67, 0.72, 0.77, and 0.82 mm** respectively. Choose the narrowest
throat that installs without damaging the jacket or permanently spreading the
PETG jaws. Smaller values provide more retention and require more snap force.
Change `entry_mouth_width` only if the initial lead-in is awkward; it does not
set final retention.

Return `render_mode` to `"spacer"` before exporting the production part. Print
two or three final spacers and test them while bending, coiling, and uncoiling
a short sample of completed feedline before committing to dozens.

### Spacer Quantity

An initial field spacing of about **8 inches / 200 mm** is a reasonable
lightweight starting point. The exact interval is not critical at HF; add
spacers where needed to keep the wires from twisting together.

| Feedline length | Approximate spacers at 8 in |
| ---: | ---: |
| 20 ft | 30 |
| 25 ft | 38 |
| 30 ft | 45 |
| 35 ft | 53 |
| 40 ft | 60 |

Place the first spacer about 2–3 inches below the center support.

## Continuous-Wire Doublet Center Strain Relief

The center is a 60 × 38 × 4 mm T-shaped plate with:

- a 6.5 mm hoist hole;
- three chamfered wire holes per conductor;
- 12.7 mm spacing between the two lower feedline exit holes; and
- no terminals, fasteners, or electrical joints.

The wire-path holes default to `wire_od + 0.80 mm`, giving room to thread the
long conductors. Their diameter and edge chamfer are parameterized separately
from the tighter snap-fit channels in the spacer. Assertions preserve at least
2.0 mm of plastic outside every face-side hole chamfer when dimensions or hole
positions change. The same checks retain at least 2.0 mm between adjacent
face-side chamfers.

### Threading Each Continuous Conductor

With the front face of the center toward you:

1. Bring the conductor in from its antenna-element side and pass it through
   the outer hole from front to back.
2. On the back, route it diagonally inward and down through the middle relief
   hole to the front.
3. On the front, route it diagonally inward and down through the lower
   feedline hole to the back.
4. Let the conductor continue downward as one side of the balanced feedline.
5. Mirror the routing for the other conductor.

Simplified front view of either side:

```text
antenna element ---- O  outer hole
                     \\  segment on back
                      O  middle relief hole
                       \\ segment on front
                        O lower feedline hole
                        |
                        | balanced feedline conductor
```

This weave transfers antenna tension into the center plate and keeps it off the
hanging feedline. The 0.60 mm wire-hole chamfers reduce jacket loading at the
printed edges. Do not apply high antenna tension; this is intended for a
lightweight portable doublet.

## Terminalized Doublet Center Strain Relief

The terminalized center is an alternative to the continuous-wire part, not a
replacement for it. Use it when interchangeable radiator pairs are worth the
extra hardware and weight. The default plate is approximately 64 × 42 × 5 mm.
It keeps these functions separate:

- two 22 mm-spaced terminal studs make the electrical joints;
- opposing snap-open radiator channels form a removable two-point weave;
- two-hole feedline weaves carry the hanging feedline weight; and
- the lower feedline exits remain 12.7 mm center-to-center.

The wider terminal spacing leaves finger room for the two terminal stacks; it
does not change the 12.7 mm spacing of the parallel feedline below the plate.
The default 4.0 mm printed stud holes provide 0.49 mm diametral clearance over
the nominal 3.51 mm major diameter of a #6 screw.

Each radiator channel defaults to a 1.82 mm round wire path, a 0.82 mm snap
throat, and a 1.20 mm tapered mouth. The outer channel opens upward and the
inner channel opens downward. Neither opening points along the horizontal
antenna-tension path, and the opposing openings keep the wire captured while
still allowing an already-crimped radiator to be removed without threading its
full length through the plate. These dimensions are independently
parameterized as `wire_hole_clearance`, `radiator_slot_width`, and
`radiator_mouth_width`.

### Hardware Bill of Materials

All terminal hardware should be 18-8/A2 stainless unless noted. The example
part numbers establish useful dimensions, but equivalent hardware is fine.

| Qty | Hardware | Required specification |
| ---: | --- | --- |
| 2 | Machine screws | #6-32 × 7/8 inch (22.2 mm), fully threaded, pan head |
| 4 | Flat washers | #6, 0.156 inch ID × 0.375 inch OD |
| 2 | Base nuts | #6-32 finished hex nuts |
| 2 | Lock washers | #6 internal-tooth stainless lock washers |
| 2 | Removable nuts | #6-32 flanged knurled thumb nuts, 3/8 inch head OD; McMaster 95150A139 or equivalent |
| 4 | Ring terminals | uninsulated tinned-copper closed rings, 26–22 AWG, #6/M3.5 stud; TE Connectivity 31430 or equivalent |
| 4 | Heat-shrink pieces | approximately 1/8 inch / 3.2 mm, 3:1 adhesive-lined, long enough to cover each crimp barrel |

Do not substitute the common red 22–16 AWG automotive terminals: their barrel
is too large for the 26 AWG wire. Use a crimper specified for the selected
26–22 AWG terminal, then pull-test every crimp. The referenced
[TE Connectivity 31430](https://www.te.com/en/product-31430.html) is an
uninsulated, tin-plated 26–22 AWG ring sized for a #6/M3.5 stud. Its heat shrink
provides environmental protection and support; it is not a substitute for the
printed strain-relief weave.

The 7/8 inch screw length allows for the 5 mm plate, two flat washers, the base
nut, two approximately 0.8 mm ring tongues, the tooth washer, and full
engagement of the thumb nut. A 3/4 inch screw is likely to be marginal with
both ring terminals installed. A longer screw works electrically but leaves a
snag-prone exposed end.

### Terminal Hardware Stack

Insert each screw from the back. From back to front, use this order:

```text
pan-head screw
  -> #6 flat washer
  -> printed plate
  -> #6 flat washer
  -> #6-32 hex nut (tightened to make a fixed stud)
  -> radiator ring terminal
  -> feedline ring terminal
  -> #6 internal-tooth lock washer
  -> #6-32 flanged knurled thumb nut
```

The two ring tongues must touch each other directly; do not place a plain
washer between them. Hold the base hex nut with a wrench when loosening the
thumb nut so the fixed stud does not unwind. Tighten the thumb nut firmly by
hand, not with pliers. The tooth washer follows the same anti-rotation principle
used in the [ARRL end-fed kit instructions](https://www.arrl.org/end-fed-half-wave-antenna-kit),
where tooth washers keep a cable lug from rotating.

### Stud-Hole Fit Test

Printed holes vary by printer and filament. Before printing the full center,
set:

```scad
render_mode = "stud_fit_test";
```

The small, single-piece coupon has 3.8, 4.0, and 4.2 mm holes. The **notched
end identifies the 3.8 mm hole**, followed by 4.0 and 4.2 mm moving away from
the notch. Use the smallest hole through which the actual #6-32 screw passes
without threading or forcing it. Set `stud_hole_clearance` to the selected hole
diameter minus `stud_nominal_d`, then return `render_mode` to `"center"`.

### Radiator Snap-Fit Test

The removable radiator channels are thicker and more heavily restrained than
the feedline-spacer jaws, so validate them with their own tiny coupon. Set:

```scad
render_mode = "radiator_fit_test";
```

The three channels have 0.72, 0.82, and 0.92 mm throats. The **notched end
identifies the 0.72 mm sample**, followed by 0.82 and 0.92 mm moving away from
the notch. Choose the narrowest throat that lets the actual wire snap through
without jacket damage or permanent jaw spreading, then pull the wire sideways
and toward the solid end of the coupon to check retention. Set
`radiator_slot_width` to that result and return `render_mode` to `"center"`.

### Wiring and Assembly

Treat the face carrying the base nuts, ring terminals, and thumb nuts as the
front:

1. Bend a short section of each radiator from front to back through its outer
   side channel and snap it sideways through the upward-facing tapered slot.
   Route the wire along the back toward the inner radiator channel.
2. Bring the wire back to the front through the inner channel and snap it
   through that channel's downward-facing slot. The opposing slots capture the
   removable two-point weave without requiring the long radiator end or its
   ring terminal to pass through a closed hole.
3. Leave a small relaxed loop between that relief hole and the stud. Strip,
   crimp, pull-test, and heat-shrink its ring terminal.
4. Bring each feedline conductor upward and pass it front-to-back through its
   lower hole, then back-to-front through the upper feedline-relief hole.
5. Leave another small relaxed loop, terminate it, and stack both rings on the
   matching stud as documented above.
6. Check that the radiator and feedline weaves take the load before the ring
   terminals become taut. Verify continuity across each stud and verify that
   there is no continuity between the two studs.

To change bands or radiator lengths, lower the antenna, remove only the two
thumb nuts, exchange the radiator pair, and reassemble the same stack. Replace
radiators as a matched pair. Recheck the thumb nuts after the first deployment
and inspect the wire jacket, crimps, and printed holes before each use.

## Printing

PETG is the intended material because the spacer jaws need some flex and both
center styles may see sun and field handling.

Suggested starting settings:

- print every part flat, with either center's broad plate face on the bed;
- no supports;
- 0.20 mm layer height;
- 0.4 mm nozzle;
- four walls;
- 100% infill for the tiny spacers; and
- at least five top and bottom layers for the center.

PLA is suitable for quick dimensional test prints, but PETG should be used for
the snap-fit and outdoor validation. Physical fit and retention against the
actual wire remain required before field use.

## Command-Line Rendering

From the repository root:

```bash
openscad --hardwarnings \
  -o /tmp/balanced_feedline_spacer.stl \
  models/ham_radio/lightweight_balanced_feedline/balanced_feedline_spacer.scad

openscad --hardwarnings -D 'render_mode="channel_fit_test"' \
  -o /tmp/balanced_feedline_channel_fit_test.stl \
  models/ham_radio/lightweight_balanced_feedline/balanced_feedline_spacer.scad

openscad --hardwarnings -D 'render_mode="slot_fit_test"' \
  -o /tmp/balanced_feedline_slot_fit_test.stl \
  models/ham_radio/lightweight_balanced_feedline/balanced_feedline_spacer.scad

openscad --hardwarnings \
  -o /tmp/doublet_center_strain_relief.stl \
  models/ham_radio/lightweight_balanced_feedline/doublet_center_strain_relief.scad

openscad --hardwarnings \
  -o /tmp/doublet_center_terminal_strain_relief.stl \
  models/ham_radio/lightweight_balanced_feedline/doublet_center_terminal_strain_relief.scad

openscad --hardwarnings -D 'render_mode="stud_fit_test"' \
  -o /tmp/doublet_center_terminal_stud_fit_test.stl \
  models/ham_radio/lightweight_balanced_feedline/doublet_center_terminal_strain_relief.scad

openscad --hardwarnings -D 'render_mode="radiator_fit_test"' \
  -o /tmp/doublet_center_terminal_radiator_fit_test.stl \
  models/ham_radio/lightweight_balanced_feedline/doublet_center_terminal_strain_relief.scad
```
