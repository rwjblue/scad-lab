# Geometry and retention notes

The compact four-hole strap keeps two threading holes per wire end. A zip
tie wraps the full plate thickness and clamps the wire bridge between those
holes. The electrical connector remains on slack external tails.

Default geometry:

- 38 × 10 × 2.6 mm body; 6 mm hole pitch; outer holes 4 mm from each end.
- 1.8 mm bores with 0.45 mm chamfers, giving 2.7 mm mouths.
- Tie seats at x = ±12 mm: 3 mm axial flat, 0.75 mm relief per edge,
  and 0.75 mm smooth shoulder transitions.
- 0.4 mm label recess leaves 2.2 mm of plastic beneath the letters.

The tie seat retains full thickness through its middle. The small perimeter
bevel softens exposed edges. Hole pitch, width, and label span grow when
parameters require more room; enlarging the entire model would also change
the hole fit and is unnecessary.

## What the strength calculation establishes

Treating the entire hole as its larger mouth diameter gives a conservative
nominal net area of `(10 − 2.7) × 2.6 = 18.98 mm²`. Before the small edge bevel,
the 8.5 mm waist has `8.5 × 2.6 = 22.1 mm²` gross area. At an illustrative
20 N pull, nominal stress is about 1.05 MPa at that hole section and 0.91 MPa
at the waist. These calculations exclude local stress concentrations,
layer adhesion, creep, and wire contact pressure; they are not a load rating.

Two holes alone do not provide a known holding force. The ideal
[capstan equation](https://sciencedemonstrations.fas.harvard.edu/presentations/friction),
`T_loaded / T_tail = exp(mu × theta)`, multiplies an existing tail restraint.
It does not establish a useful absolute load with a free tail and unknown
friction. The tie adds clamp restraint, but actual wire retention depends on
the jacket, print, tightening, and conditions.

A [HellermannTyton T18R](https://www.hellermanntyton.com/products/cable-ties-inside-serrated/t18r/111-01916)
is a useful dimensional reference: a 2.5 mm band and a substantially larger
head. Its loop tensile rating is not an axial wire-retention rating. The head
and connector add bulk beyond the bare plate envelope.

The first physical check should mark the wire at the holes, load the assembly
with the connector tails slack, and observe slip or jacket damage. An initial
20 N test point is an experiment, not a working limit. Check sustained load,
wet handling, repeated flexing, and winding on the intended winder before
assigning any working load.
