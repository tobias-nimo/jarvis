# src/tools/mistral_ocr.py

"""
Process a document (text or image) with Mistral OCR and save the output
as a folder inside .workspace/docs/ containing:
  - <name>.md       : full concatenated markdown with image refs and page numbers
  - figures/        : every extracted image, decoded from base64

API LIMITS: Files must not exceed 50 MB and 1,000 pages.
"""

import base64
from pathlib import Path

from langchain.tools import tool
from langchain_core.tools import ToolException
from mistralai.client import Mistral

from ..config import settings


# ── MIME type map for base64 data-URIs ────────────────────────────────────────

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

def detect_document_type(path: Path) -> str:
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


def build_document_payload(path: Path, doc_type: str) -> dict:
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
    else:
        media_type = DOCUMENT_MIME_TYPES[ext]
        return {
            "type": "document_url",
            "document_url": f"data:{media_type};base64,{b64}",
        }


def save_images(pages, output_dir: Path) -> None:
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

            # Strip any leading "data:...;base64," prefix the API might add
            raw_b64 = img.image_base64
            if "," in raw_b64:
                raw_b64 = raw_b64.split(",", 1)[1]

            dest = figures_dir / img.id
            dest.write_bytes(base64.b64decode(raw_b64))


def build_markdown(pages) -> str:
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
        # Rewrite image references to point to figures/ subdirectory
        for img in page.images:
            md = md.replace(f"]({img.id})", f"](figures/{img.id})")
        md += f"\n\n*Page {i} of {total}*"
        parts.append(md)
    return "\n\n---\n\n".join(parts)


# ── Tool ──────────────────────────────────────────────────────────────────────

@tool
def to_md(doc_path: str) -> str:
    """
    Runs OCR pipeline on local document or image.
    Saves a Markdown file and extracted images into
    .workspace/docs/<name>/ inside the project root.

    Supported input formats:
      - Documents: PDF, DOCX, DOC, PPTX, PPT, XLSX, CSV, TXT, EPUB, XML,
                   RTF, ODT, BIB, FB2, IPYNB, TEX, OPML, man/troff pages.
      - Images: JPEG, PNG, AVIF, TIFF, GIF, HEIC/HEIF, BMP, WebP.

    API limits: max 50 MB per file, max 1,000 pages.

    Args:
        doc_path: Absolute or relative path to the file to process.

    Returns:
        The absolute path to the output folder as a string.
    """
    try:
        path = Path(doc_path).expanduser()
        if not path.is_absolute():
            path = Path(settings.project_root) / path
        path = path.resolve()

        if not path.exists():
            raise ToolException(f"File not found: {path}")

        # Output folder inside the workspace directory
        workspace = Path(settings.project_root) / ".workspace" / "docs"
        output_dir = workspace / path.stem
        md_path = output_dir / f"{path.stem}.md"

        # Skip if already converted
        if md_path.exists():
            return str(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        # Call Mistral API
        client = Mistral(api_key=settings.mistral_api_key)

        doc_type = detect_document_type(path)
        document = build_document_payload(path, doc_type)

        response = client.ocr.process(
            model="mistral-ocr-latest",
            document=document,
            include_image_base64=True,  # required to get base64 image data back
        )

        # Save outputs
        save_images(response.pages, output_dir)
        md_path.write_text(build_markdown(response.pages), encoding="utf-8")

        return str(output_dir)

    except ToolException:
        raise
    except Exception as e:
        raise ToolException(f"to_md failed: {e}")


to_md.handle_tool_error = True