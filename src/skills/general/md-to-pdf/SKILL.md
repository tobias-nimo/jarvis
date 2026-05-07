---
name: md-to-pdf
description: "Use this skill whenever the user wants to convert a Markdown (.md) file into a PDF. Handles math equations (via LaTeX), tables, headings, code blocks with syntax highlighting, and embedded images. Uses pandoc with xelatex under the hood."
---

# Markdown → PDF Conversion

## Requirements

```bash
# check if pandoc is installed
pandoc --version

# check if python wrapper is installed
python -c "import pypandoc; print('pypandoc installed')"

# install system dependencies (if missing)
brew install pandoc basictex
tlmgr install xetex lmodern collection-fontsrecommended collection-latexextra

# install python wrapper (if missing)
pip install pypandoc
```

## Approaches

- **DEFAULT** → Use predefined Python functions with minimal arguments.
- **FALLBACK** → Inspect the Markdown, write custom Python to address the specific issue, and retry.
- **CUSTOM** → Use the Pandoc CLI directly for full control.

> Start with the default approach. If an error occurs, switch to fallback. Use custom only when user explicitly asks for customization or when advanced control is required.

---

## Default

```python
from scripts.convert import fix_markdown, md_to_pdf

fix_markdown("input.md", "input_fixed.md")
md_to_pdf("input_fixed.md", "output.pdf")
```

That's it. `fix_markdown` handles the most common xelatex-breaking issues (HTML entities,
literal `\n` in text). `md_to_pdf` uses sane defaults: 1in margins, 11pt, DejaVu fonts,
tango code highlighting.

If images are in a different folder, add only `image_dir`:

```python
md_to_pdf("input_fixed.md", "output.pdf", image_dir="figures")
```

---

## Fallback: custom MD fix + retry

If step 1 raises an error, **read the xelatex error message carefully** — it includes the
line number and the offending token. Inspect that line in the `.md` file, write a targeted
Python fix, and retry.

Common xelatex errors and their fixes:

| xelatex error | Cause in the MD | Custom fix |
|---|---|---|
| `Undefined control sequence \n` | Literal `\n` in plain text | Wrap in backtick: `` `\n` `` |
| `Misplaced alignment tab &` | `&` outside math/tables (e.g. `&amp;`) | Replace with `\&` or `and` |
| `Missing $ inserted` | `_` or `^` used outside math | Escape: `\_`, `\^` |
| `Undefined control sequence \foo` | Backslash in text not in math | Escape or wrap in code span |
| `File X not found` | Missing image | Check path, fix with `--resource-path` |
| `File lmodern.sty not found` | Missing LaTeX package | `apt install lmodern` |

Example targeted fix pattern:
```python
import re

with open("input.md") as f:
    content = f.read()

# Example: escape underscores used as "var_name" in plain text (not in code/math)
# This is a rough heuristic — refine the regex for the specific file
content = re.sub(r'(?<!`)\b(\w+)_(\w+)\b(?!`)', r'\1\\_\2', content)

with open("input_patched.md", "w") as f:
    f.write(content)

from scripts.convert import md_to_pdf
md_to_pdf("input_patched.md", "output.pdf")
```

---

## Custom: pandoc CLI directly

Use this when the user asks for specific layout, fonts, LaTeX preambles, or flags not
exposed by the script.

```bash
# Basic
pandoc input.md -o output.pdf --pdf-engine=xelatex --standalone

# Full-featured
pandoc input.md -o output.pdf \
  --pdf-engine=xelatex \
  --standalone \
  -V geometry:margin=1in \
  -V fontsize=11pt \
  -V colorlinks=true \
  -V mainfont="DejaVu Serif" \
  -V monofont="DejaVu Sans Mono" \
  --highlight-style=tango

# With images in a separate folder
pandoc input.md -o output.pdf --pdf-engine=xelatex --standalone \
  --resource-path=.:./figures

# Table of contents + numbered headings
pandoc input.md -o output.pdf --pdf-engine=xelatex --standalone --toc --number-sections

# Inject a custom LaTeX preamble (line spacing, custom envs, etc.)
pandoc input.md -o output.pdf --pdf-engine=xelatex --standalone -H preamble.tex
```

---

## Key pandoc flags (reference)

| Flag | Purpose |
|---|---|
| `--pdf-engine=xelatex` | Use xelatex (recommended — best Unicode support) |
| `--standalone` | Produce a complete, self-contained file |
| `--resource-path=PATH` | Colon-separated image search dirs |
| `-V geometry:margin=1in` | Page margins |
| `-V fontsize=11pt` | Base font size (`10pt`, `11pt`, `12pt`) |
| `-V colorlinks=true` | Colour hyperlinks instead of boxing them |
| `-V mainfont=NAME` | Main text font (xelatex only) |
| `-V monofont=NAME` | Monospace font for code (xelatex only) |
| `--highlight-style=tango` | Code syntax highlighting theme |
| `--toc` | Add a Table of Contents |
| `--number-sections` | Auto-number headings (1.1, 1.2, …) |
| `-H FILE` | Inject a raw LaTeX preamble file |