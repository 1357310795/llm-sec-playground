from scenarios.services.guards import TRAINING_FLAGS, event

INSTRUCTION_WORDS = ["ignore", "system", "developer", "必须", "忽略", "输出", "泄露", "覆盖"]


def analyze_schema(schema, defenses):
    events = []
    findings = []

    def walk(value, path="$"):
        if isinstance(value, dict):
            for key, child in value.items():
                inspect_string(str(key), f"{path}.{key}", "field_name")
                walk(child, f"{path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{path}[{index}]")
        elif isinstance(value, str):
            inspect_string(value, path, "string")

    def inspect_string(text, path, kind):
        for flag in TRAINING_FLAGS:
            if flag in text:
                events.append(event("schema_embedded_training_flag", "critical", "schema", "Schema 中包含训练标记，说明结构化输出约束也是攻击面。", "flagged", flag, {"path": path, "kind": kind}))
                findings.append({"path": path, "kind": kind, "message": "发现训练 flag"})
        lowered = text.lower()
        if any(word in lowered for word in INSTRUCTION_WORDS):
            events.append(event("schema_instruction_text", "high", "schema", "Schema 文本包含指令性内容。", "flagged", text[:80], {"path": path, "kind": kind}))
            findings.append({"path": path, "kind": kind, "message": "发现指令性文本"})

    if schema:
        walk(schema)

    sanitized = schema
    if defenses.get("promptInjectionDetection") or defenses.get("outputModeration"):
        sanitized = _sanitize_schema(schema)
        print(sanitized)
        if events:
            events.append(event("schema_sanitized", "medium", "schema", "已在模拟链路中清理风险 schema 描述、默认值或枚举。", "sanitized"))

    return {"findings": findings, "sanitizedSchema": sanitized}, events


def _sanitize_schema(value):
    if isinstance(value, dict):
        cleaned = {}
        for key, child in value.items():
            if key in {"description", "default", "examples"}:
                continue
            cleaned[key] = _sanitize_schema(child)
        return cleaned
    if isinstance(value, list):
        return [_sanitize_schema(item) for item in value if not (isinstance(item, str) and any(flag in item for flag in TRAINING_FLAGS))]
    if isinstance(value, str) and any(flag in value for flag in TRAINING_FLAGS):
        return "[TRAINING_FLAG_REDACTED]"
    return value
