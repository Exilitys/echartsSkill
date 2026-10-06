# Streamlit 1.65 compatibility audit

Baseline: **Streamlit 1.65.0**, checked on **2026-10-06** against the official
[API documentation](https://docs.streamlit.io/develop/api-reference/charts/st.echarts_chart),
the [versioned Python implementation](https://github.com/streamlit/streamlit/blob/1.65.0/lib/streamlit/elements/echarts_chart.py),
and the [frontend implementation](https://github.com/streamlit/streamlit/blob/1.65.0/frontend/lib/src/components/elements/EChartsChart/EChartsChart.tsx).
The frontend depends on [core ECharts 6.1](https://github.com/streamlit/streamlit/blob/1.65.0/frontend/lib/package.json).

## Documented contract

```python
st.echarts_chart(
    spec, *, width="stretch", height="content", theme="streamlit",
    key=None, renderer="canvas", alt=None,
)
```

| Documentation requirement | Skill/repository behavior |
| --- | --- |
| Native method is `st.echarts_chart` | Used in every native integration and the demo |
| Accept dictionary, JSON string, or a compatible pyecharts chart | Generate strict JSON; explain the three inputs and test them with native serialization |
| Dataframe-like `dataset.source` becomes records | Guide explains automatic conversion; integration tests verify records, dimensions, and missing values |
| Width accepts stretch/content/integer; fixed width respects parent bounds | Wrapper guide and README use supported values |
| Height accepts content/stretch/integer; default content height is 350px | Demo uses integer height, not CSS strings |
| Theme is streamlit or None | Demo exposes those two choices |
| Theme None still applies accessibility/cursor defaults | Explicit in the skill and Streamlit guide; browser checks use both theme modes |
| Stable key maintains element identity | Explained without promising every interaction survives an option change |
| Canvas and SVG rendering | Both offered in the demo and browser checks |
| Nonempty alt overrides an option description, including disabled aria | Explained; demo supplies a specific description when the installed API has alt |
| Empty alt behaves as None and is logged | Guide discourages empty alt for this chart API |
| Only JSON-compatible options; JavaScript callbacks unsupported | No callbacks in native examples; linter catches source/JsCode misuse |
| Map/geo, custom, GL, and separately loaded extensions unavailable | Native examples exclude these; external examples identify prerequisites and fail native compatibility checks |
| In-chart controls belong in the option | dataZoom/legend guidance and examples; toolbox placement avoids the hover toolbar |
| ECharts labels do not parse Streamlit Markdown | Guide directs formatted app copy to adjacent Streamlit elements |

## Coverage and limits

All 23 core ECharts series types are documented. Twenty-one have a
native-compatible setup in the example collection. `map` and `custom` are
documented through external examples, rather than advertised as supported in
native Streamlit. Geographic variants of otherwise supported types remain
unsupported. `lines` explicitly uses Cartesian coordinates to avoid its geo
default. Chord requires an ECharts 6 host.

JavaScript source inside a JSON string is not converted to a function. The linter
flags this misuse even when the host can parse the JSON. Some ECharts properties
accept templates; callback-only properties still require another approach.

The Python linter validates selected contracts and simple option overrides. It
does not execute arbitrary transforms, register modules, or validate every
ECharts property. The native integration checks use the pinned Streamlit version,
and browser checks exercise the shipped examples. See [VALIDATION.md](../VALIDATION.md)
for the actual run results.

## Streamlit 1.64

Native ECharts started in 1.64. The portable demo checks the installed signature
and omits `alt` when it is unavailable. For app code targeting 1.64, put the
description in `aria.label.description`. The primary regression baseline remains
1.65.0; do not assume untested future versions share the same behavior.
