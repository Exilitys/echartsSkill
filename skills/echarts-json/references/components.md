# Shared components, data, and presentation

## Dataset and encode

Use `series.data` for a small, direct chart; use `dataset` for shared table data.
Prefer explicit dimensions and encode mappings to avoid inference errors:

```json
{
  "dataset": {
    "dimensions": ["month","revenue","cost"],
    "source": [
      {"month":"Jan","revenue":120,"cost":80},
      {"month":"Feb","revenue":150,"cost":90}
    ]
  },
  "xAxis": {"type":"category"},
  "yAxis": {"type":"value","name":"USD"},
  "legend": {},
  "tooltip": {"trigger":"axis"},
  "series": [
    {"id":"revenue","name":"Revenue","type":"bar",
     "encode":{"x":"month","y":"revenue","tooltip":["revenue"]}},
    {"id":"cost","name":"Cost","type":"bar",
     "encode":{"x":"month","y":"cost","tooltip":["cost"]}}
  ]
}
```

For two-dimensional arrays, set `sourceHeader:true` if the first row is a header,
or `false` when all rows are observations. Match dimensions to table width.
`seriesLayoutBy:"column"` is the usual orientation; a row-oriented table needs
different mappings. With multiple datasets, set `datasetIndex` or `datasetId`.
Preserve dimension types with named dimension objects when needed.

Do not supply direct data and expect it to merge automatically with an unrelated
dataset. Do not add Cartesian `encode` to nested trees or graph link structures.

Core ECharts provides filter/sort transforms in supported builds. Use only
verified registered transforms. Statistical/regression/clustering transforms
from external packages require registration and are not available simply by
putting their names in native JSON. Precomputing in Python is the dependable
default. The linter does not execute transforms.

Complete example: [dataset bar](../examples/native/dataset_bar.json).

## Axes and grids

| Axis type | Use | Important checks |
| --- | --- | --- |
| `category` | Named groups, trading sessions, regular discrete periods | Category order agrees with data |
| `value` | Numeric magnitudes | Units and baseline are appropriate |
| `time` | Actual elapsed time | Sorted timestamps and timezone interpretation |
| `log` | Positive values spanning orders of magnitude | No zero/negative plotted values; label the log scale |

Use `name`, `nameLocation`, `nameGap`, `axisLabel`, `splitLine`, and `axisPointer`
to clarify axes. `axisLabel.formatter:"{value} kg"` appends a unit. Time-axis
formatters use date tokens such as `{yyyy}-{MM}-{dd}` where supported; these are
not interchangeable with tooltip template tokens. Callback-only formatting needs
preprocessing or another renderer, not a JavaScript string.

Use `scale:true` deliberately for prices/scatter. Keep a zero baseline for bars.
For percent points use 0–100; for fractions use 0–1 with correct labels. Axis
`min`/`max` can be numbers or supported keywords; never emit a function callback.
Prefer rotation or fewer labels to hiding meaningful categories.

Multiple grids require matching grid indexes, axis indexes, and zoom targets.
Maintain room for title, top legend, bottom zoom, and labels. ECharts 6 introduced
additional layout/axis features; verify their names against the installed version.

## Tooltips and formatters

- `trigger:"axis"`: aligned line/bar observations; optional cross or shadow
  `axisPointer`.
- `trigger:"item"`: independent scatter points, pie slices, hierarchy nodes,
  and network items.
- Use `confine:true` when a tooltip could overflow the container.
- Basic tooltip tokens: `{a}` series name, `{b}` item/category name, `{c}` value;
  pie additionally provides `{d}` percent. Their meanings vary by series.
- Axis tooltip templates can address series indexes (`{a0}`, `{c0}`), but only
  when the chart's series order and tooltip shape are known.
- `encode.tooltip` controls dimensions for dataset-backed charts. Prefer a
  default tooltip for multivalue observations until a custom template is tested.
- `tooltip.valueFormatter` is callback-only. Native cannot accept a JS string
  there. Do not assume Python f-strings dynamically format client-side values.

## Legends and color

Give each comparable series a unique name. Legends generally use series names;
pie legends use slice names, and graph category legends require categories.
Avoid ambiguous duplicate names. A long legend can use `type:"scroll"`.
Place the legend above the plot when a slider occupies the bottom.

Use `color` for an explicit categorical palette. Use `itemStyle` for item fill,
`lineStyle` for lines, `areaStyle` for fills, and `emphasis` for hover states. Keep
meaningful categories consistently colored across charts. Precompute
conditional item styles; callbacks are unavailable in native Streamlit.

Let the default Streamlit theme supply general fonts/colors. When exact styling
is requested, provide appropriate contrast and pass `theme=None` on the wrapper.
A serializable gradient object is possible without `new echarts.graphic...`:

```json
{"type":"linear","x":0,"y":0,"x2":0,"y2":1,
 "colorStops":[{"offset":0,"color":"#3B82F6"},
               {"offset":1,"color":"#DBEAFE"}]}
```

Use that object in a color-valued property; it is not a complete option itself.
Avoid HTML/Markdown assumptions in labels. ECharts rich-text labels use its own
`rich` styles and `{styleName|text}` syntax.

## Visual mapping

`visualMap` maps a quantitative or categorical dimension to color, size, or
opacity. Choose `type:"continuous"` for a numeric gradient or `"piecewise"` for
bins/categories. Set `seriesIndex` when only selected series should be mapped.
Explicitly set `dimension` when observations contain coordinates plus values:
Cartesian heatmap value is dimension 2; calendar heatmap value is dimension 1.
Use observed or meaningful domain bounds and an explained legend. Do not apply a
numeric mapping to the timestamp/category dimension accidentally.

## Zoom, toolbox, and brush

For a dense time/category x-axis:

```json
[{"type":"inside","xAxisIndex":0,"start":0,"end":100},
 {"type":"slider","xAxisIndex":0,"bottom":8,"height":20}]
```

Place this array in `dataZoom` and reserve about 72px below the grid. Use
`yAxisIndex`, `radiusAxisIndex`, or `angleAxisIndex` for different axes as supported.
`filterMode` affects whether out-of-window observations are removed or left
empty; choose it based on the comparison the user needs.

A useful toolbox can expose `restore` and `dataZoom`. `magicType` applies only
to compatible chart types such as line/bar. Avoid duplicate image-download
controls beside Streamlit's hover toolbar. Position toolbox controls separately
from the legend. A `brush` supports in-chart visual selection; native exposes no
Python selection event result.

## Markers and annotations

Use `markLine` for a known threshold, `markPoint` for a specified observation or
supported min/max, and `markArea` for a highlighted interval. Bind coordinates
to actual axis values and label their meaning. Avoid invented thresholds or
claims. These are series properties, not extra chart types.

```json
{"markLine":{"data":[{"yAxis":100,"name":"Target"}]}}
```

Merge into the intended series only if a target of 100 is supplied or justified.

## Timeline and responsive media

Timeline uses `baseOption` plus `options`:

```json
{
  "baseOption": {
    "timeline":{"axisType":"category","data":["2025","2026"]},
    "xAxis":{"type":"category","data":["A","B"]},
    "yAxis":{"type":"value"},
    "series":[{"id":"sales","type":"bar"}]
  },
  "options":[{"series":[{"id":"sales","data":[10,20]}]},
             {"series":[{"id":"sales","data":[15,25]}]}]
}
```

Overrides can omit a series type when they update an existing series. Preserve
IDs or indexes and timeline length. Responsive `media` entries use `query` and
`option`, e.g. a `maxWidth` condition and a compact legend/grid override.
Validate all nested option variants for unsupported native features. The focused
linter inherits simple series/component overrides but cannot prove every ECharts
merge behavior; test complex timelines/media in the actual host.

## Accessibility, responsiveness, and scale

Use `aria:{"enabled":true,"label":{"description":"..."}}` with a meaningful
description. Native Streamlit 1.65 can also set it via `alt`. Use labels, patterns,
or position alongside color; `aria.decal.show:true` can help distinguish series.
Let the container stretch and avoid fixed pixel chart widths where possible.

For large data, prefer canvas, fewer labels/symbols, an appropriate zoom window,
and supported `large`/`progressive` options on the selected series. Disable
unnecessary animation with `animation:false`. Sampling, binning, and aggregation
must preserve or disclose the analytical meaning; performance flags cannot
make arbitrary million-point JSON payloads cheap to send.
