# Notas de Redaccion - Version Definitiva

## 1. Organizacion final del proyecto

La version definitiva se ha agrupado en una unica carpeta llamada `definitivo/` para evitar la dispersion de ficheros de pruebas, copias intermedias y versiones alternativas.

La carpeta se divide en cuatro bloques:

- `ampl/`: modelos y datos finales en AMPL.
- `tools/`: dos scripts Python sencillos para generar el `.dat` y comprobar los nodos `FIXED`.
- `datos_crudos/`: copia del fichero original entregado por la asignatura.
- `notes/`: notas de redaccion para la memoria final.

Esta organizacion permite distinguir claramente entre:

- el dato original,
- el preprocesado interno,
- los ficheros finales de AMPL,
- y la documentacion de apoyo.

## 2. Formulacion matematica del apartado A

### Conjuntos

- `I`: conjunto de intersecciones.
- `P`: conjunto de caminos.
- `F`: conjunto de intersecciones fijas.
- `Q`: conjunto de intersecciones prohibidas.
- `I_p`: intersecciones pertenecientes al camino `p`.

### Parametros

- `f_p > 0`: flujo del camino `p`.

### Variables de decision

- `x_i in {0,1}`: vale 1 si se instala sensor en la interseccion `i`.
- `y_p in {0,1}`: vale 1 si el camino `p` se considera detectado.

### Funcion objetivo

Maximizar el flujo total detectado:

`max sum_{p in P} f_p * y_p`

### Restricciones

1. Presupuesto de sensores:
   `sum_{i in I} x_i <= 15`
2. Nodos fijos:
   `x_i = 1` para todo `i in F`
3. Nodos prohibidos:
   `x_i = 0` para todo `i in Q`
4. Deteccion de caminos:
   `sum_{i in I_p} x_i >= 2 * y_p`

### Justificacion de la restriccion de deteccion

No hace falta una restriccion adicional para forzar `y_p = 1` cuando haya al menos dos sensores, porque todos los flujos son estrictamente positivos y la funcion objetivo es maximizadora. Por tanto, cuando el modelo puede activar un `y_p`, le conviene hacerlo.

## 3. Formulacion matematica del apartado B

El apartado B reutiliza la formulacion del apartado A y anade:

- `N`: conjunto de pares de intersecciones vecinas a distancia menor o igual que 300 metros.

Restriccion adicional:

`x_i + x_j <= 1` para todo `(i,j) in N`

Con esto se evita colocar sensores demasiado cercanos.

## 4. Implementacion AMPL elegida

### Apartado A

Se ha optado por una implementacion simple y directa:

- `x` y `y` son binarias.
- `PATH_INTERSECTIONS` se modela como conjunto bidimensional.
- La restriccion de deteccion se escribe como:

`sum {(p, i) in PATH_INTERSECTIONS} x[i] >= 2 * y[p]`

Esta expresion es compacta, legible y se corresponde muy bien con la formulacion matematica.

### Apartado B

Se utiliza exactamente el mismo esquema, anadiendo `NEIGHBORS` y la restriccion de separacion:

`x[i] + x[j] <= 1`

## 5. Scripts Python y generacion del .dat

El fichero crudo proporcionado por la practica no esta en formato AMPL, por lo que se han usado dos scripts Python muy simples.

El primero, `tools/build_ampl_data.py`, recorre el fichero original, detecta cada seccion por su cabecera y va guardando las lineas hasta encontrar la siguiente seccion. Con esa informacion genera el fichero final `practica2.dat`.

El segundo, `tools/verify_fixed_intersections.py`, comprueba de forma directa que no haya nodos `FIXED` vecinos entre si dentro de `intersection_neighborhood`, para descartar que el apartado B sea infactible de partida por esa razon.

Los scripts usados son:

- `tools/build_ampl_data.py`
- `tools/verify_fixed_intersections.py`

## 6. Validaciones realizadas

Antes de usar los modelos en AMPL se han comprobado varios aspectos:

### Cardinalidades del dataset

- 457 intersecciones
- 42 caminos
- 542 pares en `PATH_INTERSECTIONS`

### Vecindad para el apartado B

La lista de vecinos del crudo se normaliza para construir pares unicos `(min(i,j), max(i,j))`. De este modo se evita duplicar restricciones simetricas en AMPL.

### Conflictos entre nodos fijos

Se verifica expresamente que no existan dos nodos `FIXED` que sean vecinos, ya que eso volveria intrinsecamente infactible el apartado B.

## 7. Salida de los ficheros .run

Se ha optado por una salida limpia, mostrando solo:

- el valor final de `total_flow`,
- los sensores seleccionados,
- los caminos detectados.

Esto es preferible a mostrar todas las variables con valor 0 y 1, porque facilita:

- la lectura de resultados,
- la comparacion entre solvers,
- y la inclusion directa en el informe.

## 8. Decisiones de integracion entre versiones

Se han combinado las mejores partes de ambas versiones previas:

- del trabajo propio: generacion automatica del `.dat` a partir del fichero crudo y comprobacion simple de los nodos `FIXED`;
- de la version alternativa: salida de AMPL mas limpia y una formulacion del conjunto `PATH_INTERSECTIONS` especialmente clara en las restricciones.

Ademas, se ha mantenido la condicion estricta:

- `PATH_FLOW > 0`

en lugar de `>= 0`, porque el enunciado trabaja con flujos estrictamente positivos y eso justifica mejor la logica del modelo.

Como el fichero `practica2.dat` se ha unificado para ambos apartados, el modelo A admite tambien la declaracion del conjunto `NEIGHBORS`, aunque no lo utiliza en ninguna restriccion del apartado A. Esto evita mantener dos ficheros `.dat` distintos.

## 9. Comprobaciones que conviene citar en la memoria

Para el apartado A:

- el solver devuelve solucion optima,
- el flujo total coincide entre solvers MILP,
- el numero total de sensores no supera 15,
- todos los nodos `FIXED` aparecen activados,
- todos los nodos `PROHIBITED` quedan a 0.

Para el apartado B:

- el conjunto `NEIGHBORS` se ha normalizado sin duplicados,
- no hay conflictos previos entre nodos `FIXED`,
- la solucion final no activa simultaneamente nodos vecinos.

## 10. Recomendacion para el informe

En la memoria final conviene explicar el flujo de trabajo en este orden:

1. Formulacion matematica del apartado A.
2. Formulacion matematica del apartado B.
3. Breve explicacion del parser Python y la generacion del `.dat`.
4. Decision de usar un `.dat` unificado y verificaciones previas.
5. Ejecucion de AMPL y solver usado en cada apartado.
6. Presentacion de la solucion optima y su interpretacion.
