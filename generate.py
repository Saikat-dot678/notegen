import os
import requests
from dotenv import load_dotenv

# Load your OpenRouter API Key from .env
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL = "deepseek/deepseek-chat:free"

PROMPT_TEMPLATE = """
You are an expert academic assistant specializing in creating exceptionally comprehensive, granular, and well-structured study materials.

Your task is to generate highly detailed and meticulously organized study notes from the provided text. Ensure that no relevant piece of information is omitted, no matter how minor it may seem. For every concept, definition, example, use case, and distinguishing characteristic, provide an in-depth explanation.

Your notes must adhere to the following structural and formatting guidelines:


Exhaustive Coverage: Extract and present every single piece of information available in the source text.

Clear and Logical Headings: Use a hierarchical structure with multiple levels of headings (e.g., H1, H2, H3) to organize information logically.

In-depth Explanations: Provide thorough explanations for all key concepts, definitions, and examples, breaking down complex ideas into digestible components.

Detailed Bullet Points: Present information using bullet points, ensuring each distinct piece of information within a bullet point is captured.

Comprehensive Summaries: Include summaries for major sections, synthesizing the detailed points.

Illustrative ASCII Diagrams: Incorporate ASCII diagrams to visually represent architectures or relationships, where helpful and applicable.

Consistent Indentation: Maintain clear and consistent indentation to enhance readability and hierarchy.

Crucially, do NOT use JSON formatting or any programmatic data structures in the output. The formatting should rely exclusively on standard text, Markdown elements, and ASCII visuals for maximum readability as a study document.

Here is the content to be summarized and structured into these detailed notes:

\"\"\"{chunk}\"\"\"
"""
def generate_chunk_notes(chunk: str, max_tokens: int = 4096):
    prompt = PROMPT_TEMPLATE.format(chunk=chunk)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "AI Notes Generator"
    }

    data = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

    if response.status_code == 200:
        content = response.json()['choices'][0]['message']['content']
        return {
            "title": "Generated Notes",
            "content": content.strip()
        }
    else:
        print("❌ API Error:", response.status_code, response.text)
        raise Exception("API call failed")
