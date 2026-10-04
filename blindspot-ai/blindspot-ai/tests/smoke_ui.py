"""Runs app.py end-to-end against a stubbed Streamlit (no server needed)."""
import os, runpy, sys
from unittest.mock import MagicMock
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); os.chdir(ROOT)

class SS(dict):
    __getattr__ = dict.get
    def __setattr__(self, k, v): self[k] = v

def make_stub(state):
    st = MagicMock()
    st.session_state = state
    st.columns.side_effect = lambda spec, **k: [MagicMock() for _ in range(spec if isinstance(spec, int) else len(spec))]
    st.form_submit_button.return_value = False
    st.button.return_value = False
    st.checkbox.return_value = False
    st.radio.side_effect = lambda label, options, **k: options[k.get("index", 0)]
    st.text_input.return_value = ""; st.text_area.return_value = ""
    return st

def run(state):
    sys.modules["streamlit"] = make_stub(state)
    for m in [m for m in sys.modules if m.startswith("blindspot")]: del sys.modules[m]
    runpy.run_path(os.path.join(ROOT, "app.py"), run_name="__main__")

# 1) landing page renders
s = SS(); run(s); assert s["page"] == "input"; print("PASS input page")

# 2) results page for every version renders
from blindspot import demo
for fn, mode in ((demo.demo_analysis, "analyze"), (demo.demo_challenge, "challenge"), (demo.demo_strengthen, "strengthen")):
    runs = [{"mode": "analyze", "data": demo.demo_analysis()}, {"mode": mode, "data": fn(), "notice": "n"}]
    s = SS(page="results", runs=runs, active=1, form=dict(demo.EXAMPLE_FORM)); run(s)
    print("PASS results", mode)

# 3) offline example path via analyse() fallback (no API key)
for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY"): os.environ.pop(k, None)
sys.modules["streamlit"] = make_stub(SS())
for m in [m for m in sys.modules if m.startswith("blindspot")]: del sys.modules[m]
ns = runpy.run_path(os.path.join(ROOT, "app.py"), run_name="not_main")
data, notice = ns["analyse"](dict(demo.EXAMPLE_FORM), "challenge", None)
assert data and "offline" in notice; print("PASS offline fallback")
