# N0SA RLP V3 magnetic nose guard

One-piece, front-only protective shroud for the N0SA RLP V3 dual-lever CW paddle. The guard shields the moving finger pieces during transport and uses two additional magnets in a **flat, continuous underside tongue** that reaches just past the existing front pair of magnets on the key. The tongue has a **straight rear edge**—there is no U-shaped cutout. It does not try to protect the rear 3.5 mm jack or mount in reverse.

**Status: experimental first-fit print.** Dimensions of the paddle envelope were supplied by the owner, but the magnet diameter, locations, and exposed-paddle clearance were estimated from photographs. The provided STL geometry is not a guaranteed fit. **Do not force the sleeve onto the paddles.** Check clearances and the magnet positions before installing or gluing magnets.

## Parts and generated STLs

The repository tracks the OpenSCAD source; use the commands below to generate the three STL outputs. Prebuilt first-fit STLs were also supplied separately for slicing.

- `n0sa_rlp_v3_guard.scad` — one parametric source for all three parts. Set `part` at the top or override with `-D`.
- `rlp_v3_nose_guard.stl` (`part="guard"`) — full nose shroud, including magnet pockets.
- `rlp_v3_magnet_fit_coupon.stl` (`part="fit_coupon"`) — thin replica of only the straight underside tongue, two magnet pockets, and shallow alignment lips. Use this to check underside fit, magnet spacing and polarity with minimal filament.
- `rlp_v3_magnet_gauge.stl` (`part="magnet_gauge"`) — tiny two-pocket gauge for testing magnet diameter/tolerance. The **notched +X end is the looser pocket**; the unmarked end is the tighter one.

All variants are one-piece prints. The magnets are the only separately installed parts.

## Measurements and defaults

| Input | Default | Confidence |
|---|---:|---|
| Key width | 36.77 mm | Caliper photo |
| Key height | 28.92 mm | Caliper photo |
| Exposed paddle projection | 18.72 mm | Caliper photo; reference point should be verified |
| Existing front magnet center spacing | 23.0 mm | **Estimated** from oblique underside photograph |
| Existing front magnet location behind the fixed body's front edge | 8.5 mm | **Estimated** |
| Magnets to install in guard | 6.0 × 2.0 mm | **Assumed**; adjust to available magnets |
| Pocket diameter | 6.2 mm | For 6.0 mm inserts, adjustable |
| Pocket depth | 2.15 mm | For 2.0 mm inserts, adjustable |

Default STL bounding boxes measured from rendered binary meshes:

| Part | X width × Y length × Z height |
|---|---|
| Guard | 41.67 × 37.98 × 35.07 mm |
| Magnet-fit coupon | 41.67 × 12.90 × 5.42 mm |
| Magnet pocket gauge | 28.00 × 14.00 × 3.30 mm |

These are *part* dimensions, not the total key plus guard. The protective nose extends about 4.0 mm beyond the photographed paddle projection; most guard length overlaps the existing key envelope.

## Printing

- PETG, 0.4 mm nozzle, about 0.2 mm layers is a reasonable starting point.
- Lay the **continuous bottom surface** on the build plate (default STL orientation is already flat). The broad top of the enclosed shroud spans an opening; evaluate the bridge in the slicer and use minimal supports under the roof if your PETG cannot bridge it cleanly. The small coupon and pocket gauge should print without supports.
- Do a **dry fit with no added magnets first**. Slide the shroud straight over the front, without levering the fingers sideways. Confirm the full movement of both paddles is clear, including at the tip and where the tapered roof starts.
- Test the gauge if unsure about insert diameter. Then test the fit coupon against the key underside and existing front magnets. A wrong magnet spacing cannot be corrected by polarity alone: change `magnet_spacing` and/or `magnet_y`, regenerate and reprint.
- Confirm **attraction** separately for **each magnet** against its corresponding installed key magnet *before gluing*. The faces of the inserted magnets sit slightly below the printed tongue's top face; the blind pocket leaves about 1.15 mm of plastic beneath each magnet. Do not use excessive press force on PETG or the key magnets.
- The magnetic strip is intended for retention and alignment, **not for absorbing impacts**. Two small, parametric stop pads at the outside corners of the fixed lower plate (`enable_stop_pads`) are intended to transfer a nose impact into the stationary body, not the moving fingers. **They are based on the assumed front edge at Y=0**; inspect their fit carefully and disable/adjust them if they hit an adjustment screw, lever or post. Confirm this with a low-force shake/handling test before carrying it in a bag.

## Regenerating STL files

```sh
openscad --export-format binstl -o rlp_v3_nose_guard.stl -D 'part="guard"' n0sa_rlp_v3_guard.scad
openscad --export-format binstl -o rlp_v3_magnet_fit_coupon.stl -D 'part="fit_coupon"' n0sa_rlp_v3_guard.scad
openscad --export-format binstl -o rlp_v3_magnet_gauge.stl -D 'part="magnet_gauge"' n0sa_rlp_v3_guard.scad
```

For example, to use 8 × 2 mm magnets and try a 25 mm center spacing, update `insert_diameter=8.0`, `magnet_spacing=25.0`, then verify the `back_overlap` is still long enough. If the actual RLP geometry differs, adjust the other values at the top of the SCAD. No third-party STL geometry is included.

## Next physical-fit feedback

After printing the coupon or guard: note actual magnet diameter and thickness, magnet center-to-center distance, front magnet center-to-body-front distance, and whether either paddle contacts the inner nose or roof at full travel. These let us replace estimates with measured parameters in the next revision.
