# -*- coding: utf-8 -*-
"""Suma las fotos de los activos de CMD DENTRO de la seccion 'Imagenes' del
index (CATS_IMG), como categorias mas. Asi los contadores de la galeria las
cuentan solas. Idempotente: se puede correr las veces que haga falta."""
import os, io, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = os.path.join(REPO, "index.html")
ACT = os.path.join(REPO, "media", "activos")

MARCA_INI = "  /* === ACTIVOS CMD (generado por rutina/_inyectar_activos.py) === */"
MARCA_FIN = "  /* === FIN ACTIVOS CMD === */"

# datos comerciales (planilla "Cia. MD - Inventario de Activos" del Drive)
META = {
    "INM-001": ("Depto 1 dorm · Torre Aymará", "Posadas · Beethoven 1650",
                "USD 66.000 · 69 m² · un dormitorio con balcón. Dos unidades: pisos 7 y 13."),
    "INM-002": ("Terreno Río Paraná", "Oberá · casi Dinamarca",
                "USD 50.000 · 12 × 50 m · un lote."),
    "INM-003": ("Lotes zona Aeródromo", "Oberá",
                "USD 25.000 c/u · 12,5 × 32,5 m · dos lotes disponibles."),
    "INM-004": ("Lotes zona Colectora", "Oberá · casi Picada Sarmiento",
                "USD 25.000 c/u · 12,5 × 37,5 m · dos lotes disponibles."),
    "INM-005": ("Hectáreas Ruta 117", "Paso de los Libres · Corrientes",
                "Precio a confirmar · 2 hectáreas sobre la entrada."),
    "INM-006": ("Hectáreas Ruta 14", "San José · entrada a Misiones",
                "Precio a confirmar · 1,5 hectáreas."),
    "INM-008": ("Solares de Loreto · el loteo", "Loreto · Candelaria",
                "Desde USD 8.000 · lotes de 490 a 1.250 m² con financiación propia."),
    "INM-009": ("Terraza rooftop Aymará", "Posadas · Beethoven 1650",
                "Precio a confirmar · 630 m² de terraza rooftop."),
    "INM-010": ("Local planta baja Aymará", "Posadas · Beethoven 1650",
                "Precio a confirmar · 30 m² a la calle."),
}


def js(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def bloque():
    cats, total = [], 0
    for d in sorted(os.listdir(ACT)):
        ruta = os.path.join(ACT, d)
        if not os.path.isdir(ruta):
            continue
        inm = d[:7]
        if inm not in META:
            continue
        nombre, lugar, desc = META[inm]
        fs = sorted(f for f in os.listdir(ruta) if f.lower().endswith(".jpg"))
        if not fs:
            continue
        total += len(fs)
        items = [
            '{{file:"activos/{}/{}", nombre:"{} {:02d}", desc:"{}", drive:"{}"}}'.format(
                d, f, js(nombre), i, js(desc), js("Drive · Cia. MD - Activos / " + inm))
            for i, f in enumerate(fs, 1)
        ]
        cats.append(
            '  {{ id:"{}", nombre:"{}", drive:"{}",\n    items: [\n      {}\n    ] }}'.format(
                inm.lower(), js("{} · {}".format(inm, nombre)), js(lugar),
                ",\n      ".join(items))
        )
    return MARCA_INI + "\n" + ",\n".join(cats) + ",\n" + MARCA_FIN + "\n", total


def main():
    html = io.open(IDX, encoding="utf-8").read()

    # --- limpiar cualquier version anterior ---
    html = re.sub(re.escape(MARCA_INI) + r".*?" + re.escape(MARCA_FIN) + r"\n", "", html, flags=re.S)
    html = re.sub(r"const CATS_ACTIVOS = \[.*?\n\];\n\n", "", html, flags=re.S)
    html = re.sub(r'  \{id:"activos",[^\n]*\n', "", html)

    # --- insertar las categorias DENTRO de CATS_IMG, antes de su cierre ---
    ini = html.index("const CATS_IMG = [")
    fin = html.index("\n];", ini)
    blq, total = bloque()
    html = html[:fin + 1] + blq + html[fin + 1:]

    # --- boton al catalogo en el header (una sola vez) ---
    viejo = '<div class="h-sub">USO INTERNO · <b>CMD</b> · Colonia Santa Ana, Sección Loreto, Candelaria, Misiones</div>'
    nuevo = ('<div class="h-sub">USO INTERNO · <b>CMD</b> · Multimedia de Solares de Loreto + todos los activos de la empresa</div>\n'
             '      <a href="activos.html" style="display:inline-block;margin-top:10px;padding:9px 16px;border-radius:7px;'
             'background:#1B5E20;color:#F4EFE3;font-size:.72rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;'
             'text-decoration:none">Ver cat&aacute;logo de activos &rarr;</a>')
    if viejo in html:
        html = html.replace(viejo, nuevo, 1)

    io.open(IDX, "w", encoding="utf-8").write(html)
    print("Sumadas {} fotos de activos DENTRO de la seccion Imagenes".format(total))


if __name__ == "__main__":
    main()
