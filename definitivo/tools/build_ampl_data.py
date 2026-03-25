#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from practica2_data import collect_validation_errors, parse_raw_data, summary, write_ampl_dat


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = BASE_DIR / "datos_crudos" / "OPT25-26_Datos práctica 2.txt"
DEFAULT_OUTPUT = BASE_DIR / "ampl" / "practica2.dat"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genera el practica2.dat definitivo para AMPL.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Fichero crudo de entrada.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Fichero .dat de salida.")
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
