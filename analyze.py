#!/usr/bin/env python3
"""
Quick analysis script for Grothendieck transcription.

Usage:
    python analyze.py data/handwritten_119.pdf
    python analyze.py data/handwritten_119.pdf --model gemini-3-pro-preview
    python analyze.py data/handwritten_119.pdf --pages 1-5
    python analyze.py data/handwritten_119.pdf --delay 15  # For free tier (5 req/min)
"""

import json
import re
import time
from datetime import datetime
from pathlib import Path
import argparse

import fitz  # PyMuPDF
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from config import OUTPUT_DIR, TRANSCRIPTION_PROMPT
from models.gemini import transcribe_with_gemini, get_client

console = Console()


def transcribe_with_retry(image_bytes: bytes, model_name: str, thinking_level: str,
                          max_retries: int = 3) -> dict:
    """Transcribe with exponential backoff retry on rate limit errors."""
    for attempt in range(max_retries):
        result = transcribe_with_gemini(
            image_bytes=image_bytes,
            model_name=model_name,
            thinking_level=thinking_level,
        )

        if result["status"] == "success":
            return result

        # Check if it's a rate limit error
        error_msg = result.get("error", "")
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            # Extract retry delay from error message if available
            retry_match = re.search(r'retry in (\d+\.?\d*)s', error_msg.lower())
            if retry_match:
                wait_time = float(retry_match.group(1)) + 1  # Add 1s buffer
            else:
                wait_time = 15 * (attempt + 1)  # Exponential backoff: 15, 30, 45s

            console.print(f"[yellow]Rate limited. Waiting {wait_time:.1f}s before retry {attempt + 1}/{max_retries}...[/yellow]")
            time.sleep(wait_time)
        else:
            # Non-rate-limit error, don't retry
            return result

    return result  # Return last result after all retries


def pdf_to_images(pdf_path: Path, dpi: int = 150) -> list[dict]:
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


def main():
    parser = argparse.ArgumentParser(description="Analyze Grothendieck manuscript transcription")
    parser.add_argument("pdf_path", type=Path, help="Path to PDF file")
    parser.add_argument("--model", default="gemini-3-flash-preview",
                       choices=["gemini-3-flash-preview", "gemini-3-pro-preview"],
                       help="Model to use")
    parser.add_argument("--pages", default=None, help="Page range (e.g., '1-5' or '3')")
    parser.add_argument("--thinking", default="low", choices=["low", "medium", "high"],
                       help="Thinking level for Gemini 3")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests (seconds). Use 15+ for free tier.")
    parser.add_argument("--retries", type=int, default=3, help="Max retries on rate limit errors")
    parser.add_argument("--output", type=Path, default=None, help="Output file path")

    args = parser.parse_args()

    if not args.pdf_path.exists():
        console.print(f"[red]File not found: {args.pdf_path}[/red]")
        return

    console.print(f"\n[bold]Grothendieck OCR Analysis[/bold]")
    console.print(f"Model: {args.model}")
    console.print(f"Thinking level: {args.thinking}")
    console.print(f"File: {args.pdf_path}")

    # Convert PDF to images
    console.print(f"\nConverting PDF to images...")
    images = pdf_to_images(args.pdf_path)
    console.print(f"Total pages: {len(images)}")

    # Parse page range
    if args.pages:
        if "-" in args.pages:
            start, end = map(int, args.pages.split("-"))
            images = [img for img in images if start <= img["page_num"] <= end]
        else:
            page_num = int(args.pages)
            images = [img for img in images if img["page_num"] == page_num]
        console.print(f"Processing pages: {[img['page_num'] for img in images]}")

    # Ensure client is initialized before progress bar
    console.print(f"\nInitializing Gemini client...")
    try:
        get_client()
        console.print("[green]Client ready[/green]")
    except Exception as e:
        console.print(f"[red]Failed to initialize client: {e}[/red]")
        return

    # Transcribe
    results = {
        "pdf_name": args.pdf_path.name,
        "model": args.model,
        "thinking_level": args.thinking,
        "timestamp": datetime.now().isoformat(),
        "total_pages": len(images),
        "pages": []
    }

    console.print(f"\nTranscribing {len(images)} pages...")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Transcribing...", total=len(images))

        for img_data in images:
            page_num = img_data["page_num"]
            progress.update(task, description=f"Page {page_num}...")

            result = transcribe_with_retry(
                image_bytes=img_data["image_bytes"],
                model_name=args.model,
                thinking_level=args.thinking,
                max_retries=args.retries,
            )
            result["page_num"] = page_num
            results["pages"].append(result)

            progress.update(task, advance=1)
            time.sleep(args.delay)

    # Summary
    success = sum(1 for p in results["pages"] if p["status"] == "success")
    failed = sum(1 for p in results["pages"] if p["status"] == "error")

    console.print(f"\n[bold]Summary[/bold]")
    console.print(f"  Success: {success}")
    console.print(f"  Failed: {failed}")

    # Save results
    output_path = args.output or (OUTPUT_DIR / f"analysis_{args.pdf_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    console.print(f"\n[green]Results saved to: {output_path}[/green]")

    # Print first transcription as sample
    if results["pages"] and results["pages"][0]["status"] == "success":
        console.print(f"\n[bold]Sample (Page {results['pages'][0]['page_num']}):[/bold]")
        console.print("-" * 60)
        # Truncate to first 1000 chars
        sample = results["pages"][0]["transcription"][:1000]
        if len(results["pages"][0]["transcription"]) > 1000:
            sample += "\n... [truncated]"
        console.print(sample)


if __name__ == "__main__":
    main()
