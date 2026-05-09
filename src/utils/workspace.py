import shutil
from pathlib import Path

from ..config import settings

_SRC = Path(__file__).resolve().parent.parent
_ROOT = Path(settings.project_root)

WORKSPACE = _ROOT / ".workspace"
SKILLS_SRC = _SRC / "skills"

SKILLS_DIR = WORKSPACE / "skills"
MEMORIES_DIR = WORKSPACE / "memories"

def sync_skills() -> None:
    """Sync skills from src/skills/ into .workspace/skills/.

    Copies new and updated skill files without removing skills that only
    exist in the destination (i.e. project-specific skills are preserved).
    """
    for src_path in SKILLS_SRC.rglob("*"):
        rel = src_path.relative_to(SKILLS_SRC)
        dest_path = SKILLS_DIR / rel

        if src_path.is_dir():
            dest_path.mkdir(parents=True, exist_ok=True)
        elif not dest_path.exists() or src_path.stat().st_mtime > dest_path.stat().st_mtime:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest_path)


def setup_workspace() -> None:
    """Initialise .workspace/ in the project root (idempotent).

    On every run this will:
    - Create memories and AGENTS.md if missing
    - Sync src/skills/ → .workspace/skills/ 
        - adds new/updated skills,
        - preserves project-specific skills
    """
    MEMORIES_DIR.mkdir(parents=True, exist_ok=True)

    agents_md = WORKSPACE / "AGENTS.md"
    if not agents_md.exists():
        agents_md.touch()

    sync_skills()