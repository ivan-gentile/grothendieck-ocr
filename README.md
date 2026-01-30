# Grothendieck Archives OCR

Using vision LLMs to transcribe Alexandre Grothendieck's handwritten mathematical manuscripts into machine-readable text (LaTeX).

## Background

The [Grothendieck Archives](https://grothendieck.umontpellier.fr/) contain ~28,000 pages of handwritten mathematical manuscripts, including foundational work in algebraic geometry. These are notoriously difficult to read, even for mathematicians.

This project uses multimodal LLMs (Gemini, Claude) to produce transcriptions that can then be verified by domain experts.

**Collaboration**: Working with [Istituto Grothendieck](https://igrothendieck.org/) and their [transcription project](https://csg.igrothendieck.org/transcriptions/).

## Quick Start

```bash
# Clone and setup
git clone https://github.com/ivogentile/grothendieck-ocr.git
cd grothendieck-ocr

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your Gemini API key

# Download archives (optional - 4GB)
python download_grothendieck.py

# Transcribe a document
python transcribe.py --input grothendieck_archives/119.pdf --output output/
```

## Project Structure

```
grothendieck-ocr/
├── download_grothendieck.py  # Download PDFs from Montpellier archive
├── transcribe.py             # Main transcription script
├── config.py                 # Configuration and paths
├── models/                   # Model-specific transcription code
│   ├── gemini.py
│   └── claude.py
├── output/                   # Transcription outputs
│   ├── json/                 # Full transcription with metadata
│   └── text/                 # Plain text/LaTeX output
├── grothendieck_archives/    # Downloaded PDFs (gitignored)
└── tests/                    # Test suite
```

## Features

- **Multi-model support**: Gemini 2.0 Flash, Claude Opus 4.5
- **LaTeX output**: Mathematical notation preserved in LaTeX format
- **Progress tracking**: Resume interrupted transcriptions
- **Batch processing**: Process multiple documents efficiently
- **Quality metrics**: Track transcription confidence and errors

## Cost Estimate

| Model | Cost/Page | 10k Pages |
|-------|-----------|-----------|
| Gemini 2.0 Flash | ~$0.002 | ~$20 |
| Claude Opus 4.5 | ~$0.03 | ~$300 |

The bottleneck is human verification, not API cost.

## Output Format

**JSON** (full metadata):
```json
{
  "pdf_name": "119.pdf",
  "page_num": 1,
  "transcription": "Soit $X$ un schéma...",
  "model": "gemini-2.0-flash",
  "confidence": 0.92,
  "timestamp": "2026-01-30T12:00:00Z"
}
```

**Text** (LaTeX-ready):
```latex
% Transcription of 119.pdf, Page 1
% Model: gemini-2.0-flash

Soit $X$ un schéma de type fini sur un corps $k$...
```

## Related

- [Grothendieck Archives (Montpellier)](https://grothendieck.umontpellier.fr/)
- [Istituto Grothendieck](https://igrothendieck.org/)
- [CSG Transcriptions](https://csg.igrothendieck.org/transcriptions/)
- [Blog post: Transcribing Grothendieck with AI](https://thinkgentile.com/posts/grothendieck-ocr)

## License

MIT
