"""Experimentos y gráficas del análisis de saturación de la bodega.

Ejecutar desde la raíz del repositorio:

    python -m src.saturacion_bodega.medicion

Genera las gráficas en graficas/saturacion_bodega/ y las tablas en
resultados/saturacion_bodega/. Las series se generan antes de cronometrar y
las operaciones se cuentan en una corrida aparte.
"""

import csv
import json
import math
import time
from collections.abc import Callable
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .contador import Contador  # noqa: E402
from .datos import (  # noqa: E402
    CATEGORIAS_REALES,
    HORAS_HISTORICO,
    generar_categorias,
    generar_serie,
)
from .dividir_vencer import tramo_dividir_vencer  # noqa: E402
from .estrategia import Tramo, tramo_kadane  # noqa: E402
from .regla_actual import tramo_fuerza_bruta  # noqa: E402

Solucion = Callable[..., Tramo]

RAIZ = Path(__file__).resolve().parents[2]
CARPETA_GRAFICAS = RAIZ / "graficas" / "saturacion_bodega"
CARPETA_RESULTADOS = RAIZ / "resultados" / "saturacion_bodega"

TAMANOS_COMUNES = [250, 500, 1000, 2000, 4000, 8000]  # aquí corre la fuerza bruta
TAMANOS_GRANDES = [9000, 18000, 36000, 72000, 144000, 288000]
POTENCIA_KW = 0.150
CORRIDAS_POR_ANIO = 12  # supuesto: el análisis se actualiza una vez al mes

SOLUCIONES: dict[str, Solucion] = {
    "fuerza_bruta": tramo_fuerza_bruta,
    "dividir_vencer": tramo_dividir_vencer,
    "kadane": tramo_kadane,
}
ETIQUETAS = {
    "fuerza_bruta": "Actual: todos los tramos Θ(n²)",
    "dividir_vencer": "Dividir y vencer Θ(n log n)",
    "kadane": "Kadane (PD) Θ(n)",
}
COLORES = {"fuerza_bruta": "#eb6834", "dividir_vencer": "#1baf7a", "kadane": "#2a78d6"}
MARCADORES = {"fuerza_bruta": "s", "dividir_vencer": "^", "kadane": "o"}


def cronometrar(solucion: Solucion, cambios: list[int],
                repeticiones: int) -> tuple[float, Tramo]:
    """Mide el tiempo medio de una solución sobre la misma serie.

    Args:
        solucion: función a medir.
        cambios: serie generada antes de medir.
        repeticiones: veces que se ejecuta para promediar.

    Returns:
        El tiempo medio en segundos y el tramo que devolvió.
    """
    total = 0.0
    tramo: Tramo = (0, 0, 0)
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        tramo = solucion(cambios)
        total += time.perf_counter() - inicio
    return total / repeticiones, tramo


def contar(solucion: Solucion, cambios: list[int]) -> int:
    """Cuenta las operaciones elementales de una solución.

    Args:
        solucion: función a medir.
        cambios: serie de cambios netos.

    Returns:
        El número de operaciones contadas.
    """
    contador = Contador()
    solucion(cambios, contador)
    return contador.total


def medir(tamanos: list[int], nombres: list[str],
          repeticiones: dict[str, int]) -> list[dict[str, float]]:
    """Mide tiempo y operaciones de varias soluciones en tamaños crecientes.

    Verifica, dentro del experimento, que todas den el mismo crecimiento.

    Args:
        tamanos: longitudes n de la serie.
        nombres: claves de SOLUCIONES a medir.
        repeticiones: repeticiones por solución.

    Returns:
        Una fila por tamaño.
    """
    filas = []
    for n in tamanos:
        cambios = generar_serie(n, 4000 + n)
        fila: dict[str, float] = {"n": n}
        valores = set()
        for nombre in nombres:
            tiempo, tramo = cronometrar(SOLUCIONES[nombre], cambios,
                                        repeticiones[nombre])
            fila[f"t_{nombre}"] = tiempo
            fila[f"ops_{nombre}"] = contar(SOLUCIONES[nombre], cambios)
            valores.add(tramo[0])
        assert len(valores) == 1, f"las soluciones no coinciden con n={n}"
        filas.append(fila)
        print(f"  n={n:>7}: " + " | ".join(
            f"{x} {fila['t_' + x] * 1e3:9.2f} ms" for x in nombres))
    return filas


def volumen_real() -> dict[str, float]:
    """Mide las estrategias rápidas sobre las 40 categorías de 36.000 horas.

    Returns:
        El tiempo total en segundos de dividir y vencer y de Kadane.
    """
    series = generar_categorias(CATEGORIAS_REALES, HORAS_HISTORICO, 7000)
    resultado = {}
    for nombre in ("dividir_vencer", "kadane"):
        inicio = time.perf_counter()
        for cambios in series.values():
            SOLUCIONES[nombre](cambios)
        resultado[f"seg_40cat_{nombre}"] = time.perf_counter() - inicio
    return resultado


def guardar_csv(filas: list[dict[str, float]], nombre: str) -> None:
    """Guarda las filas de un experimento como CSV.

    Args:
        filas: resultados del experimento.
        nombre: nombre del archivo sin extensión.
    """
    CARPETA_RESULTADOS.mkdir(parents=True, exist_ok=True)
    with open(CARPETA_RESULTADOS / f"{nombre}.csv", "w", newline="",
              encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)


def factor(filas: list[dict[str, float]], a: int, b: int, campo: str) -> float:
    """Calcula cuánto se multiplica un campo al pasar de n = a a n = b.

    Args:
        filas: resultados del experimento.
        a: tamaño inicial.
        b: tamaño final.
        campo: columna medida.

    Returns:
        El cociente campo(b) / campo(a).
    """
    valor_a = next(f[campo] for f in filas if f["n"] == a)
    valor_b = next(f[campo] for f in filas if f["n"] == b)
    return valor_b / valor_a


def estilo_ejes(eje: plt.Axes, titulo: str, x: str, y: str) -> None:
    """Aplica título, rótulos, rejilla discreta y leyenda a unos ejes.

    Args:
        eje: ejes de matplotlib.
        titulo: título del panel.
        x: rótulo del eje x con unidades.
        y: rótulo del eje y con unidades.
    """
    eje.set_title(titulo, fontsize=11)
    eje.set_xlabel(x)
    eje.set_ylabel(y)
    eje.grid(True, alpha=0.25)
    for lado in ("top", "right"):
        eje.spines[lado].set_visible(False)
    eje.legend(fontsize=8, frameon=False)


def trazar(eje: plt.Axes, filas: list[dict[str, float]], campo: str,
           nombres: list[str], escala: float = 1.0) -> None:
    """Dibuja una serie por solución.

    Args:
        eje: ejes de matplotlib.
        filas: resultados del experimento.
        campo: prefijo del campo ("t" u "ops").
        nombres: soluciones a dibujar.
        escala: factor de cambio de unidades.
    """
    for nombre in nombres:
        eje.plot([f["n"] for f in filas], [f[f"{campo}_{nombre}"] * escala for f in filas],
                 marker=MARCADORES[nombre], color=COLORES[nombre], linewidth=2,
                 markersize=6, label=ETIQUETAS[nombre])


def graficas_vs_n(comunes: list[dict], grandes: list[dict], campo: str,
                  archivo: str, rotulo: str, escala: float) -> None:
    """Produce una gráfica de dos paneles frente a n.

    Args:
        comunes: tamaños donde corren las tres soluciones.
        grandes: tamaños grandes, solo las dos rápidas.
        campo: "t" u "ops".
        archivo: nombre del PNG.
        rotulo: rótulo del eje y con unidades.
        escala: factor de cambio de unidades.
    """
    figura, (izq, der) = plt.subplots(1, 2, figsize=(13, 5))
    trazar(izq, comunes, campo, list(SOLUCIONES), escala)
    izq.set_xscale("log", base=2)
    izq.set_yscale("log")
    estilo_ejes(izq, "Las tres soluciones (ejes log-log)",
                "Horas de la serie n (escala log)",
                rotulo.replace(")", ", escala log)", 1))
    trazar(der, grandes, campo, ["dividir_vencer", "kadane"], escala)
    estilo_ejes(der, "Solo las estrategias rápidas, n grande",
                "Horas de la serie n", rotulo)
    der.axvline(HORAS_HISTORICO, color="#52514e", linestyle="--", linewidth=1)
    der.text(HORAS_HISTORICO * 1.05, der.get_ylim()[1] * 0.9,
             "10 años de histórico\n(36.000 h)", fontsize=8, color="#52514e")
    if campo == "ops":
        der.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    figura.suptitle(f"Análisis de saturación: {rotulo.split(' (')[0].lower()} frente a n")
    figura.tight_layout()
    figura.savefig(CARPETA_GRAFICAS / archivo, dpi=150)
    plt.close(figura)


def grafica_volumen_real(resumen: dict[str, float]) -> None:
    """Produce graficas/saturacion_bodega/volumen_real.png.

    Barras con el tiempo de las 40 categorías de 36.000 horas: medido para
    las estrategias rápidas y extrapolado para la fuerza bruta.

    Args:
        resumen: cifras calculadas en resumir.
    """
    nombres = ["fuerza_bruta", "dividir_vencer", "kadane"]
    valores = [resumen["seg_40cat_fuerza_bruta_estimado"],
               resumen["seg_40cat_dividir_vencer"], resumen["seg_40cat_kadane"]]
    figura, eje = plt.subplots(figsize=(9, 4.5))
    barras = eje.bar([ETIQUETAS[x] for x in nombres], valores,
                     color=[COLORES[x] for x in nombres], width=0.6)
    eje.set_yscale("log")
    for barra, valor, nombre in zip(barras, valores, nombres):
        texto = (f"{valor / 60:.1f} min (estimado)" if nombre == "fuerza_bruta"
                 else f"{valor:.2f} s (medido)")
        eje.text(barra.get_x() + barra.get_width() / 2, valor * 1.4, texto,
                 ha="center", fontsize=9)
    eje.set_ylim(top=max(valores) * 20)
    eje.set_ylabel("Tiempo total (s, escala log)")
    eje.set_title("40 categorías × 36.000 horas (10 años de histórico)")
    eje.grid(True, axis="y", alpha=0.25)
    for lado in ("top", "right"):
        eje.spines[lado].set_visible(False)
    eje.tick_params(axis="x", labelsize=9)
    figura.tight_layout()
    figura.savefig(CARPETA_GRAFICAS / "volumen_real.png", dpi=150)
    plt.close(figura)


def resumir(comunes: list[dict], grandes: list[dict],
            real: dict[str, float]) -> dict[str, float]:
    """Calcula factores al duplicar, extrapolación y energía.

    La fuerza bruta se extrapola con la forma cuadrática medida: el tiempo
    de n = 8.000 por (36.000 / 8.000)², por 40 categorías.

    Args:
        comunes: resultados con las tres soluciones.
        grandes: resultados de las estrategias rápidas.
        real: tiempos medidos en el volumen real.

    Returns:
        Las cifras que se citan en el informe.
    """
    resumen = dict(real)
    for nombre in SOLUCIONES:
        for campo in ("t", "ops"):
            resumen[f"factor_4000_8000_{campo}_{nombre}"] = factor(
                comunes, 4000, 8000, f"{campo}_{nombre}")
    for nombre in ("dividir_vencer", "kadane"):
        for campo in ("t", "ops"):
            resumen[f"factor_36000_72000_{campo}_{nombre}"] = factor(
                grandes, 36000, 72000, f"{campo}_{nombre}")
    t_8000 = next(f["t_fuerza_bruta"] for f in comunes if f["n"] == 8000)
    por_categoria = t_8000 * (HORAS_HISTORICO / 8000) ** 2
    resumen["seg_1cat_fuerza_bruta_estimado"] = por_categoria
    resumen["seg_40cat_fuerza_bruta_estimado"] = por_categoria * CATEGORIAS_REALES
    resumen["seg_80cat_fuerza_bruta_estimado"] = por_categoria * 2 * CATEGORIAS_REALES
    # Contraste con la forma n log n para dividir y vencer.
    esperado_dyv = 2 * math.log2(72000) / math.log2(36000)
    resumen["factor_esperado_dyv_36000_72000"] = esperado_dyv
    for nombre in ("fuerza_bruta", "dividir_vencer", "kadane"):
        clave = "seg_40cat_fuerza_bruta_estimado" if nombre == "fuerza_bruta" \
            else f"seg_40cat_{nombre}"
        kwh = POTENCIA_KW * resumen[clave] / 3600
        resumen[f"kwh_corrida_{nombre}"] = kwh
        resumen[f"kwh_anio_{nombre}"] = kwh * CORRIDAS_POR_ANIO
    return resumen


def main() -> None:
    """Corre los experimentos y guarda tablas, gráficas y el resumen."""
    CARPETA_GRAFICAS.mkdir(parents=True, exist_ok=True)
    print("Experimento 1: las tres soluciones en tamaños comunes")
    comunes = medir(TAMANOS_COMUNES, list(SOLUCIONES),
                    {"fuerza_bruta": 3, "dividir_vencer": 10, "kadane": 30})
    print("Experimento 2: estrategias rápidas con n grande")
    grandes = medir(TAMANOS_GRANDES, ["dividir_vencer", "kadane"],
                    {"dividir_vencer": 5, "kadane": 20})
    print("Experimento 3: volumen real (40 categorías × 36.000 horas)")
    real = volumen_real()
    guardar_csv(comunes, "comunes")
    guardar_csv(grandes, "grandes")
    resumen = resumir(comunes, grandes, real)
    graficas_vs_n(comunes, grandes, "t", "tiempo_vs_n.png", "Tiempo medio (ms)", 1000)
    graficas_vs_n(comunes, grandes, "ops", "operaciones_vs_n.png",
                  "Operaciones elementales (tramos u horas recorridas)", 1)
    grafica_volumen_real(resumen)
    with open(CARPETA_RESULTADOS / "resumen.json", "w", encoding="utf-8") as archivo:
        json.dump(resumen, archivo, indent=2, ensure_ascii=False)
    for clave, valor in resumen.items():
        print(f"  {clave}: {valor:.6g}")
    print("Listo: gráficas en graficas/saturacion_bodega/")


if __name__ == "__main__":
    main()
