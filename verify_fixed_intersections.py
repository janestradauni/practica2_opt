#!/usr/bin/env python3
"""Check that no FIXED intersection conflicts with another FIXED neighbor."""

from pathlib import Path

from practica2_data import (
    build_neighbor_adjacency,
    collect_validation_errors,
    fixed_neighbor_conflicts,
    parse_raw_data,
)


RAW_DATA_PATH = Path("OPT25-26_Datos práctica 2.txt")
EXAMPLE_NODE = 30


def main() -> int:
    try:
        dataset = parse_raw_data(RAW_DATA_PATH)
    except FileNotFoundError:
        print(f"Error: No se encuentra el archivo '{RAW_DATA_PATH}'.")
        return 1
    except ValueError as exc:
        print(f"Error al parsear los datos crudos: {exc}")
        return 1

    errors = collect_validation_errors(dataset)
    if errors:
        print("Se han detectado errores de consistencia en el dataset:")
        for error in errors:
            print(f"- {error}")
        return 1

    fixed = sorted(dataset.fixed)
    adjacency = build_neighbor_adjacency(dataset)
    conflicts = fixed_neighbor_conflicts(dataset)

    print(f"Total de nodos FIXED encontrados: {len(fixed)}")
    print(f"Nodos FIXED: {fixed}")
    print("-" * 50)

    if EXAMPLE_NODE in adjacency:
        neighbors = adjacency[EXAMPLE_NODE]
        shared = sorted(set(neighbors).intersection(dataset.fixed))
        print(
            f"Ejemplo documentado para el informe: el nodo '{EXAMPLE_NODE}' "
            f"tiene como vecinos a: {neighbors}."
        )
        print(f"Elementos comunes con el conjunto FIXED: {shared}")

    print("-" * 50)
    if conflicts:
        print(
            "PELIGRO: se han encontrado conflictos entre nodos FIXED vecinos entre si: "
            f"{conflicts}"
        )
        return 1

    print("EXITO: 0 conflictos encontrados.")
    print("El modelo no sufrira infactibilidad intrinseca en el apartado B.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
