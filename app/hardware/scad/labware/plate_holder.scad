// 96-well microplate holder — SBS/ANSI standard with alignment pins
// Port of hardware/cad/plate_holder.py
// Regenerate: openscad -o hardware/stl/96well_plate_holder.stl hardware/scad/plate_holder.scad

// Parameters (mm)
PLATE_LENGTH    = 127.76;  // SBS standard
PLATE_WIDTH     = 85.48;   // SBS standard
PLATE_HEIGHT    = 14.35;
WALL_THICKNESS  = 2.0;
BASE_THICKNESS  = 3.0;
HOLDER_CLEARANCE = 0.5;
PIN_DIAMETER    = 3.0;
PIN_HEIGHT      = 5.0;
PIN_INSET       = 5.0;

// Derived
INNER_L    = PLATE_LENGTH + HOLDER_CLEARANCE * 2;  // 128.76
INNER_W    = PLATE_WIDTH  + HOLDER_CLEARANCE * 2;  // 86.48
OUTER_L    = INNER_L + WALL_THICKNESS * 2;          // 132.76
OUTER_W    = INNER_W + WALL_THICKNESS * 2;          // 90.48
WALL_HEIGHT = PLATE_HEIGHT * 0.6;                    // 8.61
FLOOR_DEPTH = 1.0;

union() {
    // Base plate with pocket (floor_depth = 1mm)
    difference() {
        translate([0, 0, BASE_THICKNESS / 2])
            cube([OUTER_L, OUTER_W, BASE_THICKNESS], center = true);
        // Pocket cut (leave 1mm floor)
        translate([0, 0, FLOOR_DEPTH + (BASE_THICKNESS - FLOOR_DEPTH) / 2 + 0.01])
            cube([INNER_L, INNER_W, BASE_THICKNESS - FLOOR_DEPTH + 0.02], center = true);
    }

    // Walls
    translate([0, 0, BASE_THICKNESS + WALL_HEIGHT / 2])
        difference() {
            cube([OUTER_L, OUTER_W, WALL_HEIGHT], center = true);
            cube([INNER_L, INNER_W, WALL_HEIGHT + 1], center = true);
        }

    // 4 alignment pins at corners
    for (sx = [-1, 1])
        for (sy = [-1, 1])
            translate([
                sx * (INNER_L / 2 - PIN_INSET),
                sy * (INNER_W / 2 - PIN_INSET),
                BASE_THICKNESS + PIN_HEIGHT / 2
            ])
                cylinder(h = PIN_HEIGHT, d = PIN_DIAMETER, center = true, $fn = 24);
}
