# diagrams.py

import subprocess
import os
from typing import List, Optional, Union
import logging
from graphviz import Digraph

def make_mermaid(mmd: str, out_path: str) -> str:
    with open("temp.mmd", "w") as f:
        f.write(mmd)
    subprocess.run(["mmdc", "-i", "temp.mmd", "-o", out_path], check=True)
    os.remove("temp.mmd")
    return out_path

def make_flowchart(steps: List[str], out_prefix: str) -> str:
    dot = Digraph(format="png")
    for i, label in enumerate(steps):
        dot.node(label)
        if i > 0:
            dot.edge(steps[i-1], label)
    filename = dot.render(out_prefix, cleanup=True)
    return filename

def gen_diagram(diagram_obj: Union[dict, str, None]) -> Optional[str]:
    """
    Generate diagram image path based on the diagram specification dict.

    Expected diagram_obj format:
    {
      "type": "venn" | "flowchart" | "hierarchy" | "timeline" | "custom",
      "elements": ["Label1", "Label2", ...],
      "description": "Text describing the layout."
    }

    Returns path to generated diagram image or None if unable.
    """
    if not diagram_obj:
        logging.warning("gen_diagram called with empty diagram_obj.")
        return None

    # If a string is passed by mistake, attempt minimal parsing or skip
    if isinstance(diagram_obj, str):
        logging.warning("Diagram prompt is a string, expected dict. Returning None.")
        return None

    if not isinstance(diagram_obj, dict):
        logging.error(f"Invalid type for diagram_obj: {type(diagram_obj)}. Expected dict.")
        return None

    diagram_type = str(diagram_obj.get("type", "")).lower()
    elements = diagram_obj.get("elements", [])
    description = diagram_obj.get("description", "")

    # Basic validation
    if not isinstance(elements, list) or not all(isinstance(el, str) for el in elements):
        logging.warning(f"Invalid elements format in diagram_obj: {elements}")
        elements = []

    try:
        if diagram_type == "venn" and len(elements) >= 2:
            a, b = elements[0], elements[1]
            mmd = (
                "graph TB\n"
                f"  subgraph {a}[\"{a}\"]\n"
                "  end\n"
                f"  subgraph {b}[\"{b}\"]\n"
                "  end\n"
                f"  {a} --- {b}"
            )
            return make_mermaid(mmd, "venn.png")

        if diagram_type == "flowchart" and len(elements) >= 2:
            return make_flowchart(elements, "flowchart")

        if diagram_type == "hierarchy" and len(elements) >= 1:
            # Example: root is first element, rest are children
            dot = Digraph(format='png')
            root = elements[0]
            dot.node(root)
            for child in elements[1:]:
                dot.node(child)
                dot.edge(root, child)
            filename = dot.render("hierarchy", cleanup=True)
            return filename

        if diagram_type == "timeline" and len(elements) >= 1:
            # Simple linear timeline
            dot = Digraph(format='png')
            for i, event in enumerate(elements):
                dot.node(event)
                if i > 0:
                    dot.edge(elements[i-1], event)
            filename = dot.render("timeline", cleanup=True)
            return filename

        # Custom or unknown type: could implement image generation from description here
        logging.info(f"Diagram type '{diagram_type}' not specifically handled, returning None.")
        return None

    except Exception as e:
        logging.error(f"Error generating diagram: {e}", exc_info=True)
        return None
