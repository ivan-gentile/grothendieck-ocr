"""Gemini 3 model transcription using the new google.genai SDK."""

from google import genai
from google.genai import types
from config import GEMINI_API_KEY, TRANSCRIPTION_PROMPT

# Initialize client once
_client = None

def get_client():
    """Get or create the Gemini client."""
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in environment")
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def transcribe_with_gemini(
    image_bytes: bytes,
    model_name: str = "gemini-3-flash-preview",
    prompt: str = TRANSCRIPTION_PROMPT,
    thinking_level: str = "low",
) -> dict:
    """
    Transcribe a single page image using Gemini 3.

    Args:
        image_bytes: PNG image data
        model_name: Gemini model to use (gemini-3-pro-preview or gemini-3-flash-preview)
        prompt: Transcription prompt
        thinking_level: "low", "medium", or "high" (controls reasoning depth)

    Returns:
        dict with transcription, status, and metadata
    """
    client = get_client()

    try:
        # Create the image part
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/png"
        )

        # Configure generation with Gemini 3 settings
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level=thinking_level),
            # Temperature 1.0 is recommended for Gemini 3
        )

        response = client.models.generate_content(
            model=model_name,
            contents=[prompt, image_part],
            config=config,
        )

        transcription = response.text if response.text else "[No text detected]"

        return {
            "transcription": transcription,
            "status": "success",
            "model": model_name,
            "provider": "google",
            "thinking_level": thinking_level,
        }

    except Exception as e:
        return {
            "transcription": None,
            "status": "error",
            "error": str(e),
            "model": model_name,
            "provider": "google",
        }


def transcribe_pdf_with_gemini(
    pdf_bytes: bytes,
    model_name: str = "gemini-3-flash-preview",
    prompt: str = TRANSCRIPTION_PROMPT,
    thinking_level: str = "low",
    media_resolution: str = "media_resolution_medium",
) -> dict:
    """
    Transcribe an entire PDF using Gemini 3's native PDF support.

    For PDFs, media_resolution_medium (560 tokens) is recommended.
    Higher resolutions rarely improve OCR for standard documents.

    Args:
        pdf_bytes: PDF file bytes
        model_name: Gemini model to use
        prompt: Transcription prompt
        thinking_level: "low", "medium", or "high"
        media_resolution: Resolution setting for the PDF

    Returns:
        dict with transcription, status, and metadata
    """
    client = get_client()

    try:
        # Create PDF part with media resolution
        # Note: media_resolution requires v1alpha API
        pdf_part = types.Part.from_bytes(
            data=pdf_bytes,
            mime_type="application/pdf"
        )

        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level=thinking_level),
        )

        response = client.models.generate_content(
            model=model_name,
            contents=[prompt, pdf_part],
            config=config,
        )

        transcription = response.text if response.text else "[No text detected]"

        return {
            "transcription": transcription,
            "status": "success",
            "model": model_name,
            "provider": "google",
            "thinking_level": thinking_level,
        }

    except Exception as e:
        return {
            "transcription": None,
            "status": "error",
            "error": str(e),
            "model": model_name,
            "provider": "google",
        }
