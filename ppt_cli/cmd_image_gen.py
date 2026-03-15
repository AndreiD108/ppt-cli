"""Standalone image-gen command: generate images to disk via Gemini."""

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from .helpers import _die
from .image_gen import SUPPORTED_RATIOS, generate_image, generate_image_name


def cmd_image_gen(args):
    if args.ratio and args.ratio not in SUPPORTED_RATIOS:
        _die(f"unsupported aspect ratio: {args.ratio!r}. "
             f"Supported: {', '.join(sorted(SUPPORTED_RATIOS))}")

    if args.resolution not in ("512", "1k", "2k"):
        _die(f"invalid resolution: {args.resolution!r}. Choose from: 512, 1k, 2k")

    if args.count < 1:
        _die(f"--count must be >= 1, got {args.count}")

    # Validate --ref
    ref_images = getattr(args, "ref", None) or []
    if len(ref_images) > 14:
        _die(f"--ref accepts at most 14 images, got {len(ref_images)}")
    for img_path in ref_images:
        if not os.path.isfile(img_path):
            _die(f"reference image not found: {img_path}")

    if not os.environ.get("GEMINI_API_KEY"):
        _die("GEMINI_API_KEY not set. Get one at https://aistudio.google.com/api-keys or https://console.cloud.google.com/apis/credentials")

    # Generate a name for the files
    try:
        name = generate_image_name(args.prompt)
    except Exception:
        name = "generated-image"

    # Determine output paths
    paths = _build_output_paths(args.output, name, args.count)

    # Generate images in parallel
    def _gen(_idx):
        return generate_image(
            args.prompt,
            resolution=args.resolution,
            aspect_ratio=args.ratio,
            grounding=args.grounding,
            reasoning=args.reasoning,
            ref_images=ref_images or None,
        )

    results = []
    failed = 0
    with ThreadPoolExecutor(max_workers=args.count) as pool:
        futures = {pool.submit(_gen, i): i for i in range(args.count)}
        for future in futures:
            idx = futures[future]
            try:
                buf = future.result()
                path = paths[idx]
                os.makedirs(os.path.dirname(path), exist_ok=True)
                data = buf.read()
                with open(path, "wb") as f:
                    f.write(data)
                results.append({"path": path, "bytes": len(data)})
            except Exception as e:
                failed += 1
                print(f"error: image {idx + 1} failed: {e}", file=sys.stderr)

    print(json.dumps({"images": results, "failed": failed}))


def _build_output_paths(output, name, count):
    if output:
        if count == 1:
            return [output]
        base, ext = os.path.splitext(output)
        return [f"{base}_{i + 1}{ext}" for i in range(count)]

    out_dir = "/tmp/ppt-cli/image-gen"
    uid = uuid4().hex[:8]
    if count == 1:
        return [os.path.join(out_dir, f"{name}_{uid}.png")]
    return [
        os.path.join(out_dir, f"{name}_{i + 1}_{uid}.png")
        for i in range(count)
    ]
