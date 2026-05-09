"""
scripts/mistral_ocr.py — helpers for the any-to-md skill (MistralOCR pipeline).

Usage:
    from scripts.mistral_ocr import to_md

    out_dir = to_md("path/to/document.pdf", "path/to/output_dir")
"""

import base64
import os
from pathlib import Path

from mistralai.client import Mistral


# ── MIME type maps for base64 data-URIs ───────────────────────────────────────

IMAGE_MIME_TYPES: dict[str, str] = {
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png":  "image/png",
    ".avif": "image/avif",
    ".tiff": "image/tiff",
    ".tif":  "image/tiff",
    ".gif":  "image/gif",
    ".heic": "image/heic",
    ".heif": "image/heif",
    ".bmp":  "image/bmp",
    ".webp": "image/webp",
}

DOCUMENT_MIME_TYPES: dict[str, str] = {
    ".pdf":   "application/pdf",
    ".docx":  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc":   "application/msword",
    ".pptx":  "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".ppt":   "application/vnd.ms-powerpoint",
    ".xlsx":  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".csv":   "text/csv",
    ".txt":   "text/plain",
    ".epub":  "application/epub+zip",
    ".xml":   "application/xml",
    ".rtf":   "application/rtf",
    ".odt":   "application/vnd.oasis.opendocument.text",
    ".bib":   "text/plain",
    ".fb2":   "application/xml",
    ".ipynb": "application/json",
    ".tex":   "text/x-tex",
    ".opml":  "text/x-opml",
    ".1":     "text/troff",
    ".man":   "text/troff",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _detect_document_type(path: Path) -> str:
    """Return the OCR document type string expected by the Mistral API."""
    ext = path.suffix.lower()

    if ext in IMAGE_MIME_TYPES:
        return "image_url"
    if ext in DOCUMENT_MIME_TYPES:
        return "document_url"

    raise ValueError(
        f"Unsupported file extension '{ext}' for '{path.name}'. "
        f"Supported image extensions: {sorted(IMAGE_MIME_TYPES)}, "
        f"supported document extensions: {sorted(DOCUMENT_MIME_TYPES)}."
    )


def _build_document_payload(path: Path, doc_type: str) -> dict:
    """
    Build the `document` dict for client.ocr.process().
    Files are always base64-encoded so no public URL is required.
    """
    ext = path.suffix.lower()
    raw = path.read_bytes()
    b64 = base64.standard_b64encode(raw).decode()

    if doc_type == "image_url":
        media_type = IMAGE_MIME_TYPES[ext]
        return {
            "type": "image_url",
            "image_url": f"data:{media_type};base64,{b64}",
        }
    media_type = DOCUMENT_MIME_TYPES[ext]
    return {
        "type": "document_url",
        "document_url": f"data:{media_type};base64,{b64}",
    }


def _save_images(pages, output_dir: Path) -> None:
    """
    Decode every image embedded in the OCR response and write it to
    output_dir/figures/ using the image id as the filename (e.g. img-0.jpeg).
    """
    figures_dir = output_dir / "figures"
    figures_dir.mkdir(exist_ok=True)

    for page in pages:
        for img in page.images:
            if not img.image_base64:
                continue

            raw_b64 = img.image_base64
            if "," in raw_b64:
                raw_b64 = raw_b64.split(",", 1)[1]

            dest = figures_dir / img.id
            dest.write_bytes(base64.b64decode(raw_b64))


def _build_markdown(pages) -> str:
    """
    Concatenate per-page markdown into a single document.
    Image references are rewritten to point to the figures/ subdirectory.
    Each page ends with a 'Page n of N' footer.
    """
    total = len(pages)
    parts = []
    for i, page in enumerate(pages, 1):
        md = (page.markdown or "").strip()
        if not md:
            continue
        for img in page.images:
            md = md.replace(f"]({img.id})", f"](figures/{img.id})")
        md += f"\n\n*Page {i} of {total}*"
        parts.append(md)
    return "\n\n---\n\n".join(parts)


# ── Main conversion function ──────────────────────────────────────────────────

def to_md(
    doc_path: str,
    output_dir: str,
    api_key: str | None = None,
    model: str = "mistral-ocr-latest",
) -> str:
    """
    Run Mistral OCR on a local document or image.

    Writes to `output_dir`:
      - <name>.md   : full concatenated markdown with page numbers
      - figures/    : every extracted image, decoded from base64

    API limits: max 50 MB per file, max 1,000 pages.

    Args:
        doc_path:   Absolute or relative path to the file to process.
        output_dir: Directory to write the .md file and figures/ folder into.
                    Created if it does not exist.
        api_key:    Mistral API key. Defaults to env var MISTRAL_API_KEY.
        model:      Mistral OCR model name.

    Returns:
        Absolute path to the written .md file.

    Supported input formats:
        Documents: PDF, DOCX, DOC, PPTX, PPT, XLSX, CSV, TXT, EPUB, XML,
                   RTF, ODT, BIB, FB2, IPYNB, TEX, OPML, man/troff pages.
        Images:    JPEG, PNG, AVIF, TIFF, GIF, HEIC/HEIF, BMP, WebP.
    """
    path = Path(doc_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    out_dir = Path(output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / f"{path.stem}.md"

    key = api_key or os.environ.get("MISTRAL_API_KEY")
    if not key:
        raise ValueError("Mistral API key not provided (set MISTRAL_API_KEY or pass api_key=).")

    client = Mistral(api_key=key)

    doc_type = _detect_document_type(path)
    document = _build_document_payload(path, doc_type)

    response = client.ocr.process(
        model=model,
        document=document,
        include_image_base64=True,
    )

    _save_images(response.pages, out_dir)
    md_path.write_text(_build_markdown(response.pages), encoding="utf-8")

    return str(md_path)
