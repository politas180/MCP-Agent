"""Shared configuration constants."""

LMSTUDIO_HOST = "http://127.0.0.1:1234"  # Change if you exposed the server on another port
LMSTUDIO_MODEL = "Qwen2.5-7B-Instruct-1M-Q4_K_M"  # Specify the actual model name
MAX_MODEL_TOKENS = 1024                   # Reduced to prevent token repetition issues
TEMPERATURE = 0.7                         # Increased for more varied responses
TOP_P = 0.9                               # Add top_p sampling to improve output quality
FREQUENCY_PENALTY = 0.5                   # Add frequency penalty to reduce repetition
PRESENCE_PENALTY = 0.5                    # Add presence penalty to encourage diversity
