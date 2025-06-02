# test_generate.py

from generate import generate_chunk_notes

if __name__ == "__main__":
    sample = (
        "In supervised learning, we train a model on labeled data. "
        "The goal is to minimize a loss function via gradient descent."
    )
    notes = generate_chunk_notes(sample, max_new_tokens=256)
    print("TITLE:", notes["title"])
    print("\nBULLETS:")
    for b in notes["bullets"]:
        print(" •", b)
    print("\nDIAGRAM PROMPT:", notes["diagram_prompt"])
