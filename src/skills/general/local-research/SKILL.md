---
name: local-research
description: Use this skill for requests that require finding, reading, or analyzing information within local documents and files.
---

# Local Research Skill

This skill provides a structured approach to researching information across local documents — markdown files, PDFs, images, and Office documents — using the `task` tool to spawn local research subagents. It emphasizes efficient document discovery, targeted searching, and clear synthesis of findings.

## When to Use This Skill

Use this skill when you need to:

- Find specific information across multiple local documents
- Analyze or summarize the contents of PDFs, Office documents, or markdown files
- Answer questions that require cross-referencing several local files
- Extract and compare data from documents

**Do NOT use this skill for web research** — use the web-research skill instead.

## Research Process

### Step 1: Scope the Research

Before delegating to subagents:

1. **Identify what files exist** — Use `ls` or `glob` to discover relevant documents
2. **Determine file types** — Non-markdown files (PDF, DOCX, images) need OCR conversion before they can be searched
3. **Plan the approach** — Decide whether you need a single subagent or multiple parallel subagents based on the number of files and questions

### Step 2: Delegate to Research Subagents

For each research task:

1. **Use the `task` tool** to spawn a local research subagent with:
   - A clear, specific question to answer
   - The file path(s) or glob pattern to search
   - Instructions to write findings to a file if the output is substantial

2. **Run up to 3 subagents in parallel** for multi-file or multi-question research

**Subagent Instructions Template:**

```
Find information about [SPECIFIC TOPIC] in [FILE PATH or GLOB PATTERN].
Use outline to understand document structure, then search to find relevant sections.
Read the matching sections and extract the key information.
Write your findings to research_[topic]/findings_[subtopic].md with file paths and line references.
```

**For non-markdown files**, instruct the subagent to run `to_md` first:

```
Convert [FILE PATH] to markdown using to_md, then search the converted output for [TOPIC].
```

### Step 3: Synthesize Findings

After all subagents complete:

1. **Review the findings files** saved by subagents:
   - Use `ls` to see what was created
   - Use `read_file` to review each findings file

2. **Synthesize the information** — Create a response that:
   - Directly answers the original question
   - Cites specific files and line ranges for each finding
   - Notes any gaps or documents that didn't contain relevant information

3. **Write final report** (optional) — Save to `research_[topic]/research_report.md` if requested

## Available Subagent Tools

Each local research subagent has access to:

- **outline**: Get heading hierarchy with line ranges for a markdown file
- **search**: BM25-ranked section search across one or many markdown files
- **to_md**: OCR pipeline — converts PDFs, images, and Office documents to markdown
- **view_image**: Visually inspect an image
- **read_file**: Read file contents with optional line ranges
- **ls** / **glob**: Discover files by listing or pattern
- **grep**: Exact-match or regex search across file contents