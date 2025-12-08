/*
  lib/rounded_cube.scad

  Simple "rounded cube" helper using minkowski sum.
  Not super performance-friendly for big parts, but handy for small stuff.
*/

module rounded_cube(size = [10, 10, 10], r = 1, center = false) {
    minkowski() {
        cube(size, center = center);
        sphere(r = r, $fn = 32);
    }
}
