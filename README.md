# Proyecto final — Análisis de algoritmos

## Caso 3 — Banco Regional de Alimentos: planeación de despachos

**Curso:** Análisis de algoritmos · 2026-2

**Integrantes**

- David Stiven Franco Lopez
- Juan Sebastian Echeverri Gallego
- Mateo Mesa Cardona
- Julián David Agudelo Acevedo

**Caso asignado:** Caso 3 — Banco de alimentos.

**Operaciones trabajadas**

| Operación | Estrategias implementadas | Estrategia recomendada |
|---|---|---|
| 3. Cargue de los vehículos | Programación dinámica (mochila 0/1), exhaustiva, regla actual por vencimiento y voraz por densidad | Programación dinámica |
| 4. Análisis de saturación de la bodega | Fuerza bruta actual, dividir y vencer, Kadane (programación dinámica) | Kadane |

El informe en PDF, con el mismo contenido de este README, está en [docs/informe.pdf](docs/informe.pdf).

**Contenido**

1. [Análisis del problema](#1-análisis-del-problema)
2. [Diseño de la solución](#2-diseño-de-la-solución)
3. [Implementación](#3-implementación)
4. [Evaluación del desempeño](#4-evaluación-del-desempeño)
5. [Análisis comparativo](#5-análisis-comparativo)
6. [Implicaciones éticas, sociales y ambientales](#6-implicaciones-éticas-sociales-y-ambientales)
7. [Conclusiones](#7-conclusiones)
8. [Referencias](#8-referencias)
9. [Cómo reproducir los datos y los experimentos](#9-cómo-reproducir-los-datos-y-los-experimentos)

---

## 1. Análisis del problema

### 1.1 Descripción del problema computacional

El Banco Regional de Alimentos planea cada madrugada qué lotes salen de la bodega, en qué orden y en qué vehículo. La planeación tiene que caber entre las 03:00 y las 05:00, porque a las 05:30 empieza el alistamiento y a las 06:30 salen los carros. Hoy se demora unas 4 horas y media, entonces los vehículos salen tarde, los comedores reciben la comida después de la hora en que la preparan y parte de lo perecedero se vence en la bodega.

Leyendo el caso, nos quedó claro que el problema no es el computador sino cómo están resueltas las operaciones. Por eso lo vemos como cuatro problemas computacionales distintos que comparten los mismos datos (los lotes):

| # | Operación | Qué crece (n) | Cómo se hace hoy | Orden de crecimiento actual |
|---|---|---|---|---|
| 1 | Consulta de inventario (por código y por rango de vencimiento) | lotes activos, ≈ 220.000 | recorrer la lista completa en cada consulta | Θ(n) por consulta; ≈ 30.000 consultas al día |
| 2 | Ordenamiento FEFO | lotes activos (n) y nuevos del día (k = 6.000 a 9.000) | inserción, agregando los nuevos al final de una lista ya ordenada | Θ(n·k) en la práctica (Θ(n²) en el peor caso) |
| 3 | Cargue de los vehículos | lotes candidatos por ruta (300 a 600) y capacidad W (2.500 a 4.000 kg) | cargar por vencimiento hasta que el siguiente no cabe | Θ(n log n), pero **no da el óptimo** |
| 4 | Análisis de saturación | horas de histórico por categoría (≈ 36.000) × 40 categorías | evaluar todos los tramos de horas posibles | Θ(n²) por categoría |

### 1.2 Operaciones críticas del proceso

No todas las operaciones fallan de la misma manera, y eso fue lo que usamos para escoger:

- **Operación 2 (FEFO)** y la consulta por rango de la **operación 1** son las que más tiempo consumen dentro de la ventana de planeación. Con la inserción, cada lote nuevo tiene que "caminar" hasta su posición dentro de la lista de 220.000 lotes; con 9.000 lotes nuevos son del orden de 9.000 × 110.000 ≈ 10⁹ movimientos por madrugada.
- **Operación 3 (cargue)** casi no gasta tiempo de cómputo, pero su problema es otro: **la respuesta es mala**. Los vehículos salen al 78 % de su capacidad y la regla no mira el valor nutricional. Es la operación obligatoria del Laboratorio 4.
- **Operación 4 (saturación)** está fuera de la ventana, pero es la más costosa de todas: el cliente dice que con 10 años de histórico tarda más de un día para las 40 categorías.

Escogimos la **operación 3** (obligatoria, y donde el impacto social es directo: comida que llega o no llega) y la **operación 4** (la de mayor costo computacional y energético del proceso). Las operaciones 1 y 2 quedan analizadas de forma teórica en las recomendaciones (sección 7.3), porque también son parte del cuello de botella de la ventana.

### 1.3 Costo energético del proceso actual (línea base)

La energía la calculamos como en clase: **kWh = potencia (kW) × tiempo (h)**. El computador de la fundación consume unos 150 W = 0,15 kW bajo carga, y el banco opera 300 días al año.

| Proceso actual | Tiempo informado por el cliente | Energía por corrida | Corridas al año | Energía al año |
|---|---|---|---|---|
| Planeación (operaciones 1 a 3) | ≈ 4,5 h cada madrugada | 4,5 h × 0,15 kW = 0,675 kWh | 300 | **202,5 kWh** |
| Saturación (operación 4), 40 categorías | más de 24 h | ≥ 24 h × 0,15 kW = 3,6 kWh | 12 (supuesto: una vez al mes) | **≥ 43,2 kWh** |
| **Total línea base** | | | | **≥ 245,7 kWh/año** |

Además de la electricidad está el costo ambiental más grande: el banco estima que **cada kilogramo de alimento que se bota equivale a 2,5 kg de CO₂ equivalente**. Una planeación lenta y un cargue que deja espacio vacío en los carros significan comida que se vence en la bodega, y eso pesa mucho más que los kWh del computador. Lo retomamos en la sección 6.

Con nuestras mediciones (sección 4) también estimamos la línea base de las dos operaciones que trabajamos en nuestro propio equipo, y la comparamos con la que reporta el cliente.

### 1.4 Operación 3 — Cargue de los vehículos: entradas, salida y restricciones

Para cada ruta, el coordinador tiene una lista de lotes candidatos y un vehículo. Hay que decidir qué lotes suben. Lo que tiene de especial es que **un lote no se parte**: o sube completo o no sube. Eso lo vuelve una mochila 0/1.

| Elemento | Descripción |
|---|---|
| **Entrada 1** | Lista de n lotes candidatos de la ruta. Cada lote es una tupla `(peso_kg, valor_nutricional, dias_para_vencer)`. En el caso real n está entre 300 y 600. |
| **Entrada 2** | `capacidad_kg` (W): capacidad máxima del vehículo, entero entre 2.500 y 4.000 kg. |
| **Salida** | El valor nutricional total cargado y los índices de los lotes que suben. |
| **Valor nutricional** | Raciones del lote × prioridad de la categoría. Usamos prioridad 3 para proteína, 2 para frutas y verduras y 1 para otros. |
| **Restricción 1** | La suma de los pesos de los lotes elegidos no puede pasar de W. |
| **Restricción 2** | Un lote no se fracciona ni se repite. |
| **Restricción 3** | El valor tiene que ser **el máximo posible**, no una aproximación (lo pide el cliente explícitamente). |
| **Restricción 4** | Ningún lote vencido se despacha. |
| **Volumen real** | 14 vehículos por día, cada uno con su ruta; ventana de 2 horas (03:00–05:00) compartida con las operaciones 1 y 2; computador de 150 W. |

### 1.5 Operación 4 — Análisis de saturación: entradas, salida y restricciones

La Dirección quiere saber, para cada categoría, en qué tramo de horas seguidas el inventario creció más, para dimensionar el cuarto frío que piensa alquilar. Cada hora tiene un cambio neto (lo que entró menos lo que salió o se descartó), y puede ser negativo. Encontrar ese tramo es exactamente el problema del **subarreglo de suma máxima**.

| Elemento | Descripción |
|---|---|
| **Entrada** | Para cada una de las 40 categorías, una lista de n enteros: el cambio neto del inventario en kg en cada hora de operación. Con 12 h/día, 300 días/año y 10 años, n ≈ 36.000. |
| **Salida** | Para cada categoría, la tupla `(crecimiento_kg, hora_inicio, hora_fin)` del tramo de mayor crecimiento acumulado. |
| **Restricción 1** | El tramo reportado debe ser el de **mayor** crecimiento acumulado (no uno "bastante bueno"). |
| **Restricción 2** | El registro original no se modifica (trazabilidad sanitaria). |
| **Volumen real** | 40 categorías × 36.000 horas; hoy tarda más de un día en el computador de 150 W. |

### 1.6 Supuestos del equipo

**Operación 3 (cargue)**

- Los pesos son enteros en kilogramos (así lo dice la estructura del lote). La tabla de la programación dinámica tiene una columna por kilogramo; no usamos gramos porque la tabla crecería mil veces sin mejorar la respuesta.
- Todos los lotes pesan al menos 1 kg.
- **Cómo interpretamos la regla actual:** el coordinador ordena los lotes por días para vencer (si dos vencen el mismo día, el que aparece primero en la lista) y los va subiendo uno a uno. **Se detiene en el primer lote que ya no cabe**, aunque detrás haya lotes más pequeños que sí cabrían. Ejemplo: con un vehículo de 10 kg y lotes de 6, 1 y 4 kg en ese orden de vencimiento, suben los de 6 y 1 kg (7 kg), el de 4 kg no cabe y ahí para, aunque quedan 3 kg libres. Así lo entendimos de "carga por orden de vencimiento hasta que ya no cabe el siguiente lote".
- **Voraz por densidad:** ordena por valor/kg de mayor a menor y, a diferencia de la regla actual, si un lote no cabe lo salta y sigue con el siguiente.
- Un lote con 0 días o menos para vencer se considera vencido y ninguna de las soluciones lo sube.
- Si hay empate entre dos cargas con el mismo valor, cualquiera de las dos es válida; la programación dinámica se queda con la que no incluye el último lote evaluado (usa `>` estricto).
- Cada vehículo se resuelve por separado: los lotes candidatos de una ruta ya vienen asignados a esa ruta.

**Operación 4 (saturación)**

- El tramo tiene al menos una hora. Si en toda la serie el inventario solo bajó, el "tramo de mayor crecimiento" es la hora en que menos bajó (crecimiento negativo); lo reportamos así en vez de devolver un tramo vacío.
- Una serie vacía es un error de datos y se rechaza con `ValueError`.
- Si hay dos tramos con el mismo crecimiento, cualquiera es correcto; las pruebas comparan el crecimiento y verifican que las horas reportadas sumen ese valor.
- Las horas se numeran desde 0 y el tramo incluye la hora de inicio y la de fin.
- La operación se corre una vez al mes (12 veces al año) para actualizar el dimensionamiento; el caso no dice la frecuencia y este fue nuestro supuesto para la energía anual.

**Generales (permitidos por el enunciado)**

- Los datos son válidos, caben en memoria y no cambian mientras corre el algoritmo.
- No procesamos el volumen real completo para la exhaustiva ni para la fuerza bruta: generamos datos sintéticos de tamaño creciente con semilla fija y extrapolamos con la forma de la curva medida.
- Todo corre en un solo hilo, como el computador de la fundación.

---

## 2. Diseño de la solución

### 2.1 Estructuras de datos seleccionadas

> ⏳ Sección en construcción.

### 2.2 Operación 3 — Cargue de los vehículos

Diseñamos cuatro soluciones para la misma operación: la que proponemos y tres contra las que se compara.

| Solución | Familia | Para qué está |
|---|---|---|
| Mochila 0/1 por programación dinámica | Programación dinámica | **Propuesta**: da el óptimo en Θ(n·W). |
| Exhaustiva | Fuerza bruta | Juez para verificar que la PD sí da el óptimo (solo con pocos lotes). |
| Por vencimiento | Regla actual | Línea base: lo que hace hoy el coordinador. |
| Por densidad (valor/kg) | Voraz | Regla "tentadora" que el laboratorio pide incluir para mostrar que tampoco garantiza el óptimo. |

#### Por qué el problema admite programación dinámica

Decidimos lote por lote si sube o no. Después de decidir sobre el último lote de la lista, lo que queda es **el mismo problema** pero más pequeño: menos lotes por decidir y, si el lote subió, menos capacidad libre. Para describir "lo que queda" hacen falta dos números: cuántos lotes faltan (i) y cuántos kilos quedan libres (w).

- **Subestructura óptima.** Si una carga óptima para los lotes 1..i con w kg incluye el lote i, entonces el resto de esa carga tiene que ser una carga óptima para los lotes 1..i−1 con w − peso_i kg. Si no lo fuera, cambiaríamos ese resto por uno mejor y la carga total subiría, lo que contradice que era óptima. Lo mismo si el lote i no sube: el resto es óptimo para 1..i−1 con w kg.
- **Subproblemas que se repiten.** Muchas combinaciones distintas de decisiones terminan en el mismo estado. Por ejemplo, subir un lote de 6 kg, o subir uno de 4 kg y otro de 2 kg, deja en ambos casos la misma capacidad libre y los mismos lotes por decidir. Un recorrido recursivo resolvería ese estado varias veces; la tabla lo resuelve una sola vez.

Una regla voraz no sirve aquí porque escoger "el mejor lote ahora" puede dejar un hueco que después no se llena con nada útil (lo mostramos con el contraejemplo de la sección 5.1).

#### La recurrencia

Definimos **K[i][w]** = el mayor valor nutricional que se puede cargar usando solo los primeros i lotes en un vehículo de w kg.

```
K[0][w] = 0                                         para todo w   (sin lotes no hay valor)
K[i][w] = K[i-1][w]                                 si peso_i > w o el lote i está vencido
K[i][w] = max( K[i-1][w] , valor_i + K[i-1][w - peso_i] )   si peso_i <= w
```

- `K[i-1][w]`: **no subir** el lote i. La capacidad sigue igual y decidimos sobre los anteriores.
- `valor_i + K[i-1][w - peso_i]`: **subir** el lote i. Ganamos su valor y nos quedan `w - peso_i` kg para los anteriores. Se usa la fila i−1 (y no la i) para que un mismo lote no suba dos veces.
- **Caso base:** la fila 0 (ningún lote) es toda ceros. La columna w = 0 también queda en cero porque no cabe nada.
- **Orden de llenado:** cada casilla de la fila i solo depende de la fila i−1, así que llenamos fila por fila, de arriba hacia abajo. Dentro de la fila el orden de las columnas no importa.
- **Respuesta:** K[n][W].
- **Reconstrucción:** desde K[n][W] subimos fila por fila. Si K[i][w] ≠ K[i−1][w], el lote i subió y restamos su peso a w; si son iguales, no subió.

#### Ejemplo pequeño resuelto a mano

Usamos un vehículo a escala con **W = 10 kg** y cinco lotes, ya ordenados por vencimiento:

| Lote | Producto (categoría) | Peso (kg) | Raciones × prioridad | Valor | Días para vencer | Valor/kg |
|---|---|---|---|---|---|---|
| L0 | Arroz (otros) | 6 | 12 × 1 | 12 | 1 | 2,0 |
| L1 | Atún (proteína) | 1 | 3 × 3 | 9 | 2 | 9,0 |
| L2 | Guayaba (frutas y verduras) | 4 | 8 × 2 | 16 | 3 | 4,0 |
| L3 | Tomate (frutas y verduras) | 1 | 3 × 2 | 6 | 4 | 6,0 |
| L4 | Fríjol (proteína) | 6 | 6 × 3 | 18 | 5 | 3,0 |

Llenamos la tabla fila por fila (la fila i ya considera los lotes L0 a L(i−1)):

| i \ w | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 (ninguno) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 1 (+L0: 6 kg, 12) | 0 | 0 | 0 | 0 | 0 | 0 | 12 | 12 | 12 | 12 | 12 |
| 2 (+L1: 1 kg, 9) | 0 | 9 | 9 | 9 | 9 | 9 | 12 | 21 | 21 | 21 | 21 |
| 3 (+L2: 4 kg, 16) | 0 | 9 | 9 | 9 | 16 | 25 | 25 | 25 | 25 | 25 | 28 |
| 4 (+L3: 1 kg, 6) | 0 | 9 | 15 | 15 | 16 | 25 | 31 | 31 | 31 | 31 | 31 |
| 5 (+L4: 6 kg, 18) | 0 | 9 | 15 | 15 | 16 | 25 | 31 | 31 | 33 | 33 | **34** |

Algunas casillas explicadas paso a paso:

- **K[2][7]** (L0 y L1, 7 kg): no subir L1 da K[1][7] = 12; subirlo da 9 + K[1][6] = 9 + 12 = 21. Gana 21 (arroz + atún).
- **K[3][10]** (L0, L1, L2 con 10 kg): no subir L2 da K[2][10] = 21; subirlo da 16 + K[2][6] = 16 + 12 = 28. Gana 28.
- **K[4][10]**: no subir L3 da 28; subirlo da 6 + K[3][9] = 6 + 25 = 31. Gana 31.
- **K[5][10]** (todos, 10 kg): no subir L4 da K[4][10] = 31; subirlo da 18 + K[4][4] = 18 + 16 = **34**. Gana 34.

**Reconstrucción** desde K[5][10] = 34:

1. Fila 5, w = 10: K[5][10] = 34 ≠ K[4][10] = 31 → **L4 sube**. Quedan 10 − 6 = 4 kg.
2. Fila 4, w = 4: K[4][4] = 16 = K[3][4] = 16 → L3 no sube.
3. Fila 3, w = 4: K[3][4] = 16 ≠ K[2][4] = 9 → **L2 sube**. Quedan 4 − 4 = 0 kg.
4. Filas 2 y 1, w = 0: todo es 0 → L1 y L0 no suben.

**Resultado óptimo: guayaba (L2) + fríjol (L4), 10 kg exactos y valor 34.** Este mismo ejemplo está como prueba en `pruebas.py`.

### 2.3 Operación 4 — Análisis de saturación

> ⏳ Sección en construcción.

### 2.4 Cómo reducen el consumo energético las propuestas

> ⏳ Sección en construcción.

---

## 3. Implementación

### 3.1 Tecnologías y herramientas

El proyecto se desarrolló en **Python 3**, utilizando las siguientes herramientas y técnicas:

| Herramienta o técnica | Uso en el proyecto |
|---|---|
| Python | Implementación de algoritmos y pruebas. |
| Programación dinámica | Resolución óptima del problema de mochila 0/1. |
| Fuerza bruta | Verificación mediante evaluación exhaustiva. |
| Estrategias voraces | Comparación de las reglas por vencimiento y densidad nutricional. |
| `random` | Generación de instancias reproducibles con semillas fijas. |
| `time.perf_counter()` | Medición de tiempos de ejecución. |
| Contador de operaciones | Análisis del crecimiento de los algoritmos. |
| Matplotlib | Generación de gráficas comparativas. |
| CSV y JSON | Almacenamiento de resultados experimentales. |
| Git y GitHub | Control de versiones y trabajo colaborativo. |

Los algoritmos se encuentran en `src/cargue_vehiculos/`, las gráficas en `graficas/cargue_vehiculos/` y los resultados en `resultados/cargue_vehiculos/`.

### 3.2 Operación 3 — Código del cargue de vehículos

Los algoritmos y las pruebas están implementados en [src/cargue_vehiculos/](src/cargue_vehiculos/).

| Archivo | Descripción |
|---|---|
| [contador.py](src/cargue_vehiculos/contador.py) | Contador de operaciones elementales. |
| [estrategia.py](src/cargue_vehiculos/estrategia.py) | Solución óptima mediante programación dinámica (mochila 0/1): `cargar_vehiculo`, que llena la tabla (`llenar_tabla`) y reconstruye los lotes elegidos (`reconstruir_lotes`). |
| [exhaustivo.py](src/cargue_vehiculos/exhaustivo.py) | Solución exacta mediante fuerza bruta: `cargar_exhaustivo` prueba los 2ⁿ subconjuntos. |
| [regla_actual.py](src/cargue_vehiculos/regla_actual.py) | Regla por vencimiento (`cargar_por_vencimiento`, la que se usa hoy) y estrategia voraz por densidad (`cargar_por_densidad`). |
| [datos.py](src/cargue_vehiculos/datos.py) | Generación de instancias reproducibles para las pruebas y las mediciones. |
| [pruebas.py](src/cargue_vehiculos/pruebas.py) | Pruebas automatizadas, casos límite y 300 instancias aleatorias. |
| [medicion.py](src/cargue_vehiculos/medicion.py) | Experimentos de tiempo y operaciones, tablas en `resultados/` y gráficas en `graficas/`. |

**Decisiones de implementación**

- Respetamos las firmas del esqueleto del laboratorio. Solo agregamos un parámetro opcional `contador` al final, que no cambia lo que devuelve cada función. Al cronometrar lo dejamos en `None` para que contar no infle el tiempo, y contamos en una corrida aparte.
- En `llenar_tabla` cada fila empieza como copia de la anterior (la opción "no subir el lote") y solo se recorren las columnas `w >= peso` (la opción "subirlo"). Es la misma recurrencia, pero evita comparaciones inútiles donde el lote no cabe.
- La reconstrucción compara `K[i][w]` con `K[i-1][w]` y baja `w` cada vez que un lote sube; por eso se guarda la tabla completa y no solo una fila.
- La exhaustiva usa un entero como máscara de bits (bit i = lote i) para recorrer los 2ⁿ subconjuntos.
- Las reglas ordenan **índices** y no los lotes, para no modificar la lista original.
- Los lotes vencidos (0 días o menos) se excluyen en las cuatro soluciones, para que la comparación sea justa y ninguna despache comida vencida.
- Los módulos usan importaciones relativas (`from .contador import Contador`), así que se ejecutan como módulo desde la raíz del repositorio (`python -m src.cargue_vehiculos.pruebas`), como se explica en la sección 9.

### 3.3 Operación 4 — Código del análisis de saturación

> ⏳ Sección en construcción.

---

## 4. Evaluación del desempeño

### 4.1 Operación 3 — Complejidad temporal y espacial

Para analizar los algoritmos se utilizan dos variables:

- **n:** cantidad de lotes disponibles.
- **W:** capacidad máxima del vehículo, expresada en kilogramos enteros.

| Algoritmo | Complejidad temporal | Complejidad espacial |
|---|---|---|
| Programación dinámica | Θ(n·W) | O(n·W) |
| Fuerza bruta | Θ(n·2^n) | O(n) |
| Regla por vencimiento | O(n log n) | O(n) |
| Regla por densidad | O(n log n) | O(n) |

**Programación dinámica:** construye una tabla de soluciones para las combinaciones de lotes y capacidades. Su tiempo y memoria dependen de n y W. Es un algoritmo pseudo-polinomial porque W representa un valor numérico, no la longitud de su representación.

**Fuerza bruta:** evalúa los 2^n subconjuntos posibles y comprueba su peso y valor nutricional. Garantiza encontrar el óptimo, pero su crecimiento exponencial impide utilizarlo con grandes cantidades de lotes.

**Regla por vencimiento:** ordena los lotes según los días restantes antes de vencer y selecciona siguiendo ese orden. Su costo está dominado por el ordenamiento, pero no garantiza el máximo valor nutricional.

**Regla por densidad:** ordena los lotes según su valor nutricional por kilogramo. También tiene un costo dominado por el ordenamiento y tampoco garantiza el óptimo cuando los lotes no se pueden fraccionar.

Las mediciones experimentales de las secciones 4.3 y 4.4 permiten contrastar estas complejidades con los tiempos y las operaciones observadas.

### 4.2 Operación 3 — Verificación

Las pruebas están en [pruebas.py](src/cargue_vehiculos/pruebas.py) y se corren con `python -m src.cargue_vehiculos.pruebas`. Cubren:

| Grupo | Qué verifica |
|---|---|
| Casos límite | Sin lotes; un lote que cabe; un lote que no cabe; ningún lote cabe; todos caben; capacidad 0; dos lotes que llenan justo la capacidad; capacidad negativa (debe lanzar `ValueError`). |
| Ejemplo a mano | La PD y la exhaustiva dan 34 con los lotes [2, 4] (guayaba y fríjol) en el ejemplo de la sección 2.2. |
| Contraejemplo | En el mismo ejemplo la regla por vencimiento da 21 y la de densidad 31: las dos quedan por debajo del óptimo 34. |
| Lotes vencidos | Ninguna de las cuatro soluciones sube un lote con 0 o menos días para vencer. |
| 300 instancias aleatorias (semilla 2026) | La PD y la exhaustiva dan **el mismo valor** en las 300 (de 0 a 12 lotes, la guía pide mínimo 20); además la carga reconstruida no pasa de la capacidad, no repite lotes y suma exactamente el valor óptimo; y las dos reglas nunca superan el óptimo ni la capacidad. |
| Trazabilidad | Ninguna solución modifica la lista original de lotes. |

Además, dentro de [medicion.py](src/cargue_vehiculos/medicion.py) hay un `assert` que vuelve a comprobar que la PD y la exhaustiva coinciden en cada tamaño medido. Todas las pruebas pasan.

Una cosa que aprendimos: que la PD coincida con la exhaustiva no prueba que el **modelo** esté bien (si las dos partieran de una idea equivocada, se equivocarían igual). Por eso también está el ejemplo resuelto a mano y los casos límite.

### 4.3 Operación 3 — Pruebas experimentales y resultados

Para evaluar el comportamiento de los algoritmos se implementó el módulo
[medicion.py](src/cargue_vehiculos/medicion.py), que genera instancias
reproducibles, mide los tiempos de ejecución y cuenta las operaciones
elementales de cada solución.

Los experimentos se realizaron utilizando `time.perf_counter()` para
medir el tiempo. La generación de los datos queda fuera del cronometraje
y el conteo de operaciones se realiza por separado.

**Cómo medimos**

- Los datos se generan con [datos.py](src/cargue_vehiculos/datos.py) usando semilla fija: la instancia de tamaño n usa la semilla 1000 + n en el experimento de tamaños pequeños y 2000 + n en el de crecimiento de n. Todas las soluciones se miden **con las mismas instancias** en cada tamaño.
- Repeticiones: 50 para la programación dinámica y las reglas en tamaños pequeños; 5 para la programación dinámica y 20 para las reglas en tamaños grandes; 5 para la fuerza bruta (3 desde 16 lotes). Se reporta el promedio.
- Las operaciones se cuentan con `Contador`: casillas de la tabla (PD), subconjuntos × n (fuerza bruta) y comparaciones más lotes revisados (reglas).
- En los tamaños donde corren las dos, un `assert` comprueba que la PD y la fuerza bruta dan el mismo valor.

Se desarrollaron cuatro experimentos:

1. **Tamaños pequeños:** entre 8 y 20 lotes, con capacidad fija de 120 kg.
   Se compararon programación dinámica, fuerza bruta y las dos reglas voraces.
2. **Crecimiento de n:** entre 75 y 2400 lotes, con capacidad fija de 3000 kg.
3. **Crecimiento de W:** 300 lotes y capacidades entre 250 y 8000 kg.
4. **Volumen real del caso:** 10 días simulados, cada uno con 14 vehículos,
   entre 300 y 600 lotes por ruta y capacidades entre 2500 y 4000 kg.

Los resultados se guardaron en
[resultados/cargue_vehiculos/](resultados/cargue_vehiculos/).

**Tiempo de ejecución según la cantidad de lotes**

![Tiempo frente a n](graficas/cargue_vehiculos/tiempo_vs_n.png)

La fuerza bruta presenta crecimiento exponencial. Con apenas 20 lotes
alcanzó aproximadamente 1957,94 ms, mientras que la programación dinámica
tardó aproximadamente 0,161 ms para el mismo tamaño.

**Conteo de operaciones elementales**

![Operaciones frente a n](graficas/cargue_vehiculos/operaciones_vs_n.png)

Al duplicar la cantidad de lotes de 10 a 20, las operaciones de la
programación dinámica se multiplicaron por 2, mientras que las de
fuerza bruta se multiplicaron por 2048.

**Tiempo según la capacidad del vehículo**

![Tiempo frente a la capacidad](graficas/cargue_vehiculos/tiempo_vs_capacidad.png)

Al duplicar la capacidad de 2000 a 4000 kg, manteniendo fija la cantidad
de lotes, el tiempo de programación dinámica se multiplicó por 2,17.
Esto es consistente con su complejidad temporal Θ(n·W).

**Calidad de las soluciones**

![Calidad del cargue](graficas/cargue_vehiculos/calidad_cargue.png)

| Algoritmo | Valor nutricional respecto al óptimo | Capacidad utilizada |
|---|---:|---:|
| Programación dinámica | 100 % | 100 % |
| Regla por densidad | 98,60 % | 100 % |
| Regla por vencimiento | 42,17 % | 86,50 % |

Los porcentajes corresponden a las instancias sintéticas utilizadas
en los experimentos. La programación dinámica garantiza el máximo valor
nutricional, mientras que las reglas voraces no garantizan el óptimo.

### 4.4 Operación 3 — Comparación entre resultados teóricos y experimentales

La programación dinámica tiene complejidad temporal Θ(n·W). Cuando
la capacidad permanece constante, el trabajo aumenta linealmente
con la cantidad de lotes. Cuando n permanece constante, el trabajo
aumenta aproximadamente de forma lineal con W.

| Comparación | Factor experimental de tiempo | Factor de operaciones |
|---|---:|---:|
| PD: 8 a 16 lotes | 2,03 | 2,00 |
| PD: 10 a 20 lotes | 1,83 | 2,00 |
| PD: 300 a 600 lotes | 1,84 | 2,00 |
| PD: 1200 a 2400 lotes | 2,04 | 2,00 |
| PD: capacidad 2000 a 4000 kg | 2,17 | 2,00 |
| Fuerza bruta: 8 a 16 lotes | 503,82 | 512,00 |
| Fuerza bruta: 10 a 20 lotes | 1817,15 | 2048,00 |

Los resultados respaldan el análisis teórico: la programación dinámica
presenta un crecimiento pseudo-polinomial, mientras que la fuerza bruta
crece exponencialmente.

Las diferencias entre los factores de tiempo y operaciones se explican
por los costos de ejecución de Python y las variaciones propias de las
mediciones en el computador utilizado.

### 4.5 Operación 3 — Extrapolación al volumen real y consumo energético

Se simularon 10 días de operación con 14 vehículos diarios.

Para programación dinámica se obtuvo un tiempo promedio de
**1,6684 segundos por día**, considerando las 14 rutas.

La ruta más costosa registrada necesitó aproximadamente 0,2433 segundos,
con 585 lotes y capacidad de 3845 kg.

Estos tiempos representan una fracción muy pequeña de la ventana
disponible de dos horas para la planeación de despachos.

**Extrapolación de la fuerza bruta.** No se puede medir con el volumen
real, así que la extrapolamos con la forma de su curva, Θ(n·2ⁿ), que
la sección 4.4 confirma (el factor al duplicar se acerca a 2048 = 2 · 2¹⁰).
Con 20 lotes tardó 1,958 s para 20.971.520 operaciones, es decir,
unos 9,3 × 10⁻⁸ s por operación:

- Con **40 lotes**: 40 · 2⁴⁰ ≈ 4,4 × 10¹³ operaciones ≈ 4,1 × 10⁶ s, unos
  **47 días** para un solo vehículo.
- Con **300 lotes** (la ruta real más pequeña): 300 · 2³⁰⁰ · 9,3 × 10⁻⁸ ≈
  5,7 × 10⁸⁵ s, muchísimo más que la edad del universo (≈ 4,4 × 10¹⁷ s).

Por eso la fuerza bruta **sencillamente no termina** con el volumen real:
solo sirve como juez en instancias pequeñas.

**¿Cabe cada solución en la ventana de 2 horas (7.200 s)?**

| Algoritmo | Tiempo por día (14 vehículos) | ¿Cabe en la ventana? |
|---|---:|---|
| Programación dinámica | 1,67 s medido (≈ 3,4 s si las 14 rutas fueran como la más pesada) | **Sí**, usa menos del 0,05 % de la ventana |
| Regla por vencimiento | 0,0030 s | Sí, pero no da el óptimo |
| Regla por densidad | 0,0031 s | Sí, pero no da el óptimo |
| Fuerza bruta | > 10⁸⁵ s | **No, nunca termina** |

Aunque el computador de la fundación fuera cien veces más lento que
nuestro portátil, la programación dinámica tardaría unos 3 a 6 minutos
por día y seguiría cabiendo en la ventana.

**Comparación diaria**

| Algoritmo | Tiempo estimado por día | Kilogramos despachados por día |
|---|---:|---:|
| Programación dinámica | 1,6684 s | 46.162,5 kg |
| Regla por vencimiento | 0,0030 s | 39.931,9 kg |
| Regla por densidad | 0,0031 s | 46.162,5 kg |

En las simulaciones, la programación dinámica permitió cargar
aproximadamente **6230,6 kg adicionales por día** frente a la regla
actual por vencimiento.

**Estimación de energía**

Para estimar el consumo energético se utilizó un computador de
150 W y 300 días de operación al año.

| Algoritmo | Consumo energético anual estimado |
|---|---:|
| Programación dinámica | 0,02086 kWh |
| Regla por vencimiento | 0,00003755 kWh |
| Regla por densidad | 0,00003877 kWh |

Aunque la programación dinámica requiere más procesamiento que las
reglas voraces, su consumo energético estimado sigue siendo muy bajo
y permite obtener una carga nutricionalmente óptima.

Los resultados dependen de las instancias sintéticas y del equipo
utilizado para las mediciones. No deben interpretarse como mediciones
directas de la operación real del banco de alimentos.

### 4.6 Operación 4 — Complejidad, verificación y resultados

> ⏳ Sección en construcción.

---

## 5. Análisis comparativo

### 5.1 Operación 3 — Contraejemplo de la regla actual (y de la voraz por densidad)

Usamos el mismo ejemplo de la sección 2.2: vehículo de **10 kg** y estos lotes (peso, valor, días para vencer): L0 (6, 12, 1), L1 (1, 9, 2), L2 (4, 16, 3), L3 (1, 6, 4), L4 (6, 18, 5).

**Regla actual (por vencimiento, se detiene en el primero que no cabe):**

| Paso | Lote (por vencimiento) | Peso | ¿Cabe? | Carga | Valor |
|---|---|---|---|---|---|
| 1 | L0 arroz (vence en 1 día) | 6 | sí (6 ≤ 10) | 6 kg | 12 |
| 2 | L1 atún (2 días) | 1 | sí (7 ≤ 10) | 7 kg | 21 |
| 3 | L2 guayaba (3 días) | 4 | **no** (11 > 10) → **para** | 7 kg | 21 |

Resultado: **valor 21, 7 kg (70 % del vehículo)**. Quedan 3 kg libres y todavía estaba el tomate (1 kg), pero la regla ya paró.

**Voraz por densidad (salta el que no cabe y sigue):** orden por valor/kg: L1 (9,0), L3 (6,0), L2 (4,0), L4 (3,0), L0 (2,0).

| Paso | Lote | Peso | ¿Cabe? | Carga | Valor |
|---|---|---|---|---|---|
| 1 | L1 atún | 1 | sí | 1 kg | 9 |
| 2 | L3 tomate | 1 | sí | 2 kg | 15 |
| 3 | L2 guayaba | 4 | sí | 6 kg | 31 |
| 4 | L4 fríjol | 6 | no (12 > 10), lo salta | 6 kg | 31 |
| 5 | L0 arroz | 6 | no (12 > 10), lo salta | 6 kg | 31 |

Resultado: **valor 31, 6 kg**. Metió primero lo "más eficiente" y dejó un hueco de 4 kg que ya ningún lote podía llenar.

**Óptimo (programación dinámica y exhaustiva):** guayaba + fríjol, **10 kg, valor 34**.

| Solución | Lotes | Peso | Valor | Diferencia con el óptimo |
|---|---|---|---|---|
| Por vencimiento (actual) | L0, L1 | 7 kg | 21 | **−13 (−38 %)** |
| Voraz por densidad | L1, L2, L3 | 6 kg | 31 | **−3 (−9 %)** |
| Programación dinámica | L2, L4 | 10 kg | **34** | — |

La regla actual falla por dos razones que se suman: no mira el valor (solo la fecha) y se detiene en el primer lote que no cabe. La de densidad corrige la primera, pero igual falla porque **los lotes no se pueden partir**: si se pudiera llevar media porción del fríjol, la densidad sí daría el óptimo. Este contraejemplo está en `pruebas.py` (`probar_contraejemplo_reglas`).

### 5.2 Operación 3 — Condición contraria: cuándo bastaría una regla voraz

La regla por densidad sería la adecuada (y daría el óptimo en Θ(n log n), sin depender de W) si **los lotes se pudieran fraccionar**, es decir, si se pudiera subir una parte de un lote y recibir la parte proporcional de su valor. Eso es la mochila fraccionaria: se mete lo de mayor valor por kilo y el último lote se parte para llenar justo la capacidad, así nunca queda un hueco. Por ejemplo, si los productos llegaran a granel y se pudieran reempacar en la bodega. También funcionaría una voraz si todos los lotes tuvieran el **mismo valor por kilogramo** (entonces cualquier carga llena es óptima) o si todos pesaran lo mismo (bastaría con escoger los de mayor valor). En el banco ninguna de esas condiciones se cumple: el lote "sube completo o no sube" y los valores por kilo son muy distintos entre proteína, frutas y otros.

### 5.3 Operación 3 — Recomendación

Se recomienda utilizar **programación dinámica (mochila 0/1)** para seleccionar los lotes que se cargarán en cada vehículo del banco de alimentos.

Esta recomendación se fundamenta en los siguientes resultados:

1. **Calidad de la solución:** la programación dinámica garantiza el máximo valor nutricional posible sin superar la capacidad del vehículo y sin dividir los lotes.

2. **Verificación:** las pruebas automatizadas confirmaron que la programación dinámica y la fuerza bruta obtienen el mismo valor óptimo en 300 instancias aleatorias.

3. **Tiempo de ejecución:** en las simulaciones de 10 días y 14 vehículos diarios, la programación dinámica necesitó aproximadamente 1,6684 segundos por día para calcular las cargas.

4. **Aprovechamiento de capacidad:** en las instancias simuladas, la programación dinámica alcanzó un aprovechamiento promedio del 100 %, frente al 86,50 % de la regla por vencimiento.

5. **Valor nutricional:** la regla por vencimiento consiguió el 42,17 % del valor óptimo, mientras que la regla por densidad alcanzó el 98,60 %. Ninguna de las dos garantiza encontrar siempre la mejor combinación.

6. **Viabilidad operativa:** los tiempos medidos se encuentran muy por debajo de la ventana de dos horas disponible para planear los despachos.

Aunque las reglas voraces son más rápidas y consumen menos recursos computacionales, pueden seleccionar combinaciones que desperdician capacidad o reducen el valor nutricional transportado.

Por otra parte, la fuerza bruta garantiza el óptimo, pero su crecimiento exponencial la hace inviable cuando aumenta considerablemente la cantidad de lotes.

**Conclusión:** la programación dinámica ofrece el mejor equilibrio entre calidad de la solución y tiempo de procesamiento para las capacidades y cantidades de lotes evaluadas.

Se recomienda mantener la regla por vencimiento como referencia comparativa y utilizar la programación dinámica como estrategia principal de planificación. Antes de aplicar los resultados en una operación real, se deben validar los datos de inventario, las restricciones de vencimiento y las condiciones logísticas del banco de alimentos.

### 5.4 Operación 4 — Comparación, ventajas y limitaciones

> ⏳ Sección en construcción.

### 5.5 Comparación general y solución seleccionada

> ⏳ Sección en construcción.

---

## 6. Implicaciones éticas, sociales y ambientales

### 6.1 Consumo energético

Para estimar el consumo energético de los algoritmos se utilizó como referencia un computador con una potencia supuesta de **150 W (0,15 kW)** y **300 días de operación al año**.

El consumo se calcula mediante:

**Energía (kWh) = Potencia (kW) × Tiempo de ejecución (horas)**

Los tiempos se obtuvieron de los experimentos realizados con 10 días simulados y 14 vehículos por día.

| Algoritmo | Tiempo estimado por día | Consumo anual estimado |
|---|---:|---:|
| Programación dinámica | 1,6684 s | 0,02086 kWh |
| Regla por vencimiento | 0,0030 s | 0,00003755 kWh |
| Regla por densidad | 0,0031 s | 0,00003877 kWh |
| Fuerza bruta | no termina (sección 4.5) | no se puede usar: aun con solo 40 lotes serían ≈ 171 kWh por vehículo y por día |

La programación dinámica necesita más tiempo de procesamiento porque evalúa diferentes combinaciones de lotes y capacidades para encontrar la solución óptima.

Las reglas voraces realizan menos operaciones y, por lo tanto, presentan un menor consumo energético estimado. Sin embargo, no garantizan encontrar la combinación de mayor valor nutricional.

En las simulaciones, la programación dinámica obtuvo el **100 % del valor nutricional óptimo**, mientras que la regla por vencimiento alcanzó el **42,17 %** y la regla por densidad el **98,60 %**.

Por esta razón, el mayor tiempo de procesamiento de la programación dinámica se considera aceptable frente al beneficio de seleccionar una mejor combinación de alimentos.

**Limitación:** esta estimación supone una potencia constante de 150 W durante la ejecución. No corresponde a una medición directa del consumo eléctrico del computador ni incluye el consumo energético de los vehículos, la refrigeración o la operación de la bodega.

Los valores se pueden reproducir ejecutando `python -m src.cargue_vehiculos.medicion` y consultando `resultados/cargue_vehiculos/resumen.json`.

> ⏳ Sección en construcción.

### 6.2 Preguntas de impacto del caso

> ⏳ Sección en construcción.

### 6.3 Consecuencias sobre las personas cuando el algoritmo se equivoca o llega tarde

> 🚧 Sección en construcción.

### 6.4 Marco normativo y buenas prácticas

Investigamos las normas colombianas y las buenas prácticas que tocan la solución. Las fuentes están en la sección 8.

| Norma o buena práctica | Qué exige | Cómo la respeta nuestro diseño |
|---|---|---|
| **Ley 9 de 1979** (Código Sanitario Nacional) | Condiciones sanitarias para manipular, almacenar y distribuir alimentos para consumo humano. | Ningún lote vencido se carga (prueba `probar_no_despacha_vencidos`). |
| **Resolución 2674 de 2013**, Ministerio de Salud y Protección Social | Requisitos sanitarios para fabricar, almacenar, transportar y distribuir alimentos; condiciones del transporte y registros. | Ningún vehículo supera su capacidad (verificado). Los algoritmos no modifican los registros de los lotes, que son los que soportan la vigilancia sanitaria. |
| **Resolución 5109 de 2005**, Ministerio de la Protección Social (rotulado) | La fecha de vencimiento debe estar en el rótulo de los alimentos envasados. | Usamos esa fecha (días para vencer) como dato de entrada y como barrera para no despachar vencidos. |
| **Ley 1990 de 2019** (política contra la pérdida y el desperdicio de alimentos) | Prevenir la pérdida y el desperdicio de alimentos, y promover su donación y redistribución. | El objetivo de la propuesta es justamente que más comida salga de la bodega y llegue a tiempo; medimos el aumento de kilos despachados. |
| **Ley 1581 de 2012** y **Decreto 1377 de 2013** (protección de datos personales) | Tratamiento de datos con autorización, finalidad y seguridad; el artículo 7 de la ley protege especialmente los datos de niños, niñas y adolescentes. | Los algoritmos trabajan solo con datos de los lotes (peso, valor, fecha) y de inventario; **no necesitan ni leen los listados de población beneficiaria**. Si se implementan cuotas por organización, se usan conteos agregados, nunca datos de los menores. |
| **Ley 1098 de 2006** (Código de la Infancia y la Adolescencia) | Prevalencia del interés superior de los niños. | Por eso proponemos cuotas mínimas y prioridad para jardines infantiles, en vez de dejar que solo mande la eficiencia. |
| **Codex Alimentarius, CXC 1-1969** (Principios generales de higiene de los alimentos, FAO/OMS) | Rotación de inventario, control de vencimiento y sistemas de trazabilidad/retiro de producto. | El FEFO y la exclusión de vencidos van en esa línea; el registro original no se toca, así que un retiro de producto se puede rastrear. |
| **ISO 22005:2007** (trazabilidad en la cadena de alimentos) | Poder identificar el origen y el destino de cada lote. | Las soluciones devuelven **índices** de los lotes cargados, no copias modificadas: cada lote despachado se puede asociar a su `codigo_lote` y su donante. |
| **Ley 842 de 2003** (código de ética de la ingeniería en Colombia) y **Código de ética de la ACM (2018)** | Proteger la salud y el bienestar de las personas, ser honestos con las limitaciones de lo que se entrega. | Declaramos los supuestos, las estimaciones y los límites de cada estrategia (por ejemplo, que la PD no mira fechas y que el 42 % depende de los datos sintéticos). |
| **Objetivo de Desarrollo Sostenible 12.3** (ONU) | Reducir a la mitad el desperdicio de alimentos para 2030. | Más carga útil por viaje y planeación a tiempo reducen el desperdicio en la bodega. |

**Trazabilidad de los datos originales.** En todo el código los lotes son tuplas (inmutables), las reglas ordenan índices en vez de reordenar la lista, y hay pruebas en las dos operaciones que comprueban que la lista original queda igual después de correr cada solución.

### 6.5 Sostenibilidad de la decisión: escenario de crecimiento

> ⏳ Sección en construcción.

---

## 7. Conclusiones

> ⏳ Sección en construcción.

---

## 8. Referencias

- Cormen, T. H., Leiserson, C. E., Rivest, R. L. y Stein, C. (2009). *Introduction to Algorithms* (3.ª ed.). MIT Press. Capítulos 4.1 (subarreglo máximo), 15 (programación dinámica) y 16 (algoritmos voraces; mochila 0/1 en 16.2).
- Kleinberg, J. y Tardos, É. (2006). *Algorithm Design*. Pearson. Sección 6.4 (Subset Sums and Knapsacks).
- Bentley, J. (1984). Programming Pearls: Algorithm Design Techniques. *Communications of the ACM*, 27(9), 865–873 (origen del algoritmo de Kadane).
- Material del curso: "Fundamentos de programación dinámica", "Estrategia voraz", "Programación dinámica: decidir, verificar y medir" y "Complemento del Laboratorio 4 — Mochila 0/1". Nodo, 2026.
- Documentación de Python: `time.perf_counter`, `random`, `tracemalloc` (https://docs.python.org/3/library/) y matplotlib (https://matplotlib.org/stable/).

**Normativa y buenas prácticas** (consultadas en el Gestor Normativo de Función Pública, https://www.funcionpublica.gov.co/eva/gestornormativo/, y en los portales de cada entidad):

- Congreso de Colombia. Ley 9 de 1979, por la cual se dictan medidas sanitarias (Código Sanitario Nacional).
- Ministerio de Salud y Protección Social. Resolución 2674 de 2013, requisitos sanitarios para personas naturales y jurídicas que ejercen actividades de fabricación, procesamiento, preparación, envase, almacenamiento, transporte, distribución y comercialización de alimentos. https://www.minsalud.gov.co
- Ministerio de la Protección Social. Resolución 5109 de 2005, reglamento técnico sobre rotulado o etiquetado de alimentos envasados.
- Congreso de Colombia. Ley 1990 de 2019, política para prevenir la pérdida y el desperdicio de alimentos.
- Congreso de Colombia. Ley 1581 de 2012, disposiciones generales para la protección de datos personales; y Decreto 1377 de 2013 (compilado en el Decreto 1074 de 2015).
- Congreso de Colombia. Ley 1098 de 2006, Código de la Infancia y la Adolescencia.
- Congreso de Colombia. Ley 842 de 2003, Código de Ética para el ejercicio de la ingeniería en Colombia.
- FAO/OMS. Codex Alimentarius, CXC 1-1969, Principios generales de higiene de los alimentos (rev. 2020). https://www.fao.org/fao-who-codexalimentarius/
- ISO 22005:2007, Trazabilidad en la cadena de piensos y alimentos. https://www.iso.org
- ACM (2018). ACM Code of Ethics and Professional Conduct. https://www.acm.org/code-of-ethics
- Naciones Unidas. Objetivo de Desarrollo Sostenible 12, meta 12.3. https://sdgs.un.org/goals/goal12

---

## 9. Cómo reproducir los datos y los experimentos

Los experimentos de la operación 3 se pueden reproducir utilizando Python 3 y las dependencias del proyecto.

### 9.1 Preparación del entorno

Clonar el repositorio:

~~~powershell
git clone https://github.com/Davdfranco/proyecto-final-banco-alimentos.git
cd proyecto-final-banco-alimentos
~~~

Crear y activar el entorno virtual (Python 3.12 o superior), e instalar las dependencias. Todos los comandos se ejecutan **desde la raíz del repositorio**:

~~~powershell
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows (PowerShell)
# source .venv/bin/activate       # Linux / macOS
python -m pip install -r requirements.txt
~~~

Si PowerShell no deja activar el entorno, se habilita una sola vez con `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

### 9.2 Ejecutar las pruebas automatizadas

~~~powershell
python -m src.cargue_vehiculos.pruebas
~~~

Las pruebas incluyen casos límite, contraejemplos y 300 instancias aleatorias reproducibles.

### 9.3 Ejecutar los experimentos

~~~powershell
python -m src.cargue_vehiculos.medicion
~~~

El programa compara los algoritmos, mide su crecimiento y simula 10 días de operación con 14 vehículos diarios.

### 9.4 Archivos generados

Gráficas en `graficas/cargue_vehiculos/`:

- `tiempo_vs_n.png`
- `operaciones_vs_n.png`
- `tiempo_vs_capacidad.png`
- `calidad_cargue.png`

Resultados en `resultados/cargue_vehiculos/`:

- `pequenas.csv`
- `grandes_n.csv`
- `capacidad.csv`
- `dias_reales.csv`
- `resumen.json`

### 9.5 Consideraciones de reproducibilidad

Las semillas fijas permiten reproducir las instancias utilizadas.

Los tiempos pueden variar según el computador, el sistema operativo y la versión de Python.

Las mediciones corresponden a datos sintéticos y no representan registros directos de la operación real del banco de alimentos.
