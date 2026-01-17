# Luggage Tag

This model supports a simple personal-info flow without committing private data.

## Quick Start

1. Generate a local wrapper file with your info:

```
scripts/generate_luggage_tag.sh --first "Ada" --last "Lovelace" --phone "+15551234567" --email "ada@example.com"
```

2. Open `models/luggage_tag/luggage_tag_user.scad` in OpenSCAD.
3. Render (F6), then export STL for printing.

## Notes

- `models/luggage_tag/luggage_tag_user.scad` is ignored by git.
- The base model is `models/luggage_tag/luggage_tag.scad` and reads the values from the wrapper.
- The email address is only embedded in the QR vCard and is not printed as text.
