# Changelog

## 1.2.0 — 2026-10-07

- Moved all installable resources into `skills/echarts-json/`; repository tests,
  validation reports, development configuration, and packaging tools stay outside.
- Changed ZIP packaging to include only the skill folder and its license.
- Updated discovery, manual installation, links, test imports, and CI paths.
- Kept the skills CLI installation command unchanged and added migration guidance
  for installations that cloned the whole repository into an agent skill directory.

## 1.1.0 — 2026-10-06

- Rechecked the native integration against Streamlit 1.65 documentation and
  versioned source, including accessibility, cursor, sizing, and `alt` behavior.
- Added portable Agent Skills metadata and installation instructions for Codex,
  Claude Code, Cursor, OpenCode, Gemini CLI, GitHub Copilot, and Windsurf.
- Reworked the README with setup, invocation, JSON integration, compatibility,
  examples, validation, and repository navigation.
- Added a portable ZIP builder, repository checks, Streamlit integration tests,
  browser checks, formatting configuration, and continuous validation.
- Moved regression tests into `tests/`; added contribution guidance, an MIT
  license, and development/cache exclusions.

## 1.0.0 — 2026-10-06

- Created the ECharts JSON skill, core-series catalog, and setup references.
- Added 37 native-compatible JSON examples and five external-runtime examples.
- Added a standard-library validator and native Streamlit example browser.
- Published the initial repository to `Exilitys/echartsSkill`.
