# Source attribution

The leg-winder outline derives from **K6ARK Wire Antenna Winder — UL Wireframe
Model** by **Adam Kimmerly (K6ARK)**,
[Printables model 383037](https://www.printables.com/model/383037-k6ark-wire-antenna-winder-ul-wireframe-model).

The user-supplied `K6ARK_Wire_Winder.stl` (also named
`newWinder_wireframe.stl`) has SHA-256:

`d023e8ecb8b5e7718d9f2c8431a90b2c823550a700396df8e0421103dbf5ad0d`

At the default `wing_length=37.5` and `winding_span=140`, this remix preserves
the original **one-sided** outer winding outline at 1:1 scale. It shifts the
X origin by −62.5 mm, extrudes the projected silhouette to 5 mm, and bevels its
broad-face edges by 0.5 mm. The two original spine stations at
X = ±36 mm, Y = −11 mm have 12 × 10 mm pads. One carries
an unheaded 6 mm stud with a 0.6 mm rounded root; the other contains a
matching round socket. The stud rises 8 mm above the frame. The central
tie window is retained. There are no retaining catches.
This remix does not reproduce the source STL's fully rounded cross section.

The embedded [native_profile.scad](native_profile.scad) and adjustable
[winder_profile.scad](winder_profile.scad) are independent snapshots from
[Modular dipole](../modular_dipole/README.md), taken on 10 September 2026.
Optional larger settings extend the swept arms and widen the outboard frame,
retaining the original mating stations, tie opening, and rounded tip profiles.
These custom settings modify the original horns and winding bay. The profile
extraction's provenance remains recorded in the modular model's
[generator](../modular_dipole/generate_native_profile.py); native coordinates
are not hand-edited. Nesting dipole does not import its clip mechanism.

The prior [source notice](../dipole_winder/NOTICE.md) records verification on
9 September 2026 that the original Printables listing links to **Creative
Commons Attribution–NonCommercial–ShareAlike 4.0 International**. This remix
retains those attribution, noncommercial, and share-alike terms. No endorsement
by the original author is implied.

The SCAD, derived STL, generated profile, and renders of the remix retain those
source terms. New mechanical arrangement by Robert Jackson (N1RWJ), September
2026: two identical leg winders overlap at their spines after one is turned
180 degrees in the frame plane. Both studs point in the same direction;
the lower stud enters the upper hole and the upper stud remains unused.
Their winding regions extend in opposite directions. A separate 90 mm-wide
center sits crosswise, with strap slots in line with the terminal and wire
holes. Its enlarged 8 mm hoist eye and inward-shifted terminal and wire-hole
groups retain the original functions; their coordinates and sizes are revised.
Symmetric end sections support the slots for a short strap around the back.
The stud locates the winders but allows pivoting; the rear strap retains the
bundle. Individual ties retain each wire coil. Packing views use conservative
wire reserves and an illustrative strap route; physical fit remains a
prototype trial.
This arrangement replaces the earlier four-post center carrier in the same model.

The design reuses helpers from the existing
[dipole center](../dipole_center/dipole_center.scad) and
[frame bevel](../dipole_winder/frame_bevel.scad). The BNC shelf, ribs and
shelf-root reinforcement are unchanged. The original center is
licensed by Robert Jackson (N1RWJ) under
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/), as recorded
in its source and README. Manufacturer connector drawings retain their own terms.
