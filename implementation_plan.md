# Plan Definitivo: Práctica 2 de OPT (Red de Sensorización)

Este documento contiene el plan definitivo para resolver la Práctica 2 de la asignatura de Optimización, teniendo en cuenta el enunciado original y todas las correcciones señaladas en revisiones previas. Está diseñado para garantizar una nota máxima a nivel universitario, combinando rigor matemático, simplicidad en el entregable y robustez en la ejecución.

## 1. Formulación Matemática Formal

### 1.1. Modelo para el Apartado A

**Conjuntos:**
- $I$: conjunto de todas las intersecciones de la red.
- $P$: conjunto de todos los caminos de la red.
- $F \subset I$: subconjunto de intersecciones fijas (obligatorias).
- $Q \subset I$: subconjunto de intersecciones prohibidas.
- $I_p \subset I$: subconjunto de intersecciones que forman parte del camino $p \in P$.

**Parámetros:**
- $f_p$: flujo de vehículos del camino $p \in P$ (estrictamente positivo).

**Variables de decisión:**
- $x_i \in \{0, 1\} \quad \forall i \in I$: Toma valor 1 si se instala un sensor en la intersección $i$, y 0 en caso contrario.
- $y_p \in \{0, 1\} \quad \forall p \in P$: Toma valor 1 si el camino $p$ cuenta como detectado, y 0 en caso contrario.

**Función objetivo:**
Maximizar el flujo total de los caminos detectados:
$$\max Z = \sum_{p \in P} f_p \cdot y_p$$

**Restricciones:**
1. **Límite de presupuesto:** Se pueden instalar como máximo 15 sensores.
   $$\sum_{i \in I} x_i \leq 15$$
2. **Intersecciones fijas:** Se debe instalar un sensor obligatoriamente en todas las intersecciones del conjunto $F$.
   $$x_i = 1 \quad \forall i \in F$$
3. **Intersecciones prohibidas:** No se puede instalar ningún sensor en las intersecciones del conjunto $Q$.
   $$x_i = 0 \quad \forall i \in Q$$
4. **Detección de caminos:** Para que un camino $p$ se considere detectado ($y_p=1$), al menos 2 de sus intersecciones deben tener sensor.
   $$\sum_{i \in I_p} x_i \geq 2 \cdot y_p \quad \forall p \in P$$

**Justificación de suficiencia para la detección de caminos:**
Dado que la función objetivo busca maximizar el flujo total y todos los flujos $f_p$ correspondientes a los caminos son valores estrictamente positivos, el solver siempre estará incentivado a asignar $y_p = 1$ siempre que la región factible lo permita. 
* Si un camino cuenta con 0 o 1 sensores activos instalados ($\sum_{i \in I_p} x_i \leq 1$), la inecuación descrita fuerza matemáticamente a que $2 \cdot y_p \le 1$. Dado que $y_p \in \{0, 1\}$, la única opción factible es que $y_p = 0$.
* Si el camino tiene 2 o más sensores, la restricción permite tanto $y_p = 0$ como $y_p = 1$. Gracias a la naturaleza maximizadora de la función objetivo, el solver lógicamente y de forma natural empujará la variable a $y_p = 1$. 
Por este motivo, no es necesario incluir ninguna otra restricción o penalización *Big-M* para forzar a 0 la variable $y_p$ cuando no hay sensores suficientes; la combinación de la restricción y la dirección de optimización es suficiente y muy eficiente.

---

### 1.2. Modelo para el Apartado B

Se reutilizan la función objetivo y las 4 restricciones del Apartado A, añadiendo lo siguiente:

**Conjuntos Adicionales:**
- $N \subset I \times I$: conjunto de pares de intersecciones $(i, j)$ que son vecinas (se encuentran a $\le 300$ m). Para evitar restricciones duplicadas e ineficientes, el conjunto $N$ se construye de manera simétrica y deduplicada, garantizando que siempre se cumpla $i < j$.

**Verificación de factibilidad (Intersecciones Fijas vs. Vecindad):**
Se ha realizado un análisis exhaustivo del dataset de entrada que confirma que no existe ningún conflicto o superposición entre las intersecciones de asignación obligatoria (conjunto $F$) y el grafo de distancias (conjunto $N$). El conjunto $F$ cuenta con las intersecciones obligatorias: `30 78 44628 45173 45481 45555 45787 49180`. Se ha implementado un script ad hoc para recorrer los vecinos reales de todos estos nodos en el archivo crudo y comprobar intersecciones mutuas. Por poner un ejemplo documentado, la intersección `30` únicamente tiene como vecinas a `{31, 32, 45534, 45714}`; ninguna se encuentra en $F$. *(Nota para el informe: Para demostrar esto de forma empírica te he dejado creado en la carpeta raíz el script `verify_fixed_intersections.py`. Ejecútalo sin miedo y anexa su salida por consola o cítalo metodológicamente en el PDF final para defender este chequeo irrefutablemente).* Esta verificación pre-solver exhaustiva garantiza empírica y matemáticamente que el problema no será intrínsecamente infactible antes de pasar al solver, cumpliendo el chequeo crítico indicado en las revisiones.

**Restricciones Adicionales:**
5. **Separación de sensores:** No se puede colocar un sensor en dos intersecciones que sean vecinas simultáneamente.
   $$x_i + x_j \leq 1 \quad \forall (i, j) \in N$$

---

## 2. Entregables y Archivos AMPL

El entregable final prescindirá de scripts complejos en Python. Serán exclusivamente los ficheros requeridos:

- `practica2_a.mod`: Implementación en sintaxis AMPL del modelo del apartado A. (Nota: Se tiene que asegurar declarar la función objetivo referenciada como `total_flow` implícitamente o como variable calculada en el propio `.mod` para que el `.run` pueda hacer display de la misma de forma directa).
- `practica2_b.mod`: Implementación en sintaxis AMPL del modelo del apartado B. (Se aplican las mismas pautas de declaración directa `total_flow` para el sumario de NEOS).
- `practica2.dat`: Fichero unificado con los datos limpios en formato nativo de AMPL.
- `practica2_a.run`: Fichero de ejecución para el apartado A (local).
- `practica2_b.run`: Fichero de ejecución especial para NEOS.
- `informe.pdf`: PDF documentando la resolución. La estructura planificada para este documento, ciñéndose estrictamente a las indicaciones académicas, será la siguiente:
  1. **Autores:** Nombre, apellidos y DNI de los integrantes.
  2. **Formulación Matemática:** Transcripción limpia de la formulación descrita en este documento (conjuntos, parámetros, variables, e inecuaciones) para el Apartado A y Apartado B.
  3. **Código de Implementación:** Código `.mod`, `.dat` y `.run` de AMPL copiados de manera legible indicando explícitamente el uso del solver Cplex para la parte local del Apartado A.
  4. **Descripción de la Implementación:** Pequeños comentarios sobre las decisiones técnicas relevantes como el parseo a min/max y la deduplicación de sets.
  5. **Salida y Soluciones:** Solución óptima obtenida expuesta con claridad e interpretación de los resultados (flujo total logrado y la lista íntegra de nodos que componen la red seleccionada de 15 sensores).

### 2.1. Ficheros `.run`

**Para el Apartado A (local `practica2_a.run`):**
```ampl
# reset;  # ATENCIÓN: No usar/descomentar en NEOS, ya que vaciaría el modelo.
model practica2_a.mod;
data practica2.dat;
option solver cplex;
solve;
display x;
display y;
display total_flow;
```

**Para el Apartado B (NEOS `practica2_b.run`):**
Dejar explicitado que en NEOS sólo se suben los ficheros, por lo que el `.run` no debe cargar nada, tan solo ejecutar y mostrar resultados. El solver en este caso lo dictamina el backend de NEOS:
```ampl
solve;
display x;
display y;
display total_flow;
```

### 2.2. Preprocesado para generar el `.dat`
Para rellenar el `practica2.dat` a partir del crudo `OPT25-26_Datos práctica 2.txt`, se usará un pequeño script Python local de **uso exclusivamente interno** (no se entregará). Su única función será transcribir y formatear:
- Los sets simples (lista delimitada).
- El set relacional de caminos a intersecciones, formateado apropiadamente como set de tuplas 2D en AMPL `(p, i)`.
- El parámetro de flujo.
- El set relacional de vecindades. Dado que el fichero de datos crudos no es iterativamente simétrico en la declaración de conectividades, la mera comprobación `i < j` en el parseo es insuficiente. Primero se normalizará cada par en memoria para obtener su versión inamovible o estricta mediante `(min(i,j), max(i,j))`, y posteriormente se aplicará un conjunto (`set()`) sobre todas las tuplas normalizadas. Solo entonces se procederá al volcado de la lista `NEIGHBORS`, garantizando que ninguna restricción simétrica se pierda o se duplique en el solver.

Ejemplo representativo de la sintaxis correcta que contendrá el `practica2.dat` (obsérvese la notación requerida por AMPL para conjuntos 2D, con comas y estructurados por filas o paréntesis):
```ampl
set INTERSECTIONS := 73701 73702 ... ;
set PATHS := 1439 1441 ... ;
set FIXED := 30 78 44628 45173 45481 45555 45787 49180 ;
set PROHIBITED := 54977 73703 68 ;

param PATH_FLOW :=
1439 3.01909319
1441 0.201561508
...
;

set PATH_INTERSECTIONS :=
(1439, 5)
(1439, 88)
... ;

set NEIGHBORS :=
(5, 6)
(5, 7)
... ;
```

## 3. Plan de Verificación

Se realizarán las siguientes tareas de validación internas antes de crear el PDF final:

1. **Construcción del `.dat`**: Correr el script generador y asegurar que los tamaños de los conjuntos listados coinciden numéricamente con las cotas iniciales: **457 intersecciones, 42 caminos, y 542 asociaciones relacionales en `PATH_INTERSECTIONS`**.
2. **Ejecución Apartado A**: Lanzar `ampl practica2_a.run`. Verificar en los logs:
   - Que Cplex encuentra una solución óptima en un tiempo razonable.
   - Que $\sum x \le 15$.
   - Que todas las intersecciones de la lista `FIXED` valen $x=1$.
   - Que todas las intersecciones de la lista `PROHIBITED` valen $x=0$.
3. **Ejecución Apartado B (simulación)**: Para evitar depender de NEOS para pruebas repetitivas, se relajará inicialmente el límite de restricciones o se hará la resolución local asumiendo licencias completas. Una vez probado, se ejecutará el envío oficial por NEOS.
4. **Validación de la lógica del flujo**: Inspeccionar visualmente 2 o 3 caminos de la salida para constatar empíricamente que $y_p=1$ si y solo si la suma de sus sensores es $\ge 2$.
