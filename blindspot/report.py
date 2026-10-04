"""Export an analysis as a shareable Markdown report."""
from __future__ import annotations


def to_markdown(form: dict, d: dict, label: str = "Initial analysis") -> str:
    out = ["# BlindSpot AI Report", "", f"_Don't decide faster. Think deeper._  ({label})", ""]
    out += ["## Decision", form.get("decision", "") or d.get("decision_summary", ""), ""]
    out += [d.get("decision_summary", ""), ""]
    out += [
        "## Reasoning Snapshot (quality of reasoning, not probability an option is right)",
        f"- Reasoning strength: {d['reasoning_strength']}/100",
        f"- Information coverage: {d['information_coverage']}/100",
        f"- Assumption risk: {d['assumption_risk']}/100 (higher = riskier)",
        f"- Blind spot level: {d['blind_spot_level']}",
        "",
    ]
    if d.get("analysis_notes"):
        out += [f"> {d['analysis_notes']}", ""]
    out.append("## Blind Spots")
    for b in d["blind_spots"]:
        out += [f"### [{b['severity']}] {b['title']}", b["explanation"],
                f"- **Why it matters:** {b['why_it_matters']}",
                f"- **Evidence needed:** {b['evidence_needed']}", ""]
    out.append("## Hidden Assumptions")
    for a in d["hidden_assumptions"]:
        out += [f"- **{a['assumption']}** (reliance: {a['confidence']})",
                f"  - Why it might be wrong: {a['why_it_might_be_wrong']}",
                f"  - How to test: {a['how_to_test_it']}"]
    out += ["", "## Possible Contradictions"]
    for c in d["contradictions"]:
        out += [f"- {c['tension']}", f"  - Parts: {c['parts_in_tension']}", f"  - Question: {c['question_to_resolve']}"]
    out += ["", "## Missing Information"]
    out += [f"- **{m['item']}**: {m['why_it_matters']}" for m in d["missing_information"]]
    out += ["", "## Alternative Perspectives"]
    out += [f"- **{p['perspective']}**: {p['insight']}" for p in d["alternative_perspectives"]]
    out += ["", "## Questions Worth Asking"]
    out += [f"{i}. {q}" for i, q in enumerate(d["reflection_questions"], 1)]
    out += ["", "## Evidence to Seek"]
    out += [f"- [ ] {e['action']} ({e['why']})" if e["why"] else f"- [ ] {e['action']}" for e in d["evidence_to_seek"]]
    if d["mind_changers"]:
        out += ["", "## What Would Change My Mind"] + [f"- {m}" for m in d["mind_changers"]]
    out += ["", "## What You're Already Doing Well"]
    out += [f"- **{s['strength']}** {s['detail']}" for s in d["reasoning_strengths"]]
    out += ["", "---", "BlindSpot AI does not make decisions. The decision remains yours."]
    return "\n".join(out)
