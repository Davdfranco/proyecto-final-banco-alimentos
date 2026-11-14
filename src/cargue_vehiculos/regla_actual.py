"""Reglas de cargue que no garantizan el óptimo.

- cargar_por_vencimiento: lo que hace hoy el coordinador (línea base).
- cargar_por_densidad: la variante voraz por valor/kg, tentadora pero inexacta.
"""

from collections.abc import Callable
from functools import cmp_to_key

from .contador import Contador

Lote = tuple[int, int, int]  # (peso_kg, valor_nutricional, dias_para_vencer)


def ordenar_indices(
    lotes: list[Lote], clave: Callable[[int], tuple], contador: Contador | None
) -> list[int]:
    """Ordena los índices de los lotes según una clave, contando comparaciones.

    Sin contador usa sorted con key (rápido, para cronometrar). Con contador
    usa un comparador que suma una operación por cada comparación.

    Args:
        lotes: lotes candidatos de la ruta.
        clave: función que recibe un índice y devuelve la tupla de orden.
        contador: si se entrega, cuenta las comparaciones del ordenamiento.

    Returns:
        Los índices de los lotes en el orden pedido.
    """
    if contador is None:
        return sorted(range(len(lotes)), key=clave)

    def comparar(a: int, b: int) -> int:
        contador.sumar()
        ka, kb = clave(a), clave(b)
        return (ka > kb) - (ka < kb)

    return sorted(range(len(lotes)), key=cmp_to_key(comparar))


def cargar_por_vencimiento(
    lotes: list[Lote], capacidad_kg: int, contador: Contador | None = None
) -> tuple[int, list[int]]:
    """Reproduce el procedimiento actual: carga por vencimiento.

    Se ordenan los lotes por días para vencer (a igual fecha, por su posición
    en la lista, que es el orden en que los ve el coordinador) y se suben uno
    a uno. Se detiene en el primer lote que ya no cabe.

    Args:
        lotes: lotes candidatos de la ruta.
        capacidad_kg: capacidad máxima del vehículo en kilogramos.
        contador: si se entrega, cuenta comparaciones y lotes revisados.

    Returns:
        El valor nutricional cargado y los índices de los lotes cargados.
    """
    orden = ordenar_indices(lotes, lambda i: (lotes[i][2], i), contador)
    libre = capacidad_kg
    valor = 0
    elegidos: list[int] = []
    for i in orden:
        if contador is not None:
            contador.sumar()
        if lotes[i][2] <= 0:
            continue  # un lote vencido nunca sube
        peso = lotes[i][0]
        if peso > libre:
            break  # el coordinador deja de cargar aquí
        elegidos.append(i)
        libre -= peso
        valor += lotes[i][1]
    elegidos.sort()
    return valor, elegidos


def cargar_por_densidad(
    lotes: list[Lote], capacidad_kg: int, contador: Contador | None = None
) -> tuple[int, list[int]]:
    """Carga por mayor valor por kilogramo; no garantiza el óptimo.

    A diferencia de la regla actual, no se detiene en el primer lote que no
    cabe: lo salta y sigue buscando lotes que sí quepan.

    Args:
        lotes: lotes candidatos de la ruta (peso mayor que 0).
        capacidad_kg: capacidad máxima del vehículo en kilogramos.
        contador: si se entrega, cuenta comparaciones y lotes revisados.

    Returns:
        El valor nutricional cargado y los índices de los lotes cargados.
    """
    orden = ordenar_indices(
        lotes, lambda i: (-lotes[i][1] / lotes[i][0], i), contador
    )
    libre = capacidad_kg
    valor = 0
    elegidos: list[int] = []
    for i in orden:
        if contador is not None:
            contador.sumar()
        peso = lotes[i][0]
        if lotes[i][2] > 0 and peso <= libre:  # nunca un lote vencido
            elegidos.append(i)
            libre -= peso
            valor += lotes[i][1]
    elegidos.sort()
    return valor, elegidos
