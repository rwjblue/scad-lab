# DX Commander Hitch Base Puck

Soft TPU puck for protecting the DX Commander Expedition mast base inside a
hitch-mounted flag pole holder.

## Default Dimensions

| Feature | Value |
| --- | ---: |
| Bottom cup ID | 50.56 mm |
| Lower plug OD | 50.2 mm |
| Lower plug height | 5 mm |
| Full-width floor thickness | 1.2 mm |
| Mast base measured OD | 50.85 mm |
| Mast base pocket ID | 51.2 mm |
| Upper guide OD | 58.5 mm |
| Upper guide height | 10 mm |
| Total height | 16.2 mm |

The lower plug fits into the small bottom cup. A 1.2 mm full-width TPU floor
sits above that plug and bonds the upper guide ring to the base. The mast base
rests on that flat floor, while the upper guide surrounds the mast base to limit
side-to-side movement and prevent abrasion.

## Printing

Print upright in TPU with the lower plug on the build plate. Enable supports:
the upper guide has a square outside shoulder where it widens from the lower
plug, and that overhang is expected to need support. The supported area is not a
precision fit surface.

## Fit Tuning

The main fit parameters are at the top of
`dx_commander_hitch_base_puck.scad`.

- If the lower plug is too tight in the cup, reduce `lower_plug_d`.
- If the lower plug is too loose in the cup, increase `lower_plug_d`, keeping
  it below `cup_inner_d`.
- If the mast base is too tight in the pocket, increase `mast_base_bore_d`.
- If the mast base wiggles too much, reduce `mast_base_bore_d`.
