# Maps, custom renderers, and extensions

These configurations describe other ECharts hosts. Native `st.echarts_chart`
cannot render them. A valid JSON option alone does not load or register assets,
callbacks, maps, extensions, or custom transforms.

## Map and geographic charts

A map requires the host to register GeoJSON or supported SVG before `setOption`.
The option's `map` name must exactly match the registration name. Geographic
scatter, effect scatter, graph, lines, and heatmap can also require `geo` and its
registered map. Longitude/latitude points use **`[longitude,latitude,value]`**;
do not swap longitude and latitude.

For a choropleth:

1. Obtain a permitted geographic asset and inspect its region-name property.
2. Register it under a name such as `sample-regions` in a host that supports
   map registration.
3. Use `type:"map", map:"sample-regions"`, matching named region values, and
   a value-based `visualMap`.
4. Check unmatched names, coordinate projection, missing regions, and units.

The bundled [map option](../examples/external/map.json) matches the synthetic
[GeoJSON asset](../examples/assets/sample-regions.geojson). These are toy regions,
not real geographic boundaries. In a browser host the separate setup is:

```javascript
echarts.registerMap("sample-regions", geojson);
chart.setOption(option);
```

Do not put `registerMap` inside JSON, invent `maps=` for native Streamlit, or
claim that a geo chart is supported just because its series type is `scatter`.
For a native-only request, suggest ranked regional bars or a nongeographic grid;
use a geographic renderer only with the user's established integration choice.

## Custom series

`type:"custom"` usually needs a JavaScript `renderItem(params,api)` returning
graphic elements. That function cannot be represented as an executable strict
JSON value. ECharts 6 also allows registered renderers named by a string, but
the renderer still has to be installed and registered by the host. Native
Streamlit rejects custom series in either form.

The [custom range-bar example](../examples/external/custom_bar_range.json) uses
`renderItem:"barRange"`, `encode:{"x":0,"y":[1,2]}`, and data `[categoryIndex,
low,high]`. It requires the official `@echarts-x/custom-bar-range` package and
registration (for a plain browser host, its `bar-range.auto.js` bundle). This
example is a JSON option for a prepared external runtime, not a self-contained
native Streamlit chart.

Other official/custom packages include violin, contour, beeswarm, stage,
range-line, and range-bar. Follow each package's data/encode/itemPayload contract;
there is no universal `type:"violin"` or `type:"gantt"` in core ECharts. For native
Streamlit, consider boxplots, ordinary lines/bars, or precomputed approximations
when they satisfy the intended question.

## ECharts GL

GL is a separate WebGL extension and must be loaded into the host. Verify its
compatibility with the host's exact ECharts version; do not assume v6 support
from a chart name. Native Streamlit bundles core ECharts only.

| GL chart/component | Required setup and data |
| --- | --- |
| `bar3D` | `grid3D` and x/y/z axes; `[x,y,z]` values, often category x/y and value z |
| `scatter3D` | `grid3D` and value x/y/z axes; point triples |
| `line3D` | `grid3D` axes and an ordered trajectory of point triples |
| `lines3D` | A supported 3D coordinate system; route items with `coords` triples or geo positions according to that coordinate system |
| `surface` | `grid3D`; precomputed `[x,y,z]` mesh samples for JSON-only output; equation callbacks require JavaScript |
| `map3D` | Registered geographic asset, map name, and region values; coordinate/height setup from the extension |
| `polygons3D` | Supported 3D geographic coordinate system and polygon coordinate arrays in the documented format |
| `graphGL` | Graph nodes/links and the extension's graph layout; not ordinary `graph` |
| `scatterGL` | A supported 2D coordinate system with point arrays and the GL module |
| `flowGL` | Vector-field samples with coordinates and velocity components; supported coordinate system and extension-specific options |
| `globe` (component) | Top-level globe, projection/texture configuration, and compatible geographic series; not a core `series.type` |
| `geo3D` (component) | Top-level 3D map coordinate component, registration, and compatible series |
| `grid3D` (component) | 3D Cartesian plot plus `xAxis3D`, `yAxis3D`, and `zAxis3D` |

Some host versions also recognize `linesGL`/other extension types. Confirm their
package/version contract instead of inventing a setup. Native rejects them.
The [bar3D option](../examples/external/bar3d.json) is one minimal external
example; it is not a guarantee that the host has GL installed.

## Other extensions

- **Word cloud** (`wordCloud`, `echarts-wordcloud`): named weighted items,
  `sizeRange`, and layout options; load the extension before setting the option.
  Precompute per-word colors for JSON-only delivery. [Example](../examples/external/wordcloud.json).
- **Liquid fill** (`liquidFill`, `echarts-liquidfill`): values commonly as fractions
  in `[0,1]`, shape/wave options, and meaningful percent labels; requires the
  separate module. [Example](../examples/external/liquid_fill.json).
- **Statistical transforms**: packages such as `echarts-stat` require registration
  before their transform names work. Precompute regression, clustering, bins, or
  summaries in Python for native Streamlit.
- **Map-provider coordinate extensions**: require their plugin, provider setup,
  and sometimes a key. They are not available by naming `bmap`/`mapbox` in a
  native option. Inspect the established external host first.

When an external feature is requested, deliver the correct option plus the exact
runtime prerequisites and keep executable setup separate from JSON.
