#!/usr/bin/env python3

from pathlib import Path


base_dir = Path(__file__).resolve().parents[1]
raw_data = base_dir / "datos_crudos" / "OPT25-26_Datos práctica 2.txt"
output_dat = base_dir / "ampl" / "practica2.dat"

section_names = [
    "INTERSECTIONS",
    "PATHS",
    "FIXED",
    "PROHIBITED",
    "path_flow",
    "path_intersections",
    "intersection_neighborhood",
]

sections = {name: [] for name in section_names}
current = None

for raw_line in raw_data.read_text(encoding="utf-8").splitlines():
    line = raw_line.strip()

    if not line:
        continue

    if line in sections:
        current = line
        continue

    if current is not None:
        sections[current].append(line)


def split_values(lines):
    values = []
    for line in lines:
        values.extend(line.split())
    return values


def format_set(name, values, per_line=12):
    text = [f"set {name} :="]
    for i in range(0, len(values), per_line):
        text.append("  " + " ".join(values[i : i + per_line]))
    text.append(";")
    return "\n".join(text)


intersections = split_values(sections["INTERSECTIONS"])
paths = split_values(sections["PATHS"])
fixed = split_values(sections["FIXED"])
prohibited = split_values(sections["PROHIBITED"])
path_flow = sections["path_flow"]
path_intersections = sections["path_intersections"]

neighbors = set()
for line in sections["intersection_neighborhood"]:
    a, b = map(int, line.split())
    if a != b:
        neighbors.add((min(a, b), max(a, b)))

neighbors = sorted(neighbors)

text = [
    "# Generated from OPT25-26_Datos practica 2.txt",
    f"# intersections: {len(intersections)}",
    f"# paths: {len(paths)}",
    f"# path_intersections: {len(path_intersections)}",
    f"# neighbors: {len(neighbors)}",
    "",
    format_set("INTERSECTIONS", intersections),
    "",
    format_set("PATHS", paths),
    "",
    format_set("FIXED", fixed),
    "",
    format_set("PROHIBITED", prohibited),
    "",
    "param PATH_FLOW :=",
]

for line in path_flow:
    text.append(f"  {line}")

text.extend([";", "", "set PATH_INTERSECTIONS :="])

for line in path_intersections:
    a, b = line.split()
    text.append(f"  ({a}, {b})")

text.extend([";", "", "set NEIGHBORS :="])

for a, b in neighbors:
    text.append(f"  ({a}, {b})")

text.extend([";", ""])

output_dat.write_text("\n".join(text), encoding="utf-8")

print(f"Fichero generado: {output_dat}")
print(f"Intersections: {len(intersections)}")
print(f"Paths: {len(paths)}")
print(f"Path intersections: {len(path_intersections)}")
print(f"Neighbors: {len(neighbors)}")
