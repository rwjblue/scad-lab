# Design and ergonomics review — 9 September 2026

Two independent agents reviewed the printable A5 model from commit
`c85c3002`: one for mechanical criticism, one for ergonomics. Both inspected
the SCAD and measured geometry rather than relying only on the mockup.

## Findings and decisions

| Finding | Decision |
| --- | --- |
| Square edges on the 5 mm extrusion contact fingers and wound wire; the source had a rounded cross-section. Both reviewers identified this as the strongest improvement. | Add 0.5 mm, 45° bevels around the exterior and retained window rims on both broad faces. Keep the original outline through the central 4 mm. |
| Five tiny central openings offer no useful finger access. Two are 1.14 mm wide and the central diamond is 1.67 mm wide, close to the planned wire’s insulated diameter. | Accept the ergonomics recommendation to fill these five openings while retaining six larger windows. Snagging is a plausible handling concern, not a demonstrated failure. The mechanical reviewer regarded filling as discretionary; the source mesh itself is valid. |
| The BNC coupon does not test the three-hole wire weave. Both reviewers requested a direct way to test grip. | Add `part="relief_coupon"`, cut directly from the actual upper arm, retaining its thickness, bores, pitch, mouth chamfers, and outer edge. |
| The hardware preview omitted the shell tag and gave no wire-routing context. | Add a schematic outward-facing shell tag and relaxed lead paths in F5 only, plus a threading section diagram. |
| The hanging cord and soldered wire tails could make assembly awkward if fitted in the wrong order. | Thread the cord and wire first; keep the cord knot behind the frame. Dry-fit the BNC and orient its tag away from the frame before soldering. |
| Neither review demonstrated a collision requiring a larger BNC offset or movement of the horns. | Retain the accepted 75 × 140 × 24 mm envelope, BNC axis, shelf thickness, eye, and 7 mm relief pitch. |

The eye and wire-hole chamfers stay at 0.5 mm. Enlarging those mouths would
consume useful material: with the new perimeter bevel, the smallest measured
face ligament is approximately 2.48 mm at the eye and 2.33 mm at the outer
relief hole. Geometry checks establish those dimensions, not a load rating.

## Iteration and verification

A subtractive conical bevel expands the profile’s outside and subtracts it at
each broad face. This keeps the original middle outline intact, including
concave details, without the small ledges that rebuilding an inset outline
outward can create. The bevel respects the existing shelf and rib attachments.

A second mechanical pass caught a 0.299 mm underside ledge where the original
rib bases started above the new bevel. Embedding those bases in the unchanged
middle band removes the ledge. A regression check compares six successive
sections around that transition and requires supported, nested contours.

The revised STL is one watertight solid with 9,490 triangles and unchanged
75 × 140 × 24 mm bounds. Six large native windows, seven frame holes, and the
BNC opening remain open. Seven section planes verify both bevels within
0.0011 mm of their ideal shape. The original exterior and retained windows
match the source within 0.000003 mm through the middle section. The wire
bores/chamfers, 7 mm pitch, 9.9 × 9.05 mm BNC D-hole, and reinforcement
clearance all pass. See [validation.json](validation.json).

The resulting volume is 22,363.09 mm³ versus 22,459.98 mm³ before this review:
the edge and rib refinements remove slightly more than the window fills add. Physical
wire grip, printed strength, and the complete BNC/tag/coax fit still need the
actual components. The new coupon and assembly illustration support those checks.
