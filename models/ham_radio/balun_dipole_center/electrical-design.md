# Winding and qualifying the current balun

Guide prototype: one **Fair-Rite 2631801202 mix 31** core, **13 bifilar
turns of BNTECHGO 22 AWG polyurethane-enamelled copper**, ASIN B07DYF89T9.
The fixed sequence is six ordinary paired turns, one paired crossover
aperture passage (turn 7), then six ordinary paired turns. Input leads emerge
toward the BNC below and output leads toward the antenna terminals above.
The owned 22 AWG FEP is a viable comparison winding. Mostly 12/50 W CW on a resonant
40/30/20/17/15 m dipole; 100 W is the intended qualification target.
No power rating has been measured for this assembly.

## Two continuous conductors

```text
BNC centre ── A start ══ 13 turns ══ A finish ── terminal / leg 1
BNC shell  ── B start ══ 13 turns ══ B finish ── terminal / leg 2
                         same core
```

This is a 1:1 Guanella current balun. Both conductors are wound together in
the same direction. There is **no series join, centre tap, compensating
capacitor or direct shell-to-leg bypass**. Equal and opposite signal currents
largely cancel core flux; net common-mode current sees the choke impedance.

1. Print, inspect and fit the separate open-bottom guide following
   [winding-guide.md](winding-guide.md). Protect any exposed ferrite edge
   that contacts wire with a thin smooth PTFE layer and account for tape
   in the fit; avoid thick overlaps. Cut two continuous wires using the
   modeled path length plus generous termination tails, and identify A/B.
2. Follow the paired channels and [numbered debug view](winding_debug.png):
   wind ordinary turns 1–6, carry the entire pair across the aperture as
   turn 7, then wind ordinary turns 8–13. The input and output tails emerge
   on opposite sides of the toroid.
   Keep the turns magnetically aiding; do not make a cancelling winding
   by reversing the direction of passage through the aperture.
   **Count every passage of the pair through the hole, including the
   crossover, toward the total of 13 turns on each conductor.** The twelve
   ordinary turns plus crossover are thirteen, not twelve.
3. Orient the input tails toward the BNC below the core, and the output
   tails toward the posts above it. Keep the output pair together until
   it splits toward the posts. Leave relaxed bends and trim only after
   dry fitting. The crossover moves both insulated wires together; it
   does not swap A/B, join them, or change the electrical circuit.
   Measure the wound package against the 34 × 18 mm CAD allowance.
4. Remove enamel completely at terminations. Inspect and meter the connection;
   insulate soldered splices and keep all strain off enamelled wire.
   Use the 26–22 AWG Panduit terminals only on appropriate stripped conductors.
   For the 18 AWG winding, solder short 22 AWG FEP pigtails and individually
   insulate the splices, or use eyelets that fit both 18 AWG and the M3 stud.
   Keep pigtails short and strain-free; do not force 18 AWG into P22-6R-M.

The pair is a transmission line as well as a choke winding. Insulation,
spacing and lead layout determine its impedance; **gauge alone does not mean
50 ohms**. The selected
[BNTECHGO 22 AWG wire](https://www.amazon.com/dp/B07DYF89T9) has an
approximately 0.644 mm nominal bare copper diameter. Its advertised
0.650 mm finished diameter is an adjustable prototype default; enamel
thickness is unverified. Specify the enamel build and measure finished OD.
The guide defaults to a 0.100 mm gap between the enamel surfaces, giving
`wire_center_spacing = wire_od + wire_surface_gap = 0.750 mm`.
Groove fit clearance is independent and must not widen that intended center
spacing; it reduces the remaining printable ridge between channels instead.
This spacing is not a validated 50 Ω geometry. Thin enamel
can make a touching pair's impedance too low; enamel is not automatically
better matched than hookup wire. Begin with a short paired sample, adjust
spacing only from measurements, and then recheck the complete winding.

The owned orange/yellow 22 AWG FEP has 19 x 0.15 mm strands and **1.42 +/-0.1 mm
insulated OD**. There is nothing inherently unsuitable about FEP here. Its
thicker jacket takes more room and probably produces a higher-impedance
pair than 50 ohms; this is a geometric inference, not a measured value.
It is a reasonable winding experiment if the final match, insertion loss,
common-mode impedance and thermal tests pass, as required for enamel too.
Silicone stock is bulkier still. The 28 AWG magnet wire is a
small-coil/low-power candidate, not the first choice for this 100 W goal.

[BNTECHGO 18 AWG listing](https://www.amazon.com/dp/B07H7DP7RN) ·
[BNTECHGO FEP specifications](https://bntechgo.com/bntechgo-22awg-fep-teflon-coated-tin-plated-copper-wire-in-orange-100-ft-has-a-temperature-rating-of-65-to-200-c-fep-teflon-wire-is-suitable-for-applications-requiring-high-temperature-resistance/).
The eight exact variants and original pack sizes are now in the parts-bin
source in the sibling `rwjblue.com` repository. The further wire comparison
is in `antenna-lab/docs/case-studies/owned-balun-wire.md`.


The crossover is a routing choice, not a promised RF improvement.
[G3TXQ's choke article](https://gm3sek.com/wp-content/uploads/2019/01/G3TXQ-RC.pdf)
illustrates the arrangement with coax and explicitly counts the crossover
pass as a turn. Our adaptation carries the two-wire pair together. Record
photographs and remeasure because the numerical screen does not resolve
this winding geometry. The new [guide documentation](winding-guide.md) and
[numbered debug view](winding_debug.png) describe the modeled 13-turn route;
the renders do not establish insulation safety or RF performance.

## Earlier 12-turn baseline and the 13-turn prototype

The companion `antenna-lab` study uses
[Fair-Rite material data](https://fair-rite.com/31-material-data-sheet/) and
[exact-part data](https://fair-rite.com/product/toroidal-suppression-core-2631801202/)
to compare 10–14 turns with several assumed winding capacitances.
It selects this core as a practical prototype, not a guaranteed 100 W part.

[KN5L's ten-turn measurement](https://www.kn5l.net/Balun-CM/BalunMeasure/)
and [VE5REV's twelve-turn RG-316 test](https://mjarc.ca/docs/T31-2631801202-TestData.pdf)
support trying the exact core. Neither measures this bifilar winding.
The latter uses coax with a crossover; its fixture attenuation is not
installed current reduction or a thermal power rating.

Compared with the earlier 12-turn baseline, 13 turns raises the magnetic
part of impedance by 17.4% before capacitance,
but does not necessarily improve total impedance on 20/17/15 m. In the
uncalibrated 1–8 pF scenarios, the minimum magnitude on 20 m spans roughly
1.6–7.2 kΩ for 12 turns; some scenarios miss the target. That wide range is
why measuring capacitance effects matters more than choosing 12 versus 13
on paper. The current guide starts at 13 turns and requires its own complete
sweep; the 12-turn results are not measurements or predictions validated for
this guide. These ranges are sensitivity scenarios, not confidence
intervals or guaranteed bounds for the real winding.

## RF measurements

Record core part, winding wire/insulation, turns, layout photographs, lead
lengths, pads, ties and whether measurements are before or after mounting.
Assume a resonant or linked dipole; the balun does not match arbitrary wire
lengths across all five bands.

1. **DC:** with the antenna disconnected, A start–finish and B start–finish
   must be continuous, A–B must be isolated, and enamel must isolate the wire
   from the ferrite. Repeat after flexing and mounting.
2. **Differential match:** terminate the two output posts in a short-leaded
   50 Ω test load. Calibrate at the BNC input and sweep 7–7.3, 10.1–10.15,
   14–14.35, 18.068–18.168 and 21–21.45 MHz. Prototype target: **SWR ≤1.3**.
   Compare the load directly to account for fixture error. The parts-bin
   49.9 Ω, 0.25 W resistor is analyser-only, never a transmitter dummy load.
   Use a calibrated two-port setup to assess insertion loss as well as SWR;
   a good match alone can conceal dissipation.
3. **Common mode:** temporarily join A+B at the input and A+B at the output.
   These form the two terminals of the choke for this separate measurement.
   Insert them between the two centre pins of a calibrated 50 Ω VNA series
   fixture. Join the port shields directly with a short wide connection;
   neither choke terminal goes to shield. Calibrate/de-embed to the DUT
   terminals and keep exposed leads short to limit bypass capacitance.

   Use **complex linear S21**, with phase:

   ```text
   Zcm = 2 Z0 (1/S21 − 1) = 100 (1/S21 − 1) Ω
   ```

   Inspect R, X and |Z|. Aim for **|Z| ≥2 kΩ and R ≥1 kΩ** across 40/20 m,
   preferably several kΩ resistive, and apply the same screen to 30/17/15 m
   before claiming coverage. These are engineering targets, not measured
   performance. Assess fixture error and VNA dynamic range at high impedance.
   Remove the temporary joins before normal wiring.
4. Repeat after mounting. If 17/15 m needs additional choking, test an
   external choke at the BNC in the final coax arrangement. Multiple chokes
   and intervening coax can interact; their benefit is not automatically
   the sum of standalone impedances. They cannot fix pair mismatch.

## Working toward 100 W

At 100 W into 50 Ω the differential signal is 1.41 A RMS, 70.7 V RMS
(100 V peak). At 50/12 W it is 1.00/0.49 A RMS. This current largely cancels
magnetically when balanced, but still heats the copper. The simple skin-only
model estimates about 0.84 W total winding copper loss on 40 m and 1.17 W on
20 m at 100 W, for the original 12-turn, 0.60 m per 22 AWG conductor baseline.
These are not updated loss estimates for the new 13-turn guide. The same calculation
for nominal 18 AWG gives about 0.53 W on 40 m and 0.74 W on 20 m, excluding
the 22 AWG pigtails. Actual loss includes proximity,
joints and load/mismatch effects, so those values are not a thermal budget.

Ferrite loss depends on common-mode excitation. For an illustrative 5 kΩ
resistive choke, net common-mode currents of 10, 20 and 50 mA RMS dissipate
0.5, 2 and 12.5 W respectively. The transmitter's wattage does not determine
which case applies. Air exposure helps cooling but does not establish a rating.

Use a **transmitter-rated** load for initial power tests, then the intended
resonant dipole and coax route. Start at 12 W, then test 50 W, then 100 W on
40/20 m and the remaining bands. Log ambient, ferrite and wire/joint
temperature through repeated normal CW sending cycles until stable; include
the longest key-down or tune interval you intend to use. Establish a numerical
stop temperature from the actual wire, pad and print-material limits with
margin beforehand. Stop for continuing rise, changing SWR, softening, odor or
insulation damage. Let the assembly cool between test cases.

A balanced dummy load does not reproduce installed common-mode stress.
Passing at 12/50 W does not automatically qualify 100 W. The first physical
prototype must supply that evidence before a Printables listing claims it.
