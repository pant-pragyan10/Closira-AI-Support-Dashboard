import os
import json
from typing import Optional
from utils.logger import ConversationLogger
from utils.config import get_config

# Use official Groq Python SDK
try:
    from groq import Groq
except Exception:
    Groq = None


class GroqClient:
    """Minimal Groq SDK wrapper.

    Uses the official `groq` SDK. No manual REST probing, no custom endpoints.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        cfg = get_config()
        self.api_key = api_key or cfg.groq_api_key
        self.model = model or cfg.groq_model or "llama-3.3-70b-versatile"
        self.logger = ConversationLogger("logs/groq_errors.json")
        self.sdk_available = Groq is not None
        self.client = None
        if self.api_key and self.sdk_available:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                self.logger.log({"event": "sdk_init_error", "error": str(e)})

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        """Call the Groq SDK chat completions and return the raw content string.

        Returns the model content string on success. On failure raises Exception.
        """
        if not self.sdk_available:
            raise RuntimeError("Groq SDK not installed")
        if not self.client:
            raise RuntimeError("Groq client not initialized; check GROQ_API_KEY")

        try:
            # Build messages list
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            # Use the official SDK chat API
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
            )
            # Attempt to access response content
            try:
                content = resp.choices[0].message.content
            except Exception:
                # Fallback to string repr
                content = str(resp)
            # Log success snippet
            self.logger.log({"event": "sdk_call_success", "model": self.model, "response_snippet": (content or "")[:2000]})
            return content
        except Exception as e:
            self.logger.log({"event": "sdk_call_error", "error": str(e)})
            raise

    def validate_model(self) -> tuple:
        """Lightweight model/API validation returning (ok: bool, reason: str).

        Uses a single SDK call to ensure the client and model are reachable. Returns (True, "") on success,
        otherwise (False, <error message>).
        """
        if not self.sdk_available:
            return False, "groq-sdk-not-installed"
        if not self.client:
            return False, "groq-client-not-initialized"
        try:
            # Use a minimal chat call as a sanity check (very small prompt)
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": "You are a responder."}, {"role": "user", "content": "Ping"}],
                temperature=0.0,
            )
            # If we got a response object, consider it OK
            return True, ""
        except Exception as e:
            return False, str(e)
