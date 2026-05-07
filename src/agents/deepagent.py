# agents/deepagent.py

from pathlib import Path
from datetime import date

from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend
from langchain_groq import ChatGroq # or ChatOpenAI

from ..config import settings
from ..prompts import prompts
from ..middleware import image_content_middleware
from ..tools.md_tools import outline, search
from ..tools.view_image import view_image
from .subagents import subagents
from ..utils import setup_workspace, SKILLS_DEST, COWORK_MD

# Set up .workspace/
_ROOT = Path(settings.project_root)
setup_workspace()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=settings.groq_api_key
)

#llm = ChatOpenAI(
#    model="openai/gpt-5.4-nano",
#    api_key=settings.openrouter_api_key,
#    base_url="https://openrouter.ai/api/v1",
#    reasoning={"effort": "high"},
#)

# Deep Agent
cowork = create_deep_agent(
    # LLM
    model=llm,
    
    # System prompt
    system_prompt=prompts.get(
        "general",
        project_root=settings.project_root,
        today_date=str(date.today()),
    ),

    # SubAgents
    subagents=subagents,

    # Skills + Memory
    skills=[str((SKILLS_DEST / "general").relative_to(_ROOT))],
    memory=[str(COWORK_MD.relative_to(_ROOT))],

    # Tools
    tools=[view_image, outline, search], # + built-ins

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

    # Middleware
    middleware=[image_content_middleware],

    # Debug mode
    debug=settings.debug
)
