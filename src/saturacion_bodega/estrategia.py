"""Análisis de saturación de la bodega: estrategia propuesta (Kadane).

Programación dinámica de una sola pasada: mejor_aqui[i] es el mayor
crecimiento de un tramo que termina exactamente en la hora i, y cumple

    mejor_aqui[i] = max(cambios[i], mejor_aqui[i - 1] + cambios[i])

Como cada valor solo depende del anterior, basta guardar un número: Θ(n) en
tiempo y Θ(1) en memoria adicional.
"""

from .contador import Contador

Tramo = tuple[int, int, int]  # (crecimiento_kg, hora_inicio, hora_fin), fin incluido


def tramo_kadane(cambios: list[int], contador: Contador | None = None) -> Tramo:
    """Encuentra el tramo de horas consecutivas en que más creció el inventario.

    Args:
        cambios: cambio neto del inventario (kg) en cada hora de operación;
            puede ser negativo.
        contador: si se entrega, suma una operación por hora procesada.

    Returns:
        El crecimiento acumulado máximo y las horas de inicio y fin del tramo
        (índices desde 0, ambos incluidos).

    Raises:
        ValueError: si la serie está vacía.
    """
    if not cambios:
        raise ValueError("La serie de cambios no puede estar vacía")
    mejor = (cambios[0], 0, 0)
    aqui = cambios[0]  # mejor tramo que termina en la hora actual
    inicio_aqui = 0
    for hora in range(1, len(cambios)):
        valor = cambios[hora]
        if aqui + valor < valor:  # conviene empezar de nuevo en esta hora
            aqui = valor
            inicio_aqui = hora
        else:  # conviene extender el tramo que venía
            aqui += valor
        if aqui > mejor[0]:
            mejor = (aqui, inicio_aqui, hora)
    if contador is not None:
        contador.sumar(len(cambios))
    return mejor


def analizar_categorias(series: dict[str, list[int]]) -> dict[str, Tramo]:
    """Aplica Kadane a la serie de cada categoría de producto.

    Args:
        series: para cada categoría, su serie de cambios netos por hora.

    Returns:
        Para cada categoría, su tramo de mayor crecimiento.
    """
    return {categoria: tramo_kadane(cambios) for categoria, cambios in series.items()}
