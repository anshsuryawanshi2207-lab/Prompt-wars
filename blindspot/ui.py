"""All presentation code. HTML is built as single-line strings (Streamlit's markdown
treats indented lines as code blocks) and every dynamic value is escaped."""
from __future__ import annotations

import html

import streamlit as st

SEV_COLOR = {"HIGH": "#ef4444", "MEDIUM": "#f59e0b", "LOW": "#22c55e"}
TYPE_COLOR = {"EVIDENCE": "#22c55e", "ASSUMPTION": "#f59e0b", "EMOTION": "#ec4899",
              "VALUE": "#6366f1", "UNKNOWN": "#94a3b8"}
TYPE_LABEL = {"EVIDENCE": "Evidence-backed", "ASSUMPTION": "Assumption", "EMOTION": "Emotion",
              "VALUE": "Stated value", "UNKNOWN": "Unknown / unverified"}
ACCENT = "#7c83ff"


def e(x) -> str:
    return html.escape(str(x if x is not None else ""))


CSS = """
<style>
.block-container {padding-top: 2rem; max-width: 1100px;}
.bs-hero {text-align:center; padding: 1.5rem 0 .5rem;}
.bs-logo {font-size: 3.1rem; font-weight: 800; letter-spacing:-1px;
  background: linear-gradient(90deg,#7c83ff,#c084fc 55%,#38bdf8); -webkit-background-clip:text;
  -webkit-text-fill-color: transparent; line-height:1.1;}
.bs-sub {font-size: 1.3rem; font-weight:600; margin-top:.4rem;}
.bs-tag {opacity:.7; font-style:italic; margin-top:.2rem;}
.bs-expl {max-width: 640px; margin: .9rem auto 0; opacity:.8; line-height:1.55;}
.bs-card {border:1px solid rgba(128,128,150,.28); background: rgba(128,128,160,.07);
  border-radius: 14px; padding: 1rem 1.15rem; margin: .55rem 0; animation: bsfade .45s ease both;}
.bs-card h4 {margin:0 0 .35rem; font-size:1.05rem;}
.bs-card p {margin:.25rem 0; line-height:1.5;}
.bs-muted {opacity:.72; font-size:.9rem;}
.bs-badge {display:inline-block; font-size:.7rem; font-weight:700; letter-spacing:.5px;
  padding:.15rem .55rem; border-radius:999px; margin-right:.5rem; vertical-align:middle;}
.bs-bar {height:9px; border-radius:99px; background: rgba(128,128,150,.22); overflow:hidden; margin:.4rem 0;}
.bs-fill {height:100%; border-radius:99px; transition: width .8s ease;}
.bs-metric {border:1px solid rgba(128,128,150,.28); background: rgba(128,128,160,.07);
  border-radius:14px; padding:.9rem 1rem; height:100%; animation: bsfade .45s ease both;}
.bs-metric .lbl {font-size:.78rem; text-transform:uppercase; letter-spacing:.8px; opacity:.7;}
.bs-metric .val {font-size:2rem; font-weight:800; line-height:1.2;}
.bs-metric .note {font-size:.78rem; opacity:.65;}
.bs-q {border-left:4px solid #7c83ff; background: linear-gradient(90deg, rgba(124,131,255,.14), transparent);
  border-radius: 0 12px 12px 0; padding:.8rem 1rem; margin:.5rem 0; font-size:1.05rem; line-height:1.5;
  animation: bsfade .45s ease both;}
.bs-q b {color:#7c83ff; margin-right:.5rem;}
.bs-title {font-size:1.45rem; font-weight:750; margin:2rem 0 .1rem;}
.bs-title-sub {opacity:.65; margin-bottom:.4rem;}
.bs-decision {border:1px solid rgba(124,131,255,.5); background: linear-gradient(135deg, rgba(124,131,255,.16), rgba(56,189,248,.08));
  border-radius:16px; padding:1.1rem 1.3rem; margin-bottom:1rem;}
.bs-decision .k {font-size:.75rem; letter-spacing:1px; text-transform:uppercase; opacity:.7;}
.bs-decision .v {font-size:1.35rem; font-weight:700; margin:.2rem 0;}
.bs-chip {display:inline-block; font-size:.78rem; padding:.2rem .6rem; border-radius:999px;
  border:1px solid rgba(128,128,150,.35); margin:.15rem .25rem .15rem 0;}
.bs-row {display:grid; grid-template-columns: 170px 1fr 60px; gap:.7rem; align-items:center; margin:.15rem 0;}
.bs-gap {border-color: rgba(239,68,68,.55) !important; background: rgba(239,68,68,.07) !important;}
details.bs-d summary {cursor:pointer; opacity:.85; font-size:.9rem; margin-top:.35rem;}
@keyframes bsfade {from {opacity:0; transform: translateY(6px);} to {opacity:1; transform:none;}}
@media (max-width: 700px) {.bs-row {grid-template-columns: 1fr;} .bs-logo{font-size:2.3rem;}}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def badge(text: str, color: str) -> str:
    return (f'<span class="bs-badge" style="background:{color}22;color:{color};'
            f'border:1px solid {color}66">{e(text)}</span>')


def bar(pct: int, color: str) -> str:
    return f'<div class="bs-bar"><div class="bs-fill" style="width:{int(pct)}%;background:{color}"></div></div>'


def good_color(v: int) -> str:
    return "#22c55e" if v >= 70 else "#f59e0b" if v >= 45 else "#ef4444"


def risk_color(v: int) -> str:
    return "#ef4444" if v >= 66 else "#f59e0b" if v >= 36 else "#22c55e"


def section(icon: str, title: str, sub: str = "") -> None:
    st.markdown(f'<div class="bs-title">{icon} {e(title)}</div>'
                + (f'<div class="bs-title-sub">{e(sub)}</div>' if sub else ""), unsafe_allow_html=True)


# ------------------------------------------------------------------- landing
def hero() -> None:
    st.markdown(
        '<div class="bs-hero"><div class="bs-logo">BlindSpot AI</div>'
        '<div class="bs-sub">Find what your reasoning might be missing.</div>'
        '<div class="bs-tag">Don\'t decide faster. Think deeper.</div>'
        '<div class="bs-expl">BlindSpot AI doesn\'t tell you what to choose. It challenges your reasoning, '
        'exposes hidden assumptions, and helps you ask better questions.</div></div>',
        unsafe_allow_html=True)


# ------------------------------------------------------------------- results
def decision_banner(form: dict, d: dict) -> None:
    st.markdown(
        f'<div class="bs-decision"><div class="k">Your decision</div>'
        f'<div class="v">{e(form.get("decision") or d["decision_summary"])}</div>'
        f'<div class="bs-muted">{e(d["decision_summary"])}</div></div>', unsafe_allow_html=True)


def _delta(cur: int, base: int | None, lower_is_better: bool = False) -> str:
    if base is None or cur == base:
        return ""
    diff = cur - base
    good = (diff < 0) if lower_is_better else (diff > 0)
    color = "#22c55e" if good else "#ef4444"
    arrow = "▲" if diff > 0 else "▼"
    return f'<span style="color:{color};font-size:.8rem"> {arrow} {abs(diff)} vs initial</span>'


def snapshot(d: dict, base: dict | None = None) -> None:
    level = d["blind_spot_level"]
    level_pct = {"LOW": 25, "MEDIUM": 60, "HIGH": 90}[level]
    cards = [
        ("Reasoning Strength", f'{d["reasoning_strength"]}', d["reasoning_strength"], good_color(d["reasoning_strength"]),
         "Clarity, evidence and balance", _delta(d["reasoning_strength"], base and base["reasoning_strength"])),
        ("Blind Spot Level", level, level_pct, SEV_COLOR[level], "Overall exposure",
         ""),
        ("Information Coverage", f'{d["information_coverage"]}', d["information_coverage"], good_color(d["information_coverage"]),
         "Relevant factors backed by facts", _delta(d["information_coverage"], base and base["information_coverage"])),
        ("Assumption Risk", f'{d["assumption_risk"]}', d["assumption_risk"], risk_color(d["assumption_risk"]),
         "Higher = more untested beliefs", _delta(d["assumption_risk"], base and base["assumption_risk"], True)),
    ]
    cols = st.columns(4)
    for col, (lbl, val, pct, color, note, delta) in zip(cols, cards):
        with col:
            st.markdown(
                f'<div class="bs-metric"><div class="lbl">{lbl}</div>'
                f'<div class="val" style="color:{color}">{e(val)}{delta}</div>{bar(pct, color)}'
                f'<div class="note">{note}</div></div>', unsafe_allow_html=True)
    st.caption("These scores rate the quality and completeness of your reasoning, not the probability "
               "that either option is correct.")


def attention_balance(items: list[dict]) -> None:
    if not items:
        return
    section("⚖️", "Attention Balance",
            "What you say matters vs. where your reasoning actually spends its attention")
    st.markdown('<span class="bs-chip">🟪 Importance you stated</span>'
                '<span class="bs-chip">🟦 Attention in your reasoning</span>'
                '<span class="bs-chip">🔴 Red = large gap, a possible blind spot</span>', unsafe_allow_html=True)
    for it in items:
        gap = it["importance"] - it["attention"]
        cls = "bs-card bs-gap" if gap >= 35 else "bs-card"
        st.markdown(
            f'<div class="{cls}"><div class="bs-row"><b>{e(it["factor"])}</b>'
            f'<div>{bar(it["importance"], "#a78bfa")}{bar(it["attention"], "#38bdf8")}</div>'
            f'<span class="bs-muted">{it["importance"]} / {it["attention"]}</span></div>'
            + (f'<div class="bs-muted">{e(it["note"])}</div>' if it["note"] else "") + '</div>',
            unsafe_allow_html=True)


def reasoning_map(items: list[dict]) -> None:
    if not items:
        return
    section("🗺️", "Reasoning X-Ray", "Your own claims, classified by what they actually rest on")
    legend = "".join(badge(TYPE_LABEL[k], c) for k, c in TYPE_COLOR.items())
    st.markdown(legend, unsafe_allow_html=True)
    for it in items:
        c = TYPE_COLOR[it["type"]]
        st.markdown(
            f'<div class="bs-card" style="border-left:4px solid {c}">'
            f'{badge(TYPE_LABEL[it["type"]], c)}<b>{e(it["claim"])}</b>'
            + (f'<div class="bs-muted">{e(it["note"])}</div>' if it["note"] else "") + '</div>',
            unsafe_allow_html=True)


def blind_spots(items: list[dict]) -> None:
    section("🕳️", "Blind Spots", f"{len(items)} areas your reasoning may be underweighting")
    for b in items:
        c = SEV_COLOR[b["severity"]]
        st.markdown(
            f'<div class="bs-card" style="border-left:4px solid {c}">'
            f'<h4>{badge(b["severity"], c)}{e(b["title"])}</h4><p>{e(b["explanation"])}</p>'
            f'<details class="bs-d"><summary>Why it matters · what evidence is needed</summary>'
            f'<p><b>Why it matters:</b> {e(b["why_it_matters"])}</p>'
            f'<p><b>Evidence needed:</b> {e(b["evidence_needed"])}</p></details></div>',
            unsafe_allow_html=True)


def assumptions(items: list[dict]) -> None:
    section("🧩", "Hidden Assumptions", "Beliefs your reasoning may rely on without having tested them")
    for a in items:
        with st.expander(f'{a["assumption"]}   ·   reliance: {a["confidence"]}'):
            st.markdown(f"**Why it might be wrong:** {a['why_it_might_be_wrong']}")
            st.markdown(f"**How to test it:** {a['how_to_test_it']}")


def contradictions(items: list[dict]) -> None:
    section("⚔️", "Possible Contradictions", "Tensions worth examining, not accusations")
    if not items:
        st.info("No clear tensions detected in what you wrote. That's a good sign, though it may also reflect limited detail.")
    for c in items:
        st.markdown(
            f'<div class="bs-card" style="border-left:4px solid #ec4899"><p>{e(c["tension"])}</p>'
            + (f'<p class="bs-muted">{e(c["parts_in_tension"])}</p>' if c["parts_in_tension"] else "")
            + (f'<p>❓ <i>{e(c["question_to_resolve"])}</i></p>' if c["question_to_resolve"] else "") + '</div>',
            unsafe_allow_html=True)


def missing_information(items: list[dict]) -> None:
    section("🔎", "Missing Information", "Facts that could materially change the picture")
    for m in items:
        st.markdown(f'<div class="bs-card"><b>{e(m["item"])}</b>'
                    + (f'<div class="bs-muted">{e(m["why_it_matters"])}</div>' if m["why_it_matters"] else "")
                    + '</div>', unsafe_allow_html=True)


def perspectives(items: list[dict]) -> None:
    section("🔭", "Alternative Perspectives", "Lenses you may not have tried")
    cols = st.columns(2)
    for i, p in enumerate(items):
        with cols[i % 2]:
            st.markdown(f'<div class="bs-card"><h4>🔭 {e(p["perspective"])}</h4><p>{e(p["insight"])}</p></div>',
                        unsafe_allow_html=True)


def questions(items: list[str]) -> None:
    section("❓", "Questions Worth Asking", "Sit with these before you decide")
    for i, q in enumerate(items, 1):
        st.markdown(f'<div class="bs-q"><b>{i}</b>{e(q)}</div>', unsafe_allow_html=True)


def evidence(items: list[dict], key_prefix: str) -> None:
    section("📚", "Evidence to Seek", "Tick items off as you collect real information")
    done = 0
    for i, it in enumerate(items):
        label = it["action"] + (f"  —  {it['why']}" if it["why"] else "")
        if st.checkbox(label, key=f"{key_prefix}_ev_{i}"):
            done += 1
    if items:
        st.progress(done / len(items), text=f"{done} of {len(items)} evidence items collected")


def mind_changers(items: list[str]) -> None:
    if not items:
        return
    section("🧭", "What Would Change Your Mind", "Decide in advance what would count as new evidence")
    for m in items:
        st.markdown(f'<div class="bs-card">🔁 {e(m)}</div>', unsafe_allow_html=True)


def strengths(items: list[dict]) -> None:
    section("💪", "What You're Already Doing Well", "Good reasoning habits worth keeping")
    for s in items:
        st.markdown(f'<div class="bs-card" style="border-left:4px solid #22c55e"><b>✅ {e(s["strength"])}</b>'
                    + (f'<div class="bs-muted">{e(s["detail"])}</div>' if s["detail"] else "") + '</div>',
                    unsafe_allow_html=True)


def render_results(form: dict, d: dict, base: dict | None, key_prefix: str) -> None:
    decision_banner(form, d)
    if d.get("analysis_notes"):
        st.info(d["analysis_notes"])
    st.markdown('<div class="bs-title" style="margin-top:.5rem">🧠 Reasoning Snapshot</div>', unsafe_allow_html=True)
    snapshot(d, base)
    attention_balance(d["attention_balance"])
    reasoning_map(d["reasoning_map"])
    blind_spots(d["blind_spots"])
    assumptions(d["hidden_assumptions"])
    contradictions(d["contradictions"])
    missing_information(d["missing_information"])
    perspectives(d["alternative_perspectives"])
    questions(d["reflection_questions"])
    evidence(d["evidence_to_seek"], key_prefix)
    mind_changers(d["mind_changers"])
    strengths(d["reasoning_strengths"])
