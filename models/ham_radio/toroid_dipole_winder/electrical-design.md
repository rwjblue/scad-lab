# Electrical design: a light 1:1 current balun

Use **one Fair-Rite 2631801202 Mix 31 core with 12 bifilar turns of 22 AWG
enamelled copper wire**. This is a buildable prototype specification for the
open-mount winder, with an intended operating profile of mostly **10 W CW** and
occasional operation **below 100 W**. It has **no verified power rating or
measured RF performance yet**.

The working band assumption is **40–10 m, approximately 7–30 MHz**, because the
requested bands have not been specified. This is for a resonant or linked,
centre-fed dipole using coax. The 1:1 balun does not turn an arbitrary wire
length into a multiband matched antenna. Include 80 m in the measurements if
useful, but do not assume coverage from the ferrite material designation.

## Selecting from the parts bin

The [N1RWJ inventory](https://rwjblue.com/radio/equipment/parts-bin/), checked
September 10, 2026, still labels these quantities **incoming** from the August
13 order. They are listed parts, not a verified count of received stock.
Dimensions below are nominal OD × ID × height; mass is the current
manufacturer's catalog value for the bare core.

| Listed core | Quantity | Dimensions | Mass | Assessment for this build |
| --- | ---: | --- | ---: | --- |
| [Medium Mix 31, 2631801802](https://fair-rite.com/product/toroidal-suppression-core-2631801802/) | 5 | 22.1 × 13.7 × 6.35 mm | 7 g | Attractive for a later minimum-weight QRP version; less winding space and thermal capacity. |
| **[Large Mix 31, 2631801202](https://fair-rite.com/product/toroidal-suppression-core-2631801202/)** | **5** | **29 × 19 × 13.85 mm** | **24 g** | **Selected: useful winding aperture, modest outside diameter, and published measurements of this exact core.** |
| [FT-114-43, 5943001001](https://fair-rite.com/product/toroids-5943001001/) | 25 | 29 × 19 × 7.5 mm | 13 g | Lighter alternative with the same aperture; would need its own winding evaluation. |
| [FT-140-43, 5943002701](https://fair-rite.com/product/toroids-5943002701/) | 2 | 35.55 × 23 × 12.7 mm | 33 g | More winding room, but larger and heavier than the selected core before insulation. |

Mix 43 can make useful HF current baluns. This choice is not a rule that 43
cannot be used for suppression. Fair-Rite describes [Mix 31](https://fair-rite.com/31-material-data-sheet/)
as a suppression material extending down to 1 MHz. Its suitability here comes
from the combination of material, geometry, winding and verification, not
from a generic wattage assigned to a toroid size.

For the selected core, allow for the manufacturer's tolerances: **29 ±0.75 mm
OD, 19 ±0.50 mm ID, 13.85 ±0.40 mm height**. The CAD reserves a **36 mm diameter
× 20 mm thick finished package**. That is a fit allowance; measure the actual
wound and sleeved part before choosing the CAD parameters.

## Winding and connections

1. Cover the bare ferrite with a thin, smooth layer of PTFE tape to protect the
   enamel from abrasion. Avoid bulky overlaps.
2. Cut **two 650 mm lengths of 22 AWG heavy-build enamelled copper winding
   wire**. Label the conductors A and B. Leave enough lead length for the
   connector and antenna splices, then trim after fitting.
3. Wind A and B together for **12 turns**. Each passage of the pair through
   the centre counts as one turn: there are 12 turns on each conductor.
   Keep the pair close together and distribute the turns around the core,
   leaving a gap between the input and output ends. Wind both conductors in
   the same sense; a crossover is not required.
4. Remove enamel completely from the connections and verify with a meter.
   Add flexible insulated pigtails for the antenna connections; anchor their
   tension in the winder's strain-relief holes. Neither the winding nor its
   solder joints should carry antenna or coax loads.

```text
BNC centre ── A start ═══ 12 turns ═══ A finish ── dipole leg 1
BNC shell  ── B start ═══ 12 turns ═══ B finish ── dipole leg 2
                         same core
```

This is a **1:1 Guanella current balun**. The two conductors remain electrically
separate: no centre tap, series connection, compensating capacitor, or direct
connection bypassing the winding. Equal and opposite differential currents
largely cancel their core flux; common-mode current sees the choke impedance.

The pair is also a short transmission line. **22 AWG does not itself specify
50 Ω characteristic impedance.** Enamel thickness, spacing and winding layout
matter. Thick PTFE hookup wire is not an automatic substitute with the same
upper-HF match. The terminated input measurement below checks the actual build.

## What the evidence establishes

[KN5L's measurements of a ten-turn 2631801202](https://www.kn5l.net/FT31-Loss/FR2631801202/)
and his [measurement/model comparison](https://www.kn5l.net/Balun-CM/BalunMeasure/)
support this core as an HF choke candidate. The latter reports self-resonance
near 17.3 MHz for his ten-turn assembly. **Those are not measurements of this
12-turn bifilar winding.** Do not copy its impedance curve or scale it by turns
squared across HF without accounting for winding capacitance.

The closest published twelve-turn comparison is [VE5REV's measured
2631801202 choke](https://mjarc.ca/docs/T31-2631801202-TestData.pdf): **12 turns
of RG-316 coax with a crossover**, reporting about −31 dB average fixture
S21 magnitude across 80–10 m. This strengthens the case for the selected core
and turn count, but it uses a different transmission line. The report supplies
neither our bifilar pair's input match nor its complex common-mode impedance,
and does not establish a thermal power rating. Its fixture attenuation is
not a prediction of installed antenna-current reduction. Keep the intended
40–10 m coverage and power capability subject to the checks below.

[K6ARK's commercial 1:1 kit instructions](https://k6ark.com/qrp-20w-11-balun-instructions/)
use 10–12 bifilar magnet-wire turns and heatshrink for a compact dipole centre.
That supports the construction approach. Its core, package and claimed power
capability do not establish a rating for this design.

## Finishing supplies

The inventory does not list winding wire. Obtain the specified magnet wire
and thin PTFE tape, or confirm suitable wire already on hand. Its largest
listed heatshrink has only **9 mm expanded ID** and will not cover the core.
Obtain approximately **38–40 mm expanded-ID thin-wall heatshrink**, checking
that it passes over the finished package. Expanded diameter is different from
the lay-flat width some sellers specify.

Test before permanently sleeving. Shrink the module **off the PETG winder**,
then mount it on the specified cushion with nonconductive straps. Insulate and
weather-protect the splices separately. Heatshrink reduces exposed area and
abrasion but does not establish a waterproof rating, carry tension, or improve
cooling. A whole-module metal band through the core aperture must not form a
closed conducting turn.

## Bench and deployment checks

Record the core part, wire specification, turns, photographs, lead lengths,
sleeve and measured temperature conditions with the results.

1. **DC checks:** A start–finish and B start–finish must be continuous. A–B
   must remain isolated. Check again after securing the package.
2. **Input match:** calibrate the analyser at the input connector. Terminate
   the two antenna leads with the inventory's **49.9 Ω resistor**, keeping
   leads short, and sweep the intended bands. A useful prototype target is
   **SWR ≤1.3:1**. Compare the resistor directly to identify fixture error.
   This resistor is **0.25 W: analyser use only**, never a transmitter load.
3. **Common-mode impedance:** disconnect the antenna and transmitter. For this
   separate measurement, temporarily join A and B at each end of the winding.
   Insert these two junctions as a series device between the VNA's two centre
   conductors. Connect the port shields directly together with a short, wide
   connection; neither winding junction goes to shield. Calibrate/de-embed
   the fixture to its DUT terminals with a suitable through reference. Keep
   exposed leads short and separated to reduce bypass capacitance.

   For matched **50 Ω ports** and a calibrated series fixture:

   ```text
   Zcm = 2 × Z0 × (1 / S21 - 1) = 100 × (1 / S21 - 1) Ω
   ```

   Use **complex linear S21**, including phase, not its dB magnitude. Inspect
   `R = real(Zcm)`, `X = imag(Zcm)` and `|Zcm|` across the bands. The engineering
   target is **|Zcm| ≥2 kΩ**, with several kΩ preferred and substantial
   resistance rather than a sharp, mainly reactive peak. These are design
   targets, not measured results or guarantees of a particular deployment's
   current reduction. Repeat after sleeving and mounting. Remove the temporary
   junctions before restoring normal wiring.
4. **Thermal assessment:** first operate at **10 W CW** with the intended
   resonant dipole, coax route and normal sending duty cycle. Measure module
   temperature and ambient temperature over a representative session. Stop
   for continuing temperature rise, changing match, softening or damaged
   insulation. Then assess the actual occasional higher power and duty cycle
   progressively, with cooling between trials. A balanced dummy load checks
   differential heating but does not reproduce installation common-mode stress.

Power capability remains unassigned until the assembled unit is measured and
tested. Heat depends on common-mode current, band, mismatch, duty cycle and
packaging. Successful 10 W operation or an unchanged input SWR does not by
itself qualify the assembly for operation approaching 100 W.
