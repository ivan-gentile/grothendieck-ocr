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

- **Multi-model support**: Gemini 3 Flash/Pro, Claude Opus 4.5
- **Thinking mode**: Configurable reasoning depth (low/medium/high) for Gemini 3
- **LaTeX output**: Mathematical notation preserved in LaTeX format
- **Progress tracking**: Resume interrupted transcriptions
- **Batch processing**: Process multiple documents efficiently
- **Rate limit handling**: Automatic retry with exponential backoff

## Cost Estimate

| Model | Cost/Page | 18k Pages |
|-------|-----------|-----------|
| Gemini 3 Flash | ~$0.01 | ~$180 |
| Gemini 3 Pro | ~$0.03 | ~$540 |
| Claude Opus 4.5 | ~$0.03 | ~$540 |

The bottleneck is human verification, not API cost.

## Output Format

**JSON** (full metadata):
```json
{
  "pdf_name": "119.pdf",
  "page_num": 1,
  "transcription": "Soit $\\mathcal{C}$ la catégorie des esp. top...",
  "model": "gemini-3-flash-preview",
  "provider": "google",
  "thinking_level": "low",
  "status": "success"
}
```

**Text** (LaTeX-ready):
```latex
% Transcription of 119.pdf, Page 1
% Model: gemini-3-flash-preview

Soit $\mathcal{C}$ la catégorie des esp. top. localement sur $X$...
```

## Related

- [Grothendieck Archives (Montpellier)](https://grothendieck.umontpellier.fr/)
- [Istituto Grothendieck](https://igrothendieck.org/)
- [CSG Transcriptions](https://csg.igrothendieck.org/transcriptions/)
- [Blog post: Transcribing Grothendieck with AI](https://thinkgentile.com/posts/grothendieck-ocr)

## License

MIT
