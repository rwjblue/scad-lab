# FT-140 Current-Balun Enclosure

`ft140_current_balun_holder.scad` is a compact PETG enclosure for a radio-end
current balun using an FT-140-size toroid. It combines:

- opposing RADIO and COAX OUT right-angle BNC bulkheads;
- an internal toroid support and four closed-floor strap anchors;
- two M5 balanced-output studs on opposite long walls; and
- a separate slip-on protective lid.

The box sits at the radio/ground end of the feedline and is not an antenna
strain relief. Closed, it is approximately **79 × 55 × 24 mm**. Both parts
print with their open sides upward and require no generated supports.

This is a mechanical enclosure, not a prescribed winding design. Select and
test the winding for the intended frequency range and power.

## Why the Terminals Are on Opposite Sides

Commercial balun enclosures commonly distinguish between studs on top and
studs on the sides. Balun Designs offers both configurations on its
[Model 1115 1:1 current balun](https://www.balundesigns.com/model-1115-1-1-current-balun-1-31-mhz-3kw/)
and describes internal ring-terminal/stud assembly in its
[kit notes](https://www.balundesigns.com/assembly-notes-for-model-1113-1115-kits/).
A lightweight portable-dipole example independently places its bolts on
[opposite sides of the center](https://practicalantennas.com/designs/dipole/dipole-kit/)
to increase separation and keep one stud out of the operator's hand while the
other is tightened.

That pattern fits this enclosure better than a shared terminal panel:

- each wing nut has unrestricted rotation and cannot hit a BNC plug;
- the balanced conductors remain physically separated;
- permanent pigtails and solder joints stay inside the box;
- both BNC end walls remain clear; and
- the lid is independent of every electrical connection.

The feedline's approximately 12.7 mm conductor spacing simply fans out for its
short ring-terminal leads at the box. The M5 stud separation is mechanical and
does not define the balanced line's characteristic impedance.

## Default Geometry

The toroid defaults follow the nominal **35.55 mm OD × 23.00 mm ID × 15.00 mm
height** dimensions of the Fair-Rite 31-material
[2631805302 suppression core](https://fair-rite.com/printer_friendly_datasheet.php?part=2631805302).
The model separately reserves **42 mm OD × 18.5 mm height** for the completed
winding.

| Parameter | Default |
| --- | ---: |
| Box exterior | 76 × 52 × 22.5 mm |
| Closed envelope | approximately 79 × 55 × 24 mm |
| Floor / general walls | 1.8 / 1.8 mm |
| Local BNC mounting section | 4.0 mm |
| Toroid support OD / opening | 42.0 / 20.0 mm |
| Strap-anchor opening | 3.2 × 1.8 mm |
| BNC bulkhead hole | 9.7 mm |
| BNC connector-axis height | 11.0 mm |
| M5 printed holes | 5.4 mm |
| M5 connector-axis height | 11.0 mm |
| Lid clearance per side | 0.30 mm |
| Modeled box + lid PETG mass | approximately 35 g |

The lid overlaps the box by 3.5 mm but stops above a nominal 14 mm BNC body.
Small finger scallops help remove it without pulling on a connector. One raised
rib identifies RADIO and terminal A; two ribs identify COAX OUT and terminal B.
These tactile marks remain readable when tiny printed lettering would not.

## Output Modes

Choose `render_mode` near the top of the SCAD file:

| Mode | Output |
| --- | --- |
| `"box"` | enclosure base and walls |
| `"lid"` | lid, already oriented for printing |
| `"print_layout"` | box and lid side by side |
| `"assembly_preview"` | exploded reference view with simplified hardware |
| `"bnc_bulkhead_fit_test"` | 9.4, 9.7, and 10.0 mm upright holes |
| `"m5_fit_test"` | 5.2, 5.4, and 5.6 mm upright holes |

Export the box and lid separately when possible so each can be reprinted
without the other.

## Fit Tests

Both BNC walls target this
[Superbat single-hole threaded bulkhead BNC](https://a.co/d/00oDfxkC). The
listing does not provide a trustworthy mechanical drawing, so 9.7 mm is a
starting point rather than a guaranteed fit. For comparison, a similar
commercial bulkhead BNC specifies a 9.6 mm mounting hole and 5.5 mm maximum
panel thickness in its
[manufacturer drawing](https://www.fairviewmicrowave.com/content/dam/infinite-electronics/product-assets/fairview-microwave/product-datasheets/FMCN5169.pdf).

For either upright coupon, the clipped base corner marks sample 1, the smallest
hole. Hole sizes increase in order toward the opposite end:

- BNC: **9.4, 9.7, 10.0 mm**;
- M5: **5.2, 5.4, 5.6 mm**.

Choose the smallest hole that accepts the hardware without force. Set
`bnc_bulkhead_hole_d` directly for the BNC. Set `m5_hole_clearance` to the
chosen M5 hole diameter minus 5.0 mm.

The lid defaults to 0.30 mm clearance on each side. If dimensional calibration
is good, print it unchanged first. Increase `lid_clearance` by 0.10 mm if it
binds after elephant-foot removal; decrease it by 0.05–0.10 mm if it is too
loose. Do not force a tight lid over installed connectors.

## Hardware Bill of Materials

Brass terminal hardware is electrically preferable; stainless is mechanically
acceptable for a low-power prototype. The dimensions below match the defaults.

| Qty | Hardware | Specification |
| ---: | --- | --- |
| 2 | Terminal screws | M5 × 25 mm, fully threaded, pan- or button-head |
| 4 | Terminal flat washers | M5, approximately 5.3 mm ID × 10 mm OD |
| 2 | Terminal base nuts | M5 finished hex nuts |
| 2 | Terminal lock washers | M5 internal-tooth |
| 2 | Removable terminal nuts | M5 wing nuts |
| 4 | Ring terminals | closed ring, matched to wire gauge, M5/#10 stud |
| 4 | Ring-terminal heat-shrink pieces | sized for the selected crimp barrels |
| 2 | Toroid straps | 2.5 mm × approximately 100–150 mm zip ties or narrow reusable ties |
| 2 | Bulkhead BNC | Superbat single-hole solder-terminal connector, with supplied nut, tooth washer, and shell lug |
| 4 | Optional sealing washers | thin EPDM/neoprene washers sized for the two BNC shoulders and two M5 studs |
| 1 | Optional seam wrap | narrow self-fusing silicone tape or good vinyl electrical tape |

For 26 AWG DXE-SANTW-500 feedline, the partially insulated, tin-plated
[TE Connectivity 324075](https://www.te.com/en/product-324075.html) is one
dimensional example with a 26–22 AWG barrel and M5/#10 ring. Do not use an
oversized 22–16 AWG automotive barrel on 26 AWG wire. Use the specified crimp
tool, heat-shrink the crimp barrel, and pull-test every termination.

## Electrical Topology

This is one two-conductor, 1:1 current choke with two alternative output
interfaces:

```text
RADIO BNC center ----- conductor A through core -----+-- COAX OUT center
                                                     +-- M5 terminal A (one rib)

RADIO BNC shell ------ conductor B through core -----+-- COAX OUT shell
                                                     +-- M5 terminal B (two ribs)
```

Do not bond the two BNC shells together outside the winding. Both center and
shell paths must travel through the paired winding for the choke to work.

For coax common-mode-choke service, use both BNCs and leave both M5 terminals
unloaded. For balanced output, use RADIO plus the two M5 terminals and leave
COAX OUT capped and disconnected. COAX OUT and the M5 terminals are parallel
outputs; do not attach two loads simultaneously.

This is not an impedance-transforming unun. An end-fed random-wire or end-fed
half-wave system still needs its appropriate matching network. This unit can
provide common-mode suppression in the 50-ohm coax path.

## Starting Bifilar Winding

For portable **40–10 m** experimentation with the Fair-Rite 2631805302 core,
start with **12 bifilar turns of two differently colored 22 AWG PTFE-insulated
wires**, approximately **80 cm / 32 inches each**. Every passage through the
core center counts as one turn. Keep the pair side-by-side or lightly twisted,
sequential, and snug without crushing the insulation.

This is an experimental starting point, not a guaranteed broadband or power
rating. Fair-Rite identifies 31 material as an EMI-suppression material useful
from HF upward, while K9YC's measured
[2018 Choke Cookbook](http://k9yc.com/2018Cookbook.pdf) uses different turn
counts on the larger 2.4-inch 31-material core. The smaller FT-140 winding must
be measured and heat-tested as built.

If 80 and 60 m matter more than the upper bands, **14 turns** is a reasonable
second prototype to measure. More turns are not automatically better: winding
capacitance lowers self-resonance and may reduce upper-HF choking impedance.

The 22 AWG copper and PTFE insulation do not establish the RF power rating.
Start with low power, inspect SWR and continuity, then increase power in short
steps while monitoring core and wire temperature. Digital modes, imbalance,
and high SWR require substantial derating.

### Winding Connections

1. Mark the winding ends `A-IN`, `B-IN`, `A-OUT`, and `B-OUT` before trimming.
2. Solder `A-IN` to RADIO center and `B-IN` to the RADIO shell lug.
3. Solder `A-OUT` to COAX OUT center and `B-OUT` to the COAX OUT shell lug.
4. Add a short insulated pigtail from COAX OUT center to the internal ring on
   terminal A, marked by one external rib.
5. Add the matching pigtail from the COAX OUT shell lug to the internal ring on
   terminal B, marked by two external ribs.

Keep all leads short and clear of the opposite end of the winding. Verify
continuity from RADIO center to COAX OUT center/A, continuity from RADIO shell
to COAX OUT shell/B, and **no DC continuity** between A and B.

## Terminal Stack

Insert each M5 screw from inside the box, pointing outward. From inside to
outside:

```text
M5 screw head
  -> M5 flat washer
  -> permanent internal pigtail ring
  -> printed boss and side wall
  -> M5 flat washer
  -> M5 base hex nut (tightened to make a fixed stud)
  -> removable balanced-feedline ring
  -> M5 internal-tooth lock washer
  -> M5 wing nut
```

Hold the screw head while tightening the base nut. Later, hold the base nut if
needed while loosening the wing nut so the fixed stud does not unwind. Hand
tighten only; do not crush the PETG or use pliers on the wings.

## Printing and Assembly

1. Print the BNC and M5 coupons and update the hole parameters.
2. Print `box` and `lid` open-side up in PETG with four walls, 0.16 or 0.20 mm
   layers, and about 20–30% infill. No brim or supports should be necessary on
   a clean build plate.
3. Remove elephant foot from the box rim and test the empty lid before adding
   hardware. It should slide on without bowing the walls.
4. Crimp the two short output pigtails to their M5 rings. Install both M5 fixed
   studs and internal rings using the documented stack.
5. Insert both BNCs from outside their end walls. Install each shell lug, tooth
   washer, and nut inside. Support the connector while tightening; do not crush
   the PETG. If splash resistance matters, place a thin sealing washer under
   each external BNC shoulder and each external M5 flat washer, or use a very
   small amount of neutral-cure electronics-safe RTV at those penetrations.
6. Wind and label the toroid. Thread two ties through the four internal anchor
   bridges, set the winding on its annular support, and tighten the ties only
   enough to prevent movement.
7. Solder the winding and pigtails according to `Winding Connections`. Cover
   every exposed joint with appropriately rated heat shrink.
8. Perform continuity, short, impedance, and low-power thermal checks before
   fitting the lid.
9. Fit the lid. For splash-prone use, wrap only the lid seam with removable
   self-fusing silicone tape. Keep the BNC bayonet interfaces and wing nuts
   accessible.
10. Attach the balanced-feedline rings to the external studs, or connect COAX
    OUT for coax-choke service—never both loads at once.

The printed enclosure is an abrasion, dust, and incidental-splash shield, not
a certified waterproof enclosure. A thin removable seam wrap is preferable to
potting: the toroid needs to shed heat and remain available for inspection or
rewinding.
