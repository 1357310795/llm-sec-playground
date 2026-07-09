from scenarios.models import Attempt, RiskEvent
from scenarios.services.guards import detect_flag_leak, detect_prompt_risks, precheck_real_harm
from scenarios.services.llm_client import generate_llm_response
from scenarios.services.normalizer import normalize_text
from scenarios.services.rag_sandbox import retrieve_documents
from scenarios.services.schema_analyzer import analyze_schema
from scenarios.services.scoring import repair_advice_for, score_attempt
from scenarios.services.tool_policy import plan_tool_calls

DEFENSE_KEYS = [
    "inputModeration",
    "promptInjectionDetection",
    "encodingNormalization",
    "instructionDataSeparation",
    "outputModeration",
    "toolPolicyEnforcement",
    "humanConfirmationRequired",
    "rateLimit",
]


def run_attempt(scenario, payload):
    message = payload.get("message") or ""
    messages = payload.get("messages") or []
    schema = payload.get("schema")
    submitted_documents = payload.get("documents") or []
    session_id = payload.get("sessionId") or "demo-session"
    defenses = merge_defenses(scenario, payload.get("defenses") or {})
    timeline = []
    risk_events = []
    retrieved_docs = []
    tool_calls = []
    schema_result = None

    timeline.append({"phase": "input_received", "data": {"message": message[:240], "allowedInputs": scenario.allowed_inputs}})

    blocked_events = precheck_real_harm(message)
    if blocked_events:
        risk_events.extend(blocked_events)
        output = "本靶场只支持无害化 LLM 安全训练。请改用固定训练标记、假文档或模拟工具目标。"
        status = Attempt.Status.BLOCKED
        timeline.append({"phase": "safety_precheck", "riskEvents": blocked_events})
        return persist_attempt(scenario, session_id, messages, message, schema, submitted_documents, defenses, retrieved_docs, tool_calls, output, output, status, risk_events, timeline)

    normalized = normalize_text(message) if defenses.get("encodingNormalization") else {"raw": message, "normalized": message, "decoded": [], "views": [message]}
    timeline.append({"phase": "normalization", "data": {"normalized": normalized["normalized"], "decoded": normalized["decoded"]}})

    if defenses.get("inputModeration") or defenses.get("promptInjectionDetection"):
        guard_events = detect_prompt_risks(normalized["views"])
        risk_events.extend(guard_events)
        timeline.append({"phase": "input_guard", "riskEvents": guard_events})

    if scenario.category == "indirect_prompt_injection":
        retrieved_docs, rag_events = retrieve_documents(scenario, message, submitted_documents, defenses)
        risk_events.extend(rag_events)
        timeline.append({"phase": "rag_retrieval", "docs": retrieved_docs, "riskEvents": rag_events})

    if scenario.category == "constrained_decoding":
        schema_result, schema_events = analyze_schema(schema or {}, defenses)
        risk_events.extend(schema_events)
        timeline.append({"phase": "schema_analysis", "data": schema_result, "riskEvents": schema_events})

    if scenario.category == "agent_tool_misuse":
        tool_calls, tool_events = plan_tool_calls(message, defenses)
        risk_events.extend(tool_events)
        timeline.append({"phase": "tool_policy", "toolCalls": tool_calls, "riskEvents": tool_events})

    llm_result = generate_llm_response(scenario, message, defenses, normalized, retrieved_docs, schema_result, tool_calls)
    raw_output = llm_result.content
    output = raw_output
    timeline.append({
        "phase": "model_call",
        "data": {
            "success": llm_result.success,
            "model": llm_result.model,
            "providerHost": llm_result.provider_host,
            "usage": llm_result.usage,
            "error": llm_result.error,
        },
    })

    safe_output = output
    output_events = []
    if defenses.get("outputModeration"):
        output_events = detect_flag_leak(raw_output)
        if output_events:
            safe_output = "[输出已拦截] 真实 LLM 尝试输出训练敏感标记，已替换为教学提示。"
            output = safe_output
    risk_events.extend(output_events)
    timeline.append({"phase": "output_guard", "riskEvents": output_events, "safeOutput": safe_output})

    status = Attempt.Status.COMPLETED if llm_result.success else Attempt.Status.ERROR
    score = score_attempt(raw_output, risk_events, status)
    timeline.append({"phase": "scoring", "score": score})
    return persist_attempt(scenario, session_id, messages, message, schema, submitted_documents, defenses, retrieved_docs, tool_calls, output, safe_output, status, risk_events, timeline, score)


def merge_defenses(scenario, overrides):
    defaults = scenario.default_defenses.as_camel_dict()
    merged = {key: bool(defaults.get(key)) for key in DEFENSE_KEYS}
    for key in DEFENSE_KEYS:
        if key in overrides:
            merged[key] = bool(overrides[key])
    return merged


def persist_attempt(scenario, session_id, messages, message, schema, documents, defenses, retrieved_docs, tool_calls, output, safe_output, status, risk_events, timeline, score=None):
    score = score if score is not None else score_attempt(output, risk_events, status)
    attempt = Attempt.objects.create(
        scenario=scenario,
        session_id=session_id,
        messages=messages,
        submitted_text=message,
        submitted_schema=schema,
        submitted_documents=documents,
        defense_overrides=defenses,
        retrieved_docs=retrieved_docs,
        tool_calls=tool_calls,
        model_output=output,
        safe_output=safe_output,
        score=score,
        status=status,
        timeline=timeline,
        repair_advice=repair_advice_for(scenario),
    )
    for item in risk_events:
        RiskEvent.objects.create(attempt=attempt, **item)
    return attempt
