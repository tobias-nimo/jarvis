# src/tools/view_image.py

"""
Thin validation tool for viewing images directly.
The actual image injection into the ToolMessage is handled by
image_content_middleware in src/middleware/image_content.py.
"""

from pathlib import Path

from langchain.tools import tool
from langchain_core.tools import ToolException

from ..config import settings

SUPPORTED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".avif", ".tiff", ".tif",
    ".gif", ".heic", ".heif", ".bmp", ".webp",
}


@tool
def view_image(image_path: str) -> str:
    """
    Load an image so you can see and analyze it directly.
    Use this when you need to visually inspect an image yourself,
    rather than getting a text description from another model.

    Args:
        image_path: Absolute or relative path to the image file.
    """
    try:
        path = Path(image_path).expanduser()
        if not path.is_absolute():
            path = Path(settings.project_root) / path
        path = path.resolve()

        if not path.exists():
            raise ToolException(f"Image not found: {path}")

        ext = path.suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            raise ToolException(
                f"Unsupported image extension '{ext}'. "
                f"Supported: {sorted(SUPPORTED_EXTENSIONS)}"
            )

        # Return the validated absolute path — middleware will read and inject the image
        return f"image_path:{path}"

    except ToolException:
        raise
    except Exception as e:
        raise ToolException(f"view_image failed: {e}")


view_image.handle_tool_error = True
