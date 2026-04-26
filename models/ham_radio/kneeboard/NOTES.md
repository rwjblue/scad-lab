# Ham Radio Kneeboard Reverse Engineering Notes

## Assembly

The model set appears to be a foldable ham radio kneeboard made from two
rounded rectangular plates joined by separate hinge knuckles. The top plate has
bungee retention paths. The bottom plate provides a larger writing or equipment
surface with repeated elastic cord holes and side slots. The magnetic mod adds a
steel-plate recess to the bottom plate so a magnetic Morse key can be attached.

The printed photos show elastic cord routed through the edge holes and slots,
with the hinge along the shared long edge. The modified bottom plate places a
black metal insert near one lower corner when the board is open.

The PDF describes the board as 200 x 140 mm closed and 200 x 280 mm open. It
calls for 3 mm shock cord, up to 4 mm shock-cord holes, 1 to 1.5 inch elastic
leg straps, a 1/16 inch hinge rod, and a 4 x 5 inch silicone non-slip pad. This
remix currently omits the large top pad recess.

## Component Identification

- `files/kneeboard_bottom_plate.stl`: original lower plate, approximately
  200 x 139.7 x 6 mm.
- `KFH_KneeBoardMod_BottomPlate.stl`: same lower plate plus a shallow rounded
  rectangular pocket for a flush steel plate.
- `files/kneeboard_top_plate_v2.stl`: upper plate, approximately
  200 x 139.7 x 6 mm, with a recessed pad/tray area and bungee routing. This
  remix keeps the bungee routing but fills in the large pad/tray recess.
- `files/kneeboard_hinge.stl`: individual hinge knuckle.
- `files/kneeboard_hinge_with_flange.stl`: hinge knuckle variant with an
  additional lower flange.

The original print list is one top plate, one bottom plate, two regular hinge
pieces, and three hinge-with-flange pieces.

Both plates have a comb-like hinge edge. The repeated hinge fingers and gaps are
about 18.18 mm wide and 6.3 mm deep. This remix starts and ends the hinge edge
with printed teeth so the outer left and right edges are supported. The
hinge-facing corners are intentionally square rather than rounded, while the
non-hinge outside corners remain rounded. The separate hinge pieces sit in the
gaps between teeth and are pinned with 1/16 inch rods. The OpenSCAD hinge blocks
include the rod bores, and the plate teeth include matching bore cuts.

The OpenSCAD coordinate layout intentionally puts the bottom plate hinge edge at
the top of the bottom plate and the top plate hinge edge at the bottom of the
top plate. In `assembly` mode, those two hinge edges face each other with a
small inspection gap. The separate hinge blocks are rendered with
`render_part = "hinge"` or `render_part = "hinge_flange"`.

## Bottom Plate Difference

The original and magnetic-mod bottom plates share the same bounding box:

- X: 200 mm
- Y: 139.7 mm
- Z: 6 mm

The magnetic STL adds a recessed pocket only:

- Local center from lower-left plate corner: approximately `[34.23, 104.98]`
- Pocket size: approximately `45.45 x 65.45 mm`
- Pocket depth: approximately `0.75 mm`
- Pocket top plane: `z = 5.25 mm` on a `6 mm` plate

This is modeled by default in `bottom_plate()`. Use
`bottom_plate(enable_magnetic_inset = false)` or set
`enable_magnetic_plate_inset = false` to render the original bottom plate.

## Print Orientation

The plate STLs are oriented flat on the build plate with the broad face down and
the feature side upward. Hinges are likely printed flat in their STL orientation.

## Assumptions and Uncertainties

- Rounded plate corners are estimated as 14 mm radius.
- The top pad recess is simplified from mesh boundaries and photos.
- Shallow top-plate cord channels are modeled as grooves, not through-slots,
  so cordage can remain installed when the board closes. The top side holes are
  aligned with these grooves and with the bottom plate's strap/cord line.
- Hinge geometry is simplified as a rectangular knuckle with a longitudinal
  1/16 inch rod bore plus clearance.
