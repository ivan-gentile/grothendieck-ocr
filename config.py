"""Configuration for Grothendieck OCR project."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Paths
PROJECT_ROOT = Path(__file__).parent
INPUT_DIR = Path(os.getenv("ARCHIVES_PATH", r"D:\documents-Orso\code\wilson\grothendieck_archives"))
OUTPUT_DIR = PROJECT_ROOT / "output"
PROGRESS_FILE = OUTPUT_DIR / "progress.json"

# Ensure output directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
(OUTPUT_DIR / "json").mkdir(exist_ok=True)
(OUTPUT_DIR / "text").mkdir(exist_ok=True)

# Model settings
MODELS = {
    "gemini-flash": {
        "name": "gemini-2.0-flash",
        "provider": "google",
        "cost_per_page": 0.002,
    },
    "gemini-pro": {
        "name": "gemini-1.5-pro",
        "provider": "google",
        "cost_per_page": 0.01,
    },
    "claude-opus": {
        "name": "claude-opus-4-5-20251101",
        "provider": "anthropic",
        "cost_per_page": 0.03,
    },
    "claude-sonnet": {
        "name": "claude-sonnet-4-20250514",
        "provider": "anthropic",
        "cost_per_page": 0.006,
    },
}

DEFAULT_MODEL = "gemini-flash"

# Processing settings
MAX_PAGES_PER_BATCH = 10
DELAY_BETWEEN_REQUESTS = 1.0  # seconds
IMAGE_DPI = 150

# Transcription prompt
TRANSCRIPTION_PROMPT = """You are an expert in transcribing mathematical manuscripts.

This is a scanned page from Alexandre Grothendieck's mathematical archives (1949-1991).
The documents contain:
- Handwritten mathematical notes in French
- Mathematical formulas, diagrams, and category theory
- Dense notation in algebraic geometry and homological algebra

Transcribe this page accurately:
1. Use LaTeX for ALL mathematical notation: $x^2$, $\\mathcal{O}_X$, $\\lim_{n \\to \\infty}$
2. Preserve French text exactly as written
3. Mark diagrams as: [DIAGRAM: brief description]
4. Mark illegible sections as: [illegible]
5. Preserve structure (headers, numbered items, etc.)

Begin transcription:"""
