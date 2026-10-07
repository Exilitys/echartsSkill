#!/usr/bin/env python3
"""Focused ECharts JSON/data-contract linter. Python standard library only.

This is intentionally not a full ECharts schema or rendering test. Complex
dataset transforms and option merge semantics must be verified in the host.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CORE_TYPES = frozenset(
    {
        "line",
        "bar",
        "pie",
        "scatter",
        "effectScatter",
        "radar",
        "tree",
        "treemap",
        "sunburst",
        "boxplot",
        "candlestick",
        "heatmap",
        "map",
        "parallel",
        "lines",
        "graph",
        "sankey",
        "funnel",
        "gauge",
        "pictorialBar",
        "themeRiver",
        "custom",
        "chord",
    }
)
GL_TYPES = frozenset(
    {
        "bar3D",
        "scatter3D",
        "line3D",
        "lines3D",
        "map3D",
        "surface",
        "polygons3D",
        "graphGL",
        "scatterGL",
        "flowGL",
        "linesGL",
        "globe",
    }
)
EXTENSION_TYPES = GL_TYPES | {"wordCloud", "liquidFill"}
GL_COMPONENTS = frozenset({"grid3D", "geo3D", "globe", "mapbox3D"})
CARTESIAN_TYPES = frozenset(
    {"line", "bar", "scatter", "effectScatter", "boxplot", "candlestick", "heatmap", "pictorialBar"}
)
COMPONENTS = frozenset(
    {
        "series",
        "xAxis",
        "yAxis",
        "grid",
        "dataset",
        "calendar",
        "radar",
        "parallel",
        "parallelAxis",
        "polar",
        "singleAxis",
        "angleAxis",
        "radiusAxis",
        "visualMap",
        "matrix",
    }
)
CALLBACK_FIELDS = frozenset(
    {
        "formatter",
        "valueFormatter",
        "renderItem",
        "symbolSize",
        "symbolRotate",
        "color",
        "opacity",
        "sort",
        "min",
        "max",
        "labelLayout",
        "position",
        "onClick",
        "onclick",
        "onmouseover",
    }
)
JS_SOURCE = re.compile(
    r"^\s*(?:function(?:\s+[\w$]+)?\s*\(|(?:async\s+)?\([^)]*\)\s*=>|"
    r"(?:async\s+)?[A-Za-z_$][\w$]*\s*=>)"
)


@dataclass(frozen=True)
class Issue:
    level: str
    path: str
    message: str


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _bad_constant(value: str) -> Any:
    raise ValueError(f"{value} is not a strict JSON number")


def load_option(text: str) -> Any:
    """Reject duplicate keys and JavaScript nonfinite tokens while parsing."""
    return json.loads(text, object_pairs_hook=_pairs, parse_constant=_bad_constant)


def _walk(value: Any, path: str = "$"):
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _walk(child, f"{path}.{key}")
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from _walk(child, f"{path}[{i}]")


def _entries(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list):
        return [v for v in value if isinstance(v, dict)]
    return []


def _merge(base: Any, change: Any, key: str = "") -> Any:
    """Approximate simple component overrides by ID or position, without mutation."""
    if key in COMPONENTS and isinstance(base, (dict, list)) and isinstance(change, (dict, list)):
        left = deepcopy(_entries(base))
        for i, item in enumerate(_entries(change)):
            item_id = item.get("id")
            index = next(
                (
                    j
                    for j, old in enumerate(left)
                    if item_id is not None and old.get("id") == item_id
                ),
                None,
            )
            if index is None:
                index = i if item_id is None else len(left)
            if index < len(left):
                left[index] = _merge(left[index], item)
            else:
                left.append(deepcopy(item))
        return (
            left
            if isinstance(base, list) or isinstance(change, list)
            else (left[0] if left else {})
        )
    if isinstance(base, dict) and isinstance(change, dict):
        result = deepcopy(base)
        for name, value in change.items():
            result[name] = _merge(result[name], value, name) if name in result else deepcopy(value)
        return result
    return deepcopy(change)


def _variants(option: dict[str, Any]):
    ordinary = {k: v for k, v in option.items() if k not in {"baseOption", "options", "media"}}
    base = _merge(
        ordinary,
        option.get("baseOption", {}) if isinstance(option.get("baseOption", {}), dict) else {},
    )
    yield "$.baseOption" if "baseOption" in option else "$", base
    for prefix, host in [("$", option), ("$.baseOption", option.get("baseOption", {}))]:
        if not isinstance(host, dict):
            continue
        media = host.get("media", [])
        if isinstance(media, list):
            for i, entry in enumerate(media):
                if isinstance(entry, dict) and isinstance(entry.get("option"), dict):
                    yield f"{prefix}.media[{i}].option", _merge(base, entry["option"])
    options = option.get("options", [])
    if isinstance(options, list):
        for i, change in enumerate(options):
            if not isinstance(change, dict):
                continue
            effective = _merge(base, change)
            yield f"$.options[{i}]", effective
            media = change.get("media", [])
            if isinstance(media, list):
                for j, entry in enumerate(media):
                    if isinstance(entry, dict) and isinstance(entry.get("option"), dict):
                        yield (
                            f"$.options[{i}].media[{j}].option",
                            _merge(effective, entry["option"]),
                        )


def _number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and (not isinstance(value, float) or math.isfinite(value))
    )


def _value(item: Any) -> Any:
    return item.get("value") if isinstance(item, dict) else item


def _stamp(value: Any) -> float | None:
    if _number(value):
        return float(value)
    if isinstance(value, str):
        try:
            date = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return (
                date.replace(tzinfo=timezone.utc).timestamp() * 1000
                if date.tzinfo is None
                else date.timestamp() * 1000
            )
        except (ValueError, OverflowError):
            return None
    return None


def validate_option(option: Any, target: str = "streamlit", echarts_major: int = 6) -> list[Issue]:
    issues: list[Issue] = []
    seen: set[tuple[str, str, str]] = set()

    def report(level: str, path: str, message: str) -> None:
        item = (level, path, message)
        if item not in seen:
            issues.append(Issue(*item))
            seen.add(item)

    def error(path: str, message: str) -> None:
        report("ERROR", path, message)

    def warn(path: str, message: str) -> None:
        report("WARN", path, message)

    if not isinstance(option, dict):
        return [Issue("ERROR", "$", "An ECharts option must be a JSON object.")]

    for path, value in _walk(option):
        if isinstance(value, float) and not math.isfinite(value):
            error(path, "Number is not finite, including an overflowing JSON exponent.")
        if isinstance(value, str):
            if value.startswith("--x_x--") and value.endswith("--x_x--") and len(value) > 14:
                error(path, "pyecharts JsCode is not a usable JSON-only callback.")
            field = path.rsplit(".", 1)[-1]
            if field in CALLBACK_FIELDS and JS_SOURCE.match(value):
                error(path, "JavaScript source is not executable in a JSON-only option.")
        if isinstance(value, dict):
            for key in COMPONENTS:
                if key in value and (
                    path == "$"
                    or path.endswith(".baseOption")
                    or ".options[" in path
                    or ".media[" in path
                ):
                    component = value[key]
                    if not isinstance(component, (dict, list)) or (
                        isinstance(component, list)
                        and any(not isinstance(x, dict) for x in component)
                    ):
                        error(
                            f"{path}.{key}", "Component must be an object or an array of objects."
                        )
            if value.get("valueFormatter") is not None:
                error(
                    f"{path}.valueFormatter",
                    "valueFormatter requires a function; use a supported tooltip template instead.",
                )
            for key in ("options", "media"):
                if key in value and not isinstance(value[key], list):
                    error(f"{path}.{key}", "This option envelope field must be an array.")
            if "baseOption" in value and not isinstance(value["baseOption"], dict):
                error(f"{path}.baseOption", "baseOption must be an object.")

    if "spec" in option or ("options" in option and isinstance(option["options"], dict)):
        error("$", "Pass the option itself, without a spec/options wrapper.")
    for key in ("height", "width", "theme", "key", "renderer", "alt", "events", "on_select"):
        if key in option:
            warn(f"$.{key}", "This is normally a host argument, not a top-level ECharts option.")

    def component(variant: dict[str, Any], key: str, index: Any, path: str) -> dict[str, Any]:
        values = _entries(variant.get(key))
        if not isinstance(index, int) or isinstance(index, bool) or index < 0:
            error(path, f"{key} index must be a nonnegative integer.")
            return {}
        if index >= len(values):
            error(path, f"Missing {key} component at index {index}.")
            return {}
        return values[index]

    def datasets(variant: dict[str, Any], prefix: str) -> None:
        for i, dataset in enumerate(_entries(variant.get("dataset"))):
            path = f"{prefix}.dataset[{i}]"
            dims = dataset.get("dimensions", [])
            if not isinstance(dims, list):
                error(path + ".dimensions", "Dimensions must be an array.")
                continue
            names = [d.get("name") if isinstance(d, dict) else d for d in dims]
            if any(not isinstance(n, str) for n in names) or len(names) != len(
                set(n for n in names if isinstance(n, str))
            ):
                error(path + ".dimensions", "Dimension names must be unique strings.")
            source = dataset.get("source")
            if isinstance(source, list) and source and isinstance(source[0], list):
                if any(not isinstance(row, list) or len(row) != len(source[0]) for row in source):
                    error(path + ".source", "Tabular rows must have a consistent column count.")
                if names and len(names) != len(source[0]):
                    error(path + ".dimensions", "Dimension count does not match table width.")
            if "transform" in dataset:
                warn(
                    path + ".transform",
                    "Transform execution and registration are not checked; verify the host or precompute data.",
                )

    def links(series: dict[str, Any], kind: str, path: str) -> None:
        nodes = series.get("data", series.get("nodes", []))
        edges = series.get("links", series.get("edges", []))
        if not isinstance(nodes, list) or not isinstance(edges, list):
            error(path, "Network nodes and links must be arrays.")
            return
        ids: dict[str, int] = {}
        for i, node in enumerate(nodes):
            if not isinstance(node, dict):
                error(
                    f"{path}.data[{i}]",
                    "Use named/identified node objects for this network contract.",
                )
                continue
            identifier = node.get("name") if kind == "sankey" else node.get("id", node.get("name"))
            if not isinstance(identifier, str):
                error(f"{path}.data[{i}]", "Node needs a string name/ID.")
            elif identifier in ids:
                error(f"{path}.data[{i}]", "Node names/IDs must be unique.")
            else:
                ids[identifier] = i
        adjacency: dict[int, list[int]] = {i: [] for i in range(len(nodes))}
        for i, edge in enumerate(edges):
            ep = f"{path}.links[{i}]"
            if not isinstance(edge, dict):
                error(ep, "Link must be an object.")
                continue
            ends = []
            for key in ("source", "target"):
                ref = edge.get(key)
                index = (
                    ref
                    if isinstance(ref, int) and not isinstance(ref, bool) and 0 <= ref < len(nodes)
                    else ids.get(ref)
                    if isinstance(ref, str)
                    else None
                )
                if index is None:
                    error(ep + "." + key, "Link endpoint does not resolve to an existing node.")
                ends.append(index)
            if kind in {"sankey", "chord"} and (
                not _number(edge.get("value")) or edge["value"] < 0
            ):
                error(ep + ".value", "Weighted links require a nonnegative finite value.")
            if all(end is not None for end in ends):
                adjacency[ends[0]].append(ends[1])
        if kind == "sankey":
            incoming = {i: 0 for i in adjacency}
            for targets in adjacency.values():
                for end in targets:
                    incoming[end] += 1
            ready = [i for i, degree in incoming.items() if degree == 0]
            count = 0
            while ready:
                node = ready.pop()
                count += 1
                for end in adjacency[node]:
                    incoming[end] -= 1
                    if incoming[end] == 0:
                        ready.append(end)
            if count != len(nodes):
                error(path + ".links", "Sankey links contain a directed cycle.")

    def hierarchy(nodes: Any, path: str, quantitative: bool) -> None:
        if not isinstance(nodes, list):
            error(path, "Hierarchy nodes/children must be arrays.")
            return
        for i, node in enumerate(nodes):
            np = f"{path}[{i}]"
            if not isinstance(node, dict):
                error(np, "Hierarchy nodes must be objects.")
                continue
            value = node.get("value")
            if quantitative and value is not None and (not _number(value) or value < 0):
                error(np + ".value", "Area hierarchy values must be nonnegative finite numbers.")
            if "children" in node:
                hierarchy(node["children"], np + ".children", quantitative)

    for prefix, variant in _variants(option):
        if target == "streamlit":
            for key in ("geo", *sorted(GL_COMPONENTS)):
                if key in variant:
                    error(
                        prefix + "." + key,
                        "Native Streamlit does not support geo or GL coordinate components.",
                    )
        if echarts_major < 6 and "matrix" in variant:
            error(prefix + ".matrix", "Matrix coordinates require ECharts 6 or later.")
        datasets(variant, prefix)
        series_list = _entries(variant.get("series"))
        if not series_list:
            warn(
                prefix, "No series found; confirm this is an intentional graphic-only/empty option."
            )
        series_ids: set[str] = set()
        for si, series in enumerate(series_list):
            path = f"{prefix}.series[{si}]"
            kind = series.get("type")
            if not isinstance(kind, str) or kind not in CORE_TYPES | EXTENSION_TYPES:
                error(
                    path + ".type",
                    "Missing or unrecognized series type; check its spelling or extension contract.",
                )
                continue
            sid = series.get("id")
            if isinstance(sid, str):
                if sid in series_ids:
                    error(path + ".id", "Series IDs must be unique within an option.")
                series_ids.add(sid)
            if echarts_major < 6 and kind == "chord":
                error(path + ".type", "Chord series requires ECharts 6 or later.")
            if kind in EXTENSION_TYPES:
                if target == "streamlit":
                    error(
                        path + ".type", "Native Streamlit bundles core ECharts, not this extension."
                    )
                else:
                    warn(
                        path + ".type",
                        "Requires an externally loaded extension; rendering and module compatibility are not checked.",
                    )
            coord = series.get(
                "coordinateSystem",
                "geo" if kind == "lines" else "cartesian2d" if kind in CARTESIAN_TYPES else None,
            )
            if target == "streamlit" and (kind in {"map", "custom"} or coord == "geo"):
                error(
                    path,
                    "Native Streamlit cannot render map/geo or custom series; lines defaults to geo unless explicitly overridden.",
                )
            if kind == "map" and target == "echarts":
                if not isinstance(series.get("map"), str):
                    error(path + ".map", "A map series needs its registered map name.")
                warn(
                    path,
                    "Map asset registration and region-name matching must be checked in the external host.",
                )
            if kind == "custom":
                if not isinstance(series.get("renderItem"), str):
                    error(
                        path + ".renderItem",
                        "JSON-only custom series need a named externally registered renderer.",
                    )
                elif echarts_major < 6:
                    error(
                        path + ".renderItem", "Named custom renderers require ECharts 6 or later."
                    )
                else:
                    warn(
                        path + ".renderItem",
                        "Named custom renderer must be registered in the external host.",
                    )

            axes: dict[str, dict[str, Any]] = {}
            if coord == "cartesian2d":
                for key in ("xAxis", "yAxis"):
                    axes[key] = component(
                        variant, key, series.get(key + "Index", 0), path + "." + key + "Index"
                    )
                if (
                    axes["xAxis"]
                    and axes["yAxis"]
                    and axes["xAxis"].get("gridIndex", 0) != axes["yAxis"].get("gridIndex", 0)
                ):
                    error(path, "Cartesian axes must belong to the same grid.")
            elif coord == "polar":
                for key in ("polar", "angleAxis", "radiusAxis"):
                    component(
                        variant,
                        key,
                        series.get("polarIndex", 0) if key == "polar" else 0,
                        path + "." + key,
                    )
            elif coord == "calendar":
                component(
                    variant, "calendar", series.get("calendarIndex", 0), path + ".calendarIndex"
                )
            elif coord == "matrix":
                if echarts_major < 6:
                    error(
                        path + ".coordinateSystem", "Matrix coordinates require ECharts 6 or later."
                    )
                component(variant, "matrix", series.get("matrixIndex", 0), path + ".matrixIndex")
                warn(
                    path,
                    "Matrix coordinate mappings and series compatibility require a host rendering check.",
                )

            if kind == "radar":
                radar = component(
                    variant, "radar", series.get("radarIndex", 0), path + ".radarIndex"
                )
                indicators = radar.get("indicator", [])
                if not isinstance(indicators, list) or not indicators:
                    error(path, "Radar needs a nonempty indicator array.")
                    indicators = []
            else:
                indicators = []
            if kind == "parallel":
                component(
                    variant, "parallel", series.get("parallelIndex", 0), path + ".parallelIndex"
                )
                pa = _entries(variant.get("parallelAxis"))
                dims = [a.get("dim") for a in pa]
                if (
                    not dims
                    or any(not isinstance(d, int) or isinstance(d, bool) or d < 0 for d in dims)
                    or len(dims) != len(set(d for d in dims if isinstance(d, int)))
                ):
                    error(path, "Parallel axes need distinct nonnegative integer dimensions.")
            else:
                dims = []
            if kind == "themeRiver":
                axis = component(
                    variant,
                    "singleAxis",
                    series.get("singleAxisIndex", 0),
                    path + ".singleAxisIndex",
                )
                if axis and axis.get("type") != "time":
                    error(path, "This theme-river contract requires a time singleAxis.")
            if kind in {"graph", "sankey", "chord"}:
                links(series, kind, path)
            if kind in {"tree", "treemap", "sunburst"}:
                hierarchy(series.get("data", []), path + ".data", kind != "tree")

            direct = series.get("data")
            if direct is not None and not isinstance(direct, list):
                error(path + ".data", "Direct data must be an array in this JSON contract.")
                continue
            if direct is None and kind in CARTESIAN_TYPES:
                dsets = _entries(variant.get("dataset"))
                if not dsets:
                    warn(
                        path,
                        "No direct data or dataset found; confirm an intentional empty series.",
                    )
                elif "datasetId" in series:
                    matches = [d for d in dsets if d.get("id") == series["datasetId"]]
                    if not matches:
                        error(path + ".datasetId", "No dataset matches this ID.")
                    dataset = matches[0] if matches else {}
                else:
                    dataset = component(
                        variant, "dataset", series.get("datasetIndex", 0), path + ".datasetIndex"
                    )
                if dsets:
                    source = dataset.get("source", [])
                    names = (
                        [
                            d.get("name") if isinstance(d, dict) else d
                            for d in dataset.get("dimensions", [])
                        ]
                        if isinstance(dataset.get("dimensions", []), list)
                        else []
                    )
                    if not names and isinstance(source, list) and source:
                        names = (
                            list(source[0])
                            if isinstance(source[0], dict)
                            else source[0]
                            if isinstance(source[0], list) and dataset.get("sourceHeader") is True
                            else []
                        )
                    if isinstance(series.get("encode"), dict):
                        for channel, encoding in series["encode"].items():
                            for ref in encoding if isinstance(encoding, list) else [encoding]:
                                if isinstance(ref, str) and names and ref not in names:
                                    error(
                                        path + ".encode." + channel,
                                        "Encoded dimension is not present in the dataset.",
                                    )
                                if (
                                    isinstance(ref, int)
                                    and not isinstance(ref, bool)
                                    and names
                                    and (ref < 0 or ref >= len(names))
                                ):
                                    error(
                                        path + ".encode." + channel,
                                        "Encoded dimension index is outside the dataset.",
                                    )
                    if (
                        names
                        and isinstance(source, list)
                        and source
                        and isinstance(source[0], dict)
                    ):
                        if any(
                            not isinstance(row, dict)
                            or any(name not in row for name in names if isinstance(name, str))
                            for row in source
                        ):
                            warn(
                                path,
                                "Some dataset records omit declared dimensions; confirm intended missing values.",
                            )
                continue
            data = direct if isinstance(direct, list) else []
            values = [_value(item) for item in data]
            if (
                kind in {"line", "bar", "pictorialBar"}
                and coord == "cartesian2d"
                and all(not isinstance(v, list) for v in values)
            ):
                for key, axis in axes.items():
                    if (
                        axis.get("type") == "category"
                        and isinstance(axis.get("data"), list)
                        and len(axis["data"]) != len(data)
                    ):
                        error(
                            path + ".data",
                            f"Scalar observation count does not match {key} categories.",
                        )

            for di, value in enumerate(values):
                dp = f"{path}.data[{di}]"
                if kind == "lines":
                    coords = data[di].get("coords") if isinstance(data[di], dict) else data[di]
                    if (
                        not isinstance(coords, list)
                        or len(coords) < 2
                        or any(
                            not isinstance(c, list) or len(c) != 2 or not all(_number(v) for v in c)
                            for c in coords
                        )
                    ):
                        error(
                            dp, "2D routes need coords containing at least two numeric [x,y] pairs."
                        )
                if value is None:
                    continue
                if kind in {"boxplot", "candlestick"}:
                    count = 5 if kind == "boxplot" else 4
                    if (
                        not isinstance(value, list)
                        or len(value) < count
                        or not all(_number(v) for v in value[:count])
                    ):
                        error(dp, f"{kind} requires {count} numeric summary values.")
                    elif kind == "boxplot" and value[:5] != sorted(value[:5]):
                        error(dp, "Boxplot values must be ordered low, Q1, median, Q3, high.")
                    elif kind == "candlestick" and not (
                        value[2] <= min(value[0], value[1]) <= max(value[0], value[1]) <= value[3]
                    ):
                        error(
                            dp,
                            "Candlestick low/high must bound open/close in [open,close,low,high] order.",
                        )
                if kind == "radar" and (
                    not isinstance(value, list) or len(value) != len(indicators)
                ):
                    error(dp, "Radar value count does not match indicator count.")
                elif kind == "radar" and not all(v is None or _number(v) for v in value):
                    error(
                        dp, "Radar measurements must be finite numbers or explicit missing values."
                    )
                if (
                    kind == "parallel"
                    and dims
                    and all(isinstance(d, int) and not isinstance(d, bool) for d in dims)
                    and (not isinstance(value, list) or len(value) <= max(dims))
                ):
                    error(dp, "Parallel row does not cover its axis dimensions.")
                if kind in {"pie", "funnel"} and (not _number(value) or value < 0):
                    error(dp, "Part/stage values must be nonnegative finite numbers.")
                if kind in {"scatter", "effectScatter"} and (
                    not isinstance(value, list) or len(value) < 2
                ):
                    error(dp, "Scatter points need at least x and y dimensions.")
                if kind == "themeRiver" and (
                    not isinstance(value, list)
                    or len(value) != 3
                    or _stamp(value[0]) is None
                    or not _number(value[1])
                    or value[1] < 0
                    or not isinstance(value[2], str)
                ):
                    error(dp, "Theme-river rows must be [time,nonnegativeValue,seriesName].")
                if kind == "heatmap" and coord == "cartesian2d":
                    if not isinstance(value, list) or len(value) < 3:
                        error(dp, "Cartesian heatmap cells need [xIndex,yIndex,value].")
                    else:
                        for dim, key in enumerate(("xAxis", "yAxis")):
                            categories = axes.get(key, {}).get("data")
                            index = value[dim]
                            if isinstance(categories, list) and (
                                not isinstance(index, int)
                                or isinstance(index, bool)
                                or index < 0
                                or index >= len(categories)
                            ):
                                error(dp, f"Heatmap {key} index is outside the category array.")
                        if value[2] is not None and not _number(value[2]):
                            error(dp, "Heatmap magnitude must be a finite number or null.")
                if (
                    kind == "heatmap"
                    and coord == "calendar"
                    and (not isinstance(value, list) or len(value) != 2 or _stamp(value[0]) is None)
                ):
                    error(dp, "Calendar heatmap cells need [date,value].")
            if kind == "line" and axes.get("xAxis", {}).get("type") == "time":
                times = [_stamp(v[0]) for v in values if isinstance(v, list) and len(v) >= 2]
                if len(times) != len(values):
                    error(path + ".data", "Time lines need explicit [time,value] observations.")
                elif any(t is None for t in times):
                    warn(
                        path + ".data",
                        "Some timestamp formats are not recognized by this linter; verify parsing in the host.",
                    )
                elif times != sorted(times):
                    error(path + ".data", "Time observations are not sorted.")
            if kind == "heatmap":
                maps = _entries(variant.get("visualMap"))
                if not maps:
                    warn(path, "Heatmap has no visualMap; confirm intended direct item coloring.")
                expected = 1 if coord == "calendar" else 2 if coord == "cartesian2d" else None
                for mi, mapping in enumerate(maps):
                    targets = mapping.get("seriesIndex")
                    applies = (
                        targets is None
                        or targets == si
                        or isinstance(targets, list)
                        and si in targets
                    )
                    if (
                        applies
                        and expected is not None
                        and "dimension" in mapping
                        and mapping["dimension"] != expected
                    ):
                        warn(
                            f"{prefix}.visualMap[{mi}].dimension",
                            f"Heatmap values are conventionally dimension {expected}; verify this mapping.",
                        )
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="Option JSON files, or directories containing option JSON files.",
    )
    parser.add_argument("--target", choices=["streamlit", "echarts"], default="streamlit")
    parser.add_argument("--echarts-major", type=int, choices=[5, 6], default=6)
    args = parser.parse_args(argv)
    files: list[Path] = []
    for path in args.paths:
        if path.is_dir():
            files.extend(sorted(path.rglob("*.json")))
        elif path.is_file():
            files.append(path)
        else:
            parser.error(f"Path does not exist: {path}")
    files = list(dict.fromkeys(files))
    if not files:
        parser.error("No option JSON files found.")
    bad = warnings = 0
    for path in files:
        try:
            issues = validate_option(
                load_option(path.read_text(encoding="utf-8")), args.target, args.echarts_major
            )
        except (OSError, ValueError, RecursionError) as exc:
            issues = [Issue("ERROR", "$", f"Cannot read/parse strict JSON: {exc}")]
        bad += any(i.level == "ERROR" for i in issues)
        warnings += sum(i.level == "WARN" for i in issues)
        for issue in issues:
            print(f"{issue.level} {path} {issue.path}: {issue.message}")
    print(
        f"Checked {len(files)} option(s): {bad} failed, {warnings} warning(s). Focused lint only; rendering is not tested."
    )
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
