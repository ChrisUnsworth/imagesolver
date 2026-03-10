"""
Puzzle type detector using Claude vision.

Identifies what kind of puzzle is in an uploaded image so the app can
route it to the correct handler. New puzzle types should be added to
KNOWN_TYPES and described in the prompt below.
"""

import base64
import json
import mimetypes

import anthropic

SUPPORTED_MEDIA_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}

# Registry of known puzzle types. Add new entries here as support expands.
KNOWN_TYPES = {
    "sudoku": "Traditional 9x9 sudoku grid",
    "queens": "LinkedIn Queens puzzle — an N-queens variant played on a coloured grid",
    "unknown": "Puzzle type not recognised",
}

PROMPT = f"""You are a puzzle classifier. Examine the image and identify which type of puzzle it contains.

Known puzzle types:
- "sudoku": A traditional 9x9 grid puzzle where each row, column, and 3x3 box must contain the digits 1-9.
- "queens": The LinkedIn Queens game — an N×N grid divided into coloured regions where exactly one queen must be placed per row, column, and region.

Return ONLY a JSON object — no explanation, no markdown fences:

{{
  "type": "<sudoku|queens|unknown>",
  "description": "<one sentence describing what you see>"
}}

If the image does not match any known type, use "unknown".
"""


def detect_puzzle_type(image_path: str) -> dict:
    """
    Returns a dict with keys:
        type        : str  — one of "sudoku", "queens", "unknown"
        description : str  — brief description of what Claude observed
    """
    client = anthropic.Anthropic()

    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    media_type, _ = mimetypes.guess_type(image_path)
    if media_type not in SUPPORTED_MEDIA_TYPES:
        media_type = "image/jpeg"

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {"type": "text", "text": PROMPT},
                ],
            }
        ],
    )

    response_text = message.content[0].text.strip()

    if response_text.startswith("```"):
        lines = response_text.splitlines()
        response_text = "\n".join(lines[1:-1]).strip()

    result = json.loads(response_text)

    if result.get("type") not in KNOWN_TYPES:
        result["type"] = "unknown"

    return result
