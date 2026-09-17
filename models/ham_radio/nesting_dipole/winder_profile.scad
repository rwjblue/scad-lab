/*
  Adjustable K6ARK-derived winding profile; units mm.
  Attribution and upstream terms remain in NOTICE.md and native_profile.scad.

  wing_length is the native Y=0 datum to the outer horn-tip Y coordinate.
  It is 37.5 mm at original size, not the diagonal horn length. Increasing it
  moves the rounded tips along the existing horn sweep. The straight arm
  sections lengthen; tip radii, roots and the central tie brace stay intact.

  winding_span is the X distance between the two lower outer tips (140 mm
  originally). The |X| <= 44 mm core stays fixed. An 8 mm transition band on
  each side lengthens horizontally; everything beyond |X|=52 translates.
  Split polygon edges at the band boundaries to make this a continuous,
  non-contracting map rather than a vertex-only distortion. For span >=140,
  the band cannot reduce an existing wall or opening width. Horn extensions
  can project beyond the lower tips: use profile bounds for total width.

  Both adjustments only enlarge the source. Alignment posts and the tie
  brace stay at their original stations; posts are added by the main model.
  Default arguments return the exact native points and paths.
*/
use <native_profile.scad>

function winder_wing_sweep(side=1) =
    side >= 0 ? 26.40465549589185 : 26.424330211870213;
function winder_tip_point(p,wing_length=37.5) =
    p[1] > 20 && abs(p[0]) > 40 ?
        [p[0]+sign(p[0])*(wing_length-37.5)*tan(winder_wing_sweep(p[0])),
         p[1]+wing_length-37.5] : p;
function winder_span_point(p,winding_span=140) =
    [p[0]+sign(p[0])*(winding_span-140)/2*min(1,max(0,(abs(p[0])-44)/8)),p[1]];
function winder_split_edge(a,b) =
    concat([a],[for(x=b[0]>=a[0] ? [-52,-44,44,52] : [52,44,-44,-52])
        if(x>min(a[0],b[0])+0.0000001 && x<max(a[0],b[0])-0.0000001)
            a+(b-a)*(x-a[0])/(b[0]-a[0])]);
function winder_profile_rings(wing_length=37.5,winding_span=140) =
    let(points=native_points())
    [for(path=native_paths())
        let(tips=[for(i=path) winder_tip_point(points[i],wing_length)])
        [for(i=[0:len(tips)-1])
            each [for(p=winder_split_edge(tips[i],tips[(i+1)%len(tips)]))
                winder_span_point(p,winding_span)]]];
function winder_ring_start(rings,i) = i==0 ? 0 : len(rings[i-1])+winder_ring_start(rings,i-1);
function winder_profile_points(wing_length=37.5,winding_span=140) =
    wing_length==37.5 && winding_span==140 ? native_points() :
        [for(ring=winder_profile_rings(wing_length,winding_span)) each ring];
function winder_profile_paths(wing_length=37.5,winding_span=140) =
    wing_length==37.5 && winding_span==140 ? native_paths() :
        let(rings=winder_profile_rings(wing_length,winding_span))
        [for(i=[0:len(rings)-1])
            [for(j=[0:len(rings[i])-1]) winder_ring_start(rings,i)+j]];
// [[minimum X, minimum Y], [maximum X, maximum Y]] in native coordinates.
function winder_profile_bounds(wing_length=37.5,winding_span=140) =
    let(points=winder_profile_points(wing_length,winding_span))
    [[min([for(p=points) p[0]]),min([for(p=points) p[1]])],
     [max([for(p=points) p[0]]),max([for(p=points) p[1]])]];

module adjustable_winder_frame_2d(wing_length=37.5,winding_span=140) {
    assert(wing_length>=37.5 && wing_length<=60,
        "Winder wing reach must be 37.5..60 mm; only source-preserving extension is supported");
    assert(winding_span>=140 && winding_span<=200,
        "Winder lower-tip span must be 140..200 mm; keep the fixed docking core");
    polygon(points=winder_profile_points(wing_length,winding_span),
        paths=winder_profile_paths(wing_length,winding_span),convexity=20);
}
