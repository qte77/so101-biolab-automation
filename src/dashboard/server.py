"""FastAPI server for remote oversight dashboard.

Provides:
- WebSocket command channel (pause/resume, e-stop, well targeting, heartbeat, run_workflow)
- REST API for arm telemetry and status
"""

from __future__ import annotations

import json
import logging
import threading
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from biolab.arms import DualArmConfig, DualArmController
from biolab.pipette import DigitalPipette, PipetteConfig
from biolab.safety import SafetyConfig, SafetyMonitor
from biolab.tool_changer import ToolChanger, ToolDockConfig
from biolab.workflow import PlateLayout, uc4_demo_all

logger = logging.getLogger(__name__)

_mode = "idle"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Create all components on startup, cleanup on shutdown."""
    arm_config = DualArmConfig.from_yaml("configs/arms.yaml")
    controller = DualArmController(arm_config)
    controller.connect()

    monitor = SafetyMonitor(SafetyConfig(), park_callback=controller.park_all)
    monitor.start()

    dock_config = ToolDockConfig.from_yaml("configs/tool_dock.yaml")
    changer = ToolChanger(dock_config, controller, "arm_a")

    pipette = DigitalPipette(PipetteConfig())
    pipette.connect()

    layout = PlateLayout.from_yaml("configs/plate_layout.yaml")

    app.state.controller = controller
    app.state.monitor = monitor
    app.state.changer = changer
    app.state.pipette = pipette
    app.state.layout = layout

    logger.info("Dashboard started — all components active")
    yield
    monitor.stop()
    pipette.disconnect()
    controller.disconnect()
    logger.info("Dashboard shutdown")


app = FastAPI(title="so101-biolab-automation Dashboard", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    """Serve the dashboard page."""
    return """<!DOCTYPE html>
<html>
<head><title>so101-biolab-automation</title></head>
<body>
<h1>so101-biolab-automation Dashboard</h1>
<p>Camera feeds and controls will be rendered here.</p>
<div id="controls">
    <button onclick="sendCmd('pause')">Pause</button>
    <button onclick="sendCmd('resume')">Resume</button>
    <button onclick="sendCmd('heartbeat')">Heartbeat</button>
    <button onclick="sendCmd('run_workflow')">Run Demo</button>
    <button onclick="sendCmd('e_stop')" style="background:red;color:white">E-STOP</button>
</div>
<script>
const ws = new WebSocket(`ws://${location.host}/ws`);
ws.onmessage = (e) => console.log('Server:', JSON.parse(e.data));
function sendCmd(cmd) { ws.send(JSON.stringify({command: cmd})); }
</script>
</body>
</html>"""


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket command channel for remote operator."""
    global _mode
    await websocket.accept()
    logger.info("Remote operator connected")

    controller: DualArmController = websocket.app.state.controller
    monitor: SafetyMonitor = websocket.app.state.monitor

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            command = msg.get("command", "")

            if command == "e_stop":
                monitor.e_stop()
                _mode = "e_stopped"
            elif command == "heartbeat":
                monitor.heartbeat()
            elif command == "pause":
                _mode = "paused"
            elif command == "resume":
                _mode = "autonomous"
                monitor.reset_e_stop()
            elif command == "target_well":
                well = msg.get("well", "A1")
                controller.send_to_well("arm_a", well)
            elif command == "run_workflow":
                _mode = "running"
                threading.Thread(target=_run_workflow, args=(websocket.app,), daemon=True).start()

            await websocket.send_text(json.dumps({"status": _get_status(controller, monitor)}))
    except WebSocketDisconnect:
        logger.info("Remote operator disconnected")


@app.get("/api/status")
async def get_status() -> dict[str, Any]:
    """Get current system status."""
    return _get_status(app.state.controller, app.state.monitor)


def _get_status(controller: DualArmController, monitor: SafetyMonitor) -> dict[str, Any]:
    """Build status dict from real controller and monitor state."""
    return {
        "mode": _mode,
        "e_stopped": monitor.is_e_stopped,
        "connected": controller._connected,
        "arm_ids": controller.arm_ids,
    }


def _run_workflow(app: FastAPI) -> None:
    """Run full demo workflow in background thread."""
    global _mode
    try:
        uc4_demo_all(
            app.state.controller,
            app.state.pipette,
            app.state.changer,
            app.state.layout,
            "arm_a",
        )
        _mode = "idle"
    except Exception:
        logger.exception("Workflow failed")
        _mode = "error"
