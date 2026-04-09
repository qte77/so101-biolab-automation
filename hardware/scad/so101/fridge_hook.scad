// Fridge hook end-effector — fits ~20mm bar handles
// Port of hardware/cad/fridge_hook.py
// Regenerate: openscad -o hardware/stl/fridge_hook_tool.stl hardware/scad/fridge_hook.scad

// Parameters (mm)
HOOK_OPENING    = 25.0;   // fits ~20mm bar
HOOK_DEPTH      = 40.0;
HOOK_THICKNESS  = 6.0;
HOOK_WIDTH      = 20.0;
MOUNT_DIAMETER  = 30.0;
MOUNT_THICKNESS = 5.0;

union() {
    // Mounting plate (circular)
    cylinder(h = MOUNT_THICKNESS, d = MOUNT_DIAMETER, $fn = 48);

    // Vertical arm
    translate([0, 0, MOUNT_THICKNESS])
        translate([-HOOK_WIDTH / 2, -HOOK_THICKNESS / 2, 0])
            cube([HOOK_WIDTH, HOOK_THICKNESS, HOOK_DEPTH]);

    // Horizontal hook tip
    translate([0, HOOK_OPENING / 2 - HOOK_THICKNESS / 2, MOUNT_THICKNESS + HOOK_DEPTH - HOOK_THICKNESS])
        translate([-HOOK_WIDTH / 2, 0, 0])
            cube([HOOK_WIDTH, HOOK_OPENING, HOOK_THICKNESS]);
}
