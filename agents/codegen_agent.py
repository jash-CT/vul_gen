# agents/codegen_agent.py

import json
import os
import re
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


FILE_BLOCK_RE = re.compile(
    r"<<<FILE:(.*?)>>>\n(.*?)\n<<<END FILE>>>",
    re.DOTALL
)


class CodeGenAgent:
    def __init__(self, system_prompt_path: str):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY missing in environment")

        self.client = Anthropic(api_key=api_key)
        self.system_prompt = Path(system_prompt_path).read_text(encoding="utf-8")

    def generate_unit(
        self,
        planner_output: dict,
        unit_description: str,
        output_path: Path
    ):
        prompt = {
            "planner_output": planner_output,
            "unit_to_generate": unit_description
        }

        response = self.client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=8000,
            temperature=0.4,
            system=self.system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": json.dumps(prompt)
                }
            ]
        )

        raw_text = response.content[0].text

        matches = FILE_BLOCK_RE.findall(raw_text)

        if not matches:
            raise RuntimeError(
                "CodeGen output contained no file blocks. "
                "This violates the CodeGen contract."
            )

        for relative_path, content in matches:
            file_path = output_path / relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)

        return len(matches)
