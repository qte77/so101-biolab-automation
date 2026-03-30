// Tool changer — Berkeley passive tool changer (truncated cone + magnets + dowels)
// Port of hardware/cad/tool_changer.py
// Regenerate:
//   openscad -o hardware/stl/tool_cone_robot.stl -D 'PART="robot"' hardware/scad/tool_changer.scad
//   openscad -o hardware/stl/tool_cone_pipette.stl -D 'PART="male"' hardware/scad/tool_changer.scad
//   openscad -o hardware/stl/tool_cone_gripper.stl -D 'PART="male"' hardware/scad/tool_changer.scad
//   openscad -o hardware/stl/tool_cone_hook.stl -D 'PART="male"' hardware/scad/tool_changer.scad

// Part selector: "robot" (female) or "male" (tool-side)
PART = "robot";

// Parameters (mm) — Berkeley design
WRIST_SCREW_PATTERN_RADIUS = 9.0;
WRIST_SCREW_DIAMETER       = 3.2;   // M3 clearance
CONE_ANGLE_DEG             = 10.0;
CONE_HEIGHT                = 15.0;
CONE_TOP_RADIUS            = 15.0;
CONE_BOTTOM_RADIUS         = CONE_TOP_RADIUS - CONE_HEIGHT * tan(CONE_ANGLE_DEG);
DOWEL_DIAMETER             = 3.0;
DOWEL_HEIGHT               = 8.0;
DOWEL_OFFSET               = 10.0;
MAGNET_DIAMETER            = 5.0;
MAGNET_DEPTH               = 3.0;
MAGNET_OFFSET              = 12.0;
BASE_THICKNESS             = 5.0;
BASE_RADIUS                = CONE_TOP_RADIUS + 3;  // 18.0
MALE_CLEARANCE             = 0.3;
MALE_DOWEL_CLEARANCE       = 0.1;

// Truncated cone (frustum) via rotate_extrude of a trapezoid profile
module frustum(r_bottom, r_top, h) {
    rotate_extrude($fn = 64)
        polygon(points = [
            [0, 0],
            [r_bottom, 0],
            [r_top, h],
            [0, h]
        ]);
}

// Robot-side adapter (female) — conical pocket, screw holes, dowel holes, magnet pockets
module robot_cone() {
    difference() {
        // Base cylinder
        cylinder(h = BASE_THICKNESS, r = BASE_RADIUS, $fn = 64);

        // Conical pocket (cut from top)
        translate([0, 0, BASE_THICKNESS - CONE_HEIGHT])
            frustum(CONE_BOTTOM_RADIUS, CONE_TOP_RADIUS, CONE_HEIGHT + 0.01);

        // M3 mounting holes (4x at 90° intervals, offset 45°)
        for (a = [45, 135, 225, 315])
            translate([
                WRIST_SCREW_PATTERN_RADIUS * cos(a),
                WRIST_SCREW_PATTERN_RADIUS * sin(a),
                -0.5
            ])
                cylinder(h = BASE_THICKNESS + 1, d = WRIST_SCREW_DIAMETER, $fn = 24);

        // Dowel pin holes (2x opposing)
        for (a = [0, 180])
            translate([
                DOWEL_OFFSET * cos(a),
                DOWEL_OFFSET * sin(a),
                BASE_THICKNESS - DOWEL_HEIGHT
            ])
                cylinder(h = DOWEL_HEIGHT + 0.01, d = DOWEL_DIAMETER, $fn = 24);

        // Magnet pockets (2x opposing, perpendicular to dowels)
        for (a = [90, 270])
            translate([
                MAGNET_OFFSET * cos(a),
                MAGNET_OFFSET * sin(a),
                BASE_THICKNESS - MAGNET_DEPTH
            ])
                cylinder(h = MAGNET_DEPTH + 0.01, d = MAGNET_DIAMETER, $fn = 24);
    }
}

// Tool-side adapter (male) — cone protrusion, dowel pins, magnet pockets
module male_cone() {
    difference() {
        union() {
            // Base plate
            cylinder(h = BASE_THICKNESS, r = BASE_RADIUS, $fn = 64);

            // Cone protrusion
            r_top_m    = CONE_TOP_RADIUS - MALE_CLEARANCE;
            r_bottom_m = CONE_BOTTOM_RADIUS - MALE_CLEARANCE;
            translate([0, 0, BASE_THICKNESS])
                frustum(r_bottom_m, r_top_m, CONE_HEIGHT);

            // Dowel pins (2x opposing)
            dowel_d_m = DOWEL_DIAMETER - MALE_DOWEL_CLEARANCE * 2;
            for (a = [0, 180])
                translate([
                    DOWEL_OFFSET * cos(a),
                    DOWEL_OFFSET * sin(a),
                    BASE_THICKNESS + CONE_HEIGHT
                ])
                    cylinder(h = DOWEL_HEIGHT, d = dowel_d_m, $fn = 24);
        }

        // Magnet pockets (2x opposing, perpendicular to dowels)
        for (a = [90, 270])
            translate([
                MAGNET_OFFSET * cos(a),
                MAGNET_OFFSET * sin(a),
                BASE_THICKNESS - MAGNET_DEPTH
            ])
                cylinder(h = MAGNET_DEPTH + 0.01, d = MAGNET_DIAMETER, $fn = 24);
    }
}

// Render selected part
if (PART == "robot") {
    robot_cone();
} else {
    male_cone();
}
