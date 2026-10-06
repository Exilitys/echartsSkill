# Chart selection and complete core-series catalog

ECharts 6 has 23 core series types. Type names are case-sensitive. The table
lists the required coordinate or data contract, not every optional property.
Native means compatible with the documented Streamlit 1.64/1.65 integration;
special options can still introduce an unsupported feature.

| Core `type` | Use for | Required setup and data | Native | Complete example |
| --- | --- | --- | --- | --- |
| `line` | Ordered trends, time series | Cartesian axes, or supported polar setup; scalar category values or `[x,y]` | Yes | [line](../examples/native/line.json) |
| `bar` | Category comparisons | Cartesian axes, or polar axes; scalar category values or explicitly encoded dataset | Yes | [bar](../examples/native/bar.json) |
| `pie` | Nonnegative parts of a whole | No axes; `[{name,value}]`, radius and center | Yes | [pie](../examples/native/pie.json) |
| `scatter` | Relationships between measurements | Two value axes; `[[x,y]]` or objects with `value` | Yes | [scatter](../examples/native/scatter.json) |
| `effectScatter` | Emphasized points with ripple effect | Same point contract as scatter; `rippleEffect` | Yes | [effect scatter](../examples/native/effect_scatter.json) |
| `radar` | Profiles across a small set of dimensions | `radar.indicator`; each item's `value` matches indicator order | Yes | [radar](../examples/native/radar.json) |
| `tree` | Parent/child relationships | Nested `children`; a root object inside `series.data` | Yes | [tree](../examples/native/tree.json) |
| `treemap` | Hierarchical part-to-whole area | Nested nodes with nonnegative values; no Cartesian axes | Yes | [treemap](../examples/native/treemap.json) |
| `sunburst` | Hierarchical radial part-to-whole | Nested nodes with nonnegative values; radius and center | Yes | [sunburst](../examples/native/sunburst.json) |
| `boxplot` | Group distributions | Category/value axes; `[low,Q1,median,Q3,high]` per group | Yes | [boxplot](../examples/native/boxplot.json) |
| `candlestick` | OHLC prices | Category/value axes; `[open,close,low,high]` per timestamp | Yes | [candlestick](../examples/native/candlestick.json) |
| `heatmap` | Values in a two-dimensional grid | Category axes and `[xIndex,yIndex,value]`, or calendar; `visualMap` | Yes | [heatmap](../examples/native/heatmap.json) |
| `map` | Regional choropleth | Registered GeoJSON/SVG name, region-name/value pairs | No | [external map](../examples/external/map.json) |
| `parallel` | Multivariate rows | `parallel`, `parallelAxis` dimensions; one ordered value vector per row | Yes | [parallel](../examples/native/parallel.json) |
| `lines` | Routes and paths | Explicit coordinate system; each item has `coords:[[x,y],[x,y]]` | Yes, without geo | [Cartesian lines](../examples/native/lines.json) |
| `graph` | Networks and relationships | Nodes, links, and `force`, `circular`, or explicit-position layout | Yes, without geo | [graph](../examples/native/graph.json) |
| `sankey` | Directed quantitative flows | Unique named nodes and nonnegative weighted links; acyclic | Yes | [sankey](../examples/native/sankey.json) |
| `funnel` | Stage counts or decreasing conversion | `[{name,value}]`; meaningful min/max; no axes | Yes | [funnel](../examples/native/funnel.json) |
| `gauge` | A value relative to known bounds | `[{name,value}]`, min/max, detail template; no axes | Yes | [gauge](../examples/native/gauge.json) |
| `pictorialBar` | Category values encoded by symbols | Cartesian axes, category/value data, symbol configuration | Yes | [pictorial bar](../examples/native/pictorial_bar.json) |
| `themeRiver` | Changing composition over time | `singleAxis` of type `time`; `[time,value,seriesName]` triples | Yes | [theme river](../examples/native/theme_river.json) |
| `custom` | Bespoke geometry or specialized plots | JavaScript `renderItem`, or an externally registered named renderer | No | [external range bar](../examples/external/custom_bar_range.json) |
| `chord` | Weighted relationships around a circle | Named nodes and weighted links; ECharts 6+ | Yes on v6 host | [chord](../examples/native/chord.json) |

## Common names that are configurations, not series types

| Requested chart | Actual setup | Example |
| --- | --- | --- |
| Area | `line` with `areaStyle:{}` | [area](../examples/native/area.json) |
| Stacked area | Multiple area lines with the same `stack` | [stacked area](../examples/native/stacked_area.json) |
| Step chart | `line.step:"start"`, `"middle"`, or `"end"` | [step line](../examples/native/step_line.json) |
| Time series | `line`, `xAxis.type:"time"`, sorted `[time,value]` | [time line](../examples/native/time_line.json) |
| Horizontal bar | `xAxis.type:"value"`, `yAxis.type:"category"` | [horizontal bar](../examples/native/horizontal_bar.json) |
| Grouped bar | Multiple bar series without a shared `stack` | [grouped bar](../examples/native/grouped_bar.json) |
| Stacked bar | Multiple bar series sharing `stack` and category order | [stacked bar](../examples/native/stacked_bar.json) |
| 100% stacked | Precompute each category's shares; shared stack and percent axis | Adapt stacked bar; define zero-total behavior |
| Histogram | Precompute bins/counts; adjoining `bar` categories | [histogram](../examples/native/histogram.json) |
| Waterfall | Precompute cumulative offsets; transparent helper bars and changes | [waterfall](../examples/native/waterfall.json) |
| Donut | `pie.radius:[inner,outer]` | [donut](../examples/native/donut.json) |
| Rose / Nightingale | `pie.roseType:"radius"` or `"area"` | [rose](../examples/native/rose.json) |
| Bubble | `scatter`; precompute per-item `symbolSize` | [bubble](../examples/native/bubble.json) |
| Calendar heatmap | `heatmap.coordinateSystem:"calendar"`; date/value pairs | [calendar heatmap](../examples/native/calendar_heatmap.json) |
| Mixed / dual axis | Different series types sharing x, with explicit `yAxisIndex` | [mixed bar/line](../examples/native/mixed_bar_line.json) |
| Polar bars | `bar.coordinateSystem:"polar"`; `polar`, angle/radius axes | [polar bar](../examples/native/polar_bar.json) |
| Tabular dataset chart | `dataset.dimensions`, source records, explicit `encode` | [dataset bar](../examples/native/dataset_bar.json) |

Violin, contour, beeswarm, range-bar, range-line, and Gantt/X-range often need a
custom renderer or preprocessing. ECharts 6 offers registered custom-series
packages, but these are unavailable in native Streamlit. Word cloud and liquid
fill are extensions. 3D and WebGL charts require ECharts GL. See
[extensions](extensions.md) for their setup contracts.

## Pick by analytical intent

- Compare categories: bar; use horizontal bars for long names.
- Follow ordered change: line; use time axes for irregular time intervals.
- Show a small part-to-whole split: pie/donut; use bars for close comparisons.
- Compare distributions: boxplot or a precomputed histogram.
- Explore correlation: scatter, or bubble for a third quantitative dimension.
- Show many matrix cells: heatmap with a clearly labeled color scale.
- Explain hierarchy: tree for relationships, treemap/sunburst for magnitude.
- Show flows: sankey for acyclic flow, chord for circular relationships, graph
  for structure without a conservation claim.
- Summarize one bounded measurement: gauge; retain its units and bounds.

Avoid selecting a decorative encoding at the expense of reading values accurately.
