
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

if not api_key:
    raise ValueError("GEMINI_API_KEY missing in .env")

print("Creating Gemini client...", flush=True)

client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(
        timeout=120_000
    )
)

try:
    print("Sending request to Gemini...", flush=True)

    response = client.models.generate_content(
        model=model,
        contents="What is the difference between Agents and Agentic AI?"
    )

    print("\nResponse received:", flush=True)
    print(response.text, flush=True)

except Exception as e:
    print("\nRequest failed:", flush=True)
    print(type(e).__name__, flush=True)
    print(str(e), flush=True)

finally:
    client.close()
    print("\nTest completed.", flush=True)
