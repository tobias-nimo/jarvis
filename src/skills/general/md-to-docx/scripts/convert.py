"""
scripts/convert.py — helpers for the md-to-docx skill.

Usage:
    from scripts.convert import fix_markdown, md_to_docx
"""

import os
import pypandoc


# ---------------------------------------------------------------------------
# Pre-processing
# ---------------------------------------------------------------------------

def fix_markdown(input_path: str, output_path: str) -> None:
    """
    Sanitise a Markdown file before passing it to pandoc.

    Fixes:
    - HTML entities (&amp; &gt; &lt; &quot;) left over from web/PDF exports
    - Literal \\n / \\t escape sequences in plain text (outside math blocks)
      which confuse the DOCX renderer

    Args:
        input_path:  Path to the original .md file.
        output_path: Path to write the sanitised copy.
    """
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace("&amp;", "&")
    content = content.replace("&gt;",  ">")
    content = content.replace("&lt;",  "<")
    content = content.replace("&quot;", '"')

    # Literal \n inside curly-quoted strings (common in exported academic papers)
    content = content.replace("\u201d\\n\u201d",   "\u201d`\\\\n`\u201d")
    content = content.replace("\u201d\\n\\n,",     "\u201d`\\\\n\\\\n`\u201d,")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)


# ---------------------------------------------------------------------------
# Resource path builder
# ---------------------------------------------------------------------------

def _resource_path(input_path: str, image_dir) -> str:
    """
    Build a pandoc --resource-path value.

    Always prepends the directory of the source .md file so that
    relative image references like ![fig](img-0.jpeg) resolve automatically.

    Args:
        input_path: Path to the .md file being converted.
        image_dir:  Extra directory (str) or directories (list[str]) to search.

    Returns:
        Colon-separated (Unix) or semicolon-separated (Windows) path string.
    """
    sep   = ";" if os.name == "nt" else ":"
    paths = [os.path.dirname(os.path.abspath(input_path))]

    if image_dir:
        extras = [image_dir] if isinstance(image_dir, str) else list(image_dir)
        paths.extend(os.path.abspath(d) for d in extras)

    # Deduplicate while preserving insertion order
    seen, unique = set(), []
    for p in paths:
        if p not in seen:
            seen.add(p)
            unique.append(p)

    return sep.join(unique)


# ---------------------------------------------------------------------------
# Main conversion function
# ---------------------------------------------------------------------------

def md_to_docx(
    input_path: str,
    output_path: str,
    image_dir=None,
    reference_doc: str | None = None,
    toc: bool = False,
    number_sections: bool = False,
    highlight_style: str = "tango",
) -> str:
    """
    Convert a Markdown file to DOCX using pandoc.

    Args:
        input_path:       Path to the source .md file.
        output_path:      Destination path for the .docx file.
        image_dir:        Directory (str) or directories (list[str]) that contain
                          images referenced in the markdown.  The .md file's own
                          directory is always searched first automatically.
        reference_doc:    Path to a .docx template that controls styles
                          (fonts, headings, margins, etc.).
                          Generate a starter template with:
                              pandoc --print-default-data-file reference.docx > template.docx
        toc:              If True, insert a Table of Contents.
        number_sections:  If True, auto-number headings (1, 1.1, 1.2, …).
        highlight_style:  Pygments theme for code-block syntax highlighting.
                          Common values: tango, pygments, kate, monochrome, espresso.

    Returns:
        Absolute path to the created .docx file.

    Examples:
        # Simplest case — images live next to the .md file
        md_to_docx("paper/LoRA.md", "out/LoRA.docx")

        # Images in a different folder
        md_to_docx("paper/LoRA.md", "out/LoRA.docx", image_dir="paper/figures")

        # Multiple image folders + custom Word template
        md_to_docx(
            "paper/LoRA.md",
            "out/LoRA.docx",
            image_dir=["figures", "plots"],
            reference_doc="template.docx",
        )
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    extra_args = [
        "--standalone",
        f"--resource-path={_resource_path(input_path, image_dir)}",
        f"--highlight-style={highlight_style}",
    ]

    if reference_doc:
        extra_args.append(f"--reference-doc={reference_doc}")
    if toc:
        extra_args.append("--toc")
    if number_sections:
        extra_args.append("--number-sections")

    pypandoc.convert_file(
        input_path,
        "docx",
        outputfile=output_path,
        extra_args=extra_args,
    )

    return os.path.abspath(output_path)
