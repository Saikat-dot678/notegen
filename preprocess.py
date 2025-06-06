import re

def normalize_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)  # remove excessive spaces
    text = re.sub(r"[^\x00-\x7F]+", " ", text)  # remove non-ASCII chars
    return text.strip()

def chunk_text(text: str, max_tokens: int = 100000) -> list:
    words = text.split()
    chunks = []
    chunk = []
    token_count = 0

    for word in words:
        chunk.append(word)
        token_count += 1
        if token_count >= max_tokens:
            chunks.append(" ".join(chunk))
            chunk = []
            token_count = 0

    if chunk:
        chunks.append(" ".join(chunk))

    return chunks
