"""LLM access. Supports Anthropic or any OpenAI-compatible endpoint (OpenAI, Groq,
OpenRouter, Gemini's OpenAI endpoint...). Keys come from env vars or Streamlit secrets."""
from __future__ import annotations

import os

from .prompts import build_user_prompt, system_for
from .schema import apply_guardrails, extract_json, normalize

DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-5-5"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


class LLMError(Exception):
    """Raised with a user-presentable message."""


def _setting(name: str, default: str = "") -> str:
    val = os.getenv(name)
    if val:
        return val
    try:  # Streamlit Community Cloud secrets
        import streamlit as st

        v = st.secrets.get(name, default)
        return v if isinstance(v, str) else default
    except Exception:
        return default


def provider() -> str | None:
    """Which provider is configured, or None (app then runs in offline-demo mode)."""
    forced = _setting("LLM_PROVIDER").lower()
    if forced == "anthropic" and _setting("ANTHROPIC_API_KEY"):
        return "anthropic"
    if forced == "openai" and _setting("OPENAI_API_KEY"):
        return "openai"
    if _setting("ANTHROPIC_API_KEY"):
        return "anthropic"
    if _setting("OPENAI_API_KEY"):
        return "openai"
    return None


def _complete_anthropic(system: str, user: str) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=_setting("ANTHROPIC_API_KEY"), timeout=90.0, max_retries=2)
    resp = client.messages.create(
        model=_setting("ANTHROPIC_MODEL", DEFAULT_ANTHROPIC_MODEL),
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")


def _complete_openai(system: str, user: str) -> str:
    from openai import OpenAI

    client = OpenAI(
        api_key=_setting("OPENAI_API_KEY"),
        base_url=_setting("OPENAI_BASE_URL") or None,
        timeout=90.0,
        max_retries=2,
    )
    kwargs = dict(
        model=_setting("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        max_tokens=4096,
    )
    try:
        resp = client.chat.completions.create(response_format={"type": "json_object"}, **kwargs)
    except Exception:  # some compatible providers reject response_format
        resp = client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content or ""


def _complete(system: str, user: str) -> str:
    p = provider()
    if p == "anthropic":
        return _complete_anthropic(system, user)
    if p == "openai":
        return _complete_openai(system, user)
    raise LLMError("No API key configured. Set ANTHROPIC_API_KEY or OPENAI_API_KEY (see .env.example).")


def friendly_error(exc: Exception) -> str:
    text = f"{type(exc).__name__} {exc}".lower()
    if any(k in text for k in ("authentication", "401", "invalid x-api-key", "incorrect api key")):
        return "The API key was rejected. Check that your key is correct and active."
    if any(k in text for k in ("rate", "429", "overloaded", "529")):
        return "The AI provider is rate-limiting or overloaded. Wait a few seconds and try again."
    if "timeout" in text or "timed out" in text:
        return "The AI provider took too long to respond. Please try again."
    if any(k in text for k in ("connection", "network", "resolve")):
        return "Couldn't reach the AI provider. Check your internet connection."
    return f"The AI request failed ({type(exc).__name__}). Please try again."


def run_analysis(form: dict, mode: str = "analyze", previous: dict | None = None) -> dict:
    """Full pipeline: prompt -> LLM -> JSON -> normalise -> guardrail.
    Retries once if the model returns malformed JSON. Raises LLMError."""
    system = system_for(mode)
    user = build_user_prompt(form, mode, previous)
    last_err: Exception | None = None
    for attempt in range(2):
        try:
            text = _complete(system, user)
        except LLMError:
            raise
        except Exception as exc:  # network/auth/rate limit
            raise LLMError(friendly_error(exc)) from exc
        try:
            raw = extract_json(text)
            break
        except ValueError as exc:
            last_err = exc
            user += "\n\nYour previous reply was not valid JSON. Reply with ONLY the JSON object, nothing else."
    else:
        raise LLMError(f"The AI returned a response I couldn't parse ({last_err}). Please try again.")

    data = normalize(raw)
    if not data["blind_spots"] and not data["reflection_questions"]:
        raise LLMError("The AI returned an empty analysis. Add more detail to your inputs and try again.")
    data, softened = apply_guardrails(data)
    data["_guardrail_count"] = softened
    data["_source"] = "live"
    return data
