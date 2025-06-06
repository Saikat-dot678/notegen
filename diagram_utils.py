import os
import uuid
from diagrams import Diagram, Cluster
from diagrams.custom import Custom

# Dummy placeholder diagram generator
# Replace with actual logic as needed
def gen_diagram(diagram_prompt):
    elements = diagram_prompt.get("elements", [])
    if not elements or len(elements) < 2:
        return None

    # For now, generate dummy diagram image
    path = f"static/diagram_{uuid.uuid4().hex}.png"

    with Diagram(name="Generated Diagram", show=False, outformat="png", filename=path.replace(".png", "")):
        last = None
        for elem in elements:
            node = Custom(elem, "./static/box.png")  # you can replace with any icon
            if last:
                last >> node
            last = node

    return path
