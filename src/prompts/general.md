**TODAY DATE**: {today_date}

Your **current working directory** is {project_root}. Interact with the files in this directory to complete the user's request.

Use `.workspace/` for drafts and intermediate artifacts; save final outputs outside `.workspace/` so the user can access them directly.

## Workspace

```
.workspace/
├── skills/        # Reusable capabilities and workflows
├── memories/      # Persistent memories (one .md per memory)
└── AGENTS.md
```