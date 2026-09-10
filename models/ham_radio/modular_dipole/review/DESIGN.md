# Modular dipole design review

The four-catch design is accepted for printing and physical prototype trials.
Digital checks support its capture, parked support and sequential exit path.
Comfortable one-hand operation, glove access, wire capacity and durability
remain physical test gates. The editable model is
[modular_dipole.scad](../modular_dipole.scad).

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
is optional backup. The original winding profile and five windows are retained;
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
| Retaining head | Diameter 6, outward flat 2 from axis; flat top diameter 5.8 |
| Plate and axial room | Plate 4; head underside 4.8 above seat; top 6 above seat |
| Fixed head passage | Elliptical D shape, 6.9 X × 6.6 Y; outward flat 2.35 |
| Moving neck notch | Diameter 4.4 swept X±0.4; envelope 5.2 × 4.4 |
| Nominal retaining overlap | 0.8; 0.45 after 0.35 retreat, before print error |
| Guide | Diameter 4, length 7 above seat; diameter 4.8 shoulder |
| Guide receiver | Diameter 4.6 middle bore; 0.4 entrance chamfer at each face |
| Outer-paddle release / stop | 3.15 / 3.4 per paddle; 6.3 paired closure |
| Finger contact | Raised to 10 above center underside; resting span 33.8 |
| Fixed lifting bridges | Absolute X=48..52, Y=−8.2..8.2, height 4 |
| BNC opening | Diameter 10.10; D-flat to opposite edge 9.25 |
| Wire face reservation | 5 per face for 40 m preset; 8 for 80 m preset |

The capsule notch accommodates articulation while preserving its inward catch
edge. The elliptical passage and chamfers allow head tilt and guide entry.
The long guides remain engaged during the first peel. The 0.8 axial room permits
articulation and may produce transport play. Geometric overlap is not a pull
strength rating; ideal parked contact begins at an edge or line, not a broad
bearing area. Both wire-space presets use the same center.

## Flexure and hand-access screens

The tabs bend in the print plane. Their variable-section Euler–Bernoulli model
includes the root fillets, neck notch and raised paddles. The release parameter
is actual outer-paddle travel; it is not equal travel at the catch.

| Finger load X | Catch travel at 3.15 stroke | Estimated peak strain at 3.4 stop |
| --- | ---: | ---: |
| 41 | 1.363 mm | 0.750% |
| 46 | 1.282 mm | 0.669% |
| 51 | 1.234 mm | 0.621% |

This screen does not model root stress concentrations, nonlinear material
behavior, layer adhesion, creep, fatigue or out-of-plane twist from a raised
finger load. It is not a PETG force or lifetime rating.

The [hand-clearance script](hand_clearance.py) sweeps 18 mm spherical fingertips
through the proposed approach and pinch corridors. Its
[40 m](hand_clearance_40m.json) and [80 m](hand_clearance_80m.json) reports show
approximately 3.087 mm minimum tail clearance and 2 mm wire-reserve clearance
when contacting the raised faces near 8 mm above the center underside. These
are mathematical proxies, not measurements of hands or gloves. A low pinch
intersects the wire reservation; approach the raised faces from each outer end.

## Reproducible digital evidence and its limits

The [main report](../validation.json) checks raw watertight production meshes,
all nine inherited Z-axis bores, the BNC opening, individual head capture,
flexure travel, loaded-space reservations and both release orders in both
presets. Twenty-four admitted seated poses per winder are checked through 113
first-peel states per order, including bounded initial guide settling. The
nominal path finds parked contact near 4.65172° and verifies increasing contact
at each released head top and opposite shoulder under small virtual closure.

The independent [parked audit](parked_audit.py) and its
[report](parked_audit.json) sample 824 candidate configurations, admitting 264.
Every admitted pose retains first-head support and requires the opposite pinch
before leveling. The leveling and level-lift paths have at most approximately
0.000652 mm³ numerical intersection, below the fixed 0.001 mm³ tolerance.
Reports record their input hashes; the results apply to those recorded inputs.

These sampled rigid-body checks establish feasible geometry, not exhaustive
motion coverage, contact strength, friction, flexible-wire behavior or easy
operation. Tie buttons, hardware and tails use specified proxy dimensions and
routes. Wire reservations do not prove actual 40 m or 80 m coil capacity.

## Physical acceptance

Check printed head undersides, open slots, positive retention, release before
the stops, free return and any whitening, cracking or paddle twist. Then test
the complete pack with actual wire, silicone ties, BNC and terminal hardware.
Use one hand with the intended support; leave the first end parked for five
seconds before transferring to the second. Repeat starting from either end,
then repeat with field gloves. Record supported and free-air results separately.

Complete at least ten deployment/retrieval cycles as an initial ergonomic
screen, recording recatches, alignment stalls, dropped loops, tail interference
and wear. Verify actual coil depth and tie-button fit in each desired preset.
The local paired coupon tests latch fit and feel; only the loaded three-piece
assembly can establish the full release and payout sequence. Ten cycles do
not establish fatigue life or cold-weather durability.
