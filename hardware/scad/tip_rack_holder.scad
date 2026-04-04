// Tip rack holder — tray with walls for standard 96-tip rack
// Port of hardware/cad/tip_rack_holder.py
// Regenerate: openscad -o hardware/stl/tip_rack_holder.stl hardware/scad/tip_rack_holder.scad

// Parameters (mm)
RACK_LENGTH    = 122.0;
RACK_WIDTH     = 80.0;
WALL_THICKNESS = 2.0;
WALL_HEIGHT    = 10.0;
BASE_THICKNESS = 3.0;
CLEARANCE      = 0.5;

// Derived
INNER_L = RACK_LENGTH + CLEARANCE * 2;  // 123.0
INNER_W = RACK_WIDTH  + CLEARANCE * 2;  // 81.0
OUTER_L = INNER_L + WALL_THICKNESS * 2; // 127.0
OUTER_W = INNER_W + WALL_THICKNESS * 2; // 85.0

// Base plate
translate([0, 0, BASE_THICKNESS / 2])
    cube([OUTER_L, OUTER_W, BASE_THICKNESS], center = true);

// Walls (outer box minus inner box)
translate([0, 0, BASE_THICKNESS + WALL_HEIGHT / 2])
    difference() {
        cube([OUTER_L, OUTER_W, WALL_HEIGHT], center = true);
        cube([INNER_L, INNER_W, WALL_HEIGHT + 1], center = true);
    }
