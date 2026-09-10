# A5: direct solder with a shallower BNC shelf

A5 removes the M3 holes and terminal hardware from A4 and brings the BNC **6 mm closer to the frame**. The [layout](layout-a5.png), [SVG](layout-a5.svg), and [numeric geometry](layout-a5.json) preserve the accepted source-derived layout. This historical snapshot is now implemented in the [parameterized SCAD project](../../../models/ham_radio/dipole_winder/README.md), which documents the current printable geometry, subsequent review changes, and **10.1 mm default BNC cutout**.

## Retained geometry

The supplied K6ARK wireframe STL is mirrored at scale 1, with its exterior and horn positions unchanged: **75 × 140 × 5 mm**. The Ø6 suspension eye remains at `(0,63)`. Upper native openings are filled locally for the relief holes; the lower and central openings remain.

Each upper arm retains three **Ø3.2 mm relief bores at 7 mm pitch**, with **0.5 mm × 45° chamfers on both faces**. Right-hand centers are `(20.000,55.050)`, `(26.270,58.163)`, and `(32.539,61.276)`; the left side mirrors X. Adjacent chamfer mouths have 2.8 mm of material between them. These holes retain the planned fit for the 26 AWG wire and thin-jacketed 22 AWG examples documented in the [current model's dimensions and fit notes](../../../models/ham_radio/dipole_winder/README.md#dimensions-and-fit); pull/flex-check the weave with the actual wire.

## Compact connector placement

| Feature | A5 proposal |
| --- | ---: |
| BNC axis Z, measured from the frame back | 15 mm |
| Axis distance from the 5 mm frame's front face | 10 mm |
| Shelf depth, measured from the frame back | 24 mm |
| Shelf projection beyond the frame's front face | 19 mm |
| Shelf width × mounting thickness | 26 × 3 mm |
| Reserved connector hardware envelope | Ø18 mm |
| Envelope clearance to frame face | 1 mm |
| Ø12.7 connector barrel clearance to frame face | 3.65 mm |

The axis and shelf depth both decrease by 6 mm from A4. The Ø18 envelope comes from the existing [dipole center](../../../models/ham_radio/dipole_center/dipole_center.scad), where a 4 mm plate and z14 axis leave the same 1 mm gap. It is a CAD allowance, not a measured envelope for the entire connector, shell tag, and attached coax plug.

The shelf's vertical position remains independent of the horns: `shelf_top_y = target_contact_y − actual_rear_projection_above_panel`. The drawing retains a **12 mm estimated rear projection**, giving a shelf top at `y≈43.05` and rear contact at the inner relief level, `y≈55.05`. The projection is not explicitly dimensioned in the [Amphenol drawing hosted by DigiKey](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/8637/031_221_rfx_customer_drawing.pdf); tune shelf Y from the assembled connector before final fit signoff.

Use two flanking ribs, provisionally centered at `x=±10.5` and 3 mm thick, keeping their inner faces outside the Ø18 hardware space. Protect that space through any root reinforcement too. The old central underside gusset would interfere with the inward-shifted connector. The side-view illustration shows the flanking ribs as a dashed projection, not a central section. Orient the shell tag away from the frame and check the real nut/tag, coax coupling, and tightening access during CAD assembly review.

## Direct-solder wiring

There are **no M3 holes, posts, ring terminals, or separate terminal jumpers** in A5. From each antenna leg, weave through the three holes from outside inward: back-to-front, front-to-back, then back-to-front. Leave a relaxed insulated tail to the BNC center solder cup or shell solder tag. Thread before soldering; keep antenna tension in the frame and weave, with slack at the solder joints.

The earlier 10 mm stud-to-relief requirement no longer applies because the studs are removed. The relief rows stay in their accepted A4 locations and retain their 7 mm pitch.

## Verification

Run [layout_a5.py](layout_a5.py) with the source STL path. The generator checks the unchanged source-derived exterior and 75 × 140 mm bounds, containment of all seven frame holes, 7 mm relief pitch, and 1 mm reserved hardware-to-frame clearance. The saved JSON records no stud centers and the revised shelf dimensions.

The layout generator does not modify the source STL. The [finished SCAD project](../../../models/ham_radio/dipole_winder/README.md) supplies the printable model and its validation; full hardware fit, wire grip, and winding clearance still require physical assembly checks.
