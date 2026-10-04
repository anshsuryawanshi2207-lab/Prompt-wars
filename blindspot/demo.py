"""Internship example + handcrafted offline analyses.

The offline results let the demo work with no API key, no internet and no quota,
which makes the live demo failure-proof."""
from __future__ import annotations

import copy

from .schema import apply_guardrails, normalize

EXAMPLE_FORM = {
    "decision": "Should I accept a six-month software internship, or stay on campus this semester?",
    "option_a": "Accept the internship: ₹25,000/month stipend, 20 minutes from home, hands-on industry experience.",
    "option_b": "Decline and focus on the semester: coursework, a research project with a professor, and my hackathon team.",
    "context": "I'm a third-year B.Tech student. The offer arrived yesterday and expires in 5 days. The company is a mid-size IT services firm.",
    "leaning_reason": "The stipend is good, it's close to home so I'd save on hostel costs, and everyone says industry experience matters for placements.",
    "priorities": "Money, career growth, and finishing the semester with a good CGPA.",
    "factors": "Stipend, distance from home, industry experience.",
    "constraints": "Offer expires in 5 days. My college has a 75% attendance rule.",
    "worries": "I might miss a better offer later. I'm not sure my mentor will actually teach me anything.",
    "additional": "The recruiter said the role is 'software development related' but didn't name the team or technologies. Hours are 'flexible'.",
}


def is_example(form: dict) -> bool:
    return (form.get("decision") or "").strip() == EXAMPLE_FORM["decision"]


_BASE = {
    "decision_summary": "You are weighing a six-month software internship (Option A) against staying on campus for coursework, research and hackathons (Option B), with a 5-day deadline.",
    "reasoning_strength": 52,
    "information_coverage": 38,
    "assumption_risk": 68,
    "blind_spot_level": "HIGH",
    "analysis_notes": "",
    "blind_spots": [
        {
            "title": "Academic Opportunity Cost",
            "severity": "HIGH",
            "explanation": "You list finishing the semester with a good CGPA as a priority, but your reasoning for Option A never addresses how six months of work fits with classes and the 75% attendance rule.",
            "why_it_matters": "A six-month commitment could quietly trade away the very priority you named, and that trade-off is currently under-represented in your reasoning.",
            "evidence_needed": "Expected weekly hours, whether work is on-site or remote, college policy on internships during term, exam-period flexibility in writing.",
        },
        {
            "title": "Unknown Role Content",
            "severity": "HIGH",
            "explanation": "The recruiter described the role only as 'software development related'. Your case for 'industry experience' rests on a role you cannot yet describe.",
            "why_it_matters": "Experience in maintenance, testing or support can carry very different career value from building features, yet the label 'industry experience' hides that difference.",
            "evidence_needed": "Team name, tech stack, a sample first-month task, who you would report to, what past interns worked on.",
        },
        {
            "title": "Option B Is Described Vaguely",
            "severity": "MEDIUM",
            "explanation": "Option A has numbers (stipend, distance); Option B is a list of activities with no stated outcomes. The two options are not described at the same level of detail.",
            "why_it_matters": "When one option is concrete and the other is abstract, the concrete one tends to feel safer even if the abstract one has real, measurable upside.",
            "evidence_needed": "What the professor's project could produce (paper, recommendation letter, portfolio piece), and your hackathon team's realistic goals.",
        },
        {
            "title": "Deadline Pressure Has Not Been Examined",
            "severity": "MEDIUM",
            "explanation": "The 5-day expiry shapes your thinking, and one of your worries is 'missing a better offer later', but there is no information on whether the deadline is negotiable.",
            "why_it_matters": "Urgency narrows attention to visible factors. A short extension or a delayed start might change the shape of the decision.",
            "evidence_needed": "Whether the company would extend the deadline or allow a later or part-time start.",
        },
        {
            "title": "Financial Picture Is One-Sided",
            "severity": "LOW",
            "explanation": "The stipend and hostel savings are counted, but costs (commuting, meals, equipment, any income or scholarships you would forgo) are not.",
            "why_it_matters": "A net figure may look different from the headline stipend.",
            "evidence_needed": "A simple monthly budget for both options.",
        },
    ],
    "hidden_assumptions": [
        {
            "assumption": "Industry experience will automatically improve my placement prospects.",
            "confidence": "HIGH",
            "why_it_might_be_wrong": "The value depends on role relevance, real responsibilities, mentorship and whether you can show measurable outcomes. 'Everyone says' is not evidence about this particular role.",
            "how_to_test_it": "Ask placement seniors how recruiters weighed internships like this one, and ask the company what past interns shipped.",
        },
        {
            "assumption": "I can handle internship work and semester coursework together.",
            "confidence": "HIGH",
            "why_it_might_be_wrong": "'Flexible hours' is unverified, and workload tends to spike during exams and project deadlines.",
            "how_to_test_it": "Request the expected weekly hours and any exam-time policy in writing, then map them against your timetable.",
        },
        {
            "assumption": "A better offer might not come later, so this one is scarce.",
            "confidence": "MEDIUM",
            "why_it_might_be_wrong": "This is a prediction about the future with no data behind it. Internship cycles often repeat, and skills built this semester could widen your later options.",
            "how_to_test_it": "Check when relevant internship cycles open at your college and what seniors received in comparable windows.",
        },
        {
            "assumption": "My mentor at the company may not teach me much, so I just have to accept that risk.",
            "confidence": "MEDIUM",
            "why_it_might_be_wrong": "Mentorship quality can often be probed before accepting, so it may be an information gap rather than a fixed risk.",
            "how_to_test_it": "Ask to speak with a current or former intern or your prospective mentor before the deadline.",
        },
    ],
    "contradictions": [
        {
            "tension": "You may want to examine a possible tension between your stated priority of a good CGPA and the factors driving your lean toward Option A.",
            "parts_in_tension": "Priority: 'finishing the semester with a good CGPA' vs. reasons given: stipend, distance, industry experience.",
            "question_to_resolve": "Where does academic performance show up in your reasons for Option A?",
        },
        {
            "tension": "There may be a tension between valuing career growth and being unsure the mentor will teach you anything.",
            "parts_in_tension": "Priority: 'career growth' vs. worry: 'not sure my mentor will actually teach me'.",
            "question_to_resolve": "If learning is uncertain, what exactly is the career-growth case resting on?",
        },
        {
            "tension": "You may want to examine whether the factors you call most important are the ones that are easiest to see.",
            "parts_in_tension": "Most important factors: stipend, distance, experience (two of three are quick to quantify) vs. harder-to-measure factors such as learning, health and optionality.",
            "question_to_resolve": "Which important factors are missing from your list because they are hard to measure?",
        },
    ],
    "missing_information": [
        {"item": "Weekly time commitment and schedule flexibility", "why_it_matters": "Determines whether the internship and your coursework can realistically coexist."},
        {"item": "Actual role, team, technologies and mentor", "why_it_matters": "The value of 'experience' depends on what you would actually do and learn."},
        {"item": "Whether the deadline or start date is negotiable", "why_it_matters": "A little flexibility could change the whole shape of the choice."},
        {"item": "Reversibility: can you leave early without penalty?", "why_it_matters": "A reversible choice carries a different risk than a six-month lock-in."},
        {"item": "College policy on internships during term and attendance", "why_it_matters": "A policy conflict could make the option infeasible or costly."},
        {"item": "Concrete outcomes expected from Option B", "why_it_matters": "Without them, the two options aren't being compared on equal footing."},
    ],
    "alternative_perspectives": [
        {"perspective": "Five-year self", "insight": "Looking back from five years ahead, which of these six months would most plausibly show up on a resume, in a portfolio or in your skills, and why?"},
        {"perspective": "Pre-mortem", "insight": "Imagine it is six months later and the choice went badly. What is the most likely story for each option? Which failure would be harder to recover from?"},
        {"perspective": "Opportunity cost", "insight": "Every hour of the internship is an hour not spent on Option B's activities. What is the best thing those hours could produce?"},
        {"perspective": "Outside advisor", "insight": "A placement officer, a professor and a working engineer might each weigh these factors very differently. What would each notice that you haven't?"},
        {"perspective": "Hybrid options", "insight": "The framing is binary, but part-time, remote, delayed-start or shorter-duration versions may exist. Have you asked?"},
    ],
    "reflection_questions": [
        "If the stipend were 30% lower, would your thinking change? What does that tell you about its weight?",
        "What specific evidence makes you believe this internship will provide meaningful mentorship?",
        "What is the worst realistic outcome of each option, and how recoverable is it?",
        "What information would change your mind, in either direction?",
        "If your best friend were in your position, what would you tell them to investigate first?",
        "Which of your reasons would still hold if the stipend and the distance were removed?",
        "Who has made a similar choice, and what do they say they underestimated?",
    ],
    "evidence_to_seek": [
        {"action": "Ask the recruiter for the team, tech stack, weekly hours and a sample first-month task, in writing.", "why": "Turns 'software development related' into something you can evaluate."},
        {"action": "Talk to 2 past interns from this company or seniors at your college.", "why": "First-hand data on mentorship, workload and what the experience led to."},
        {"action": "Read your college rules on attendance and internships during term.", "why": "Confirms feasibility before you weigh anything else."},
        {"action": "Ask the professor what the research project could realistically produce.", "why": "Gives Option B concrete outcomes to compare."},
        {"action": "Ask whether the offer deadline can be extended by a few days.", "why": "Reduces time pressure so you can gather the rest."},
    ],
    "reasoning_strengths": [
        {"strength": "You named your worries openly.", "detail": "Mentorship quality and missing a better offer are real risks, and stating them gives you something to investigate."},
        {"strength": "You have explicit priorities.", "detail": "Money, career growth and CGPA give you a yardstick to hold each option against."},
        {"strength": "You noticed the unknowns.", "detail": "You flagged vague hours and an unnamed team, which is the first step toward asking the right questions."},
    ],
    "reasoning_map": [
        {"claim": "The stipend is good.", "type": "EVIDENCE", "note": "A concrete, verifiable number (though it is not yet net of costs)."},
        {"claim": "It's close to home so I'd save on hostel costs.", "type": "EVIDENCE", "note": "Concrete and checkable, as long as the savings are compared with real costs."},
        {"claim": "Everyone says industry experience matters for placements.", "type": "ASSUMPTION", "note": "Hearsay about a general claim, not evidence about this role."},
        {"claim": "Industry experience will help my career growth.", "type": "ASSUMPTION", "note": "Depends on role content that is currently unknown."},
        {"claim": "I might miss a better offer later.", "type": "EMOTION", "note": "Fear of loss, a prediction rather than data."},
        {"claim": "I want to finish the semester with a good CGPA.", "type": "VALUE", "note": "A stated priority, but it doesn't appear in the reasons for Option A."},
        {"claim": "Hours are 'flexible'.", "type": "UNKNOWN", "note": "Reported by the recruiter, with no specifics."},
        {"claim": "I'm not sure my mentor will teach me anything.", "type": "UNKNOWN", "note": "An open question that could be investigated before the deadline."},
    ],
    "attention_balance": [
        {"factor": "Stipend / money", "importance": 80, "attention": 90, "note": "Detailed, quantified and repeated."},
        {"factor": "Distance from home", "importance": 45, "attention": 75, "note": "Receives more attention than its stated weight."},
        {"factor": "Career growth / learning", "importance": 90, "attention": 35, "note": "Rated highly, but supported only by hearsay and open questions."},
        {"factor": "CGPA / academics", "importance": 85, "attention": 15, "note": "Named as a priority, then absent from the reasoning."},
        {"factor": "Option B's upside", "importance": 70, "attention": 20, "note": "Described as activities, with no expected outcomes."},
        {"factor": "Health, workload and burnout", "importance": 55, "attention": 0, "note": "Not mentioned. Importance estimated from the nature of a 6-month dual workload."},
        {"factor": "Reversibility / exit options", "importance": 60, "attention": 0, "note": "Not mentioned. Importance estimated from the six-month commitment."},
    ],
    "mind_changers": [
        "Learning that the role is mostly support or testing rather than building features.",
        "Learning that the company allows a flexible, part-time or deferred start with academic protections.",
        "Learning that Option B's project has a concrete outcome such as a publication or a strong recommendation letter.",
    ],
}


def _finish(raw: dict, source: str = "demo") -> dict:
    data = normalize(raw)
    data, n = apply_guardrails(data)
    data["_guardrail_count"] = n
    data["_source"] = source
    return data


def demo_analysis() -> dict:
    return _finish(copy.deepcopy(_BASE))


def demo_challenge() -> dict:
    raw = copy.deepcopy(_BASE)
    raw.update({"reasoning_strength": 44, "assumption_risk": 74})
    raw["analysis_notes"] = "Challenge mode (offline sample): these points push harder than the first pass. They are questions to test, not conclusions."
    raw["blind_spots"].insert(0, {
        "title": "Pre-Mortem: How This Fails Quietly",
        "severity": "HIGH",
        "explanation": "A plausible failure story for Option A is that both the internship and your grades end up mediocre because attention was split, and the 'experience' turned out to be repetitive tasks. Your current reasoning has no stress test for this scenario.",
        "why_it_matters": "A reasoning chain that has never been tested against its own failure is a chain you may be trusting more than it deserves.",
        "evidence_needed": "A written list of how you would notice the arrangement failing by week 4, and what exit options you would have.",
    })
    raw["blind_spots"].insert(1, {
        "title": "Steelman of the Option You Are Leaning Away From",
        "severity": "MEDIUM",
        "explanation": "You described Option B only as activities. At its strongest, it could be a research output, a mentor who knows you well and a team project, advantages that usually take a full semester to build.",
        "why_it_matters": "If you have not articulated the best case for the other option, your preference may be untested rather than established.",
        "evidence_needed": "Write the best honest 5-sentence case for Option B and see whether any of it surprises you.",
    })
    raw["reflection_questions"] = [
        "If you could not mention money or distance, what would your case for Option A be?",
        "What is the weakest link in your own argument, and how do you know?",
        "What would you need to see in the next 5 days to feel confident saying no?",
        "If the recruiter described the role honestly as mostly maintenance work, would your reasoning still hold?",
        "Are you choosing the option you want or the option you can justify to others?",
        "What would your reasoning look like if the offer had no deadline?",
    ]
    raw["alternative_perspectives"][1]["insight"] = "Pre-mortem: assume that six months from now you regret Option A. Write the three most likely reasons. Then do the same for Option B. Which list feels more specific?"
    return _finish(raw)


def demo_strengthen() -> dict:
    raw = copy.deepcopy(_BASE)
    raw.update({"reasoning_strength": 68, "information_coverage": 62, "assumption_risk": 49, "blind_spot_level": "MEDIUM"})
    raw["analysis_notes"] = "Strengthen mode (offline sample): each item below is a cheap, fast test that would make your reasoning more robust. Suggested thresholds are for you to adjust."
    for b in raw["blind_spots"]:
        if b["severity"] == "HIGH":
            b["severity"] = "MEDIUM"
    raw["evidence_to_seek"] = [
        {"action": "Day 1: email the recruiter 5 questions (team, stack, weekly hours, first-month task, past interns' projects).", "why": "Fast, cheap and converts the biggest unknown into facts."},
        {"action": "Day 1-2: message 2 past interns or seniors with one question: 'What did you actually build, and what did you wish you'd known?'", "why": "Tests the mentorship and 'experience' assumptions at once."},
        {"action": "Day 2: build a one-page weekly timetable with the internship hours and your classes, labs and attendance.", "why": "If the timetable breaks on paper, it will likely break in practice."},
        {"action": "Day 3: ask your professor what concrete output the research project could have by semester end.", "why": "Gives Option B a measurable outcome so both options are compared evenly."},
        {"action": "Day 3-4: ask the company whether the deadline or start date can move by one week.", "why": "Buys time for the rest of the evidence to arrive."},
    ]
    raw["mind_changers"] = [
        "Weekly hours above roughly 20 during term would conflict with the attendance rule you described (set your own threshold).",
        "A named mentor and a described first project would strengthen the 'experience' assumption considerably.",
        "A concrete research outcome for Option B would weaken the 'only the internship has tangible value' impression.",
    ]
    return _finish(raw)
