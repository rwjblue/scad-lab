# Modular dipole build notes

The [model README](../README.md) covers printing and use. These notes describe
custom sizes, fit coupons and regeneration. The [design review](DESIGN.md)
records retention changes, mechanical assumptions and physical acceptance.

The second print's larger lips improved retention but still let the winders
come free. Revision 3 increases the lips again and remains physically unproved.
Use a matched revision-3 center and two revision-3 winders; previous heads and
receiving passages are not the revised fit.

## Public parameters

Open [modular_dipole.scad](../modular_dipole.scad) in OpenSCAD's Customizer,
or supply `-D` arguments. Dimensions are millimeters. Individual allowed ranges
do not guarantee that every combination fits; the model also applies the
combined limits below.

| Parameter | Default | Allowed values and purpose |
| --- | ---: | --- |
| `part` | `print_layout` | `center`, `winder`, `print_layout`, `coupon`, `fit_coupon`, `retention_coupon`; assembly views listed below |
| `preset` | `40m` | `40m` or `80m`; selects automatic face buildup only |
| `show_wire` | `false` | Show reserved coil space in assembly previews |
| `wing_length` | 37.5 | 37.5–60; Y-direction reach from the winding datum to the horn tips |
| `winding_span` | 140 | 140–200; distance between the lower outer tips |
| `wire_face_bulge` | 0 | 0 selects 5/8 by preset; otherwise 2–12 buildup on each face |
| `wire_edge_bulge` | 5 | 2–5; displayed wire overhang around the winding region |
| `standoff` | 4 | 2.5–25; distance from winder top to center underside, independent of preset |
| `wire_hole_inner_x` | 28 | 27–30; centerline to the first strain-relief hole on each side |
| `wire_hole_pitch` | 5.5 | 4–6.5; center-to-center spacing within each three-hole group |
| `wire_hole_d` | 3.2 | 2.6–3.6; strain-relief bore diameter |
| `wire_chamfer` | 0.5 | 0–0.6; entry chamfer on wire holes and hoist eye |
| `terminal_hole_d` | 3.4 | 3.1–3.6; M3 terminal clearance |
| `hang_hole_d` | 6 | 4–6; hoist-eye bore diameter |
| `bnc_hole_d` | 10.1 | 9.7–10.2; finished D-hole diameter; flat-to-edge distance is diameter minus 0.85 |

The other `part` values are viewing aids: `assembled`, `exploded`, `released`,
`peel`, `parked` and `wire_envelopes`. Export individual parts or `print_layout`
for printing. `coupon` is an alias for `fit_coupon`, the paired-pinch test.
Use the supplied `bnc_fit_coupon.stl` for the connector test; it is generated
with `part="coupon"` in the neighboring `dipole_center.scad`.

`wing_length` measures reach along the source winder's Y axis from Y=0, not
diagonal arm length. Rounded tips move along their existing arm directions.
`winding_span` measures the lower tips; extended horns can project beyond
them, so the total width can be larger. Both settings preserve the central
tie brace and docking stations. Snap dimensions remain hidden because changing
them requires another mechanism review.

`standoff` sets both headed-post shoulders and the alignment-guide support.
Head, catch and guide dimensions above the seat remain fixed. Print two
winders with matching height settings; within the same retention revision,
the center is shared unless its hole settings change. The earlier taller
supports were 8 mm for the 40 m reservation
and 11 mm for the 80 m reservation.

Wire reservations remain full size when support height changes. They do not
establish capacity: trial approximately 10.5 m per leg for 40 m storage or
21 m for 80 m storage with the actual wire. These are storage-test lengths,
not antenna cutting lengths. Insulation diameter, winding tension and the
figure-eight pattern affect capacity. At the compact default, the coil
reservation intersects the center; increase `standoff` if the actual load
cannot seat freely or leaves insufficient finger access.

## Combined hole limits

Strain-relief settings must leave at least 4 mm beyond the specified Panduit
terminal barrel, 1.2 mm between chamfer mouths and 3 mm between the outer
mouth and the bar end. All three conditions must hold:

```text
wire_hole_inner_x - 10 - wire_hole_d/2 - wire_chamfer - 11.176 >= 4
wire_hole_pitch - wire_hole_d - 2*wire_chamfer >= 1.2
wire_hole_inner_x + 2*wire_hole_pitch + wire_hole_d/2 + wire_chamfer <= 42
```

For example, 3.6 mm wire holes fit with `wire_hole_pitch=5.7` and
`wire_chamfer=0.4`, keeping `wire_hole_inner_x=28`. Terminal centers,
strain-relief row height and hoist-eye position stay fixed. Adjust connector
clearance through `bnc_hole_d`; do not scale the whole assembly to fit hardware.

## Fit coupons

The [retention coupon](../retention_coupon.stl) has a paired receiver and two
independent single-stud feet. Point each head's straight edge toward the fixed
outer wall, away from the middle wire-hole bar. Pinch its catch and seat the
foot fully on its shoulder, then let the tongue return beneath the head.
Inspect the revision-3 head's 1.8 mm underside overhang and confirm the slots are open.
Follow the pull, rock, release and repeated-cycle checks in the
[physical acceptance procedure](DESIGN.md#physical-acceptance).

The optional [paired-pinch coupon](../fit_coupon.stl) uses one joined two-stud
foot to check both springs together. It prevents the independent outward
movement that the retention coupon tests; use it for ergonomics after the
independent feet hold securely. The [BNC coupon](../bnc_fit_coupon.stl) checks
connector fit in the upright print orientation. Neither coupon establishes
full-winder flex, loaded release, glove access or fatigue life.

## Example exports

Run from the repository root:

```sh
# Try 5.5 mm supports; print two identical winders.
openscad --backend=Manifold -D 'part="winder"' -D 'standoff=5.5' \
  -o /tmp/dipole-5p5mm-winder.stl models/ham_radio/modular_dipole/modular_dipole.scad

# Larger winding region with 11 mm supports and the 80 m wire reservation.
openscad --backend=Manifold -D 'part="print_layout"' -D 'preset="80m"' \
  -D 'wing_length=50' -D 'winding_span=170' -D 'standoff=11' \
  -o /tmp/dipole-large-plate.stl models/ham_radio/modular_dipole/modular_dipole.scad

# A center with wider wire bores and material between their mouths.
openscad --backend=Manifold -D 'part="center"' -D 'wire_hole_d=3.6' \
  -D 'wire_hole_pitch=5.7' -D 'wire_chamfer=0.4' \
  -o /tmp/dipole-center-large-holes.stl models/ham_radio/modular_dipole/modular_dipole.scad
```

Check the exported layout against the bed size. The largest 60 mm wing /
200 mm span combination occupies about 217.44 × 224.54 mm before a brim.

## Regenerate and inspect

Run from the repository checkout:

```sh
mise run modular-dipole:check
# Optionally compare with your original K6ARK STL:
# mise run modular-dipole:check -- --source /path/to/K6ARK_Wire_Winder.stl
mise run modular-dipole:render
mise run modular-dipole:package
```

The [validation report](../validation.json) records mesh checks, both dry release
orders and separate loaded-fit results. `passed_with_fit_caveats` means the
dry checks completed while `loaded_fit_status=requires_physical_check` records
unresolved loaded fit. It does not mean every load and grip proxy cleared.
The parameter screen samples coordinated settings for mesh quality, dimensions,
fixed interfaces, seated capture and print separation; it does not repeat the
full motion and hand-access audit for every custom combination. Check the
report's recorded revision and source hashes; a passing report for revision 2
does not establish revision-3 capture or release, and neither proves physical
retention.

Keep the editable model's relative dependency paths intact. The rendered model
uses embedded geometry, so OpenSCAD does not need the original downloaded STL.
See [NOTICE.md](../NOTICE.md) for source identity, regeneration and attribution.
The [flyer notes](../marketing/README.md) describe rebuilding the optional PDF.
