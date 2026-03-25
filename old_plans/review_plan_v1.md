# Revisión Crítica de [plan_v1.md](file:///home/adri/Desktop/uni/OPT/practica2/plan_v1.md)

> [!NOTE]
> Revisión desde la perspectiva de un profesor de optimización que evalúa un trabajo de universitario. El plan tiene buena estructura pero contiene errores conceptuales, sobreingeniería, y carencias en la formulación matemática.

---

## 🔴 Errores y Problemas Graves

### 1. La restricción de detección del Apartado A está MAL formulada

Tu plan dice:

```
sum{(p,i) in PATH_INTERSECTIONS: p = pp} x[i] >= 2 * y[pp]
```

Esto es **necesario pero no suficiente**. Esta restricción sólo impone que si `y[p]=1`, entonces al menos 2 sensores del camino deben estar activos. Pero **no impide** que `y[p]=0` cuando sí hay 2 o más sensores en el camino — es decir, la formulación es correcta como relajación porque la función objetivo maximiza flujo, así que el solver siempre preferirá poner `y[p]=1` si puede. **Sin embargo**, necesitas también la restricción que vincule `y[p]` por arriba:

```
y[p] <= sum{(p,i) in PATH_INTERSECTIONS: p = pp} x[i] / 2
```

O alternativamente, la más sencilla que se suele usar en clase:

```
y[p] <= x[i]  para cada intersección i del camino p (pero esto no captura "al menos 2")
```

En realidad, piénsalo mejor: como la función objetivo tiene coeficientes `PATH_FLOW[p] * y[p]` con flujos positivos, y maximizas, **no pasa nada** — el solver siempre pondrá `y[p]=1` si cumple la restricción. Así que **la restricción `≥ 2*y[p]` es suficiente en este caso**. Pero en tu plan deberías **explicar explícitamente por qué** eso basta, no dejarlo como supuesto al final. Un profesor esperaría esa justificación en el PDF.

> [!IMPORTANT]
> **Veredicto**: La formulación es técnicamente correcta pero la justificación está escondida al final como "supuesto". Debería estar integrada en la sección del modelo.

---

### 2. La restricción del Apartado B `x[i] + x[k] <= 1` es CORRECTA, pero hay un matiz

Tu plan dice:

> No usar la versión agregada `x[i] + sum vecinos <= 1`, porque sería más fuerte de lo pedido

Esto es **correcto**, bien pensado. La restricción por pares es exactamente lo que pide el enunciado. Sin embargo, hay un problema que no mencionas:

> [!WARNING]
> **Debes verificar que ninguna intersección FIJA tiene otra intersección FIJA como vecina.** Si dos intersecciones fijas están a menos de 300m entre sí en el dataset, el modelo B será **infactible** directamente. Tu plan menciona esto vagamente en pruebas ("no introduce infeasibilidad inmediata con las intersecciones fijas") pero no lo identifica como un chequeo crítico del preprocesado.

---

### 3. El `.run` para NEOS está MAL descrito

Tu plan dice:

> B para NEOS, sin `model` ni `data`, solo `solve` y la salida final pedida.

Esto es confuso pero se acerca a lo correcto. En NEOS, cuando subes un problema AMPL, subes **tres ficheros**: `.mod`, `.dat` y `.run`. El fichero `.run` que subes a NEOS **no debe tener** las líneas `model`, `data`, ni `option` de solver, porque NEOS lo gestiona. Pero **sí** debe tener `solve;` y los `display`/`printf` de salida. Tu descripción es ambigua — parece que dices que el `.run` solo tiene `solve`, pero **también necesita los displays**.

**Corrección**:
```ampl
# practica_b.run (para NEOS)
solve;
display x;
display y;
display total_flow;
# O los printf que quieras para la salida
```

---

### 4. Falta la formulación matemática formal

El enunciado pide explícitamente:

> *"Formulación matemática de los modelos de programación lineal entero propuestos"*

Tu plan habla de restricciones en pseudocódigo AMPL pero **no presenta la formulación matemática formal** con notación de conjuntos, parámetros, variables, función objetivo y restricciones. Esto es lo que tiene que ir en el PDF y debería estar planificado. Un ejemplo de lo que se espera:

**Conjuntos:**
- $I$ = conjunto de intersecciones
- $P$ = conjunto de caminos  
- $I_p \subseteq I$ = intersecciones del camino $p$
- $F \subseteq I$ = intersecciones fijas
- $Q \subseteq I$ = intersecciones prohibidas

**Parámetros:**
- $f_p$ = flujo del camino $p$

**Variables:**
- $x_i \in \{0,1\}$ = 1 si se coloca sensor en intersección $i$
- $y_p \in \{0,1\}$ = 1 si el camino $p$ está sensorizado

**Función objetivo:**
$$\max \sum_{p \in P} f_p \cdot y_p$$

**Restricciones:**
$$\sum_{i \in I} x_i \leq 15$$
$$x_i = 1 \quad \forall i \in F$$
$$x_i = 0 \quad \forall i \in Q$$
$$\sum_{i \in I_p} x_i \geq 2 \cdot y_p \quad \forall p \in P$$

> [!CAUTION]
> Sin esta formulación formal el ejercicio estaría incompleto para la entrega.

---

## 🟡 Sobreingeniería para un trabajo universitario

### 5. Python para parsear datos y validar soluciones: INNECESARIO

Tu plan propone dos scripts Python:
- `build_dat.py`: parser del [.txt](file:///home/adri/Desktop/uni/OPT/practica2/OPT25-26_Datos%20pr%C3%A1ctica%202.txt) para generar el `.dat`
- `check_solution.py`: validador de soluciones

**Problema**: Esto es sobreingeniería para una práctica de optimización. Un universitario haría lo siguiente:

1. **Escribir el `.dat` copiando/transformando a mano (o con un script simple de 20 líneas)** los datos del [.txt](file:///home/adri/Desktop/uni/OPT/practica2/OPT25-26_Datos%20pr%C3%A1ctica%202.txt) al formato AMPL.
2. **Verificar la solución visualmente** mirando la salida del solver.

Un profesor vería los scripts Python y pensaría: "esto no lo ha hecho un estudiante, lo ha generado una IA". **No es que esté mal**, pero es sospechosamente profesional.

> [!TIP]
> **Recomendación**: Quita los scripts Python del entregable. Si quieres usarlos internamente para verificar, vale, pero **no los entregues**. El entregable debería ser: 2 `.mod`, 1 `.dat`, 2 `.run` y el PDF. Exactamente lo que pide el enunciado.

---

### 6. La "salida estandarizada" es innecesaria

Tu plan propone estandarizar la salida con formato tipo:
```
SENSOR <id>
DETECTED_PATH <id>
OBJECTIVE <valor>
```

Esto no lo pide el enunciado. La salida de AMPL con `display` es perfectamente aceptable. De nuevo, sobreingeniería.

---

## 🟡 Cosas que faltan o están incompletas

### 7. No mencionas el formato concreto del `.dat`

Tu plan lista las estructuras AMPL (`set INTERSECTIONS`, `param PATH_FLOW`, etc.) pero no muestra **cómo se vería el `.dat` real**. Esto es importante porque la transformación del [.txt](file:///home/adri/Desktop/uni/OPT/practica2/OPT25-26_Datos%20pr%C3%A1ctica%202.txt) al `.dat` es la parte más "manual" del trabajo. Ejemplo esperado:

```ampl
set INTERSECTIONS := 73701 73702 73703 ... ;

set PATHS := 1439 1441 1442 ... ;

set FIXED := 30 78 44628 45173 45481 45555 45787 49180 ;

set PROHIBITED := 54977 73703 68 ;

param PATH_FLOW :=
1439  3.01909319
1441  0.201561508
...
;

set PATH_INTERSECTIONS :=
(1439, 5)
(1439, 88)
...
;
```

### 8. No mencionas `intersection_neighborhood` correctamente para el `.dat`

Para el apartado B, necesitas representar la vecindad. Pero tu plan dice:

> `set CONFLICTS within {INTERSECTIONS, INTERSECTIONS};`

La vecindad del fichero ya viene como pares `(i, j)`. Tu idea de "normalizar como conjunto no dirigido" está bien conceptualmente, pero la forma más natural en AMPL sería:

```ampl
set NEIGHBORS within {INTERSECTIONS, INTERSECTIONS};
```

Y luego la restricción:
```ampl
subject to no_overlap {(i,j) in NEIGHBORS}: x[i] + x[j] <= 1;
```

Llamarlo `CONFLICTS` está bien, pero asegúrate de que sea simétrico: si `(i,j)` está, **puedes deduplicar** guardando solo pares con `i < j` para evitar restricciones duplicadas (cada par generaría dos restricciones idénticas: `x[i]+x[j]<=1` y `x[j]+x[i]<=1`).

### 9. No mencionas qué solver usar

El plan debería especificar: "Apartado A: CPLEX o Gurobi con AMPL local. Apartado B: NEOS con CPLEX (o similar)". Tú lo dejas vago.

### 10. Falta planificación del PDF

El entregable más importante es el PDF. Tu plan apenas menciona "PDF con formulación matemática, explicación breve, solver usado y resultados". Pero el enunciado pide:
- Nombre, apellidos y DNIs
- Formulación matemática de **ambos** modelos
- Código AMPL (copiar .mod y .dat)
- Descripción de la implementación
- Solución óptima: **localización de sensores** y **flujo total**

---

## 🟢 Cosas que están BIEN

| Aspecto | Comentario |
|---|---|
| Dos `.mod` separados | ✅ Correcto, más limpio que condicionales |
| Restricción por pares en B | ✅ `x[i]+x[j]<=1` es exactamente lo correcto |
| Detección = 2 sensores | ✅ Bien interpretado del enunciado |
| Vecindad simétrica | ✅ Buena observación, el dataset no es 100% simétrico |
| Conteos del dataset verificados | ✅ (457 intersecciones, 42 caminos, etc.) |
| Identificación del límite de NEOS | ✅ Correcto que B excede 500 restricciones |

---

## 📋 Resumen de acciones

| # | Acción | Prioridad |
|---|---|---|
| 1 | Escribir la formulación matemática formal (conjuntos, parámetros, variables, FO, restricciones) para A y B | 🔴 Crítica |
| 2 | Eliminar o reducir drásticamente los scripts Python — no forman parte del entregable | 🟡 Alta |
| 3 | Escribir el `.dat` real mostrando el formato concreto | 🟡 Alta |
| 4 | Corregir/clarificar la descripción del `.run` para NEOS | 🟡 Alta |
| 5 | Añadir verificación de que no hay conflicto entre intersecciones FIJAS en B | 🟡 Alta |
| 6 | Especificar el solver concreto (CPLEX/Gurobi) | 🟢 Media |
| 7 | Deduplicar pares de vecindad (`i<j`) para evitar restricciones redundantes | 🟢 Media |
| 8 | Planificar la estructura del PDF del entregable | 🟢 Media |
| 9 | Eliminar la salida estandarizada — usar `display` normal de AMPL | 🟢 Baja |
| 10 | Justificar formalmente por qué `≥ 2y` basta (FO maximiza → solver pone y=1 siempre que puede) | 🟢 Baja |
