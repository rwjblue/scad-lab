# N0SA RLP V3 magnetic nose guard

One-piece, front-only protective shroud for the N0SA RLP V3 dual-lever CW paddle. The guard shields the moving finger pieces during transport and uses two additional magnets in a **flat, continuous underside tongue** that reaches just past the existing front pair of magnets on the key. The tongue has a **straight rear edge**—there is no U-shaped cutout. It does not try to protect the rear 3.5 mm jack or mount in reverse.

**Status: experimental first-fit print, revised October 30, 2026.** Dimensions of the paddle envelope were supplied by the owner. **The front magnet diameter, outer-to-outer spacing, and front-edge offset have now been measured**, but placement still assumes that the measured plastic edge corresponds to Y=0 (the fixed lower plate's front edge). The added magnet thickness and paddle clearance remain estimates. The STL is not a guaranteed fit. **Do not force the sleeve onto the paddles.** Check clearances and the magnet positions before installing or gluing magnets.

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
| Existing magnet diameter | 6.0 mm | **Measured** |
| Outer-to-outer distance, front magnet pair | 21.51 mm | **Measured** with calipers |
| Center-to-center distance, front magnet pair | **15.51 mm** | Derived as 21.51 − 6.0 |
| Front body edge to nearest magnet edge | 1.5 mm | **Measured approximately** |
| Front body edge to magnet center | **4.5 mm** | Derived as 1.5 + (6.0 / 2) |
| Back of front magnet to straight tongue's rear edge | 2.0 mm | Design margin (adjustable) |
| Magnets to install in guard | 6.0 × 2.0 mm | Diameter matches key; **insert thickness remains assumed** |
| Pocket diameter | 6.2 mm | For 6.0 mm inserts, adjustable |
| Pocket depth | 2.15 mm | For 2.0 mm inserts, adjustable |

Default STL bounding boxes measured from rendered binary meshes:

| Part | X width × Y length × Z height |
|---|---|
| Guard | **41.67 × 32.28 × 35.07 mm** |
| Magnet-fit coupon | **41.67 × 9.50 × 5.42 mm** |
| Magnet pocket gauge | 28.00 × 14.00 × 3.30 mm |

These are *part* dimensions, not the total key plus guard. The protective nose extends about 4.0 mm beyond the photographed paddle projection; most guard length overlaps the existing key envelope. The continuous underside tongue extends **9.5 mm behind the front plastic edge**, including the measured 7.5 mm magnet-to-rear extent and a further 2 mm printed margin.

## Printing

- PETG, 0.4 mm nozzle, about 0.2 mm layers is a reasonable starting point.
- Lay the **continuous bottom surface** on the build plate (default STL orientation is already flat). The broad top of the enclosed shroud spans an opening; evaluate the bridge in the slicer and use minimal supports under the roof if your PETG cannot bridge it cleanly. The small coupon and pocket gauge should print without supports.
- Do a **dry fit with no added magnets first**. Slide the shroud straight over the front, without levering the fingers sideways. Confirm the full movement of both paddles is clear, including at the tip and where the tapered roof starts.
- Test the gauge if unsure about insert diameter. Then test the fit coupon against the key underside and existing front magnets. A wrong magnet spacing cannot be corrected by polarity alone: adjust `key_magnet_outer_span` and/or `key_magnet_front_margin` (which derive `magnet_spacing` and `magnet_y`), regenerate and reprint.
- Confirm **attraction** separately for **each magnet** against its corresponding installed key magnet *before gluing*. The faces of the inserted magnets sit slightly below the printed tongue's top face; the blind pocket leaves about 1.15 mm of plastic beneath each magnet. Do not use excessive press force on PETG or the key magnets.
- The magnetic strip is intended for retention and alignment, **not for absorbing impacts**. Two small, parametric stop pads at the outside corners of the fixed lower plate (`enable_stop_pads`) are intended to transfer a nose impact into the stationary body, not the moving fingers. **They are based on the assumed front edge at Y=0**; inspect their fit carefully and disable/adjust them if they hit an adjustment screw, lever or post. Confirm this with a low-force shake/handling test before carrying it in a bag.

## Regenerating STL files

```sh
openscad --export-format binstl -o rlp_v3_nose_guard.stl -D 'part="guard"' n0sa_rlp_v3_guard.scad
openscad --export-format binstl -o rlp_v3_magnet_fit_coupon.stl -D 'part="fit_coupon"' n0sa_rlp_v3_guard.scad
openscad --export-format binstl -o rlp_v3_magnet_gauge.stl -D 'part="magnet_gauge"' n0sa_rlp_v3_guard.scad
```

The measured key geometry is parameterized by `key_magnet_diameter=6.0`, `key_magnet_outer_span=21.51`, and `key_magnet_front_margin=1.5`. The SCAD **derives** `magnet_spacing=15.51` and `magnet_y=-4.5` from these values. Use `insert_diameter` and `insert_thickness` for the two magnets you supply in the print; changing the insert size does **not** change the positions of the magnets already in the RLP. `magnet_rear_margin=2.0` controls the continuous tongue's extra rear overlap. If the actual RLP geometry differs, adjust the values at the top of the SCAD. No third-party SP4 case geometry is included.

## Next physical-fit feedback

After printing the coupon or guard: measure the **spare magnet thickness**, confirm the key's front-edge datum, check whether the magnet pockets align and whether the rigid body's front corners contact the stop pads. Ensure each paddle moves freely without contacting the tapered walls or roof. These observations will guide the next revision.
