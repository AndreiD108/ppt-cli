"""Inspection commands: info, list, dump, peek, screenshot."""

import json
import os
import subprocess
import sys
import tempfile

from .helpers import _die, _open, _get_slide
from .serialisation import _emu_to_in, _dump_slide, _peek_slide


def cmd_info(args):
    prs = _open(args.file)
    info = {
        "file": args.file,
        "slides": len(prs.slides),
        "width": _emu_to_in(prs.slide_width),
        "height": _emu_to_in(prs.slide_height),
        "layouts": [layout.name for layout in prs.slide_layouts],
    }
    print(json.dumps(info, indent=2))


def cmd_list(args):
    prs = _open(args.file)
    slides = []
    for i, slide in enumerate(prs.slides, 1):
        title = None
        for shape in slide.shapes:
            if shape.has_text_frame and shape.is_placeholder:
                if shape.placeholder_format.idx == 0:
                    title = shape.text
                    break
        slides.append({"slide": i, "title": title, "shapes": len(slide.shapes)})
    print(json.dumps(slides, indent=2))


def cmd_dump(args):
    prs = _open(args.file)
    if args.all:
        result = [_dump_slide(s, i) for i, s in enumerate(prs.slides, 1)]
        print(json.dumps(result, indent=2))
    else:
        if args.slide is None:
            _die("specify a slide number or --all")
        slide = _get_slide(prs, args.slide)
        print(json.dumps(_dump_slide(slide, args.slide), indent=2))


def cmd_peek(args):
    prs = _open(args.file)
    if args.all or args.slide is None:
        for i, slide in enumerate(prs.slides, 1):
            if i > 1:
                print()
            print(_peek_slide(slide, i))
    else:
        slide = _get_slide(prs, args.slide)
        print(_peek_slide(slide, args.slide))


def _is_snap_lo(lo_path):
    """Check if LibreOffice is a snap installation."""
    try:
        real = os.path.realpath(
            subprocess.run(["which", lo_path], capture_output=True,
                           text=True).stdout.strip())
        return "/snap/" in real or "/snap/" in subprocess.run(
            ["which", lo_path], capture_output=True, text=True).stdout
    except Exception:
        return False


def cmd_screenshot(args):
    """Render slide as PNG via LibreOffice + pdftoppm."""
    lo = None
    for name in ("libreoffice", "soffice"):
        try:
            if subprocess.run(["which", name], capture_output=True).returncode == 0:
                lo = name
                break
        except FileNotFoundError:
            continue
    if not lo:
        mac_lo = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
        if os.path.isfile(mac_lo):
            lo = mac_lo
    if not lo:
        _die("libreoffice not found (install libreoffice for screenshots)")

    abs_file = os.path.abspath(args.file)
    slide_num = args.slide
    dpi = args.dpi or 150
    output = args.output or f"slide_{slide_num}.png"
    abs_output = os.path.abspath(output)

    snap = _is_snap_lo(lo)
    if snap:
        snap_tmp = os.path.expanduser("~/snap/libreoffice/common/.ppt-cli-tmp")
        os.makedirs(snap_tmp, exist_ok=True)
    work_dir = snap_tmp if snap else tempfile.mkdtemp()

    try:
        if snap:
            import shutil
            src_copy = os.path.join(work_dir, os.path.basename(abs_file))
            shutil.copy2(abs_file, src_copy)
            convert_src = src_copy
        else:
            convert_src = abs_file

        r = subprocess.run(
            [lo, "--headless", "--convert-to", "pdf",
             "--outdir", work_dir, convert_src],
            capture_output=True,
        )
        if r.returncode != 0:
            _die(f"libreoffice failed: {r.stderr.decode()}")

        pdfs = [f for f in os.listdir(work_dir) if f.endswith(".pdf")]
        if not pdfs:
            _die("PDF conversion produced no output "
                 "(if LibreOffice is open, close it first)")
        pdf = os.path.join(work_dir, pdfs[0])

        out_stem = os.path.splitext(abs_output)[0]
        r = subprocess.run(
            ["pdftoppm", "-png", "-singlefile",
             "-f", str(slide_num), "-l", str(slide_num),
             "-r", str(dpi), pdf, out_stem],
            capture_output=True,
        )
        if r.returncode != 0:
            _die(f"pdftoppm failed (install poppler-utils): {r.stderr.decode()}")

    finally:
        import shutil
        shutil.rmtree(work_dir, ignore_errors=True)

    print(json.dumps({"output": abs_output}))
