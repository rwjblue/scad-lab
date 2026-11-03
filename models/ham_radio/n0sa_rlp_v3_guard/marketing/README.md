# Printables listing assets

`printables.html` is the listing description. `metadata.json` contains the title, short description, tags and suggested license. The key photo is in `../images/rlp-v3-key.jpg`; the QRZ listing is linked for photo and product attribution. `views.scad` produces illustrations of the guard from its actual source.

Build the upload files and a local browser preview from the repository root:

```sh
mise run rlp-v3-guard:package
```

The output is in `output/printables/n0sa-rlp-v3-guard/`. It includes the full guard, two optional fit tools, editable source, README, an uploadable text guide, key photo, CAD views, pocket diagram, listing text and one download bundle. STL filenames stay the same as the design evolves.

The package task builds local files. Save the listing as a draft on Printables, check the license and category in the editor, and add photographs of the printed guard on the key before publication. The key reference photo shows the paddle on its own; the guard illustrations are labeled CAD renders.

## Reference listings

The short introduction, hardware list and separate print/assembly notes follow the same layout as these projects:

- [BNC Dipole Center on Winder](https://www.printables.com/model/1838087-bnc-dipole-center-on-winder)
- [BNC Dipole Center](https://www.printables.com/model/1838086-bnc-dipole-center)
- [Doublet Center](https://www.printables.com/model/1838095-doublet-center)
- [Doublet Feedline Spacers](https://www.printables.com/model/1838096-doublet-feedline-spacers)
