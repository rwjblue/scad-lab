# Modular dipole center with removable winders

Two identical K6ARK-style winders dock to the center with **four retained studs**.
With the BNC at the bottom and the hoist eye at the top, pinch the upper and
lower orange tabs on the **right** to
release the right stud of **both** winders. The matching left pair releases
their left studs. The two winders remain identical prints.

The intended release uses **one hand, one end at a time**. After lifting the released end
clear, its tabs return above the broad, flat stud tops and the center rests on
those heads. This holds the first end open while the same hand changes ends.

**The current prints combine revision-2 retention with 4 mm standoffs.**
The first print looked good and its
spring controls felt comfortable, but the winders slipped free even with the
catches beneath the heads. Revision 2 enlarges the retaining lips and increases
catch movement with a slightly longer pinch. Its independent critic supports another
physical trial; secure retention has not yet been demonstrated on this revision.

`standoff` directly sets the gap in millimeters from the winder's top surface
to the center's underside. It defaults to 4 mm for both wire-space presets.
**Compact loaded fit is experimental.** The unchanged wire reservation overlaps
the lowered center, and the finger-clearance result changes. The planned static
tie route remains clear, but check your actual wound wire, ties and finger
access; increase `standoff` if needed.

Start with the [retention coupon](retention_coupon.stl). After it passes the
checks below, print the [complete three-piece plate](print_layout.stl), or one
[center](center.stl) and two copies of the [winder](winder.stl).
**Use the revision-2 center and two matching-height revision-2 winders.** Mixing the
new larger heads with the first center, or old winders with the new center,
does not provide the revised fit. An already printed revision-2 center can be
reused with the shorter winders; the standoff change does not alter that center.

![Four retained studs and mirrored end controls](images/assembled.png)

## What changed after the first print

The original catch had only 0.80 mm nominal overlap, reduced to approximately
0.45 mm when the stud moved outward within its clearance. The revised head is
7.0 mm across, up from 6.0 mm, giving 1.30 mm nominal overlap and 0.95 mm after
the same outward movement. The springs have a slightly longer flexible root
and a wider outer span, allowing more catch movement with a 3.30 mm paddle
stroke, 0.15 mm more per tab than the first print. The retaining geometry,
raised controls and 10.1 mm BNC hole are unchanged by the subsequent standoff
reduction. The wire-space assumptions also remain unchanged.

Small dimensional errors and a rounded head underside can consume a shallow
lip or let it push the spring aside. The new
[retention audit](review/retention_audit.json) measures actual exported contact
shapes under stated edge-loss, spring-set and clearance assumptions. These are
geometric screens, not measurements of the failed print or predictions of pull
force. The [design review](review/DESIGN.md) records the failure and limitations.

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
34 mm at rest; a full paired pinch closes it by about 6.6 mm. The intended
contact is on the upper part of those faces. Lowering the center reduces both
clearance above the wound wire and access beneath the lifting bridges. The
compact parts do not inherit the previous finger-clearance result; check the
complete loaded assembly, including with gloves. The lower 4 mm plate edges
provide less clearance still.

The sampled guide-clearance check allows a small sideways settling movement during
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

The two ties retain the wound wire. The four catches are intended to retain the
three printed parts, with a whole-bundle tie available as backup. Confirm the
revised catches hold the printed assembly before relying on them for transport.

## Print and fit

The default print set is **one center and two identical winders**. Both
wire-space presets use these same printed parts; the presets change only the
displayed wire and tie reservations.
Use matching winder heights and the current revision for all three parts.

| Item | File | Quantity |
| --- | --- | ---: |
| Retention coupon: paired receiver and two independent stud feet; print first | [retention_coupon.stl](retention_coupon.stl) | 1 plate |
| Paired release coupon: receiver and one joined two-stud foot | [fit_coupon.stl](fit_coupon.stl) | Optional 1 plate |
| Center, selected 10.1 mm BNC opening | [center.stl](center.stl) | 1 |
| Winder, 4 mm standoff | [winder.stl](winder.stl) | 2 identical |
| Complete default plate | [print_layout.stl](print_layout.stl) | 1 |

Choose separate files or the complete plate. Parts are separately printed and
assembled; this is **not a print-in-place assembly**. The flexible tabs are part
of the center print and bend in the bed's XY plane. The default BNC clearance
remains 0.20 mm per side: 10.1 mm diameter and 9.25 mm from the D-flat to the
opposite edge. Both wire-space presets use the same center.

**Print the retention coupon first.** Its two independent feet let each stud
move outward as a separate winder can. The joined foot in the older paired
coupon prevents that independent movement and can make retention feel better
than it is in the full assembly.

1. Check the slots are open and each head has a clean, flat underside. The
   revised head projects 1.5 mm beyond its neck on the catch side; inspect this
   printed overhang closely.
2. Point the head's straight edge toward the fixed outer wall, away from the
   middle wire-hole bar. Pinch a catch and seat that loose foot until the
   receiver rests on the stud shoulder. Let the catch return **beneath** the
   head, not onto its parking top.
3. Hold the fixed receiver and foot with fingers clear of the tab. Move the
   stud toward the fixed outer wall, then pull it straight out and gently rock
   it. The intended response is about 0.8 mm of axial play followed by a
   positive stop. Free withdrawal fails this check.
4. Pinch the tab: the foot should now release without forcing it. Repeat with
   the other foot and catch, then repeat at least ten times, checking return,
   edge wear, whitening or cracks. This is a fit check, not a fatigue rating.

The optional paired coupon checks whether both catches release with one
comfortable pinch. Initial PETG settings remain 0.20 mm layers, five walls and
solid infill, subject to the actual printer and coupons. No release force,
fatigue life or cold-weather material performance has been measured.

Then print the complete assembly. Check each winder separately for retention,
then test the one-hand sequence while both winders carry the actual wire and
silicone ties. A coupon cannot establish the effects of full-winder flex, the
four-stud peel, glove access or a comfortable full grip.

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
each face; the 80 m preset reserves 8 mm. These reservations remain full size
when `standoff` changes; the display does not shrink the coil or ties to fit.
The presets do not change the printed parts, wing length, span or support
height. These are space assumptions, **not verified wire capacities**.
Trial about 10.5 m per leg for the default use and about 21 m for an 80 m storage
test; these figures are not antenna cutting lengths. Measure the actual maximum
bundle depth and adjust `wire_face_bulge` accordingly.

At the compact default, portions of the wire reservation intersect the center.
The schematic ties remain clear in their planned static route. These proxies
do not measure your wound coil or every tie position, and the shorter supports
cannot claim clearance for the original assumed load. Seat
the center without compressing wire or trapping a tie in a catch. If the loaded
pack or grip does not fit, increase `standoff`. The earlier taller geometry used
8 mm supports for the 40 m reservation and 11 mm for the 80 m reservation.

The winders sit 26 mm either side of the centerline to leave space for the
inward release tongues and finger access.

| Exported estimate at default wing length/span | 40 m space | 80 m space |
| --- | ---: | ---: |
| Bare assembled packet | 140 × 127 × 32 mm | 140 × 127 × 32 mm |
| Packet including reserved wire envelope, before hardware and ties | 150 × 137 × 37 mm | 150 × 137 × 40 mm |

The envelope dimensions describe occupied bounds; they do not establish
clearance between the reserved wire and the center.

Use the current validation report or slicer for the revised parts' mass estimate;
wire, metal and silicone add to the printed mass. The complete print layout
occupies about 140 × 180 mm; recenter in the slicer and allow any required brim
space, or use the separate files.

Larger settings change these dimensions and the print-bed footprint. All four
heads have intentional axial
clearance so the opposite end can tilt during release; inspect transport play
on the print rather than assuming a tight, silent fit.

## Adjustable dimensions

Open [modular_dipole.scad](modular_dipole.scad) in OpenSCAD and use the
Customizer, or supply `-D` values when exporting. Dimensions below are mm.
The defaults produce the compact parts with
revision-2 retention. Other public sizing and hole controls keep their previous
defaults and ranges.

| Parameter | Default | Allowed range and purpose |
| --- | ---: | --- |
| `wing_length` | 37.5 | 37.5–60; Y-direction reach from the winding datum to the horn tips |
| `winding_span` | 140 | 140–200; distance between the lower outer tips |
| `preset` | `40m` | `40m` or `80m`; selects automatic face buildup only |
| `wire_face_bulge` | 0 | 0 selects 5/8 by preset; otherwise 2–12 buildup on **each** face |
| `wire_edge_bulge` | 5 | 2–5; displayed wire overhang around the winding region |
| `standoff` | 4 | 2.5–25; distance from the winder's top surface to the center's underside, independent of wire-space preset |
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

Increasing wing length or span adds winding space. `standoff` is the support
height in millimeters: use `4` for the compact default, `5.5` for an intermediate
trial or `8` for more space. An `11` mm setting restores the earlier taller
80 m support height. Changing this value does not change the coil or tie
reservations, and selecting a wire-space preset does not change this value.
Both headed posts and the alignment-guide support follow this setting; head,
catch and guide dimensions above the seat stay fixed. None of these settings
specifies a guaranteed wire length. Actual capacity also depends on insulation
diameter, winding tension and the figure-eight pattern. Print two winders with
matching height settings; the center is shared unless its hole settings change.

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
# Set 8 mm between the winder's top surface and the center's underside.
openscad --backend=Manifold -D 'part="winder"' -D 'standoff=8' \
  -o /tmp/dipole-8mm-winder.stl models/ham_radio/modular_dipole/modular_dipole.scad

# Try 5.5 mm supports; print two identical winders.
openscad --backend=Manifold -D 'part="winder"' -D 'standoff=5.5' \
  -o /tmp/dipole-5p5mm-winder.stl models/ham_radio/modular_dipole/modular_dipole.scad

# Larger winding region with 11 mm supports and the 80 m wire reservation.
openscad --backend=Manifold -D 'part="print_layout"' -D 'preset="80m"' \
  -D 'wing_length=50' -D 'winding_span=170' -D 'standoff=11' \
  -o /tmp/dipole-large-plate.stl models/ham_radio/modular_dipole/modular_dipole.scad

# A center with wider wire bores and enough material between their mouths.
openscad --backend=Manifold -D 'part="center"' -D 'wire_hole_d=3.6' \
  -D 'wire_hole_pitch=5.7' -D 'wire_chamfer=0.4' \
  -o /tmp/dipole-center-large-holes.stl models/ham_radio/modular_dipole/modular_dipole.scad
```

Check the exported layout against your printer's bed size: the largest
60 mm wing / 200 mm span combination occupies about 217.44 × 224.54 mm,
before adding a brim. The dry mechanism audit covers both release orders and
the two default presets. Loaded wire, tie and fingertip results are reported
separately; compact-default collisions require a physical fit check. A separate
parameter screen checks
coordinated custom configurations for mesh quality, requested dimensions,
unchanged docking geometry, seated retention, wire reservations, support height
and separated print parts. It does not prove every combination in these ranges
or repeat the full release and hand-access audit for customized parts.

## Reproduce and review

Run these commands from the repository checkout. The STL bundle also includes
the editable CAD source and digital check reports. The package task
writes `modular-dipole-STLs.zip`; generated ZIPs are not committed.
`passed_with_fit_caveats` means the dry CAD checks completed successfully while
the report's `loaded_fit_status=requires_physical_check` records unresolved
loaded fit. It does not mean the compact pack cleared every load and grip proxy.

```sh
mise run modular-dipole:check
# Optionally also compare against your original K6ARK STL:
# mise run modular-dipole:check -- --source /path/to/K6ARK_Wire_Winder.stl
mise run modular-dipole:render
mise run modular-dipole:package
```

[Source](modular_dipole.scad), [digital checks](validation.json),
[retention margin audit](review/retention_audit.json),
[design and ergonomics review](review/DESIGN.md).
See [NOTICE.md](NOTICE.md) for the upstream model attribution and licensing.
