// Gripper fingertip attachments — TPU 95A with grip ridges
// Port of hardware/cad/gripper_tips.py
// Regenerate: openscad -o hardware/stl/gripper_tips_tpu.stl hardware/scad/gripper_tips.scad

// Parameters (mm)
FINGER_WIDTH  = 20.0;
TIP_THICKNESS = 3.0;
TIP_LENGTH    = 25.0;
RIDGE_COUNT   = 5;
RIDGE_DEPTH   = 0.8;
RIDGE_WIDTH   = 1.5;

// Tip base with grip ridges cut out
difference() {
    cube([FINGER_WIDTH, TIP_THICKNESS, TIP_LENGTH], center = true);

    // Cut ridges along the grip surface
    for (i = [0 : RIDGE_COUNT - 1]) {
        z_pos = -TIP_LENGTH / 2 + TIP_LENGTH / (RIDGE_COUNT + 1) * (i + 1);
        translate([0, TIP_THICKNESS / 2 - RIDGE_DEPTH / 2 + 0.5, z_pos])
            cube([FINGER_WIDTH + 1, RIDGE_DEPTH, RIDGE_WIDTH], center = true);
    }
}
