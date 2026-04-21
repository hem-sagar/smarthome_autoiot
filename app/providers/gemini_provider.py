from __future__ import annotations
import json
import re
from app.config import GEMINI_API_KEY, GEMINI_MODEL, USE_GEMINI

LAST_GEMINI_ERROR = ""


def _parse_json_from_text(text: str) -> dict:
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        raise ValueError("No JSON in Gemini output")
    return json.loads(match.group(0))


def get_last_gemini_error() -> str:
    return LAST_GEMINI_ERROR


def generate_with_gemini(prompt: str) -> dict | None:
    global LAST_GEMINI_ERROR
    LAST_GEMINI_ERROR = ""

    if not USE_GEMINI or not GEMINI_API_KEY:
        LAST_GEMINI_ERROR = "Gemini is disabled or missing GEMINI_API_KEY."
        return None
    try:
        from google import genai

        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        text = getattr(response, "text", "") or ""
        if not text:
            raise ValueError("Gemini returned an empty response body")
        return _parse_json_from_text(text)
    except Exception as exc:
        LAST_GEMINI_ERROR = f"{type(exc).__name__}: {exc}"
        return None
