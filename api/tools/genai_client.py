import os
from dotenv import load_dotenv
from google import genai


load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# model_to_use = 'gemini-2.0-flash-lite'
model_to_use = 'gemini-1.5-flash-8b'


def generate_content(contents: str):
    response = client.models.generate_content(
        model=model_to_use,
        config=generation_config,
        contents=contents,
    )
    return response


