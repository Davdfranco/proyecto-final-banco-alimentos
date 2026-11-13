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

| Operación | Estado | Estrategias |
|---|---|---|
| 3. Cargue de los vehículos (Laboratorio 4) | Entrega del 18 de noviembre | Programación dinámica (mochila 0/1), exhaustiva, regla actual por vencimiento y voraz por densidad |
| 4. Análisis de saturación de la bodega | Pendiente para el 23 de noviembre | — |

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

> ⏳ Pendiente para la entrega del 23 de noviembre.

### 1.2 Operaciones críticas del proceso

> ⏳ Pendiente para la entrega del 23 de noviembre.

### 1.3 Costo energético del proceso actual (línea base)

> ⏳ Pendiente para la entrega del 23 de noviembre.

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

> ⏳ Pendiente para la entrega del 23 de noviembre.

### 1.6 Supuestos del equipo

**Operación 3 (cargue)**

- Los pesos son enteros en kilogramos (así lo dice la estructura del lote). La tabla de la programación dinámica tiene una columna por kilogramo; no usamos gramos porque la tabla crecería mil veces sin mejorar la respuesta.
- Todos los lotes pesan al menos 1 kg.
- **Cómo interpretamos la regla actual:** el coordinador ordena los lotes por días para vencer (si dos vencen el mismo día, el que aparece primero en la lista) y los va subiendo uno a uno. **Se detiene en el primer lote que ya no cabe**, aunque detrás haya lotes más pequeños que sí cabrían. Ejemplo: con un vehículo de 10 kg y lotes de 6, 1 y 4 kg en ese orden de vencimiento, suben los de 6 y 1 kg (7 kg), el de 4 kg no cabe y ahí para, aunque quedan 3 kg libres. Así lo entendimos de "carga por orden de vencimiento hasta que ya no cabe el siguiente lote".
- **Voraz por densidad:** ordena por valor/kg de mayor a menor y, a diferencia de la regla actual, si un lote no cabe lo salta y sigue con el siguiente.
- Un lote con 0 días o menos para vencer se considera vencido y ninguna de las soluciones lo sube.
- Si hay empate entre dos cargas con el mismo valor, cualquiera de las dos es válida; la programación dinámica se queda con la que no incluye el último lote evaluado (usa `>` estricto).
- Cada vehículo se resuelve por separado: los lotes candidatos de una ruta ya vienen asignados a esa ruta.

---

## 2. Diseño de la solución

### 2.1 Estructuras de datos seleccionadas

> ⏳ Pendiente para la entrega del 23 de noviembre.

### 2.2 Operación 3 — Cargue de los vehículos

> 🚧 Sección en construcción.

### 2.3 Operación 4 — Análisis de saturación

> ⏳ Pendiente para la entrega del 23 de noviembre.

### 2.4 Cómo reducen el consumo energético las propuestas

> ⏳ Pendiente para la entrega del 23 de noviembre.

---

## 3. Implementación

### 3.1 Tecnologías y herramientas

> 🚧 Sección en construcción.

### 3.2 Operación 3 — Código del cargue de vehículos

> 🚧 Sección en construcción.

### 3.3 Operación 4 — Código del análisis de saturación

> ⏳ Pendiente para la entrega del 23 de noviembre.

---

## 4. Evaluación del desempeño

### 4.1 Operación 3 — Complejidad temporal y espacial

> 🚧 Sección en construcción.

### 4.2 Operación 3 — Verificación

> 🚧 Sección en construcción.

### 4.3 Operación 3 — Pruebas experimentales y resultados

> 🚧 Sección en construcción.

### 4.6 Operación 4 — Complejidad, verificación y resultados

> ⏳ Pendiente para la entrega del 23 de noviembre.

---

## 5. Análisis comparativo

### 5.1 Operación 3 — Contraejemplo de la regla actual (y de la voraz por densidad)

> 🚧 Sección en construcción.

### 5.3 Operación 3 — Recomendación

> 🚧 Sección en construcción.

### 5.4 Operación 4 — Comparación, ventajas y limitaciones

> ⏳ Pendiente para la entrega del 23 de noviembre.

### 5.5 Comparación general y solución seleccionada

> ⏳ Pendiente para la entrega del 23 de noviembre.

---

## 6. Implicaciones éticas, sociales y ambientales

### 6.1 Consumo energético

> 🚧 Sección en construcción.

### 6.2 Preguntas de impacto del caso

> ⏳ Pendiente para la entrega del 23 de noviembre.

### 6.3 Consecuencias sobre las personas cuando el algoritmo se equivoca o llega tarde

> ⏳ Pendiente para la entrega del 23 de noviembre.

### 6.4 Marco normativo y buenas prácticas

> ⏳ Pendiente para la entrega del 23 de noviembre.

### 6.5 Sostenibilidad de la decisión: escenario de crecimiento

> ⏳ Pendiente para la entrega del 23 de noviembre.

---

## 7. Conclusiones

> ⏳ Pendiente para la entrega del 23 de noviembre.

---

## 8. Referencias

- Cormen, T. H., Leiserson, C. E., Rivest, R. L. y Stein, C. (2009). *Introduction to Algorithms* (3.ª ed.). MIT Press. Capítulos 4.1 (subarreglo máximo), 15 (programación dinámica) y 16 (algoritmos voraces; mochila 0/1 en 16.2).
- Kleinberg, J. y Tardos, É. (2006). *Algorithm Design*. Pearson. Sección 6.4 (Subset Sums and Knapsacks).
- Bentley, J. (1984). Programming Pearls: Algorithm Design Techniques. *Communications of the ACM*, 27(9), 865–873 (origen del algoritmo de Kadane).
- Material del curso: "Fundamentos de programación dinámica", "Estrategia voraz", "Programación dinámica: decidir, verificar y medir" y "Complemento del Laboratorio 4 — Mochila 0/1". Nodo, 2026.
- Documentación de Python: `time.perf_counter`, `random`, `tracemalloc` (https://docs.python.org/3/library/) y matplotlib (https://matplotlib.org/stable/).

---

## 9. Cómo reproducir los datos y los experimentos

> 🚧 Sección en construcción.
