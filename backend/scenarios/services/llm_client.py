from dataclasses import dataclass
from urllib.parse import urlparse

from django.conf import settings
from openai import OpenAI


@dataclass
class LLMResult:
    content: str
    model: str
    success: bool
    provider_host: str = ""
    usage: dict | None = None
    error: str = ""
    tool_calls: list | None = None
    finish_reason: str = ""


def generate_llm_response(chat_messages, tools=None, tool_choice=None, response_format=None):
    config = _provider_config(use_openai2=response_format is not None)
    missing = [name for name, value in config["required"].items() if not value]
    provider_host = _provider_host(config["base_url"])
    if missing:
        return LLMResult(
            content="LLM API 配置缺失，已安全停止本次真实模型调用。",
            model=config["model"],
            success=False,
            provider_host=provider_host,
            error="missing_llm_config",
        )

    client = OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"],
        timeout=settings.OPENAI_TIMEOUT_SECONDS,
    )

    request = {
        "model": config["model"],
        "messages": chat_messages,
        "temperature": settings.OPENAI_TEMPERATURE,
        "max_tokens": settings.OPENAI_MAX_TOKENS,
        # "extra_body": { "enable_thinking": False }
    }
    if tools is not None:
        request["tools"] = tools
        request["tool_choice"] = tool_choice or "auto"
    if response_format is not None:
        request["response_format"] = response_format
    print(request)
    try:
        completion = client.chat.completions.create(**request)
    except Exception as ex:
        print(str(ex))
        return LLMResult(
            content="LLM API 调用失败，已隐藏供应商错误详情。请检查后端 .env、网络和模型配置。",
            model=config["model"],
            success=False,
            provider_host=provider_host,
            error="provider_call_failed",
        )

    choice = completion.choices[0]
    message = choice.message
    content = message.content or ""
    usage = completion.usage.model_dump() if getattr(completion, "usage", None) else None
    return LLMResult(
        content=content,
        model=completion.model or config["model"],
        success=True,
        provider_host=provider_host,
        usage=usage,
        tool_calls=_normalize_tool_calls(getattr(message, "tool_calls", None)),
        finish_reason=getattr(choice, "finish_reason", "") or "",
    )


def _normalize_tool_calls(tool_calls):
    if not tool_calls:
        return []
    normalized = []
    for tool_call in tool_calls:
        normalized.append(
            {
                "id": tool_call.id,
                "type": tool_call.type,
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments or "{}",
                },
            }
        )
    return normalized


def _provider_config(use_openai2=False):
    if use_openai2:
        return {
            "base_url": getattr(settings, "OPENAI2_BASE_URL", ""),
            "api_key": getattr(settings, "OPENAI2_API_KEY", ""),
            "model": getattr(settings, "OPENAI2_MODEL", ""),
            "required": {
                "OPENAI2_BASE_URL": getattr(settings, "OPENAI2_BASE_URL", ""),
                "OPENAI2_API_KEY": getattr(settings, "OPENAI2_API_KEY", ""),
                "OPENAI2_MODEL": getattr(settings, "OPENAI2_MODEL", ""),
            },
        }
    return {
        "base_url": settings.OPENAI_BASE_URL,
        "api_key": settings.OPENAI_API_KEY,
        "model": settings.OPENAI_MODEL,
        "required": {
            "OPENAI_BASE_URL": settings.OPENAI_BASE_URL,
            "OPENAI_API_KEY": settings.OPENAI_API_KEY,
            "OPENAI_MODEL": settings.OPENAI_MODEL,
        },
    }


def _provider_host(base_url):
    parsed = urlparse(base_url or "")
    return parsed.netloc or "configured-provider"
