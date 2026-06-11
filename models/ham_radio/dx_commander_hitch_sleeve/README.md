# DX Commander Hitch Sleeve

Sleeve adapter for using a DX Commander Expedition mast in a hitch-mounted
flag pole holder.

## Default Dimensions

| Feature | Value |
| --- | ---: |
| Holder tube ID | 59 mm |
| Sleeve body OD | 58.5 mm |
| Mast measured OD | 47 mm |
| Mast bore ID | 47.6 mm |
| Lower insertion height | 76.2 mm |
| Upper guide height | 20 mm |
| Stop flange OD | 68 mm |
| Stop flange height | 5 mm |
| Total height | 101.2 mm |

When installed, the 68 mm flange rests on the holder rim. The sleeve extends
76.2 mm into the holder and 20 mm above the rim.

## Printing

Print upright in PETG. Enable supports for the underside of the stop flange. The
supported underside is not a precision fit surface; the important fit surfaces
are the sleeve body OD, mast bore ID, and the flat lower face of the flange that
rests on the holder rim.

## Fit Tuning

The main fit parameters are at the top of
`dx_commander_hitch_sleeve.scad`.

- If the holder fit is too tight, reduce `body_outer_d`.
- If the holder fit is too loose, increase `body_outer_d`, keeping it below
  `holder_inner_d`.
- If the mast fit is too tight, increase `mast_bore_d` toward 47.8 mm.
- If the mast fit is too loose, reduce `mast_bore_d` toward 47.4 mm.
