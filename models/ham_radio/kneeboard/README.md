# Ham Radio Kneeboard

This is my OpenSCAD remix of a folding ham radio kneeboard for portable
operating. It is meant to be easy to tweak, reprint, and adapt instead of being
a one-off STL-only model.

The board folds to about 200 x 140 mm and opens to about 200 x 280 mm. It has
slots for an elastic leg strap and holes/grooves for shock cord to hold radios,
paddles, batteries, tuners, or a notebook.

This version defaults to the magnetic bottom plate remix, with a shallow recess
for a steel plate so a magnetic Morse key can sit on the board.

## Attribution

This is a remix based on these designs:

- "Ham Radio Kneeboard" by KYFriedHam  
  https://www.printables.com/model/874685-ham-radio-kneeboard
- "Ham Radio Kneeboard Magnetic Mod" by Jason T  
  https://www.printables.com/model/1168939-ham-radio-kneeboard-magnetic-mod

The OpenSCAD here is a new parametric version made from the published STL files,
photos, and PDF notes. It is not the original source model.

## Parts

The main assembly uses:

- 1 top plate
- 1 bottom plate
- 2 hinge pieces
- 3 hinge-with-flange pieces
- 1/16 inch metal rod for the hinge pin
- 3 mm shock cord
- 1 to 1.5 inch elastic strap for attaching the board to your leg

The OpenSCAD assembly preview lays the two plates open with their hinge edges
facing each other with a small inspection gap. It does not render the separate
hinge blocks between the plates, so the preview stays readable. The bottom plate
keeps through-slots for the leg strap. The top plate uses shallow cord grooves
instead of through-slots so shock cord can stay installed while the board closes
flat. Those grooves run nearly the full usable height and width of the top plate
while leaving material near the edges. The top plate also has half-depth relief
slots aligned with the bottom leg-strap slots so the wider elastic straps can
stay installed when the board is folded. The left and right side recesses open
to the outside edge; the horizontal top and hinge-side grooves remain inset.

## Rendering

Open `model.scad` in OpenSCAD and set `render_part` near the top:

- `"bottom"`: bottom plate using the current default settings
- `"bottom_original"`: bottom plate without the magnetic recess
- `"bottom_magnetic"`: explicit magnetic bottom plate
- `"top"`: top plate
- `"hinge"`: plain hinge piece
- `"hinge_flange"`: hinge piece with flange
- `"assembly"`: laid-out preview

Render with F6, then export STL for the selected part.

## Magnetic Recess

The magnetic recess is enabled by default. To print the original-style bottom
plate without the steel-plate pocket, set:

```openscad
enable_magnetic_plate_inset = false;
```

Useful parameters:

- `metal_plate_length`
- `metal_plate_width`
- `metal_plate_depth`
- `metal_plate_offset_x`
- `metal_plate_offset_y`
- `metal_plate_corner_radius`

The current recess is about 45.45 x 65.45 mm and 0.75 mm deep, based on the
magnetic mod STL.

## Current Accuracy

The bottom plate is the most complete part. Its overall size, hole layout, side
slots, magnetic recess, and hinge-edge fingers are based on direct STL
measurements.

The top plate and hinge pieces are usable first-pass parametric versions. The
main dimensions and hinge-edge fingers are measured, but some details are
simplified: rounded edges, shallow cord grooves, and hinge profiles are not
exact copies. The original large top pad/tray recess is intentionally omitted.

## Measurements To Improve Later

- Real steel plate length, width, thickness, and desired clearance
- Exact plate corner radius
- Exact side-slot radius, strap-slot dimensions, and top relief/groove clearance
- Hinge bore clearance around the two 1/16 inch rods
- Hinge spacing in the assembled board
