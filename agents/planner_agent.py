# agents/planner_agent.py

import json
import os
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

# Load .env once
load_dotenv()


class PlannerAgent:
    def __init__(self, system_prompt_path: str):
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY not found in environment. "
                "Ensure it exists in your .env file."
            )

        self.client = Anthropic(api_key=api_key)
        self.system_prompt = Path(system_prompt_path).read_text(encoding="utf-8")

    def run(self, planner_input: dict) -> dict:
        """
        Executes the Planner Agent.

        Input:
            planner_input (dict) — must conform to planner_input.schema.json

        Output:
            planner_output (dict) — strict JSON, conforms to planner_output.schema.json
        """

        response = self.client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=8000,
            temperature=0.3,  # architectural determinism
            system=self.system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": json.dumps(planner_input)
                }
            ]
        )

        raw_text = response.content[0].text.strip()

        try:
            planner_output = json.loads(raw_text)
        except json.JSONDecodeError as e:
            raise ValueError(
                "Planner output is not valid JSON. "
                "This violates the Planner Agent contract."
            ) from e

        return planner_output
