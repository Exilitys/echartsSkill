"""Integration checks against the installed native Streamlit API, not a mock."""

from __future__ import annotations

import importlib.util
import inspect
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HAS_STREAMLIT = importlib.util.find_spec("streamlit") is not None
if HAS_STREAMLIT:
    import streamlit as st
    from streamlit.elements.echarts_chart import _normalize_spec, _serialize_option
    from streamlit.errors import StreamlitAPIException
    from streamlit.testing.v1 import AppTest


@unittest.skipUnless(HAS_STREAMLIT, "Install requirements-dev.txt for native integration checks")
class NativeStreamlitTests(unittest.TestCase):
    def test_documented_signature(self):
        parameters = inspect.signature(st.echarts_chart).parameters
        self.assertEqual(
            list(parameters), ["spec", "width", "height", "theme", "key", "renderer", "alt"]
        )
        expected = {
            "width": "stretch",
            "height": "content",
            "theme": "streamlit",
            "key": None,
            "renderer": "canvas",
            "alt": None,
        }
        for name, default in expected.items():
            self.assertEqual(parameters[name].default, default)

    def test_all_native_examples_accept_dict_and_json_inputs(self):
        for path in sorted((ROOT / "examples/native").glob("*.json")):
            raw = path.read_text()
            for spec in (json.loads(raw), raw):
                with self.subTest(example=path.name, input=type(spec).__name__):
                    self.assertEqual(
                        json.loads(_serialize_option(_normalize_spec(spec))), json.loads(raw)
                    )

    def test_all_external_examples_are_rejected_by_native_streamlit(self):
        for path in sorted((ROOT / "examples/external").glob("*.json")):
            with self.subTest(example=path.name), self.assertRaises(StreamlitAPIException):
                _normalize_spec(path.read_text())

    def test_unsupported_features_are_rejected_in_option_variants(self):
        variants = [
            {"geo": {"map": "sample"}},
            {"series": [{"type": "custom", "renderItem": "namedRenderer"}]},
            {"series": [{"type": "scatter3D"}]},
            {"series": [{"type": "wordCloud"}]},
        ]
        for variant in variants:
            for option in (
                variant,
                {"baseOption": variant},
                {"media": [{"option": variant}]},
                {"baseOption": {}, "options": [variant]},
            ):
                with self.subTest(option=option), self.assertRaises(StreamlitAPIException):
                    _normalize_spec(option)

    def test_callbacks_and_nonfinite_values_are_not_serializable(self):
        for value in (lambda item: item, float("nan"), float("inf"), object()):
            with self.subTest(value=type(value).__name__), self.assertRaises(StreamlitAPIException):
                _serialize_option({"series": [{"type": "bar", "data": [value]}]})
        for raw in (
            '{"tooltip":{"formatter":function(p){return p.value;}}}',
            '{"tooltip":{"formatter":"--x_x--function(p){return p.value;}--x_x--"}}',
        ):
            with self.subTest(raw=raw), self.assertRaises(StreamlitAPIException):
                _normalize_spec(raw)

    def test_dataframe_conversion_preserves_order_missing_values_and_input(self):
        import pandas as pd

        frame = pd.DataFrame({"product": ["A", "B"], "2025": [2.0, float("nan")], "2026": [4, 5]})
        spec = {
            "dataset": {"source": frame},
            "xAxis": {"type": "category"},
            "yAxis": {},
            "series": [{"type": "bar"}, {"type": "bar"}],
        }
        converted = json.loads(_serialize_option(_normalize_spec(spec)))
        self.assertEqual(converted["dataset"]["dimensions"], ["product", "2025", "2026"])
        self.assertEqual(
            converted["dataset"]["source"],
            [
                {"product": "A", "2025": 2.0, "2026": 4},
                {"product": "B", "2025": None, "2026": 5},
            ],
        )
        self.assertIs(spec["dataset"]["source"], frame)
        self.assertNotIn("dimensions", spec["dataset"])
        spec["dataset"]["dimensions"] = ["product", "sales", "forecast"]
        self.assertEqual(
            _normalize_spec(spec)["dataset"]["dimensions"], ["product", "sales", "forecast"]
        )

    @unittest.skipUnless(
        importlib.util.find_spec("pyecharts"), "Install pyecharts for input checks"
    )
    def test_pyecharts_and_dump_options_duck_typing(self):
        from pyecharts.charts import Bar

        chart = Bar().add_xaxis(["A", "B"]).add_yaxis("Sales", [3, 5])
        serialized = json.loads(_serialize_option(_normalize_spec(chart)))
        self.assertEqual(serialized["series"][0]["type"], "bar")
        self.assertEqual(serialized["series"][0]["data"], [3, 5])

        class Dumpable:
            def dump_options(self):
                return '{"series":[{"type":"pie","data":[{"name":"A","value":1}]}]}'

        self.assertEqual(_normalize_spec(Dumpable())["series"][0]["type"], "pie")

    def test_public_api_serializes_wrapper_arguments_and_rejects_invalid_values(self):
        app = AppTest.from_string("""
import streamlit as st
st.echarts_chart('{"series":[{"type":"pie","data":[{"name":"A","value":1}]}]}',
    theme=None, renderer="svg", height=420, width="stretch", key="pie", alt="One category")
""").run(timeout=15)
        self.assertEqual(len(app.exception), 0)
        chart = app.get("echarts_chart")[0].proto
        self.assertEqual(chart.alt, "One category")
        self.assertEqual(chart.theme, "")
        self.assertEqual(chart.renderer, 1)
        self.assertEqual(json.loads(chart.spec)["series"][0]["type"], "pie")
        for argument in (
            {"theme": "dark"},
            {"renderer": "webgl"},
            {"height": "420px"},
            {"width": "100%"},
        ):
            with self.subTest(argument=argument), self.assertRaises(StreamlitAPIException):
                # Use the public entrypoint; invalid wrapper values fail before enqueueing.
                st.echarts_chart({"series": []}, **argument)

    def test_demo_controls_stable_key_and_alt(self):
        app = AppTest.from_file(str(ROOT / "scripts/demo_app.py")).run(timeout=20)
        self.assertEqual(len(app.exception), 0)
        original_id = app.get("echarts_chart")[0].proto.id
        app.selectbox[0].select("chord")
        app.selectbox[1].select("svg")
        app.toggle[0].set_value(False)
        app.run(timeout=20)
        self.assertEqual(len(app.exception), 0)
        chart = app.get("echarts_chart")[0].proto
        self.assertEqual(chart.id, original_id)
        self.assertEqual(chart.renderer, 1)
        self.assertEqual(chart.theme, "")
        self.assertTrue(chart.alt.strip())
        option = json.loads(chart.spec)
        self.assertEqual(option["series"][0]["type"], "chord")
        self.assertNotIn("description", option.get("aria", {}).get("label", {}))
