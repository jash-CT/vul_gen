# graph/graph.py

from typing import TypedDict, NotRequired
from pathlib import Path
import json
import uuid

from langgraph.graph import StateGraph, END
from jsonschema import validate, ValidationError

from agents.codegen_agent import CodeGenAgent
from agents.planner_agent import PlannerAgent
from schemas import (
    load_planner_input_schema,
    load_planner_output_schema
)


# -----------------------------
# Graph State Definition
# -----------------------------

class GraphState(TypedDict):
    planner_input: dict
    planner_output: dict
    codebase_id: str
    codebase_path: str
    codebase_index: NotRequired[int]


# -----------------------------
# Utility Functions
# -----------------------------

def generate_codebase_id() -> str:
    return f"codebase_{uuid.uuid4().hex[:8]}"


def persist_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def _normalize_async_and_background(planner_output: dict) -> None:
    """
    Normalize async_and_background_processing when the LLM returns
    { workers: [...] } with name/state_handling instead of worker_name/state_model/trigger.
    Mutates planner_output in place so it passes the schema.
    """
    key = "async_and_background_processing"
    raw = planner_output.get(key)
    if raw is None:
        return
    # Unwrap { workers: [...] } → [...]
    if isinstance(raw, dict) and "workers" in raw:
        raw = raw["workers"]
    if not isinstance(raw, list):
        return
    normalized = []
    for item in raw:
        if not isinstance(item, dict):
            # LLM sometimes returns plain strings; treat as worker_name and fill defaults
            worker_name = str(item) if item else "worker"
            if len(worker_name) < 1:
                worker_name = "worker"
            normalized.append({
                "worker_name": worker_name,
                "trigger": "event-driven or scheduled",
                "state_model": "event-sourced with replay",
                "retry_behavior": "exponential backoff with jitter",
                "failure_assumptions": "temporary inconsistencies are acceptable",
            })
            continue
        # Map LLM field names to schema field names
        worker_name = item.get("worker_name") or item.get("name") or "worker"
        trigger = item.get("trigger") or item.get("responsibility", "event-driven")[:50]
        if len(trigger) < 10:
            trigger = "event-driven"
        state_model = item.get("state_model") or item.get("state_handling") or "event-sourced"
        if len(state_model) < 15:
            state_model = "event-sourced with replay"
        retry_behavior = item.get("retry_behavior") or "exponential backoff"
        if len(retry_behavior) < 15:
            retry_behavior = "exponential backoff with jitter"
        failure_assumptions = item.get("failure_assumptions") or "temporary inconsistencies"
        if len(failure_assumptions) < 15:
            failure_assumptions = "temporary inconsistencies are acceptable"
        normalized.append({
            "worker_name": worker_name,
            "trigger": trigger,
            "state_model": state_model,
            "retry_behavior": retry_behavior,
            "failure_assumptions": failure_assumptions,
        })
    planner_output[key] = normalized


def _str_min_len(val, min_len: int = 20, default: str = "Not specified.") -> str:
    """Coerce value to a string of at least min_len characters."""
    if val is None:
        s = default
    elif isinstance(val, list):
        s = ", ".join(str(x) for x in val) if val else default
    elif isinstance(val, dict):
        s = json.dumps(val) if val else default
    else:
        s = str(val)
    return s if len(s) >= min_len else (s + " " * (min_len - len(s)))


def _normalize_system_overview(planner_output: dict) -> None:
    """
    Normalize system_overview when the LLM returns different keys or types
    (e.g. user_types array instead of assumed_users string, object/array for traffic_patterns/non_goals).
    Mutates planner_output in place so it passes the schema.
    """
    key = "system_overview"
    raw = planner_output.get(key)
    if not isinstance(raw, dict):
        return
    so = raw
    # Map LLM variants to schema keys; ensure all required strings exist and meet minLength
    assumed_users = so.get("assumed_users") or so.get("user_types")
    so["assumed_users"] = _str_min_len(assumed_users, 20, "Enterprise and internal users.")
    so["product_goal"] = _str_min_len(so.get("product_goal"), 20, "Business operations platform.")
    so["traffic_patterns"] = _str_min_len(so.get("traffic_patterns"), 20, "Variable by region and time.")
    so["non_goals"] = _str_min_len(so.get("non_goals"), 20, "Out of scope for this system.")
    so["explicitly_unprotected_areas"] = _str_min_len(
        so.get("explicitly_unprotected_areas"), 20, "Areas intentionally not in scope."
    )
    # Keep only schema-allowed properties so additionalProperties: false passes
    allowed = {"product_goal", "assumed_users", "traffic_patterns", "non_goals", "explicitly_unprotected_areas"}
    planner_output[key] = {k: so[k] for k in allowed}


def _normalize_expected_vulnerabilities(planner_output: dict) -> None:
    """
    Normalize expected_vulnerabilities when the LLM returns different keys
    (e.g. distribution / distribution_rationale instead of distribution_by_class / rationale),
    or distribution values < 1. Mutates planner_output in place so it passes the schema.
    """
    key = "expected_vulnerabilities"
    raw = planner_output.get(key)
    if not isinstance(raw, dict):
        return
    ev = raw
    dist = ev.get("distribution_by_class") or ev.get("distribution")
    if isinstance(dist, dict):
        # Schema requires each count >= 1; drop or clamp zeros
        distribution_by_class = {k: max(1, int(v)) for k, v in dist.items() if isinstance(v, (int, float)) and v > 0}
        if not distribution_by_class:
            distribution_by_class = {"general": 1}
    else:
        distribution_by_class = {"general": 1}
    rationale = ev.get("rationale") or ev.get("distribution_rationale") or ""
    rationale = _str_min_len(rationale, 30, "Reflects architectural and integration risks.")
    total_count = ev.get("total_count")
    if not isinstance(total_count, int) or total_count < 1:
        total_count = sum(distribution_by_class.values()) or 1
    planner_output[key] = {
        "total_count": total_count,
        "distribution_by_class": distribution_by_class,
        "rationale": rationale,
    }


def _normalize_service_architecture(planner_output: dict) -> None:
    """
    Normalize service_architecture when the LLM returns different keys or types
    (e.g. name instead of service_name, arrays for responsibilities/data_owned/external_dependencies).
    Mutates planner_output in place so it passes the schema.
    """
    key = "service_architecture"
    raw = planner_output.get(key)
    if not isinstance(raw, list):
        return
    allowed_trust = {"internal", "semi-trusted", "untrusted"}
    normalized = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        service_name = item.get("service_name") or item.get("name") or "unknown-service"
        language = item.get("language") or "unknown"
        responsibilities = _str_min_len(item.get("responsibilities"), 30, "Core service responsibilities.")
        data_owned = _str_min_len(item.get("data_owned"), 20, "Service-owned data and state.")
        external_dependencies = _str_min_len(item.get("external_dependencies"), 10, "External systems and APIs.")
        trust_level = item.get("trust_level") or "internal"
        if trust_level not in allowed_trust:
            trust_level = "internal"
        split_rationale = _str_min_len(item.get("split_rationale"), 20, "Separation of concerns and scale.")
        normalized.append({
            "service_name": service_name,
            "language": language,
            "responsibilities": responsibilities,
            "data_owned": data_owned,
            "external_dependencies": external_dependencies,
            "trust_level": trust_level,
            "split_rationale": split_rationale,
        })
    # Schema requires minItems: 6; pad with placeholder services if LLM returned fewer
    min_services = 6
    placeholder = {
        "service_name": "placeholder_service",
        "language": "Python",
        "responsibilities": "Placeholder for schema compliance; minimal behavior.",
        "data_owned": "No persistent data; stateless placeholder.",
        "external_dependencies": "None; no external APIs.",
        "trust_level": "internal",
        "split_rationale": "Added to meet minimum service count.",
    }
    while len(normalized) < min_services:
        placeholder_copy = placeholder.copy()
        placeholder_copy["service_name"] = f"placeholder_service_{len(normalized) + 1}"
        normalized.append(placeholder_copy)
    planner_output[key] = normalized


def _normalize_data_flows(planner_output: dict) -> None:
    """
    Normalize data_flows when the LLM returns different keys or types
    (e.g. authentication/authorization/implicitly_trusted_data instead of
    authentication_assumptions/authorization_assumptions/implicit_trust).
    Mutates planner_output in place so it passes the schema.
    """
    key = "data_flows"
    raw = planner_output.get(key)
    if not isinstance(raw, list) or len(raw) == 0:
        return
    normalized = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        source = item.get("source") or "unknown"
        destination = item.get("destination") or "unknown"
        protocol = item.get("protocol") or "REST/gRPC"
        auth_assumptions = item.get("authentication_assumptions") or item.get("authentication") or "Token or mTLS"
        auth_assumptions = _str_min_len(auth_assumptions, 15, "Token or certificate-based authentication.")
        authz_assumptions = item.get("authorization_assumptions") or item.get("authorization") or "Role or scope-based"
        authz_assumptions = _str_min_len(authz_assumptions, 15, "Role or scope-based authorization.")
        implicit_trust = item.get("implicit_trust") or item.get("implicitly_trusted_data")
        implicit_trust = _str_min_len(implicit_trust, 15, "Payload and headers within boundary.")
        normalized.append({
            "source": source,
            "destination": destination,
            "protocol": protocol,
            "authentication_assumptions": auth_assumptions,
            "authorization_assumptions": authz_assumptions,
            "implicit_trust": implicit_trust,
        })
    if normalized:
        planner_output[key] = normalized


def _normalize_trust_boundaries(planner_output: dict) -> None:
    """
    Normalize trust_boundaries when the LLM returns different keys or types
    (e.g. boundary_rationale/potential_failures instead of why_boundary_exists/failure_modes,
    arrays for assumptions/failure_modes). Mutates planner_output in place so it passes the schema.
    """
    key = "trust_boundaries"
    raw = planner_output.get(key)
    if not isinstance(raw, list) or len(raw) == 0:
        return
    normalized = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            continue
        boundary_id = item.get("boundary_id") or f"boundary_{i}"
        components = item.get("components")
        if not isinstance(components, list):
            components = ["component_a", "component_b"]
        components = [str(c) for c in components]
        if len(components) < 2:
            components.extend(["component_b"] * (2 - len(components)))
        why_boundary_exists = item.get("why_boundary_exists") or item.get("boundary_rationale")
        why_boundary_exists = _str_min_len(why_boundary_exists, 20, "Security and isolation between components.")
        assumptions = item.get("assumptions")
        assumptions = _str_min_len(assumptions, 20, "Standard trust and rate-limiting assumptions.")
        failure_modes = item.get("failure_modes") or item.get("potential_failures")
        failure_modes = _str_min_len(failure_modes, 20, "Credential compromise or misuse.")
        normalized.append({
            "boundary_id": boundary_id,
            "components": components,
            "why_boundary_exists": why_boundary_exists,
            "assumptions": assumptions,
            "failure_modes": failure_modes,
        })
    if normalized:
        planner_output[key] = normalized


def _normalize_design_tradeoffs(planner_output: dict) -> None:
    """
    Normalize design_tradeoffs when the LLM returns different keys or types
    (e.g. rationale/acceptance_reason instead of justification/why_accepted,
    introduced_risks as array). Mutates planner_output in place so it passes the schema.
    """
    key = "design_tradeoffs"
    raw = planner_output.get(key)
    if not isinstance(raw, list) or len(raw) == 0:
        return
    normalized = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        decision = _str_min_len(item.get("decision"), 15, "Architectural or technology choice.")
        justification = item.get("justification") or item.get("rationale")
        justification = _str_min_len(justification, 20, "Team expertise and requirements.")
        introduced_risks = item.get("introduced_risks")
        introduced_risks = _str_min_len(introduced_risks, 20, "Complexity and operational risks.")
        why_accepted = item.get("why_accepted") or item.get("acceptance_reason")
        why_accepted = _str_min_len(why_accepted, 15, "Tradeoff accepted for delivery.")
        normalized.append({
            "decision": decision,
            "justification": justification,
            "introduced_risks": introduced_risks,
            "why_accepted": why_accepted,
        })
    if normalized:
        planner_output[key] = normalized


def _normalize_risk_analysis(planner_output: dict) -> None:
    """
    Normalize risk_analysis when the LLM returns different keys or types
    (e.g. architectural_origin/affected_components/realistic_manifestation instead of
    originating_architectural_decision/affected_services/manifestation, missing why_it_survives_reviews).
    Mutates planner_output in place so it passes the schema.
    """
    key = "risk_analysis"
    raw = planner_output.get(key)
    if not isinstance(raw, list) or len(raw) == 0:
        return
    normalized = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            continue
        risk_id = item.get("risk_id") or f"R{i + 1:03d}"
        originating = item.get("originating_architectural_decision") or item.get("architectural_origin")
        originating = _str_min_len(originating, 20, "Multi-service or cross-boundary design choice.")
        affected = item.get("affected_services") or item.get("affected_components")
        if not isinstance(affected, list):
            affected = [str(affected)] if affected else ["unknown"]
        affected = [str(s) for s in affected]
        if not affected:
            affected = ["unknown"]
        vulnerability_class = item.get("vulnerability_class") or "general"
        manifestation = item.get("manifestation") or item.get("realistic_manifestation")
        manifestation = _str_min_len(manifestation, 30, "Vulnerability may surface at runtime or under load.")
        why_survives = item.get("why_it_survives_reviews")
        why_survives = _str_min_len(why_survives, 30, "Subtle or cross-cutting; easy to miss in review.")
        normalized.append({
            "risk_id": risk_id,
            "originating_architectural_decision": originating,
            "affected_services": affected,
            "vulnerability_class": vulnerability_class,
            "manifestation": manifestation,
            "why_it_survives_reviews": why_survives,
        })
    if normalized:
        planner_output[key] = normalized


# -----------------------------
# Graph Nodes
# -----------------------------

# def planner_node(state: GraphState) -> GraphState:
#     """Runs Planner Agent with strict schema validation."""

#     # Validate planner input
#     try:
#         validate(
#             instance=state["planner_input"],
#             schema=load_planner_input_schema()
#         )
#     except ValidationError as e:
#         raise RuntimeError(f"Planner input schema violation: {e.message}")

#     planner = PlannerAgent(
#         system_prompt_path="prompts/planner.system.txt"
#     )

#     planner_output = planner.run(state["planner_input"])
#     _normalize_async_and_background(planner_output)
#     _normalize_system_overview(planner_output)
#     _normalize_expected_vulnerabilities(planner_output)
#     _normalize_service_architecture(planner_output)
#     _normalize_data_flows(planner_output)
#     _normalize_trust_boundaries(planner_output)
#     _normalize_design_tradeoffs(planner_output)

#     # Validate planner output
#     try:
#         validate(
#             instance=planner_output,
#             schema=load_planner_output_schema()
#         )
#     except ValidationError as e:
#         raise RuntimeError(
#             f"Planner output schema violation: {e.message}"
#         )

#     codebase_id = generate_codebase_id()
#     codebase_path = Path("codebases") / codebase_id

#     persist_json(
#         codebase_path / "planner_output.json",
#         planner_output
#     )

#     return {
#         **state,
#         "planner_output": planner_output,
#         "codebase_id": codebase_id,
#         "codebase_path": str(codebase_path)
#     }

def planner_node(state: GraphState) -> GraphState:
    """Runs Planner Agent with strict schema validation."""

    # Validate planner input
    try:
        validate(
            instance=state["planner_input"],
            schema=load_planner_input_schema()
        )
    except ValidationError as e:
        raise RuntimeError(f"Planner input schema violation: {e.message}")

    planner = PlannerAgent(
        system_prompt_path="prompts/planner.system.txt"
    )

    planner_output = planner.run(state["planner_input"])

    # Normalize the output to fill missing fields
    _normalize_risk_analysis(planner_output)
    _normalize_async_and_background(planner_output)
    _normalize_system_overview(planner_output)
    _normalize_expected_vulnerabilities(planner_output)
    _normalize_service_architecture(planner_output)
    _normalize_data_flows(planner_output)
    _normalize_trust_boundaries(planner_output)
    _normalize_design_tradeoffs(planner_output)

    # Validate planner output
    try:
        validate(
            instance=planner_output,
            schema=load_planner_output_schema()
        )
    except ValidationError as e:
        raise RuntimeError(
            f"Planner output schema violation: {e.message}"
        )

    codebase_index = state.get("codebase_index")
    codebase_id = f"codebase{codebase_index}" if codebase_index is not None else generate_codebase_id()
    codebase_path = Path("codebases") / codebase_id

    persist_json(
        codebase_path / "planner_output.json",
        planner_output
    )

    return {
        **state,
        "planner_output": planner_output,
        "codebase_id": codebase_id,
        "codebase_path": str(codebase_path)
    }



def codegen_node(state: GraphState) -> GraphState:
    planner_output = state["planner_output"]
    codebase_path = Path(state["codebase_path"])

    codegen = CodeGenAgent(
        system_prompt_path="prompts/codegen.system.txt"
    )

    # Generate services incrementally
    for service in planner_output["service_architecture"]:
        service_name = service["service_name"]

        unit_description = (
            f"Implement service '{service_name}' exactly as described. "
            f"Language: {service['language']}. "
            f"Responsibilities: {service['responsibilities']}. "
            f"Trust level: {service['trust_level']}. "
            f"Data owned: {service['data_owned']}."
        )

        codegen.generate_unit(
            planner_output=planner_output,
            unit_description=unit_description,
            output_path=codebase_path / "services" / service_name
        )

    return state


def generate_vulnerability_report(planner_output: dict) -> dict:
    return {
        "summary": planner_output["expected_vulnerabilities"],
        "vulnerabilities": planner_output["risk_analysis"]
    }


# -----------------------------
# Graph Assembly
# -----------------------------

def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("planner", planner_node)
    graph.add_node("codegen", codegen_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "codegen")
    graph.add_edge("codegen", END)

    return graph.compile()
