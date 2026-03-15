"""Google Gemini image generation engine."""

import io
import json
import os
import time

SUPPORTED_RATIOS = {
    "1:1", "9:16", "16:9", "3:4", "4:3",
    "3:2", "2:3", "5:4", "4:5", "21:9",
    "9:21", "1:4", "4:1", "1:8", "8:1",
}

IMAGE_MODEL = "gemini-3.1-flash-image-preview"
NAME_MODEL = "gemini-2.5-flash-lite"


def _get_client():
    from google import genai
    return genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def _build_tools(grounding):
    from google.genai import types

    if grounding is None:
        return []
    if grounding == "search":
        return [types.Tool(googleSearch=types.GoogleSearch())]
    if grounding == "image":
        return [types.Tool(googleSearch=types.GoogleSearch(
            search_types=types.SearchTypes(imageSearch=types.ImageSearch()),
        ))]
    if grounding == "full":
        return [types.Tool(googleSearch=types.GoogleSearch(
            search_types=types.SearchTypes(
                webSearch=types.WebSearch(),
                imageSearch=types.ImageSearch(),
            ),
        ))]
    return []


def generate_image(prompt, resolution="1k", aspect_ratio=None, grounding=None,
                   reasoning=False, ref_images=None):
    """Generate an image from a text prompt. Returns io.BytesIO with PNG data.

    ref_images: optional list of file paths to include as reference images.
    """
    from google.genai import types
    from PIL import Image

    config_kwargs = {
        "image_config": types.ImageConfig(
            image_size=resolution,
            **({"aspect_ratio": aspect_ratio} if aspect_ratio else {}),
        ),
        "response_modalities": ["IMAGE"],
    }
    if reasoning:
        config_kwargs["thinking_config"] = types.ThinkingConfig(
            thinking_level="MINIMAL",
        )
    tools = _build_tools(grounding)
    if tools:
        config_kwargs["tools"] = tools

    config = types.GenerateContentConfig(**config_kwargs)

    content_parts = [prompt]
    if ref_images:
        for img_path in ref_images:
            content_parts.append(Image.open(img_path))
    contents = content_parts

    client = _get_client()
    last_error = None

    for attempt in range(3):
        if attempt > 0:
            time.sleep(2 * attempt)
        data_buffer = bytearray()
        try:
            for chunk in client.models.generate_content_stream(
                model=IMAGE_MODEL,
                contents=contents,
                config=config,
            ):
                if chunk.parts:
                    for part in chunk.parts:
                        if part.inline_data and part.inline_data.data:
                            data_buffer.extend(part.inline_data.data)

            if not data_buffer:
                last_error = "API returned 0 bytes"
                continue

            buf = io.BytesIO(bytes(data_buffer))
            buf.seek(0)
            return buf

        except Exception as e:
            err_str = str(e)
            if "timed out" in err_str.lower() or "timeout" in err_str.lower():
                last_error = "timed out (60s)"
            else:
                last_error = err_str
            continue

    raise RuntimeError(f"image generation failed after 3 attempts: {last_error}")


def generate_image_name(prompt):
    """Generate a short file name for an image based on the prompt."""
    from google.genai import types
    from google import genai as genai_module

    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0),
        response_mime_type="application/json",
        response_schema=genai_module.types.Schema(
            type=genai_module.types.Type.OBJECT,
            required=["file_name"],
            properties={
                "file_name": genai_module.types.Schema(
                    type=genai_module.types.Type.STRING,
                ),
            },
        ),
        system_instruction=[types.Part.from_text(
            text="You are an image file naming assistant. Return a name for "
                 "the file, without extension.",
        )],
    )

    client = _get_client()
    response = client.models.generate_content(
        model=NAME_MODEL,
        contents=prompt,
        config=config,
    )
    return json.loads(response.text)["file_name"]
