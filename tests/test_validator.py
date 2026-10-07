"""Regression checks for malformed chart contracts and valid option overrides.

Run from the repository root: python -m unittest discover -s tests -t .
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from validate_option import CORE_TYPES, load_option, validate_option

from tests import SKILL_ROOT

ROOT = SKILL_ROOT


def example(name, folder="native"):
    return load_option((ROOT / "examples" / folder / f"{name}.json").read_text(encoding="utf-8"))


def errors(option, **kwargs):
    return [issue for issue in validate_option(option, **kwargs) if issue.level == "ERROR"]


class StrictJSONTests(unittest.TestCase):
    def test_reject_invalid_json_and_duplicate_keys(self):
        for raw in [
            '{"x":1,"x":2}',
            '{"data":[NaN]}',
            '{"data":[Infinity]}',
            '{"data":[-Infinity]}',
            '{"x":1,}',
            "{'x':1}",
        ]:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                load_option(raw)

    def test_reject_overflowing_exponent(self):
        chart = example("bar")
        chart["series"][0]["data"][0] = load_option("1e400")
        self.assertTrue(errors(chart))

    def test_option_must_be_object(self):
        self.assertTrue(errors([]))
        self.assertTrue(errors({"spec": example("bar")}))

    def test_literal_function_text_is_allowed(self):
        chart = example("bar")
        chart["title"]["text"] = "The function (x) and x => y notation"
        self.assertFalse(errors(chart))


class ChartContractTests(unittest.TestCase):
    def test_all_native_examples(self):
        for path in sorted((ROOT / "examples/native").glob("*.json")):
            with self.subTest(path=path.name):
                self.assertEqual(validate_option(load_option(path.read_text())), [])

    def test_catalog_covers_every_core_series(self):
        index = json.loads((ROOT / "examples/index.json").read_text())["examples"]
        covered = {kind for entry in index for kind in entry["series_types"]}
        self.assertTrue(CORE_TYPES <= covered)
        for entry in index:
            self.assertTrue((ROOT / "examples" / entry["file"]).is_file())

    def test_external_examples_require_an_external_host(self):
        for path in sorted((ROOT / "examples/external").glob("*.json")):
            option = load_option(path.read_text())
            with self.subTest(path=path.name):
                self.assertTrue(errors(option))
                self.assertFalse(errors(option, target="echarts"))

    def test_category_alignment_and_missing_axis(self):
        chart = example("bar")
        chart["series"][0]["data"].pop()
        self.assertTrue(errors(chart))
        chart = example("line")
        del chart["yAxis"]
        self.assertTrue(errors(chart))

    def test_null_gap_is_allowed(self):
        self.assertFalse(errors(example("line")))

    def test_boxplot_order_and_candlestick_contract(self):
        chart = example("boxplot")
        chart["series"][0]["data"][0] = [10, 18, 15, 12, 22]
        self.assertTrue(errors(chart))
        chart = example("candlestick")
        chart["series"][0]["data"][0] = [100, 104, 105, 106]
        self.assertTrue(errors(chart))
        chart["series"][0]["data"][0] = [100, 104, 98]
        self.assertTrue(errors(chart))

    def test_radar_dimension_alignment(self):
        chart = example("radar")
        chart["series"][0]["data"][0]["value"].pop()
        self.assertTrue(errors(chart))
        chart["radar"]["indicator"] = None
        self.assertTrue(errors(chart))

    def test_heatmap_index_and_magnitude(self):
        chart = example("heatmap")
        chart["series"][0]["data"][0][0] = 999
        self.assertTrue(errors(chart))
        chart = example("heatmap")
        chart["series"][0]["data"][0][2] = "many"
        self.assertTrue(errors(chart))

    def test_heatmap_wrong_dimension_warns(self):
        chart = example("calendar_heatmap")
        chart["visualMap"]["dimension"] = 2
        self.assertTrue(
            any(i.level == "WARN" and "dimension" in i.path for i in validate_option(chart))
        )

    def test_link_resolution(self):
        chart = example("graph")
        chart["series"][0]["links"][0]["target"] = "missing-node"
        self.assertTrue(errors(chart))

    def test_sankey_cycle_rejected_chord_cycle_allowed(self):
        chart = example("sankey")
        chart["series"][0]["links"].append({"source": "Industry", "target": "Supply", "value": 5})
        self.assertTrue(errors(chart))
        self.assertFalse(errors(example("chord")))

    def test_duplicate_nodes_and_negative_flows(self):
        chart = example("sankey")
        chart["series"][0]["data"].append({"name": "Supply"})
        self.assertTrue(errors(chart))
        chart = example("sankey")
        chart["series"][0]["links"][0]["value"] = -1
        self.assertTrue(errors(chart))

    def test_lines_default_geo_and_coords_without_value(self):
        chart = example("lines")
        del chart["series"][0]["coordinateSystem"]
        self.assertTrue(errors(chart))
        chart = example("lines")
        chart["series"][0]["data"] = [{"coords": [[1, 2], [3, 4]]}]
        self.assertFalse(errors(chart))
        chart["series"][0]["data"] = [{"coords": [[1, 2]]}]
        self.assertTrue(errors(chart))

    def test_unsorted_time_series(self):
        chart = example("time_line")
        chart["series"][0]["data"].reverse()
        self.assertTrue(errors(chart))

    def test_dataset_encode_and_dimension_contract(self):
        chart = example("dataset_bar")
        chart["series"][0]["encode"]["y"] = "missing-column"
        self.assertTrue(errors(chart))
        chart = example("dataset_bar")
        chart["dataset"]["dimensions"] = ["month", "revenue", "revenue"]
        self.assertTrue(errors(chart))
        chart = example("dataset_bar")
        chart["dataset"]["source"] = [["Jan", 120, 80], ["Feb", 150]]
        self.assertTrue(errors(chart))

    def test_malformed_hierarchy(self):
        chart = example("tree")
        chart["series"][0]["data"][0]["children"] = {"name": "wrong-container"}
        self.assertTrue(errors(chart))

    def test_callback_string_and_callback_only_formatter(self):
        for formatter in [
            "function(p) { return p.value; }",
            "p => p.value",
            "(p) => p.value",
            "--x_x--function(p){return p;}--x_x--",
        ]:
            chart = example("bar")
            chart["tooltip"]["formatter"] = formatter
            with self.subTest(formatter=formatter):
                self.assertTrue(errors(chart))
        chart = example("bar")
        chart["tooltip"]["valueFormatter"] = "{value} USD"
        self.assertTrue(errors(chart))

    def test_v5_rejects_chord(self):
        self.assertTrue(errors(example("chord"), echarts_major=5))


class OverrideAndCLITests(unittest.TestCase):
    def timeline(self):
        return {
            "baseOption": {
                "timeline": {"axisType": "category", "data": ["2025", "2026"]},
                "xAxis": {"type": "category", "data": ["A", "B"]},
                "yAxis": {"type": "value"},
                "series": [{"id": "sales", "type": "bar"}],
            },
            "options": [
                {"series": [{"id": "sales", "data": [10, 20]}]},
                {"series": [{"id": "sales", "data": [15, 25]}]},
            ],
        }

    def test_timeline_inherits_type_and_axes(self):
        self.assertFalse(errors(self.timeline()))

    def test_nested_unsupported_features_cannot_hide(self):
        chart = self.timeline()
        chart["options"][1]["series"][0].update(type="custom", renderItem="barRange")
        self.assertTrue(errors(chart))
        chart = example("bar")
        chart["media"] = [{"query": {"maxWidth": 600}, "option": {"geo": {"map": "world"}}}]
        self.assertTrue(errors(chart))
        chart = self.timeline()
        chart["baseOption"]["media"] = [
            {"option": {"series": [{"id": "sales", "type": "wordCloud"}]}}
        ]
        self.assertTrue(errors(chart))

    def test_partial_media_series_inherits_type(self):
        chart = example("bar")
        chart["media"] = [
            {
                "query": {"maxWidth": 600},
                "option": {"series": [{"id": chart["series"][0]["id"], "barMaxWidth": 20}]},
            }
        ]
        self.assertFalse(errors(chart))

    def test_cli_rejects_invalid_json_with_nonzero_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "invalid.json"
            path.write_text('{"series":[],"series":[]}')
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/validate_option.py"), str(path)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("Duplicate JSON key", result.stdout)


if __name__ == "__main__":
    unittest.main()
