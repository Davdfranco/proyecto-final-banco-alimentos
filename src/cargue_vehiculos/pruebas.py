"""Pruebas con assert del cargue de vehículos.

Ejecutar desde la raíz del repositorio:

    python src/cargue_vehiculos/pruebas.py
"""

import random

from .datos import generar_instancia_pequena
from .estrategia import Lote, cargar_vehiculo
from .exhaustivo import cargar_exhaustivo
from .regla_actual import cargar_por_densidad, cargar_por_vencimiento

# Ejemplo resuelto a mano en el informe (Diseño de la solución).
# (peso_kg, valor_nutricional, dias_para_vencer)
EJEMPLO_MANO: list[Lote] = [
    (6, 12, 1),  # L0 arroz (otros)
    (1, 9, 2),  # L1 atún (proteína)
    (4, 16, 3),  # L2 guayaba (frutas y verduras)
    (1, 6, 4),  # L3 tomate (frutas y verduras)
    (6, 18, 5),  # L4 fríjol (proteína)
]
CAPACIDAD_MANO = 10


def peso_de(lotes: list[Lote], indices: list[int]) -> int:
    """Suma el peso de los lotes elegidos.

    Args:
        lotes: lotes candidatos.
        indices: índices de los lotes cargados.

    Returns:
        El peso total en kg.
    """
    return sum(lotes[i][0] for i in indices)


def valor_de(lotes: list[Lote], indices: list[int]) -> int:
    """Suma el valor nutricional de los lotes elegidos.

    Args:
        lotes: lotes candidatos.
        indices: índices de los lotes cargados.

    Returns:
        El valor nutricional total.
    """
    return sum(lotes[i][1] for i in indices)


def es_carga_valida(lotes: list[Lote], capacidad: int, indices: list[int]) -> bool:
    """Revisa la restricción del negocio sobre una carga.

    Ningún vehículo supera su capacidad y ningún lote se fracciona ni se
    repite: cada índice aparece a lo sumo una vez y corresponde a un lote
    completo de la lista.

    Args:
        lotes: lotes candidatos.
        capacidad: capacidad del vehículo en kg.
        indices: índices de los lotes cargados.

    Returns:
        True si la carga respeta las restricciones.
    """
    sin_repetidos = len(indices) == len(set(indices))
    indices_validos = all(0 <= i < len(lotes) for i in indices)
    return sin_repetidos and indices_validos and peso_de(lotes, indices) <= capacidad


def probar_casos_limite() -> None:
    """Prueba entrada vacía, un lote, nada cabe, todo cabe y capacidad 0."""
    assert cargar_vehiculo([], 100) == (0, [])
    assert cargar_exhaustivo([], 100) == (0, [])
    assert cargar_vehiculo([(30, 90, 2)], 50) == (90, [0])
    assert cargar_vehiculo([(30, 90, 2)], 29) == (0, [])  # un lote que no cabe
    nada_cabe = [(60, 10, 1), (70, 20, 2), (80, 30, 3)]
    assert cargar_vehiculo(nada_cabe, 50) == (0, [])
    assert cargar_exhaustivo(nada_cabe, 50) == (0, [])
    todo_cabe = [(10, 5, 3), (20, 8, 1), (5, 4, 2)]
    assert cargar_vehiculo(todo_cabe, 100) == (17, [0, 1, 2])
    assert cargar_vehiculo(todo_cabe, 0) == (0, [])
    exacto = [(25, 10, 1), (25, 10, 2)]  # llenan justo la capacidad
    assert cargar_vehiculo(exacto, 50) == (20, [0, 1])
    try:
        cargar_vehiculo(todo_cabe, -1)
        raise AssertionError("una capacidad negativa debe rechazarse")
    except ValueError:
        pass


def probar_ejemplo_a_mano() -> None:
    """Comprueba el ejemplo de 5 lotes que se resolvió a mano en el informe."""
    valor, elegidos = cargar_vehiculo(EJEMPLO_MANO, CAPACIDAD_MANO)
    assert valor == 34
    assert elegidos == [2, 4]  # guayaba y fríjol, 10 kg exactos
    assert cargar_exhaustivo(EJEMPLO_MANO, CAPACIDAD_MANO) == (34, [2, 4])


def probar_contraejemplo_reglas() -> None:
    """Comprueba el contraejemplo: las dos reglas quedan por debajo del óptimo."""
    venc_valor, venc_elegidos = cargar_por_vencimiento(EJEMPLO_MANO, CAPACIDAD_MANO)
    assert (venc_valor, venc_elegidos) == (21, [0, 1])  # 7 kg, para en L2
    dens_valor, dens_elegidos = cargar_por_densidad(EJEMPLO_MANO, CAPACIDAD_MANO)
    assert (dens_valor, dens_elegidos) == (31, [1, 2, 3])  # 6 kg
    optimo, _ = cargar_vehiculo(EJEMPLO_MANO, CAPACIDAD_MANO)
    assert venc_valor < optimo and dens_valor < optimo
    assert optimo - venc_valor == 13 and optimo - dens_valor == 3


def probar_no_despacha_vencidos() -> None:
    """Ningún lote vencido (0 días o menos para vencer) se carga."""
    lotes = [(5, 100, 0), (5, 10, 3), (5, 90, -2), (5, 20, 1)]
    for solucion in (
        cargar_vehiculo,
        cargar_exhaustivo,
        cargar_por_vencimiento,
        cargar_por_densidad,
    ):
        valor, elegidos = solucion(lotes, 20)
        assert all(lotes[i][2] > 0 for i in elegidos), solucion.__name__
        assert valor == 30, solucion.__name__


def probar_aleatorias(casos: int = 300, semilla: int = 2026) -> None:
    """Compara la programación dinámica con la exhaustiva en instancias al azar.

    Además de que el valor coincida, verifica que la reconstrucción respete
    la capacidad y sume exactamente el valor óptimo, y que las dos reglas
    nunca superen el óptimo ni la capacidad.

    Args:
        casos: número de instancias aleatorias (mínimo 20 según la guía).
        semilla: semilla fija para que el resultado sea reproducible.
    """
    rng = random.Random(semilla)
    for caso in range(casos):
        n = rng.randint(0, 12)
        lotes, capacidad = generar_instancia_pequena(n, semilla + caso)
        capacidad = rng.choice([capacidad, rng.randint(0, 60)])
        valor_pd, elegidos_pd = cargar_vehiculo(lotes, capacidad)
        valor_ex, elegidos_ex = cargar_exhaustivo(lotes, capacidad)
        assert valor_pd == valor_ex, (lotes, capacidad)
        assert es_carga_valida(lotes, capacidad, elegidos_pd), (lotes, capacidad)
        assert valor_de(lotes, elegidos_pd) == valor_pd, (lotes, capacidad)
        assert es_carga_valida(lotes, capacidad, elegidos_ex), (lotes, capacidad)
        for regla in (cargar_por_vencimiento, cargar_por_densidad):
            valor_r, elegidos_r = regla(lotes, capacidad)
            assert valor_r <= valor_pd, (regla.__name__, lotes, capacidad)
            assert es_carga_valida(lotes, capacidad, elegidos_r)


def probar_no_modifica_entrada() -> None:
    """Verifica que ninguna solución altere la lista original de lotes."""
    lotes, capacidad = generar_instancia_pequena(10, 99)
    copia = list(lotes)
    for solucion in (
        cargar_vehiculo,
        cargar_exhaustivo,
        cargar_por_vencimiento,
        cargar_por_densidad,
    ):
        solucion(lotes, capacidad)
        assert lotes == copia, solucion.__name__


def main() -> None:
    """Ejecuta todas las pruebas e informa el resultado."""
    probar_casos_limite()
    probar_ejemplo_a_mano()
    probar_contraejemplo_reglas()
    probar_no_despacha_vencidos()
    probar_aleatorias()
    probar_no_modifica_entrada()
    print("cargue_vehiculos: todas las pruebas pasaron")


if __name__ == "__main__":
    main()
