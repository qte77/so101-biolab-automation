"""Tests for eLabFTW ELN client."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

if TYPE_CHECKING:
    from pathlib import Path
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from so101.eln_client import ElnClient, ElnConfig


class TestElnConfigModel:
    """ElnConfig pydantic model validation."""

    def test_defaults(self) -> None:
        cfg = ElnConfig()
        assert cfg.base_url == "https://elab.example.com/api/v2"
        assert cfg.api_key == ""
        assert cfg.verify_ssl is True
        assert cfg.timeout_s == 30.0

    def test_strict_rejects_str_for_float(self) -> None:
        with pytest.raises(ValidationError):
            ElnConfig(timeout_s="30")  # type: ignore[arg-type]

    def test_strict_rejects_int_for_str(self) -> None:
        with pytest.raises(ValidationError):
            ElnConfig(base_url=123)  # type: ignore[arg-type]

    @pytest.mark.integration
    def test_from_yaml(self) -> None:
        cfg = ElnConfig.from_yaml("configs/eln.yaml")
        assert cfg.base_url == "https://elab.example.com/api/v2"
        assert cfg.timeout_s == 30.0


class TestElnClientStubMode:
    """Tests for stub mode activation."""

    def test_connect_without_package(self) -> None:
        """ImportError on elabapi_python triggers stub mode."""
        import builtins

        original_import = builtins.__import__

        def mock_import(name: str, *args: object, **kwargs: object) -> object:
            if name == "elabapi_python":
                raise ImportError("no module named elabapi_python")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            client = ElnClient(ElnConfig())
            client.connect()
            assert client.is_stub_mode is True

    def test_is_stub_mode_property(self) -> None:
        client = ElnClient(ElnConfig())
        assert client.is_stub_mode is False
        client._stub_mode = True
        assert client.is_stub_mode is True

    def test_disconnect_idempotent(self) -> None:
        client = ElnClient(ElnConfig())
        client.disconnect()
        client.disconnect()  # second call must not raise


class TestElnClientOperations:
    """Stub-mode operations return safe defaults."""

    @pytest.fixture
    def stub_client(self) -> ElnClient:
        """Return an ELN client in stub mode."""
        client = ElnClient(ElnConfig())
        client._stub_mode = True
        return client

    def test_create_experiment_stub(self, stub_client: ElnClient) -> None:
        assert stub_client.create_experiment("test title") == -1

    def test_update_experiment_stub(self, stub_client: ElnClient) -> None:
        stub_client.update_experiment(1, body="updated")  # must not raise

    def test_upload_attachment_stub(self, stub_client: ElnClient, tmp_path: Path) -> None:
        assert stub_client.upload_attachment(1, tmp_path / "test.csv") == -1

    def test_get_item_stub(self, stub_client: ElnClient) -> None:
        assert stub_client.get_item(1) == {}


class TestElnClientWithMock:
    """Mock SDK methods to verify API calls."""

    def _make_connected_client(self) -> tuple[ElnClient, MagicMock]:
        """Create a client with mocked SDK internals."""
        client = ElnClient(ElnConfig())
        mock_experiments_api = MagicMock()
        mock_items_api = MagicMock()
        mock_uploads_api = MagicMock()
        client._experiments_api = mock_experiments_api
        client._items_api = mock_items_api
        client._uploads_api = mock_uploads_api
        client._api_client = MagicMock()
        return client, mock_experiments_api

    def test_create_experiment_calls_api(self) -> None:
        client, mock_api = self._make_connected_client()
        mock_api.post_experiment.return_value = MagicMock(id=42)
        result = client.create_experiment("My Experiment", body="some body")
        mock_api.post_experiment.assert_called_once()
        assert result == 42

    def test_update_experiment_calls_api(self) -> None:
        client, mock_api = self._make_connected_client()
        client.update_experiment(42, body="new body", status="running")
        mock_api.patch_experiment.assert_called_once()

    def test_upload_attachment_calls_api(self, tmp_path: Path) -> None:
        client, _ = self._make_connected_client()
        mock_uploads = client._uploads_api
        mock_uploads.post_upload.return_value = MagicMock(id=99)
        result = client.upload_attachment(42, tmp_path / "test.csv")
        mock_uploads.post_upload.assert_called_once()
        assert result == 99


class TestElnConfigHypothesis:
    """Property-based tests for config construction."""

    @given(st.text())
    def test_fuzz_base_url(self, url: str) -> None:
        cfg = ElnConfig(base_url=url)
        assert cfg.base_url == url

    @given(st.text())
    def test_fuzz_api_key(self, key: str) -> None:
        cfg = ElnConfig(api_key=key)
        assert cfg.api_key == key
