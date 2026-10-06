# Sources and version snapshot

Checked on **2026-10-06**. This package contains original setup guidance and small
illustrative configurations; it does not bundle or replace the upstream manuals.
Recheck APIs when the host version differs or an unfamiliar option is required.

## Streamlit

- [Native ECharts API documentation](https://docs.streamlit.io/develop/api-reference/charts/st.echarts_chart)
  — input types, parameters, JavaScript/map/custom/GL restrictions, and examples.
- [Streamlit releases](https://github.com/streamlit/streamlit/releases/tag/1.64.0)
  — native `st.echarts_chart` introduced in 1.64.0.
- [Streamlit 1.65.0 native implementation](https://github.com/streamlit/streamlit/blob/1.65.0/lib/streamlit/elements/echarts_chart.py)
  — strict serialization, unsupported extensions, nested variant checks, and `alt`.
- [Streamlit 1.65.0 frontend dependencies](https://github.com/streamlit/streamlit/blob/1.65.0/frontend/lib/package.json)
  — core ECharts dependency `^6.1.0`.
- [Third-party streamlit-echarts](https://github.com/andfanilo/streamlit-echarts)
  — separate component and API; confirm against the installed release.

## Apache ECharts

- [Option reference](https://echarts.apache.org/en/option.html)
  — all series, component, and property contracts. Deep-link with fragments such
  as `#series-candlestick`, `#series-chord`, `#dataset`, or `#matrix`.
- [Official examples](https://echarts.apache.org/examples/en/index.html)
  — visual reference; examples containing JavaScript must be adapted for JSON.
- [Handbook](https://echarts.apache.org/handbook/en/get-started/)
  — concepts and setup guides.
- [ECharts 6 features](https://echarts.apache.org/handbook/en/basics/release-note/v6-feature/)
  — chord, matrix, custom renderer registration, and additional v6 features.
- [Custom series guide](https://echarts.apache.org/handbook/en/how-to/custom-series/)
  — callbacks and named registered custom-series setup.
- [Machine-readable documentation index](https://echarts.apache.org/en/llms.txt)
  — links to series/component Markdown. If a listed Markdown URL is unavailable,
  use the option site, the handbook, or the authoritative source repositories;
  do not infer properties from an inaccessible page.
- [ECharts 6.1.0 source](https://github.com/apache/echarts/tree/6.1.0/src)
  — exact types and defaults. In particular, `chart/chord/ChordSeries.ts` defines
  chord node/link and radius options; `chart/lines/LinesSeries.ts` shows that
  lines defaults to the geographic coordinate system.
- [ECharts documentation source](https://github.com/apache/echarts-doc/tree/master/en/option)
  — readable option reference source when the site requires JavaScript.

## Extensions

- [Official custom-series packages](https://github.com/apache/echarts-custom-series)
- [ECharts GL](https://github.com/ecomfe/echarts-gl)
- [Word cloud](https://github.com/ecomfe/echarts-wordcloud)
- [Liquid fill](https://github.com/ecomfe/echarts-liquidfill)
- [Statistical transforms](https://github.com/ecomfe/echarts-stat)

## Agent packaging and installation

- [Agent Skills specification](https://agentskills.io/specification)
  — portable `SKILL.md` frontmatter, resources, and progressive disclosure.
- [Skills CLI](https://github.com/vercel-labs/skills)
  — repository discovery, agent selection, copy installation, and update/removal.
- [Codex skills](https://developers.openai.com/codex/skills/)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Cursor skills](https://cursor.com/docs/skills)
- [OpenCode skills](https://opencode.ai/docs/skills/)
- [Gemini CLI skills](https://geminicli.com/docs/cli/skills/)
- [GitHub Copilot skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
- [Windsurf / Devin Desktop Cascade skills](https://docs.devin.ai/desktop/cascade/skills)

The [installation guide](../docs/installation.md) records the current documented
locations. CLI target IDs and native discovery paths can differ across versions.

Core ECharts support is distinct from support in the selected Streamlit host.
Verify both the chart property and the host's ability to load its prerequisites.
