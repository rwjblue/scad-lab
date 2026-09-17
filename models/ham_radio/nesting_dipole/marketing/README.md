# Nesting Dipole flyer

One-page US Letter flyer explaining the packing/deployment tradeoff and how
the clip-free nesting carrier works. The product illustration is rendered
from the actual CAD; the walk-out diagram is a schematic. Identical winders
overlap at their spines, with the lower stud entering the upper hole and the
wire coils on opposite sides. A compact 90 mm-wide center sits crosswise.
Slots in line with its wire bar anchor a short strap around the back of the
pair. An 8 mm hoist eye gives the suspension line more room.

The single engaged stud locates the winders; the rear strap retains the
bundle. Packing illustrations use representative wire reserves and a strap
route, not a measured capacity or a guarantee of printed fit.

- [Printable PDF](../../../../output/pdf/nesting-dipole-flyer.pdf)
- [Shareable PNG](../../../../output/pdf/nesting-dipole-flyer.png)
- [Editable layout and copy](build_flyer.py)

From the repository root:

```sh
mise run nesting-dipole:flyer
```

The task needs Poppler's `pdftoppm` and uses `uv` for Python dependencies.
The layout uses macOS DIN Alternate and Arial when available, with PDF-standard
Helvetica fallbacks. The generated PDF embeds the selected TrueType fonts.

The hero is a high-resolution CAD render. To render the loaded packing view
after a model change, then rebuild the flyer:

```sh
openscad --backend=Manifold --hardwarnings --imgsize=4000,2857 \
  --camera=190,-240,240,0,0,10 --projection=o --viewall --autocenter \
  --colorscheme=Tomorrow -D 'view="loaded"' \
  -o models/ham_radio/nesting_dipole/marketing/hero.png \
  models/ham_radio/nesting_dipole/mockups.scad
mise run nesting-dipole:flyer
```

Attribution and remix terms remain in [NOTICE.md](../NOTICE.md).
