---
name: deep-research
description: Use this skill for intensive, multi-source research tasks that require synthesis across several documents or web sources. Not for simple lookups, quick web searches, or single-file word matching.
---

# Deep Research Skill

This skill covers **intensive research** using the `local-search-subagent` (workspace documents) and the `web-search-subagent` (Tavily web search). Use it when the task requires exploring multiple sources, synthesizing findings, or producing a structured report.

**Do not use this skill for:**
- Simple web searches (use the web-search skill instead)
- Single-file lookups or keyword searches in local files (use the local-search skill instead)
- Quick factual questions answerable in one search or one file read

## Choosing the right approach

| Situation | Use |
|---|---|
| Question about files/docs already in the workspace | local only |
| Question requiring current or external information | web only |
| Question where local context should be enriched with web data, or vice versa | both |

When in doubt, check local first — if the answer is there, no web search needed.

## Step 1: Create a Research Plan

Before spawning any subagent:

1. **Create a research folder** — `mkdir research_[topic_name]`
2. **Write `research_[topic_name]/research_plan.md`** containing:
   - The main research question
   - 2-5 subtopics to investigate
   - For each subtopic: whether it goes to local, web, or both
   - How results will be synthesized

**Subtopic count guidelines:**
- Simple fact-finding: 1-2 subtopics
- Comparative analysis: 1 per element (max 3)
- Complex investigations: 3-5 subtopics

## Step 2: Delegate to Subagents

Use the `task` tool to spawn the appropriate subagent(s). Run up to 3 in parallel.

**Local** (`local-search-subagent`):
```
Find information about [TOPIC] in [FILE PATH or GLOB].
Use outline to understand structure, then search to find relevant sections.
Read matching sections and extract key information.
Save findings to research_[topic]/findings_[subtopic].md with file paths and line references.
```

For non-markdown files, instruct the subagent to run `to_md` first:
```
Convert [FILE PATH] to markdown using to_md, then search for [TOPIC].
Save findings to research_[topic]/findings_[subtopic].md.
```

**Web** (`web-search-subagent`):
```
Research [SPECIFIC TOPIC] on the web.
Save findings to research_[topic]/findings_[subtopic].md with source URLs.
Use 3-5 searches maximum.
```

## Step 3: Synthesize Findings

After all subagents complete:

1. `ls research_[topic_name]` to confirm all findings files exist
2. `read_file` each findings file
3. Synthesize into a response that:
   - Directly answers the original question
   - Cites local sources (file path + line range) and web sources (URLs) separately
   - Identifies any gaps or conflicts between sources
4. Optionally write `research_[topic_name]/research_report.md` if a report was requested
