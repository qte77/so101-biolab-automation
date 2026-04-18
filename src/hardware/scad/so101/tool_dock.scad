// Tool dock — 3-station magnetic parking rack
// Port of hardware/cad/tool_dock.py (Berkeley passive tool changer design)
// Regenerate: openscad -o hardware/stl/tool_dock_3station.stl hardware/scad/tool_dock.scad

// Parameters (mm)
SLOT_DIAMETER   = 38.0;
SLOT_DEPTH      = 20.0;
SLOT_SPACING    = 50.0;  // center-to-center
NUM_SLOTS       = 3;
BASE_THICKNESS  = 5.0;
MAGNET_DIAMETER = 5.0;
MAGNET_DEPTH    = 3.0;

// Derived
DOCK_LENGTH = SLOT_SPACING * (NUM_SLOTS - 1) + SLOT_DIAMETER + 10;  // 148
DOCK_WIDTH  = SLOT_DIAMETER + 10;                                     // 48
TOTAL_H     = BASE_THICKNESS + SLOT_DEPTH;

difference() {
    // Solid base block
    translate([0, 0, TOTAL_H / 2])
        cube([DOCK_LENGTH, DOCK_WIDTH, TOTAL_H], center = true);

    // Cut cylindrical slots
    for (i = [0 : NUM_SLOTS - 1]) {
        x_pos = (i - 1) * SLOT_SPACING;
        // Slot pocket (cut from top)
        translate([x_pos, 0, BASE_THICKNESS + SLOT_DEPTH / 2 + 0.01])
            cylinder(h = SLOT_DEPTH + 0.02, d = SLOT_DIAMETER, center = true, $fn = 48);
        // Magnet pocket (at bottom of slot)
        translate([x_pos, 0, BASE_THICKNESS - MAGNET_DEPTH / 2])
            cylinder(h = MAGNET_DEPTH + 0.01, d = MAGNET_DIAMETER, center = true, $fn = 24);
    }
}
