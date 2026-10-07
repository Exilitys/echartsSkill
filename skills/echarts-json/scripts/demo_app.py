"""Run with: streamlit run scripts/demo_app.py (Streamlit >= 1.64)."""

import inspect
import json
from pathlib import Path

import streamlit as st
from validate_option import load_option, validate_option

ROOT = Path(__file__).resolve().parent.parent
st.set_page_config(page_title="ECharts JSON examples", layout="wide")
st.title("ECharts JSON examples")
st.caption("Illustrative data. Choose a chart to view and download its ECharts option.")

if not hasattr(st, "echarts_chart"):
    st.error("These examples require Streamlit 1.64 or later and its native st.echarts_chart API.")
    st.stop()

catalog = json.loads((ROOT / "examples/index.json").read_text(encoding="utf-8"))
native = {entry["name"]: entry for entry in catalog["examples"] if entry["target"] == "native"}
with st.sidebar:
    selected = st.selectbox(
        "Chart", list(native), format_func=lambda name: name.replace("_", " ").title()
    )
    height = st.slider("Chart height", min_value=320, max_value=720, value=460, step=20)
    renderer = st.selectbox("Renderer", ["canvas", "svg"])
    themed = st.toggle("Apply Streamlit theme", value=True)

entry = native[selected]
raw = (ROOT / "examples" / entry["file"]).read_text(encoding="utf-8")
option = load_option(raw)
issues = validate_option(option)
errors = [i for i in issues if i.level == "ERROR"]
if errors:
    for issue in errors:
        st.error(f"{issue.path}: {issue.message}")
    st.stop()

st.caption(entry["description"])
chart_arguments = {
    "height": height,
    "renderer": renderer,
    "theme": "streamlit" if themed else None,
    "key": "example-chart",
}
if "alt" in inspect.signature(st.echarts_chart).parameters:
    chart_arguments["alt"] = entry["description"]
    # Use the native name once; retain the option description on Streamlit 1.64.
    option.get("aria", {}).get("label", {}).pop("description", None)
st.echarts_chart(option, **chart_arguments)
st.download_button(
    "Download option JSON", data=raw, file_name=f"{selected}.json", mime="application/json"
)
with st.expander("ECharts option JSON"):
    st.code(raw, language="json")
