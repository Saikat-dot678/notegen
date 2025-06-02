import os
import json
import torch
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

# 1. Load .env variables
load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACE_HUB_TOKEN")
if not HF_TOKEN:
    raise RuntimeError("HUGGINGFACE_HUB_TOKEN not set in .env")

# 2. Model and prompt
MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
PROMPT = """
You are an expert academic assistant specialized in converting lecture or textbook content into high-quality study notes. 
Given the following text chunk, respond **only** with a JSON object having exactly three keys:

{{
  "title":       "<a 5-7 word section heading>",
  "bullets":     ["<bullet 1>", "<bullet 2>", …], 
  "diagram":     "<one-sentence diagram instruction>"
}}

Requirements:
1. **Title**: Summarize the core idea of this chunk in 5–7 words.
2. **Bullets**:
   - Provide **3–5** distinct, standalone bullet points.
   - Each bullet should convey a single key fact or insight.
   - Use precise terminology and avoid filler language.
   - **Do not** repeat any bullet content you have output for previous chunks.
   - If two ideas are closely related, merge them into one clear bullet.
3. **Diagram** (exactly one object):  
   - **type**: choose from a small set (`venn`, `flowchart`, `hierarchy`, `timeline`, or `custom` if none of the above fit).  
   - **elements**: list the key labels/data points to include (e.g. `["Structured", "Unstructured"]`).  
   - **description**: a single sentence describing how to arrange those elements (e.g. `"Draw a Venn diagram showing overlap between Structured and Unstructured data."`). 
4. **Formatting**: Return **valid JSON only**—no extra text, no markdown.

Here is the text chunk to summarize:

\"\"\"{chunk}\"\"\"
"""

# 3. Load tokenizer with auth
tokenizer = AutoTokenizer.from_pretrained(MODEL, token=HF_TOKEN)

# 4. Load quantized model (8-bit fallback to 4-bit)
def load_model():
    try:
        return AutoModelForCausalLM.from_pretrained(
            MODEL,
            token=HF_TOKEN,
            quantization_config=BitsAndBytesConfig(load_in_8bit=True),
            device_map="auto"
        )
    except RuntimeError:
        return AutoModelForCausalLM.from_pretrained(
            MODEL,
            token=HF_TOKEN,
            quantization_config=BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype="bfloat16"
            ),
            device_map="auto"
        )

model = load_model()
model.eval()
def clean_json_text(text: str) -> str:
    """
    Cleans model output text to extract JSON string.
    Removes markdown code fences ``` and any text before/after JSON.
    """
    text = text.strip()
    # Remove triple backticks and language hints if present
    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()
        # Remove first and last lines which are ```
        text = "\n".join(lines[1:-1]).strip()
    # Optionally, try to find JSON substring (first { to last })
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end+1]
    return text


def parse_response(text: str):
    try:
        cleaned_text = clean_json_text(text)
        obj = json.loads(cleaned_text)
        return {
            "title": obj.get("title", "").strip(),
            "bullets": obj.get("bullets", []),
            "diagram_prompt": obj.get("diagram", {})  # keep diagram as dict
        }

    except json.JSONDecodeError as e:
        print("❌ Failed to parse LLM output after cleaning:\n", cleaned_text)
        raise e


def generate_chunk_notes(chunk: str, max_new_tokens: int = 512):
    prompt = PROMPT.format(chunk=chunk)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            pad_token_id=tokenizer.eos_token_id,
            do_sample=False  # deterministic generation
        )

    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Remove prompt prefix from output if present
    if decoded.startswith(prompt):
        decoded = decoded[len(prompt):].strip()
    else:
        # fallback: remove chunk if inside output
        if chunk in decoded:
            decoded = decoded.split(chunk, 1)[-1].strip()

    return parse_response(decoded)
