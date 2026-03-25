#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from practica2_data import collect_validation_errors, parse_raw_data, summary, write_ampl_dat


DEFAULT_INPUT = Path("OPT25-26_Datos práctica 2.txt")
DEFAULT_OUTPUT = Path("practica2.dat")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate practica2.dat for AMPL.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Raw input dataset.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="AMPL dat output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        dataset = parse_raw_data(args.input)
    except FileNotFoundError:
        print(f"Error: no se encuentra el archivo de entrada '{args.input}'.")
        return 1
    except ValueError as exc:
        print(f"Error al parsear los datos crudos: {exc}")
        return 1

    errors = collect_validation_errors(dataset)
    if errors:
        print("No se ha generado el .dat porque hay errores de consistencia:")
        for error in errors:
            print(f"- {error}")
        return 1

    write_ampl_dat(args.output, dataset)

    print(f"Fichero AMPL generado en: {args.output}")
    for key, value in summary(dataset).items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
