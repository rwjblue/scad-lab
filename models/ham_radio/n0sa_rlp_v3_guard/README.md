# N0SA RLP V3 magnetic nose guard

One-piece, front-only protective shroud for the N0SA RLP V3 dual-lever CW paddle. The guard shields the moving finger pieces during transport and uses two additional magnets in a **continuous bottom floor** aligned with the key's front magnet pair. **The top, sides, and magnetic bottom now all end at one common, straight rear plane**, about 10.24 mm behind the fixed body's front edge. There is no projecting underside tongue, no U-shaped cutout, and no rear-jack or reversible mounting feature.

**Status: V6 depth correction following the first physical print (October 30, 2026).** The owner confirmed that the first print was **too shallow for the paddle tips**, although the remaining geometry appeared aligned. New measurements place the paddle tips **27.11 mm forward of the fixed-body edge** (the old model assumed 18.72 mm), and the far edge of the front magnets **8.24 mm behind that edge**. The updated model provides **2 mm tip clearance plus a 2 mm nose wall**, and the shell extends 2 mm past the measured rear edge of the magnets. **Magnet pocket centers have deliberately not moved**, preserving the alignment reported on the first print. The 1.5 mm and 2 mm add-on magnet options remain supported. This revision is not yet physically fit-tested. **Do not force the sleeve onto the paddles.**

## Parts and generated STLs

The repository tracks the OpenSCAD source; use the commands below to generate STL outputs for either magnet thickness. Prebuilt STLs are supplied separately in the prototype download package. All six outputs are geometrically distinct where the magnet pocket depths change.

- `n0sa_rlp_v3_guard.scad` — one parametric source for all three parts. Set `part` at the top or override with `-D`. The full guard now exports in the recommended **nose-down print orientation** by default (`print_orientation="nose_down"`). Set `print_orientation="as_used"` for a key-mounted visualization (not recommended for support-free printing).
- `rlp_v3_guard_6x1p5.stl` / `rlp_v3_guard_6x2p0.stl` (`part="guard"`) — full nose shroud with pockets sized for either supplied magnet thickness.
- `rlp_v3_fit_coupon_6x1p5.stl` / `rlp_v3_fit_coupon_6x2p0.stl` (`part="fit_coupon"`) — thin replica of just the continuous floor's rear overlap, two magnet pockets, and shallow alignment lips. Use this to check underside fit, magnet spacing and polarity with minimal filament.
- `rlp_v3_magnet_gauge_6x1p5.stl` / `rlp_v3_magnet_gauge_6x2p0.stl` (`part="magnet_gauge"`) — tiny two-pocket gauge for testing magnet diameter/tolerance. The **notched +X end is the looser pocket**; the unmarked end is the tighter one.

All variants are one-piece prints. The magnets are the only separately installed parts.

## Measurements and defaults

| Input | Default | Confidence |
|---|---:|---|
| Key width | 36.77 mm | Caliper photo |
| Key height | 28.92 mm | Caliper photo |
| Paddle projection, front body edge to tips | **27.11 mm** | **Measured after initial print; replaces incorrect 18.72 mm datum** |
| Existing magnet diameter | 6.0 mm | **Measured** |
| Outer-to-outer distance, front magnet pair | 21.51 mm | **Measured** with calipers |
| Center-to-center distance, front magnet pair | **15.51 mm** | Derived as 21.51 − 6.0 |
| Front body edge to nearest magnet edge | 1.5 mm | **Measured approximately** |
| Front body edge to magnet center | **4.5 mm** | Derived as 1.5 + (6.0 / 2) |
| Front body edge to far edge of existing magnet | **8.24 mm** | **Measured after initial print** |
| Back of measured far magnet edge to shell rear edge | 2.0 mm | Design margin (adjustable) |
| Magnet pockets' Y position | **−4.50 mm** | Preserved from first print; reported aligned, despite 0.74 mm difference between edge measurements |
| Available magnet inserts | **6 × 1.5 mm and 6 × 2.0 mm** | Owner has both sizes (N48 specified for the 1.5 mm version) |
| Default insert selection | **6 × 1.5 mm** | Set `insert_thickness=2.0` for the thicker option |
| Pocket diameter | 6.2 mm | For 6.0 mm inserts, adjustable |
| Pocket depth for 1.5 mm magnets | **1.65 mm** | 1.5 mm thickness + 0.15 mm tolerance |
| Pocket depth for 2.0 mm magnets | **2.15 mm** | 2.0 mm thickness + 0.15 mm tolerance |
| Remaining continuous bottom floor | **1.65 / 1.15 mm** | With 1.5 / 2.0 mm magnets in a 3.3 mm floor |

STL bounding boxes measured from the rendered binary meshes (same for both insert thicknesses):

| Part | X width × Y length × Z height |
|---|---|
| Guard, **nose-down STL on build plate** | **41.67 × 35.07 × 41.47 mm** |
| Magnet-fit coupon | **41.67 × 10.24 × 5.42 mm** |
| Magnet pocket gauge | 28.00 × 14.00 × 3.30 mm |

These are *part* dimensions, not the total key plus guard. The outside of the protective nose extends **4.0 mm past the measured paddle tips**, consisting of 2.0 mm free interior clearance and a 2.0 mm nose wall. Its outer nose is **31.11 mm forward of the fixed-body front edge**. The **entire shell** extends **10.24 mm behind the front plastic edge** (8.24 mm measured far magnet edge plus 2 mm margin), preserving the uniform rear opening. The overall Y-length in assembled orientation is therefore about **41.35 mm** (about **41.47 mm** including the modeling slices); it is roughly **9.1 mm longer than V5**.

## Printing

- PETG, 0.4 mm nozzle, about 0.2 mm layers is a reasonable starting point.
- **Print the full guard on its closed nose**, with the open end facing **straight up**. This is the default orientation for generated guard STLs. Its closed nose forms a broad, flat ~955 mm² contact area on the plate. Do **not** lay the magnetic floor down: that would leave a ~38 mm roof bridge across the hollow center. Nose-down, the roof becomes a vertical wall with no large unsupported span. In Bambu Studio, check that the broad, closed nose is on the plate and avoid **Auto Orient** if it flips the part. The coupon and pocket gauge still export with their flat floors against the bed.
- Start with **supports off** for the nose-down guard, then inspect the sliced preview for the two **6.2 mm diameter magnet pockets** (now facing sideways) and the small internal stop pads. The pockets have only a short curved overhang, and the stop pads are short cantilevers; those may print cleanly without supports but **we have not verified this in Bambu Studio or physically**. Use narrowly painted supports only if the slicer indicates trouble, rather than filling the entire inside of the sleeve with supports.
- Do a **dry fit with no added magnets first**. Slide the shroud straight over the front, without levering the fingers sideways. Confirm the full movement of both paddles is clear, including at the tip and where the tapered roof starts.
- Test the gauge if unsure about insert diameter. Then test the fit coupon against the key underside and existing front magnets. A wrong magnet spacing cannot be corrected by polarity alone: adjust `key_magnet_outer_span` and/or `key_magnet_front_margin` (which derive `magnet_spacing` and `magnet_y`), regenerate and reprint.
- Confirm **attraction** separately for **each magnet** against its corresponding installed key magnet *before gluing*. When fully seated, either insert sits about 0.15 mm below the key-facing surface. The blind pocket leaves **1.65 mm** of printed material under the 1.5 mm insert, or **1.15 mm** under the 2.0 mm insert. Both pockets are 6.2 mm diameter. Do not use excessive press force on PETG or the key magnets.
- The magnetic strip is intended for retention and alignment, **not for absorbing impacts**. Two small, parametric stop pads at the outside corners of the fixed lower plate (`enable_stop_pads`) are intended to transfer a nose impact into the stationary body, not the moving fingers. **They are based on the assumed front edge at Y=0**; inspect their fit carefully and disable/adjust them if they hit an adjustment screw, lever or post. Confirm this with a low-force shake/handling test before carrying it in a bag.

## Regenerating STL files

The one OpenSCAD file has `insert_thickness = 1.5` as its default; override it to `2.0` for the second set. The 6.2 mm pocket diameter, magnet positions and outside dimensions remain identical. The pocket depths differ by 0.5 mm.

```sh
# Six STLs for the two magnet sizes on hand:
for thickness in 1.5 2.0; do
  case "$thickness" in 1.5) name=1p5 ;; 2.0) name=2p0 ;; esac
  for part in guard fit_coupon magnet_gauge; do
    openscad --export-format binstl \
      -D "part=\"$part\"" \
      -D "insert_thickness=$thickness" \
      -o "rlp_v3_${part}_6x${name}.stl" n0sa_rlp_v3_guard.scad
  done
done
```

For the first fit test, either coupon is sufficient to check alignment. Use the matching thickness variant when testing the depth of an insert; do **not** press a 2 mm magnet into the 1.5 mm pocket or modify the print by force.

The measured key geometry is parameterized by `paddle_projection=27.11`, `key_magnet_diameter=6.0`, `key_magnet_outer_span=21.51`, and the new `measured_magnet_far_edge=8.24`. The printed V5 magnet pockets were reported aligned, so the earlier approximate `key_magnet_front_margin=1.5` is **retained for pocket positioning only**: `magnet_spacing=15.51` and `magnet_y=-4.5` stay unchanged. The new measured far edge **independently** determines the rear shell margin: `back_overlap = measured_magnet_far_edge + magnet_rear_margin` = 10.24 mm. This explicitly tolerates the 0.74 mm discrepancy between the two edge measurements rather than shifting pockets that already fit. Changing `insert_thickness` only changes pocket depth. The rear plane is common to the roof, sides and floor. If the actual RLP geometry differs, adjust the parameters at the top of the SCAD. No third-party SP4 case geometry is included.

## Next physical-fit feedback

After printing V6: dry-fit **without glued magnets**, gently seat the fixed body to the stop pads, then confirm at least ~2 mm clearance from the longest paddle tip to the **inside** closed nose (not just the outside). Ensure neither lever touches the tapered roof or side walls at full travel, and confirm the magnet pockets still align. The new depth and overlap have not yet been verified with a physical print.
