---
name: echarts-json
description: Generate, adapt, validate, and repair Apache ECharts option objects as strict JSON, especially for Streamlit's native st.echarts_chart. Use for chart selection, series and coordinate setup, datasets, axes, tooltips, legends, zoom, and styling across all built-in ECharts chart families. Explain compatibility when requests require maps, custom JavaScript, or extensions.
license: MIT
compatibility: Instructions work in agents supporting the Agent Skills format. Optional scripts require Python 3.10+. Native chart integration targets Streamlit 1.65.0 and core ECharts 6.1; Streamlit 1.64 is supported without the alt argument.
metadata:
  author: Exilitys
  version: "1.1.0"
---

# ECharts JSON

Create a complete ECharts **option object** that matches the user's data and the
target renderer. Default to strict JSON and native Streamlit when the request
mentions `st.echarts`, `st.echarts_chart`, or this skill without another target.

## Read only what the task needs

1. Read [Streamlit integration](references/streamlit.md) for Streamlit requests.
2. Use [chart catalog](references/chart-catalog.md) to select the chart and example.
3. Read the relevant setup guide:
   - [Cartesian and polar](references/cartesian.md): line, bar, scatter, effects,
     boxplot, candlestick, pictorial bar, heatmap, and mixed charts.
   - [Circular and hierarchical](references/hierarchy.md): pie, radar, tree,
     treemap, sunburst, funnel, and gauge.
   - [Relationships and special coordinates](references/relationships.md):
     graph, sankey, chord, lines, parallel, theme river, calendar, and matrix.
   - [Shared components and data](references/components.md): dataset/encode,
     axes, tooltip, legend, visualMap, dataZoom, toolbox, brush, timeline, media,
     styling, accessibility, and performance.
   - [Maps, custom series, and extensions](references/extensions.md) when needed.
4. Use [sources](references/sources.md) to verify unfamiliar or version-dependent
   options. The guides cover setup contracts; the upstream option reference is
   the authority for the full property surface.

## Work through this sequence

1. **Identify the target.** Native `st.echarts_chart` is the default. The older
   `from streamlit_echarts import st_echarts` is a separate component with a
   different API. Respect an explicit host or version. For an existing app,
   inspect its imports and installed version before changing integration.
2. **Identify the data contract.** Determine dimensions, units, missing values,
   ordering, aggregation, and whether values represent totals, rates, or flows.
   Use supplied data. If no data is provided and an example is requested, use a
   small illustrative dataset and identify it as sample data outside the JSON.
   Ask only when missing information materially prevents correct configuration.
3. **Select a supported representation.** Use the catalog's purpose and data
   shapes. Explain an unavailable chart briefly and propose a compatible chart
   that preserves the user's analytical intent. Do not silently change the host
   or install another component to work around a native limitation.
4. **Build the smallest complete option.** Start from the matching example under
   `examples/native/`. Replace all sample data and relevant labels. Add the
   required coordinate components, choose axis types, and map dimensions
   explicitly when using a dataset. Keep wrapper arguments outside the option.
5. **Apply useful presentation.** Include a clear title or surrounding app
   heading, units, a suitable tooltip, and legends for multiple series. Reserve
   space for controls. Use the user's theme; otherwise let Streamlit supply
   colors and fonts. Include an accessible description when its meaning is known.
6. **Validate.** Parse strict JSON, check shape and analytical consistency, and
   run the bundled validator when a shell is available:

   ```bash
   python "/absolute/path/to/echarts-json/scripts/validate_option.py" chart.json --target streamlit
   ```

   Resolve the script path from this skill's installed directory, keeping
   `chart.json` relative to the user's working directory or using its absolute
   path. Do not assume the skill is installed in the app's repository root.
   For another ECharts host, use `--target echarts`; external examples still
   require the assets or modules described in the extensions guide. Use
   `--echarts-major 5` for a known v5 host.
   This is a focused linter, not a full ECharts schema or a rendering test. Review
   warnings and, when possible, render once in the actual app and check browser
   errors, legends, labels, tooltip content, zoom, and narrow-screen layout.
7. **Deliver the requested artifact.** If asked for JSON only, return one strict
   JSON object with no explanation, Python, wrapper, or Markdown fence. Otherwise
   give the option and a short integration snippet if useful, with only material
   assumptions or compatibility notes. Do not claim a render was tested unless
   it was actually rendered.

## Strict JSON rules

- Double-quoted keys and strings; lowercase `true`, `false`, and `null`.
- No comments, trailing commas, `undefined`, `NaN`, `Infinity`, duplicate keys,
  Python expressions, dates as objects, typed arrays, or JavaScript functions.
- Export the option itself, not `{"options": ...}` or `{"spec": ...}`. ECharts'
  timeline envelope `{"baseOption": ..., "options": [...]}` is a valid exception.
- Use a `series` array. Every new series must have a valid, case-sensitive `type`.
  Give series stable `id` values when options change across Streamlit reruns.
- String-template formatters are allowed. A string containing JavaScript source
  is still not an executable formatter in native Streamlit. `JsCode` does not
  make callbacks JSON-compatible.
- Precompute derived data in Python: bins, boxplot summaries, percentages,
  conditional item colors, symbol sizes, formatted category names, and transforms
  that need external registration. Return their JSON-native results.
- Keep `height`, `width`, `theme`, `key`, `renderer`, and version-specific `alt`
  as `st.echarts_chart` arguments. They are not ECharts option keys.
- Preserve `null` as missing, not zero. Use `connectNulls` only if the user intends
  to interpolate gaps. Avoid silently dropping or merging observations.

## Native Streamlit compatibility

The documented native method is **`st.echarts_chart`**, available since Streamlit
1.64. The verification baseline is **Streamlit 1.65.0** with core ECharts 6.1.
Check the installed version rather than assuming a future host matches that
snapshot.

Native options support ordinary built-in charts, including chord, and ECharts
controls inside the chart. Native Streamlit does **not** support:

- `type: "map"`, a `geo` component, or `coordinateSystem: "geo"`;
- `type: "custom"`, even with a named, JSON-string `renderItem`;
- JavaScript callbacks or arbitrary module/transform registration;
- ECharts GL, `wordCloud`, `liquidFill`, or other separately loaded extensions;
- the third-party component's `events` or `on_select` arguments.

The default `theme="streamlit"` applies app colors, fonts, and layout. Use
`theme=None` for an explicitly styled option; native accessibility and cursor
defaults still apply unless the option overrides them. In 1.65+, a nonempty
`alt` overrides `aria.label.description` and gives the chart an accessible name
even when `aria.enabled` was false. Prefer a specific short description and
avoid an empty `alt` string.

For native route/path charts, explicitly use `lines.coordinateSystem:
"cartesian2d"`; its ECharts default is geographic. A calendar or matrix is a
coordinate component, not a new series type. Area, donut, rose, histogram,
waterfall, and bubble are configurations or data preparations of existing types.

## Correctness checklist

- Each series has the coordinate components it requires and valid indexes.
- Category labels and scalar observations align; time observations are sorted
  and use an explicit timezone or documented local-date interpretation.
- Dataset `dimensions`, `encode`, `datasetIndex`, and source headers agree.
- Boxplots use `[lowWhisker, Q1, median, Q3, highWhisker]`; candlesticks use
  `[open, close, low, high]`.
- Radar values align with indicators. Heatmap cells use `[xIndex, yIndex, value]`
  and have a `visualMap` whose dimension targets the value.
- Graph/chord/sankey links resolve to existing nodes; sankey is acyclic.
- Tree structures are valid; hierarchy values do not double-count parent totals.
- Pie/funnel/area-size encodings use meaningful nonnegative values. Gauge bounds
  and percent units match the data. Percentage stacks are normalized before
  plotting and define the handling of a zero total.
- A log axis has positive plotted values. Dual axes have distinct labeled units.
  A quantitative bar axis includes zero unless explicitly justified.
- Legend, title, toolbox, dataZoom, grid, visualMap, and outside labels have room.
- No unsupported native features hide in `baseOption`, timeline `options`, or
  responsive `media[*].option` overrides.

## Tiny native integration

```python
import json
from pathlib import Path
import streamlit as st

option = json.loads(Path("chart.json").read_text(encoding="utf-8"))
st.echarts_chart(option, height=420, key="chart", alt="Monthly revenue in USD")
```

Tailor `alt` to the actual data; the text above assumes a monthly revenue chart.
For Streamlit 1.64, omit `alt` and set `aria.label.description` in the option.
For a runnable example browser, resolve `scripts/demo_app.py` inside this skill's
directory and run it with Streamlit installed. All bundled data is illustrative.
The demo offers only native-compatible examples. Agents without shell access can
still follow these instructions and return JSON; running a script is optional.
