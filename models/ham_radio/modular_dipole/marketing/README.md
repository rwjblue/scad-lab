# Modular dipole flyer

[Download the one-page PDF](../../../../output/pdf/modular-dipole-flyer.pdf).

The flyer explains the separate-winder packing and walk-out deployment idea.
It uses the current [assembled CAD render](../images/assembled.png), a schematic
deployment diagram and a short prototype-status note. For printing, release
instructions and fit checks, use the [model guide](../README.md).

Rebuild from the repository root with Python and ReportLab:

```sh
uv run --no-project --with reportlab python models/ham_radio/modular_dipole/marketing/flyer.py
```

The [source](flyer.py) writes `output/pdf/modular-dipole-flyer.pdf`. Regenerate
the model illustrations with `mise run modular-dipole:render` first if the
geometry changed. The PDF uses Avenir Next when available, with Helvetica as
the fallback. Source attribution and remix terms are in [NOTICE.md](../NOTICE.md).

## Printables

The [Printables listing](https://www.printables.com/model/1838498/edit) remains
an unpublished draft. [printables.html](printables.html) is the description
source, using the same hardware, printing and assembly format as the other
N1RWJ listings. The draft includes five current STLs, four CAD illustrations,
the flyer and `modular-dipole-editable-source.zip`. Rebuild the source archive
with `mise run modular-dipole:package` before replacing that download.
