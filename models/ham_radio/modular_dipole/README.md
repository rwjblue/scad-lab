# Modular dipole center with removable winders

Two identical K6ARK-style winders dock to the center with **four retained studs**.
With the BNC at the bottom and the hoist eye at the top, pinch the upper and
lower orange tabs on the **right** to
release the right stud of **both** winders. The matching left pair releases
their left studs. The two winders remain identical prints.

The intended release uses **one hand, one end at a time**. After lifting the released end
clear, its tabs return above the broad, flat stud tops and the center rests on
those heads. This holds the first end open while the same hand changes ends.

Print the [complete three-piece plate](print_layout.stl), or one
[center](center.stl) and two copies of the [winder](winder.stl).

**Accepted by the independent critic for printing and physical trials.** At
the default winding dimensions, CAD checks cover both wire-space presets and
both release orders, including individual
support contacts and 264 independently sampled parked configurations. Results
are in [validation.json](validation.json) and the reviews below.
Hand operation, glove fit and durability still require the printed trial.
Parameterization preserves the geometry selected for that first print.

![Four retained studs and mirrored end controls](images/assembled.png)

## The one-hand sequence to test

Begin with the tied winders supported on a surface or your lap. The surface
supports their weight; it does not by itself restrain them against lifting.

1. Pinch the right upper/lower tabs inward with thumb and forefinger.
2. Use another finger on the **fixed outer lifting edge**, between those tabs,
   to lift the right end of the center. Keep the tied winders down with the
   same hand or let their weight provide the reaction if sufficient.
3. Release the pinch and lower that end gently onto the flat head tops. It
   should remain visibly raised. The left end remains retained.
4. Move the same hand to the left, pinch its tabs, and lift the fixed left edge
   until the center is level. Then lift the center clear of the guide pins.
5. Secure the center low at the mast, open one winder's silicone tie, and walk
   that leg outward. Repeat for the other leg, then hoist the antenna.

Both left-first and right-first operation must work. The resting position is
for handling, not transport. The full assembly is secured only when all four
heads are through the openings and all four catches have returned beneath them.

The CAD model can establish contact, capture and clearance. **Whether the
winders stay down during that initial one-hand lift, and whether the gesture
works in gloves, require the physical trial.** Free-air one-hand use is not yet
demonstrated. The fixed lifting edges keep lift force off the flexible tabs.

The raised finger faces are 10 mm high. Their contact span is approximately
34 mm at rest; a full paired pinch closes it by about 6.3 mm. The intended
contact is on the upper part of those faces, above the wound wire. The lower
4 mm plate edges do not provide the same loaded-finger clearance.

The guide-clearance proof allows a small sideways settling movement during
the first lift. Support the winders so they can move slightly instead of
clamping them immovably. The physical trial must confirm that this feels like
an easy guided release, without needing a second hand or deliberate jiggling.

![Pinch pairs, fixed lifting edges, and the park–level–lift sequence](images/release_explainer.png)

## Reassembly

**Pinch to seat each end**, then release the tabs under the heads. A straight
push alone is
not the intended docking action. Close each winder's silicone tie first,
align the four studs, and keep the relaxed antenna tails outside the slots
and away from the lifting edges. Check each end with a gentle pull.

Two additional smooth guide pins maintain alignment while the ends lift. They
do not retain the center by friction; the four headed studs provide retention.

The two ties retain the wound wire. The four catches retain the three printed
parts, so a whole-bundle tie is optional backup rather than a required closure.

## Print and fit

The default print set is **one center and two identical 40 m winders**.
Use matching winder heights. These are the parts selected for the first full
prototype print on 10 September 2026.

| Item | File | Quantity |
| --- | --- | ---: |
| Paired release coupon | [fit_coupon.stl](fit_coupon.stl) | 1 plate |
| Center, selected 10.1 mm BNC opening | [center.stl](center.stl) | 1 |
| Default 40 m space winder | [winder.stl](winder.stl) | 2 identical |
| Optional 80 m space winder | [winder_80m.stl](winder_80m.stl) | 2 identical |
| Complete default plate | [print_layout.stl](print_layout.stl) | 1 |
| Complete 80 m plate | [print_layout_80m.stl](print_layout_80m.stl) | 1 |

Choose separate files or the complete plate. Parts are separately printed and
assembled; this is **not a print-in-place assembly**. The flexible tabs are part
of the center print and bend in the bed's XY plane. The default BNC clearance
remains 0.20 mm per side: 10.1 mm diameter and 9.25 mm from the D-flat to the
opposite edge. Both wire-space presets use the same center.

Start with the paired coupon. Check all slots are open and the flat head
undersides print cleanly. Its two catches should release with one comfortable
pinch and return freely. Initial PETG settings remain 0.20 mm layers, five walls
and solid infill, subject to the actual printer and coupon. No release force,
fatigue life or cold-weather material performance has been measured.

Then print the complete assembly and test the one-hand sequence while both
winders carry the actual wire and silicone ties. A coupon checks the local
latch; it cannot establish the four-stud peel or a comfortable full grip.

## Wire, ties and space

The default winding region retains the K6ARK outline at original scale. Larger
winder settings extend the arms while preserving the central tie brace and
docking stations.
Wind **tip first**, working toward the center, so the center end is outside the
figure-eight coil for deployment. Leave roughly 100–150 mm of relaxed tail,
adjusted to the final hardware and release path. The short UMUST ties stay
captive around each winder's upper brace and close around the wound wire before
docking. Button and strap dimensions remain provisional until measured.

With `wire_face_bulge=0`, the default preset reserves 5 mm of wire buildup on
each face; the 80 m preset reserves 8 mm. The presets change clearance height,
not wing length or span. These are space assumptions, **not verified wire capacities**.
Trial about 10.5 m per leg for the default use and about 21 m for an 80 m storage
test; these figures are not antenna cutting lengths. Measure the actual maximum
bundle depth and adjust `wire_face_bulge` accordingly.

The winders sit 26 mm either side of the centerline to leave space for the
inward release tongues and finger access.

| Exported estimate at default wing length/span | 40 m space | 80 m space |
| --- | ---: | ---: |
| Bare assembled packet | 140 × 127 × 36 mm | 140 × 127 × 39 mm |
| Reserved wire envelope, before hardware and ties | 150 × 137 × 41 mm | 150 × 137 × 47 mm |
| Three printed parts, solid PETG estimate | 50.0 g | 50.9 g |

Mass uses 1.27 g/cm³ and excludes wire, metal and silicone. Actual slicer mass
will differ. Both complete print layouts occupy about 140 × 179.54 mm; recenter
in the slicer and allow any required brim space, or use the separate files.

Larger settings change these dimensions and the print-bed footprint. All four
heads have intentional axial
clearance so the opposite end can tilt during release; inspect transport play
on the print rather than assuming a tight, silent fit.

## Adjustable dimensions

Open [modular_dipole.scad](modular_dipole.scad) in OpenSCAD and use the
Customizer, or supply `-D` values when exporting. All dimensions below are mm.
The default values reproduce the current first-print parts.

| Parameter | Default | Allowed range and purpose |
| --- | ---: | --- |
| `wing_length` | 37.5 | 37.5–60; Y-direction reach from the winding datum to the horn tips |
| `winding_span` | 140 | 140–200; distance between the lower outer tips |
| `preset` | `40m` | `40m` or `80m`; selects automatic face buildup only |
| `wire_face_bulge` | 0 | 0 selects 5/8 by preset; otherwise 2–12 buildup on **each** face |
| `wire_edge_bulge` | 5 | 2–5; displayed wire overhang around the winding region |
| `wire_gap` | 3 | 3–5; extra height above the coil for the tie and air gap |
| `wire_hole_inner_x` | 28 | 27–30; centerline to the first strain-relief hole on each side |
| `wire_hole_pitch` | 5.5 | 4–6.5; center-to-center spacing within each three-hole group |
| `wire_hole_d` | 3.2 | 2.6–3.6; strain-relief bore diameter |
| `wire_chamfer` | 0.5 | 0–0.6; entry chamfer on wire holes and hoist eye |
| `terminal_hole_d` | 3.4 | 3.1–3.6; M3 terminal clearance |
| `hang_hole_d` | 6 | 4–6; hoist-eye bore diameter |
| `bnc_hole_d` | 10.1 | 9.7–10.2; finished D-hole diameter; flat-to-edge distance is diameter minus 0.85 |

`wing_length` measures reach along the source winder's **Y axis**, starting at
Y=0; it is not the diagonal arm length. The rounded tips move along the existing
arm direction. `winding_span` measures the lower tips: extended horns can project
beyond them, making the total width larger. The preview and print layout use
the actual profile bounds. Both controls enlarge the source profile; the
central docking and tie-brace geometry stays fixed. Snap dimensions remain
hidden because changing them requires another mechanism review.

Increasing wing length or span adds winding space, while face buildup and
`wire_gap` raise the stud shoulders to clear the tied coil. None specifies a
guaranteed length of wire. Actual capacity also depends on insulation diameter,
winding tension and the figure-eight pattern. Print two winders with matching
height settings; the center is shared unless its hole settings are changed.

The strain-relief controls interact. The model rejects combinations that leave
less than 4 mm beyond the specified Panduit terminal barrel, 1.2 mm between
chamfer mouths, or 3 mm between the outer mouth and the bar end. In parameter
terms, all three conditions must hold:

```text
wire_hole_inner_x - 10 - wire_hole_d/2 - wire_chamfer - 11.176 >= 4
wire_hole_pitch - wire_hole_d - 2*wire_chamfer >= 1.2
wire_hole_inner_x + 2*wire_hole_pitch + wire_hole_d/2 + wire_chamfer <= 42
```

For example, 3.6 mm wire holes fit with `wire_hole_pitch=5.7` and
`wire_chamfer=0.4`, keeping `wire_hole_inner_x=28`. Terminal centers, the
strain-relief row height and hoist-eye position stay fixed.

Example exports from the repository root:

```sh
# Larger winding region, with the automatic 80 m face-clearance setting.
openscad --backend=Manifold -D 'part="print_layout"' -D 'preset="80m"' \
  -D 'wing_length=50' -D 'winding_span=170' \
  -o /tmp/dipole-large-plate.stl models/ham_radio/modular_dipole/modular_dipole.scad

# A center with wider wire bores and enough material between their mouths.
openscad --backend=Manifold -D 'part="center"' -D 'wire_hole_d=3.6' \
  -D 'wire_hole_pitch=5.7' -D 'wire_chamfer=0.4' \
  -o /tmp/dipole-center-large-holes.stl models/ham_radio/modular_dipole/modular_dipole.scad
```

Check the exported layout against your printer's bed size: the largest
60 mm wing / 200 mm span combination occupies about 217.44 × 224.54 mm,
before adding a brim. The full release
audit covers the two default presets. A separate parameter screen checks six
coordinated custom configurations for mesh quality, requested dimensions,
unchanged docking geometry, seated retention, wire reservations and separated
print parts. It does not prove every combination in these ranges or repeat the
full release and hand-access audit for customized parts.

## Reproduce and review

Run these commands from the repository checkout. The STL bundle also includes
the editable CAD source and the completed proof reports. The package task
writes `modular-dipole-STLs.zip`; generated ZIPs are not committed.

```sh
mise run modular-dipole:check
# Optionally also compare against your original K6ARK STL:
# mise run modular-dipole:check -- --source /path/to/K6ARK_Wire_Winder.stl
mise run modular-dipole:render
mise run modular-dipole:package
```

[Source](modular_dipole.scad), [digital checks](validation.json),
[design and ergonomics review](review/DESIGN.md).
See [NOTICE.md](NOTICE.md) for the upstream model attribution and licensing.
