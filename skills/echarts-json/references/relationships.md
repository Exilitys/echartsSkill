# Relationships and special coordinate systems

## Network (`graph`)

Define nodes in `data`, preferably with unique string `id` and readable `name`.
Define links with `source` and `target` matching IDs (or the supported name/index
form). Use one consistent reference scheme.

- `layout:"force"`: configure `force.repulsion`, `edgeLength`, and optionally
  `gravity`; good for exploratory networks.
- `layout:"circular"`: arrange nodes around a circle.
- `layout:"none"`: provide explicit node `x`/`y` positions.
- `roam:true` supports pan/zoom. `draggable:true` supports dragging where the
  chosen layout allows it. These are in-chart interactions, not Python events.
- Use `edgeSymbol:["none","arrow"]` for direction, `lineStyle` for links,
  `label.show`, and `emphasis.focus:"adjacency"` for readable neighborhoods.
- Optional `categories` and node category indexes organize the legend. Degree,
  community, centrality, and conditional symbol sizes must be precomputed.

Weighted link values do not make a graph a conserved flow chart. Geo-based graph
coordinates need map registration and are unavailable in native Streamlit.

Example: [graph](../examples/native/graph.json).

## Flow (`sankey`)

Define unique named nodes in `data` and links
`[{"source":"A","target":"B","value":10}]`. Every endpoint must exist and
weights must be nonnegative. The graph must be **acyclic**. Use graph or chord
for cycles; do not remove genuine links silently to force a sankey layout.

Set placement margins, `nodeWidth`, `nodeGap`, `orient:"horizontal"` or
`"vertical"`, and `nodeAlign:"justify"`, `"left"`, or `"right"` as appropriate.
`lineStyle.color:"source"` visually tracks origin; modest opacity prevents dense
links from overwhelming nodes. Label units and explain any imbalance if the
data purports to conserve a quantity.

Example: [sankey](../examples/native/sankey.json).

## Circular relationships (`chord`, ECharts 6+)

Use nodes in `data` and weighted `links` with the graph-like endpoint contract.
Set `radius:[inner,outer]`, `center`, and `padAngle` to create readable node arcs.
`lineStyle.color:"source"`, opacity, `label.position:"outside"`, and
`emphasis.focus:"adjacency"` help trace links.

Chord accepts cyclic relationships. Preserve whether each link is directed,
undirected, or represents a bilateral total; do not accidentally count an
undirected relation twice. Distinguish node totals from link weights.
This is a core v6 series, not a custom series, but a v5 renderer cannot render it.

Example: [chord](../examples/native/chord.json).

## Routes and paths (`lines`)

Each item is `{"coords":[[x1,y1],[x2,y2]],"value":10}`. This differs from a
`line` series, which connects observations in a data sequence.

**Set `coordinateSystem:"cartesian2d"` explicitly for native Streamlit**, and
provide value axes. ECharts defaults `lines` to `geo`, which native rejects.
Other coordinate systems require their corresponding verified setup.

Use `lineStyle.curveness` for two-point arcs, `symbol:["none","arrow"]` for
direction, and optional `effect` for animated movement. `polyline:true` permits
more than two points per route; curveness, labels, and some animation capabilities
do not apply in the same way to polylines. Avoid needless continuous animation.

Example: [Cartesian lines](../examples/native/lines.json).

## Parallel coordinates (`parallel`)

Define `parallel` for placement and `parallelAxis` entries with zero-based `dim`
indexes. Each row in `series.data` is a vector in that same dimension order:

```json
{
  "parallel": {"left":60,"right":40,"top":60,"bottom":40},
  "parallelAxis": [{"dim":0,"name":"Speed"},{"dim":1,"name":"Cost"}],
  "series": [{"type":"parallel","data":[[80,40],[60,70]]}]
}
```

Axes can be value, category, or other supported axis types; category axes need
`data`. Specify comparable bounds and units, and reduce line opacity for many
rows. Brush/axis interactions happen in the chart; they do not return Python
selection data through the native API.

Example: [parallel](../examples/native/parallel.json).

## Stream composition (`themeRiver`)

Define `singleAxis:{"type":"time",...}` and triples
`[timestamp,nonnegativeValue,seriesName]`. Sort by time and keep names consistent.
Use the same temporal sampling across streams, and precompute any resampling.
When an absent observation truly means zero, fill it explicitly; otherwise
preserve and explain missingness.

Set a readable single-axis placement and use a legend for the stream names.
The floating streamgraph baseline makes precise values harder to compare; use
stacked area if a fixed zero baseline is needed.

Example: [theme river](../examples/native/theme_river.json).

## Calendar heatmap

Calendar is a coordinate component, not a series. Define a `calendar.range`
(year, month, or start/end dates), placement, `cellSize`, weekday labels, and
`firstDay`. Use `type:"heatmap"`, `coordinateSystem:"calendar"`, optional
`calendarIndex`, and `["YYYY-MM-DD",value]` observations. `visualMap.dimension`
is **1**, because the date is dimension 0. Match dates to the configured range.

For multiple calendars, use an array of components and bind series indexes
explicitly. A missing day need not be assigned zero. Reserve room for month/day
labels and a color scale.

Example: [calendar heatmap](../examples/native/calendar_heatmap.json).

## Matrix (ECharts 6+)

Matrix is a table-like coordinate component, not `type:"matrix"`. Its `x` and
`y` configuration define columns and rows, including header data. Compatible
series/components can be positioned within cells using their supported matrix
coordinate properties. A matrix can host small multiples and annotations; it
does not replace a normal Cartesian heatmap automatically.

Check the version-specific matrix option reference and coordinate compatibility
table before generating a matrix-based option. Verify the chosen series supports
it and how the series maps cell coordinates. Do not assume that every Cartesian
series can change `coordinateSystem` to `matrix` without further setup. Prefer a
Cartesian heatmap when the user simply asks for a two-dimensional value grid.
