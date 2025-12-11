"""
Graphiti Integration Configuration
==================================

Constants, status mappings, and configuration helpers for Graphiti memory integration.
Follows the same patterns as linear_config.py for consistency.

Environment Variables:
    GRAPHITI_ENABLED: Set to "true" to enable Graphiti integration
    OPENAI_API_KEY: Required by Graphiti for embeddings
    GRAPHITI_FALKORDB_HOST: FalkorDB host (default: localhost)
    GRAPHITI_FALKORDB_PORT: FalkorDB port (default: 6380)
    GRAPHITI_FALKORDB_PASSWORD: FalkorDB password (default: empty)
    GRAPHITI_DATABASE: Graph database name (default: auto_build_memory)
    GRAPHITI_TELEMETRY_ENABLED: Set to "false" to disable telemetry (default: true)
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


# Default configuration values
DEFAULT_FALKORDB_HOST = "localhost"
DEFAULT_FALKORDB_PORT = 6380
DEFAULT_DATABASE = "auto_build_memory"

# Graphiti state marker file (stores connection info and status)
GRAPHITI_STATE_MARKER = ".graphiti_state.json"

# Episode types for different memory categories
EPISODE_TYPE_SESSION_INSIGHT = "session_insight"
EPISODE_TYPE_CODEBASE_DISCOVERY = "codebase_discovery"
EPISODE_TYPE_PATTERN = "pattern"
EPISODE_TYPE_GOTCHA = "gotcha"


@dataclass
class GraphitiConfig:
    """Configuration for Graphiti memory integration."""
    enabled: bool = False
    openai_api_key: str = ""
    falkordb_host: str = DEFAULT_FALKORDB_HOST
    falkordb_port: int = DEFAULT_FALKORDB_PORT
    falkordb_password: str = ""
    database: str = DEFAULT_DATABASE
    telemetry_enabled: bool = True

    @classmethod
    def from_env(cls) -> "GraphitiConfig":
        """Create config from environment variables."""
        # Check if Graphiti is explicitly enabled
        enabled_str = os.environ.get("GRAPHITI_ENABLED", "").lower()
        enabled = enabled_str in ("true", "1", "yes")

        # Get OpenAI API key (required for Graphiti embeddings)
        openai_api_key = os.environ.get("OPENAI_API_KEY", "")

        # Get FalkorDB connection settings
        falkordb_host = os.environ.get(
            "GRAPHITI_FALKORDB_HOST",
            DEFAULT_FALKORDB_HOST
        )

        try:
            falkordb_port = int(os.environ.get(
                "GRAPHITI_FALKORDB_PORT",
                str(DEFAULT_FALKORDB_PORT)
            ))
        except ValueError:
            falkordb_port = DEFAULT_FALKORDB_PORT

        falkordb_password = os.environ.get("GRAPHITI_FALKORDB_PASSWORD", "")
        database = os.environ.get("GRAPHITI_DATABASE", DEFAULT_DATABASE)

        # Telemetry setting
        telemetry_str = os.environ.get("GRAPHITI_TELEMETRY_ENABLED", "true").lower()
        telemetry_enabled = telemetry_str not in ("false", "0", "no")

        return cls(
            enabled=enabled,
            openai_api_key=openai_api_key,
            falkordb_host=falkordb_host,
            falkordb_port=falkordb_port,
            falkordb_password=falkordb_password,
            database=database,
            telemetry_enabled=telemetry_enabled,
        )

    def is_valid(self) -> bool:
        """
        Check if config has minimum required values for operation.

        Graphiti requires:
        - GRAPHITI_ENABLED=true
        - OPENAI_API_KEY set (for embeddings)
        """
        return self.enabled and bool(self.openai_api_key)

    def get_connection_uri(self) -> str:
        """Get the FalkorDB connection URI."""
        if self.falkordb_password:
            return f"redis://:{self.falkordb_password}@{self.falkordb_host}:{self.falkordb_port}"
        return f"redis://{self.falkordb_host}:{self.falkordb_port}"


@dataclass
class GraphitiState:
    """State of Graphiti integration for an auto-build spec."""
    initialized: bool = False
    database: Optional[str] = None
    indices_built: bool = False
    created_at: Optional[str] = None
    last_session: Optional[int] = None
    episode_count: int = 0
    error_log: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "initialized": self.initialized,
            "database": self.database,
            "indices_built": self.indices_built,
            "created_at": self.created_at,
            "last_session": self.last_session,
            "episode_count": self.episode_count,
            "error_log": self.error_log[-10:],  # Keep last 10 errors
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GraphitiState":
        return cls(
            initialized=data.get("initialized", False),
            database=data.get("database"),
            indices_built=data.get("indices_built", False),
            created_at=data.get("created_at"),
            last_session=data.get("last_session"),
            episode_count=data.get("episode_count", 0),
            error_log=data.get("error_log", []),
        )

    def save(self, spec_dir: Path) -> None:
        """Save state to the spec directory."""
        marker_file = spec_dir / GRAPHITI_STATE_MARKER
        with open(marker_file, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, spec_dir: Path) -> Optional["GraphitiState"]:
        """Load state from the spec directory."""
        marker_file = spec_dir / GRAPHITI_STATE_MARKER
        if not marker_file.exists():
            return None

        try:
            with open(marker_file, "r") as f:
                return cls.from_dict(json.load(f))
        except (json.JSONDecodeError, IOError):
            return None

    def record_error(self, error_msg: str) -> None:
        """Record an error in the state."""
        self.error_log.append({
            "timestamp": datetime.now().isoformat(),
            "error": error_msg[:500],  # Limit error message length
        })
        # Keep only last 10 errors
        self.error_log = self.error_log[-10:]


def is_graphiti_enabled() -> bool:
    """
    Quick check if Graphiti integration is available.

    Returns True if:
    - GRAPHITI_ENABLED is set to true/1/yes
    - OPENAI_API_KEY is set (required for embeddings)
    """
    config = GraphitiConfig.from_env()
    return config.is_valid()


def get_graphiti_status() -> dict:
    """
    Get the current Graphiti integration status.

    Returns:
        Dict with status information:
            - enabled: bool
            - available: bool (has required dependencies)
            - host: str
            - port: int
            - database: str
            - reason: str (why unavailable if not available)
    """
    config = GraphitiConfig.from_env()

    status = {
        "enabled": config.enabled,
        "available": False,
        "host": config.falkordb_host,
        "port": config.falkordb_port,
        "database": config.database,
        "reason": "",
    }

    if not config.enabled:
        status["reason"] = "GRAPHITI_ENABLED not set to true"
        return status

    if not config.openai_api_key:
        status["reason"] = "OPENAI_API_KEY not set (required for embeddings)"
        return status

    status["available"] = True
    return status
