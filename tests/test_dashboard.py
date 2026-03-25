"""Tests for dashboard server — FastAPI integration."""

from __future__ import annotations

import json

from starlette.testclient import TestClient

from dashboard.server import app


class TestDashboardEndpoints:
    """Test REST endpoints."""

    def test_index_returns_html(self) -> None:
        """GET / returns HTML dashboard page."""
        with TestClient(app) as client:
            resp = client.get("/")
            assert resp.status_code == 200
            assert "so101-biolab-automation" in resp.text

    def test_status_endpoint(self) -> None:
        """GET /api/status returns dict with expected keys."""
        with TestClient(app) as client:
            resp = client.get("/api/status")
            assert resp.status_code == 200
            data = resp.json()
            assert "mode" in data
            assert "e_stopped" in data
            assert "connected" in data
            assert data["connected"] is True

    def test_status_shows_arm_ids(self) -> None:
        """GET /api/status includes arm IDs."""
        with TestClient(app) as client:
            data = client.get("/api/status").json()
            assert "arm_ids" in data
            assert "arm_a" in data["arm_ids"]
            assert "arm_b" in data["arm_ids"]


class TestDashboardWebSocket:
    """Test WebSocket command channel."""

    def test_e_stop_websocket(self) -> None:
        """e_stop command sets e_stopped state."""
        with TestClient(app) as client:
            with client.websocket_connect("/ws") as ws:
                ws.send_text(json.dumps({"command": "e_stop"}))
                resp = json.loads(ws.receive_text())
                assert resp["status"]["e_stopped"] is True
                assert resp["status"]["mode"] == "e_stopped"

    def test_heartbeat_websocket(self) -> None:
        """heartbeat command succeeds without error."""
        with TestClient(app) as client:
            with client.websocket_connect("/ws") as ws:
                ws.send_text(json.dumps({"command": "heartbeat"}))
                resp = json.loads(ws.receive_text())
                assert "status" in resp

    def test_target_well_websocket(self) -> None:
        """target_well command returns status."""
        with TestClient(app) as client:
            with client.websocket_connect("/ws") as ws:
                ws.send_text(json.dumps({"command": "target_well", "well": "A1"}))
                resp = json.loads(ws.receive_text())
                assert "status" in resp
