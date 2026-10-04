# 🕳️ BlindSpot AI: Decision Intelligence Copilot
> **Don't decide faster. Think deeper.**

## Problem
People decide using the information that is most *visible*: salary, distance, brand. They overlook diffuse factors, lean on unstated assumptions, and miss conflicts in their own reasoning. Chatbots make this worse by simply handing back an answer.

## Solution
BlindSpot AI analyses **how** you are thinking, never **what** you should choose. You describe a decision in 10 structured fields; it returns a structured audit of your reasoning plus the questions and evidence that would improve it.

## Key features
- **Reasoning X-Ray**: each claim from *your own words* is classified as Evidence-backed / Assumption / Emotion / Stated value / Unknown.
- **Attention Balance**: stated importance vs. where your reasoning actually spends its attention; large gaps are flagged as likely blind spots (visibility bias made visible).
- Blind spots (severity-rated), hidden assumptions (with how to test them), possible contradictions, missing information, alternative perspectives, reflection questions, an evidence checklist, "what would change my mind", and credited strengths.
- **Reasoning Snapshot** scores: reasoning strength, information coverage, assumption risk, blind-spot level. These rate the *quality of reasoning*, never the probability an option is right.
- 🔴 **Challenge My Thinking** (pre-mortem, steelman of the other option) and 🟢 **Strengthen My Thinking** (cheapest tests, thresholds). Each adds a new version with score deltas vs. the initial analysis.
- **Non-directive guardrail**: prompt-level rules *plus* a code-level filter that rewrites directive phrases ("you should accept...") and shows how many were softened.
- **Offline demo mode**: the internship example works with no API key and no internet, and is also the automatic fallback if the live call fails.
- Markdown report download.

## Architecture
```
app.py                Streamlit pages + session_state flow
blindspot/prompts.py  system prompt (role, rules, schema, scoring) + mode add-ons
blindspot/llm.py      Anthropic / OpenAI-compatible client, retry on bad JSON, friendly errors
blindspot/schema.py   JSON extraction, normalisation (never crashes the UI), guardrail
blindspot/ui.py       CSS + components   blindspot/demo.py  example + offline analyses
blindspot/report.py   Markdown export      tests/            unit + stubbed-UI smoke tests
```



