
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from .env")

client = genai.Client(api_key=API_KEY)


def get_llm_response(prompt: str) -> str:
    """Generate a normal text response."""
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return response.text or ""


async def get_json_llm_response(prompt: str) -> str:
    """Generate a response in JSON format asynchronously."""

    response = await client.aio.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2
        )
    )

    return response.text or ""