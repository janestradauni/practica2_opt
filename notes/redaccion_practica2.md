# Notas de Redacción Completas — Práctica 2 OPT

> Documento de referencia para la redacción del informe PDF final.
> Cubre: modelo matemático, implementación en código, pipeline de datos, y verificaciones.

---

## 1. Contexto del Problema

Se dispone de una red urbana con **457 intersecciones** y **42 caminos** (rutas vehiculares) que traversan dichas intersecciones. Cada camino tiene un **flujo vehicular** asociado (estrictamente positivo). El objetivo es instalar sensores en intersecciones para detectar el máximo flujo posible, sujeto a restricciones de presupuesto y operativas.

### Datos de entrada

| Concepto                     | Cardinalidad |
|------------------------------|--------------|
| Intersecciones ($I$)         | 457          |
| Caminos ($P$)                | 42           |
| Intersecciones fijas ($F$)   | 8            |
| Intersecciones prohibidas ($Q$) | 3         |
| Asociaciones camino-intersección | 542      |
| Pares de vecindad (normalizados, $N$) | ~1284 |

Las **intersecciones fijas** ($F$) son: `30, 78, 44628, 45173, 45481, 45555, 45787, 49180`.
Las **intersecciones prohibidas** ($Q$) son: `54977, 73703, 68`.

---

## 2. Modelo Matemático — Apartado A

### 2.1. Conjuntos

| Símbolo | Descripción |
|---------|-------------|
| $I$ | Conjunto de todas las intersecciones de la red (457 nodos). |
| $P$ | Conjunto de todos los caminos de la red (42 caminos). |
| $F \subset I$ | Subconjunto de intersecciones de instalación obligatoria (8 nodos). |
| $Q \subset I$ | Subconjunto de intersecciones donde no se puede instalar sensor (3 nodos). |
| $I_p \subset I$ | Intersecciones que componen el camino $p \in P$ (definido por la tabla relacional). |

### 2.2. Parámetros

- $f_p > 0$: flujo vehicular del camino $p \in P$.

### 2.3. Variables de decisión

- $x_i \in \{0, 1\}, \quad \forall i \in I$: Toma valor 1 si se instala sensor en la intersección $i$.
- $y_p \in \{0, 1\}, \quad \forall p \in P$: Toma valor 1 si el camino $p$ se considera detectado.

### 2.4. Función objetivo

Maximizar el flujo total de caminos detectados:

$$\max Z = \sum_{p \in P} f_p \cdot y_p$$

### 2.5. Restricciones

1. **Presupuesto de sensores (máx. 15)**:
   $$\sum_{i \in I} x_i \leq 15$$

2. **Sensores obligatorios** — las intersecciones del conjunto $F$ deben tener sensor:
   $$x_i = 1 \quad \forall i \in F$$

3. **Intersecciones prohibidas** — no se puede instalar sensor en $Q$:
   $$x_i = 0 \quad \forall i \in Q$$

4. **Detección de caminos** — un camino necesita al menos 2 sensores para estar detectado:
   $$\sum_{i \in I_p} x_i \geq 2 \cdot y_p \quad \forall p \in P$$

### 2.6. Justificación: ¿por qué basta con una sola restricción para $y_p$?

Esta es una cuestión clave para la memoria. La restricción (4) solo establece un **límite inferior** sobre la suma de sensores para que $y_p$ pueda ser 1. No hay restricción que fuerce $y_p = 0$ cuando hay menos de 2 sensores *excepto* la propia restricción:

- **Si** $\sum_{i \in I_p} x_i \leq 1$: entonces $2 \cdot y_p \leq 1$, y como $y_p \in \{0,1\}$, la única opción factible es $y_p = 0$.
- **Si** $\sum_{i \in I_p} x_i \geq 2$: la restricción permite $y_p = 0$ o $y_p = 1$. Como la función objetivo es de **maximización** y $f_p > 0$ estrictamente, el solver siempre elegirá $y_p = 1$.

**Conclusión**: no hace falta incluir restricciones tipo Big-M ni penalizaciones adicionales. La combinación de la restricción lineal y la dirección de optimización es suficiente y más eficiente.

---

## 3. Modelo Matemático — Apartado B

Se reutiliza íntegramente el modelo A y se añade:

### 3.1. Conjunto adicional

- $N \subset I \times I$: pares de intersecciones vecinas (a $\leq 300$ m). Se construye normalizado ($i < j$) y sin duplicados.

### 3.2. Restricción adicional

5. **Separación de sensores** — no se puede colocar sensor en dos intersecciones vecinas:
   $$x_i + x_j \leq 1 \quad \forall (i, j) \in N$$

### 3.3. Verificación de factibilidad previa

Antes de resolver el modelo B, se comprueba que las **intersecciones fijas** ($F$) no entren en conflicto con la restricción de vecindad: si dos nodos de $F$ fueran vecinos, el problema sería intrínsecamente infactible. Se ha verificado esto con un script ad hoc (`verify_fixed_intersections.py`) que confirma **0 conflictos**.

Ejemplo documentado: el nodo `30` (fijo) tiene como vecinos: `{31, 32, 45534, 45714, 45874, 46038, 46136, 54972, 74225}` — ninguno pertenece a $F$.

---

## 4. Implementación en AMPL

### 4.1. Fichero `practica2_a.mod` (Apartado A)

```ampl
set INTERSECTIONS;
set PATHS;
set FIXED within INTERSECTIONS;
set PROHIBITED within INTERSECTIONS;
set PATH_INTERSECTIONS within {PATHS, INTERSECTIONS};
set NEIGHBORS within {INTERSECTIONS, INTERSECTIONS};

param PATH_FLOW {PATHS} > 0;

var x {INTERSECTIONS} binary;
var y {PATHS} binary;

maximize total_flow:
    sum {p in PATHS} PATH_FLOW[p] * y[p];

s.t. sensor_budget:
    sum {i in INTERSECTIONS} x[i] <= 15;

s.t. fixed_sensors {i in FIXED}:
    x[i] = 1;

s.t. prohibited_sensors {i in PROHIBITED}:
    x[i] = 0;

s.t. detected_paths {p in PATHS}:
    sum {i in INTERSECTIONS: (p, i) in PATH_INTERSECTIONS} x[i] >= 2 * y[p];
```

**Notas de implementación:**

- Se declara `NEIGHBORS` incluso en el modelo A, aunque no se usa, para poder compartir el mismo fichero `.dat` entre ambos apartados. Esto simplifica la gestión de datos.
- La función objetivo se nombra `total_flow` para que el `.run` pueda hacer `display total_flow` directamente y obtener el valor óptimo.
- La restricción `detected_paths` usa un filtro `(p, i) in PATH_INTERSECTIONS` dentro de la suma, lo que evita iterar sobre todas las 457 intersecciones para cada camino. Solo suma las intersecciones que realmente pertenecen a ese camino.
- `param PATH_FLOW {PATHS} > 0` incorpora directamente la validación de que todos los flujos sean estrictamente positivos; AMPL lanzará un error si algún flujo fuera ≤ 0 al cargar los datos.

### 4.2. Fichero `practica2_b.mod` (Apartado B)

Idéntico al modelo A más una restricción adicional:

```ampl
s.t. separated_sensors {(i, j) in NEIGHBORS}:
    x[i] + x[j] <= 1;
```

### 4.3. Fichero `practica2.dat` (Datos unificados)

Contiene todos los datos en sintaxis nativa AMPL:

- **Sets escalares**: `INTERSECTIONS`, `PATHS`, `FIXED`, `PROHIBITED` — valores separados por espacios.
- **Parámetro**: `PATH_FLOW` — formato `path_id valor_decimal`.
- **Sets 2D (tuplas)**: `PATH_INTERSECTIONS` y `NEIGHBORS` — formato `(id1, id2)` con comas, una tupla por línea.

**Ejemplo de sintaxis AMPL para sets 2D:**
```ampl
set PATH_INTERSECTIONS :=
  (1439, 5)
  (1439, 88)
  ...
;
```

> **Decisión técnica**: Se usa un fichero `.dat` unificado para ambos modelos. El modelo A simplemente ignora `NEIGHBORS` (lo declara pero no lo usa en restricciones).

### 4.4. Ficheros `.run`

**Apartado A (ejecución local)** — `runs/a/cplex.run`:
```ampl
model practica2_a.mod;
data practica2.dat;
option solver cplex;
solve;
display total_flow;
display x;
display y;
```

**Apartado B (NEOS)** — `runs/b/neos.run`:
```ampl
solve;
display total_flow;
display x;
display y;
```

En NEOS, el `.run` no debe cargar modelo ni datos porque estos se suben por separado en la interfaz web. NEOS los incorpora automáticamente.

---

## 5. Pipeline de Datos (Python)

### 5.1. Arquitectura del parser

El preprocesamiento se implementa en dos scripts Python de **uso interno** (no se entregan):

| Fichero | Propósito |
|---------|-----------|
| `practica2_data.py` | Módulo con toda la lógica: parsing, validación, normalización, escritura. |
| `build_ampl_data.py` | CLI que invoca al módulo y genera `practica2.dat`. |

### 5.2. Estructura del módulo `practica2_data.py`

#### Dataclass `RawDataset`

```python
@dataclass
class RawDataset:
    intersections: list[int]
    paths: list[int]
    fixed: list[int]
    prohibited: list[int]
    path_flow: dict[int, str]          # clave=path_id, valor=string decimal
    path_intersections: list[tuple[int, int]]
    raw_neighbors: list[tuple[int, int]]
```

- Los flujos se almacenan como **strings** (no floats) para preservar la precisión decimal exacta del fichero de datos. Se valida que sean decimales positivos usando `Decimal`.

#### Función `parse_raw_data(path)`

1. Lee el fichero línea a línea.
2. Detecta las **7 cabeceras de sección** predefinidas: `INTERSECTIONS`, `PATHS`, `FIXED`, `PROHIBITED`, `path_flow`, `path_intersections`, `intersection_neighborhood`.
3. Cambia de modo según la cabecera actual y parsea cada línea con `str.split()`.
4. Para cada sección, aplica parsing estricto de enteros (`int()`) y decimales (`Decimal()`).
5. Lanza `ValueError` con número de línea si:
   - Aparece un dato fuera de sección.
   - Un entero o decimal no es válido.
   - `path_flow` o `path_intersections` tienen columnas incorrectas.
   - Un flujo es ≤ 0 o está duplicado.

#### Función `collect_validation_errors(dataset)`

Ejecuta una batería de **14 comprobaciones de consistencia** sobre el dataset parseado:

| # | Comprobación | Qué detecta |
|---|-------------|-------------|
| 1 | Duplicados en `INTERSECTIONS` | Intersecciones repetidas |
| 2 | Duplicados en `PATHS` | Caminos repetidos |
| 3 | Duplicados en `FIXED` | Nodos fijos repetidos |
| 4 | Duplicados en `PROHIBITED` | Nodos prohibidos repetidos |
| 5 | Duplicados en `path_intersections` | Tuplas (camino, intersección) repetidas |
| 6 | `FIXED ⊂ INTERSECTIONS` | Nodos fijos no existentes como intersección |
| 7 | `PROHIBITED ⊂ INTERSECTIONS` | Nodos prohibidos no existentes |
| 8 | `FIXED ∩ PROHIBITED = ∅` | Solapamiento entre fijos y prohibidos |
| 9 | Todo camino tiene flujo | Caminos sin flujo definido |
| 10 | Todo flujo referencia camino existente | Flujos huérfanos |
| 11 | Todo camino tiene intersecciones | Caminos sin filas en `path_intersections` |
| 12 | Toda fila de `path_intersections` ref. camino existente | Filas huérfanas |
| 13 | Toda referencia inversa es válida | Intersecciones inexistentes en tuplas |
| 14 | Vecindades no reflexivas | Ningún nodo es vecino de sí mismo |

Adicionalmente, verifica las **cardinalidades exactas** esperadas:
- 457 intersecciones ✅
- 42 caminos ✅
- 542 asociaciones camino-intersección ✅

#### Función `normalized_neighbor_pairs(dataset)`

Normaliza y deduplica los pares de vecindad del fichero crudo:

```python
def _normalize_pair(left, right):
    return (left, right) if left < right else (right, left)

def normalized_neighbor_pairs(dataset):
    return sorted({_normalize_pair(l, r) for l, r in dataset.raw_neighbors})
```

**¿Por qué es necesario?** El fichero de datos crudos no es simétrico: a veces aparece `(A, B)` pero no `(B, A)`, o viceversa. La normalización:
1. Ordena cada par para que siempre sea `(min, max)`.
2. Aplica un `set()` para eliminar duplicados.
3. Ordena el resultado para determinismo en el `.dat`.

Esto garantiza que cada restricción de vecindad `x_i + x_j ≤ 1` se genera exactamente una vez.

#### Función `write_ampl_dat(path, dataset)`

Ensambla y escribe el fichero `.dat` en formato AMPL:
- Sets escalares: se vuelcan en trozos de 12 elementos por línea.
- Sets 2D (`PATH_INTERSECTIONS`, `NEIGHBORS`): se vuelcan como tuplas `(id, id)` una por línea.
- Parámetro `PATH_FLOW`: formato `path_id valor_string`, preservando la precisión decimal original.

### 5.3. Script `build_ampl_data.py`

CLI simple que:
1. Parsea el fichero de datos crudo.
2. Ejecuta las validaciones.
3. Si hay errores, los imprime y aborta (exit 1).
4. Si todo es correcto, genera `practica2.dat` e imprime el resumen de cardinalidades.

```
$ python3 build_ampl_data.py
Fichero AMPL generado en: practica2.dat
intersections: 457
paths: 42
fixed: 8
prohibited: 3
path_flow_rows: 42
path_intersections_rows: 542
raw_neighbor_rows: 2542
normalized_neighbor_pairs: 1284
raw_asymmetric_pairs: 26
fixed_neighbor_conflicts: 0
```

### 5.4. Script `verify_fixed_intersections.py`

Script autónomo de verificación que:
1. Parsea los datos crudos.
2. Ejecuta la validación completa.
3. Construye el grafo de adyacencia completo.
4. Comprueba si alguna pareja de nodos fijos son vecinos.
5. Imprime ejemplo documentable (nodo `30`).

Salida esperada:
```
Total de nodos FIXED encontrados: 8
Nodos FIXED: [30, 78, 44628, 45173, 45481, 45555, 45787, 49180]
--------------------------------------------------
Ejemplo documentado para el informe: el nodo '30' tiene como vecinos a: [31, 32, 45534, 45714, 45874, 46038, 46136, 54972, 74225].
Elementos comunes con el conjunto FIXED: []
--------------------------------------------------
EXITO: 0 conflictos encontrados.
El modelo no sufrira infactibilidad intrinseca en el apartado B.
```

---

## 6. Resultados del Solver — Apartado A

### 6.1. Datos de ejecución

- **Solver**: Gurobi 13.0.0
- **Estado**: `optimal solution`
- **Valor objetivo**: $Z^*_A = 350.7337301$
- **Iteraciones simplex**: 43
- **Nodos de branching**: 1

### 6.2. Sensores instalados (15 de 15)

| # | Intersección | ¿Fija? |
|---|-------------|--------|
| 1 | **5** | No |
| 2 | **30** | ✅ Sí |
| 3 | **78** | ✅ Sí |
| 4 | **20349** | No |
| 5 | **41633** | No |
| 6 | **41970** | No |
| 7 | **44494** | No |
| 8 | **44609** | No |
| 9 | **44628** | ✅ Sí |
| 10 | **45173** | ✅ Sí |
| 11 | **45481** | ✅ Sí |
| 12 | **45555** | ✅ Sí |
| 13 | **45787** | ✅ Sí |
| 14 | **49180** | ✅ Sí |
| 15 | **54839** | No |

- 8 sensores corresponden a nodos FIXED ✅
- 7 sensores son de libre elección del solver

### 6.3. Caminos detectados ($y_p = 1$): 24 de 42

| Camino | Flujo | Camino | Flujo |
|--------|-------|--------|-------|
| 1439 | 3.019 | 1537 | 0.237 |
| 1441 | 0.202 | 1541 | 0.041 |
| 1451 | 1.817 | 1547 | 0.027 |
| 1479 | 3.168 | 1549 | 1.908 |
| 1483 | 0.794 | 1550 | 0.662 |
| 1484 | 0.785 | 1560 | 5.527 |
| 1488 | 29.181 | 1561 | 2.623 |
| 1492 | 7.313 | 1577 | 1.119 |
| 1493 | 7.235 | 1499 | 1.149 |
| 1500 | 0.261 | 1504 | 3.603 |
| 1513 | 261.109 | 1516 | 12.737 |
| 1518 | 4.954 | 1536 | 1.262 |

### 6.4. Verificación de restricciones ✅

| Verificación | Resultado |
|-------------|-----------|
| Solver reporta óptimo | ✅ `optimal solution; objective 350.7337301` |
| $\sum x_i = 15$ | ✅ 15 sensores exactos |
| $x_i = 1 \, \forall i \in F$ | ✅ Los 8 fijos: 30, 78, 44628, 45173, 45481, 45555, 45787, 49180 |
| $x_i = 0 \, \forall i \in Q$ | ✅ 54977=0, 73703=0, 68=0 |
| Detección coherente | ✅ (ver ejemplo abajo) |

**Ejemplo de verificación empírica** — Camino 1513 ($y = 1$):
- Intersecciones del camino: `{44604, 44609, 44616, 44623, 44628, 44635}`
- Sensores activos en esas intersecciones: `44609` y `44628` → **2 sensores** ≥ 2 ✅

**Ejemplo negativo** — Camino 1445 ($y = 0$):
- Intersecciones: `{88, 89, 90, 40948, 44464, 44510, 44515, 44522, 44604, 44609, 44793, 44800, 73720, 74243}`
- Sensor activo: solo `44609` → **1 sensor** < 2, correctamente no detectado ✅

---

## 7. Resultados del Solver — Apartado B

### 7.1. Datos de ejecución

- **Solver**: Gurobi 13.0.0
- **Estado**: `optimal solution`
- **Valor objetivo**: $Z^*_B = 350.1781172$
- **Iteraciones simplex**: 75
- **Nodos de branching**: 1
- **MIP gap**: $5.68 \times 10^{-14}$ (prácticamente cero)

### 7.2. Sensores instalados (15 de 15)

| # | Intersección | ¿Fija? | ¿También en A? |
|---|-------------|--------|-----------------|
| 1 | **5** | No | ✅ |
| 2 | **30** | ✅ Sí | ✅ |
| 3 | **78** | ✅ Sí | ✅ |
| 4 | **41633** | No | ✅ |
| 5 | **41653** | No | ❌ *Nuevo* |
| 6 | **41970** | No | ✅ |
| 7 | **44522** | No | ❌ *Nuevo* |
| 8 | **44609** | No | ✅ |
| 9 | **44628** | ✅ Sí | ✅ |
| 10 | **45173** | ✅ Sí | ✅ |
| 11 | **45481** | ✅ Sí | ✅ |
| 12 | **45555** | ✅ Sí | ✅ |
| 13 | **45787** | ✅ Sí | ✅ |
| 14 | **49180** | ✅ Sí | ✅ |
| 15 | **54839** | No | ✅ |

### 7.3. Caminos detectados ($y_p = 1$): 24 de 42

| Camino | Flujo | Camino | Flujo |
|--------|-------|--------|-------|
| 1445 | 0.088 | 1537 | 0.237 |
| 1451 | 1.817 | 1541 | 0.041 |
| 1479 | 3.168 | 1547 | 0.027 |
| 1483 | 0.794 | 1549 | 1.908 |
| 1484 | 0.785 | 1550 | 0.662 |
| 1488 | 29.181 | 1560 | 5.527 |
| 1492 | 7.313 | 1561 | 2.623 |
| 1493 | 7.235 | 1577 | 1.119 |
| 1499 | 1.149 | 1525 | 2.577 |
| 1500 | 0.261 | 1504 | 3.603 |
| 1513 | 261.109 | 1516 | 12.737 |
| 1518 | 4.954 | 1536 | 1.262 |

### 7.4. Verificación de restricciones ✅

| Verificación | Resultado |
|-------------|-----------|
| Solver reporta óptimo | ✅ `optimal solution; objective 350.1781172` |
| $\sum x_i = 15$ | ✅ 15 sensores exactos |
| $x_i = 1 \, \forall i \in F$ | ✅ Los 8 fijos presentes |
| $x_i = 0 \, \forall i \in Q$ | ✅ 54977=0, 73703=0, 68=0 |
| Separación de vecinos | ✅ Ningún par de nodos activos es vecino |

---

## 8. Análisis Comparativo A vs B

### 8.1. Impacto de la restricción de vecindad

| Métrica | Apartado A | Apartado B | Diferencia |
|---------|-----------|-----------|------------|
| Flujo óptimo ($Z^*$) | 350.7337301 | 350.1781172 | −0.5556129 (−0.16%) |
| Sensores instalados | 15 | 15 | Misma cantidad |
| Caminos detectados | 24 | 24 | Misma cantidad |
| Iteraciones simplex | 43 | 75 | +32 (más complejo) |

### 8.2. Cambios en la selección de sensores

De 15 sensores, **13 son comunes** entre ambos modelos.

| Solo en A | Solo en B |
|-----------|-----------|
| 44494 | 41653 |
| 20349 | 44522 |

**Interpretación**: la restricción de vecindad obligó al solver a reubicar 2 sensores. Los nodos `44494` y `20349` del modelo A son vecinos de algún otro sensor activo, por lo que en B se sustituyeron por `41653` y `44522`.

### 8.3. Cambios en caminos detectados

| Solo detectado en A | Solo detectado en B |
|---------------------|---------------------|
| 1439 (flujo 3.019) | 1445 (flujo 0.088) |
| 1441 (flujo 0.202) | 1525 (flujo 2.577) |

**Interpretación**: Al perder los sensores en 44494 y 20349, los caminos 1439 y 1441 dejan de tener ≥ 2 sensores. En cambio, el nuevo sensor en 44522 habilita la detección de 1445 y 1525. El flujo neto perdido (~3.22 - 2.67 ≈ 0.56) coincide con la diferencia de objetivos.

---

## 9. Solvers Utilizados

| Solver | Uso | Notas |
|--------|-----|-------|
| Gurobi 13.0.0 | Apartados A y B (local) | Solver MILP, usado para la resolución principal |
| CPLEX | Alternativa local | Igualmente válido para cross-checking |
| CBC | Alternativa open-source | Más lento pero funcional |
| HiGHS | Alternativa open-source | Solver LP/MIP moderno |
| NEOS | Apartado B (remoto) | Ejecución vía web si no hay licencias locales |

> **Importante**: `minos` **no sirve** para este problema porque no resuelve problemas binarios MILP (solo LP continuo).

---

## 10. Notas para la Redacción del PDF

### Estructura propuesta del informe

1. **Autores**: Nombre, apellidos, DNI.
2. **Formulación Matemática**: Conjuntos, parámetros, variables, función objetivo y restricciones (Secciones 2 y 3 de este documento).
3. **Código de Implementación**: Código `.mod`, `.dat` y `.run` legible y comentado.
4. **Descripción de la Implementación**: Decisiones técnicas relevantes (ver abajo).
5. **Salida y Soluciones**: Valor óptimo, lista de sensores, interpretación.

### Puntos clave a destacar en la memoria

1. **Decisión de compartir `.dat`**: Un solo fichero de datos para ambos modelos, simplificando la gestión.
2. **Normalización de vecinos**: El fichero crudo no es simétrico; se normalizan los pares a `(min, max)` y se deduplican para garantizar restricciones no redundantes.
3. **Validación exhaustiva pre-solver**: 14 comprobaciones automáticas del dataset antes de generar el `.dat`.
4. **Flujos como strings**: Se preserva la precisión decimal del dato original evitando errores de representación en punto flotante.
5. **Eficiencia de la restricción de detección**: No se necesitan restricciones Big-M gracias a la dirección de optimización.
6. **Verificación de factibilidad para B**: Se comprueba *antes* de ejecutar el solver que ningún par de nodos fijos es vecino.
7. **Reducción mínima del flujo en B**: La restricción de vecindad solo reduce el flujo un 0.16%, indicando que la red permite una buena distribución de sensores incluso con separación obligatoria.
