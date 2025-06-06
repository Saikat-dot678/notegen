from generate import generate_chunk_notes
import json

if __name__ == "__main__":
    sample_chunk = """
    Photosynthesis is the process by which green plants and some other organisms use sunlight to synthesize foods from carbon dioxide and water.
    It generally involves the green pigment chlorophyll and generates oxygen as a byproduct.
    """

    try:
        notes = generate_chunk_notes(sample_chunk)
        print("Generated Notes JSON:")
        print(json.dumps(notes, indent=2))
    except Exception as e:
        print("Error during note generation:", e)
