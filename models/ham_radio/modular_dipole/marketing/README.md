# Modular dipole flyer

[View the gallery image](../../../../output/pdf/modular-dipole-flyer.png) or
[download the one-page PDF](../../../../output/pdf/modular-dipole-flyer.pdf).

The flyer explains the separate-winder packing and walk-out deployment idea.
It uses the current [assembled CAD render](../images/assembled.png), a schematic
deployment diagram and a short prototype-status note. For printing, release
instructions and fit checks, use the [model guide](../README.md).

Rebuild from the repository root with Python and ReportLab:

```sh
uv run --no-project --with reportlab python models/ham_radio/modular_dipole/marketing/flyer.py
pdftoppm -r 200 -singlefile -png output/pdf/modular-dipole-flyer.pdf output/pdf/modular-dipole-flyer
```

The [source](flyer.py) writes `output/pdf/modular-dipole-flyer.pdf`. Regenerate
the model illustrations with `mise run modular-dipole:render` first if the
geometry changed. The PDF uses Avenir Next when available, with Helvetica as
the fallback. Source attribution and remix terms are in [NOTICE.md](../NOTICE.md).

## Printables

The [Printables listing](https://www.printables.com/model/1838498/edit) remains
an unpublished draft. [printables.html](printables.html) is the description
source, using the same hardware, printing and assembly format as the other
N1RWJ listings. The draft includes the three assembly STLs, five directly
downloadable SCAD files, `NOTICE.txt`, four CAD illustrations, and the flyer
as both a gallery image and PDF. Fit coupons remain in the repository's build
notes. Run `mise run modular-dipole:package` to prepare the direct-upload SCAD
files under `output/printables/modular-dipole/`; save all five together and
open `modular_dipole.scad`. The upload copies use same-folder helper paths.
