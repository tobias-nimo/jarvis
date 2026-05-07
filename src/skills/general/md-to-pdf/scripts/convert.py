"""
scripts/convert.py — helpers for the md-to-pdf skill.

Usage:
    from scripts.convert import fix_markdown, md_to_pdf
"""

import os
import pypandoc


# ---------------------------------------------------------------------------
# Pre-processing
# ---------------------------------------------------------------------------

def fix_markdown(input_path: str, output_path: str) -> None:
    """
    Sanitise a Markdown file before passing it to pandoc/xelatex.

    Fixes:
    - HTML entities (&amp; &gt; &lt; &quot;) left over from web/PDF exports.
      These cause 'Misplaced alignment tab &' or parse errors in LaTeX.
    - Literal \\n / \\t escape sequences in plain text (outside math blocks).
      These cause 'Undefined control sequence' errors in xelatex.

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

    seen, unique = set(), []
    for p in paths:
        if p not in seen:
            seen.add(p)
            unique.append(p)

    return sep.join(unique)


# ---------------------------------------------------------------------------
# Main conversion function
# ---------------------------------------------------------------------------

def md_to_pdf(
    input_path: str,
    output_path: str,
    image_dir=None,
    pdf_engine: str = "xelatex",
    margin: str = "1in",
    font_size: str = "11pt",
    main_font: str = "DejaVu Serif",
    mono_font: str = "DejaVu Sans Mono",
    colorlinks: bool = True,
    toc: bool = False,
    number_sections: bool = False,
    highlight_style: str = "tango",
    extra_args: list | None = None,
) -> str:
    """
    Convert a Markdown file to PDF using pandoc + xelatex.

    Args:
        input_path:       Path to the source .md file.
        output_path:      Destination path for the .pdf file.
        image_dir:        Directory (str) or directories (list[str]) that contain
                          images referenced in the markdown.  The .md file's own
                          directory is always searched first automatically.
        pdf_engine:       LaTeX engine to use. 'xelatex' recommended (Unicode support).
                          Other options: 'pdflatex' (fast, ASCII only), 'lualatex' (full LaTeX).
        margin:           Page margin on all sides, e.g. '1in', '2cm', '0.75in'.
        font_size:        Base font size: '10pt', '11pt', or '12pt'.
        main_font:        Main text font (xelatex/lualatex only).
                          'DejaVu Serif' has broad Unicode coverage.
        mono_font:        Monospace font for code (xelatex/lualatex only).
        colorlinks:       If True, hyperlinks are coloured instead of boxed.
        toc:              If True, insert a Table of Contents.
        number_sections:  If True, auto-number headings (1, 1.1, 1.2, …).
        highlight_style:  Pygments theme for code-block syntax highlighting.
                          Common values: tango, pygments, kate, monochrome, espresso.
        extra_args:       Any additional pandoc flags, e.g. ['-H', 'preamble.tex'].

    Returns:
        Absolute path to the created .pdf file.

    Examples:
        # Simplest case — images live next to the .md file
        md_to_pdf("paper/LoRA.md", "out/LoRA.pdf")

        # Images in a different folder
        md_to_pdf("paper/LoRA.md", "out/LoRA.pdf", image_dir="paper/figures")

        # Multiple image folders + TOC
        md_to_pdf(
            "paper/LoRA.md",
            "out/LoRA.pdf",
            image_dir=["figures", "plots"],
            toc=True,
        )

        # Inject a custom LaTeX preamble
        md_to_pdf("paper/LoRA.md", "out/LoRA.pdf", extra_args=["-H", "preamble.tex"])
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    args = [
        f"--pdf-engine={pdf_engine}",
        "--standalone",
        f"--resource-path={_resource_path(input_path, image_dir)}",
        f"-V", f"geometry:margin={margin}",
        f"-V", f"fontsize={font_size}",
        f"--highlight-style={highlight_style}",
    ]

    # Font flags are only meaningful for xelatex / lualatex
    if pdf_engine in ("xelatex", "lualatex"):
        args += ["-V", f"mainfont={main_font}", "-V", f"monofont={mono_font}"]

    if colorlinks:
        args += ["-V", "colorlinks=true"]
    if toc:
        args.append("--toc")
    if number_sections:
        args.append("--number-sections")
    if extra_args:
        args.extend(extra_args)

    pypandoc.convert_file(
        input_path,
        "pdf",
        outputfile=output_path,
        extra_args=args,
    )

    return os.path.abspath(output_path)
