"""First-run setup and skill installation tracking."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from importlib.resources import files

from ppt_cli import __version__

# ── Overridable paths/values (for testing) ─────────────────────────────
VERSION = os.environ.get("PPT_CLI_VERSION_OVERRIDE") or __version__
INSTALL_JSON = os.environ.get("PPT_CLI_INSTALL_JSON") or os.path.expanduser(
    "~/.config/ppt-cli/install.json"
)
SKILL_DIR = os.environ.get("PPT_CLI_SKILL_DIR") or str(files("ppt_cli") / "skill")
FORCE_TTY = os.environ.get("PPT_CLI_FORCE_TTY") == "1"


def _is_interactive():
    """Check if we're in an interactive terminal (or forced via env var)."""
    return FORCE_TTY or sys.stdin.isatty()


def _read_install_json():
    """Read install.json and return the dict, or None if it doesn't exist."""
    try:
        with open(INSTALL_JSON) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _write_install_json(data):
    """Write install.json, creating the parent directory if needed."""
    os.makedirs(os.path.dirname(INSTALL_JSON), exist_ok=True)
    with open(INSTALL_JSON, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def _current_skill_hash():
    """SHA-256 hash of the bundled SKILL.md."""
    skill_md = os.path.join(SKILL_DIR, "SKILL.md")
    with open(skill_md) as f:
        content = f.read()
    return hashlib.sha256(content.encode()).hexdigest()


def _make_install_data(skill_installed, skill_hash=None):
    """Build an install.json data dict."""
    return {
        "ppt_cli_version": VERSION,
        "skill_installed": skill_installed,
        "skill_hash": skill_hash or "",
        "installed_at": datetime.now(timezone.utc).isoformat(),
    }


def _run_npx_skills_add(interactive):
    """Run npx skills add for the bundled skill directory.

    interactive=True:  human terminal, full interactive flow
    interactive=False: silent auto-update, all prompts skipped
    Returns True on success, False on failure.
    """
    npx = shutil.which("npx")
    if not npx:
        print(
            "npx not found. Install Node.js first: https://nodejs.org/",
            file=sys.stderr,
        )
        return False

    cmd = [npx, "-y", "skills", "add", SKILL_DIR, "-g"]
    if not interactive:
        cmd.append("-y")

    if interactive:
        result = subprocess.run(cmd)
    else:
        result = subprocess.run(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    return result.returncode == 0


def cmd_setup(args):
    """Explicit setup command: ppt-cli setup."""
    if not _is_interactive():
        print("ppt-cli setup requires an interactive terminal.", file=sys.stderr)
        sys.exit(1)

    success = _run_npx_skills_add(interactive=True)
    skill_hash = _current_skill_hash() if success else ""
    _write_install_json(_make_install_data(
        skill_installed=success,
        skill_hash=skill_hash,
    ))
    if not success:
        sys.exit(1)


def _check_setup(command):
    """Pre-command setup check. Called from main() before dispatching.

    - Skipped when command is 'setup' (handled by cmd_setup itself)
    - First run (no install.json): interactive setup or agent guidance
    - Version matches: skip
    - Version differs: silent update or auto-update depending on hash
    """
    if command == "setup":
        return

    data = _read_install_json()

    if data is None:
        # ── First run ──
        if _is_interactive():
            print("Welcome to ppt-cli! Let's set up agent integration.\n")
            success = _run_npx_skills_add(interactive=True)
            skill_hash = _current_skill_hash() if success else ""
            _write_install_json(_make_install_data(
                skill_installed=success,
                skill_hash=skill_hash,
            ))
            if success:
                print()  # blank line after npx output
        else:
            print(
                "ppt-cli requires first-time setup. "
                "Ask the user to run: ppt-cli setup",
                file=sys.stderr,
            )
            sys.exit(1)
        return

    # ── Version matches → nothing to do ──
    if data.get("ppt_cli_version") == VERSION:
        return

    # ── Version differs ──
    if not data.get("skill_installed"):
        # User previously declined — just bump version, don't nag
        data["ppt_cli_version"] = VERSION
        _write_install_json(data)
        return

    # skill_installed == true — check if SKILL.md content changed
    old_hash = data.get("skill_hash", "")
    new_hash = _current_skill_hash()

    if old_hash == new_hash:
        # SKILL.md unchanged — just bump version
        data["ppt_cli_version"] = VERSION
        _write_install_json(data)
    else:
        # SKILL.md changed — silent auto-update
        _run_npx_skills_add(interactive=False)
        data["ppt_cli_version"] = VERSION
        data["skill_hash"] = new_hash
        data["installed_at"] = datetime.now(timezone.utc).isoformat()
        _write_install_json(data)
