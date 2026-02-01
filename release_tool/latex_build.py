"""LaTeX compilation utilities."""

import subprocess
from pathlib import Path


def build_latex(latex_dir: Path) -> None:
    """
    Build LaTeX document using Makefile.

    Args:
        latex_dir: Path to LaTeX directory

    Raises:
        RuntimeError: If compilation fails
        FileNotFoundError: If Makefile doesn't exist
    """
    makefile = latex_dir / "Makefile"

    if not makefile.exists():
        raise FileNotFoundError(f"Makefile not found at {makefile}")

    print(f"📄 Building LaTeX document in {latex_dir}...\n\n")

    try:
        result = subprocess.run(
            ["make", "deploy"],
            cwd=latex_dir,
            check=True,
            # capture_output=True,
            text=True
        )
        print("\n\n✅ LaTeX compilation successful")

    except subprocess.CalledProcessError as e:
        print(f"✗ LaTeX compilation failed")
        print(f"\nStdout:\n{e.stdout}")
        print(f"\nStderr:\n{e.stderr}")
        raise RuntimeError("LaTeX compilation failed") from e
