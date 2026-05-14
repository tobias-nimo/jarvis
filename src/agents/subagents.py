# agent/subagents.py

from pathlib import Path

from langchain_openai import ChatOpenAI
#from langchain_groq import ChatGroq

from ..config import settings
from ..prompts import prompts
from ..utils import WORKSPACE
from ..tools.view_image import view_image
from ..tools.md_tools import outline, search

_ROOT = Path(settings.project_root)

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

# Subagents

web_search_subagent = {
    "name": "web-search-subagent",
    "model": llm,
    "description": "Performs precise, in-depth web research and returns structured, reliable findings.",
    "system_prompt": prompts.get("web-search"),
    "tools": [view_image],
    "skills": [str((WORKSPACE / "skills" / "tavily").relative_to(_ROOT))]
}

local_search_subagent = {
    "name": "local-search-subagent",
    "model": llm,
    "description": "Searches, navigates, and analyzes local documents and files — use it to find information in large markdown files within the workspace.",
    "system_prompt": prompts.get("local-search"),
    "tools": [outline, search, view_image],
    "skills": [str((WORKSPACE / "skills" / "local").relative_to(_ROOT))]
}

gws_subagent = {
    "name": "gws-subagent",
    "model": llm,
    "description": "Interacts with the full Google Workspace suite (Drive, Gmail, Calendar, Docs and Sheets) via the gws CLI, logged into the user's Google account (tobiasnimo99@gmail.com).",
    "system_prompt": prompts.get("google"),
    "tools": [view_image],
    "skills": [str((WORKSPACE / "skills" / "gws").relative_to(_ROOT))]
}

browser_subagent = {
    "name": "browser-subagent",
    "model": llm,
    "description": "Automates browser interactions — navigates websites, fills forms, extracts data, takes screenshots, and handles authenticated sessions via the browser-use CLI.",
    "system_prompt": prompts.get("browser"),
    "tools": [view_image],
    "skills": [str((WORKSPACE / "skills" / "browser").relative_to(_ROOT))]
}

subagents = [
    local_search_subagent,
    web_search_subagent,
    browser_subagent,
    gws_subagent
]