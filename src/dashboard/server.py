"""FastAPI server for remote oversight dashboard.

Provides:
- WebSocket command channel (pause/resume, e-stop, well targeting, heartbeat)
- REST API for arm telemetry and status
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from biolab.arms import ArmConfig, DualArmConfig, DualArmController
from biolab.safety import SafetyConfig, SafetyMonitor

logger = logging.getLogger(__name__)

_mode = "idle"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Create controller and monitor on startup, cleanup on shutdown."""
    config = DualArmConfig(
        arm_a=ArmConfig(arm_id="arm_a", port="/dev/null", role="follower"),
        arm_b=ArmConfig(arm_id="arm_b", port="/dev/null", role="follower"),
    )
    controller = DualArmController(config)
    controller.connect()

    monitor = SafetyMonitor(SafetyConfig(), park_callback=controller.park_all)
    monitor.start()

    app.state.controller = controller
    app.state.monitor = monitor
    logger.info("Dashboard started — controller and monitor active")
    yield
    monitor.stop()
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
    global _mode  # noqa: PLW0603
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
