---
name: web-search
description: Use this skill for quick web searches.
---

# Web Search Skill

Lightweight web search using the `web-search-subagent`. Use for targeted lookups — not for multi-source synthesis (use deep-research for that).

## When to Use

- Look up a specific fact, definition, or piece of current information
- Fetch content from a known URL
- Answer a question with 1-3 searches

## How to Use

Spawn the `web-search-subagent` via the `task` tool with a direct question:

```
Search the web for [SPECIFIC QUESTION].
Return the answer with source URLs. Do not write any files. Use 1-3 searches maximum.
```

The subagent returns its findings directly — no intermediate files needed.
