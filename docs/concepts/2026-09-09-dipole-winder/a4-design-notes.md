# A4: mirrored original dimensions

A4 supersedes A3's resized arms and extended upper neck. The [layout](layout-a4.png), [SVG](layout-a4.svg), and [numeric geometry](layout-a4.json) are derived directly from the supplied K6ARK wireframe STL. This is still a layout study, not a printable SCAD model.

## Fixed winder geometry

- Use the original source at **scale 1**, with no arm translation or rotation relative to its spine.
- Transform source coordinates to `new_x=source_y`, `new_y=source_x−62.5`, then mirror across `new_x=0` and union the profiles.
- The shared-spine mirrored frame is **75 mm wide × 140 mm high × 5 mm thick**. Mirroring overlaps the original backing-spine area; it does not simply double the source's full 54.04 mm width.
- Preserve the complete original exterior and all horn positions. The measured approximately 26.4° arm sweeps therefore carry through unchanged.
- Fill the upper native openings locally for the drilled head/arms. Lower and central native wireframe openings remain.
- Put the Ø6 mm suspension hole at `(0,63)`, inside the existing top end. There is no added neck or tail.

The layout generator asserts the 75 × 140 mm bounds and zero exterior-boundary difference between the mirrored source and the proposed frame. The new shelf is an added perpendicular mounting feature; its dimensions do not relocate the frame or horns.

## Wider strain-relief pitch

Use **7 mm pitch**, **Ø3.2 mm bores**, and **0.5 mm × 45° chamfers on both faces**. The same wire-jacket fit guidance from A3 applies for the planned 26 AWG wire and thin-jacketed 22 AWG examples.

Right-arm hole centers, with the left arm mirrored in X:

| Hole | X | Y |
| --- | ---: | ---: |
| Inner relief | 20.000 | 55.050 |
| Middle relief | 26.270 | 58.163 |
| Outer relief | 32.539 | 61.276 |
| Optional M3 | 4.000 | 47.550 |

The M3 clearance bores remain Ø3.4 mm. This arrangement gives approximately:

- **17.671 mm** stud-to-first-relief center distance.
- **13.871 mm** clear between the M3 bore edge and first relief chamfer mouth, exceeding the 10 mm minimum.
- **4.395 mm** from the end of the maximum 11.176 mm Panduit terminal reach to the first chamfer.
- **2.8 mm** material between adjacent Ø4.2 mm chamfer mouths.
- **4.876, 4.876, and 2.824 mm** minimum exterior ligaments beyond the three chamfer mouths.

An 8 mm row fits the holes by themselves. The 7 mm choice gives room for the terminal barrel and stud hardware above the shelf while retaining the original horn envelope.

Alternate the wire through all three holes and leave slack at the electrical termination. The wider pitch retains that routing, but geometry alone does not establish holding force: pull/flex-check it with the actual 26/22 AWG wire.

## Position the BNC independently

The intended rear solder-contact height is **at the inner strain-relief level**, currently `y≈55.05`. Set the shelf with:

`shelf_top_y = target_contact_y − actual_rear_projection_above_panel`

The current diagram uses an **estimated 12 mm rear projection above the 3 mm panel**, putting the shelf top at `y≈43.05`. This is an estimate from the [Amphenol side drawing hosted by DigiKey](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/8637/031_221_rfx_customer_drawing.pdf); that rear projection is not explicitly dimensioned there. Measure the actual connector/stack before treating this shelf Y coordinate as final. The rear contact's target level and the native horn coordinates remain fixed when tuning shelf placement.

Provisional hardware layout:

- BNC axis `z=21`; shelf depth about 30 mm, shelf thickness 3 mm.
- Place studs at `y=shelf_top_y+4.5`, above the shelf.
- Limit stud washers/nuts to Ø7 mm and assembled hardware to `z≤14`, or **9 mm proud of the z5 plate face**.
- This gives **1 mm** between stud hardware and shelf top, and **1 mm** between the two Ø7 mm washers.
- With a Ø12.7 mm connector envelope centered at z21, its nearest surface is z14.65: **0.65 mm conservative clearance** beyond the stud envelope. This is a conditional envelope check, not a verified full assembly.
- Route ring-terminal barrels outward toward their relief groups, above the shelf. Check the shell tag, jumpers, full fastener stack and coax coupling in the eventual 3D assembly.

Stud hardware is optional. The direct-solder variant leaves the M3 holes unused. Closed relief holes continue to capture a crimped ring terminal even when it is disconnected from its stud.

## Reproduction and verification

Run [layout_a4.py](layout_a4.py) with the source STL path, using numpy, shapely, and matplotlib as in its docstring. Source identity and all derived measurements are saved in [layout-a4.json](layout-a4.json).

Verified: unchanged source scale/exterior/positions, 75 × 140 mm plan bounds, all nine new holes contained in the filled frame, 7 mm relief pitch, and the >10 mm stud-to-relief clear gap. The main illustration uses a translucent/schematic connector so the stud positions remain legible; the side section explains their depth separation.

No source STL was modified and no image-generated geometry is used for A4.
