# Nesting dipole

Two separate leg winders pack together at their spines, with their wire
bundles on opposite sides. Print **two identical winders and one center**.
Each winder has one stud and one hole at the original spine stations. A
compact crosswise center has strap slots in line with its wire bar. A short
strap through those slots holds the bundle together around the back.

This replaces the earlier four-post center arrangement in the same model.
It remains independent of [Modular dipole](../modular_dipole/README.md) and its
retaining clips. The editable source is [nesting_dipole.scad](nesting_dipole.scad).
The winding profile is an independent snapshot; the original dipole center
and frame bevel remain shared helpers.

![One 6 mm stud and one hole at the original two spine stations](images/winder.png)

The [one-page flyer](marketing/README.md) explains the packing and deployment
idea with a product illustration and a simple walk-out diagram.

## How the pieces meet

The original station centers stay at **X = ±36 mm, Y = −11 mm**. The
**6 mm stud** remains at X = +36 mm; the station at X = −36 mm becomes a
**6.5 mm round hole** at the default clearance. There is no new central tongue.
Both stations retain the earlier 12 × 10 mm pads and their 72 mm spacing.

Keep both winders' studs pointing up. Turn one winder 180 degrees in the
plane of the frame, then place its spine over the other spine. Their winding
regions extend in opposite directions. The **lower stud enters the upper
winder's hole**; the upper stud remains exposed and unused. The overlapping
spines contact directly, without a standoff.

The single engaged stud locates the pair but allows it to pivot. The rear
strap supplies retention and holds the center in its packing position.

![Direct connection at the original stud stations](images/joint.png)

Each stud rises **8 mm above its 5 mm frame**, 1 mm taller than the earlier
7 mm stud. The engaged stud passes through the upper frame and projects
**3 mm beyond it**. Its rounded root and tip chamfer are both 0.6 mm.
The receiving hole has 0.6 mm relief at its printed top face and a 0.4 mm
entry chamfer at its printed bottom face.

The center measures **90 × 39 × 23 mm**. Its **8 mm hoist eye** gives more
room for suspension clips. The strap slots sit in line with the terminal
and wire holes, so the strap pulls through the center bar. Each end widens
symmetrically around its slot while staying within the 90 mm overall width.

All nine functional plate holes remain, with a revised layout: the two M3
terminal centers move to **X = ±7 mm**, and the three wire holes on each side
move to **X = ±25, ±30.5 and ±36 mm**. Moving both groups inward together
preserves the 18 mm terminal-to-inner-hole spacing and 4.724 mm of wire-entry
space at the maximum specified ring-terminal length, as described in the
[dipole center guide](../dipole_center/README.md).
The BNC shelf, ribs and shelf-root reinforcement are unchanged. There are no
center docking holes.

![Inline strap slots, relocated wire and terminal holes, and larger hoist eye](images/center.png)

The packing views put the center crosswise above the wire, with 2 mm reserved
for the strap to turn beneath it. Its illustrated plate height is 17 mm for
the 40m reserve or 20 mm for the 80m reserve. These are packing positions,
not printed standoffs. The actual center can tilt as the strap settles against
the wound coils.

Use the matching one-stud/one-hole winders; the earlier two-stud winders
cannot make this joint. This revision changes the center and packing
arrangement while retaining the current winder geometry.

![Side view of the separate coils, rear strap and crosswise center](images/side.png)

## The short rear strap

The center bar ends have **14 × 3 mm slots**, intended for roughly **12.7 mm
(half-inch) wide hook-and-loop strap up to 2 mm thick**. Choose end closures
or hook patches that engage the strap body when folded back. Check the
actual strip before cutting; a fold alone does not close every tape style.
A silicone tie can also be tried if its body, ends and closure fit the slots.

Thread one end through each center slot. Beneath the center, run the strap
outward over the coils before turning it down around the back of both
winders. Fold the ends back and fasten them at the slots. The strap makes an
open U: it does **not** cross the front of the center or make a full lap
around the bundle. Trim it after trying the actual wound coils, leaving
enough material for both end closures.

The route reserves room for a 12.7 × 2 mm strip but does not set its cut
length or closure overlap. Individual coil ties retain each leg's wound wire;
the rear strap holds the separate center and winders together.

At the default dimensions, each slot retains 2.5 mm of material to the outer
edge, 3 mm at its ends and a 1.4 mm web to the nearest wire-hole chamfer. The
enlarged hoist eye retains a 2.5 mm wall around its chamfered mouth.

![Short rear strap with its ends passing through the center bar](images/back.png)

## Print and use

Start with [fit_coupon.stl](fit_coupon.stl). It contains two identical
strips with the full **72 mm station spacing**, stud, hole, rounded root,
face bevel and socket relief of the winders. Print both flat, turn one
180 degrees in plane, and stack them with both studs pointing up. Check that
the single engaged joint seats fully and separates without force. Start with
the default **0.25 mm clearance per side**; the 0.15 mm setting can interfere
at the rounded root and is not recommended. Try lateral loading on the
coupon before printing the winders; CAD checks establish geometry, not
printed strength.

Print the broad backs of the center and both winders flat on the bed. The
supplied layouts use this orientation. Test the bare winders first, with the
upper winder's back against the lower winder's printed top. To separate them,
lift the upper winder a little more than 8 mm off the lower stud.

The intended packing sequence is to wind each leg independently, join the
winders, place the center crosswise with relaxed wire tails, and connect the
short rear strap through its end slots. Check the assembled bundle with the
actual wire and ties before relying on it for a trip.
For deployment, release the strap, lift away the center, separate the winders,
and walk out each leg from the mast before hoisting the center.

![Exploded assembly](images/exploded.png)

| File | Print quantity / purpose |
| --- | --- |
| [center.stl](center.stl) | One crosswise center with end strap slots |
| [winder.stl](winder.stl) | Two identical winders, each with one stud and one socket |
| [winder_80m.stl](winder_80m.stl) | Same geometry as `winder.stl`; retained filename |
| [print_layout.stl](print_layout.stl) | Complete three-piece layout |
| [print_layout_80m.stl](print_layout_80m.stl) | Same geometry as `print_layout.stl`; retained filename |
| [fit_coupon.stl](fit_coupon.stl) | Two matching strips at the original station spacing |

![Separated print layout](images/print_layout.png)

## Parameters

Open the SCAD file in OpenSCAD's Customizer. Dimensions are millimeters.

| Parameter | Default | Meaning / range |
| --- | --- | --- |
| `part` | `print_layout` | `center`, `winder`, `assembled`, `winders`, `print_layout`, `exploded`, `fit_coupon`, `wire_envelopes` |
| `preset` | `40m` | `40m` or `80m`; selects displayed coil buildup |
| `show_wire` | `false` | Show reserved coil space in assembly previews |
| `wing_length` | 37.5 | Native datum to horn-tip Y; 37.5–60 |
| `winding_span` | 140 | Lower outer-tip spacing; 140–200 |
| `post_protrusion` | 3 | Stud length beyond the other winder's frame; 2–5 |
| `alignment_clearance` | 0.25 | Clearance per side of the stud; 0.15–0.40 |
| `strap_slot_width` | 14 | Clear slot length for strap width; 10–20 |
| `strap_slot_thickness` | 3 | Clear slot width for strap thickness; 2–4 |
| `wire_face_bulge` | 0 | Auto 5/8 by preset; otherwise 2–12 per face |
| `wire_edge_bulge` | 5 | Reserved wire overhang around the winding region; 2–5 |
| `wire_hole_inner_x` | 25 | Centerline to first strain-relief hole; 24–30 |
| `wire_hole_pitch` | 5.5 | Pitch within each three-hole group; 4–6.5 |
| `wire_hole_d` | 3.2 | Strain-relief bore; 2.6–3.6 |
| `wire_chamfer` | 0.5 | Wire-hole and hoist-eye entry chamfer; 0–0.6 |
| `terminal_hole_x` | 7 | Centerline to each M3 terminal; 7–10 |
| `terminal_hole_d` | 3.4 | M3 clearance bore; 3.1–3.6 |
| `hang_hole_d` | 8 | Hoist-eye bore; 6–8 |
| `bnc_hole_d` | 10.1 | Finished BNC cutout diameter; 9.7–10.2 |

Stud height above the frame is `5 + post_protrusion`. The old
`alignment_slot_extra` parameter is removed: both winders use the same round
socket. Hole spacing and chamfers have combined material and terminal
clearance guards, so not every combination of individually allowed values fits.

Both wire-space presets produce the same printed parts with otherwise equal
settings. They reserve 5 mm or 8 mm of coil buildup per face; they do not
establish wire capacity. The reserves extend to opposite sides of the joined
spines; check the actual wound coils and ties against the packing views.

Longer wings and wider spans preserve the original mating stations and enlarge
the print footprint. Extended horns can project beyond `winding_span`. The
center keeps its compact 90 mm width at the default settings.

## Regenerate and inspect

Run from the repository root:

```sh
mise run nesting-dipole:check
mise run nesting-dipole:render
```

The [CAD validation report](validation.json) separates bare-part checks from
loaded-fit observations. It checks watertight parts, the single engaged stud,
face contact, straight lift separation, the revised center hole layout,
unchanged BNC mounting geometry, strap-slot walls, coupon interfaces and
matching print layouts. It also checks
the conservative wire reserves and schematic hardware and strap routes.

The [paired coupon preview](images/fit_coupon.png) shows the fit-test pieces.
Bare assembly views omit wire. The [loaded view](images/loaded.png) and rear
view illustrate the separate coils and short strap path. Printed fit,
strength, loaded wire clearance and comfort in the hand still need prototype
trials.

Source attribution and remix terms are in [NOTICE.md](NOTICE.md).
