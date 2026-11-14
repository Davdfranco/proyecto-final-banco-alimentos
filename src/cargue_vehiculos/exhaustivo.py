"""Solución exhaustiva del cargue: prueba todos los subconjuntos de lotes.

Es la solución exacta con la que se verifica la programación dinámica. Su
costo es Θ(n·2^n), así que solo se usa con pocas decenas de lotes.
"""

from .contador import Contador

Lote = tuple[int, int, int]  # (peso_kg, valor_nutricional, dias_para_vencer)


def evaluar_subconjunto(lotes: list[Lote], mascara: int) -> tuple[int, int]:
    """Suma el peso y el valor de los lotes marcados en una máscara de bits.

    El bit i de la máscara en 1 significa que el lote i sube al vehículo.

    Args:
        lotes: lotes candidatos de la ruta.
        mascara: entero cuyos bits indican qué lotes se cargan.

    Returns:
        La pareja (peso total en kg, valor nutricional total).
    """
    peso = 0
    valor = 0
    for i in range(len(lotes)):
        if mascara >> i & 1:
            peso += lotes[i][0]
            valor += lotes[i][1]
    return peso, valor


def indices_de_mascara(mascara: int, n: int) -> list[int]:
    """Convierte una máscara de bits en la lista de índices encendidos.

    Args:
        mascara: entero cuyos bits indican qué lotes se cargan.
        n: número de lotes.

    Returns:
        Los índices de los bits en 1, en orden creciente.
    """
    return [i for i in range(n) if mascara >> i & 1]


def cargar_exhaustivo(
    lotes: list[Lote], capacidad_kg: int, contador: Contador | None = None
) -> tuple[int, list[int]]:
    """Calcula el mismo resultado probando todos los subconjuntos de lotes.

    Args:
        lotes: lotes candidatos de la ruta.
        capacidad_kg: capacidad máxima del vehículo en kilogramos.
        contador: si se entrega, suma n operaciones por subconjunto revisado.

    Returns:
        El valor nutricional máximo y los índices de los lotes cargados.
    """
    n = len(lotes)
    vencidos = sum(1 << i for i in range(n) if lotes[i][2] <= 0)
    mejor_valor = 0
    mejor_mascara = 0
    for mascara in range(1 << n):  # 2^n subconjuntos
        peso, valor = evaluar_subconjunto(lotes, mascara)
        if contador is not None:
            contador.sumar(n)
        if mascara & vencidos:
            continue  # un subconjunto con un lote vencido no es válido
        if peso <= capacidad_kg and valor > mejor_valor:
            mejor_valor = valor
            mejor_mascara = mascara
    return mejor_valor, indices_de_mascara(mejor_mascara, n)
