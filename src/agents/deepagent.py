# agents/deepagent.py

from pathlib import Path
from datetime import date

from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend
from langchain_groq import ChatGroq # or ChatOpenAI

from ..config import settings
from ..prompts import prompts
from .subagents import subagents
from ..tools.md_tools import outline, search
from ..utils import setup_workspace, WORKSPACE

# Set up .workspace/
_ROOT = Path(settings.project_root)
setup_workspace()

#llm = ChatOpenAI(
#    model="openai/gpt-5.4-nano",
#    api_key=settings.openrouter_api_key,
#    base_url="https://openrouter.ai/api/v1",
#    reasoning={"effort": "high"},
#)

# Create deepagent
jarvis = create_deep_agent(
    # LLM
    model=ChatGroq(
        model="openai/gpt-oss-20b",
        api_key=settings.groq_api_key
    ),
    
    # System prompt
    system_prompt=prompts.get(
        "general",
        project_root=settings.project_root,
        today_date=str(date.today()),
    ),

    # SubAgents
    subagents=subagents,

    # Skills + Memory
    skills=[str((WORKSPACE / "skills" / "general").relative_to(_ROOT))],
    memory=[str((WORKSPACE / "AGENTS.md").relative_to(_ROOT))],

    # Tools
    tools=[outline, search], # + built-ins

    # HITL
    interrupt_on={
        "edit_file": True, # If True, default options are: approve, edit, reject
        "read_file": False,
        "write_file": False,
    },

    # Backend
    backend=LocalShellBackend(
        root_dir=settings.project_root,
        inherit_env=True
    ), # + exec tool

    # Debug mode
    debug=settings.debug
)
