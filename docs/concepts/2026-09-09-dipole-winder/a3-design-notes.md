# A3 design decisions and measured dimensions

A3 uses the [dimensioned layout](layout-a3.png) for geometry and the [product render](concept-a3-straight-arm.png) for appearance. These are concept studies; no printable SCAD model has been created for this design.

## K6ARK angles

Both user-supplied meshes measure **140 × 54.043564 × 5 mm** and have the same retention-arm directions. The solid model is translated −66 mm in Y relative to the wireframe. The Downloads copy is byte-for-byte identical to the attached wireframe, verified by SHA-256.

| Bay-facing straight surface | Acute angle to original long spine | Sweep from perpendicular |
| --- | ---: | ---: |
| Left arm | 63.575670° | 26.424330° |
| Right arm | 63.595345° | 26.404655° |

Use a symmetric **26.414493°** sweep, displayed as **26.4°**. With the long spine vertical, upper arms rise outward at that angle above horizontal and lower arms descend outward at that angle below horizontal. Each tip splays away from the center.

These are measured mesh angles, not recovered native design parameters. Straight external surface endpoints and independent side-facet normals agree. Triangulation diagonals and the low-angle back-rail slope were excluded. See [reference figure](reference-angles.png), [numeric results and provenance](reference-angles.json), and the reproducible [analysis script](analyze_reference.py). Both STL inputs are unmodified.

## Shape and BNC position

Replace curved paddles with straight, parallel-sided arms, rounded ends, and small root fillets. Retain the open outer sides and smooth, unslotted tips.

Set **45 mm from suspension-eye center to BNC shelf top**. This explicit target moves the connector lower and reserves wiring/stud space away from the suspension cord. A2 had no dimensional baseline, so an exact 25.4 mm translation from that image cannot be established.

The main-plate proposal is 4 mm thick; the BNC shelf remains 3 mm thick with a reinforced root. The BNC mating barrel points down. Preserve the existing connector cutout and hardware-clearance approach from [dipole_center](../../../models/ham_radio/dipole_center/README.md), then verify the actual nut/tag/washer stack and coax coupling.

## Optional studs and wire holes

Each upper arm has one optional **Ø3.4 mm M3 clearance hole**, then an **18 mm center-to-center gap** to the first of three **Ø3.2 mm strain-relief bores**. Wire-hole center pitch is **5.5 mm**. Both faces get **0.5 mm × 45° chamfers**, making each chamfer mouth **Ø4.2 mm**. This transfers the relevant dipole_center spacing along the arm.

| Clearance | Calculation | Result |
| --- | --- | ---: |
| M3 bore edge to first relief chamfer | 18 − 1.7 − 2.1 | **14.2 mm** |
| Suggested 7 mm washer edge to chamfer | 18 − 3.5 − 2.1 | **12.4 mm** |
| Material between adjacent chamfer mouths | 5.5 − 4.2 | **1.3 mm** |
| Longest owned Panduit barrel entry to chamfer | 18 − 11.176 − 2.1 | **4.724 mm** |

The user's **10 mm minimum is exceeded even as an edge-to-edge clearance at the plate face**. The ring barrel and relaxed wire bend still require a physical fit check.

The stud holes can remain empty for direct soldering. Fit M3 studs and short BNC jumpers for electrical disconnect. Closed relief holes still capture an already-crimped ring terminal: full leg removal requires removing the terminal/unthreading the wire or a separately designed mechanical release.

## 26 AWG / 22 AWG fit

The repository uses **1.02 mm nominal insulated diameter** for DXE-SANTW-500, a design assumption to verify with the actual 26 AWG wire. [Davis RF's manufacturer table](https://www.davisrf.com/antenna-wire/polystealth.php) gives **0.052 in = 1.321 mm nominal insulated diameter** for 22 AWG POLYS-22. Both fit the proposed 3.2 mm bores.

Gauge alone does not determine insulation diameter; compatibility does not cover every 22 AWG jacket. The alternating three-hole weave must also be pull/flex-checked with the chosen wire: fitting through the holes does not prove grip. Leave a slack tail from the innermost hole to the electrical connection.

## Provisional layout coordinates

The [layout script](layout_a3.py) produces a front-view outline approximately **119 × 156 mm**. Units are millimetres, Y is up, and the spine is centered on X=0.

| Feature | Coordinate |
| --- | --- |
| Suspension-eye center | (0, 72) |
| BNC shelf top | y=27 |
| M3 centers | (±15, 38.450794) |
| Right inner wire-hole center | (31.120787, 46.458304) |
| Right middle wire-hole center | (36.046583, 48.905043) |
| Right outer wire-hole center | (40.972379, 51.351782) |

Mirror X for the left wire group. These dimensions are proposed, not measured from the product render. The BNC is represented by a schematic envelope in the front-view layout. Full hardware geometry, wound-wire envelopes, capacity, edge rounding and structural performance remain to be resolved during SCAD development.

## Artifacts and reproduction

- [Dimensioned layout PNG](layout-a3.png) and [editable SVG](layout-a3.svg).
- [Source-angle figure PNG](reference-angles.png) and [SVG](reference-angles.svg).
- [Image-generation prompts](prompt-a3.md), using the built-in image-generation tool.
- [Source angle analysis](analyze_reference.py) accepts the two supplied STL paths; see its help.
- Regenerate the proposed layout with: `uv run --with matplotlib --with shapely --with numpy python layout_a3.py`.

The source geometry is Adam Kimmerly/K6ARK's [UL wireframe winder](https://www.printables.com/model/383037-k6ark-wire-antenna-winder-ul-wireframe-model) and the solid counterpart supplied by the user. Source meshes retain their original terms; they were analyzed without modification.
