"""Inspection commands: info, list, dump, peek, screenshot."""

import fcntl
import hashlib
import json
import os
import shutil
import subprocess
import tempfile

from .helpers import _die, _open, _get_slide, Presentation
from .serialisation import _emu_to_in, _dump_slide, _peek_slide


def _is_hidden(slide):
    """Check if a slide is hidden (show='0' in XML)."""
    return slide._element.attrib.get("show", "1") == "0"


def cmd_info(args):
    prs = _open(args.file)
    hidden = [i for i, s in enumerate(prs.slides, 1) if _is_hidden(s)]
    info = {
        "file": args.file,
        "slides": len(prs.slides),
        "hidden_slides": hidden,
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
        entry = {"slide": i, "title": title, "shapes": len(slide.shapes)}
        if _is_hidden(slide):
            entry["hidden"] = True
        slides.append(entry)
    print(json.dumps(slides, indent=2))


def cmd_dump(args):
    prs = _open(args.file)
    if args.all:
        slide_nums = list(range(1, len(prs.slides) + 1))
    else:
        slide_nums = args.slides
    if not slide_nums:
        _die("specify slide number(s) or --all")
    result = []
    for n in slide_nums:
        slide = _get_slide(prs, n)
        d = _dump_slide(slide, n)
        if _is_hidden(slide):
            d["hidden"] = True
        result.append(d)
    if len(result) == 1:
        print(json.dumps(result[0], indent=2))
    else:
        print(json.dumps(result, indent=2))


def _peek_with_hidden(slide, num):
    text = _peek_slide(slide, num)
    if _is_hidden(slide):
        text = text.replace(f"slide {num}:", f"slide {num}: [HIDDEN]", 1)
    return text


def cmd_peek(args):
    prs = _open(args.file)
    if args.all or not args.slides:
        slide_nums = list(range(1, len(prs.slides) + 1))
    else:
        slide_nums = args.slides
    first = True
    for n in slide_nums:
        slide = _get_slide(prs, n)
        if not first:
            print()
        print(_peek_with_hidden(slide, n))
        first = False


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


def _find_libreoffice():
    """Find a working LibreOffice binary. Returns (path, is_snap) or dies."""
    for name in ("libreoffice", "soffice"):
        try:
            if subprocess.run(["which", name], capture_output=True).returncode == 0:
                return name, _is_snap_lo(name)
        except FileNotFoundError:
            continue
    mac_lo = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    if os.path.isfile(mac_lo):
        return mac_lo, False
    _die("libreoffice not found, screenshotting not supported")


def _file_hash(path):
    """SHA-256 hash of a file's contents (first 16 hex chars)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


_CACHE_DIR = "/tmp/ppt-cli-screenshots"


def _unhide_slides(src_path, dest_path):
    """Copy a .pptx to dest_path with all hidden slides unhidden."""
    prs = Presentation(src_path)
    changed = False
    for slide in prs.slides:
        if slide._element.attrib.get("show") == "0":
            del slide._element.attrib["show"]
            changed = True
    if changed:
        prs.save(dest_path)
        return True
    return False


def _cached_pdf(abs_file, lo, snap):
    """Return path to a cached PDF for the given .pptx, converting if needed.

    Uses file locking so concurrent calls on the same file are safe: the first
    caller converts, subsequent callers find the PDF already cached.
    Caches by the original file's hash so hidden-slide unhiding is transparent.
    """
    file_hash = _file_hash(abs_file)
    os.makedirs(_CACHE_DIR, exist_ok=True)

    pdf_path = os.path.join(_CACHE_DIR, f"{file_hash}.pdf")
    lock_path = os.path.join(_CACHE_DIR, f"{file_hash}.lock")

    lock_fd = open(lock_path, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)

        # Check cache after acquiring lock (another process may have created it)
        if os.path.isfile(pdf_path):
            return pdf_path

        # Convert — use a temp copy with hidden slides unhidden so
        # LibreOffice renders every slide (it skips show="0" slides).
        if snap:
            work_dir = os.path.expanduser("~/snap/libreoffice/common/.ppt-cli-tmp")
            os.makedirs(work_dir, exist_ok=True)
            src_copy = os.path.join(work_dir, os.path.basename(abs_file))
            shutil.copy2(abs_file, src_copy)
            _unhide_slides(abs_file, src_copy)
            convert_src = src_copy
        else:
            work_dir = tempfile.mkdtemp()
            src_copy = os.path.join(work_dir, "input.pptx")
            if not _unhide_slides(abs_file, src_copy):
                # No hidden slides — convert original directly
                convert_src = abs_file
            else:
                convert_src = src_copy

        try:
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

            # Move to cache location
            shutil.move(os.path.join(work_dir, pdfs[0]), pdf_path)
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

        return pdf_path
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()


def cmd_screenshot(args):
    """Render one or more slides as PNG via LibreOffice + pdftoppm."""
    lo, snap = _find_libreoffice()
    abs_file = os.path.abspath(args.file)

    if not os.path.isfile(abs_file):
        _die(f"file not found: {args.file}")

    dpi = args.dpi or 150

    # Determine which slides to render
    if args.all:
        prs = _open(args.file)
        slide_nums = list(range(1, len(prs.slides) + 1))
    else:
        slide_nums = args.slides

    if not slide_nums:
        _die("specify slide number(s) or --all")

    # Get cached PDF (one LibreOffice conversion for all slides)
    pdf_path = _cached_pdf(abs_file, lo, snap)

    # Default output dir: /tmp/ppt-cli-screenshots/{hash}-slides/
    file_hash = _file_hash(abs_file)
    default_dir = os.path.join(_CACHE_DIR, f"{file_hash}-slides")

    # Render each slide from the cached PDF
    outputs = []
    for slide_num in slide_nums:
        if args.output:
            base, ext = os.path.splitext(args.output)
            ext = ext or ".png"
            if len(slide_nums) == 1:
                abs_output = os.path.abspath(f"{base}{ext}")
            else:
                abs_output = os.path.abspath(f"{base}_{slide_num}{ext}")
        else:
            os.makedirs(default_dir, exist_ok=True)
            abs_output = os.path.join(default_dir, f"slide_{slide_num}.png")

        out_stem = os.path.splitext(abs_output)[0]
        r = subprocess.run(
            ["pdftoppm", "-png", "-singlefile",
             "-f", str(slide_num), "-l", str(slide_num),
             "-r", str(dpi), pdf_path, out_stem],
            capture_output=True,
        )
        if r.returncode != 0:
            _die(f"pdftoppm failed (install poppler-utils): {r.stderr.decode()}")
        outputs.append({"slide": slide_num, "output": abs_output})

    if len(outputs) == 1:
        print(json.dumps(outputs[0]))
    else:
        print(json.dumps(outputs))
