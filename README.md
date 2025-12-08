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
