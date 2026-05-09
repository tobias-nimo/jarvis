# src/middleware/image_content.py

"""
Middleware that intercepts view_image tool calls and rewrites the
ToolMessage with multimodal content blocks so the LLM sees the image
directly in its conversation context.
"""

import base64
from pathlib import Path

from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage

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

TOOL_NAME = "view_image"
PATH_PREFIX = "image_path:"


@wrap_tool_call
async def image_content_middleware(request, handler):
    """Rewrite view_image tool responses with inline image content blocks."""
    result = await handler(request)

    # Only intercept view_image calls that succeeded
    if request.tool_call["name"] != TOOL_NAME:
        return result
    if not isinstance(result, ToolMessage) or result.status != "success":
        return result

    content = result.content
    if not isinstance(content, str) or not content.startswith(PATH_PREFIX):
        return result

    path = Path(content.removeprefix(PATH_PREFIX))
    if not path.exists():
        result.content = f"Error: file no longer exists at {path}"
        result.status = "error"
        return result

    ext = path.suffix.lower()
    mime = IMAGE_MIME_TYPES.get(ext)
    if not mime:
        result.content = f"Error: unsupported image type '{ext}'"
        result.status = "error"
        return result

    b64 = base64.standard_b64encode(path.read_bytes()).decode()

    result.content = [
        {"type": "text", "text": f"Image loaded: {path.name}"},
        {"type": "image", "base64": b64, "mime_type": mime},
    ]
    return result
