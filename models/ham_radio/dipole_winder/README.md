# Mirrored dipole winder

A direct-solder dipole center and two-sided wire winder based on the accepted
[A5 layout](../../../docs/concepts/2026-09-09-dipole-winder/layout-a5.png).
The native K6ARK horn positions and dimensions are retained, with a compact
perpendicular shelf for the Amphenol RF **31-221-RFX** BNC bulkhead connector.
Each antenna leg has three chamfered strain-relief holes; there are no M3 studs.

**Print file:** [dipole_winder.stl](dipole_winder.stl).
**Editable model:** [dipole_winder.scad](dipole_winder.scad), with the adjacent
[embedded profile](reference_profile.scad). No downloaded STL or Python runtime
is needed to open and render the SCAD project.

![Rendered printable winder](preview.png)

The [front view](front.png) shows the retained winding outline. The exported
STL passed the geometry checks below: one watertight solid, 75 × 140 × 24 mm.

## Dimensions and fit

| Feature | Default |
| --- | ---: |
| Overall width × height × depth | 75 × 140 × 24 mm |
| Frame thickness | 5 mm |
| Upper/lower horn sweep | Original approximately 26.4° |
| Suspension eye | Ø6 mm, center at Y63 |
| Wire holes | Three Ø3.2 mm per upper arm, 7 mm pitch |
| Wire-hole chamfers | 0.5 mm × 45°, both faces |
| Web between chamfer mouths | 2.8 mm |
| Shelf width × thickness | 26 × 3 mm |
| BNC cutout | D-shaped, Ø9.90 mm, flat-to-opposite edge 9.05 mm |
| BNC axis distance from frame front | 10 mm |
| Shelf top Y | 43.05 mm |
| Estimated rear contact Y | 55.05 mm, level with inner relief |

The BNC cutout has 0.10 mm allowance per side relative to the manufacturer’s
9.70 / 8.85 mm D-hole. The shelf is 3 mm thick, within the drawing’s 3.30 mm
panel limit. The flat faces upward during printing, with a roughly 5.55 mm
bridge and 4.9 mm of material above it.

The **12 mm rear projection remains an estimate**, not an explicitly dimensioned
value in the [Amphenol drawing](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/8637/031_221_rfx_customer_drawing.pdf).
If the assembled connector projects differently, set `bnc_rear_projection` to
the measured distance above the panel; the shelf moves to maintain contact
alignment while the horns stay fixed. `bnc_axis_from_frame` can increase the
depth if the actual plug or mounting stack needs more room.

The reserved Ø18 mm mounting-hardware envelope has 1 mm clearance to the frame.
The Ø12.7 mm barrel has 3.65 mm clearance. Two side ribs and a small trimmed heel
reinforce the shelf while preserving this envelope. Their footprint is clipped
to the frame so the heel does not start in midair beside the narrow spine.
The 26 mm shelf itself is slightly wider than the spine at its root, as in A5;
its base starts on the print bed and stays within the overall winding dimensions.
The complete connector/tag/coax fit has not been physically checked.

The Ø3.2 holes accommodate the planned 26 AWG wire and the thin-jacketed 22 AWG
examples documented during the concept work. Insulated diameter and grip vary
with wire construction; check the actual wire rather than AWG alone.

## Printing and assembly

The STL is already oriented with its **broad back flat at Z=0** and the BNC shelf
standing upright. Import it in millimetres at 100% scale. Supports are not
intended; inspect the D-hole bridge in the slicer. As a starting profile, the
dipole-center notes suggest PETG, 0.20 mm layers, five perimeters, and 100% infill;
these are starting settings, and this winder has not yet been printed or load-tested.

An optional upright fit coupon is available with `part="coupon"`. It has the
same panel thickness and print orientation, with labeled 9.7, 9.9, and 10.1 mm
D-holes. Use the same material/profile to choose `bnc_clearance`. Adjust that
parameter rather than scaling the winder. `part="frame"` displays the frame
alone. `show_hardware=true` adds a schematic connector in F5 preview only and
never exports metal hardware into the STL.

1. Remove printing burrs, especially at the winding edges and chamfered holes.
2. Dry-fit the BNC with its barrel pointing down in service and rear contact
   toward the hanging eye. Point the shell solder tag away from the frame.
   Check nut access and fit with the actual coax plug before tightening.
3. Before soldering, weave each antenna leg through its three holes from outside
   inward: back-to-front, front-to-back, then back-to-front.
4. Leave a relaxed insulated tail from each inner hole to the center cup or shell
   solder tag. Arrange the weave to take antenna tension while the solder joints
   retain slack; verify this with the pull/flex check below.
5. Pull/flex-check the relief, check center-to-one-leg and shell-to-other-leg
   continuity, and check for a center-to-shell short before use. Check winding
   clearance with the intended wire length and the actual connector fitted.

The frame stores two antenna legs. Fully deploy them for use; stored turns are
not a validated band-selection arrangement. This model contains no balun/choke.

## Export and verification

Run from this directory with OpenSCAD on PATH:

```sh
openscad --hardwarnings --export-format binstl -o dipole_winder.stl dipole_winder.scad
openscad --hardwarnings --export-format binstl -D 'part="coupon"' -o BNC_upright_fit_test.stl dipole_winder.scad
```

The main binary STL is checked in alongside the source so it can be downloaded
directly. Other generated STL variants follow the repository’s usual ignore rule.

[validate.py](validate.py) inspects exported mesh sections and compares the
frame with the accepted A5 geometry. It checks manifoldness, connectedness,
dimensions, open holes, both chamfer faces, the D-cutout and reinforcement
clearance. The saved results are in [validation.json](validation.json).
See the script’s docstring for its `uv` command and optional original-source check.

## Reference geometry and provenance

The silhouette is rotated and mirrored at scale 1, with upper openings filled
for the new holes. The 11 real lower/central windows remain, including the small
ones formed where the mirrored source overlaps. Only six floating-point
microholes were removed. Profile cleanup changes the external boundary by less
than 0.000003 mm. This is a 5 mm extrusion of the measured outline, not a copy
of the original rounded cross-section.

[generate_reference_profile.py](generate_reference_profile.py) can regenerate
the embedded polygon from the unmodified source STL:

```sh
uv run --no-project --with shapely python generate_reference_profile.py /path/to/newWinder_wireframe.stl
```

Source identity is checked by SHA-256. The actual model remains portable because
the resulting polygon is checked in. The original winder is by **Adam Kimmerly
(K6ARK)**; see [NOTICE.md](NOTICE.md) for attribution and upstream terms.
