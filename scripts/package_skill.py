"""Build a portable skill ZIP with only the repository's public resources."""

from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

SKILL_NAME = "echarts-json"
ROOT = Path(__file__).resolve().parent.parent
ROOT_FILES = (
    "SKILL.md",
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "VALIDATION.md",
    "pyproject.toml",
    "requirements-dev.txt",
    "requirements-browser.txt",
    ".editorconfig",
    ".gitattributes",
    ".gitignore",
)
RESOURCE_DIRECTORIES = ("agents", "references", "examples", "scripts", "docs", "tests")
EXCLUDED_DIRECTORIES = {"__pycache__", ".pytest_cache", ".ruff_cache", "node_modules"}
RESOURCE_SUFFIXES = {".md", ".py", ".json", ".geojson", ".yaml", ".yml"}


def package_paths(root: Path) -> list[Path]:
    """Allowlist resources, excluding generated files, environments, and symlinks."""
    paths = [root / name for name in ROOT_FILES if (root / name).is_file()]
    for directory in RESOURCE_DIRECTORIES:
        for path in sorted((root / directory).rglob("*")):
            relative = path.relative_to(root)
            if (
                path.is_file()
                and path.suffix in RESOURCE_SUFFIXES
                and not EXCLUDED_DIRECTORIES.intersection(relative.parts)
            ):
                paths.append(path)
    for path in paths:
        if path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
            raise ValueError(f"Refusing to package a symlink: {path}")
    return sorted(paths)


def build_package(root: Path, output: Path) -> list[str]:
    """Keep directory names stable and Markdown/resource links valid after extraction."""
    root = root.resolve()
    if not (root / "SKILL.md").is_file():
        raise ValueError(f"Missing SKILL.md in {root}")
    paths = package_paths(root)
    output = output.resolve()
    if output in paths:
        raise ValueError("The output archive must not replace a skill resource")
    output.parent.mkdir(parents=True, exist_ok=True)
    names = []
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in paths:
            name = f"{SKILL_NAME}/{path.relative_to(root).as_posix()}"
            archive.write(path, name)
            names.append(name)
    return names


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / f"{SKILL_NAME}.zip")
    arguments = parser.parse_args()
    try:
        names = build_package(ROOT, arguments.output)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Packaging failed: {error}\n")
    print(f"Packaged {len(names)} files into {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
