# Package validation

Checked on 2026-10-06 with Python 3.12.14.

## Checks performed

- All 37 native option files pass strict JSON parsing, data-contract checks, and
  native Streamlit compatibility lint with no errors or warnings.
- All five external option files pass the external-target lint. Each emits an
  expected warning for its map, renderer, or extension prerequisite.
- All five external examples are rejected when the target is native Streamlit.
- All 26 regression tests pass. They cover malformed JSON and duplicate keys,
  nonfinite numbers, unsupported callbacks, axis/category alignment, boxplot and
  candlestick contracts, radar and heatmap dimensions, missing link endpoints,
  sankey cycles, default geographic lines, datasets, time ordering, hierarchy
  shape, v5 chord incompatibility, nested unsupported features, and valid partial
  timeline/media overrides.
- The example index covers every one of the 23 core series types, including
  external examples for map and custom.
- Markdown file links, skill frontmatter, agent metadata, Python syntax, example
  index paths/type lists, unique series IDs, and toy map-region matching pass.

## Reproduce

Run from this skill's folder:

```bash
python scripts/validate_option.py examples/native --target streamlit
python scripts/validate_option.py examples/external --target echarts
python -m unittest discover -s scripts -p 'test_*.py'
```

## Limits

The validator is a focused linter, not the official ECharts schema. It does not
execute transforms, load extensions, or simulate every ECharts option merge.
The demo was checked for Python syntax. Streamlit and ECharts were not installed
in the validation workspace, so neither a live Streamlit app nor browser chart
rendering was tested. To inspect rendering in your own environment, install
`streamlit>=1.64` and run `streamlit run scripts/demo_app.py`.

The documented API snapshot was verified against official Streamlit documentation,
the versioned native implementation, and Apache ECharts documentation/source.
See [sources](references/sources.md).
