"""Check portable resources, links, example inventory, and archive installation."""

from __future__ import annotations

import ast
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

from scripts.package_skill import build_package
from scripts.validate_option import CORE_TYPES, load_option

ROOT = Path(__file__).resolve().parent.parent


class RepositoryTests(unittest.TestCase):
    def test_example_inventory_matches_files_and_series(self):
        entries = json.loads((ROOT / "examples/index.json").read_text())["examples"]
        names = [entry["name"] for entry in entries]
        files = [entry["file"] for entry in entries]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(len(files), len(set(files)))
        actual = {
            path.relative_to(ROOT / "examples").as_posix()
            for folder in ("native", "external")
            for path in (ROOT / "examples" / folder).glob("*.json")
        }
        self.assertEqual(set(files), actual)
        covered = set()
        for entry in entries:
            with self.subTest(example=entry["name"]):
                self.assertIn(entry["target"], {"native", "external"})
                self.assertTrue(entry["file"].startswith(entry["target"] + "/"))
                self.assertTrue(entry["description"].strip())
                option = load_option((ROOT / "examples" / entry["file"]).read_text())
                series = option["series"]
                types = {item["type"] for item in series}
                self.assertEqual(set(entry["series_types"]), types)
                ids = [item["id"] for item in series]
                self.assertEqual(len(ids), len(set(ids)))
                if entry["target"] == "external":
                    self.assertTrue(entry["requires"])
                covered.update(types)
        self.assertTrue(CORE_TYPES <= covered)

    def test_relative_markdown_links_resolve(self):
        for path in ROOT.rglob("*.md"):
            if ".git" in path.parts or any(part.startswith(".venv") for part in path.parts):
                continue
            for target in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", path.read_text()):
                target = target.strip("<>").split("#", 1)[0]
                if not target or urlsplit(target).scheme:
                    continue
                with self.subTest(file=path.relative_to(ROOT), target=target):
                    self.assertTrue((path.parent / unquote(target)).exists())

    def test_validator_and_packager_have_no_third_party_dependencies(self):
        for name in ("validate_option.py", "package_skill.py"):
            tree = ast.parse((ROOT / "scripts" / name).read_text())
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module.split(".")[0])
            self.assertTrue(imports <= sys.stdlib_module_names, imports - sys.stdlib_module_names)

    def test_map_names_match_registered_sample_regions(self):
        option = load_option((ROOT / "examples/external/map.json").read_text())
        geojson = json.loads((ROOT / "examples/assets/sample-regions.geojson").read_text())
        regions = {feature["properties"]["name"] for feature in geojson["features"]}
        self.assertEqual({item["name"] for item in option["series"][0]["data"]}, regions)

    def test_archive_is_portable_and_excludes_generated_or_private_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            sandbox = Path(temporary)
            archive_path = sandbox / "echarts-json.zip"
            names = build_package(ROOT, archive_path)
            self.assertTrue(all(name.startswith("echarts-json/") for name in names))
            for required in (
                "SKILL.md",
                "LICENSE",
                "README.md",
                "references/streamlit.md",
                "examples/index.json",
                "scripts/validate_option.py",
                "agents/openai.yaml",
            ):
                self.assertIn(f"echarts-json/{required}", names)
            self.assertFalse(any("__pycache__" in name or name.endswith(".pyc") for name in names))
            self.assertFalse(any("/.git/" in name or "/.venv/" in name for name in names))
            with ZipFile(archive_path) as archive:
                self.assertIsNone(archive.testzip())
                archive.extractall(sandbox / "installed")
            installed = sandbox / "installed/echarts-json"
            for name in names:
                relative = Path(name).relative_to("echarts-json")
                self.assertEqual(
                    (installed / relative).read_bytes(), (ROOT / relative).read_bytes()
                )
            # An installed directory may coexist with user files or Python caches.
            (installed / ".env").write_text("local-only")
            (installed / "scripts/__pycache__").mkdir(exist_ok=True)
            (installed / "scripts/__pycache__/generated.py").write_text("local-only")
            repacked = build_package(installed, sandbox / "repacked.zip")
            self.assertEqual(names, repacked)


try:
    import yaml
except ImportError:
    yaml = None


@unittest.skipIf(yaml is None, "Install requirements-dev.txt to check YAML metadata")
class SkillMetadataTests(unittest.TestCase):
    def test_frontmatter_matches_agent_skills_spec(self):
        text = (ROOT / "SKILL.md").read_text()
        self.assertTrue(text.startswith("---\n"))
        metadata = yaml.safe_load(text.split("---", 2)[1])
        self.assertRegex(metadata["name"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertLessEqual(len(metadata["name"]), 64)
        self.assertEqual(metadata["name"], "echarts-json")
        self.assertTrue(1 <= len(metadata["description"]) <= 1024)
        self.assertTrue(1 <= len(metadata["compatibility"]) <= 500)
        self.assertEqual(metadata["license"], "MIT")
        self.assertTrue(all(isinstance(value, str) for value in metadata["metadata"].values()))

    def test_optional_codex_metadata_matches_skill_name(self):
        metadata = yaml.safe_load((ROOT / "agents/openai.yaml").read_text())
        interface = metadata["interface"]
        self.assertIn("$echarts-json", interface["default_prompt"])
        self.assertTrue(25 <= len(interface["short_description"]) <= 64)
