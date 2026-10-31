# Toroid, terminal and BNC clearance review

Reviewed 17 September 2026. The 88 mm-tall prototype had room for the M3
washers, but not comfortable routing space beyond a winding-side ring
terminal pointed toward the core. The revised balun center is **100 mm tall**.
Both strap settings receive the change; the compact centers remain 39 mm tall.

## Hardware evidence

- **Panduit P22-6R-M**, drawing N41227BB-DC revision 07:
  [manufacturer drawing in the parts bin](https://rwjblue.com/downloads/radio/parts/panduit-p22-6r-m-datasheet.pdf).
  Ring-center-to-barrel-entry dimension M is 0.42 ±0.02 inch, so use
  **11.176 mm maximum**. Ring width W is 0.205 ±0.010 inch, or **5.461 mm
  maximum**. The barrel is approximately 2.05 mm OD (reference dimension).
  The drawing specifies 26–22 AWG solid or stranded copper. Enamel must be
  removed before terminating magnet wire.
- **Amphenol 31-221-RFX**, [current customer drawing B6351D4-ND3G-50 revision L](https://www.amphenolrf.com/en-us/assets/file/4065787961/):
  overall length 26.9 mm reference, maximum panel thickness 3.3 mm,
  solder cup OD 2.1 mm and ID 1.5 mm, nut 11 mm across flats and 2.4 mm
  thick. The axial distance from the mounting face to the cup tip is not
  separately dimensioned on this sheet.
- The [Amphenol catalog](https://amphenol.com.ar/wp-content/uploads/2020/11/Amphenol-RF-1.pdf),
  printed page 115 (PDF page 133), figure 2 and the **31-221-RFX** row give
  a = 27.0 mm overall and d = 12.0 mm to the mounting face. Thus the nominal
  rear projection above our 3 mm shelf is **27 − 12 − 3 ≈ 12 mm**.
  These are rounded catalog dimensions, not a tolerance-certified maximum;
  the newer customer drawing governs hardware details such as the nut size.

The CAD therefore reserves **13 mm above the shelf for the connector**,
then adds a separate **12 mm lead-routing gap**. This avoids treating the
solder joint or wire bend as part of an undocumented connector dimension.
Measure the installed connector if it exceeds this envelope, then increase
`bnc_rear_projection`. A washer placed under the mounting flange changes
the datum; the calculation assumes the flange seats directly against the
outside of the printed shelf.

## Conservative vertical clearances

All toroid distances use the **34 mm wound envelope**, not the 29 mm bare
ferrite. Values are separations along the spine, without taking credit for
the curved toroid edge, sideways offsets or separation in depth.

| Clearance | Previous | Revised |
| --- | ---: | ---: |
| Wound top to M3 post center | 12 mm | 20 mm |
| Wound top to lower edge of a 7 mm washer | 8.5 mm | 16.5 mm |
| Wound top to downward winding-ring barrel entry, at maximum M | 0.824 mm | 8.824 mm |
| BNC hardware envelope above the shelf | 12 mm | 13 mm |
| Hardware envelope tip to wound bottom | 9 mm | 12 mm |
| Nominal bare solder-cup tip to wound bottom | About 9 mm | About 13 mm |
| Connector envelope tip to lower tie-slot mouth | 3.5 mm | 6.5 mm |
| Printed height | 88 mm | 100 mm |

The original 8.5 mm washer check did **not** account for the much longer
downward-facing winding terminal. The 0.824 mm gap was not a modeled metal
collision, but left almost no straight space for the wire to leave its
barrel before bending. The revised 8.824 mm makes that route practical to
prototype. If insulation projects 3 mm beyond the barrel, about 5.8 mm of
vertical space remains before the wound envelope. This is an assembly
allowance, not a manufacturer-specified minimum wire bend radius.

Likewise, allowing a solder joint or sleeve to extend 3 mm past the BNC
hardware envelope leaves 9 mm of the lower routing gap. Keep the pair
together, use relaxed bends and trim after fitting. These dimensions are
not a claim that every soldering iron or wrench fits with the toroid installed.

## Ring orientation and assembly

Use an outward-facing ring for each antenna leg, toward its wire weave,
and a second ring pointed downward for the winding lead. The two rings
stack on the same M3 stud. The existing 18 mm post-to-inner-wire-hole
spacing and 4.724 mm minimum outward barrel-to-hole-mouth space are unchanged.
This applies both to X = ±10 mm posts without packing slots and X = ±7 mm
posts with packing slots. The existing suggested 16 mm screws need a dry
fit with the actual washers, nuts and two rings.

Fit and tighten the BNC and solder its two leads before securing the
toroid. Point the shell solder tag forward, away from the backplate; its
12.7 mm radial reach is different from the axial tip clearance measured
here. Put the winding rings on their studs, leave relaxed lead bends and
snug the toroid ties last. The new [assembly render](assembly.png) shows
both ring directions; winding paths and hardware details remain schematic.

## Parameters and checks

Defaults in the shared `dipole_center.scad`:

```scad
bnc_rear_projection = 13;
bnc_to_toroid_gap = 12;
toroid_to_post_gap = 20;
```

At the default 34 mm wound diameter, the wound envelope spans Y = 28–62 mm,
the BNC hardware envelope ends at Y = 16 mm, and the M3 post centers are at
Y = 82 mm. Toroid tie rows are at Y = 24 and 66 mm. The coupon preserves
these same interfaces.

The validators inspect the exported holes and package clearances, include
conservative maximum-width downward ring envelopes, and check the permitted
larger spacing settings. The clearance improvement is modeled; actual
connector, solder, crimp, nut-tool and wire-bend fit still needs a dry assembly.
