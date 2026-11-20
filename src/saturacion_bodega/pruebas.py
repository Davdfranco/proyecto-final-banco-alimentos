"""Pruebas con assert del análisis de saturación de la bodega.

Ejecutar desde la raíz del repositorio:

    python -m src.saturacion_bodega.pruebas
"""

import random
from collections.abc import Callable

from .datos import generar_categorias, generar_serie_pequena
from .dividir_vencer import tramo_dividir_vencer
from .estrategia import Tramo, analizar_categorias, tramo_kadane
from .regla_actual import tramo_fuerza_bruta

SOLUCIONES: list[Callable[[list[int]], Tramo]] = [
    tramo_fuerza_bruta,
    tramo_dividir_vencer,
    tramo_kadane,
]

# Ejemplo resuelto a mano en el informe: 8 horas de una categoría (kg).
EJEMPLO_MANO = [30, -50, 40, 60, -20, 70, -90, 10]


def suma_tramo(cambios: list[int], tramo: Tramo) -> int:
    """Suma los cambios de las horas que reporta un tramo.

    Args:
        cambios: serie de cambios netos por hora.
        tramo: (crecimiento, inicio, fin) reportado por una solución.

    Returns:
        La suma real de cambios[inicio..fin].
    """
    _, inicio, fin = tramo
    return sum(cambios[inicio:fin + 1])


def es_tramo_consistente(cambios: list[int], tramo: Tramo) -> bool:
    """Revisa que el tramo sea válido y que su suma sea la que dice.

    Args:
        cambios: serie de cambios netos por hora.
        tramo: (crecimiento, inicio, fin) reportado por una solución.

    Returns:
        True si 0 <= inicio <= fin < n y la suma coincide con el crecimiento.
    """
    crecimiento, inicio, fin = tramo
    rango_ok = 0 <= inicio <= fin < len(cambios)
    return rango_ok and suma_tramo(cambios, tramo) == crecimiento


def probar_casos_limite() -> None:
    """Serie vacía, una hora, todo negativo, todo positivo y todo en cero."""
    for solucion in SOLUCIONES:
        try:
            solucion([])
            raise AssertionError(f"{solucion.__name__} aceptó una serie vacía")
        except ValueError:
            pass
        assert solucion([42]) == (42, 0, 0)
        assert solucion([-7]) == (-7, 0, 0)
        # Todo negativo: el tramo es la hora que menos decreció.
        assert solucion([-30, -5, -12, -40])[0] == -5
        assert solucion([-30, -5, -12, -40])[1:] == (1, 1)
        # Todo positivo: el tramo es la serie completa.
        assert solucion([5, 10, 3, 8]) == (26, 0, 3)
        assert solucion([0, 0, 0])[0] == 0


def probar_ejemplo_a_mano() -> None:
    """Comprueba el ejemplo de 8 horas que se resolvió a mano en el informe."""
    for solucion in SOLUCIONES:
        assert solucion(EJEMPLO_MANO) == (150, 2, 5), solucion.__name__


def probar_aleatorias(casos: int = 300, semilla: int = 2026) -> None:
    """Compara las tres soluciones con la fuerza bruta en series al azar.

    La fuerza bruta revisa todos los tramos, así que su valor es el exacto.
    Cada solución debe dar el mismo crecimiento máximo y reportar un tramo
    cuyas horas realmente sumen ese crecimiento.

    Args:
        casos: número de series aleatorias (mínimo 20).
        semilla: semilla fija para que el resultado sea reproducible.
    """
    rng = random.Random(semilla)
    for caso in range(casos):
        cambios = generar_serie_pequena(rng.randint(1, 60), semilla + caso)
        exacto = tramo_fuerza_bruta(cambios)
        assert es_tramo_consistente(cambios, exacto), cambios
        for solucion in (tramo_dividir_vencer, tramo_kadane):
            tramo = solucion(cambios)
            assert tramo[0] == exacto[0], (solucion.__name__, cambios)
            assert es_tramo_consistente(cambios, tramo), (solucion.__name__, cambios)


def probar_es_el_maximo() -> None:
    """Restricción del negocio: ningún tramo crece más que el reportado."""
    cambios = generar_serie_pequena(40, 7)
    reportado = tramo_kadane(cambios)[0]
    for inicio in range(len(cambios)):
        for fin in range(inicio, len(cambios)):
            assert sum(cambios[inicio:fin + 1]) <= reportado


def probar_no_modifica_entrada() -> None:
    """Trazabilidad: ninguna solución altera la serie original."""
    cambios = generar_serie_pequena(50, 11)
    copia = list(cambios)
    for solucion in SOLUCIONES:
        solucion(cambios)
        assert cambios == copia, solucion.__name__


def probar_varias_categorias() -> None:
    """La función por categorías coincide con la fuerza bruta en cada una."""
    series = generar_categorias(5, 300, 99)
    resultado = analizar_categorias(series)
    assert set(resultado) == set(series)
    for categoria, cambios in series.items():
        assert resultado[categoria][0] == tramo_fuerza_bruta(cambios)[0]


def main() -> None:
    """Ejecuta todas las pruebas e informa el resultado."""
    probar_casos_limite()
    probar_ejemplo_a_mano()
    probar_aleatorias()
    probar_es_el_maximo()
    probar_no_modifica_entrada()
    probar_varias_categorias()
    print("saturacion_bodega: todas las pruebas pasaron")


if __name__ == "__main__":
    main()
