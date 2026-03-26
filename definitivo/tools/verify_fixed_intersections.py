from pathlib import Path


raw_data = Path(__file__).resolve().parents[1] / "datos_crudos" / "OPT25-26_Datos práctica 2.txt"

fixed = set()
neighbors = {}
mode = ""

for raw_line in raw_data.read_text(encoding="utf-8").splitlines():
    line = raw_line.strip()

    if not line:
        continue

    if line == "FIXED":
        mode = "FIXED"
        continue

    if line == "intersection_neighborhood":
        mode = "NEIGHBORS"
        continue

    if line in {"INTERSECTIONS", "PATHS", "PROHIBITED", "path_flow", "path_intersections"}:
        mode = ""
        continue

    if mode == "FIXED":
        fixed.update(map(int, line.split()))

    elif mode == "NEIGHBORS":
        a, b = map(int, line.split())
        neighbors.setdefault(a, set()).add(b)
        neighbors.setdefault(b, set()).add(a)

conflicts = []
for node in sorted(fixed):
    for neighbor in sorted(neighbors.get(node, set())):
        if neighbor in fixed and node < neighbor:
            conflicts.append((node, neighbor))

print(f"FIXED: {sorted(fixed)}")
print("-" * 50)
print(f"Vecinos de 30: {sorted(neighbors.get(30, []))}")
print("-" * 50)

if conflicts:
    print(f"Hay conflictos entre nodos FIXED vecinos: {conflicts}")
else:
    print("No hay conflictos entre nodos FIXED vecinos.")
    print("El apartado B no es infactible de partida por esta razon.")
