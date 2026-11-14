"""Experimentos y gráficas del cargue de vehículos.

Ejecutar desde la raíz del repositorio:

    python -m src.cargue_vehiculos.medicion

Genera las gráficas en graficas/cargue_vehiculos/ y las tablas de resultados
en resultados/cargue_vehiculos/. Los datos se generan antes de cronometrar y
time.perf_counter() rodea solo la llamada a cada solución. Las operaciones se
cuentan en una corrida aparte, para que el contador no ensucie el tiempo.
"""

import csv
import json
import time
from collections.abc import Callable
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .contador import Contador  # noqa: E402
from .datos import (  # noqa: E402
    generar_dia_real,
    generar_instancia_pequena,
    generar_lotes,
)
from .estrategia import Lote, cargar_vehiculo  # noqa: E402
from .exhaustivo import cargar_exhaustivo  # noqa: E402
from .regla_actual import cargar_por_densidad, cargar_por_vencimiento  # noqa: E402

Solucion = Callable[..., tuple[int, list[int]]]

RAIZ = Path(__file__).resolve().parents[2]
CARPETA_GRAFICAS = RAIZ / "graficas" / "cargue_vehiculos"
CARPETA_RESULTADOS = RAIZ / "resultados" / "cargue_vehiculos"

TAMANOS_PEQUENOS = [8, 10, 12, 14, 16, 18, 20]  # pares 8-16 y 10-20
CAPACIDAD_PEQUENA = 120  # kg, fija para que el tiempo de la PD dependa de n
TAMANOS_GRANDES = [75, 150, 300, 600, 1200, 2400]
CAPACIDAD_GRANDE = 3000  # kg, fija
LOTES_FIJOS = 300
CAPACIDADES = [250, 500, 1000, 2000, 4000, 8000]
DIAS_REALES = 10  # días simulados de 14 vehículos cada uno
POTENCIA_KW = 0.150  # computador de la fundación, 150 W
DIAS_OPERACION_ANIO = 300

SOLUCIONES: dict[str, Solucion] = {
    "pd": cargar_vehiculo,
    "exhaustiva": cargar_exhaustivo,
    "vencimiento": cargar_por_vencimiento,
    "densidad": cargar_por_densidad,
}
ETIQUETAS = {
    "pd": "Programación dinámica Θ(n·W)",
    "exhaustiva": "Exhaustiva Θ(n·2ⁿ)",
    "vencimiento": "Regla actual: por vencimiento Θ(n log n)",
    "densidad": "Voraz por densidad Θ(n log n)",
}
COLORES = {  # paleta categórica validada, en orden fijo
    "pd": "#2a78d6",
    "exhaustiva": "#eb6834",
    "vencimiento": "#1baf7a",
    "densidad": "#eda100",
}
MARCADORES = {"pd": "o", "exhaustiva": "s", "vencimiento": "^", "densidad": "D"}


def cronometrar(
    solucion: Solucion, lotes: list[Lote], capacidad: int, repeticiones: int
) -> tuple[float, int]:
    """Mide el tiempo medio de una solución sobre una misma instancia.

    Args:
        solucion: función de cargue a medir.
        lotes: lotes candidatos (generados antes de medir).
        capacidad: capacidad del vehículo en kg.
        repeticiones: veces que se ejecuta para promediar.

    Returns:
        El tiempo medio en segundos y el valor que devolvió la solución.
    """
    total = 0.0
    valor = 0
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        valor, _ = solucion(lotes, capacidad)
        total += time.perf_counter() - inicio
    return total / repeticiones, valor


def contar(solucion: Solucion, lotes: list[Lote], capacidad: int) -> int:
    """Cuenta las operaciones elementales de una solución en una instancia.

    Args:
        solucion: función de cargue.
        lotes: lotes candidatos.
        capacidad: capacidad del vehículo en kg.

    Returns:
        El número de operaciones contadas.
    """
    contador = Contador()
    solucion(lotes, capacidad, contador)
    return contador.total


def medir_instancia(
    lotes: list[Lote], capacidad: int, nombres: list[str], repeticiones: dict[str, int]
) -> dict[str, float]:
    """Mide tiempo, operaciones y valor de varias soluciones en una instancia.

    También verifica, dentro del experimento, que la programación dinámica y
    la exhaustiva den el mismo valor cuando ambas se ejecutan.

    Args:
        lotes: lotes candidatos.
        capacidad: capacidad del vehículo en kg.
        nombres: claves de SOLUCIONES que se miden.
        repeticiones: repeticiones por solución.

    Returns:
        Un diccionario con t_<nombre>, ops_<nombre> y valor_<nombre>.
    """
    fila: dict[str, float] = {}
    for nombre in nombres:
        tiempo, valor = cronometrar(
            SOLUCIONES[nombre], lotes, capacidad, repeticiones[nombre]
        )
        fila[f"t_{nombre}"] = tiempo
        fila[f"ops_{nombre}"] = contar(SOLUCIONES[nombre], lotes, capacidad)
        fila[f"valor_{nombre}"] = valor
    if "exhaustiva" in nombres:
        assert fila["valor_pd"] == fila["valor_exhaustiva"], "la PD no es óptima"
    return fila


def experimento_pequenas() -> list[dict[str, float]]:
    """Compara las cuatro soluciones en tamaños que la exhaustiva alcanza.

    Returns:
        Una fila por tamaño n.
    """
    filas = []
    for n in TAMANOS_PEQUENOS:
        lotes, _ = generar_instancia_pequena(n, 1000 + n)
        reps = {"pd": 50, "exhaustiva": 3 if n >= 16 else 5,
                "vencimiento": 50, "densidad": 50}
        fila = {"n": n, "W": CAPACIDAD_PEQUENA}
        fila.update(medir_instancia(lotes, CAPACIDAD_PEQUENA, list(SOLUCIONES), reps))
        filas.append(fila)
        print(f"  pequeñas n={n:>3}: PD {fila['t_pd']*1e3:8.3f} ms | "
              f"exhaustiva {fila['t_exhaustiva']*1e3:10.1f} ms")
    return filas


def experimento_grandes_n() -> list[dict[str, float]]:
    """Mide la PD y las reglas con W fijo y n creciente, sin la exhaustiva.

    Returns:
        Una fila por tamaño n.
    """
    filas = []
    nombres = ["pd", "vencimiento", "densidad"]
    reps = {"pd": 5, "vencimiento": 20, "densidad": 20}
    for n in TAMANOS_GRANDES:
        lotes = generar_lotes(n, 2000 + n)
        fila = {"n": n, "W": CAPACIDAD_GRANDE}
        fila.update(medir_instancia(lotes, CAPACIDAD_GRANDE, nombres, reps))
        filas.append(fila)
        print(f"  grandes n={n:>5}: PD {fila['t_pd']*1e3:8.2f} ms")
    return filas


def experimento_capacidad() -> list[dict[str, float]]:
    """Mide la PD con n fijo y la capacidad W creciente.

    Returns:
        Una fila por capacidad W.
    """
    filas = []
    lotes = generar_lotes(LOTES_FIJOS, 3000)
    nombres = ["pd", "vencimiento", "densidad"]
    reps = {"pd": 5, "vencimiento": 20, "densidad": 20}
    for capacidad in CAPACIDADES:
        fila = {"n": LOTES_FIJOS, "W": capacidad}
        fila.update(medir_instancia(lotes, capacidad, nombres, reps))
        filas.append(fila)
        print(f"  capacidad W={capacidad:>5}: PD {fila['t_pd']*1e3:8.2f} ms")
    return filas


def experimento_dias_reales() -> list[dict[str, float]]:
    """Simula días completos de operación con el volumen real del caso.

    Cada día tiene 14 rutas de 300 a 600 lotes y vehículos de 2.500 a
    4.000 kg. Se mide el tiempo de cada solución y la calidad de la carga.

    Returns:
        Una fila por ruta (vehículo) simulada.
    """
    filas = []
    for dia in range(1, DIAS_REALES + 1):
        for vehiculo, (lotes, capacidad) in enumerate(generar_dia_real(dia)):
            fila: dict[str, float] = {"dia": dia, "vehiculo": vehiculo,
                                      "n": len(lotes), "W": capacidad}
            for nombre in ("pd", "vencimiento", "densidad"):
                inicio = time.perf_counter()
                valor, elegidos = SOLUCIONES[nombre](lotes, capacidad)
                fila[f"t_{nombre}"] = time.perf_counter() - inicio
                fila[f"valor_{nombre}"] = valor
                fila[f"kg_{nombre}"] = sum(lotes[i][0] for i in elegidos)
            filas.append(fila)
        print(f"  día real {dia}: 14 rutas medidas")
    return filas


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


def factor(filas: list[dict[str, float]], eje: str, a: int, b: int,
           campo: str) -> float:
    """Calcula cuánto se multiplica un campo al pasar del tamaño a al b.

    Args:
        filas: resultados del experimento.
        eje: columna del tamaño ("n" o "W").
        a: tamaño inicial.
        b: tamaño final (normalmente el doble de a).
        campo: columna medida (por ejemplo "t_pd").

    Returns:
        El cociente campo(b) / campo(a).
    """
    valor_a = next(f[campo] for f in filas if f[eje] == a)
    valor_b = next(f[campo] for f in filas if f[eje] == b)
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


def trazar(eje: plt.Axes, filas: list[dict[str, float]], x: str, campo: str,
           nombres: list[str], escala: float = 1.0) -> None:
    """Dibuja una serie por solución sobre unos ejes.

    Args:
        eje: ejes de matplotlib.
        filas: resultados del experimento.
        x: columna del eje x.
        campo: prefijo del campo ("t" u "ops").
        nombres: soluciones a dibujar.
        escala: factor para cambiar unidades (por ejemplo 1000 para ms).
    """
    for nombre in nombres:
        eje.plot([f[x] for f in filas], [f[f"{campo}_{nombre}"] * escala for f in filas],
                 marker=MARCADORES[nombre], color=COLORES[nombre], linewidth=2,
                 markersize=6, label=ETIQUETAS[nombre])


def grafica_tiempo_vs_n(pequenas: list[dict], grandes: list[dict]) -> None:
    """Produce graficas/cargue_vehiculos/tiempo_vs_n.png.

    Args:
        pequenas: resultados del experimento con la exhaustiva.
        grandes: resultados de la PD con n grande.
    """
    figura, (izq, der) = plt.subplots(1, 2, figsize=(13, 5))
    trazar(izq, pequenas, "n", "t", list(SOLUCIONES), 1000)
    izq.set_yscale("log")
    estilo_ejes(izq, f"Donde la exhaustiva termina (W = {CAPACIDAD_PEQUENA} kg)",
                "Número de lotes candidatos n", "Tiempo medio (ms, escala log)")
    trazar(der, grandes, "n", "t", ["pd", "vencimiento", "densidad"], 1000)
    estilo_ejes(der, f"Solo PD y reglas, n grande (W = {CAPACIDAD_GRANDE} kg)",
                "Número de lotes candidatos n", "Tiempo medio (ms)")
    figura.suptitle("Cargue de vehículos: tiempo de ejecución frente a n")
    figura.tight_layout()
    figura.savefig(CARPETA_GRAFICAS / "tiempo_vs_n.png", dpi=150)
    plt.close(figura)


def grafica_operaciones_vs_n(pequenas: list[dict], grandes: list[dict]) -> None:
    """Produce graficas/cargue_vehiculos/operaciones_vs_n.png.

    Args:
        pequenas: resultados del experimento con la exhaustiva.
        grandes: resultados de la PD con n grande.
    """
    figura, (izq, der) = plt.subplots(1, 2, figsize=(13, 5))
    trazar(izq, pequenas, "n", "ops", list(SOLUCIONES))
    izq.set_yscale("log")
    estilo_ejes(izq, f"Donde la exhaustiva termina (W = {CAPACIDAD_PEQUENA} kg)",
                "Número de lotes candidatos n",
                "Operaciones elementales (escala log)")
    trazar(der, grandes, "n", "ops", ["pd", "vencimiento", "densidad"])
    estilo_ejes(der, f"Solo PD y reglas, n grande (W = {CAPACIDAD_GRANDE} kg)",
                "Número de lotes candidatos n", "Operaciones elementales")
    der.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    figura.suptitle("Cargue de vehículos: operaciones contadas frente a n "
                    "(casillas, subconjuntos×n, comparaciones)")
    figura.tight_layout()
    figura.savefig(CARPETA_GRAFICAS / "operaciones_vs_n.png", dpi=150)
    plt.close(figura)


def grafica_tiempo_vs_capacidad(filas: list[dict]) -> None:
    """Produce graficas/cargue_vehiculos/tiempo_vs_capacidad.png.

    Args:
        filas: resultados con n fijo y W creciente.
    """
    figura, (izq, der) = plt.subplots(1, 2, figsize=(13, 5))
    trazar(izq, filas, "W", "t", ["pd", "vencimiento", "densidad"], 1000)
    estilo_ejes(izq, f"Tiempo con n = {LOTES_FIJOS} lotes fijos",
                "Capacidad del vehículo W (kg)", "Tiempo medio (ms)")
    trazar(der, filas, "W", "ops", ["pd", "vencimiento", "densidad"])
    estilo_ejes(der, f"Operaciones con n = {LOTES_FIJOS} lotes fijos",
                "Capacidad del vehículo W (kg)", "Operaciones elementales")
    der.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    figura.suptitle("Cargue de vehículos: el costo de la PD crece con W, "
                    "las reglas no dependen de W")
    figura.tight_layout()
    figura.savefig(CARPETA_GRAFICAS / "tiempo_vs_capacidad.png", dpi=150)
    plt.close(figura)


def grafica_calidad(dias: list[dict]) -> None:
    """Produce graficas/cargue_vehiculos/calidad_cargue.png.

    Compara, en las rutas de volumen real, el valor nutricional logrado (como
    % del óptimo) y el uso de la capacidad (% de kg) de cada solución.

    Args:
        dias: resultados de los días reales simulados.
    """
    nombres = ["pd", "densidad", "vencimiento"]
    valor = [100 * sum(f[f"valor_{x}"] for f in dias) / sum(f["valor_pd"] for f in dias)
             for x in nombres]
    llenado = [100 * sum(f[f"kg_{x}"] for f in dias) / sum(f["W"] for f in dias)
               for x in nombres]
    figura, (izq, der) = plt.subplots(1, 2, figsize=(12, 4.5))
    for eje, datos, titulo, rotulo in (
        (izq, valor, "Valor nutricional cargado", "% del óptimo"),
        (der, llenado, "Uso de la capacidad del vehículo", "% de la capacidad (kg)"),
    ):
        barras = eje.bar([ETIQUETAS[x].split(" Θ")[0] for x in nombres], datos,
                         color=[COLORES[x] for x in nombres], width=0.6,
                         edgecolor="white", linewidth=2)
        for barra, dato in zip(barras, datos):
            eje.text(barra.get_x() + barra.get_width() / 2, dato + 1.5,
                     f"{dato:.1f} %", ha="center", fontsize=9)
        eje.set_ylim(0, 112)
        eje.set_title(titulo, fontsize=11)
        eje.set_ylabel(rotulo)
        eje.grid(True, axis="y", alpha=0.25)
        for lado in ("top", "right"):
            eje.spines[lado].set_visible(False)
        eje.tick_params(axis="x", labelsize=8)
    figura.suptitle(f"Calidad de la carga en {len(dias)} rutas de volumen real "
                    f"({DIAS_REALES} días × 14 vehículos)")
    figura.tight_layout()
    figura.savefig(CARPETA_GRAFICAS / "calidad_cargue.png", dpi=150)
    plt.close(figura)


def resumir(pequenas: list[dict], grandes: list[dict], capacidad: list[dict],
            dias: list[dict]) -> dict[str, float]:
    """Calcula los factores al duplicar, la extrapolación y la energía.

    Args:
        pequenas: resultados con la exhaustiva.
        grandes: resultados de la PD con n grande.
        capacidad: resultados con W creciente.
        dias: resultados de los días reales.

    Returns:
        Un diccionario con las cifras que se citan en el informe.
    """
    resumen: dict[str, float] = {}
    for campo in ("t_pd", "ops_pd", "t_exhaustiva", "ops_exhaustiva",
                  "t_vencimiento", "ops_vencimiento"):
        resumen[f"factor_8_16_{campo}"] = factor(pequenas, "n", 8, 16, campo)
        resumen[f"factor_10_20_{campo}"] = factor(pequenas, "n", 10, 20, campo)
    for campo in ("t_pd", "ops_pd", "t_vencimiento", "t_densidad"):
        resumen[f"factor_n_300_600_{campo}"] = factor(grandes, "n", 300, 600, campo)
        resumen[f"factor_n_1200_2400_{campo}"] = factor(grandes, "n", 1200, 2400, campo)
        resumen[f"factor_W_2000_4000_{campo}"] = factor(capacidad, "W", 2000, 4000, campo)
    # Tiempo real por día: suma de las 14 rutas, promediado entre los días.
    for nombre in ("pd", "vencimiento", "densidad"):
        por_dia = sum(f[f"t_{nombre}"] for f in dias) / DIAS_REALES
        resumen[f"seg_por_dia_{nombre}"] = por_dia
        resumen[f"kwh_por_dia_{nombre}"] = POTENCIA_KW * por_dia / 3600
        resumen[f"kwh_anio_{nombre}"] = resumen[f"kwh_por_dia_{nombre}"] * DIAS_OPERACION_ANIO
        resumen[f"pct_valor_{nombre}"] = 100 * sum(f[f"valor_{nombre}"] for f in dias) / sum(
            f["valor_pd"] for f in dias)
        resumen[f"pct_llenado_{nombre}"] = 100 * sum(f[f"kg_{nombre}"] for f in dias) / sum(
            f["W"] for f in dias)
        resumen[f"kg_dia_{nombre}"] = sum(f[f"kg_{nombre}"] for f in dias) / DIAS_REALES
    resumen["peor_ruta_pd_seg"] = max(f["t_pd"] for f in dias)
    resumen["peor_ruta_pd_n"] = max(dias, key=lambda f: f["t_pd"])["n"]
    resumen["peor_ruta_pd_W"] = max(dias, key=lambda f: f["t_pd"])["W"]
    resumen["min_pct_valor_densidad_ruta"] = min(
        100 * f["valor_densidad"] / f["valor_pd"] for f in dias)
    resumen["min_pct_valor_vencimiento_ruta"] = min(
        100 * f["valor_vencimiento"] / f["valor_pd"] for f in dias)
    resumen["t_exhaustiva_n20"] = pequenas[-1]["t_exhaustiva"]
    return resumen


def main() -> None:
    """Corre los cuatro experimentos, guarda tablas, gráficas y el resumen."""
    CARPETA_GRAFICAS.mkdir(parents=True, exist_ok=True)
    print("Experimento 1: tamaños pequeños (PD, exhaustiva y reglas)")
    pequenas = experimento_pequenas()
    print("Experimento 2: n grande con W fijo")
    grandes = experimento_grandes_n()
    print("Experimento 3: W creciente con n fijo")
    capacidad = experimento_capacidad()
    print("Experimento 4: días con el volumen real del caso")
    dias = experimento_dias_reales()
    for filas, nombre in ((pequenas, "pequenas"), (grandes, "grandes_n"),
                          (capacidad, "capacidad"), (dias, "dias_reales")):
        guardar_csv(filas, nombre)
    grafica_tiempo_vs_n(pequenas, grandes)
    grafica_operaciones_vs_n(pequenas, grandes)
    grafica_tiempo_vs_capacidad(capacidad)
    grafica_calidad(dias)
    resumen = resumir(pequenas, grandes, capacidad, dias)
    with open(CARPETA_RESULTADOS / "resumen.json", "w", encoding="utf-8") as archivo:
        json.dump(resumen, archivo, indent=2, ensure_ascii=False)
    for clave, valor in resumen.items():
        print(f"  {clave}: {valor:.6g}")
    print("Listo: gráficas en graficas/cargue_vehiculos/")


if __name__ == "__main__":
    main()
