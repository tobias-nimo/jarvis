---
name: md-to-docx
description: "Use this skill whenever the user wants to convert a Markdown (.md) file into a Word document (.docx). Handles math equations (rendered as OMML), tables, headings, code blocks, and embedded images. Uses pandoc under the hood."
---

# Markdown → DOCX Conversion

## Requirements

```bash
# check if pandoc is installed
pandoc --version

# check if python wrapper is installed
python -c "import pypandoc; print('pypandoc installed')"

# install pandoc (if missing)
brew install pandoc

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
from scripts.convert import fix_markdown, md_to_docx

fix_markdown("input.md", "input_fixed.md")
md_to_docx("input_fixed.md", "output.docx")
```

That's it. `fix_markdown` handles the most common issues (HTML entities, escape sequences).
`md_to_docx` will automatically find images that sit next to the `.md` file.

If images are in a different folder, add only `image_dir`:

```python
md_to_docx("input_fixed.md", "output.docx", image_dir="figures")
```

---

## Fallback: custom MD fix + retry

If step 1 raises an error or produces bad output, **read the error message**, inspect the
problematic lines in the `.md` file, and write a targeted fix before retrying.

Common issues and how to fix them:

| Symptom | Likely cause | Custom fix |
|---|---|---|
| Corrupt table in output | Malformed pipe table | Rewrite the table rows in Python |
| Missing content | HTML tags (`<div>`, `<span>`) not stripped | Strip tags with `re` or `BeautifulSoup` |
| Broken math block | `$` used as currency, not math | Escape with `\$` outside math blocks |
| Image missing silently | Wrong relative path in `![]()` | Rewrite image paths to absolute paths |

Example targeted fix pattern:
```python
import re

with open("input.md") as f:
    content = f.read()

# Example: escape $ signs that are currency, not math
content = re.sub(r'\$(?!\$)(?![^$]*\$)', r'\\$', content)

with open("input_patched.md", "w") as f:
    f.write(content)

from scripts.convert import md_to_docx
md_to_docx("input_patched.md", "output.docx")
```

---

## Custom: pandoc CLI directly

Use this when the user asks for specific styling, templates, or flags not exposed by the script.

```bash
# Basic
pandoc input.md -o output.docx --standalone

# With a Word template for custom styles
pandoc input.md -o output.docx --standalone --reference-doc=template.docx

# With images in a separate folder
pandoc input.md -o output.docx --standalone --resource-path=.:./figures

# Table of contents + numbered sections
pandoc input.md -o output.docx --standalone --toc --number-sections

# Multiple image folders (colon-separated on Unix)
pandoc input.md -o output.docx --standalone --resource-path=.:./figures:./images
```

**Generate a starter Word template to customise styles:**
```bash
pandoc --print-default-data-file reference.docx > template.docx
# Open template.docx in Word → edit Heading 1, Body Text, Code styles → save
# Then use: --reference-doc=template.docx
```

---

## Key pandoc flags (reference)

| Flag | Purpose |
|---|---|
| `--standalone` | Produce a complete, self-contained file |
| `--resource-path=PATH` | Colon-separated image search dirs |
| `--reference-doc=FILE` | Word template for styles |
| `--highlight-style=tango` | Code syntax highlighting theme |
| `--toc` | Add a Table of Contents |
| `--number-sections` | Auto-number headings (1.1, 1.2, …) |