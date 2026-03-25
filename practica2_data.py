from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path


SECTION_NAMES = (
    "INTERSECTIONS",
    "PATHS",
    "FIXED",
    "PROHIBITED",
    "path_flow",
    "path_intersections",
    "intersection_neighborhood",
)

EXPECTED_COUNTS = {
    "intersections": 457,
    "paths": 42,
    "path_intersections": 542,
}


@dataclass
class RawDataset:
    intersections: list[int]
    paths: list[int]
    fixed: list[int]
    prohibited: list[int]
    path_flow: dict[int, str]
    path_intersections: list[tuple[int, int]]
    raw_neighbors: list[tuple[int, int]]


def parse_raw_data(path: Path) -> RawDataset:
    dataset = RawDataset(
        intersections=[],
        paths=[],
        fixed=[],
        prohibited=[],
        path_flow={},
        path_intersections=[],
        raw_neighbors=[],
    )
    mode = None

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue

        if line in SECTION_NAMES:
            mode = line
            continue

        if mode is None:
            raise ValueError(f"Linea {line_number}: dato fuera de seccion reconocida: {line!r}")

        parts = line.split()
        if mode == "INTERSECTIONS":
            dataset.intersections.extend(_parse_ints(parts, line_number))
        elif mode == "PATHS":
            dataset.paths.extend(_parse_ints(parts, line_number))
        elif mode == "FIXED":
            dataset.fixed.extend(_parse_ints(parts, line_number))
        elif mode == "PROHIBITED":
            dataset.prohibited.extend(_parse_ints(parts, line_number))
        elif mode == "path_flow":
            if len(parts) != 2:
                raise ValueError(f"Linea {line_number}: path_flow debe tener 2 columnas.")
            path_id = _parse_int(parts[0], line_number)
            if path_id in dataset.path_flow:
                raise ValueError(f"Linea {line_number}: flujo duplicado para el camino {path_id}.")
            _parse_positive_decimal(parts[1], line_number)
            dataset.path_flow[path_id] = parts[1]
        elif mode == "path_intersections":
            if len(parts) != 2:
                raise ValueError(f"Linea {line_number}: path_intersections debe tener 2 columnas.")
            dataset.path_intersections.append(
                (_parse_int(parts[0], line_number), _parse_int(parts[1], line_number))
            )
        elif mode == "intersection_neighborhood":
            if len(parts) != 2:
                raise ValueError(
                    f"Linea {line_number}: intersection_neighborhood debe tener 2 columnas."
                )
            dataset.raw_neighbors.append(
                (_parse_int(parts[0], line_number), _parse_int(parts[1], line_number))
            )

    return dataset


def collect_validation_errors(dataset: RawDataset) -> list[str]:
    errors: list[str] = []

    errors.extend(_duplicate_errors("INTERSECTIONS", dataset.intersections))
    errors.extend(_duplicate_errors("PATHS", dataset.paths))
    errors.extend(_duplicate_errors("FIXED", dataset.fixed))
    errors.extend(_duplicate_errors("PROHIBITED", dataset.prohibited))
    errors.extend(_duplicate_errors("path_intersections", dataset.path_intersections))

    intersections = set(dataset.intersections)
    paths = set(dataset.paths)
    fixed = set(dataset.fixed)
    prohibited = set(dataset.prohibited)
    flow_paths = set(dataset.path_flow)

    missing_fixed = sorted(fixed - intersections)
    if missing_fixed:
        errors.append(f"FIXED contiene intersecciones que no existen: {missing_fixed}")

    missing_prohibited = sorted(prohibited - intersections)
    if missing_prohibited:
        errors.append(f"PROHIBITED contiene intersecciones que no existen: {missing_prohibited}")

    overlap = sorted(fixed & prohibited)
    if overlap:
        errors.append(f"FIXED y PROHIBITED se solapan: {overlap}")

    missing_flow = sorted(paths - flow_paths)
    if missing_flow:
        errors.append(f"Hay caminos sin flujo definido: {missing_flow}")

    orphan_flow = sorted(flow_paths - paths)
    if orphan_flow:
        errors.append(f"Hay filas de path_flow para caminos inexistentes: {orphan_flow}")

    referenced_paths = {path_id for path_id, _ in dataset.path_intersections}
    missing_path_rows = sorted(paths - referenced_paths)
    if missing_path_rows:
        errors.append(f"Hay caminos sin intersecciones asociadas: {missing_path_rows}")

    orphan_path_rows = sorted(referenced_paths - paths)
    if orphan_path_rows:
        errors.append(f"Hay filas de path_intersections para caminos inexistentes: {orphan_path_rows}")

    invalid_path_intersections = sorted(
        (path_id, intersection_id)
        for path_id, intersection_id in dataset.path_intersections
        if path_id not in paths or intersection_id not in intersections
    )
    if invalid_path_intersections:
        errors.append(
            "Hay filas de path_intersections con referencias invalidas: "
            f"{invalid_path_intersections[:10]}"
        )

    invalid_neighbors = sorted(
        (left, right)
        for left, right in dataset.raw_neighbors
        if left not in intersections or right not in intersections
    )
    if invalid_neighbors:
        errors.append(
            "Hay filas de intersection_neighborhood con referencias invalidas: "
            f"{invalid_neighbors[:10]}"
        )

    self_neighbors = sorted((left, right) for left, right in dataset.raw_neighbors if left == right)
    if self_neighbors:
        errors.append(f"Hay vecindades reflexivas, lo cual no deberia ocurrir: {self_neighbors[:10]}")

    expected_intersections = EXPECTED_COUNTS["intersections"]
    if len(dataset.intersections) != expected_intersections:
        errors.append(
            f"Se esperaban {expected_intersections} intersecciones y se han leido "
            f"{len(dataset.intersections)}."
        )

    expected_paths = EXPECTED_COUNTS["paths"]
    if len(dataset.paths) != expected_paths:
        errors.append(
            f"Se esperaban {expected_paths} caminos y se han leido {len(dataset.paths)}."
        )

    expected_path_intersections = EXPECTED_COUNTS["path_intersections"]
    if len(dataset.path_intersections) != expected_path_intersections:
        errors.append(
            f"Se esperaban {expected_path_intersections} filas en path_intersections y se han "
            f"leido {len(dataset.path_intersections)}."
        )

    return errors


def normalized_neighbor_pairs(dataset: RawDataset) -> list[tuple[int, int]]:
    return sorted({_normalize_pair(left, right) for left, right in dataset.raw_neighbors})


def build_neighbor_adjacency(dataset: RawDataset) -> dict[int, list[int]]:
    adjacency: dict[int, set[int]] = {}
    for left, right in normalized_neighbor_pairs(dataset):
        adjacency.setdefault(left, set()).add(right)
        adjacency.setdefault(right, set()).add(left)
    return {node: sorted(neighbors) for node, neighbors in adjacency.items()}


def raw_neighbor_symmetry_gaps(dataset: RawDataset) -> list[tuple[int, int]]:
    raw_set = set(dataset.raw_neighbors)
    missing_reverse = {
        _normalize_pair(left, right)
        for left, right in dataset.raw_neighbors
        if (right, left) not in raw_set
    }
    return sorted(missing_reverse)


def fixed_neighbor_conflicts(dataset: RawDataset) -> list[tuple[int, int]]:
    fixed = set(dataset.fixed)
    return [
        (left, right)
        for left, right in normalized_neighbor_pairs(dataset)
        if left in fixed and right in fixed
    ]


def summary(dataset: RawDataset) -> dict[str, int]:
    return {
        "intersections": len(dataset.intersections),
        "paths": len(dataset.paths),
        "fixed": len(dataset.fixed),
        "prohibited": len(dataset.prohibited),
        "path_flow_rows": len(dataset.path_flow),
        "path_intersections_rows": len(dataset.path_intersections),
        "raw_neighbor_rows": len(dataset.raw_neighbors),
        "normalized_neighbor_pairs": len(normalized_neighbor_pairs(dataset)),
        "raw_asymmetric_pairs": len(raw_neighbor_symmetry_gaps(dataset)),
        "fixed_neighbor_conflicts": len(fixed_neighbor_conflicts(dataset)),
    }


def write_ampl_dat(path: Path, dataset: RawDataset) -> None:
    lines: list[str] = [
        "# Generated from OPT25-26_Datos practica 2.txt",
        "",
        _format_scalar_set("INTERSECTIONS", dataset.intersections),
        "",
        _format_scalar_set("PATHS", dataset.paths),
        "",
        _format_scalar_set("FIXED", dataset.fixed),
        "",
        _format_scalar_set("PROHIBITED", dataset.prohibited),
        "",
        "param PATH_FLOW :=",
    ]

    for path_id in dataset.paths:
        lines.append(f"  {path_id} {dataset.path_flow[path_id]}")
    lines.extend([";", "", "set PATH_INTERSECTIONS :="])

    for path_id, intersection_id in dataset.path_intersections:
        lines.append(f"  ({path_id}, {intersection_id})")
    lines.extend([";", "", "set NEIGHBORS :="])

    for left, right in normalized_neighbor_pairs(dataset):
        lines.append(f"  ({left}, {right})")
    lines.extend([";", ""])

    path.write_text("\n".join(lines), encoding="utf-8")


def _duplicate_errors(name: str, values: list[object]) -> list[str]:
    seen: set[object] = set()
    duplicates: list[object] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    if not duplicates:
        return []
    return [f"La seccion {name} contiene duplicados: {duplicates[:10]}"]


def _format_scalar_set(name: str, values: list[int], chunk_size: int = 12) -> str:
    lines = [f"set {name} :="]
    for start in range(0, len(values), chunk_size):
        chunk = " ".join(str(value) for value in values[start : start + chunk_size])
        lines.append(f"  {chunk}")
    lines.append(";")
    return "\n".join(lines)


def _normalize_pair(left: int, right: int) -> tuple[int, int]:
    return (left, right) if left < right else (right, left)


def _parse_int(token: str, line_number: int) -> int:
    try:
        return int(token)
    except ValueError as exc:
        raise ValueError(f"Linea {line_number}: entero invalido {token!r}.") from exc


def _parse_ints(tokens: list[str], line_number: int) -> list[int]:
    return [_parse_int(token, line_number) for token in tokens]


def _parse_positive_decimal(token: str, line_number: int) -> Decimal:
    try:
        value = Decimal(token)
    except InvalidOperation as exc:
        raise ValueError(f"Linea {line_number}: decimal invalido {token!r}.") from exc
    if value <= 0:
        raise ValueError(f"Linea {line_number}: el flujo debe ser estrictamente positivo.")
    return value
