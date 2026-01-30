"""Configuration management for the release tool."""

import os
from pathlib import Path
from typing import Optional


def find_project_root(start_path: Optional[Path] = None) -> Path:
    """
    Find the project root by looking for .git directory.

    Args:
        start_path: Starting path for search (default: current working directory)

    Returns:
        Path to project root

    Raises:
        RuntimeError: If project root cannot be found
    """
    current = start_path or Path.cwd()

    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent

    raise RuntimeError("Cannot find project root (no .git directory found)")


def load_env(project_root: Path) -> dict[str, str]:
    """
    Load environment variables from .env file.

    Args:
        project_root: Path to project root

    Returns:
        Dictionary of environment variables

    Raises:
        FileNotFoundError: If .env file doesn't exist
    """
    env_file = project_root / ".env"

    if not env_file.exists():
        raise FileNotFoundError(
            f".env file not found at {env_file}\n"
            f"Create one from .env.example"
        )

    env_vars = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, _, value = line.partition("=")
                env_vars[key.strip()] = value.strip().strip('"').strip("'")

    return env_vars


class Config:
    """Configuration for release tool."""

    def __init__(self):
        self.project_root = find_project_root()
        self.env_vars = load_env(self.project_root)
        self.main_branch = self.env_vars.get("MAIN_BRANCH", "main")

        # Get LaTeX directory from env or use default
        latex_dir_str = self.env_vars.get("LATEX_DIR", "")
        self.latex_dir = self.project_root / latex_dir_str

        # Validate LaTeX directory exists
        if not self.latex_dir.exists():
            raise FileNotFoundError(
                f"LaTeX directory not found: {self.latex_dir}\n"
                f"Check LATEX_DIR in .env file"
            )

    def __repr__(self) -> str:
        return (
            f"Config(project_root={self.project_root}, "
            f"main_branch={self.main_branch}, "
            f"latex_dir={self.latex_dir})"
        )
