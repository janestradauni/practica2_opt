# Notas de Redaccion - Practica 2 OPT

## Estado general

- Dataset crudo validado y convertido a AMPL.
- Cardinalidades verificadas:
  - Intersections: 457
  - Paths: 42
  - Path intersections: 542
- No hay conflictos entre nodos FIXED vecinos para el apartado B.

## Apartado A

### Modelo

- Variables binarias:
  - `x[i]`: 1 si se instala sensor en la interseccion `i`
  - `y[p]`: 1 si el camino `p` queda detectado
- Objetivo:
  - Maximizar el flujo total detectado
- Restricciones:
  - Maximo 15 sensores
  - Todas las intersecciones FIXED deben llevar sensor
  - Todas las PROHIBITED deben quedar a 0
  - Un camino solo puede contar como detectado si tiene al menos 2 sensores

### Verificaciones

- Comprobar que el solver devuelve estado optimo.
- Comprobar que `sum x[i] = 15`.
- Comprobar que `x[i] = 1` para todos los nodos FIXED.
- Comprobar que `x[i] = 0` para todos los nodos PROHIBITED.
- Comprobar que el valor de `total_flow` coincide entre solvers MILP.

### Resultado A

- Flujo optimo observado: `350.7337301`
- Nota:
  - Puede haber soluciones optimas alternativas con el mismo flujo total y distinta seleccion de sensores.

### Sensores elegidos en una solucion optima

- Rellenar con la solucion final que querais incluir en la memoria.

## Apartado B

### Modelo

- Se reutiliza el modelo A.
- Se anade el conjunto `NEIGHBORS`.
- Restriccion adicional:
  - `x[i] + x[j] <= 1` para todo `(i,j)` en `NEIGHBORS`.

### Verificaciones

- Comprobar que no hay conflicto previo entre nodos FIXED vecinos.
- Comprobar que el solver devuelve estado optimo o, si procede, que NEOS encuentra optimo.
- Comprobar que ninguna pareja de `NEIGHBORS` tiene ambos extremos con sensor.

### Resultado B

- Pendiente de resolver y documentar.

## Entregables

- `practica2_a.mod`
- `practica2_b.mod`
- `practica2.dat`
- `runs/a/...`
- `runs/b/...`
- Informe PDF

## Observaciones utiles

- `minos` no sirve para este problema porque no resuelve binarias MILP.
- Solvers adecuados: `gurobi`, `cplex`, `cbc`, `highs`.
