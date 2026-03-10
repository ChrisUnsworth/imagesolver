"""
LinkedIn Queens puzzle analyser using Claude vision.

Extracts the N×N colour-region grid from an image and returns it as a
2-D array of integer region IDs (1 … N).
"""

import base64
import json
import mimetypes

import anthropic

SUPPORTED_MEDIA_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}

PROMPT = """Analyze this LinkedIn Queens puzzle image.

The puzzle is an N×N grid divided into N distinctly coloured regions.
Each cell belongs to exactly one region.

Your tasks:
1. Determine N (the grid size — number of rows = columns = regions).
2. For every cell assign a region ID (integer 1 to N).
   - Assign IDs by scanning left-to-right, top-to-bottom.
   - The first colour you encounter gets ID 1, the next new colour gets ID 2, and so on.
   - All cells sharing the same colour must share the same ID.

Return ONLY this JSON — no explanation, no markdown fences:

{
  "size": N,
  "grid": [
    [region_id, region_id, ...],
    ...
  ]
}

The grid must have exactly N rows, each containing exactly N integers in the range 1–N.
"""


def analyze_queens(image_path: str) -> dict:
    """
    Returns:
        {
            "size" : int             — grid dimension N,
            "grid" : list[list[int]] — N×N array of region IDs (1-indexed),
        }
    Raises ValueError on malformed responses.
    """
    client = anthropic.Anthropic()

    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    media_type, _ = mimetypes.guess_type(image_path)
    if media_type not in SUPPORTED_MEDIA_TYPES:
        media_type = "image/jpeg"

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
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

    n = result.get("size")
    grid = result.get("grid", [])

    if not isinstance(n, int) or n < 1:
        raise ValueError(f"Invalid grid size returned: {n!r}")
    if len(grid) != n or any(len(row) != n for row in grid):
        raise ValueError(f"Grid shape mismatch: expected {n}×{n}, got {len(grid)} rows")

    return result
