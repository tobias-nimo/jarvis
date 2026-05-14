---
name: any-to-md
description: "Use this skill whenever the user wants to convert an unstructured document (PDF, DOCX, PPTX, XLSX, images, and more) to Markdown. Tries LiteParse first (fast, local, no cloud) and falls back to MistralOCR (cloud-based) for scanned PDFs, complex layouts, or math-heavy documents."
---

# Any → Markdown Conversion

Convert unstructured documents to Markdown. Two backends are available:

| Backend | When to use | Cost | Setup |
|---|---|---|---|
| **LiteParse** (default) | Text-based PDFs, Office docs, plain images, anything where local parsing is good enough | Free, local | Node 18+, `@llamaindex/liteparse` global, optional LibreOffice / ImageMagick |
| **MistralOCR** (fallback) | Scanned PDFs, complex layouts, math-heavy papers, low-quality scans, anything LiteParse mangles | Cloud (paid) | `MISTRAL_API_KEY` env var, `mistralai` Python pkg |

## Approach

1. **DEFAULT** → LiteParse via the `lit` CLI. Fast, free, runs locally.
2. **FALLBACK** → MistralOCR via `scripts/mistral_ocr.py`. Use when LiteParse output is poor or the file is a scan / image-heavy document.

---

## Default — LiteParse

### Setup check

```bash
# verify lit is installed
lit --version

# install if missing
npm i -g @llamaindex/liteparse

# Office docs need LibreOffice; images need ImageMagick (macOS):
brew install --cask libreoffice
brew install imagemagick
```

### Common commands

```bash
# Plain text extraction (default)
lit parse document.pdf

# Markdown-friendly JSON output to a file
lit parse document.pdf --format json -o output.json

# Specific page range
lit parse document.pdf --target-pages "1-5,10,15-20"

# Disable OCR for fast, text-only PDFs
lit parse document.pdf --no-ocr

# Higher DPI for better quality
lit parse document.pdf --dpi 300

# Batch a directory of PDFs
lit batch-parse ./input ./output --extension .pdf --recursive

# Render page screenshots (useful when layout matters)
lit screenshot document.pdf --pages "1-10" --dpi 300 --format png -o ./screenshots
```

### Key options

| Option | Description |
|---|---|
| `--format json\|text` | Output format (default `text`) |
| `-o <file>` | Save output to file |
| `--target-pages "1-5,10"` | Parse specific pages |
| `--no-ocr` | Disable OCR (faster, text-only PDFs) |
| `--ocr-language fra` | OCR language (ISO code) |
| `--ocr-server-url <url>` | Plug in EasyOCR/PaddleOCR/custom HTTP OCR backend |
| `--dpi <n>` | Rendering DPI (default 150; use 300 for high quality) |
| `--max-pages <n>` | Limit pages parsed |
| `--no-precise-bbox` | Faster, looser bounding boxes |
| `--skip-diagonal-text` | Ignore rotated/diagonal text |
| `--preserve-small-text` | Keep very small text |

### Repeated use — config file

Generate `liteparse.config.json` once, reuse with `--config`:

```json
{
  "ocrLanguage": "en",
  "ocrEnabled": true,
  "maxPages": 1000,
  "dpi": 150,
  "outputFormat": "json",
  "preciseBoundingBox": true,
  "skipDiagonalText": false,
  "preserveVerySmallText": false
}
```

```bash
lit parse document.pdf --config liteparse.config.json
```

### Supported input formats (LiteParse)

| Category | Formats |
|---|---|
| PDF | `.pdf` |
| Word | `.doc`, `.docx`, `.docm`, `.odt`, `.rtf` |
| PowerPoint | `.ppt`, `.pptx`, `.pptm`, `.odp` |
| Spreadsheets | `.xls`, `.xlsx`, `.xlsm`, `.ods`, `.csv`, `.tsv` |
| Images | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`, `.svg` |

Office docs auto-convert to PDF via LibreOffice; images via ImageMagick.

---

## Fallback — MistralOCR

Use when LiteParse output is empty, garbled, or the source is a scanned/image-heavy document. API limits: **max 50 MB per file, max 1,000 pages**.

### Setup check

```bash
# verify mistralai is installed
python -c "import mistralai; print('mistralai installed')"

# install if missing
pip install mistralai

# API key required
export MISTRAL_API_KEY=...
```

### Usage

```python
from scripts.mistral_ocr import to_md

# Writes <name>.md and figures/ into output_dir
md_path = to_md("paper.pdf", "out/paper")
print(md_path)  # → out/paper/paper.md
```

`to_md` writes:
- `<output_dir>/<name>.md` — concatenated markdown, page footers, image refs rewritten to `figures/`
- `<output_dir>/figures/` — extracted images decoded from base64

Optional args: `api_key=...` (defaults to `MISTRAL_API_KEY` env var), `model="mistral-ocr-latest"`.

### Supported input formats (MistralOCR)

- **Documents**: PDF, DOCX, DOC, PPTX, PPT, XLSX, CSV, TXT, EPUB, XML, RTF, ODT, BIB, FB2, IPYNB, TEX, OPML, man/troff pages
- **Images**: JPEG, PNG, AVIF, TIFF, GIF, HEIC/HEIF, BMP, WebP
