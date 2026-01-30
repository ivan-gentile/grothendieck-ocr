"""Gemini model transcription."""

import google.generativeai as genai
from config import GEMINI_API_KEY, TRANSCRIPTION_PROMPT


def setup_gemini(model_name: str = "gemini-2.0-flash"):
    """Initialize Gemini API."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set in environment")
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel(model_name)


def transcribe_with_gemini(
    image_bytes: bytes,
    model_name: str = "gemini-2.0-flash",
    prompt: str = TRANSCRIPTION_PROMPT,
) -> dict:
    """
    Transcribe a single page image using Gemini.

    Args:
        image_bytes: PNG image data
        model_name: Gemini model to use
        prompt: Transcription prompt

    Returns:
        dict with transcription, status, and metadata
    """
    model = setup_gemini(model_name)

    try:
        image_part = {
            "mime_type": "image/png",
            "data": image_bytes
        }

        response = model.generate_content(
            [prompt, image_part],
            generation_config={
                "temperature": 0.1,  # Low for accuracy
                "max_output_tokens": 8192
            }
        )

        return {
            "transcription": response.text if response.text else "[No text detected]",
            "status": "success",
            "model": model_name,
            "provider": "google"
        }

    except Exception as e:
        return {
            "transcription": None,
            "status": "error",
            "error": str(e),
            "model": model_name,
            "provider": "google"
        }
