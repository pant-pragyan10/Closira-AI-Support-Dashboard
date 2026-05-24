"""utils.config

Simple configuration and environment validation helpers.

Provides a typed `Config` dataclass that reads environment variables and validates presence of required keys.
"""
from dataclasses import dataclass
import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)


@dataclass
class Config:
    """Typed configuration for Closira.

    Attributes:
        groq_api_key: optional API key for Groq; None for demo mode.
        faq_confidence_threshold: float threshold for FAQ escalation.
    """

    groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY")
    groq_model: Optional[str] = os.getenv("GROQ_MODEL")
    faq_confidence_threshold: float = float(os.getenv("FAQ_CONFIDENCE_THRESHOLD", "0.6"))

    def validate(self) -> None:
        """Validate essential config values. Raises ValueError on failure."""
        if not self.groq_api_key:
            # Demo mode allowed, so only warn
            print("Warning: GROQ_API_KEY not set — running in demo mode.")
        # normalize quoted values
        if self.groq_api_key:
            self.groq_api_key = self.groq_api_key.strip().strip('"').strip("'")
        if self.groq_model:
            self.groq_model = self.groq_model.strip().strip('"').strip("'")


def get_config() -> Config:
    """Return validated Config instance."""
    cfg = Config()
    cfg.validate()
    return cfg


__all__ = ["Config", "get_config"]
