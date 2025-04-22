"""Shared configuration constants."""

LMSTUDIO_HOST = "http://127.0.0.1:1234"  # Change if you exposed the server on another port
LMSTUDIO_MODEL = "local-model"             # Ignored by LM Studio but required by the API
MAX_MODEL_TOKENS = 8000               # Increased to allow for more detailed responses
TEMPERATURE = 0.2                         # Reduced for more consistent responses
