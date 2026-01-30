#!/usr/bin/env python3
"""
Grothendieck Archives OCR - Main transcription script.

Usage:
    python transcribe.py --input 119.pdf
    python transcribe.py --input grothendieck_archives/119.pdf --model claude-sonnet
    python transcribe.py --input grothendieck_archives/ --pages 1-10
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

from config import (
    INPUT_DIR,
    OUTPUT_DIR,
    PROGRESS_FILE,
    MODELS,
    DEFAULT_MODEL,
    IMAGE_DPI,
    DELAY_BETWEEN_REQUESTS,
)
from models import transcribe_with_gemini, transcribe_with_claude

app = typer.Typer(help="Transcribe Grothendieck manuscripts using vision LLMs")
console = Console()


def pdf_to_images(pdf_path: Path, dpi: int = IMAGE_DPI) -> list[dict]:
    """Convert PDF pages to PNG images."""
    doc = fitz.open(pdf_path)
    images = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        images.append({
            "page_num": page_num + 1,
            "image_bytes": pix.tobytes("png")
        })

    doc.close()
    return images


def load_progress() -> dict:
    """Load progress from file."""
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    return {"completed": {}, "failed": [], "last_updated": None}


def save_progress(progress: dict):
    """Save progress to file."""
    progress["last_updated"] = datetime.now().isoformat()
    PROGRESS_FILE.write_text(json.dumps(progress, indent=2), encoding="utf-8")


def transcribe_page(image_bytes: bytes, model_key: str) -> dict:
    """Transcribe a single page using the specified model."""
    model_config = MODELS[model_key]

    if model_config["provider"] == "google":
        return transcribe_with_gemini(image_bytes, model_config["name"])
    elif model_config["provider"] == "anthropic":
        return transcribe_with_claude(image_bytes, model_config["name"])
    else:
        raise ValueError(f"Unknown provider: {model_config['provider']}")


def save_results(results: dict, pdf_name: str):
    """Save transcription results to JSON and text files."""
    base_name = Path(pdf_name).stem

    # JSON output
    json_path = OUTPUT_DIR / "json" / f"{base_name}.json"
    json_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    # Text/LaTeX output
    txt_path = OUTPUT_DIR / "text" / f"{base_name}.tex"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"% Transcription of {pdf_name}\n")
        f.write(f"% Model: {results.get('model', 'unknown')}\n")
        f.write(f"% Date: {results.get('timestamp', 'unknown')}\n")
        f.write(f"% Total pages: {results.get('total_pages', 0)}\n")
        f.write("%" + "=" * 79 + "\n\n")

        for page in results.get("pages", []):
            f.write(f"\n% --- Page {page['page_num']} ---\n\n")
            if page["status"] == "success":
                f.write(page["transcription"])
            else:
                f.write(f"% [ERROR: {page.get('error', 'Unknown')}]")
            f.write("\n")

    return json_path, txt_path


@app.command()
def transcribe(
    input_path: Path = typer.Argument(
        ...,
        help="PDF file or directory to transcribe"
    ),
    model: str = typer.Option(
        DEFAULT_MODEL,
        "--model", "-m",
        help=f"Model to use: {', '.join(MODELS.keys())}"
    ),
    pages: Optional[str] = typer.Option(
        None,
        "--pages", "-p",
        help="Page range to transcribe (e.g., '1-10' or '5')"
    ),
    resume: bool = typer.Option(
        True,
        "--resume/--no-resume",
        help="Resume from previous progress"
    ),
    delay: float = typer.Option(
        DELAY_BETWEEN_REQUESTS,
        "--delay", "-d",
        help="Delay between API calls (seconds)"
    ),
):
    """Transcribe PDF documents using vision LLMs."""

    # Validate model
    if model not in MODELS:
        console.print(f"[red]Unknown model: {model}[/red]")
        console.print(f"Available models: {', '.join(MODELS.keys())}")
        raise typer.Exit(1)

    # Resolve input path
    if not input_path.is_absolute():
        # Check if it's in the archives directory
        if (INPUT_DIR / input_path).exists():
            input_path = INPUT_DIR / input_path
        elif not input_path.exists():
            console.print(f"[red]File not found: {input_path}[/red]")
            raise typer.Exit(1)

    # Get list of PDFs to process
    if input_path.is_dir():
        pdf_files = sorted(input_path.glob("*.pdf"))
    else:
        pdf_files = [input_path]

    if not pdf_files:
        console.print("[red]No PDF files found[/red]")
        raise typer.Exit(1)

    # Parse page range
    start_page, end_page = 1, None
    if pages:
        if "-" in pages:
            parts = pages.split("-")
            start_page = int(parts[0])
            end_page = int(parts[1]) if parts[1] else None
        else:
            start_page = int(pages)
            end_page = int(pages)

    # Load progress
    progress = load_progress() if resume else {"completed": {}, "failed": []}

    # Display info
    model_config = MODELS[model]
    console.print(f"\n[bold]Grothendieck OCR[/bold]")
    console.print(f"Model: {model} ({model_config['name']})")
    console.print(f"Files: {len(pdf_files)}")
    console.print(f"Cost estimate: ~${model_config['cost_per_page']}/page\n")

    total_success = 0
    total_failed = 0

    for pdf_path in pdf_files:
        pdf_name = pdf_path.name
        console.print(f"\n[bold blue]Processing: {pdf_name}[/bold blue]")

        # Check if already completed
        if pdf_name in progress["completed"] and resume:
            console.print(f"  [dim]Skipping (already completed)[/dim]")
            continue

        try:
            # Convert to images
            console.print(f"  Converting to images (DPI={IMAGE_DPI})...")
            images = pdf_to_images(pdf_path)
            total_pages = len(images)

            # Filter by page range
            if end_page:
                images = [img for img in images if start_page <= img["page_num"] <= end_page]
            else:
                images = [img for img in images if img["page_num"] >= start_page]

            console.print(f"  Pages to process: {len(images)} of {total_pages}")

            # Transcribe
            results = {
                "pdf_name": pdf_name,
                "total_pages": total_pages,
                "pages_processed": len(images),
                "model": model,
                "timestamp": datetime.now().isoformat(),
                "pages": []
            }

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as prog:
                task = prog.add_task("Transcribing...", total=len(images))

                for img_data in images:
                    result = transcribe_page(img_data["image_bytes"], model)
                    result["page_num"] = img_data["page_num"]
                    results["pages"].append(result)

                    if result["status"] == "success":
                        total_success += 1
                    else:
                        total_failed += 1

                    prog.update(task, advance=1)
                    time.sleep(delay)

            # Save results
            json_path, txt_path = save_results(results, pdf_name)
            console.print(f"  [green]Saved:[/green] {json_path.name}, {txt_path.name}")

            # Update progress
            progress["completed"][pdf_name] = {
                "timestamp": datetime.now().isoformat(),
                "pages": len(images),
                "model": model
            }
            save_progress(progress)

        except Exception as e:
            console.print(f"  [red]Error: {e}[/red]")
            progress["failed"].append({
                "file": pdf_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            save_progress(progress)

    # Summary
    console.print("\n" + "=" * 50)
    console.print("[bold]Summary[/bold]")
    console.print(f"  Pages transcribed: {total_success}")
    console.print(f"  Pages failed: {total_failed}")
    console.print(f"  Output: {OUTPUT_DIR}")


@app.command()
def status():
    """Show transcription progress status."""
    progress = load_progress()

    table = Table(title="Transcription Progress")
    table.add_column("Document", style="cyan")
    table.add_column("Pages", justify="right")
    table.add_column("Model")
    table.add_column("Date")

    for pdf_name, info in progress.get("completed", {}).items():
        table.add_row(
            pdf_name,
            str(info.get("pages", "?")),
            info.get("model", "?"),
            info.get("timestamp", "?")[:10]
        )

    console.print(table)

    if progress.get("failed"):
        console.print(f"\n[red]Failed: {len(progress['failed'])} documents[/red]")


@app.command()
def list_models():
    """List available models and their costs."""
    table = Table(title="Available Models")
    table.add_column("Key", style="cyan")
    table.add_column("Model Name")
    table.add_column("Provider")
    table.add_column("Cost/Page", justify="right")

    for key, config in MODELS.items():
        table.add_row(
            key,
            config["name"],
            config["provider"],
            f"${config['cost_per_page']:.3f}"
        )

    console.print(table)


if __name__ == "__main__":
    app()
