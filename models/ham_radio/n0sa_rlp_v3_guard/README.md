# N0SA RLP V3 magnetic nose guard

One-piece, front-only protective shroud for the N0SA RLP V3 dual-lever CW paddle. The guard shields the moving finger pieces during transport and uses two additional magnets in a **continuous bottom floor** aligned with the key's front magnet pair. **The top, sides, and magnetic bottom now all end at one common, straight rear plane**, about 10.24 mm behind the fixed body's front edge. There is no projecting underside tongue, no U-shaped cutout, and no rear-jack or reversible mounting feature.

**Status: V6 guard with an open floor coupon for the next fit test.** V6 corrected the first print's shallow nose using a measured **27.11 mm paddle projection** (replacing the incorrect 18.72 mm datum) and an **8.24 mm far magnet edge**. It provides **2 mm nominal tip clearance plus a 2 mm nose wall**, and extends 2 mm past that measured magnet edge. **Magnet pocket centers remain unchanged.** Both 1.5 mm and 2 mm insert options remain supported. See the November 1 physical feedback below; **do not force the sleeve onto the paddles.**

**November 1 physical fit report:** the owner tested the **6 × 2 mm guard** and reports that magnet diameter, magnet positions and the front stops fit well. The magnets sit approximately **0.10–0.15 mm proud** (visual estimate), and the floor-to-roof dimension is approximately **2.5 mm too tall**. Paddle-tip clearance could not be judged through the shell. The new **open floor coupon** tests deeper pockets and exposes the tips; the complete V6 guard remains unchanged pending that result. Actual magnet thickness has not been measured. The height report is a requested design correction, not a replacement measurement for `key_height`.

## Parts and generated STLs

The repository tracks the OpenSCAD source; use the commands below to generate STL outputs for either magnet thickness. Prebuilt STLs are supplied separately in the prototype download package. The original six outputs differ where the magnet pocket depths change; the open floor coupon is an additional diagnostic part.

- `n0sa_rlp_v3_guard.scad` — one parametric source for all six part selections. Set `part` at the top or override with `-D`. The full guard now exports in the recommended **nose-down print orientation** by default (`print_orientation="nose_down"`). Set `print_orientation="as_used"` for a key-mounted visualization (not recommended for support-free printing).
- `rlp_v3_guard_6x1p5.stl` / `rlp_v3_guard_6x2p0.stl` (`part="guard"`) — full nose shroud with pockets sized for either supplied magnet thickness.
- `rlp_v3_fit_coupon_6x1p5.stl` / `rlp_v3_fit_coupon_6x2p0.stl` (`part="fit_coupon"`) — thin replica of just the continuous floor's rear overlap, two magnet pockets, and shallow alignment lips. Use this to check underside fit, magnet spacing and polarity with minimal filament.
- `rlp_v3_magnet_gauge_6x1p5.stl` / `rlp_v3_magnet_gauge_6x2p0.stl` (`part="magnet_gauge"`) — tiny two-pocket gauge for testing magnet diameter/tolerance. The **notched +X end is the looser pocket**; the unmarked end is the tighter one.
- `rlp_v3_floor_coupon_6x2p0_depth2p40_pushout.stl` (`part="floor_coupon"`) — open floor with the **same two stops**, **unchanged 6.20 mm pocket diameters and magnet centers**, and **2.40 mm deep trial pockets**. It includes the forward floor so the paddle tips are visible against engraved nose/tip reference lines. No roof or side guides are included.
- `rlp_v3_depth_gauge_2p15-2p45_pushout.stl` (`part="depth_gauge"`) — a small labeled strip with four **6.20 mm diameter** pockets at **2.15, 2.25, 2.35 and 2.45 mm depth**. The notched end is shallowest.
- `rlp_v3_fit_test_plate_6x2p0_pushout.stl` (`part="fit_test_plate"`) — the open floor coupon and depth strip together, separated by 6 mm, ready for one print. The STL contains **two independent parts**. The floor coupon still has 2.40 mm pockets; the four selectable depths are on the strip. The `_pushout` filenames distinguish these recoverable-magnet versions from earlier downloads.

Each individual part is a one-piece print; the combined test plate contains two separate parts. The magnets are the only separately installed hardware.

**Recoverable test magnets:** every coupon and gauge now has a **2.0 mm push-out hole beneath each magnet pocket**. The combined plate has six: two in the floor coupon and four in the depth strip. Test without glue, remove the part from the key, and gently push each magnet out from the underside using a pin or punch smaller than the printed hole. The magnet still seats on an annular floor at the labeled depth. The **full guard retains closed pocket bottoms**. `test_pushout_diameter=0` disables these holes in test parts; this control never affects the guard.

## Test four pocket depths in one print

Print **`rlp_v3_fit_test_plate_6x2p0_pushout.stl`** for both tests on one plate, or print only **`rlp_v3_depth_gauge_2p15-2p45_pushout.stl`** if the floor coupon is already underway. Keep the parts **flat, floor-down, at 100% scale with supports off**. Use **0.10 mm layers** for this depth comparison: at 0.20 mm layers, adjacent 0.10 mm depth steps may slice to the same printed floor height. Check the sliced preview; the labels are nominal CAD depths, and printed depths still follow layer boundaries.

All four holes retain the successful **6.20 mm diameter**. Raised labels give depth in millimeters; the notch identifies the **2.15 mm baseline** end. The 3.30 mm base leaves 1.15, 1.05, 0.95 and 0.85 mm below the four pockets respectively. The label area sits away from the pocket row, so a nonmagnetic plastic card laid across a hole can help show whether the test magnet stands proud.

Try the **same actual magnet** in each pocket, without glue, and choose the shallowest one that leaves it flush or slightly recessed. Push it out through the underside hole between trials, then check the other insert too. The strip tests depth only; use the floor coupon's two stops and engraved lines for actual key alignment and tip clearance. The full guard's sideways-printed pockets still need their own seating check after the chosen depth is applied.

```sh
openscad --backend=Manifold --hardwarnings --export-format=binstl \
  -D 'part="fit_test_plate"' -D 'insert_thickness=2.0' \
  -o output/rlp_v3_fit_test_plate_6x2p0_pushout.stl \
  models/ham_radio/n0sa_rlp_v3_guard/n0sa_rlp_v3_guard.scad
```

## Open floor coupon: next fit test

Use **`rlp_v3_floor_coupon_6x2p0_depth2p40_pushout.stl`** for the current 2 mm magnet trial. Print it **flat floor-down at 100% scale, supports off**, using the same PETG, 0.4 mm nozzle and 0.20 mm layer height. It exports with its base at Z=0. Only the original stop pads rise above the floor. This is a fit tool, not a transport guard.

- **Pocket depth:** 2.40 mm, which is 0.25 mm deeper than the 2.15 mm pockets in the 6 × 2 mm V6 guard. The 3.30 mm floor leaves **0.90 mm of plastic beneath each pocket**. The diameter and positions that fit well are preserved. With otherwise identical seating, that increase would turn the estimated 0.10–0.15 mm protrusion into approximately 0.10–0.15 mm recess. This is a trial allowance; actual magnet thickness and printed pocket depth still determine seating.
- **Solid engraved line:** actual central **inside nose wall plane**, Y=29.17 mm. The outside front edge is 2 mm farther forward at Y=31.17 mm. Measure from the actual paddle tips to the **center of the solid groove**, not to the outer edge.
- **Dashed engraved line:** original measured **27.11 mm tip datum**. Do not align the key to this line; let it seat against the two stops and observe where the real tips land. Stop seating can move the tips about 0.15 mm forward of this datum.
- **Fit sequence:** check the magnets in the new pockets without glue, then seat the key against the stops and check both levers through full travel. Report whether the magnets are recessed/flush/proud and the approximate tip-to-solid-line gap. Loose magnets can remain on the key when the coupon is removed.
- **Printing limitation:** this flat coupon checks depth with upward-facing pockets. The full guard's nose-down pockets face sideways and may need different cleanup; successful coupon fit alone does not establish the final printed pocket fit.

From the repository root:

```sh
openscad --backend=Manifold --hardwarnings --export-format=binstl \
  -D 'part="floor_coupon"' -D 'insert_thickness=2.0' \
  -o output/rlp_v3_floor_coupon_6x2p0_depth2p40_pushout.stl \
  models/ham_radio/n0sa_rlp_v3_guard/n0sa_rlp_v3_guard.scad
```

`floor_coupon_depth_increase=0.25` adds to the selected insert thickness and the usual 0.15 mm pocket allowance. `floor_coupon_marks=false` disables the two engraved lines. These controls affect only this new coupon; full-guard depth, width, magnet alignment, stops and height have not changed. Apply the reported height reduction to a later full-guard revision after the exposed fit checks.

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
| Open floor coupon, including stops | **41.67 × 41.47 × 6.46 mm** |
| Four-depth strip, including labels | **52.00 × 16.00 × 3.80 mm** |
| Combined floor coupon and depth strip | **99.67 × 41.47 × 6.46 mm** |
| Magnet pocket gauge | 28.00 × 14.00 × 3.30 mm |

These are *part* dimensions, not the total key plus guard. The outside of the protective nose extends **4.0 mm past the measured paddle tips**, consisting of 2.0 mm free interior clearance and a 2.0 mm nose wall. Its outer nose is **31.11 mm forward of the fixed-body front edge**. The **entire shell** extends **10.24 mm behind the front plastic edge** (8.24 mm measured far magnet edge plus 2 mm margin), preserving the uniform rear opening. The overall Y-length in assembled orientation is therefore about **41.35 mm** (about **41.47 mm** including the modeling slices); it is roughly **9.1 mm longer than V5**.

## Printing

- PETG, 0.4 mm nozzle, about 0.2 mm layers and three walls is a reasonable starting point.
- **Print the full guard on its closed nose**, with the open end facing **straight up**. This is the default orientation for generated guard STLs. Its closed nose forms a broad, flat ~955 mm² contact area on the plate. Nose-down, the roof becomes a vertical wall with no large unsupported span. In Bambu Studio, check that the broad, closed nose is on the plate and avoid **Auto Orient** if it flips the part. The coupon and pocket gauge export with their flat floors at Z=0. **Floor-down remains a fallback with supports**: the ~38 mm roof bridge needs slicer evaluation, and support removal may roughen the mating surfaces. The `as_used` guard preserves the key coordinate system with its floor at Z=−3.55 mm; place it on the plate in the slicer before printing.
- Start with **supports off** for the nose-down guard. The owner reported a successful earlier nose-down print without supports. Inspect the two sideways **6.2 mm diameter magnet pockets** and the stop-pad cantilevers in the sliced preview and the finished print. The November 1 proud-magnet report still needs the deeper-pocket trial above.
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

## CAD review before the next print

The October 30 review of merged V6 confirmed the specified dimensions, preserved magnet centers and common rear rim. OpenSCAD renders of both magnet thicknesses, including both guard orientations, produced eight watertight meshes with consistent winding and one connected solid each. This established CAD integrity before physical fitting; the November 1 feedback is recorded above. That review's export correction places the original coupon and gauge floors at Z=0 (previously −3.55 mm); their shapes and the full guard geometry are unchanged.

- **Loft boundaries:** the centered 0.12 mm slices extend the actual nose faces to Y=29.17/31.17 mm, versus the nominal 29.11/31.11 mm. The entire rear rim is at Y=−10.30 mm, versus nominal −10.24 mm. This explains the 41.47 mm rendered length. There is no projecting bottom tongue.
- **Orientation:** nose-down maps assembled `(x,y,z)` to `(x,z+3.55,31.17−y)` at the defaults. The closed nose is at print Z=0 and the rear rim at Z=41.47 mm. The `as_used` orientation intentionally retains the original key datum.
- **Tapered clearance:** at the nominal paddle-tip plane Y=27.11 mm, the cavity's maximum width is about **29.61 mm** and its ceiling is **Z=24.48 mm above the key underside**. Rounded corners reduce clearance near the edges. Paddle-tip width, height and full swept travel have not been measured; overall key width/height alone cannot establish clearance here.
- **Stop seating:** pad faces begin at Y=+0.15 mm, so a flat stationary body front at Y=0 would allow about 0.15 mm additional insertion before contact. At that seating position, central axial tip clearance is about **1.91 mm**, rather than the 2.06 mm at the nominal datum, and pocket centers shift by the same 0.15 mm relative to the key. Verify the actual contact location before adjusting either stops or magnet positions.
- **Lower corners:** the cavity has 1.6 mm corner radii. The 0.65 mm side gap and 0.25 mm underbody gap do not guarantee clearance for a sharp rectangular lower plate corner. Check the real rounded/scalloped plate and screw heads for rub marks; the coupon's square floor/guide junction does not reproduce these full-guard corners.
- **Print details:** nose-down removes the large roof bridge, but the sideways round pockets and square leading edges of the stop pads still create local overhangs. A floor-down gauge/coupon can establish initial pocket tolerance, but cannot establish the finish or fit of a sideways-printed guard pocket. There are no pocket lead-ins or glue-relief features yet; defer these refinements until fit feedback identifies a need.

## Next physical-fit feedback

The November 1 report confirms initial magnet alignment and stop contact. Use the open floor coupon above to expose tip clearance and test the deeper pockets. Exact tip clearance, final reduced roof height and magnetic retention remain to be established. Record the magnet thickness, orientation, supports, PETG profile, layer height and any cleanup for each print. Change one fit parameter at a time after collecting this feedback:

1. **Inspect the slice and print:** check pocket ceilings and the first layers of the stop pads, then remove loose strands or support residue before fitting. Compare nose-down and supported floor-down finish if necessary.
2. **Dry-fit without magnets:** slide on gently and record where it first stops. Identify contact on the stationary lower plate; neither pad should touch a lever, screw, adjustment mechanism or standoff unexpectedly. Check the rear opening's lower corners for scraping.
3. **Check the paddle envelope:** confirm approximately 2 mm of clearance to the **inside** nose, allowing for the seating offset above. Check both levers through full travel against the taper, roof and sides. Report actual tip clearance and any contact location; additional nose length alone does not prove the taper clears.
4. **Check magnet alignment:** use the coupon as an initial check, then verify both full-guard pockets at the actual seated position. Preserve X=±7.755 mm and Y=−4.50 mm until this feedback demonstrates a mismatch.
5. **Compare retention:** use the matching pocket-depth variant for each magnet thickness, check each magnet's polarity separately, and assess insertion, removal, rattling and gentle sideways/twisting loads. Fully seated inserts are recessed 0.15 mm; with the nominal 0.25 mm underbody gap, opposing magnet faces are about **0.40 mm apart**, assuming the key magnets are flush. Actual magnetic pull has not been measured. Loose inserts can be pulled out by the key, so do not treat an unglued trial as secure transport retention.
6. **Confirm the load path:** once clearance and magnet installation are satisfactory, use gentle hand pressure to confirm the stationary body takes load before the moving fingers can touch the shell. Record stop contact and flex; mesh validation does not establish impact strength. Reserve bag use until these checks pass.
