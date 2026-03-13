"""Guidelines commands — design principles and image prompting tips."""

import os
import sys

_PKG_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.dirname(_PKG_DIR)

_OVERVIEW = """\
Available guidelines:

  ppt-cli guidelines design      Presentation design principles, typography,
                                  color, layout, spacing, and QA workflow.
                                  Read this before building any deck.

  ppt-cli guidelines image-gen   Image prompt engineering for AI-generated
                                  visuals (add-image --prompt, image-gen).
                                  Read this when images are part of the plan.

Start with 'design' — it applies to every presentation. Only read 'image-gen'
after the deck structure is clear and you know images are needed.
"""


def _read_guideline(filename):
    path = os.path.join(_PROJECT_DIR, filename)
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        print(f"error: {filename} not found", file=sys.stderr)
        sys.exit(1)


def cmd_guidelines_overview(_args):
    print(_OVERVIEW, end="")


def cmd_guidelines_design(_args):
    print(_read_guideline("DESIGN-GUIDELINES.md"), end="")


def cmd_guidelines_image_gen(_args):
    print(_read_guideline("IMAGE-PROMPTING-TIPS.md"), end="")
