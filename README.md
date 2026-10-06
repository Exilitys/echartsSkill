# ECharts JSON skill

A reusable agent skill for producing strict Apache ECharts JSON options for
Streamlit's native `st.echarts_chart`. It includes setup guides for all 23 core
series types, common chart variants, a standard-library validator, and a native
Streamlit example browser. Maps, custom renderers, and extensions have separate
guidance because native Streamlit cannot render them.

## Install

Clone this repository into your agent's skill directory. For a Codex project:

```bash
git clone https://github.com/Exilitys/echartsSkill.git .agents/skills/echarts-json
```

Keep `SKILL.md`, `references/`, `examples/`, and `scripts/` together so relative
links keep working. Installation does not install Python dependencies or change
an existing application.

Invoke it with a prompt such as:

> Use $echarts-json to make a stacked bar chart from this data for st.echarts_chart.
> Return only the ECharts JSON option.

## Use the examples

The examples are complete option objects, not Python dictionaries or wrapper
parameters. Choose a file using `examples/index.json` or the chart catalog.

```python
import json
from pathlib import Path
import streamlit as st

option = json.loads(Path("examples/native/bar.json").read_text(encoding="utf-8"))
st.echarts_chart(option, height=420, key="sales")
```

Run these commands from this folder:

```bash
python scripts/validate_option.py examples/native --target streamlit
python scripts/validate_option.py examples/external --target echarts
python -m pip install "streamlit>=1.64"
streamlit run scripts/demo_app.py
```

The validator checks strict JSON, selected data contracts, and host compatibility.
It is not a complete ECharts schema; success does not prove that a chart renders
or that every optional property exists in your host's ECharts version. External
examples need their specified runtime modules or map registration.

Verified API snapshot: 2026-10-06, Streamlit 1.64/1.65 and ECharts 6.1. See
`references/sources.md` for authoritative links and `VALIDATION.md` for the
checks actually performed on this package.
