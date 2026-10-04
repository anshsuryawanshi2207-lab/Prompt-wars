"""BlindSpot AI: Decision Intelligence Copilot. Don't decide faster. Think deeper."""
from __future__ import annotations

import streamlit as st

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # dotenv is optional in production
    pass

from blindspot import demo, llm, ui
from blindspot.prompts import FORM_LABELS
from blindspot.report import to_markdown

st.set_page_config(page_title="BlindSpot AI", page_icon="🕳️", layout="wide")
ui.inject_css()

FIELD_KEYS = [k for k, _ in FORM_LABELS]
MODE_LABEL = {"analyze": "① Initial analysis", "challenge": "🔴 Challenge", "strengthen": "🟢 Strengthen"}

st.session_state.setdefault("page", "input")
st.session_state.setdefault("runs", [])
st.session_state.setdefault("active", 0)
st.session_state.setdefault("form", {})


# ------------------------------------------------------------------ callbacks
def load_example() -> None:
    for k, v in demo.EXAMPLE_FORM.items():
        st.session_state[f"f_{k}"] = v


def instant_demo() -> None:
    """Offline, zero-latency demo path: works with no API key and no internet."""
    load_example()
    st.session_state.form = dict(demo.EXAMPLE_FORM)
    st.session_state.runs = [{"mode": "analyze", "data": demo.demo_analysis()}]
    st.session_state.active = 0
    st.session_state.page = "results"


def new_decision() -> None:
    st.session_state.page = "input"
    st.session_state.runs = []
    st.session_state.active = 0


# --------------------------------------------------------------------- engine
def analyse(form: dict, mode: str, previous: dict | None) -> tuple[dict | None, str | None]:
    """Returns (data, notice). Falls back to the offline demo for the built-in example
    if the live call is unavailable, so a demo never dies on stage."""
    use_demo_fallback = demo.is_example(form)
    if not llm.provider():
        if use_demo_fallback:
            fn = {"analyze": demo.demo_analysis, "challenge": demo.demo_challenge, "strengthen": demo.demo_strengthen}[mode]
            return fn(), "No API key configured, so this is the built-in offline sample analysis."
        st.error("No API key is configured. Add ANTHROPIC_API_KEY or OPENAI_API_KEY (see README), "
                 "or click 'Try the internship example' to see the offline demo.")
        return None, None
    try:
        return llm.run_analysis(form, mode, previous), None
    except llm.LLMError as exc:
        if use_demo_fallback:
            fn = {"analyze": demo.demo_analysis, "challenge": demo.demo_challenge, "strengthen": demo.demo_strengthen}[mode]
            return fn(), f"Live analysis unavailable ({exc}). Showing the built-in offline sample."
        st.error(str(exc))
        return None, None


def collect_form() -> dict:
    return {k: (st.session_state.get(f"f_{k}") or "").strip() for k in FIELD_KEYS}


# ---------------------------------------------------------------------- pages
def page_input() -> None:
    ui.hero()
    st.write("")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.button("✨ Try the internship example", on_click=load_example, use_container_width=True)
    with c2:
        st.button("⚡ Instant demo (offline)", on_click=instant_demo, use_container_width=True,
                  help="Shows a complete sample analysis with no API call.")
    with c3:
        st.caption(("🟢 Live AI connected" if llm.provider() else "🟡 No API key: example runs in offline mode"))

    with st.form("decision_form"):
        st.text_input("1. Decision / question *", key="f_decision",
                      placeholder="e.g. Should I accept this offer, or ...?")
        a, b = st.columns(2)
        with a:
            st.text_area("2. Option A", key="f_option_a", height=90)
        with b:
            st.text_area("3. Option B", key="f_option_b", height=90)
        st.text_area("4. Context / situation", key="f_context", height=90)
        st.text_area("5. Why am I leaning toward my current choice?", key="f_leaning_reason", height=90)
        a, b = st.columns(2)
        with a:
            st.text_area("6. My priorities", key="f_priorities", height=80)
        with b:
            st.text_area("7. What factors matter most?", key="f_factors", height=80)
        a, b = st.columns(2)
        with a:
            st.text_area("8. Constraints", key="f_constraints", height=80)
        with b:
            st.text_area("9. What am I worried about?", key="f_worries", height=80)
        st.text_area("10. Additional information", key="f_additional", height=80)
        submitted = st.form_submit_button("🔍 FIND MY BLIND SPOTS", type="primary", use_container_width=True)

    if submitted:
        form = collect_form()
        if not form["decision"]:
            st.warning("Please describe the decision you're facing (field 1).")
            return
        if sum(len(v) for k, v in form.items() if k != "decision") < 60:
            st.warning("Add a little more detail (options, why you're leaning, worries). "
                       "The analysis is only as good as the reasoning you share.")
            return
        with st.spinner("Mapping your reasoning, testing assumptions, looking for tensions..."):
            data, notice = analyse(form, "analyze", None)
        if data:
            st.session_state.form = form
            st.session_state.runs = [{"mode": "analyze", "data": data, "notice": notice}]
            st.session_state.active = 0
            st.session_state.page = "results"
            st.rerun()


def page_results() -> None:
    runs = st.session_state.runs
    if not runs:
        new_decision()
        st.rerun()
    form = st.session_state.form
    idx = min(st.session_state.active, len(runs) - 1)

    top_a, top_b = st.columns([4, 1])
    with top_a:
        st.markdown('<div class="bs-logo" style="font-size:2rem;text-align:left">BlindSpot AI</div>',
                    unsafe_allow_html=True)
    with top_b:
        st.button("← New decision", on_click=new_decision, use_container_width=True)

    if len(runs) > 1:
        idx = st.radio("Analysis version", list(range(len(runs))), index=idx, horizontal=True,
                       format_func=lambda i: f"{MODE_LABEL[runs[i]['mode']]} #{i + 1}" if runs[i]["mode"] != "analyze"
                       else MODE_LABEL["analyze"])
        st.session_state.active = idx
    run = runs[idx]
    data = run["data"]

    if run.get("notice"):
        st.warning(run["notice"])
    if run["mode"] == "challenge":
        st.error("🔴 **Challenge mode**: pushing harder on your reasoning. These are questions to test, not verdicts.")
    elif run["mode"] == "strengthen":
        st.success("🟢 **Strengthen mode**: what evidence would make your reasoning more robust.")

    ui.render_results(form, data, runs[0]["data"] if idx else None, key_prefix=f"run{idx}")

    st.divider()
    st.markdown("### Take your thinking further")
    b1, b2 = st.columns(2)
    for col, mode, label in ((b1, "challenge", "🔴 Challenge My Thinking"), (b2, "strengthen", "🟢 Strengthen My Thinking")):
        with col:
            if st.button(label, use_container_width=True, key=f"btn_{mode}"):
                with st.spinner("Re-analysing..." if mode == "strengthen" else "Stress-testing your reasoning..."):
                    new, notice = analyse(form, mode, data)
                if new:
                    runs.append({"mode": mode, "data": new, "notice": notice})
                    st.session_state.active = len(runs) - 1
                    st.rerun()

    st.divider()
    g1, g2 = st.columns([3, 1])
    with g1:
        n = data.get("_guardrail_count", 0)
        st.caption("🛡️ Non-directive guardrail active: BlindSpot never tells you what to choose."
                   + (f" {n} directive phrase(s) were automatically softened in this analysis." if n else ""))
    with g2:
        st.download_button("⬇️ Download report", to_markdown(form, data, MODE_LABEL[run["mode"]]),
                           file_name="blindspot-report.md", mime="text/markdown", use_container_width=True)


if st.session_state.page == "results":
    page_results()
else:
    page_input()
