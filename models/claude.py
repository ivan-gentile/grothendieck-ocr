"""Claude model transcription."""

import base64
import anthropic
from config import ANTHROPIC_API_KEY, TRANSCRIPTION_PROMPT


def transcribe_with_claude(
    image_bytes: bytes,
    model_name: str = "claude-sonnet-4-20250514",
    prompt: str = TRANSCRIPTION_PROMPT,
) -> dict:
    """
    Transcribe a single page image using Claude.

    Args:
        image_bytes: PNG image data
        model_name: Claude model to use
        prompt: Transcription prompt

    Returns:
        dict with transcription, status, and metadata
    """
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set in environment")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    try:
        # Encode image to base64
        image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

        message = client.messages.create(
            model=model_name,
            max_tokens=8192,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )

        transcription = message.content[0].text if message.content else "[No text detected]"

        return {
            "transcription": transcription,
            "status": "success",
            "model": model_name,
            "provider": "anthropic"
        }

    except Exception as e:
        return {
            "transcription": None,
            "status": "error",
            "error": str(e),
            "model": model_name,
            "provider": "anthropic"
        }
