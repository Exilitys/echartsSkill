# Circular, hierarchical, and single-measure charts

These charts usually do not use Cartesian axes or a grid. Remove leftover axes
when adapting a Cartesian template. Reserve room for legends and outside labels.

## Pie, donut, and rose (`pie`)

Use named items `[{"name":"A","value":40},{"name":"B","value":60}]`. Pie
values must be meaningful nonnegative parts; a zero total has no meaningful
share. Explain empty/all-zero data and choose an appropriate empty state.

- Pie: a scalar `radius`, e.g. `"65%"`.
- Donut: `radius:["40%","65%"]`, with inner smaller than outer.
- Rose: `roseType:"radius"` or `"area"`; this changes how magnitude is encoded.
- `center:["50%","52%"]` positions the chart; make room for outside labels.
- `tooltip.trigger:"item"` with `formatter:"{b}: {c} ({d}%)"` suits a basic pie.
- `label.formatter:"{b}: {d}%"` exposes shares without JavaScript.
- `avoidLabelOverlap:true` helps, but cannot make dozens of slices readable.
  Use a scroll legend or a better representation for many categories. Group
  categories into "Other" only when the user allows that aggregation.

Do not invent `type:"donut"`, `type:"rose"`, or `type:"area"`.
Examples: [pie](../examples/native/pie.json), [donut](../examples/native/donut.json),
[rose](../examples/native/rose.json).

## Radar (`radar`)

Define `radar.indicator:[{"name":"Speed","max":100}, ...]`. Each data item is
`{"name":"Model A","value":[80,60,...]}` in exactly the same dimension order.
Use comparable scales or explicitly normalized metrics; mixing unrelated units
on an unlabeled scale creates misleading profiles.

Choose `radar.shape:"polygon"` or `"circle"`, `radius`, `center`, and optionally
`splitNumber`. Use `areaStyle` with modest opacity when fill aids comparison.
Add a legend for multiple profiles. Indicator bounds should reflect meaningful
scales rather than clipping observations to fit.

Example: [radar](../examples/native/radar.json).

## Tree (`tree`)

The series has one root inside an array:

```json
{"type":"tree","data":[{"name":"Root","children":[{"name":"Child"}]}]}
```

Use `layout:"orthogonal"` or `"radial"`, and for orthogonal layout choose
`orient:"LR"`, `"RL"`, `"TB"`, or `"BT"`. `initialTreeDepth` controls initial
expansion; `expandAndCollapse:true` supports in-chart expansion. Position parent
labels and `leaves.label` separately so text does not sit on edges.

Tree relationships do not require numerical values. Preserve parent-child
structure rather than flattening it to category/value pairs. Check for invalid
children and unintended duplicated branches. A network with multiple parents
needs a graph, not fabricated tree ownership.

Example: [tree](../examples/native/tree.json).

## Treemap (`treemap`)

Use a forest of nodes with `name`, optional nonnegative `value`, and nested
`children`. Leaf values determine magnitude. Omit parent values to let ECharts
derive totals, or supply totals consistent with the children and intended
semantics. Never add parent and children as unrelated flat observations.

Useful options include `leafDepth`, `levels` for border/label styles,
`upperLabel`, `breadcrumb`, and `roam`. `nodeClick:"zoomToNode"` enables zooming
into branches. Border space and labels need careful sizing on small rectangles;
show details in a tooltip rather than forcing labels into every tiny cell.

Example: [treemap](../examples/native/treemap.json).

## Sunburst (`sunburst`)

Use the same nested magnitude contract as treemap. Set `radius:[0,"75%"]`,
`center`, and `levels` to control ring styles. `nodeClick:"rootToNode"` supports
branch focus. Use `sort:null` to preserve supplied sibling order when it matters.
Label rotation and ring width affect readability; reduce visible label density
for deep trees. Do not include duplicate totals as independent branches.

Example: [sunburst](../examples/native/sunburst.json).

## Funnel (`funnel`)

Use `[{name,value}]` for stage magnitudes. `sort:"descending"` visually orders
by size; `sort:"none"` preserves the process order. Prefer `"none"` when stages
represent a real sequence. Specify min/max in the data's units (a count funnel
is not automatically a 0–100 percentage funnel).

`left`, `top`, `width`, `height`, `gap`, `minSize`, and `maxSize` control placement.
Use item tooltips and readable labels. Conversion rates must be calculated
against an explicitly defined prior-stage or starting-stage denominator; width
alone does not explain that denominator. If stage counts increase, preserve the
truth and explain it rather than silently sorting away the increase.

Example: [funnel](../examples/native/funnel.json).

## Gauge (`gauge`)

Use one or more `[{name,value}]` items with meaningful `min` and `max`. Configure
`startAngle`, `endAngle`, `progress.show`, `axisLine`, `pointer`, `anchor`, and
`detail` as needed. For percent points in `[0,100]`, `detail.formatter:"{value}%"`
is a supported string template. A fraction in `[0,1]` needs different bounds or
preconversion to percent points.

Avoid arbitrary thresholds, colors, or target ranges. Keep the actual out-of-range
value visible instead of silently clipping it. A gauge summarizes status; a line
or bar is usually better for comparisons and change over time.

Example: [gauge](../examples/native/gauge.json).
