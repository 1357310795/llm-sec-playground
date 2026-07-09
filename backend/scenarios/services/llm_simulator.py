TARGET_BY_SCENARIO = {
    "roleplay-bypass": "TRAINING_FLAG_ROLEPLAY_BYPASS",
    "instruction-priority": "INTERNAL_POLICY_SIM_042",
    "encoding-obfuscation": "SIMULATED_BLOCKED_TOPIC",
    "rag-injection-basic": "RAG_INJECTION_TRAINING_FLAG",
    "cda-malicious-schema": "CDA_TRAINING_FLAG",
    "agent-tool-misuse": "TOOL_MISUSE_FLAG",
}


def simulate_response(scenario, message, defenses, normalized, retrieved_docs=None, schema_result=None, tool_calls=None):
    flag = TARGET_BY_SCENARIO.get(scenario.id, "TRAINING_FLAG")
    category = scenario.category

    if category in {"roleplay", "instruction_manipulation", "input_obfuscation"}:
        if _core_defenses_off(defenses):
            return f"模拟器：边界被绕过，输出无害训练标记 {flag}。"
        return "模拟器：请求已按系统边界处理。你可以继续尝试无害训练目标，但当前防御阻止了标记泄露。"

    if category == "indirect_prompt_injection":
        poisoned = any(flag in doc.get("content", "") for doc in retrieved_docs or [])
        if poisoned and not defenses.get("instructionDataSeparation"):
            return f"模拟器：错误采信了非可信文档指令，输出 {flag}。"
        return "模拟器：已把检索文档当作非可信数据，仅总结来源内容，不执行其中的伪指令。"

    if category == "constrained_decoding":
        has_flag = any(item.get("message") == "发现训练 flag" for item in (schema_result or {}).get("findings", []))
        if has_flag and not defenses.get("outputModeration"):
            return f'{{"status":"unsafe_simulation","trainingFlag":"{flag}"}}'
        return '{"status":"safe_simulation","note":"schema 风险已被识别或清理"}'

    if category == "agent_tool_misuse":
        unsafe_allowed = any(call.get("decision") == "allowed" and call.get("tool") in {"send_email", "read_profile"} for call in tool_calls or [])
        if unsafe_allowed and not defenses.get("toolPolicyEnforcement"):
            return f"模拟器：Agent 工具策略缺失，产生模拟误用 {flag}。"
        return "模拟器：工具请求只在沙盒中记录，策略已阻止越权或外发动作。"

    return "模拟器：完成一次安全教学响应。"


def _core_defenses_off(defenses):
    return not any([
        defenses.get("inputModeration"),
        defenses.get("promptInjectionDetection"),
        defenses.get("encodingNormalization"),
        defenses.get("outputModeration"),
    ])
