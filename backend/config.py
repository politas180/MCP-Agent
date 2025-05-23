"""Shared configuration constants."""

LMSTUDIO_HOST = "http://127.0.0.1:1234"  # Change if you exposed the server on another port
LMSTUDIO_MODEL = "local-model"             # Ignored by LM Studio but required by the API

# Default LLM settings. These can be overridden by session-specific configurations.
DEFAULT_MAX_MODEL_TOKENS = 8000      # Default context window size (max tokens)
DEFAULT_TEMPERATURE = 0.2            # Default temperature for LLM responses
