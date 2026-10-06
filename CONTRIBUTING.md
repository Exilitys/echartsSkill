# Contributing

Keep this repository a portable Agent Skill. The instructions should work without
an agent-specific plugin, and the optional Python validator should remain usable
without third-party dependencies. Keep optional Codex metadata in `agents/`.

## Development setup

Use Python 3.10 or later. From the repository root:

```bash
python -m venv .venv
```

Activate the environment using your shell's normal command, then install the
versioned validation dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

These dependencies are for development and native integration tests. They are
not required to install the skill or run its JSON validator.

## Checks

```bash
python -m ruff check .
python -m ruff format --check .
python -m unittest discover -s tests -t .
python scripts/validate_option.py examples/native --target streamlit
python scripts/validate_option.py examples/external --target echarts
python scripts/package_skill.py --output dist/echarts-json.zip
```

Integration tests are skipped if Streamlit is not installed. With
`requirements-dev.txt`, they verify the documented native input types, serializing
all native examples and rejecting the external families. The repository checks
also validate portable metadata, relative links, example inventory, packaging,
and exclusions of development caches.

Apply formatting with `python -m ruff format .` and inspect the resulting diff.

## Browser checks

Install the additional browser dependency and browser runtime:

```bash
python -m pip install -r requirements-browser.txt
python -m playwright install chromium
python tests/browser_smoke.py
```

On Linux CI, use `python -m playwright install --with-deps chromium`. If Chromium
is already installed, pass its executable path with `--executable`. The script
starts a temporary local Streamlit server, checks every native example with both
renderers and both theme choices, and stops the server when finished. It reports
errors, not just whether the server started. It does not render external charts.

## Adding or updating examples

1. Select the correct core series and coordinate/data contract from the catalog.
2. Add a complete strict JSON option to `examples/native/` or `examples/external/`.
3. Add an entry to `examples/index.json`; identify any external prerequisites.
4. Include stable series IDs, informative labels/units, and an accessible
   description. Use small illustrative data without JavaScript callbacks.
5. Link the example from the relevant guide and catalog, then run the checks.

Do not silently make an external feature look native-compatible. Check the
installed Streamlit/ECharts versions when changing a compatibility claim. Keep
source links versioned where possible, and update the validation record with
the checks actually performed.

## Versioning and packaging

The skill version lives in `SKILL.md` under `metadata.version`. Describe material
changes in `CHANGELOG.md`. `scripts/package_skill.py` creates a ZIP with an
`echarts-json/` top-level directory and excludes `.git`, environments, caches,
dependency directories, and generated output.

Before a push, check `git diff --check`. Do not commit virtual environments,
browser downloads, `dist/`, installer lock files from temporary tests, or test
reports. GitHub Actions runs the repository checks and a native browser smoke test.
