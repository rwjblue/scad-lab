# scad-lab

A grab bag of my OpenSCAD designs: brackets, spacers, ham radio widgets,
battery trays, and whatever else I need to print.

## Layout

- `lib/` – shared OpenSCAD modules (fillets, fasteners, helpers)
- `models/` – individual models, each in its own folder
- `scripts/` – helper scripts (batch rendering, etc.)

## Usage

Open any `.scad` file in `models/` with OpenSCAD, tweak the parameters at
the top, then:

1. Render (F6) in OpenSCAD  
2. Export as STL  
3. Slice in Bambu Studio (or your slicer of choice)  
4. Print

You can also use the `openscad` CLI and the scripts in `scripts/` to
batch-generate STLs if desired.

## Models in this repo

- `models/ham_radio/dx_commander_element_label/` - element label tags
- `models/ham_radio/dx_commander_hitch_base_puck/` - soft bottom puck for
  protecting a DX Commander Expedition mast base in a hitch-mounted holder
- `models/ham_radio/dx_commander_hitch_sleeve/` - sleeve adapter for a
  DX Commander Expedition mast in a hitch-mounted flag pole holder
- `models/ham_radio/ft140_current_balun_holder/` - lightweight radio-end
  FT-140 toroid enclosure with dual right-angle BNCs and opposing M5 terminals
- `models/ham_radio/lightweight_balanced_feedline/` - parameterized snap-on
  feedline spacers plus continuous-wire and terminalized doublet centers
- `models/ham_radio/spooltenna_bnc_cap/` - BNC connector protector for
  the KO4HUI Spooltenna (Ultra v1.5/v1.6 + V1.3)
- `models/ham_radio/vertical_dipole_spacer/` - 6 m vertical dipole center
- `models/luggage_tag/` - customizable QR luggage tag
- `models/mechanical/spacer_m3/` - configurable M3 spacer
