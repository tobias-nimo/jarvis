# agents/deepagent.py

from pathlib import Path
from datetime import date

from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend
from langchain_openai import ChatOpenAI 
#from langchain_groq import ChatGroq

from ..config import settings
from ..prompts import prompts
from .subagents import subagents
from ..tools.view_image import view_image
from ..tools.md_tools import outline, search
from ..middleware import image_content_middleware
from ..utils import setup_workspace, WORKSPACE

# Set up .workspace/
_ROOT = Path(settings.project_root)
setup_workspace()

# LLM
llm = ChatOpenAI(
    model="qwen/qwen3.6-35b-a3b",
    api_key=settings.openrouter_api_key,
    base_url="https://openrouter.ai/api/v1",
    temperature=1.0,
    top_p=0.95,
    presence_penalty=1.5,
    extra_body={
        "top_k": 20,
        "min_p": 0.0,
        "repetition_penalty": 1.0,
    },
    use_responses_api=False,
)
#llm = ChatOpenAI(
#    model="openai/gpt-5.4-nano",
#    api_key=settings.openrouter_api_key,
#    base_url="https://openrouter.ai/api/v1",
#    reasoning_effort="high",
#    use_responses_api=False,
#)
#llm = ChatGroq(model="openai/gpt-oss-20b", api_key=settings.groq_api_key)

# System Prompt
prompt = prompts.get(
    "general",
    project_root=settings.project_root,
    today_date=str(date.today()),
)

# Human-in-the-Loop
hitl = {
    "edit_file": True, # If True, default options are: approve, edit, reject
    "read_file": False,
    "write_file": False,
}

# Backend
backend = LocalShellBackend(
    root_dir=settings.project_root,
    inherit_env=True,
    env={"WORKSPACE_ROOT": str(_ROOT)},
    virtual_mode=True,
) # + exec tool

# Create deepagent
jarvis = create_deep_agent(
    model=llm,
    system_prompt=prompt,
    subagents=subagents,
    skills=[str((WORKSPACE / "skills" / "general").relative_to(_ROOT))],
    memory=[str((WORKSPACE / "AGENTS.md").relative_to(_ROOT))],
    tools=[outline, search, view_image], # + built-ins
    interrupt_on=hitl,
    backend=backend,
    middleware=[image_content_middleware],
    debug=settings.debug
)
