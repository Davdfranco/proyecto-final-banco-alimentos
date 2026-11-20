"""Análisis de saturación por dividir y vencer.

El tramo de mayor crecimiento de una serie está en la mitad izquierda, en la
mitad derecha o cruza el punto medio. Los dos primeros casos son el mismo
problema con la mitad del tamaño; el tercero se resuelve en tiempo lineal.
Recurrencia T(n) = 2T(n/2) + Θ(n), es decir, Θ(n log n).
"""

from .contador import Contador

Tramo = tuple[int, int, int]  # (crecimiento_kg, hora_inicio, hora_fin), fin incluido


def tramo_que_cruza(
    cambios: list[int], bajo: int, medio: int, alto: int,
    contador: Contador | None = None,
) -> Tramo:
    """Encuentra el mejor tramo que contiene las horas medio y medio + 1.

    Args:
        cambios: serie de cambios netos por hora (kg).
        bajo: primer índice del subarreglo.
        medio: índice del punto medio.
        alto: último índice del subarreglo.
        contador: si se entrega, suma una operación por hora recorrida.

    Returns:
        El crecimiento del mejor tramo que cruza y sus horas de inicio y fin.
    """
    suma = 0
    mejor_izq = cambios[medio]
    inicio = medio
    for i in range(medio, bajo - 1, -1):  # se extiende hacia la izquierda
        suma += cambios[i]
        if suma > mejor_izq:
            mejor_izq = suma
            inicio = i
    suma = 0
    mejor_der = cambios[medio + 1]
    fin = medio + 1
    for j in range(medio + 1, alto + 1):  # y hacia la derecha
        suma += cambios[j]
        if suma > mejor_der:
            mejor_der = suma
            fin = j
    if contador is not None:
        contador.sumar(alto - bajo + 1)
    return mejor_izq + mejor_der, inicio, fin


def tramo_recursivo(
    cambios: list[int], bajo: int, alto: int, contador: Contador | None = None
) -> Tramo:
    """Resuelve el subarreglo cambios[bajo..alto] dividiéndolo en dos.

    Args:
        cambios: serie de cambios netos por hora (kg).
        bajo: primer índice del subarreglo.
        alto: último índice del subarreglo (incluido).
        contador: se pasa a tramo_que_cruza.

    Returns:
        El tramo de mayor crecimiento dentro del subarreglo.
    """
    if bajo == alto:  # caso base: una sola hora
        if contador is not None:
            contador.sumar()
        return cambios[bajo], bajo, bajo
    medio = (bajo + alto) // 2
    izquierdo = tramo_recursivo(cambios, bajo, medio, contador)
    derecho = tramo_recursivo(cambios, medio + 1, alto, contador)
    cruzado = tramo_que_cruza(cambios, bajo, medio, alto, contador)
    # En empate se prefiere el tramo que empieza antes (izquierdo).
    mejor = izquierdo
    for candidato in (cruzado, derecho):
        if candidato[0] > mejor[0]:
            mejor = candidato
    return mejor


def tramo_dividir_vencer(
    cambios: list[int], contador: Contador | None = None
) -> Tramo:
    """Encuentra el tramo de mayor crecimiento con dividir y vencer.

    Args:
        cambios: cambio neto del inventario (kg) en cada hora; puede ser
            negativo.
        contador: si se entrega, cuenta las horas recorridas en total.

    Returns:
        El crecimiento acumulado máximo y las horas de inicio y fin del tramo.

    Raises:
        ValueError: si la serie está vacía.
    """
    if not cambios:
        raise ValueError("La serie de cambios no puede estar vacía")
    return tramo_recursivo(cambios, 0, len(cambios) - 1, contador)
