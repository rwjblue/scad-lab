/*
  Chamfer both faces of an arbitrary 2D plate, including internal windows.
  Usage: beveled_frame(height=5, bevel=0.5) reference_frame_2d();

  The native profile is unchanged between Z=bevel and Z=height-bevel.
  Each face retreats by bevel, so a straight edge receives a 45-degree
  chamfer without expanding the native footprint. Concave corners follow
  the circular distance offset, approximated by the local cone facets.

  Subtracting a conical expansion of the profile's OUTSIDE avoids the
  ledges that an inset-profile Minkowski bevel can leave at sharp tips.
  A finite outside band eliminates any arbitrary bounding-box limit.
  Drill separately chamfered wire/rope bores after constructing the plate.
*/

module beveled_frame(height=5, bevel=0.5, facets=48) {
    assert(height > 0, "Plate thickness must be positive");
    assert(bevel >= 0 && 2*bevel < height,
           "Bevel must leave a full-thickness central band");
    assert(facets >= 12, "Use at least 12 cone facets");

    if(bevel == 0) {
        linear_extrude(height=height, convexity=30) children();
    } else {
        difference() {
            linear_extrude(height=height, convexity=30) children();
            for(top=[false,true])
                translate([0,0,top ? height : 0])
                    scale([1,1,top ? -1 : 1])
                        translate([0,0,-bevel])
                            minkowski() {
                                linear_extrude(height=bevel, convexity=30)
                                    difference() {
                                        offset(delta=2*bevel) children();
                                        children();
                                    }
                                cylinder(h=bevel,r1=bevel,r2=0,$fn=facets);
                            }
        }
    }
}
