# Modular dipole design review

Revision 2 addresses failed retention in the first printed four-catch assembly.
The first print looked good and the spring controls felt comfortable, but the
winders slipped out even with the tongues beneath the heads. The independent
critic supports the revised geometry for another physical trial; the new parts
have not yet demonstrated secure retention, glove operation or durability.
The editable model is
[modular_dipole.scad](../modular_dipole.scad).

Upgrading from the first print needs a **matched revision-2 center and two
revision-2 winders**. The larger stud heads and their receiving passages change
together. The current compact setting uses 4 mm supports while
preserving the revision-2 center, head and catch geometry. An existing
revision-2 center can be reused with two shorter winders. Do not mix winder
heights. The winding profile, BNC fit and intended paired-pinch sequence remain.

## First-print failure and revision

The original 6 mm head provided 0.80 mm nominal overlap with its moving catch.
Outward movement within the neck clearance reduced this to approximately
0.45 mm before print error. Its underside also projected 1 mm beyond the neck
without support. A rounded or undersized head edge, a recessed catch edge or a
spring that does not fully return can consume that small bearing land. A sloped
printed underside can also push the flexible catch aside during withdrawal.
These are plausible explanations for the observed failure, not measurements of
the failed parts.

The [retention audit](retention_audit.py) measures sections of the exported
heads and catches and admits only poses allowed by the neck and guide geometry.
In the original geometry, combining an assumed 0.20 mm head-edge loss,
0.15 mm catch-edge setback and 0.10 mm inward spring set reduced the minimum
sampled engagement depth from about 0.456 mm to 0.0055 mm. Adding 0.05 mm of
radial mating play removed the remaining overlap. These assumed losses explain
how nominal CAD capture could coexist with a loose print; they do not establish
which error occurred on this printer.

Revision 2 uses a 7 mm head, increases the catch's share of paddle movement and
keeps a flat underside for retention. Release travel also increases by 0.15 mm
per paddle, from 3.15 to 3.30 mm. The smaller root section and
wider outer span redistribute bending while retaining the raised finger faces
and travel stops. The new [audit report](retention_audit.json) records the
dimensional-loss sweep and geometric acceptance thresholds. It does not model
contact force, friction or the tendency of rounded surfaces to push the catch
open. The printed coupon is the next acceptance gate.

## Compact standoff trial

The current default is `standoff=4`: 4 mm from the winder's top face to the
center's underside. The allowed range is 2.5–25 mm. This setting is independent
of the wire-space preset, so both presets use the same printed winders and
32 mm bare packet height. Try `standoff=5.5` for an intermediate height or
`standoff=8` for more room. The earlier taller geometry used 8 mm supports for
the 40 m reservation and 11 mm for the 80 m reservation.

The shorter supports lower both retaining heads and alignment guides with the
center. Their dimensions relative to the seat are unchanged, preserving the
dry latch and release geometry. The smaller standoff does not shrink the
assumed coil, silicone tie, hardware or finger proxies.

**The compact setting is an experimental loaded fit.** The original reserved
coils overlap the lowered center; the schematic ties remain clear in their
planned static route. Dry mechanism success cannot establish that the actual
tied antenna fits. The lowered paddles and lifting
bridges also need another loaded grip and glove trial. Report these proxy
collisions explicitly; do not silently reduce wire buildup or tie dimensions
to obtain a passing result. The actual wire and tie routing may differ from
the proxies. Measure and test them, increasing `standoff` if the center
cannot seat freely or finger access is inadequate. The static tie result does
not establish clearance for every tie placement or throughout the release.

## Arrangement and purpose

The assembly has three separately printed pieces: one center and two identical
K6ARK-style winders. Each winder has two headed retaining studs and one smooth
alignment guide. With the BNC down and hoist eye up, pinching the right upper
and lower paddles inward releases both right studs. The matching left pair
releases both left studs. Retention comes from the four catches beneath the
head undersides; the smooth guides control alignment without providing a latch.

Each silicone tie stays captive on its winder's original upper central brace.
Close both ties around their figure-eight coils before docking. The ties retain
the wire while the catches retain the three printed parts. A whole-packet tie
is optional backup. The default winding profile and five windows are retained;
wind from the remote tip toward the center so the center end pays out first.

## Supported one-hand sequence

The intended sequence permits one hand to release the ends sequentially:

1. Support the tied winders on a surface or lap, allowing slight guide settling.
   Pinch the right upper/lower paddles with thumb and forefinger. Use another
   finger of the same hand on the fixed right lifting bridge to raise that end.
2. Clear both right heads, let the paddles return, and gently settle the closed
   tongues onto the broad flat head tops. The opposite catches remain engaged.
3. Remove the hand from the right end and transfer it to the left. The first end
   stays visibly raised on its head tops without continued paddle pressure.
4. Pinch the left pair and lift its fixed bridge until the center is level about
   the right head tops. Then lift the level center clear of both guide pins.

The sequence also works geometrically with left and right reversed. Pulling a
still-tilted center straight upward can jam at admitted offsets; level it first.
The parked position is a temporary handling support, not a transport latch.
For transport, all four tongues must return beneath their heads.

Broad flat parking tops require **pinching each pair while seating that end**.
They do not provide an automatic push-in funnel. Keep tails slack and outside
the latch and lifting corridors, and check both ends with a gentle pull.

A surface supports weight but does not restrain the winders against lifting.
Their weight or an additional contact from the same hand must provide that
reaction. The paddles actuate the catches; use fixed plastic for the lift.
The feasible first-peel path includes small continuous translation and yaw
settling within guide clearances. This does not establish automatic centering
or favorable friction. A printed assembly must perform it without another
hand, deliberate jiggling or a separate alignment step. Free-air one-hand
operation is a separate, unproved requirement.

## Dimensions that govern the mechanism

All dimensions below are millimeters unless marked otherwise.

| Feature | Current geometry |
| --- | --- |
| Storage placement | Winders offset by 26; lower winder rotated 180° about Z |
| Retaining stations | X=±36, Y=±15; 72 between ends and 30 between rows |
| Stud base / shoulder / neck | Diameters 10 / 8 / 4 |
| Winder-to-center support height | Default `standoff=4`; same printed parts for both wire-space presets |
| Retaining head | Diameter 7, outward flat 2 from axis; flat top diameter 6.8 |
| Plate and axial room | Plate 4; head underside 4.8 above seat; top 6 above seat |
| Fixed head passage | Elliptical D shape, 7.9 X × 7.6 Y; outward flat 2.35 |
| Moving neck notch | Diameter 4.4 swept X±0.8; envelope 6.0 × 4.4 |
| Flexible root | X=13; 1.50 mm beam width with 1.5 mm root fillets |
| Inward outer-span reinforcement | Up to 1.20 mm; ramps X=23..25, full width X=25..39, returns by X=41 |
| Nominal retaining overlap | 1.3; 0.95 after 0.35 retreat, before print error |
| Flat-top parking overlap | 0.85 after 0.35 retreat, before print error |
| Guide | Diameter 4, length 7 above seat; diameter 4.8 shoulder |
| Guide receiver | Diameter 4.6 middle bore; 0.4 entrance chamfer at each face |
| Outer-paddle release / stop | 3.3 / 3.5 per paddle; 6.6 paired release closure, 7.0 at the stops |
| Finger contact | Raised to 10 above center underside; resting span 33.8 |
| Fixed lifting bridges | Absolute X=48..52, Y=−8.15..8.15, height 4 |
| Default BNC opening | Diameter 10.10; D-flat to opposite edge 9.25 |
| Automatic wire face reservation | 5 per face for 40 m preset; 8 for 80 m preset |

The capsule notch accommodates articulation while preserving its inward catch
edge. The elliptical passage and chamfers allow head tilt and guide entry.
The long guides remain engaged during the first peel. The 0.8 axial room permits
articulation and may produce transport play. Geometric overlap is not a pull
strength rating; ideal parked contact begins at an edge or line, not a broad
bearing area. Both wire-space presets use the same center.

## Parameterization and fixed interfaces

The [README parameter table](../README.md#adjustable-dimensions) defines the
public settings and their coupled limits. The sizing and hole settings retain
their defaults; exported parts use revised retention and the new compact
`standoff=4` default.
`wing_length` extends the horn-tip reach in native Y from 37.5 to
60 mm; it does not measure diagonal arm length. `winding_span` increases the
lower-tip span from 140 to 200 mm. Extended horns can exceed that span, so total
width and print-layout spacing use actual profile bounds.

The profile keeps the central tie brace and docking core fixed, lengthens the
outboard arms and retains their rounded tips. Changing these public dimensions
keeps the revision-2 retaining stations, guide stations and center flexures
fixed. `wire_face_bulge=0` selects 5 or 8 mm by preset; an explicit 2–12 mm
value overrides that choice. `standoff` sets the shoulder height directly in
millimeters, independently of the displayed coil and tie assumptions. Changing
the reservation or preset does not resize the printed supports; set their
height explicitly for the actual loaded fit. Smaller heights trade clearance
for compactness. These are reserved
spaces, not measured wire capacities. Longer arms also need a printed strength
trial; preserving their local profile does not establish equivalent stiffness.

Explicit center-hole arguments replace the inherited holes before the docking
structure is joined. This permits smaller or relocated bores without leaving
old voids. Dependent checks preserve the terminal-barrel clearance, face webs
and outer edge. BNC diameter is adjustable from 9.7 to 10.2 mm while retaining
the top anti-rotation flat, panel thickness and surrounding structure.

## Flexure and hand-access screens

The tabs bend in the print plane. Their variable-section Euler–Bernoulli model
includes the root fillets, neck notch, inward reinforcement and raised paddles.
The fixed root wall ends at the modeled beam root, outside the inherited raised
BNC ribs. The section-width calculation and exported polygon use the same
reinforcement contour. The release parameter
is actual outer-paddle travel; it is not equal travel at the catch.

The model screens finger loads at X=41, 46 and 51, checking increased catch
travel at the 3.30 mm stroke and estimated peak strain below 0.9% at the
3.50 mm stop. The paired release closes 0.30 mm farther than the first print.

| Finger load X | Catch travel at 3.3 stroke | Estimated peak strain at 3.5 stop |
| --- | ---: | ---: |
| 41 | 1.727 mm | 0.887% |
| 46 | 1.698 mm | 0.846% |
| 51 | 1.678 mm | 0.818% |

This screen does not model root stress concentrations, nonlinear material
behavior, layer adhesion, creep, fatigue or out-of-plane twist from a raised
finger load. It is not a PETG force or lifetime rating.

The [hand-clearance script](hand_clearance.py) sweeps 18 mm spherical fingertips
through the proposed approach and pinch corridors. Its
[40 m](hand_clearance_40m.json) and [80 m](hand_clearance_80m.json) reports use
the current support height and unchanged wire reservations. The earlier
full-height result—approximately 3.087 mm minimum tail clearance and 2 mm
wire-reserve clearance at the raised faces—does not carry over to the compact
default. Lowering the center also lowers the finger approaches and the access
beneath its fixed bridges. The current reports record any resulting overlaps;
these are mathematical proxies, not measurements of hands or gloves. Approach
the raised faces from each outer end and test the actual loaded grip.

## Reproducible digital evidence and its limits

The [main report](../validation.json) checks raw watertight production meshes,
all nine inherited Z-axis bores, the BNC opening, individual head capture,
flexure travel and both dry release orders in both presets. It separately
reports loaded-space and fingertip results. The compact default has loaded
proxy collisions: `status=passed_with_fit_caveats` records completed dry checks,
while `loaded_fit_status=requires_physical_check` keeps the unresolved loaded
fit visible. Neither status asserts that wire and ties clear the center.
The mechanism audit samples admitted seated offsets and first-peel paths, including
bounded initial guide settling. Its parking checks look for supporting contact
at each released head top and opposite shoulder under small virtual closure.

The independent [parked audit](parked_audit.py) and its
[report](parked_audit.json) test whether admitted parked poses retain first-head
support and require the opposite pinch before leveling. They also check the
leveling and level-lift paths against a fixed numerical intersection tolerance.
The [retention audit](retention_audit.py) and [report](retention_audit.json) add
head/catch bearing-depth and area checks under explicit dimensional losses,
including independent winder movement. Reports record input hashes; their
results apply to those recorded inputs.

The separate [parameter screen](../parameter_validation.py) samples
coordinated endpoint or combined settings. It checks the requested hole sizes
and positions, restoration of material in obsolete holes, fixed interfaces,
watertight parts, seated capture, support height, wire reservations and
print-layout separation. Loaded fit must be distinguished from the dry checks.
Invalid hole-spacing and size cases must be rejected. This screen
does not repeat the full sequential-motion audit or hand-clearance sweep for
custom sizes, and it does not cover every permitted combination.

These sampled rigid-body checks establish feasible geometry, not exhaustive
motion coverage, contact strength, friction, flexible-wire behavior or easy
operation. Tie buttons, hardware and tails use specified proxy dimensions and
routes. Wire reservations do not prove actual 40 m or 80 m coil capacity.

## Physical acceptance

Print [retention_coupon.stl](../retention_coupon.stl) first. It contains the
paired receiver and two independent single-stud feet. Separate feet allow each
stud to retreat outward as an independent winder can. The joined foot in
[fit_coupon.stl](../fit_coupon.stl) fixes the row spacing and can conceal this
failure mode; use that coupon for paired-pinch ergonomics.

Check the slots are open and the head undersides have clean bearing edges.
The revised heads project 1.5 mm beyond the neck on the catch side, so their
printed underside needs particular attention. Pinch to seat one loose foot all
the way onto its shoulder, then let the tongue return beneath the head.
Holding fixed plastic with fingers clear of the tab, move the stud toward the
fixed outer wall and pull, then gently rock it. It should take up the 0.8 mm
axial gap and stop. Free withdrawal without pinching fails the test. Pinching
must then release it comfortably before the hard stop; the tongue must return
freely. Repeat with both feet and catches over at least ten cycles, checking
for rounding, whitening, cracks and paddle twist.

After that check passes, print the matched three-piece set. Test each winder
independently for retention, then test the complete pack with actual wire,
silicone ties, BNC and terminal hardware.
Check that all four shoulders seat without trapping a tie or forcing the coil
down. The 4 mm default has known proxy overlaps; if your loaded pack does not
fit, increase `standoff` and print two matching winders. Values of 8 or 11 mm
restore the earlier 40 m or 80 m support heights without changing the
revision-2 center.
Use one hand with the intended support; leave the first end parked for five
seconds before transferring to the second. Repeat starting from either end,
then repeat with field gloves. Record supported and free-air results separately.

Complete at least ten deployment/retrieval cycles as an initial ergonomic
screen, recording recatches, alignment stalls, dropped loops, tail interference
and wear. Verify actual coil depth and tie-button fit in each desired preset.
The coupons test local fit and feel. Full-winder flex, guide leverage and the
loaded release and payout sequence require the complete assembly. Ten cycles
do not establish fatigue life or cold-weather durability, and no pull-force
rating follows from the geometric overlap or elementary beam screen.
