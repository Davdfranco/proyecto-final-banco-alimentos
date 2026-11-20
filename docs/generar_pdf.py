"""Genera docs/informe.pdf a partir del README.md del repositorio.

Convierte el Markdown a HTML con la librería markdown y lo imprime a PDF con
Microsoft Edge o Google Chrome en modo headless, para que el PDF tenga
exactamente el mismo contenido que el README.

Uso, desde la raíz del repositorio:

    pip install markdown
    python docs/generar_pdf.py
"""

import shutil
import subprocess
from pathlib import Path

import markdown

RAIZ = Path(__file__).resolve().parents[1]
README = RAIZ / "README.md"
HTML_TEMPORAL = RAIZ / "docs" / "_informe.html"
PDF = RAIZ / "docs" / "informe.pdf"

NAVEGADORES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "msedge",
    "google-chrome",
    "chromium",
    "chromium-browser",
]

ESTILO = """
@page { size: Letter; margin: 14mm 13mm; }
body { font-family: "Segoe UI", Arial, sans-serif; font-size: 9.5pt;
       line-height: 1.3; color: #111; background: #fff; }
h1 { font-size: 20pt; margin-bottom: 4pt; }
h2 { font-size: 15pt; border-bottom: 1px solid #ccc; padding-bottom: 3pt;
     margin-top: 18pt; page-break-after: avoid; }
h3 { font-size: 12.5pt; margin-top: 14pt; page-break-after: avoid; }
h4 { font-size: 11pt; page-break-after: avoid; }
table { border-collapse: collapse; margin: 6pt 0; font-size: 8pt;
        page-break-inside: avoid; }
th, td { border: 1px solid #bbb; padding: 2pt 4pt; vertical-align: top; }
th { background: #f0f0f0; }
code { font-family: Consolas, monospace; font-size: 9pt;
       background: #f5f5f5; padding: 0 2pt; }
pre { background: #f5f5f5; padding: 5pt; font-size: 7.5pt;
      white-space: pre-wrap; page-break-inside: avoid; }
pre code { background: none; padding: 0; }
img { display: block; max-width: 88%; margin: 4pt auto;
      page-break-inside: avoid; }
blockquote { color: #555; border-left: 3px solid #ccc; margin-left: 0;
             padding-left: 8pt; }
"""


def readme_a_html(texto: str) -> str:
    """Convierte el Markdown del informe en un documento HTML completo.

    Args:
        texto: contenido del README.md.

    Returns:
        El HTML, con una etiqueta base para que las rutas relativas de las
        gráficas y los enlaces apunten a la raíz del repositorio.
    """
    cuerpo = markdown.markdown(
        texto, extensions=["tables", "fenced_code", "toc", "sane_lists"]
    )
    base = RAIZ.as_uri() + "/"
    return (
        "<!doctype html><html lang='es'><head><meta charset='utf-8'>"
        f"<base href='{base}'><title>Informe técnico</title>"
        f"<style>{ESTILO}</style></head><body>{cuerpo}</body></html>"
    )


def buscar_navegador() -> str:
    """Busca un navegador basado en Chromium instalado en el equipo.

    Returns:
        La ruta o el nombre del ejecutable encontrado.

    Raises:
        FileNotFoundError: si no hay Edge ni Chrome disponibles.
    """
    for candidato in NAVEGADORES:
        if Path(candidato).exists() or shutil.which(candidato):
            return candidato
    raise FileNotFoundError("No se encontró Microsoft Edge ni Google Chrome")


def imprimir_pdf(html: Path, pdf: Path) -> None:
    """Imprime un archivo HTML a PDF con el navegador en modo headless.

    Args:
        html: archivo HTML de entrada.
        pdf: archivo PDF de salida.
    """
    subprocess.run(
        [
            buscar_navegador(),
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf}",
            html.as_uri(),
        ],
        check=True,
        capture_output=True,
        timeout=180,
    )


def main() -> None:
    """Genera el PDF del informe y borra el HTML temporal."""
    texto = README.read_text(encoding="utf-8")
    HTML_TEMPORAL.write_text(readme_a_html(texto), encoding="utf-8")
    try:
        imprimir_pdf(HTML_TEMPORAL, PDF)
    finally:
        HTML_TEMPORAL.unlink(missing_ok=True)
    print(f"PDF generado: {PDF.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
