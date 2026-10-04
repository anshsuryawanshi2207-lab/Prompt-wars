"""Run: python tests/test_core.py  (or pytest)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blindspot import demo, llm, prompts, schema
from blindspot.report import to_markdown


def test_extract_json_variants():
    assert schema.extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert schema.extract_json('Sure! Here you go: {"a": {"b": "}"}} thanks') == {"a": {"b": "}"}}
    assert schema.extract_json('{"a": [1,2,],}') == {"a": [1, 2]}
    for bad in ("", "no json", '{"a": 1', None):
        try:
            schema.extract_json(bad)
        except ValueError:
            continue
        raise AssertionError(f"should fail: {bad!r}")


def test_normalize_garbage_is_safe():
    d = schema.normalize({"reasoning_strength": "150", "blind_spots": ["just a string", {"title": "T", "severity": "extreme"}],
                          "reflection_questions": "single q", "attention_balance": "oops", "hidden_assumptions": None})
    assert d["reasoning_strength"] == 100
    assert d["blind_spots"][0]["title"] == "just a string" and d["blind_spots"][1]["severity"] == "MEDIUM"
    assert d["reflection_questions"] == ["single q"] and d["attention_balance"] == []
    assert schema.normalize(None)["blind_spot_level"] == "LOW"
    assert schema.normalize([1, 2])["blind_spots"] == []


def test_guardrail_softens_directives():
    d, n = schema.apply_guardrails({"x": ["You should accept the internship.", "Option A is clearly better."], "y": "fine"})
    assert n == 2
    assert "should accept" not in json.dumps(d).lower() and "is clearly better" not in json.dumps(d).lower()


def test_demo_data_valid_and_non_directive():
    for fn in (demo.demo_analysis, demo.demo_challenge, demo.demo_strengthen):
        d = fn()
        assert d["blind_spots"] and d["reflection_questions"] and d["attention_balance"] and d["reasoning_map"]
        assert d["_guardrail_count"] == 0, "demo content must not need softening"
        assert to_markdown(demo.EXAMPLE_FORM, d).startswith("# BlindSpot AI Report")
    assert demo.is_example(demo.EXAMPLE_FORM)


def test_prompt_contains_input_and_guards():
    p = prompts.build_user_prompt({"decision": "Buy a car?"}, "challenge", {"blind_spots": [1]})
    assert "<user_input>" in p and "Buy a car?" in p and "<previous_analysis>" in p
    assert "NEVER" in prompts.system_for("analyze") and "CHALLENGE" in prompts.system_for("challenge")


def test_run_analysis_retry_and_failure():
    good = json.dumps(demo._BASE)
    replies = iter(["not json at all", good])
    llm._complete = lambda s, u: next(replies)          # malformed first, valid second
    d = llm.run_analysis(demo.EXAMPLE_FORM)
    assert d["_source"] == "live" and d["blind_spots"]
    llm._complete = lambda s, u: "still garbage"
    try:
        llm.run_analysis(demo.EXAMPLE_FORM)
    except llm.LLMError as e:
        assert "parse" in str(e)
    else:
        raise AssertionError("expected LLMError")
    def boom(s, u): raise RuntimeError("Error code: 429 rate limit")
    llm._complete = boom
    try:
        llm.run_analysis(demo.EXAMPLE_FORM)
    except llm.LLMError as e:
        assert "rate" in str(e).lower()
    else:
        raise AssertionError("expected LLMError")


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("PASS", name)
