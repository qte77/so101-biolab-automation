"""FastAPI server for remote oversight dashboard.

Provides:
- WebSocket command channel (pause/resume, e-stop, well targeting)
- WebRTC signaling for camera streams
- REST API for arm telemetry and status
"""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger(__name__)

app = FastAPI(title="so101-biolab-automation Dashboard")


# --- State (replaced by real controller in production) ---
_state: dict[str, Any] = {
    "mode": "idle",  # idle, teleop, autonomous, paused, e_stopped
    "arm_a_tool": "gripper",
    "arm_b_tool": "gripper",
    "target_well": None,
    "task_progress": 0,
}


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    """Serve the dashboard page."""
    return """<!DOCTYPE html>
<html>
<head><title>so101-biolab-automation</title></head>
<body>
<h1>so101-biolab-automation Dashboard</h1>
<p>Camera feeds and controls will be rendered here.</p>
<div id="cameras"></div>
<div id="plate-grid"></div>
<div id="controls">
    <button onclick="sendCmd('pause')">Pause</button>
    <button onclick="sendCmd('resume')">Resume</button>
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
    await websocket.accept()
    logger.info("Remote operator connected")

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            command = msg.get("command", "")

            if command == "e_stop":
                _state["mode"] = "e_stopped"
                logger.warning("Remote E-STOP received")
            elif command == "pause":
                _state["mode"] = "paused"
            elif command == "resume":
                _state["mode"] = "autonomous"
            elif command == "target_well":
                _state["target_well"] = msg.get("well")
                logger.info("Target well set to %s", _state["target_well"])

            await websocket.send_text(json.dumps({"status": _state}))
    except WebSocketDisconnect:
        logger.info("Remote operator disconnected")


@app.get("/api/status")
async def get_status() -> dict[str, Any]:
    """Get current system status."""
    return _state
