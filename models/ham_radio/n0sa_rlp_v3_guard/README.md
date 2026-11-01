# N0SA RLP V3 magnetic nose guard

One-piece, tapered PETG nose shroud for the N0SA RLP V3 dual-lever CW paddle. A closed bumper protects the finger pieces, two added magnets align with the key’s front magnet pair, and two stops seat against the stationary body. The roof, sides and continuous bottom share one straight rear plane.

**Current print: 2.95 mm magnet pockets.** Magnet diameter/alignment, stop contact and length have passed physical fit checks. The complete guard incorporates the reported height correction, a thicker bottom and shallow glue dimples. Its lowered roof still needs a physical fit check.

## Current full print

Print **`rlp_v3_guard.stl`** at **100% scale**, keeping its supplied **nose-down orientation**, with the closed bumper against the plate and the rear opening facing up. Start with **PETG, a 0.4 mm nozzle, 0.20 mm layers, three walls and supports off**. An earlier guard printed successfully nose-down without supports. Inspect the sideways pockets and stop-pad overhangs in the slicer preview. Avoid Auto Orient if it flips the guard onto its bottom.

| Feature | Dimension |
|---|---:|
| Pocket diameter | 6.20 mm |
| Pocket seating depth | **2.95 mm**, selected after depth testing |
| Glue dimple in each seat | **2.50 mm diameter × 0.10 mm deeper** |
| Total bottom thickness | **4.25 mm** |
| Plastic below the ordinary seating annulus | **1.30 mm** |
| Plastic below the deepest glue dimple | **1.20 mm** |
| Side wall / roof / nose wall | **1.80 / 2.00 / 2.00 mm** |
| External floor-to-roof height | **32.57 mm** |
| Width / front-to-back length | **41.67 / 41.47 mm** |
| Exported STL footprint × print height | **41.67 × 32.57 × 41.47 mm** |

The final pockets are **blind**. Removal holes remain exclusive to coupons and gauges. Each dimple leaves a broad, flat annular seat so adhesive can occupy a small recess without deliberately raising the whole magnet. This is a design starting point, not a measured bond-strength result.

The thicker bottom grows **outward/downward**, preserving the key-facing floor at Z=−0.25 mm. The roof moves down **3.45 mm**: 2.50 mm for the requested net height reduction plus 0.95 mm to compensate for the extra bottom thickness. Root and nose ceilings move together, retaining the taper and wall thicknesses. This is a **net external height correction**, rather than simply reducing the internal cavity by 2.5 mm.

The photo-derived `key_height=28.92` is retained as a reference, with the later physical-fit correction applied separately. The revised central rear cavity ceiling is **Z=26.07 mm above the key underside**, and its outer roof is Z=28.07 mm. This differs from that original height measurement; dry-fit the actual key and both moving paddles under the revised roof before gluing. At the original paddle-tip datum, the central cavity ceiling is approximately Z=21.03 mm; no measured paddle height/travel envelope is available to establish that clearance numerically.

## Magnets and assembly

Hardware: **two disc magnets fitting the tested 6.20 mm pockets**, with the current pair measured by the owner at **2.96 mm thick**, plus a small amount of cyanoacrylate glue. These are approximately 6 × 3 mm discs. The exact purchase listing and magnetic grade remain unconfirmed.

The chosen **2.95 mm seating depth is exact**; the model does not silently add another glue allowance. A truly 2.96 mm magnet in a perfect 2.95 mm pocket would be **0.01 mm proud** before adhesive. Printed fit determined the owner’s selection. Confirm both actual magnets sit as intended; a glue film or debris can still lift them.

1. Dry-fit the guard without magnets first. Seat against both stops and operate both levers through their full movement. Check the lower roof and tapered nose for contact.
2. Test each magnet’s polarity against its corresponding key magnet, then mark its outward-facing side before bonding. Both must attract the key independently.
3. Clean the pocket and magnet bonding face. Use a tiny amount of CA in the dimple, seat the magnet fully against the annulus, and remove squeeze-out. Keep the guard separate from the key while the glue cures according to its instructions.
4. Once cured, check seating, removal and gentle handling retention. Avoid forcing a magnet or pressing on the moving paddles.

CA is a reasonable starting adhesive for this combination: [Prusa’s bonding guide](https://blog.prusa3d.com/the-great-guide-to-gluing-and-assembling-3d-prints_44908/) discusses CA for PETG, and [K&J’s magnet bonding guide](https://www.kjmagnetics.com/blog/sticky-business-how-to-glue-neodymium-magnets) lists CA and epoxy for neodymium magnets. The 1.20 mm backing is a conservative starting choice, not an experimentally established minimum. The glue-dimple dimensions are also design choices, rather than dimensions specified by those sources. Keep the rest of the shell thin; matching the top and sides to the magnet-bearing bottom would add bulk without helping pocket backing.

## Geometry and accepted fit data

Coordinates: X is width, +Y points toward the paddle tips, the stationary body’s front edge is Y=0, and the key underside is Z=0. These fit-critical dimensions are retained:

| Datum | Value / basis |
|---|---|
| Key width | 36.77 mm, caliper photo |
| Original key-height input | 28.92 mm, caliper photo; later physical height correction is separate |
| Paddle projection | **27.11 mm**, owner measured |
| Pocket centers | **X=±7.755 mm, Y=−4.50 mm**, physically reported aligned |
| Magnet center spacing | **15.51 mm**, from 21.51 mm outer span minus 6 mm diameter |
| Original near-edge estimate | 1.50 mm behind the body edge, used only to retain pocket Y |
| Later far-edge measurement | 8.24 mm behind the body edge |
| Rear margin | 2.00 mm behind that measured far edge |
| Rear shell plane | Nominal Y=−10.24 mm; rendered Y=−10.30 mm |
| Underbody gap | 0.25 mm |
| Side clearance | 0.65 mm each |
| Stops | Two 3.30 mm wide × 1.60 mm deep × 3.20 mm tall pads |
| Actual stop bounds | X=±15.735…19.035 mm, Y=0.15…1.75 mm, Z=−0.29…2.91 mm |
| Actual inside / outside nose planes | Central Y=29.17 / 31.17 mm |
| Nominal tip gap / nose wall | 2.00 / 2.00 mm |

The 0.12 mm centered loft slices add 0.06 mm at the ends, explaining the nominal/rendered plane differences. Stop seating can permit about 0.15 mm extra insertion, giving approximately 1.91 mm central axial tip clearance. The owner’s exposed length check was satisfactory, so this revision does not move the nose or stops.

The approximate near/far magnet-edge measurements disagree by 0.74 mm. Pocket centers are intentionally preserved because they fit; the later far-edge measurement independently sets the rear margin. Do not derive new centers from it.

Nose-down transforms assembled `(x,y,z)` to `(x,z+4.50,31.17−y)`. The closed nose sits at print Z=0 and the open rear rim at Z=41.47 mm. `print_orientation="as_used"` preserves assembled coordinates, including a floor bottom at Z=−4.50 mm; it is an inspection orientation, not the support-free print orientation.

## Regenerating the full guard

The source defaults to 2.95 mm pockets and nose-down printing:

```sh
openscad --backend=Manifold --hardwarnings --export-format=binstl \
  -o output/rlp_v3_guard.stl \
  models/ham_radio/n0sa_rlp_v3_guard/n0sa_rlp_v3_guard.scad
```

`production_pocket_depth`, `glue_relief_depth`, `glue_relief_diameter`, `magnet_min_floor` and `roof_lowering` control the new construction. Bottom thickness derives from the selected pocket, dimple and minimum backing. The roof adjustment is independent of backing thickness, so a later thinner-backing trial removes material from the outside while preserving the fitted ceiling and magnet seats. Assertions reject a guard with inadequate backing below its glue wells.

## Recoverable test parts

The same source supports `guard`, `fit_coupon`, `magnet_gauge`, `floor_coupon`, `depth_gauge` and `fit_test_plate`.

- `fit_coupon`: floor overlap, two magnet seats and shallow side guides.
- `magnet_gauge`: two diameter-tolerance pockets; the notched +X end is looser.
- `floor_coupon`: exposed floor and the same stops, with a solid engraved inside-nose reference and dashed original paddle-tip datum. It uses 2.95 mm seats; it omits the glue dimples.
- `depth_gauge`: the five labeled depths **2.50, 2.65, 2.80, 2.95 and 3.00 mm**, all at 6.20 mm diameter. Its independent 4.00 mm base leaves at least 1.00 mm of seating material. The notched end is shallowest.
- `fit_test_plate`: separate floor coupon and depth strip arranged on one plate, without joining tabs.

Every test pocket has a **2.00 mm push-out hole** under its seating annulus. Test without glue, remove the part from the key, and use a pin smaller than the hole to recover the magnet. `test_pushout_diameter=0` disables these holes in test parts; it never affects the full guard.

The depth strip defaults to **edge-down**, with upright labels and horizontally measured pocket depths, matching the nose-down guard. Print it at 100% scale, PETG, 0.4 mm nozzle, 0.10 mm layers and supports off. The optional `depth_gauge_orientation="floor_down"` lays it flat, but small depth differences may quantize to layer heights. Both exports start at print Z=0. The other coupons export floor-down.
