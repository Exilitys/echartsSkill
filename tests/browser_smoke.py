"""Render every native example through a real Streamlit app in Chromium.

Install requirements-browser.txt and run `python -m playwright install chromium`.
Use --executable /path/to/chromium to select an existing browser installation.
"""

from __future__ import annotations

import argparse
import json
import re
import socket
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parent.parent


@contextmanager
def serve(app: Path):
    """Own a local test server and terminate only that process on exit."""
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    with tempfile.TemporaryFile(mode="w+") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(app),
                "--server.address=127.0.0.1",
                f"--server.port={port}",
                "--server.headless=true",
                "--browser.gatherUsageStats=false",
                "--server.fileWatcherType=none",
            ],
            cwd=ROOT,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        try:
            deadline = time.monotonic() + 45
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    log.seek(0)
                    raise RuntimeError(f"Streamlit exited early:\n{log.read()}")
                try:
                    with urlopen(f"{url}/_stcore/health", timeout=1) as response:
                        if response.status == 200:
                            break
                except (URLError, TimeoutError):
                    time.sleep(0.1)
            else:
                raise RuntimeError("Streamlit test server did not become healthy")
            yield url
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def select(page, label: str, value: str):
    control = page.get_by_test_id("stSelectbox").filter(has=page.get_by_text(label, exact=True))
    combobox = control.get_by_role("combobox")
    combobox.click()
    # Filter first so a virtualized long list cannot recycle the clicked option.
    combobox.fill(value)
    page.get_by_role("option", name=value, exact=True).click()


@contextmanager
def serve_demo():
    """Run the unchanged demo with a test-only acknowledgement after each rerun."""
    with tempfile.TemporaryDirectory() as temporary:
        app = Path(temporary) / "demo_test_app.py"
        app.write_text(
            "import json, runpy, sys\n"
            "import streamlit as st\n"
            f"sys.path.insert(0, {str(ROOT / 'scripts')!r})\n"
            f"state = runpy.run_path({str(ROOT / 'scripts/demo_app.py')!r})\n"
            "st.text('Browser state: ' + json.dumps([state['selected'], "
            "state['renderer'], state['themed']]))\n",
            encoding="utf-8",
        )
        with serve(app) as url:
            yield url


def wait_for_demo_state(page, selected: str, renderer: str, themed: bool):
    acknowledgement = "Browser state: " + json.dumps([selected, renderer, themed])
    expect(page.get_by_test_id("stText")).to_have_text(acknowledgement, timeout=20_000)


def assert_chart(page, description: str, renderer: str):
    chart = page.get_by_test_id("stEChartsChart")
    expect(chart).to_be_visible(timeout=20_000)
    expect(chart).to_have_attribute("aria-busy", "false", timeout=20_000)
    expect(chart).to_have_attribute("role", "img")
    expect(chart).to_have_attribute("aria-label", description, timeout=20_000)
    expect(chart.locator(renderer).first).to_be_visible(timeout=20_000)
    assert chart.evaluate("element => element.clientWidth > 100 && element.clientHeight > 100")
    expect(page.get_by_test_id("stEChartsChartError")).to_have_count(0)
    expect(page.get_by_test_id("stException")).to_have_count(0)


def check_accessibility(browser, directory: Path):
    """Verify frontend defaults and explicit alt precedence with theme=None."""
    app = directory / "accessibility_app.py"
    app.write_text(
        """
import streamlit as st
mode = st.selectbox("Case", ["defaults", "override", "disabled", "empty"])
option = {
    "xAxis": {"type": "category", "data": ["A", "B"]},
    "yAxis": {"type": "value"},
    "series": [{"type": "bar", "data": [12, 18]}],
}
alt = None
if mode == "override":
    option["aria"] = {"enabled": False, "label": {"description": "Option description"}}
    alt = "Native alt wins even with disabled aria"
elif mode == "disabled":
    option["aria"] = {"enabled": False}
elif mode == "empty":
    alt = "   "
st.echarts_chart(option, theme=None, key="accessible", alt=alt)
""",
        encoding="utf-8",
    )
    with serve(app) as url:
        page = browser.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(url)
        chart = page.get_by_test_id("stEChartsChart")
        expect(chart).to_have_attribute("aria-busy", "false", timeout=20_000)
        expect(chart).to_have_attribute("role", "img")
        expect(chart).to_have_attribute("aria-label", re.compile(r".+"))
        select(page, "Case", "override")
        assert_chart(page, "Native alt wins even with disabled aria", "canvas")
        select(page, "Case", "disabled")
        expect(chart).not_to_have_attribute("role", "img", timeout=20_000)
        expect(chart).not_to_have_attribute("aria-label", re.compile(r".+"))
        select(page, "Case", "empty")
        expect(chart).to_have_attribute("role", "img", timeout=20_000)
        expect(chart).to_have_attribute("aria-label", re.compile(r".+"))
        assert not errors, errors
        page.close()
    return 4


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, help="Use an already-installed Chromium binary")
    parser.add_argument("--report", type=Path, help="Write a JSON run report")
    args = parser.parse_args()
    entries = [
        entry
        for entry in json.loads((ROOT / "examples/index.json").read_text())["examples"]
        if entry["target"] == "native"
    ]
    started = time.monotonic()
    checked = []
    with sync_playwright() as playwright:
        launch = {"headless": True, "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
        if args.executable:
            launch["executable_path"] = str(args.executable)
        browser = playwright.chromium.launch(**launch)
        try:
            with serve_demo() as url:
                page = browser.new_page(viewport={"width": 1440, "height": 1000})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.on(
                    "console",
                    lambda message: (
                        errors.append(message.text) if message.type == "error" else None
                    ),
                )
                page.goto(url)
                expect(page.get_by_test_id("stEChartsChart")).to_be_visible(timeout=30_000)
                current_selected = entries[0]["name"]
                current_themed = True
                wait_for_demo_state(page, current_selected, "canvas", current_themed)
                for renderer in ("canvas", "svg"):
                    select(page, "Renderer", renderer)
                    wait_for_demo_state(page, current_selected, renderer, current_themed)
                    for themed in (True, False):
                        toggle = page.get_by_role("switch", name="Apply Streamlit theme")
                        if toggle.is_checked() != themed:
                            # Streamlit overlays the input with a styled switch; use its keyboard UI.
                            toggle.press("Space")
                        if themed:
                            expect(toggle).to_be_checked()
                        else:
                            expect(toggle).not_to_be_checked()
                        wait_for_demo_state(page, current_selected, renderer, themed)
                        current_themed = themed
                        for entry in entries:
                            select(page, "Chart", entry["name"].replace("_", " ").title())
                            wait_for_demo_state(page, entry["name"], renderer, themed)
                            try:
                                assert_chart(page, entry["description"], renderer)
                            except AssertionError as error:
                                raise AssertionError(
                                    f"{entry['name']}, renderer={renderer}, theme={themed}: {error}"
                                ) from error
                            assert not errors, errors
                            current_selected = entry["name"]
                            checked.append(
                                {
                                    "example": entry["name"],
                                    "renderer": renderer,
                                    "theme": "streamlit" if themed else None,
                                }
                            )
                        print(
                            f"PASS: {len(entries)} examples, renderer={renderer}, theme={themed}",
                            flush=True,
                        )
                page.close()
            with tempfile.TemporaryDirectory() as temporary:
                accessibility = check_accessibility(browser, Path(temporary))
        finally:
            browser.close()
    import streamlit

    report = {
        "streamlit": streamlit.__version__,
        "native_examples": len(entries),
        "renders": len(checked),
        "accessibility_cases": accessibility,
        "seconds": round(time.monotonic() - started, 2),
        "cases": checked,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {len(checked)} chart renders and {accessibility} accessibility cases", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
