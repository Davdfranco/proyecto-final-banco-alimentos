"""Generador de series sintéticas para el análisis de saturación.

Cada serie es el cambio neto del inventario de una categoría, en kg, por
cada hora de operación (12 horas al día, 300 días al año). Se modelan tres
cosas que se ven en una bodega de alimentos:

- ruido de hora a hora (lo que entra y sale no es constante);
- un patrón diario: en la mañana se recibe más y en la tarde se despacha más;
- temporadas en que el inventario tiende a crecer (cosechas, fin de año).
"""

import math
import random

HORAS_POR_DIA = 12
DIAS_POR_ANIO = 300
ANIOS_HISTORICO = 10
HORAS_HISTORICO = HORAS_POR_DIA * DIAS_POR_ANIO * ANIOS_HISTORICO  # 36.000
CATEGORIAS_REALES = 40


def cambio_hora(rng: random.Random, hora: int, temporada: bool) -> int:
    """Genera el cambio neto de inventario de una hora.

    Args:
        rng: generador aleatorio con semilla fija.
        hora: índice de la hora dentro del histórico.
        temporada: True si la hora cae en una temporada de alto ingreso.

    Returns:
        El cambio neto en kg (entero, puede ser negativo).
    """
    hora_del_dia = hora % HORAS_POR_DIA
    patron_diario = 60 * math.cos(math.pi * hora_del_dia / (HORAS_POR_DIA - 1))
    sesgo = 60 if temporada else -15
    return round(rng.gauss(patron_diario + sesgo, 150))


def generar_serie(horas: int, semilla: int) -> list[int]:
    """Genera la serie de cambios netos por hora de una categoría.

    Args:
        horas: longitud de la serie (n).
        semilla: semilla fija para reproducir la serie.

    Returns:
        La lista de cambios netos en kg.
    """
    rng = random.Random(semilla)
    horas_temporada = HORAS_POR_DIA * 20  # temporadas de unos 20 días
    serie = []
    inicio_temporada = rng.randint(0, max(0, horas - horas_temporada))
    for hora in range(horas):
        if hora % (HORAS_POR_DIA * DIAS_POR_ANIO) == 0 and hora > 0:
            # cada año la temporada cae en un momento distinto
            inicio_temporada = hora + rng.randint(0, HORAS_POR_DIA * 250)
        temporada = inicio_temporada <= hora < inicio_temporada + horas_temporada
        serie.append(cambio_hora(rng, hora, temporada))
    return serie


def generar_categorias(
    cantidad: int, horas: int, semilla: int
) -> dict[str, list[int]]:
    """Genera las series de varias categorías de producto.

    Args:
        cantidad: número de categorías.
        horas: longitud de cada serie.
        semilla: semilla base; cada categoría usa semilla + su número.

    Returns:
        Un diccionario categoría -> serie de cambios netos.
    """
    return {f"categoria_{c:02d}": generar_serie(horas, semilla + c)
            for c in range(1, cantidad + 1)}


def generar_serie_pequena(n: int, semilla: int) -> list[int]:
    """Genera una serie corta con valores pequeños para las pruebas.

    Args:
        n: longitud de la serie.
        semilla: semilla fija.

    Returns:
        Una lista de n enteros entre -50 y 50.
    """
    rng = random.Random(semilla)
    return [rng.randint(-50, 50) for _ in range(n)]
