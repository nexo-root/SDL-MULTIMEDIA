# -*- coding: utf-8 -*-
"""Agrega la pestana 'Activos CMD' al index.html de la galeria, con las fotos
de todos los inmuebles disponibles, y un boton al catalogo completo."""
import os, io, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = os.path.join(REPO, "index.html")
ACT = os.path.join(REPO, "media", "activos")

# datos comerciales (planilla "Cia. MD - Inventario de Activos")
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
    "INM-008": ("Solares de Loreto", "Loreto · Candelaria",
                "Desde USD 8.000 · lotes de 490 a 1.250 m² con financiación propia."),
    "INM-009": ("Terraza rooftop Aymará", "Posadas · Beethoven 1650",
                "Precio a confirmar · 630 m² de terraza rooftop."),
    "INM-010": ("Local planta baja Aymará", "Posadas · Beethoven 1650",
                "Precio a confirmar · 30 m² a la calle."),
}


def js(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def construir():
    cats = []
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
        items = []
        for i, f in enumerate(fs, 1):
            items.append(
                '{{file:"activos/{}/{}", nombre:"{} {:02d}", desc:"{}", drive:"{}"}}'.format(
                    d, f, js(nombre), i, js(desc), js(lugar))
            )
        cats.append(
            '  {{ id:"{}", nombre:"{}", drive:"{}",\n    items: [\n      {}\n    ] }}'.format(
                inm.lower(), js("{} · {}".format(inm, nombre)), js(lugar),
                ",\n      ".join(items))
        )
    return "const CATS_ACTIVOS = [\n" + ",\n".join(cats) + "\n];\n\n"


def main():
    html = io.open(IDX, encoding="utf-8").read()

    # limpiar una inyeccion previa, para poder correrlo de nuevo
    html = re.sub(r"const CATS_ACTIVOS = \[.*?\n\];\n\n", "", html, flags=re.S)
    html = html.replace(
        '  {id:"activos", ico:"\U0001F3D8️", nombre:"Activos CMD", des:"Todos los inmuebles disponibles", cats:CATS_ACTIVOS, espejo:false},\n', "")

    # 1) el array, justo antes de SECCIONES
    ancla = "const SECCIONES = ["
    assert ancla in html, "no encontre SECCIONES"
    html = html.replace(ancla, construir() + ancla, 1)

    # 2) la pestana, primera de la lista
    html = html.replace(
        ancla + '\n  {id:"imagenes"',
        ancla + '\n  {id:"activos", ico:"\U0001F3D8️", nombre:"Activos CMD", des:"Todos los inmuebles disponibles", cats:CATS_ACTIVOS, espejo:false},\n  {id:"imagenes"',
        1)

    # 3) titulo y boton al catalogo en el header
    viejo = '<div class="h-sub">USO INTERNO · <b>CMD</b> · Colonia Santa Ana, Sección Loreto, Candelaria, Misiones</div>'
    nuevo = ('<div class="h-sub">USO INTERNO · <b>CMD</b> · Multimedia de Solares de Loreto + todos los activos de la empresa</div>\n'
             '      <a href="activos.html" style="display:inline-block;margin-top:10px;padding:9px 16px;border-radius:7px;'
             'background:#1B5E20;color:#F4EFE3;font-size:.72rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;'
             'text-decoration:none">Ver cat&aacute;logo de activos &rarr;</a>')
    if viejo in html:
        html = html.replace(viejo, nuevo, 1)

    io.open(IDX, "w", encoding="utf-8").write(html)
    n = html.count('file:"activos/')
    print("index.html actualizado: pestana 'Activos CMD' con {} fotos".format(n))


if __name__ == "__main__":
    main()
