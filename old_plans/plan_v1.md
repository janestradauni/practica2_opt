# Plan de implementación: práctica 2 de OPT con AMPL + preprocesado + checker Python

**Resumen**
- Implementar dos modelos AMPL separados, uno para el apartado A y otro para el B, compartiendo un único `.dat` generado automáticamente desde el fichero bruto `OPT25-26_Datos práctica 2.txt`.
- Añadir una capa Python pequeña pero fiable para dos cosas: transformar el fichero de datos al formato de AMPL y validar de forma independiente cualquier solución que salga de AMPL o NEOS.
- Mantener el flujo de trabajo simple: `txt bruto -> .dat AMPL -> solve -> salida estandarizada -> checker Python`.
- Basar el plan en hechos del dataset ya comprobados: 457 intersecciones, 42 caminos, 542 pares camino-intersección, 2536 relaciones de vecindad, 499 variables binarias en el apartado A, y conflicto claro con la licencia estudiantil en el apartado B.

**Cambios de implementación**
- Usar un parser Python para leer el `.txt` original, tolerando saltos de línea Windows y validando que todas las referencias sean coherentes.
- Generar un `.dat` común con estas estructuras:
  - `set INTERSECTIONS;`
  - `set PATHS;`
  - `set FIXED within INTERSECTIONS;`
  - `set PROHIBITED within INTERSECTIONS;`
  - `param PATH_FLOW{PATHS} >= 0;`
  - `set PATH_INTERSECTIONS within {PATHS, INTERSECTIONS};`
  - `set CONFLICTS within {INTERSECTIONS, INTERSECTIONS};` para el apartado B.
- Normalizar `CONFLICTS` como conjunto no dirigido y sin duplicados. Esto es importante porque la vecindad del fichero bruto no es perfectamente simétrica; el modelo debe imponer incompatibilidad física entre dos sensores aunque el par venga solo en un sentido.
- Modelo A:
  - Variables binarias `x[i]` para sensores y `y[p]` para caminos detectados.
  - Objetivo `maximize total_flow: sum{p in PATHS} PATH_FLOW[p] * y[p];`
  - Restricción de presupuesto `sum{i in INTERSECTIONS} x[i] <= 15;`
  - Restricciones de fijas y prohibidas con igualdad.
  - Restricción de detección `sum{(p,i) in PATH_INTERSECTIONS: p = pp} x[i] >= 2 * y[pp];`
- Modelo B:
  - Reutiliza todo lo anterior.
  - Añade solo restricciones por par conflictivo: `x[i] + x[k] <= 1` para cada `(i,k)` en `CONFLICTS`.
  - No usar la versión agregada `x[i] + sum vecinos <= 1`, porque sería más fuerte de lo pedido y podría eliminar soluciones válidas.
- Preparar dos `.run`:
  - A local, cargando modelo y datos y resolviendo con el solver disponible.
  - B para NEOS, sin `model` ni `data`, solo `solve` y la salida final pedida.
- Estandarizar la salida de ambos `.run` para que el checker la pueda leer sin depender del formato del solver. La salida debe imprimir líneas del estilo:
  - `SENSOR <id>`
  - `DETECTED_PATH <id>`
  - `OBJECTIVE <valor>`

**Interfaces y artefactos**
- `build_dat.py`
  - Entrada: fichero bruto de la práctica.
  - Salida: `.dat` de AMPL ya listo para A y B.
  - Validaciones: secciones presentes, ids consistentes, sin referencias fuera de conjunto, sin solape entre `FIXED` y `PROHIBITED`.
- `check_solution.py`
  - Entrada: salida estandarizada de AMPL/NEOS o, como modo alternativo, una lista simple de sensores seleccionados.
  - Comprobaciones:
    - máximo 15 sensores
    - todas las fijas activadas
    - ninguna prohibida activada
    - conflictos de proximidad en el apartado B
    - caminos detectados correctamente si tienen al menos 2 intersecciones con sensor
    - flujo total recalculado e igualdad con el objetivo declarado, si viene en la salida
  - Salida: informe corto de validez y resumen del flujo captado.
- Entregable final:
  - dos `.mod`
  - un `.dat`
  - dos `.run`
  - los dos scripts Python
  - PDF con formulación matemática, explicación breve, solver usado y resultados

**Plan de pruebas**
- Probar el parser con los conteos esperados del dataset.
- Probar que el generador produce un `.dat` que representa exactamente los 42 caminos y los 542 pares camino-intersección.
- Probar que `CONFLICTS` queda sin pares duplicados ni auto-conflictos y que no introduce infeasibilidad inmediata con las intersecciones fijas.
- Probar el checker con casos manuales pequeños:
  - solución con más de 15 sensores
  - solución que omite una fija
  - solución con una prohibida
  - solución con un par de sensores demasiado cercanos en B
  - camino con 1 sensor no detectado
  - camino con 2 sensores detectado
- Prueba extremo a extremo del apartado A: resolver, pasar la salida al checker y verificar que el flujo recalculado coincide.
- Prueba extremo a extremo del apartado B: repetir el mismo proceso con la salida de NEOS.

**Supuestos y decisiones por defecto**
- Se usarán dos modelos `.mod` separados para simplificar la explicación en el PDF y evitar condicionales innecesarios en AMPL.
- El checker Python será de validación, no un solucionador alternativo del problema.
- La vecindad se tratará como incompatibilidad simétrica por interpretación física del enunciado.
- La restricción `sum sensores del camino >= 2*y` es suficiente porque todos los flujos del dataset son estrictamente positivos.
- El entorno actual no tiene `ampl` instalado, así que la resolución real se asume en tu instalación de AMPL y en NEOS para el apartado B.
