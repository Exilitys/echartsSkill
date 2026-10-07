# Validation record

Checked on **2026-10-07** with Python **3.12.14**, Streamlit **1.65.0**,
pyecharts **2.1.0**, Playwright **1.63.0**, Chromium **151.0.7922.173**,
and skills CLI **1.7.0**.

## Results

| Check | Result |
| --- | --- |
| Standard-library validator and repository checks, plus pinned native integration tests | **42 tests passed**, no skips with development dependencies installed |
| Native example lint | **37 options passed**, no errors or warnings |
| External example lint | **5 options passed** for an external host, with 5 expected prerequisite warnings |
| Native rejection of external examples | All 5 rejected by both the linter and Streamlit |
| Live Streamlit browser rendering | **148 renders passed**: 37 examples × canvas/SVG × both theme modes (`"streamlit"` and `None`) |
| Live accessibility behavior | **4 cases passed**: default description, explicit alt precedence with disabled aria, disabled aria without alt, and whitespace-only alt |
| Portable metadata, links, inventory, series IDs, synthetic map-region matching | Passed |
| ZIP packaging and extraction | Exactly 57 files from `skills/echarts-json/`, with an `echarts-json/` archive root; repository tooling and generated/private files excluded |
| Skills CLI discovery and copy installation | Skill discovered and installed for all 7 requested agent targets |
| Ruff lint, formatting, and Git whitespace checks | Passed |

The native integration tests exercise dictionary and JSON-string inputs for every
native example, dataframe conversion with ordered dimensions and missing values,
pyecharts/duck-typed input, nested unsupported features, invalid wrapper arguments,
nonserializable values, the documented signature, stable element identity, and
the demo's controls and accessible descriptions.

The browser test runs the actual demo through Streamlit and Chromium. It waits
for each completed configuration, checks chart size, canvas/SVG output, accessible
names, and absence of frontend chart errors, app exceptions, and browser errors.
A test-only wrapper acknowledges reruns; the shipped demo does not include test UI.

The seven installer targets are **Codex, Claude Code, Cursor, OpenCode, Gemini CLI,
GitHub Copilot, and Windsurf**. CLI 1.7.0 creates the shared `.agents/skills`
copy plus the `.claude/skills` and `.windsurf/skills` copies. The bundled skill,
references, examples, and scripts were checked against the installed copies.
The copies contain all 57 skill files and exclude tests, reports, repository docs,
and development configuration. The copied validator and example browser also ran
from outside the repository. Skill-relative Markdown links stay inside the skill
folder, so copying that folder preserves its resources.

On 2026-10-06, a separate Streamlit **1.64.0** environment accepted all 37 native option dictionaries
and ran the demo's chart, renderer, and theme controls. The signature check and
retained `aria.label.description` confirmed the fallback without `alt`. Browser
coverage and the primary regression baseline use **1.65.0**.

## Reproduce

Install [development dependencies](requirements-dev.txt), then run from the
repository root:

```bash
python -m ruff check .
python -m ruff format --check .
python -m unittest discover -s tests -t . -v
python skills/echarts-json/scripts/validate_option.py skills/echarts-json/examples/native --target streamlit
python skills/echarts-json/scripts/validate_option.py skills/echarts-json/examples/external --target echarts
python scripts/package_skill.py --output dist/echarts-json.zip
```

For live browser checks:

```bash
python -m pip install -r requirements-browser.txt
python -m playwright install chromium
python tests/browser_smoke.py --report test-results/browser.json
```

Use `--executable /path/to/chromium` for an existing browser. Linux CI installs
Chromium with `python -m playwright install --with-deps chromium`.

To repeat copy installation without modifying an existing agent setup, make an
empty temporary project directory and run the [installation command](docs/installation.md)
there, using this checkout's absolute path as the source instead of the GitHub
repository name. `npx skills list --json` reports discovered installations.

## Limits

The validator checks selected contracts; it is not the official ECharts schema.
The browser checks detect runtime failures and basic output/accessibility issues;
they are not a pixel comparison or a full audit of tooltips, interactions, visual
layout, or analytical meaning. External charts were not rendered, and no extensions
or map registrations were loaded.

Installer checks verify discovery and resource installation, not model execution
inside each agent. Agent activation, custom directories, and cloud syncing depend
on the host. Versions other than the recorded ones require their own verification.

The documented API snapshot was checked against official documentation and
versioned source. See [compatibility audit](docs/streamlit-compatibility.md),
[contribution guidance](CONTRIBUTING.md), and [sources](skills/echarts-json/references/sources.md).
