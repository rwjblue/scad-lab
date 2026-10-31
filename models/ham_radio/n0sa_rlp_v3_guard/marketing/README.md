# Printables publication draft

**Hold for physical-fit feedback.** Prepared October 31, 2026. The next test
uses two 6 × 2 mm magnets. An earlier nose-down prototype printed successfully
without supports; the longer V6 guard still awaits physical fit and retention
validation. No new Printables model has been published.

## Listing inputs

- `printables.html`: description body for the Printables rich-text editor.
- `metadata.json`: title, short summary, tags, proposed category/license and
  public magnet sourcing links. The proposed license follows the existing
  listings; confirm it when publishing.
- `views.scad`: CAD image views using the actual guard source. The generated
  magnet diagram is a dimensioned schematic. No unmeasured key mockup is used
  to imply verified fit.

Run from the repository root:

```sh
mise run rlp-v3-guard:package
```

The ignored `output/printables/n0sa-rlp-v3-guard/` directory contains the local
preview, description, six checked STLs, direct editable SCAD, plain-text print
guide, CAD PNGs, source ZIP, complete draft ZIP, metadata and SHA-256 manifest.
The task builds local assets only. It does not log in, upload or publish.

## Existing-listing review

Reviewed in the in-app browser:

| Reference | Useful pattern carried into this draft |
|---|---|
| [BNC Dipole Center on Winder](https://www.printables.com/model/1838087-bnc-dipole-center-on-winder) | Short purpose statement, linked hardware, separate printing/assembly notes and clearly identified CAD renders |
| [BNC Dipole Center](https://www.printables.com/model/1838086-bnc-dipole-center) | File-selection table, fit aids, exact hardware dimensions and direct editable source with per-file notes |
| [Doublet Center](https://www.printables.com/model/1838095-doublet-center) | Two variants from one listing and a concrete hardware/assembly sequence |
| [Doublet Feedline Spacers](https://www.printables.com/model/1838096-doublet-feedline-spacers) | Test a small sample first, use actual measured dimensions, and state the limits of CAD checks |

Use one listing for both magnet thicknesses. Put the 2 mm file first and
separate the optional coupon/gauge from the one-piece finished guard. Use a
real photograph for the eventual cover when the fit test passes; the prepared
CAD images can explain pockets, orientation and assembly. Keep marketplace
pull-force claims out of the guard's performance claims.

## Magnet sourcing notes

Only **two discs** are required. The public 1.5 mm product link was verified
as 6 × 1.5 mm N48 with axial magnetization and NiCuNi coating. The 6 × 2 mm
link is a dimension-matched option from the recent product family, not yet
confirmed as the exact test pack. Its grade is unspecified. Keep this
distinction until the owner confirms the actual pack. Do not include account,
order or delivery information in the listing or assets.

Retail pack quantity is not assembly quantity. Use metric 6 mm diameter,
not an exact 1/4 inch substitute. Label diameter × thickness on the listing
and use the matching STL; a 2 mm disc does not fit the 1.5 mm pocket depth.

## Finish after the test print

- Record actual magnet diameter/thickness and the exact 2 mm product link.
- Confirm smooth dry fit, full paddle travel, tip clearance and stationary
  stop contact; then check cured magnet retention and deliberate removal.
- Record the successful PETG profile, layer height, walls, infill, supports
  and any cleanup. Infill has not been selected for the public guide yet.
- Add photos of the closed guard on the key, the open guard/pockets, and
  the nose-down print. A close-up should show the magnet seating.
- Update fit status in metadata, listing copy and the model README from
  actual observations; regenerate assets if geometry changes.
- Confirm license, category and final title; check the two product variants
  and individual file notes in the Printables editor.
- Upload the six STL files separately for previews; include the self-contained
  SCAD and print guide. The ZIPs are convenient supplementary downloads.
- Save and review the Printables draft before publication. The browser was
  signed out during initial preparation, so the current draft is local.
