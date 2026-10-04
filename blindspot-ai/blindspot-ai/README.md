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

## AI approach
One structured-JSON call per analysis. The system prompt defines role, objective, non-directive rules, prompt-injection defence (user text is data inside `<user_input>`), reasoning principles (visibility bias, assumption/contradiction/missing-info detection), scoring rubric, uncertainty handling and a no-fabrication rule. Output is parsed defensively (fences, preambles, trailing commas, truncation), normalised to a fixed schema, retried once on failure, then passed through the guardrail.

## Tech stack
Python 3.10+, Streamlit, Anthropic SDK and/or OpenAI SDK, python-dotenv. No database, no auth.

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # add ONE API key
streamlit run app.py
python tests/test_core.py && python tests/smoke_ui.py  # optional checks
```

## Environment variables
| Var | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` / `ANTHROPIC_MODEL` | Anthropic (default model `claude-sonnet-5-5`) |
| `OPENAI_API_KEY` / `OPENAI_MODEL` / `OPENAI_BASE_URL` | OpenAI or compatible (Groq, OpenRouter, ...) |
| `LLM_PROVIDER` | optional: force `anthropic` or `openai` |

## Deploy to Streamlit Community Cloud
1. Push this folder to a **public GitHub repo** (`.env` is git-ignored).
2. Go to share.streamlit.io, **Create app**, pick the repo, branch `main`, main file `app.py`.
3. **Advanced settings → Secrets**, paste: `ANTHROPIC_API_KEY = "your-key"` (or the OpenAI vars).
4. Deploy, then open the link and click **⚡ Instant demo** to verify. Reboot the app after changing secrets.

## Example use case
A student deciding on a six-month internship: BlindSpot surfaces that "CGPA" is a stated priority yet absent from the reasons for the internship, that "industry experience" rests on an undefined role, and that "everyone says it matters" is hearsay, then lists the exact questions to ask the recruiter.

## Future improvements
Decision history and comparison over time, shareable read-only reports, a second-pass "critic" model to audit the analysis, multi-stakeholder mode, voice input.

*BlindSpot AI does not make decisions. The decision remains yours.*
