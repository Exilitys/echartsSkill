# Cartesian and polar chart setup

## Shared Cartesian contract

Use `xAxis`, `yAxis`, and an optional `grid` for plot placement. A vertical bar
or ordinary ordered line has a category x-axis and a value y-axis. Quantitative
scatter has two value axes. Irregular time series use a time x-axis and explicit
`[time,value]` observations; do not space irregular timestamps as categories.

Start with `grid:{"left":16,"right":24,"top":60,"bottom":48,
"containLabel":true}`. Reserve more space when a legend or zoom slider is added.
For multiple grids, bind each axis with `gridIndex`, and each series with the
appropriate `xAxisIndex`/`yAxisIndex`. Indexes are zero-based.

Use scalar `series.data` only when values align with the category axis in order.
For tables, use explicit dataset dimensions and encode mappings. Remove unused
axes when converting a Cartesian option to a pie or other standalone chart.

## Line, area, step, and time (`line`)

- Minimum: axes, `type:"line"`, data; axis tooltip for aligned series.
- Area: add `areaStyle:{"opacity":0.25}`. Stacked areas must use the same `stack`
  identifier and identical category/time alignment.
- Step: choose `step:"start"`, `"middle"`, or `"end"` based on when changes occur.
- Time: set `xAxis.type:"time"`, sort actual timestamps, and use UTC timestamps
  with `useUTC:true` when the application requires UTC display.
- `smooth:true` visually interpolates; use it only if appropriate. It can imply
  intermediate values absent from the observations. Default to a straight line.
- Preserve gaps with `null` and `connectNulls:false`. `showSymbol:false` reduces
  clutter on dense series. `sampling:"lttb"` can reduce dense line rendering;
  explain aggregation or sampling when it changes interpretation.

Examples: [line](../examples/native/line.json), [area](../examples/native/area.json),
[stacked area](../examples/native/stacked_area.json),
[step](../examples/native/step_line.json), [time](../examples/native/time_line.json).

## Bar, stacks, histograms, and waterfalls (`bar`)

- Vertical: category x/value y. Horizontal: value x/category y; `yAxis.inverse:
  true` puts the first category at the top.
- Grouped: separate series with matching categories and no shared stack.
- Stacked: all parts use the same `stack`. Negative parts generally stack
  separately from positive parts; do not treat this as a cumulative waterfall.
- Percent stack: compute each part divided by its category total before building
  JSON. Set the axis to `[0,100]` for percent values, and use a percent formatter.
  Define what a zero denominator means rather than emitting infinity.
- Use a zero baseline for bar magnitude. Use `barMaxWidth` for a readable maximum;
  `barGap` controls within-group spacing, `barCategoryGap` spacing between groups.
- Histogram: calculate bin edges/counts in Python, label intervals consistently,
  and use `barCategoryGap:"0%"`. Define whether the last bin includes its right
  edge. ECharts has no core `histogram` series or built-in universal binning step.
- Waterfall: calculate each change's start/end and draw transparent offset bars
  plus visible positive/negative bars. Hide helper series from legend and tooltip.
  The bundled example keeps cumulative values nonnegative; crossing zero needs
  careful segment preparation because ordinary positive/negative stacking is
  separate. Do not reuse that helper formula blindly for negative totals.

Examples: [bar](../examples/native/bar.json),
[horizontal](../examples/native/horizontal_bar.json),
[grouped](../examples/native/grouped_bar.json),
[stacked](../examples/native/stacked_bar.json),
[histogram](../examples/native/histogram.json),
[waterfall](../examples/native/waterfall.json).

## Scatter, bubble, and effects (`scatter`, `effectScatter`)

Use two value axes, `tooltip.trigger:"item"`, and points such as `[[10,20],
[15,35]]`. An extra value dimension may drive `visualMap` or tooltip content.
Name both measured dimensions and their units.

For bubbles, assign `symbolSize` numerically on each item:

```json
{"value":[10,20,100],"name":"Group A","symbolSize":24}
```

Precompute diameter proportional to the square root of a nonnegative magnitude
when area encodes that magnitude. Establish a readable minimum/maximum and
explain any clipping. Native cannot execute a `symbolSize` callback string.
For overlapping points, opacity helps; use v6 jitter options only after checking
the exact installed ECharts API.

Effect scatter shares the point contract. Configure `rippleEffect` and use it
sparingly to highlight important observations. Geographic scatter/effects remain
unavailable in native Streamlit.

Examples: [scatter](../examples/native/scatter.json),
[bubble](../examples/native/bubble.json),
[effect scatter](../examples/native/effect_scatter.json).

## Boxplot (`boxplot`)

Each category consumes **`[lowWhisker,Q1,median,Q3,highWhisker]`**. Values must be
nondecreasing. Whiskers are not necessarily the minimum and maximum of the raw
observations: state the chosen convention, such as 1.5 IQR. Precompute quartiles,
whiskers, and outliers in Python, or verify that the host includes the intended
ECharts transform. Represent outliers separately with a scatter series.

Raw observation lists are not boxplot summaries. Match summary count and group
labels; keep category indexes consistent for outliers. Use the default tooltip
unless a tested template exposes the intended summary dimensions.

Example: [boxplot](../examples/native/boxplot.json).

## Candlestick (`candlestick`)

Each timestamp consumes **`[open,close,low,high]`**, not OHLC order. Check that
`low <= min(open,close)` and `high >= max(open,close)`. Use sorted timestamps as
categories when equal trading-session spacing is intentional. `yAxis.scale:true`
allows a price chart to focus on price variation without implying zero-based bar
magnitude. Use `axisPointer.type:"cross"` and optional inside/slider zoom.

Choose rise/fall colors explicitly when the user's locale has a convention:
`itemStyle.color`, `color0`, `borderColor`, and `borderColor0`. Add volume in a
second grid with synchronized x-axis zoom if requested; do not mix volume and
price on a single unlabeled value axis.

Example: [candlestick](../examples/native/candlestick.json).

## Heatmap (`heatmap`)

Cartesian heatmap needs category x/y axes and cells **`[xIndex,yIndex,value]`**.
Indexes refer to the category arrays. Add a `visualMap` with `dimension:2`, a
meaningful min/max, and enough reserved space for its legend. A sequential scale
suits magnitude; a diverging scale with a justified midpoint suits deviations.

Missing cells mean missing data, not zero. Precompute duplicate-cell aggregation
when the data has multiple observations per cell. Do not silently overwrite
duplicates. Native supports Cartesian/calendar heatmaps, not geo heatmaps.

Examples: [heatmap](../examples/native/heatmap.json),
[calendar heatmap](../examples/native/calendar_heatmap.json).

## Pictorial bar (`pictorialBar`)

Use Cartesian category/value axes and a `symbol` such as `rect`, `circle`, or a
verified `path://...` shape. `symbolRepeat:true` repeats symbols; `symbolClip:true`
clips to the observed value. Set an appropriate fixed `symbolBoundingData` for
comparable clipping bounds. `symbolSize`, `symbolMargin`, and the plot height
determine whether repeated symbols remain readable.

Do not let icon count imply whole units when clipping yields fractional icons.
Prefer ordinary bars when precise comparisons matter. External `image://` icons
require a reachable asset; use built-in symbols for self-contained JSON.

Example: [pictorial bar](../examples/native/pictorial_bar.json).

## Mixed charts and polar bars

Mixed charts share a coordinate system, not a new `type`. For a bar plus line,
bind series to the correct y-axis with `yAxisIndex`. Give each axis a distinct unit
and align all category values. Dual-axis charts can suggest correlation through
arbitrary scale choices; use only when the two-unit comparison is useful.

Polar bars need `polar:{}`, `angleAxis`, `radiusAxis`, and each series'
`coordinateSystem:"polar"`. For radial magnitude, use a category angle-axis and
value radius-axis. A value angle-axis and category radius-axis produces a
different angular encoding; configure it intentionally.

Examples: [mixed bar/line](../examples/native/mixed_bar_line.json),
[polar bar](../examples/native/polar_bar.json).
