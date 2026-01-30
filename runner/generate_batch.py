# runner/generate_batch.py

import json
import sys
from pathlib import Path

# Ensure project root is on path when running this script directly
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from graph.graph import build_graph


def load_base_planner_input() -> dict:
    """
    Base input template.
    You can modify business_logic_description per run if needed.
    """
    return {
        "business_logic_description": (
            "A multi-tenant enterprise platform that handles user onboarding, "
            "order processing, analytics, third-party integrations, and internal "
            "operations dashboards across multiple teams and regions."
        ),
        "constraints": {
            "scale": {
                "loc_range": "10k-30k",
                "services": "6-10"
            },
            "languages": "mixed",
            "vulnerability_count": 12,
            "vulnerability_classes": [
                "authz-boundary",
                "async-consistency",
                "service-trust",
                "data-exposure",
                "multi-tenant",
                "secrets",
                "logging",
                "supply-chain",
                "deserialization",
                "business-logic"
            ]
        }
    }


def persist_vulnerabilities(codebase_path: Path, planner_output: dict):
    """
    Vulnerabilities are derived STRICTLY from planner output.
    No code inspection. No injection.
    """
    vuln_report = {
        "summary": planner_output["expected_vulnerabilities"],
        "vulnerabilities": planner_output["risk_analysis"]
    }

    (codebase_path / "vulnerabilities.json").write_text(
        json.dumps(vuln_report, indent=2)
    )


def run_batch(total_codebases: int):
    graph = build_graph()
    base_input = load_base_planner_input()

    for i in range(total_codebases):
        print(f"\n=== Generating codebase {i + 1}/{total_codebases} ===")

        state = {
            "planner_input": base_input,
            "codebase_index": i + 1,
        }

        final_state = graph.invoke(state)

        codebase_path = Path(final_state["codebase_path"])
        planner_output = final_state["planner_output"]

        persist_vulnerabilities(codebase_path, planner_output)

        print(f"✔ Generated {codebase_path}")


if __name__ == "__main__":
    # CHANGE THIS NUMBER AS NEEDED (e.g. 500, 1000)
    run_batch(total_codebases=5)
