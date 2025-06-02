import re
from transformers import AutoTokenizer

import os
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACE_HUB_TOKEN")
if not HF_TOKEN:
    raise RuntimeError("HUGGINGFACE_HUB_TOKEN not set in .env")

tokenizer = AutoTokenizer.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.3",
    token=HF_TOKEN
)

def normalize_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r" -\n", "", text)
    return text.strip()

def chunk_text(text: str, max_tokens=200):
    """Break text into chunks with token count ≤ max_tokens."""
    words = text.split()
    chunks, current, current_len = [], [], 0

    for word in words:
        token_len = len(tokenizer.tokenize(word))
        if current_len + token_len > max_tokens:
            chunks.append(" ".join(current))
            current, current_len = [], 0
        current.append(word)
        current_len += token_len

    if current:
        chunks.append(" ".join(current))

    return chunks
