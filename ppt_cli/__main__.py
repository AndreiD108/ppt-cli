"""Entry point for python3 -m ppt_cli."""

import os
import sys

# ── venv bootstrap ────────────────────────────────────────────────────────
_pkg_dir = os.path.dirname(os.path.abspath(__file__))
_project_dir = os.path.dirname(_pkg_dir)
_venv_site = os.path.join(
    _project_dir, ".venv", "lib",
    f"python{sys.version_info.major}.{sys.version_info.minor}",
    "site-packages",
)
if os.path.isdir(_venv_site):
    sys.path.insert(0, _venv_site)

from ppt_cli.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
