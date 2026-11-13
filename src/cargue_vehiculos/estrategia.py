"""Cargue de un vehículo del banco de alimentos.

Estrategia propuesta: mochila 0/1 resuelta con programación dinámica
(tabulación) y reconstrucción de los lotes elegidos.
"""

from contador import Contador

Lote = tuple[int, int, int]  # (peso_kg, valor_nutricional, dias_para_vencer)


def esta_vencido(lote: Lote) -> bool:
    """Indica si un lote ya no se puede despachar.

    Un lote con 0 días para vencer (vence hoy) o menos se considera vencido:
    no alcanza a llegar a tiempo a la organización beneficiaria.

    Args:
        lote: el lote a revisar.

    Returns:
        True si el lote está vencido.
    """
    return lote[2] <= 0


def llenar_tabla(
    lotes: list[Lote], capacidad_kg: int, contador: Contador | None = None
) -> list[list[int]]:
    """Llena la tabla K de la mochila 0/1, fila por fila.

    K[i][w] es el mayor valor nutricional que se logra eligiendo solo entre
    los i primeros lotes con un vehículo de w kilogramos. La fila i de la
    tabla corresponde al lote lotes[i - 1]; la fila 0 es el caso base.

    Args:
        lotes: lotes candidatos de la ruta; no se fraccionan.
        capacidad_kg: capacidad máxima del vehículo en kilogramos.
        contador: si se entrega, suma una operación por cada casilla calculada.

    Returns:
        La tabla de (n + 1) filas y (capacidad_kg + 1) columnas.
    """
    n = len(lotes)
    tabla = [[0] * (capacidad_kg + 1)]  # fila 0: sin lotes no hay valor
    for i in range(1, n + 1):
        peso, valor, _ = lotes[i - 1]
        anterior = tabla[i - 1]
        # Opción (a), no llevar el lote: se copia la fila de arriba.
        fila = anterior[:]
        # Opción (b), llevarlo: solo donde cabe y si el lote no está vencido.
        inicio = capacidad_kg + 1 if esta_vencido(lotes[i - 1]) else peso
        for w in range(inicio, capacidad_kg + 1):
            llevar = valor + anterior[w - peso]
            if llevar > fila[w]:
                fila[w] = llevar
        tabla.append(fila)
        if contador is not None:
            contador.sumar(capacidad_kg + 1)  # casillas calculadas en la fila
    return tabla


def reconstruir_lotes(
    lotes: list[Lote], tabla: list[list[int]], capacidad_kg: int
) -> list[int]:
    """Recupera qué lotes forman una carga óptima a partir de la tabla.

    Se recorre desde la última fila hacia arriba: si K[i][w] cambió frente a
    K[i - 1][w], el lote i - 1 subió y la capacidad libre baja su peso.

    Args:
        lotes: los mismos lotes con que se llenó la tabla.
        tabla: tabla devuelta por llenar_tabla.
        capacidad_kg: capacidad con que se llenó la tabla.

    Returns:
        Los índices de los lotes cargados, en orden creciente.
    """
    elegidos: list[int] = []
    w = capacidad_kg
    for i in range(len(lotes), 0, -1):
        if tabla[i][w] != tabla[i - 1][w]:
            elegidos.append(i - 1)
            w -= lotes[i - 1][0]
    elegidos.reverse()
    return elegidos


def cargar_vehiculo(
    lotes: list[Lote], capacidad_kg: int, contador: Contador | None = None
) -> tuple[int, list[int]]:
    """Elige los lotes de mayor valor nutricional que caben en el vehículo.

    Args:
        lotes: lotes candidatos de la ruta; no se fraccionan. Los lotes
            vencidos nunca se eligen.
        capacidad_kg: capacidad máxima del vehículo en kilogramos.
        contador: si se entrega, cuenta las casillas calculadas de la tabla.

    Returns:
        El valor nutricional máximo y los índices de los lotes cargados.
    """
    if capacidad_kg < 0:
        raise ValueError("La capacidad del vehículo no puede ser negativa")
    tabla = llenar_tabla(lotes, capacidad_kg, contador)
    elegidos = reconstruir_lotes(lotes, tabla, capacidad_kg)
    return tabla[len(lotes)][capacidad_kg], elegidos
