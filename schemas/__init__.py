import json
from pathlib import Path


def load_planner_input_schema():
    return json.loads(
        Path("schemas/planner_input.schema.json").read_text()
    )


def load_planner_output_schema():
    return json.loads(
        Path("schemas/planner_output.schema.json").read_text()
    )
