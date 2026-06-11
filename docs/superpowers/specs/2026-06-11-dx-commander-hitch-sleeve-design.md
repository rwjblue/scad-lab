# DX Commander Hitch Sleeve Design

## Purpose

Create a PETG sleeve adapter for using a DX Commander Expedition mast in a
hitch-mounted flag pole holder. The holder tube is larger than the mast, so the
sleeve protects the mast and keeps it from wobbling inside the holder.

## Fit Requirements

- Holder tube inner diameter: 59 mm.
- Mast outer diameter: 47 mm, measured with calipers at the mast top.
- Printed material: PETG.
- The sleeve must not fall through the holder tube.
- The mast should be guided closely, but still slide through without scraping or
  requiring force.

## Recommended Geometry

The model is a straight circular bushing with an external stop flange near the
top.

| Feature | Value | Rationale |
| --- | ---: | --- |
| Body outer diameter | 58.5 mm | 0.5 mm total clearance inside the 59 mm holder tube |
| Mast bore diameter | 47.6 mm | 0.6 mm total clearance around the measured 47 mm mast |
| Lower insertion height | 76.2 mm | 3 in of contact surface below the holder rim |
| Upper guide height | 20 mm | Keeps the mast protected above the holder rim |
| Flange outer diameter | 68 mm | Wider than the holder tube so the sleeve cannot drop through |
| Flange height | 5 mm | Enough material for a durable stop without excessive bulk |
| Total height | 101.2 mm | 76.2 + 5 + 20 mm |

The flange sits between the lower insertion body and the upper guide body. When
installed, the flange rests on the rim of the hitch-mounted holder, leaving
76.2 mm of sleeve inside the holder and 20 mm above it.

## Printability

The model should be printed upright. It should not need supports because the
part is rotationally symmetric and uses chamfers instead of unsupported
overhang-heavy features.

Add small lead-in chamfers:

- Bottom outside edge, so the sleeve starts easily into the holder.
- Bottom mast bore edge, so the mast can enter cleanly from below if needed.
- Top mast bore edge, so the mast starts cleanly from above.
- Top and bottom flange edges, to reduce sharp corners and improve handling.

## Parameterization

The OpenSCAD file should expose the main dimensions as top-level parameters:

- `holder_inner_d = 59`
- `body_outer_d = 58.5`
- `mast_outer_d = 47`
- `mast_bore_d = 47.6`
- `lower_insert_h = 76.2`
- `upper_guide_h = 20`
- `flange_outer_d = 68`
- `flange_h = 5`
- `chamfer = 1`

This keeps fit tuning simple after test prints. If the mast fit is too loose,
reduce `mast_bore_d` toward 47.4 mm. If it is too tight, increase it toward
47.8 mm.

## Validation

The implementation should include OpenSCAD assertions for:

- Body outer diameter is smaller than the holder inner diameter.
- Mast bore is larger than the mast outer diameter.
- Flange outer diameter is larger than the holder inner diameter.
- Lower insert, upper guide, and flange heights are positive.

Render validation should confirm that OpenSCAD can generate the model without
assertion failures.
