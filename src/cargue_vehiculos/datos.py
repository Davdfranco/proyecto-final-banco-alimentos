"""Generador de instancias sintéticas del cargue, con semilla fija.

Cada lote es (peso_kg, valor_nutricional, dias_para_vencer). El valor
nutricional son las raciones del lote ponderadas por la prioridad de su
categoría, como lo describe el caso:

- proteína: prioridad 3
- frutas y verduras: prioridad 2
- otros: prioridad 1

En la bodega hay dos tipos de lote: cajas o canastillas sueltas (livianas) y
estibas completas (pesadas). La mezcla de los dos es lo que hace que la regla
de "cargar por vencimiento hasta que no quepa el siguiente" deje el vehículo
a medio llenar.
"""

import random

Lote = tuple[int, int, int]  # (peso_kg, valor_nutricional, dias_para_vencer)

PRIORIDADES: dict[str, int] = {"proteina": 3, "frutas_verduras": 2, "otros": 1}
PROB_CATEGORIA: dict[str, float] = {
    "proteina": 0.25,
    "frutas_verduras": 0.35,
    "otros": 0.40,
}
# Forma de los lotes en las rutas reales: (prob. de estiba, caja máx., estiba mín., estiba máx.)
FORMA_REAL: tuple[float, int, int, int] = (0.06, 15, 400, 1500)
# Forma a escala para las instancias pequeñas que se comparan con la exhaustiva.
FORMA_PEQUENA: tuple[float, int, int, int] = (0.25, 5, 10, 40)
DIAS_MAX = 30  # días para vencer de un lote recién llegado

# Volumen real del caso (enunciado del proyecto).
VEHICULOS_REALES = 14
LOTES_MIN, LOTES_MAX = 300, 600
CAPACIDAD_MIN, CAPACIDAD_MAX = 2500, 4000


def elegir_categoria(rng: random.Random) -> str:
    """Sortea la categoría de un lote según la mezcla de la bodega.

    Args:
        rng: generador aleatorio con semilla fija.

    Returns:
        El nombre de la categoría.
    """
    categorias = list(PROB_CATEGORIA)
    pesos = list(PROB_CATEGORIA.values())
    return rng.choices(categorias, weights=pesos, k=1)[0]


def generar_lote(rng: random.Random, forma: tuple[float, int, int, int]) -> Lote:
    """Genera un lote sintético.

    Args:
        rng: generador aleatorio con semilla fija.
        forma: (probabilidad de estiba, peso máximo de una caja, peso mínimo
            y peso máximo de una estiba), en kg.

    Returns:
        Un lote (peso_kg, valor_nutricional, dias_para_vencer).
    """
    prob_estiba, caja_max, estiba_min, estiba_max = forma
    if rng.random() < prob_estiba:
        peso = rng.randint(estiba_min, estiba_max)  # estiba completa
    else:
        peso = rng.randint(1, caja_max)  # caja o canastilla
    categoria = elegir_categoria(rng)
    raciones = peso * rng.randint(2, 5)  # entre 2 y 5 raciones por kg
    valor = raciones * PRIORIDADES[categoria]
    dias = rng.randint(1, DIAS_MAX)
    return peso, valor, dias


def generar_lotes(
    n: int, semilla: int, forma: tuple[float, int, int, int] = FORMA_REAL
) -> list[Lote]:
    """Genera n lotes candidatos de una ruta.

    Args:
        n: número de lotes.
        semilla: semilla fija para reproducir la instancia.
        forma: forma de los lotes (ver generar_lote).

    Returns:
        La lista de lotes.
    """
    rng = random.Random(semilla)
    return [generar_lote(rng, forma) for _ in range(n)]


def generar_instancia_pequena(n: int, semilla: int) -> tuple[list[Lote], int]:
    """Genera una instancia pequeña, a escala, para comparar con la exhaustiva.

    Conserva la estructura del caso (cajas y estibas, tres categorías) pero
    con pesos de 1 a 40 kg y una capacidad cercana al 40 % del peso total,
    para que el problema no sea trivial (ni todo cabe ni nada cabe).

    Args:
        n: número de lotes.
        semilla: semilla fija para reproducir la instancia.

    Returns:
        La pareja (lotes, capacidad_kg).
    """
    lotes = generar_lotes(n, semilla, FORMA_PEQUENA)
    total = sum(lote[0] for lote in lotes)
    capacidad = max(1, int(total * 0.4))
    return lotes, capacidad


def generar_ruta_real(semilla: int) -> tuple[list[Lote], int]:
    """Genera una ruta con el volumen real del caso.

    Args:
        semilla: semilla fija para reproducir la instancia.

    Returns:
        La pareja (lotes, capacidad_kg), con 300 a 600 lotes y una capacidad
        entre 2.500 y 4.000 kg.
    """
    rng = random.Random(semilla)
    n = rng.randint(LOTES_MIN, LOTES_MAX)
    capacidad = rng.randint(CAPACIDAD_MIN, CAPACIDAD_MAX)
    return generar_lotes(n, semilla + 1), capacidad


def generar_dia_real(semilla: int) -> list[tuple[list[Lote], int]]:
    """Genera las 14 rutas de un día de operación.

    Args:
        semilla: semilla fija para reproducir el día.

    Returns:
        Una lista con una pareja (lotes, capacidad_kg) por vehículo.
    """
    return [generar_ruta_real(semilla * 100 + v) for v in range(VEHICULOS_REALES)]
