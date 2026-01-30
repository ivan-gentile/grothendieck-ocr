---
title: "Transcribing Grothendieck's Handwriting with AI"
description: "Using vision LLMs to make 18,000 pages of handwritten mathematical genius machine-readable"
date: 2026-01-30
tags: [ai, ocr, mathematics, llm, vision]
language: en
draft: false
---

# Transcribing Grothendieck's Handwriting with AI

*How I discovered 18,000 pages of handwritten mathematical manuscripts and tried to make them readable with modern AI*

---

## The Mathematician's Mathematician

During my mathematics degree at the University of Groningen, one name kept surfacing with an almost mythical quality: **Alexandre Grothendieck**. Professors mentioned him in hushed tones. His work on algebraic geometry and category theory was foundational—the kind of mathematics that other mathematicians build their entire careers upon.

I knew he was brilliant. What I didn't know was how strange his life had been.

> "Grothendieck possessed an extraordinary ability to remove all unnecessary hypotheses and penetrate to the heart of a problem."
> — Pierre Deligne, Fields Medalist and Grothendieck's former student

## Labatut and the Fiction-Reality Boundary

It wasn't until I read Benjamin Labatut's *When We Cease to Understand the World* that I glimpsed the person behind the theorems. Labatut's book is a work of fiction—or rather, fiction woven around historical figures, blurring the line between what happened and what might have happened.

The chapter on Grothendieck was haunting. A man who revolutionized mathematics, then retreated from academic life entirely. A pacifist who walked away from prestigious positions over military funding. A recluse who spent his final decades in a small village in the Pyrenees, filling notebooks with what he called "La Clef des Songes" (The Key to Dreams).

But how much of it was true?

## Down the Wikipedia Rabbit Hole

I went to [Grothendieck's Wikipedia page](https://en.wikipedia.org/wiki/Alexander_Grothendieck) to separate fact from Labatut's imagination. Most of the broad strokes were accurate. The mathematical revolution. The political awakening. The withdrawal.

And then I found something unexpected: **the archives**.

After Grothendieck died in 2014, his family donated roughly 28,000 pages of handwritten manuscripts to the University of Montpellier. These weren't just mathematical notes—they were diaries, philosophical reflections, and yes, "La Clef des Songes."

The archives are available online at [grothendieck.umontpellier.fr](https://grothendieck.umontpellier.fr/archives-grothendieck/).[^ssl]

[^ssl]: The Montpellier website has an expired SSL certificate, so your browser may warn you. The site is legitimate—it's maintained by the university library. The [Istituto Grothendieck](https://igrothendieck.org/) in Piedmont, Italy also links to it from their transcription project at [csg.igrothendieck.org](https://csg.igrothendieck.org/).

I downloaded all 146 available PDFs. Four gigabytes of scanned pages. And then I tried to read them.

## The Problem: Genius-Level Illegibility

Grothendieck wrote in French, often mixing dense mathematical notation with philosophical prose. His handwriting is... challenging.

![Original handwritten page - table of contents](./screenshots/first_try.jpg)
*A relatively simple page: a table of contents for functional analysis topics. Even here, crossed-out text and abbreviations make transcription non-trivial.*

![Dense category theory page](./screenshots/p146_d119.png)
*A more typical page (p.145 from document 119): category theory with multiple layers of annotation, margin notes, and Grothendieck's characteristically dense notation.*

Even for French-speaking mathematicians, deciphering these manuscripts is slow, painstaking work. The Centre for Grothendieckian Studies (CSG) has been manually transcribing them, but it's a multi-year effort requiring deep mathematical expertise.

I wondered: could modern AI help?

## The Experiment

Vision-language models (VLMs) have improved dramatically in the past year. Gemini, GPT, and Claude can all process images and text together. They're trained on massive amounts of handwritten text and mathematical notation.

I built a simple pipeline:

1. **PDF to images**: Convert each page to a PNG at 150 DPI
2. **VLM transcription**: Send the image to a model with a prompt asking for faithful transcription in LaTeX
3. **Output**: Store JSON (with metadata) and plain LaTeX files

The prompt was minimal:

```
Can you extract the text from this?
```

The real question was: how good would the results be?

## Results: Comparing the Models

I tested three frontier models on the same pages from document 119 (one of the manuscripts the CSG is actively transcribing):

| Model | Transcription Quality | Math Accuracy | Handles Difficult Pages | Cost/Page |
|-------|----------------------|---------------|------------------------|-----------|
| **Gemini 3 Pro** | ⭐⭐⭐⭐⭐ | High | Yes | ~$0.01 |
| Claude Opus 4.5 | ⭐⭐⭐⭐ | Medium-High | Mostly | ~$0.03 |
| ChatGPT 5.2 | ⭐⭐⭐ | Medium | Struggles | ~$0.02 |

**Gemini 3 Pro emerged as the clear winner.**

### Test 1: Table of Contents Page (Simpler)

This page lists functional analysis topics (N°1 through N°7): rearrangements of functions, Weyl functions, spectral measures, determinants, operator ring inequalities.

**Gemini 3 Pro:**
![Gemini on simple page](./screenshots/gemini_firs_try.png)

Gemini provided:
- Full French transcription
- English translation
- **Notes on the handwriting** identifying crossed-out sections
- Mathematical context (noting $(A \in \bar{a})$ refers to operator algebra membership)

**Claude Opus 4.5:**
![Claude Opus on simple page](./screenshots/opus_first_try.png)

Claude produced clean output with proper ~~strikethrough~~ notation for crossed-out text, structured formatting, and topic identification. Slightly less contextual analysis than Gemini.

### Test 2: Dense Category Theory Page (Harder)

This is page 145 from document 119—dense category theory with multiple layers of annotation, margin notes, and corrections.

**Gemini 3 Pro:**
![Gemini on hard page](./screenshots/gemini_p146_d199.png)

Gemini handled this impressively:
- Identified the mathematical content (category equivalence between topological spaces and specific mappings)
- Preserved LaTeX notation: $\mathcal{C}$, $f: X \to Y$, $\underline{\text{Hom}}(y, y')$
- Caught the equivalence statement: $\mathcal{C} \rightleftarrows_{\approx} \mathcal{C}'$
- Noted the question at the bottom: "Quelles quantités/qualités obtient-on avec des feuilletages ???"
- Read the vertical margin text

**ChatGPT 5.2 Thinking:**
![ChatGPT on hard page](./screenshots/cgpt_first_try.png)

ChatGPT (on a similarly difficult page) struggled significantly:
```
Sei C eine C*-Algebra, [illegible] und [illegible] ...
[illegible] linearen [illegible] T_V [illegible] ...
```

Many `[illegible]` markers. The model was honest about its limitations—"I don't want to pretend I can recover the fully exact text"—but produced much less usable output.

### The Verdict

**Gemini 3 Pro** handles even the most challenging pages with remarkable accuracy. It provides not just transcription but *understanding*—identifying mathematical concepts, translating, and noting structural features like crossed-out text.

**Claude Opus** produces clean, well-formatted output and is honest about uncertainty, but offers slightly less mathematical context.

**ChatGPT 5.2** struggles with difficult handwriting and is more conservative, resulting in less complete transcriptions.

### A Note on "Understanding" vs. Confabulation

Something striking: the models recognize this is Grothendieck's work *without being told*. The prompt was simply "Can you extract the text from this?"—yet Gemini's output begins with "This transcription covers the handwritten notes from page 145 of Grothendieck's archives." The model inferred the author from handwriting style, mathematical content, and perhaps document structure.

This cuts both ways. The same pattern-matching that enables recognition can produce confident-sounding confabulation. Some of what the models output is likely correct; some is probably hallucinated, especially for heavily crossed-out or ambiguous passages. The models don't always mark uncertainty.

For transcription work, this is still enormously helpful—a human expert proofreading AI output is far faster than transcribing from scratch. But it means **every transcription needs verification**, not just spot-checking.

## Cost Analysis

At roughly **$0.01 per page** with Gemini 3 Pro, transcribing all 18,000 accessible pages would cost approximately **$180**.

Compare this to manual transcription:
- Expert verification: ~2 minutes per page minimum
- 18,000 pages = 600 hours = ~4 months full-time
- Assuming $50/hour for specialized mathematical labor = **$30,000**

AI transcription isn't perfect—it still needs human verification for mathematical accuracy. But it could reduce expert time from "writing from scratch" to "proofreading," potentially cutting the project timeline by 80%.

| Approach | Total Cost | Time |
|----------|-----------|------|
| Pure manual | ~$30,000 | 4+ months |
| AI + verification | ~$180 + reduced expert time | ~1 month |

## The Collaboration

I reached out to the Istituto Grothendieck and connected with **Olivia Caramello**, the Institute's president, and **Mateo Carmona**, their archivist. They're genuinely interested in exploring how AI could accelerate their transcription work.

The plan:
1. Run AI transcription on documents they're currently working on
2. Have experts verify and correct the output
3. Measure actual time savings vs. pure manual transcription
4. If successful, scale to the full archive

## What I Learned

1. **Vision LLMs are surprisingly good at handwritten text**—even challenging scripts like Grothendieck's
2. **Model choice matters enormously**—Gemini 3 Pro significantly outperformed alternatives on difficult pages
3. **Mathematical notation is the hardest part**—but top models handle it better than I expected
4. **The bottleneck isn't AI, it's verification**—you still need domain experts to confirm correctness
5. **Collaboration beats solo work**—connecting with people who care about the archive was more valuable than any technical improvement

## Try It Yourself

The transcription code is open source: [github.com/ivan-gentile/grothendieck-ocr](https://github.com/ivan-gentile/grothendieck-ocr)

```bash
pip install -r requirements.txt
python transcribe.py 119.pdf --model gemini-flash --pages 1-10
```

The archives themselves are freely available at [grothendieck.umontpellier.fr](https://grothendieck.umontpellier.fr/archives-grothendieck/).

---

*If you work on mathematical manuscript transcription or OCR for handwritten text, I'd love to hear from you. Reach out on [Twitter/X](https://twitter.com/ivogentile) or [LinkedIn](https://linkedin.com/in/ivangentile).*

---

## Related Reading

- [Grothendieck Circle](https://grothendieckcircle.org/) - community preserving his legacy
- [CSG Transcriptions](https://csg.igrothendieck.org/transcriptions/) - the manual transcription project
- [When We Cease to Understand the World](https://en.wikipedia.org/wiki/When_We_Cease_to_Understand_the_World) - Labatut's brilliant book
- [Olivia Caramello's paper on Topos](https://www.oliviacaramello.com/Papers/CaramelloTheUnifyingNotionOfTopos.pdf) - for the mathematically inclined
