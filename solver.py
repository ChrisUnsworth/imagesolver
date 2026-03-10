import base64
import json
import mimetypes

import anthropic

SUPPORTED_MEDIA_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}

PROMPT = """Analyze this sudoku puzzle image.

Identify all cells that contain numbers — whether pre-printed clues or handwritten entries.

Return ONLY a JSON object with this exact structure. No explanation, no markdown fences, just raw JSON:

{
  "grid": [
    [row1col1, row1col2, row1col3, row1col4, row1col5, row1col6, row1col7, row1col8, row1col9],
    [row2col1, row2col2, row2col3, row2col4, row2col5, row2col6, row2col7, row2col8, row2col9],
    [row3col1, row3col2, row3col3, row3col4, row3col5, row3col6, row3col7, row3col8, row3col9],
    [row4col1, row4col2, row4col3, row4col4, row4col5, row4col6, row4col7, row4col8, row4col9],
    [row5col1, row5col2, row5col3, row5col4, row5col5, row5col6, row5col7, row5col8, row5col9],
    [row6col1, row6col2, row6col3, row6col4, row6col5, row6col6, row6col7, row6col8, row6col9],
    [row7col1, row7col2, row7col3, row7col4, row7col5, row7col6, row7col7, row7col8, row7col9],
    [row8col1, row8col2, row8col3, row8col4, row8col5, row8col6, row8col7, row8col8, row8col9],
    [row9col1, row9col2, row9col3, row9col4, row9col5, row9col6, row9col7, row9col8, row9col9]
  ]
}

Rules:
- Use 0 for empty cells
- Use the digit (1-9) for filled cells
- The grid must be exactly 9 rows, each with exactly 9 values
- Row 1 is the top row; Row 9 is the bottom row
- Column 1 is the leftmost; Column 9 is the rightmost
"""


def analyze_sudoku(image_path: str) -> dict:
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    media_type, _ = mimetypes.guess_type(image_path)
    if media_type not in SUPPORTED_MEDIA_TYPES:
        media_type = "image/jpeg"

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
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

    # Strip markdown code fences if Claude adds them anyway
    if response_text.startswith("```"):
        lines = response_text.splitlines()
        response_text = "\n".join(lines[1:-1]).strip()

    result = json.loads(response_text)

    grid = result.get("grid", [])
    if len(grid) != 9 or any(len(row) != 9 for row in grid):
        raise ValueError(f"Claude returned an invalid grid shape: {len(grid)} rows")

    result["filled_count"] = sum(1 for row in grid for cell in row if cell != 0)
    result["empty_count"] = 81 - result["filled_count"]

    return result
