---
name: local-search
description: Use this skill for quick searches across local documents and files.
---

# Local Search Skill

Lightweight local document search using the `local-search-subagent`. Use for targeted lookups across workspace files — not for multi-document synthesis (use deep-research for that).

## When to Use

- Find specific information in one or a few local files
- Answer a question that's likely answered in a known file or directory
- Extract a section or fact from a markdown, PDF, or Office document

## How to Use

Spawn the `local-search-subagent` via the `task` tool with a direct question:

```
Find [SPECIFIC INFORMATION] in [FILE PATH or GLOB].
Return the answer with file path and line references. Do not write any files.
```

The subagent returns its findings directly — no intermediate files needed.
