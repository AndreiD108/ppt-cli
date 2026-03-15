"""Content insertion commands: add-image, add-textbox, add-table, delete-shape."""

import csv
import io
import os

from .helpers import (_die, _open, _get_slide, _find_shape, _save,
                      _parse_length, _parse_color, Inches, Pt)
from .image_gen import SUPPORTED_RATIOS as _SUPPORTED_RATIOS


def _crop_to_ratio(image_source, target_w_emu, target_h_emu):
    """Crop image minimally (center crop) to match the target aspect ratio."""
    from PIL import Image

    img = Image.open(image_source)
    img_w, img_h = img.size
    target_ratio = target_w_emu / target_h_emu
    img_ratio = img_w / img_h

    if abs(img_ratio - target_ratio) / max(target_ratio, 1e-9) < 0.01:
        # Already close enough — return as-is
        if hasattr(image_source, "seek"):
            image_source.seek(0)
            return image_source
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf

    if img_ratio > target_ratio:
        # Image is wider — crop width
        new_w = int(img_h * target_ratio)
        offset = (img_w - new_w) // 2
        box = (offset, 0, offset + new_w, img_h)
    else:
        # Image is taller — crop height
        new_h = int(img_w / target_ratio)
        offset = (img_h - new_h) // 2
        box = (0, offset, img_w, offset + new_h)

    cropped = img.crop(box)
    buf = io.BytesIO()
    cropped.save(buf, format="PNG")
    buf.seek(0)
    return buf


def _guess_ratio(w_emu, h_emu):
    """Pick the closest supported aspect ratio if within 15% relative error."""
    if not w_emu or not h_emu:
        return None
    actual = w_emu / h_emu
    best, best_err = None, float("inf")
    for r in _SUPPORTED_RATIOS:
        a, b = r.split(":")
        target = int(a) / int(b)
        err = abs(actual - target) / target
        if err < best_err:
            best, best_err = r, err
    return best if best_err < 0.15 else None


def cmd_add_image(args):
    prompt = getattr(args, "prompt", None)
    image = getattr(args, "image", None)

    # Mutual exclusivity
    if prompt and image:
        _die("provide either an image path or --prompt, not both")
    if not prompt and not image:
        _die("provide an image path or --prompt")

    # Validate --ref
    ref_images = getattr(args, "ref", None) or []
    if len(ref_images) > 14:
        _die(f"--ref accepts at most 14 images, got {len(ref_images)}")
    for img_path in ref_images:
        if not os.path.isfile(img_path):
            _die(f"reference image not found: {img_path}")

    # Validate prompt-only flags
    prompt_only_flags = {
        "--resolution": getattr(args, "resolution", "1k") != "1k",
        "--ratio": getattr(args, "ratio", None) is not None,
        "--grounding": getattr(args, "grounding", None) is not None,
        "--reasoning": getattr(args, "reasoning", False),
        "--ref": len(ref_images) > 0,
    }
    if not prompt:
        for flag, used in prompt_only_flags.items():
            if used:
                _die(f"{flag} can only be used with --prompt")

    prs = _open(args.file)
    slide = _get_slide(prs, args.slide)
    x = _parse_length(args.x) if args.x else Inches(1)
    y = _parse_length(args.y) if args.y else Inches(1)
    w = _parse_length(args.w) if args.w else None
    h = _parse_length(args.h) if args.h else None

    if prompt:
        # Validate ratio
        ratio = getattr(args, "ratio", None)
        if ratio and ratio not in _SUPPORTED_RATIOS:
            _die(f"unsupported aspect ratio: {ratio!r}. "
                 f"Supported: {', '.join(sorted(_SUPPORTED_RATIOS))}")

        if not os.environ.get("GEMINI_API_KEY"):
            _die("GEMINI_API_KEY not set. Get one at https://aistudio.google.com/api-keys or https://console.cloud.google.com/apis/credentials")

        # Auto-guess ratio from w/h if not explicit
        if not ratio and w and h:
            ratio = _guess_ratio(w, h)

        from .image_gen import generate_image, generate_image_name

        buf = generate_image(
            prompt,
            resolution=args.resolution,
            aspect_ratio=ratio,
            grounding=args.grounding,
            reasoning=args.reasoning,
            ref_images=ref_images or None,
        )

        if w and h:
            buf = _crop_to_ratio(buf, w, h)
        kwargs = {"image_file": buf, "left": x, "top": y}
        if w:
            kwargs["width"] = w
        if h:
            kwargs["height"] = h
        pic = slide.shapes.add_picture(**kwargs)

        # Set a meaningful name on the picture shape
        try:
            name = generate_image_name(prompt)
        except Exception:
            name = "generated-image"
        pic.name = name
    else:
        if not os.path.isfile(image):
            _die(f"image not found: {image}")

        img_source = image
        if w and h:
            img_source = _crop_to_ratio(image, w, h)
        kwargs = {"image_file": img_source, "left": x, "top": y}
        if w:
            kwargs["width"] = w
        if h:
            kwargs["height"] = h
        pic = slide.shapes.add_picture(**kwargs)

    _save(prs, args.file, args.output,
          extra={"shape_id": pic.shape_id, "name": pic.name})


def cmd_add_textbox(args):
    prs = _open(args.file)
    slide = _get_slide(prs, args.slide)
    x = _parse_length(args.x) if args.x else Inches(1)
    y = _parse_length(args.y) if args.y else Inches(1)
    w = _parse_length(args.w) if args.w else Inches(4)
    h = _parse_length(args.h) if args.h else Inches(1)

    txBox = slide.shapes.add_textbox(x, y, w, h)
    tf = txBox.text_frame
    tf.word_wrap = True

    lines = args.text.split("\\n") if "\\n" in args.text else [args.text]
    for i, line in enumerate(lines):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        run = para.add_run()
        run.text = line
        if args.font_size:
            run.font.size = Pt(args.font_size)
        if args.font_color:
            run.font.color.rgb = _parse_color(args.font_color)
        if args.bold:
            run.font.bold = True

    _save(prs, args.file, args.output,
          extra={"shape_id": txBox.shape_id, "name": txBox.name})


def cmd_add_table(args):
    prs = _open(args.file)
    slide = _get_slide(prs, args.slide)
    x = _parse_length(args.x) if args.x else Inches(1)
    y = _parse_length(args.y) if args.y else Inches(2)

    if not os.path.isfile(args.csv):
        _die(f"csv file not found: {args.csv}")
    with open(args.csv, newline="") as f:
        rows = list(csv.reader(f))
    if not rows:
        _die("csv file is empty")

    n_rows = len(rows)
    n_cols = max(len(r) for r in rows)
    w = _parse_length(args.w) if args.w else Inches(n_cols * 1.5)
    h = _parse_length(args.h) if args.h else Inches(n_rows * 0.4)

    table_shape = slide.shapes.add_table(n_rows, n_cols, x, y, w, h)
    table = table_shape.table

    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            if ci < n_cols:
                table.cell(ri, ci).text = val

    _save(prs, args.file, args.output,
          extra={"shape_id": table_shape.shape_id, "name": table_shape.name,
                 "rows": n_rows, "cols": n_cols})


def cmd_delete_shape(args):
    prs = _open(args.file)
    slide = _get_slide(prs, args.slide)
    shape = _find_shape(slide, args.shape_id)
    sp = shape._element
    sp.getparent().remove(sp)
    _save(prs, args.file, args.output)
