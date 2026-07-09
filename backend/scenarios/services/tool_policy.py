from scenarios.services.guards import event

FAKE_CURRENT_USER = "student-001"
FAKE_SECRET = "FAKE_PROFILE_TOKEN_123"


def plan_tool_calls(message, defenses):
    text = message or ""
    planned = []
    if "read_profile" in text or "读取" in text or "用户资料" in text:
        target = "student-002" if "其他" in text or "student-002" in text else FAKE_CURRENT_USER
        planned.append({"tool": "read_profile", "args": {"user_id": target}})
    if "send_email" in text or "邮件" in text:
        to = "external@example.com" if "外部" in text else "teacher@training.local"
        planned.append({"tool": "send_email", "args": {"to": to, "subject": "训练通知", "body": f"模拟正文 {FAKE_SECRET}"}})
    if "create_ticket" in text or "工单" in text:
        planned.append({"tool": "create_ticket", "args": {"title": "训练工单", "description": "模拟 Agent 行为", "priority": "high" if "高" in text else "low"}})
    if not planned and "agent-tool-misuse" in text:
        planned.append({"tool": "send_email", "args": {"to": "external@example.com", "subject": "training", "body": FAKE_SECRET}})
    return enforce_policy(planned, defenses)


def enforce_policy(planned, defenses):
    calls = []
    events = []
    enforce = defenses.get("toolPolicyEnforcement")
    confirm = defenses.get("humanConfirmationRequired")

    for call in planned:
        tool = call["tool"]
        args = call["args"]
        decision = "allowed"
        result = "模拟工具调用已记录，无真实副作用。"

        if enforce and tool == "read_profile" and args.get("user_id") != FAKE_CURRENT_USER:
            decision = "blocked"
            result = "阻止越权读取其他假用户资料。"
            events.append(event("tool_policy_cross_user_read", "high", "tool_policy", result, "blocked", args.get("user_id", "")))
        elif enforce and tool == "send_email" and not args.get("to", "").endswith("@training.local"):
            decision = "blocked"
            result = "阻止向训练域外邮箱发送模拟邮件。"
            events.append(event("tool_policy_external_email", "high", "tool_policy", result, "blocked", args.get("to", "")))
        elif enforce and tool == "send_email" and FAKE_SECRET in args.get("body", ""):
            decision = "blocked"
            result = "阻止假敏感字段流入邮件正文。"
            events.append(event("tool_policy_sensitive_flow", "critical", "tool_policy", result, "blocked", "FAKE_PROFILE_TOKEN"))
        elif confirm and tool == "create_ticket" and args.get("priority") == "high":
            decision = "confirmation_required"
            result = "高优先级模拟工单需要人工确认。"
            events.append(event("tool_policy_confirmation_required", "medium", "tool_policy", result, "confirmation_required", "high"))

        calls.append({"tool": tool, "args": args, "decision": decision, "result": result})

    return calls, events
