"""Análisis de saturación: lo que hace hoy el programa de la bodega.

Evalúa todos los tramos de horas consecutivas posibles. Para cada hora de
inicio va acumulando la suma hacia la derecha, así que cada tramo cuesta
Θ(1) y el total es Θ(n²) (n(n + 1)/2 tramos).
"""

from .contador import Contador

Tramo = tuple[int, int, int]  # (crecimiento_kg, hora_inicio, hora_fin), fin incluido


def tramo_fuerza_bruta(
    cambios: list[int], contador: Contador | None = None
) -> Tramo:
    """Encuentra el tramo de mayor crecimiento revisando todos los tramos.

    Args:
        cambios: cambio neto del inventario (kg) en cada hora de operación;
            puede ser negativo.
        contador: si se entrega, suma una operación por tramo evaluado.

    Returns:
        El crecimiento acumulado máximo y las horas de inicio y fin del tramo
        (índices desde 0, ambos incluidos).

    Raises:
        ValueError: si la serie está vacía.
    """
    n = len(cambios)
    if n == 0:
        raise ValueError("La serie de cambios no puede estar vacía")
    mejor = (cambios[0], 0, 0)
    for inicio in range(n):
        suma = 0
        for fin in range(inicio, n):
            suma += cambios[fin]
            if suma > mejor[0]:
                mejor = (suma, inicio, fin)
        if contador is not None:
            contador.sumar(n - inicio)  # tramos que empiezan en "inicio"
    return mejor
