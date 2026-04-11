// Pipette mount — barrel clamp for digital-pipette-v2 on SO-101 wrist
// Port of hardware/cad/pipette_mount.py
// Regenerate: openscad -o hardware/stl/pipette_mount_so101.stl hardware/scad/pipette_mount.scad

// Parameters (mm)
BARREL_DIAMETER  = 20.0;
BARREL_CLEARANCE = 0.3;
CLAMP_LENGTH     = 40.0;
CLAMP_WALL       = 4.0;
MOUNT_WIDTH      = 36.0;
MOUNT_THICKNESS  = 5.0;
SPLIT_GAP        = 2.0;
SCREW_DIAMETER   = 3.2;  // M3 clearance

// Derived
BORE_D     = BARREL_DIAMETER + BARREL_CLEARANCE * 2;  // 20.6
CLAMP_OD   = BORE_D + CLAMP_WALL * 2;                 // 28.6
SCREW_OFFSET = CLAMP_OD / 2 + 3;                      // 17.3

union() {
    // Mounting plate
    translate([0, 0, MOUNT_THICKNESS / 2])
        cube([MOUNT_WIDTH, MOUNT_WIDTH, MOUNT_THICKNESS], center = true);

    // Clamp body with barrel hole and split gap
    translate([0, 0, MOUNT_THICKNESS])
        difference() {
            // Outer clamp cylinder
            cylinder(h = CLAMP_LENGTH, d = CLAMP_OD, $fn = 48);

            // Barrel bore
            translate([0, 0, -0.5])
                cylinder(h = CLAMP_LENGTH + 1, d = BORE_D, $fn = 48);

            // Split gap for tightening
            translate([-SPLIT_GAP / 2, -CLAMP_OD / 2 - 0.5, -0.5])
                cube([SPLIT_GAP, CLAMP_OD + 1, CLAMP_LENGTH + 1]);

            // Screw holes (2x, through the split ears)
            for (z_frac = [0.25, 0.75]) {
                translate([0, -SCREW_OFFSET - 5, CLAMP_LENGTH * z_frac])
                    rotate([90, 0, 90])
                        translate([0, 0, -MOUNT_WIDTH / 2])
                            cylinder(h = MOUNT_WIDTH, d = SCREW_DIAMETER, $fn = 24);
            }
        }
}
