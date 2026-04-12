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
        with TestClient(app) as client, client.websocket_connect("/ws") as ws:
            ws.send_text(json.dumps({"command": "e_stop"}))
            resp = json.loads(ws.receive_text())
            assert resp["status"]["e_stopped"] is True
            assert resp["status"]["mode"] == "e_stopped"

    def test_heartbeat_websocket(self) -> None:
        """Heartbeat command succeeds without error."""
        with TestClient(app) as client, client.websocket_connect("/ws") as ws:
            ws.send_text(json.dumps({"command": "heartbeat"}))
            resp = json.loads(ws.receive_text())
            assert "status" in resp

    def test_target_well_websocket(self) -> None:
        """target_well command returns status."""
        with TestClient(app) as client, client.websocket_connect("/ws") as ws:
            ws.send_text(json.dumps({"command": "target_well", "well": "A1"}))
            resp = json.loads(ws.receive_text())
            assert "status" in resp


class TestWebSocketErrors:
    """WebSocket error handling paths."""

    def test_malformed_json_returns_error(self) -> None:
        """Sending non-JSON text returns an error, doesn't crash."""
        with TestClient(app) as client, client.websocket_connect("/ws") as ws:
            ws.send_text("not valid json {{{")
            resp = json.loads(ws.receive_text())
            assert "error" in resp
            assert "invalid JSON" in resp["error"]

    def test_unknown_command_succeeds(self) -> None:
        """Unknown commands don't crash — they just return status."""
        with TestClient(app) as client, client.websocket_connect("/ws") as ws:
            ws.send_text(json.dumps({"command": "nonexistent_command"}))
            resp = json.loads(ws.receive_text())
            assert "status" in resp

    def test_empty_command_succeeds(self) -> None:
        """Missing command key returns status without error."""
        with TestClient(app) as client, client.websocket_connect("/ws") as ws:
            ws.send_text(json.dumps({"no_command_key": True}))
            resp = json.loads(ws.receive_text())
            assert "status" in resp


class TestStatusEndpoint:
    """REST status endpoint."""

    def test_get_status_returns_expected_keys(self) -> None:
        """GET /api/status returns mode, e_stopped, connected, arm_ids."""
        with TestClient(app) as client:
            resp = client.get("/api/status")
            assert resp.status_code == 200
            data = resp.json()
            assert "mode" in data
            assert "e_stopped" in data
            assert "connected" in data
            assert "arm_ids" in data
