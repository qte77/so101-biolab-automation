"""eLabFTW Electronic Lab Notebook (ELN) client.

Wraps eLabFTW REST API v2 via the ``elabapi-python`` SDK.  Falls back to
stub mode when the SDK is not installed or the server is unreachable —
same graceful-degradation pattern used by :class:`BentoLab`.

Reference: https://www.elabftw.net/
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict

logger = logging.getLogger(__name__)


class ElnConfig(BaseModel):
    """Configuration for the eLabFTW ELN connection."""

    model_config = ConfigDict(strict=True)

    base_url: str = "https://elab.example.com/api/v2"
    api_key: str = ""
    verify_ssl: bool = True
    timeout_s: float = 30.0

    @classmethod
    def from_yaml(cls, path: str | Path) -> Self:
        """Load configuration from a YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)


class ElnClient:
    """Client for the eLabFTW Electronic Lab Notebook.

    Usage::

        client = ElnClient(ElnConfig.from_yaml("configs/eln.yaml"))
        client.connect()
        exp_id = client.create_experiment("PCR run 2024-01-15")
        client.update_experiment(exp_id, body="<p>Results …</p>")
        client.upload_attachment(exp_id, Path("results.csv"))
        client.disconnect()
    """

    def __init__(self, config: ElnConfig) -> None:
        """Initialize with ELN configuration."""
        self.config = config
        self._api_client: Any = None
        self._experiments_api: Any = None
        self._items_api: Any = None
        self._uploads_api: Any = None
        self._stub_mode = False

    def connect(self) -> None:
        """Connect to the eLabFTW server.

        Tries to import ``elabapi_python`` and configure the API client.
        Falls back to stub mode on ``ImportError`` or connection failure.
        """
        try:
            import elabapi_python  # type: ignore[import-untyped]

            elab: Any = elabapi_python  # untyped SDK — cast to Any once
            cfg = elab.Configuration()
            cfg.host = self.config.base_url
            cfg.verify_ssl = self.config.verify_ssl
            self._api_client = elab.ApiClient(cfg)
            self._api_client.set_default_header("Authorization", self.config.api_key)
            self._experiments_api = elab.ExperimentsApi(self._api_client)
            self._items_api = elab.ItemsApi(self._api_client)
            self._uploads_api = elab.UploadsApi(self._api_client)
            logger.info("eLabFTW connected to %s", self.config.base_url)
        except ImportError:
            logger.warning("elabapi-python not installed — running in stub mode")
            self._stub_mode = True
        except Exception as exc:
            logger.warning("eLabFTW connection failed (%s) — running in stub mode", exc)
            self._stub_mode = True

    @property
    def is_stub_mode(self) -> bool:
        """Return whether the client is running in stub mode."""
        return self._stub_mode

    def create_experiment(self, title: str, body: str = "") -> int:
        """Create a new experiment.

        Args:
            title: Experiment title.
            body: Optional HTML body content.

        Returns:
            The experiment ID, or ``-1`` in stub mode.
        """
        if self._stub_mode or self._experiments_api is None:
            logger.debug("Stub mode — skipping create_experiment(%r)", title)
            return -1
        response = self._experiments_api.post_experiment(
            body={"title": title, "body": body},
        )
        exp_id: int = response.id
        logger.info("Created experiment %d: %s", exp_id, title)
        return exp_id

    def update_experiment(
        self,
        exp_id: int,
        body: str | None = None,
        status: str | None = None,
    ) -> None:
        """Update an existing experiment.

        Args:
            exp_id: Experiment ID to update.
            body: New HTML body content (optional).
            status: New status string (optional).
        """
        if self._stub_mode or self._experiments_api is None:
            logger.debug("Stub mode — skipping update_experiment(%d)", exp_id)
            return
        patch_body: dict[str, str] = {}
        if body is not None:
            patch_body["body"] = body
        if status is not None:
            patch_body["status"] = status
        self._experiments_api.patch_experiment(exp_id, body=patch_body)
        logger.info("Updated experiment %d", exp_id)

    def upload_attachment(self, exp_id: int, filepath: Path) -> int:
        """Upload a file attachment to an experiment.

        Args:
            exp_id: Target experiment ID.
            filepath: Local file path to upload.

        Returns:
            The upload ID, or ``-1`` in stub mode.
        """
        if self._stub_mode or self._uploads_api is None:
            logger.debug("Stub mode — skipping upload_attachment(%d)", exp_id)
            return -1
        response = self._uploads_api.post_upload("experiments", exp_id, file=str(filepath))
        upload_id: int = response.id
        logger.info("Uploaded %s to experiment %d (upload %d)", filepath, exp_id, upload_id)
        return upload_id

    def get_item(self, item_id: int) -> dict[str, Any]:
        """Retrieve a database item by ID.

        Args:
            item_id: The item ID to fetch.

        Returns:
            Item data as a dictionary, or empty dict in stub mode.
        """
        if self._stub_mode or self._items_api is None:
            logger.debug("Stub mode — skipping get_item(%d)", item_id)
            return {}
        response = self._items_api.get_item(item_id)
        return dict(response.to_dict())

    def disconnect(self) -> None:
        """Clean up the API client."""
        if self._api_client is not None:
            self._api_client = None
            self._experiments_api = None
            self._items_api = None
            self._uploads_api = None
            logger.info("eLabFTW client disconnected")
