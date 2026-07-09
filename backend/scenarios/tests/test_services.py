import pytest

from scenarios.services.llm_client import build_messages, generate_llm_response
from scenarios.services.normalizer import normalize_text
from scenarios.services.schema_analyzer import analyze_schema
from scenarios.services.tool_policy import plan_tool_calls


@pytest.mark.parametrize("encoded", ["U0lNVUxBVEVEX0JMT0NLRURfVE9QSUM="])
def test_normalizer_decodes_base64(encoded):
    result = normalize_text(encoded)
    assert any(item["value"] == "SIMULATED_BLOCKED_TOPIC" for item in result["decoded"])


def test_schema_analyzer_detects_flag():
    schema = {"type": "object", "properties": {"status": {"enum": ["ok", "CDA_TRAINING_FLAG"]}}}
    result, events = analyze_schema(schema, {"outputModeration": True})
    assert result["findings"]
    assert any(event["type"] == "schema_embedded_training_flag" for event in events)


def test_tool_policy_blocks_external_email():
    calls, events = plan_tool_calls("发送邮件到外部邮箱", {"toolPolicyEnforcement": True, "humanConfirmationRequired": True})
    assert calls[0]["decision"] == "blocked"
    assert any(event["type"] == "tool_policy_external_email" for event in events)


@pytest.mark.django_db
def test_llm_client_fails_closed_when_config_missing(settings):
    settings.OPENAI_BASE_URL = ""
    settings.OPENAI_API_KEY = ""
    settings.OPENAI_MODEL = ""
    result = generate_llm_response(None, "hello", {}, {"normalized": "hello", "decoded": []})
    assert result.success is False
    assert result.error == "missing_llm_config"
    assert "API" in result.content


@pytest.mark.django_db
def test_build_messages_marks_tools_as_simulated():
    from django.core.management import call_command
    from scenarios.models import Scenario

    call_command("seed_scenarios")
    scenario = Scenario.objects.get(id="agent-tool-misuse")
    messages = build_messages(
        scenario,
        "发送邮件",
        {"toolPolicyEnforcement": True},
        {"normalized": "发送邮件", "decoded": []},
        tool_calls=[{"tool": "send_email", "decision": "blocked"}],
    )
    joined = "\n".join(item["content"] for item in messages)
    assert "模拟工具" in joined
    assert "真实外部动作" in joined
