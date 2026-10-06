# Streamlit integration

## Native API and version checks

The native method is `st.echarts_chart`, introduced in **Streamlit 1.64.0**.
`st.echarts` is not the documented name. Inspect an existing project's imports
and version before changing code:

```python
import inspect
import streamlit as st

print(st.__version__)
print(inspect.signature(st.echarts_chart))
```

The 1.65 signature is:

```python
st.echarts_chart(
    spec,
    *,
    width="stretch",
    height="content",
    theme="streamlit",
    key=None,
    renderer="canvas",
    alt=None,
)
```

`alt` was added in 1.65. Omit it for a 1.64 app, or put an accessible description
in `option["aria"]["label"]["description"]`. The 1.65 frontend dependency is
ECharts `^6.1.0`; this is a versioned snapshot, not a promise about other hosts.

## Input contract

`spec` accepts an ECharts option as a Python dictionary, a JSON string, or a
compatible pyecharts instance with `dump_options()`. Generate strict JSON by
default. Native input never evaluates JavaScript source.

```python
import json
from pathlib import Path
import streamlit as st

raw_json = Path("chart.json").read_text(encoding="utf-8")
option = json.loads(raw_json)
st.echarts_chart(option, height=420, key="monthly-revenue")
# Passing raw_json directly is also supported.
```

Native can normalize dataframe-like `dataset.source` values. That convenience
does not make a dataframe valid JSON. If the deliverable is a JSON file, convert
to records and set dimensions explicitly:

```python
records = json.loads(df.to_json(orient="records", date_format="iso"))
option = {
    "dataset": {"dimensions": ["month", "revenue"], "source": records},
    "xAxis": {"type": "category"},
    "yAxis": {"type": "value", "name": "USD"},
    "series": [{
        "id": "revenue", "name": "Revenue", "type": "bar",
        "encode": {"x": "month", "y": "revenue"},
    }],
}
# records must have month/revenue columns; normalize nonfinite values first.
json.dumps(option, allow_nan=False)
```

Do not put dataframe objects in `series.data`, use `default=str` to conceal
unsupported objects, or emit `NaN`/`Infinity` as JSON tokens. Reject duplicate
dimension names, including columns that become identical when converted to strings.

## Wrapper options

| Argument | Native contract | Practical choice |
| --- | --- | --- |
| `width` | `"stretch"`, `"content"`, or integer pixels | Usually `"stretch"` |
| `height` | `"content"`, `"stretch"`, or integer pixels | Explicit integer such as `420` |
| `theme` | `"streamlit"` or `None` | Default for app styling; `None` for an explicitly styled option |
| `key` | Stable element identity | Use a meaningful stable key |
| `renderer` | `"canvas"` or `"svg"` | Canvas for dense data; SVG for crisp scalable output |
| `alt` | Description, Streamlit 1.65+ | A short explanation of what the chart measures |

Native `height` is not a CSS string such as `"420px"`. `theme="dark"` and
`use_container_width=True` are not parameters of this API. When no explicit size
is provided, content defaults are 350px high and 700px wide; stretch width is the
default. Set dimensions on the wrapper, not in the option.

ECharts titles and labels do not parse Streamlit Markdown. Place formatted app
copy in `st.markdown` around the chart. Stable series IDs and a stable `key` help
updates across reruns; they do not guarantee every interaction survives a
changed option. The API returns a chart element, not selection data.

## Compatibility boundaries

Ordinary JSON-configurable core charts and in-chart controls such as legend
selection, zoom, and toolbox are supported. Python click/selection handlers are
not exposed by this native API. Do not invent `events`, `on_select`, `on_click`,
`maps`, or JavaScript-evaluation parameters.

The documented native host rejects map/geo charts, custom series, GL charts and
components, word clouds, and liquid fill. External JS transforms and registered
custom renderers are also not available through a JSON option. Precompute results
or choose a supported representation. If the user explicitly needs the missing
feature, explain the requirement before switching integration.

String-formatters such as `{b}: {c}` work where the ECharts property accepts them.
Callback-only fields such as `tooltip.valueFormatter` cannot be repaired by
storing a JavaScript function in a JSON string. Use the default tooltip, a
supported template, or preformatted labels.

Streamlit provides its own hover toolbar. Position an ECharts `toolbox` away
from it; omit `saveAsImage` if Streamlit's download control suffices.

## Older third-party component

Only use this route when the app already uses it or the user requests it:

```python
from streamlit_echarts import st_echarts

st_echarts(options=option, height="420px", key="monthly-revenue")
```

This component is installed with `streamlit-echarts`. It is not an alias for
`st.echarts_chart`: it uses `options`, CSS-size strings, and its own versioned
APIs for events, map registration, and JS support. Check the installed component's
documentation/signature before using those features. Legacy releases may bundle
ECharts 5; newer component versions have different capabilities.
