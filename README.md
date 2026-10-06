# ECharts JSON

[![Validate](https://github.com/Exilitys/echartsSkill/actions/workflows/validate.yml/badge.svg)](https://github.com/Exilitys/echartsSkill/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/format-Agent%20Skills-2563eb)](https://agentskills.io/specification)

A portable agent skill for generating **strict Apache ECharts JSON options**,
with **Streamlit's native `st.echarts_chart`** as the default integration.

Give your agent the data and the chart you need. The skill guides it through
chart selection, data shaping, required components, formatting, compatibility,
and validation. It follows the [Agent Skills format](https://agentskills.io/specification),
so the same instructions and resources can be installed in different coding agents.

## What is included

- Setup guidance for all **23 core ECharts series types**, with native Streamlit
  support and external-runtime requirements identified separately.
- **37 native-compatible JSON examples** across 21 supported core series types,
  including stacked charts, time series, heatmaps, networks, hierarchies, gauges,
  candlesticks, and mixed bar/line charts.
- **Five external examples** for maps, named custom renderers, 3D, word cloud,
  and liquid fill, each with explicit prerequisites.
- A Python validator for strict JSON, common data-contract mistakes, and native
  Streamlit compatibility.
- A Streamlit example browser with canvas/SVG rendering, theme controls, and JSON
  downloads.

The verification baseline is **Streamlit 1.65.0 and core ECharts 6.1**. The native
API was introduced in Streamlit 1.64; that version needs the `alt` argument omitted.
See the [compatibility audit](docs/streamlit-compatibility.md) and
[validation record](VALIDATION.md) for the checks and their limits.

## Install in your agent

### Using the skills CLI

With Node.js, `npx`, and Git available, run this from your project's root:

```bash
npx skills add Exilitys/echartsSkill --skill echarts-json --copy
```

Select your agent when prompted. You can also choose it explicitly:

```bash
# Codex
npx skills add Exilitys/echartsSkill --skill echarts-json --agent codex --copy

# Claude Code
npx skills add Exilitys/echartsSkill --skill echarts-json --agent claude-code --copy

# Cursor and OpenCode together
npx skills add Exilitys/echartsSkill --skill echarts-json --agent cursor opencode --copy
```

The CLI also has targets for Gemini CLI, GitHub Copilot, Windsurf, and other
agents. `--copy` creates independent files instead of symlinks. For more options,
manual installation, global locations, updating, and removal, see
[installation](docs/installation.md).

### Using Git or a downloaded ZIP

No Node.js is needed for a direct Git installation. For Codex, run:

```bash
git clone https://github.com/Exilitys/echartsSkill.git .agents/skills/echarts-json
```

For other agents, change the destination to their skill directory. For example,
Claude Code uses `.claude/skills/echarts-json` and Cursor supports
`.cursor/skills/echarts-json`.

You can also download the repository ZIP from **Code → Download ZIP**, rename the
extracted folder to **`echarts-json`**, and place it in your agent's skills
directory. Keep the entire folder together; copying only `SKILL.md` loses the
references and examples. Restart or reload skills if your agent does not discover
the new skill immediately.

Installing the skill requires no Python packages, API keys, or MCP server.
Python is optional for validation; Streamlit is needed only to render the charts
or run the demo.

## Use it

For agents that accept natural-language skill selection:

> Use the echarts-json skill to create a stacked bar chart of monthly revenue
> by channel from this data. Target Streamlit 1.65. Return only the ECharts JSON
> option, without Markdown or Python.

In Codex you can name **`$echarts-json`** explicitly. In Claude Code you can invoke
**`/echarts-json`**. Other agents use their own skill selector or activation flow.

Useful requests include:

- “Turn these timestamp/value rows into a time-series chart with a zoom slider.”
- “Create a heatmap from this table and label the color scale.”
- “Repair this candlestick JSON; the prices are in OHLC order.”
- “Use a donut chart with a string-template tooltip and readable percentages.”
- “Check this option for native Streamlit compatibility.”

Provide the data, units, preferred chart, and any required style or interactions.
The skill can also choose a chart from the analytical question.

## Render the generated JSON in Streamlit

Install Streamlit in your application's environment:

```bash
python -m pip install "streamlit==1.65.0"
```

Save the generated option as `chart.json`. It is a complete ECharts option object,
such as:

```json
{
  "tooltip": {"trigger": "axis"},
  "xAxis": {"type": "category", "data": ["A", "B", "C"]},
  "yAxis": {"type": "value", "name": "Units"},
  "series": [{"id": "units", "name": "Units", "type": "bar", "data": [12, 18, 9]}]
}
```

Pass the JSON string directly, or load it as a dictionary:

```python
from pathlib import Path
import streamlit as st

spec = Path("chart.json").read_text(encoding="utf-8")
st.echarts_chart(
    spec,
    width="stretch",
    height=420,
    theme="streamlit",
    key="units-chart",
    renderer="canvas",
    alt="Units for categories A, B, and C",
)
```

`width`, `height`, `theme`, `key`, `renderer`, and `alt` are **Python wrapper
arguments**, separate from the option. For Streamlit 1.64, omit `alt` and use
`aria.label.description` inside the option instead.

### Native compatibility

| Feature | Native `st.echarts_chart` |
| --- | --- |
| Option dictionary, JSON string, or compatible pyecharts chart | Supported |
| Dataframe-like `dataset.source` | Converted to records; dimensions preserve column order |
| String-template formatters | Supported where the ECharts property accepts a template |
| Legends, dataZoom, toolbox, and other in-chart controls | Supported |
| JavaScript functions / `JsCode` | Unsupported |
| `custom` series, including a named registered renderer | Unsupported |
| Maps, `geo`, and geographic coordinates | Unsupported |
| ECharts GL and separately loaded extensions | Unsupported |
| Python selection or click event callbacks | No native event bridge |

`theme=None` preserves your styling while accessibility and default cursor
settings still apply. In 1.65, a nonempty `alt` overrides the option's accessible
description and keeps the chart named. Labels inside an option use ECharts text
formatting; put Streamlit Markdown outside the chart.

The older `streamlit-echarts` component is a separate integration with its own
API. See [Streamlit integration](references/streamlit.md) for the distinction.

## Browse examples and validate an option

From this repository or the installed skill folder:

```bash
python scripts/validate_option.py chart.json --target streamlit
python scripts/validate_option.py examples/native --target streamlit
python scripts/validate_option.py examples/external --target echarts
python -m streamlit run scripts/demo_app.py
```

The validator uses only the Python 3.10+ standard library. It checks selected data
contracts and compatibility; it is not a complete ECharts schema or a rendering
test. External-target success does not load a map or extension. See the
[chart catalog](references/chart-catalog.md) and [example index](examples/index.json).

If you run validation from an application folder, use the validator's absolute
path and keep `chart.json` relative to the application folder.

## Repository layout

```text
SKILL.md                  Agent instructions and portable metadata
agents/openai.yaml        Optional Codex display and invocation metadata
references/               Chart contracts and integration guides
examples/native/          Native Streamlit JSON options
examples/external/        Options requiring another prepared host
examples/assets/          Synthetic geographic example data
scripts/                  Validator, example browser, and ZIP builder
docs/                     Installation and compatibility audit
tests/                    Validator, package, and Streamlit integration checks
```

The skill uses progressive disclosure: an agent reads the catalog and only the
guides relevant to the current request. Optional Codex metadata does not change
the portable instructions.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, tests, formatting, browser checks,
and packaging. Changes are tracked in [CHANGELOG.md](CHANGELOG.md). Report bugs
or request examples through [GitHub issues](https://github.com/Exilitys/echartsSkill/issues).

## License and references

[MIT](LICENSE). The configurations use illustrative data; the geographic asset
contains synthetic regions. Apache ECharts, Streamlit, and other referenced
projects keep their own licenses.

See [sources](references/sources.md) for authoritative API documentation. This is
an independent skill repository and is not an official Streamlit or Apache project.
