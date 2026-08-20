# -*- coding: utf-8 -*-
"""Genera activos.html: catalogo visual de los activos de CMD.
Los datos salen de la planilla 'Cia. MD - Inventario de Activos' del Drive.
Las fotos viven en media/activos/<INM-XXX-slug>/."""
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACT = os.path.join(REPO, "media", "activos")
WA = "5493764199878"

ACTIVOS = [
    dict(id="INM-001", tipo="Departamento", nombre="Depto 1 dorm · Torre Aymará",
         lugar="Posadas · Beethoven 1650", precio="USD 66.000", sup="69 m² totales",
         det="Un dormitorio con balcón. Dos unidades disponibles: pisos 7 y 13.",
         maps="https://www.google.com/maps/search/Beethoven+1650+Posadas+Misiones"),
    dict(id="INM-002", tipo="Terreno", nombre="Terreno Río Paraná",
         lugar="Oberá · Río Paraná casi Dinamarca", precio="USD 50.000", sup="12 × 50 m",
         det="Un lote.",
         maps="https://www.google.com/maps/search/Rio+Parana+184+Obera+Misiones"),
    dict(id="INM-003", tipo="Lotes", nombre="Lotes zona Aeródromo",
         lugar="Oberá · Zona aeródromo", precio="USD 25.000 c/u", sup="12,5 × 32,5 m",
         det="Dos lotes disponibles. Precio por unidad.",
         maps="https://www.google.com/maps/search/-27.510031+-55.128476"),
    dict(id="INM-004", tipo="Lotes", nombre="Lotes zona Colectora",
         lugar="Oberá · casi Picada Sarmiento", precio="USD 25.000 c/u", sup="12,5 × 37,5 m",
         det="Dos lotes disponibles. Precio por unidad.",
         maps="https://www.google.com/maps/search/-27.498411+-55.159192"),
    dict(id="INM-005", tipo="Hectáreas", nombre="Hectáreas Ruta 117",
         lugar="Paso de los Libres · Corrientes", precio="Consultar", sup="2 hectáreas",
         det="Sobre la entrada, con frente a ruta.",
         maps="https://www.google.com/maps/search/-29.720414+-57.129831"),
    dict(id="INM-006", tipo="Hectáreas", nombre="Hectáreas Ruta 14",
         lugar="San José · Ruta 14", precio="Consultar", sup="1,5 hectáreas",
         det="Sobre la entrada a Misiones.",
         maps="https://www.google.com/maps/search/-27.756179+-55.785415"),
    dict(id="INM-007", tipo="Departamento", nombre="Depto 2 dorm unificado · Torre Aymará",
         lugar="Posadas · Beethoven 1650", precio="Consultar", sup="A confirmar",
         det="Piso del costado unificado. Dos dormitorios, dos balcones.",
         maps="https://www.google.com/maps/search/Beethoven+1650+Posadas+Misiones"),
    dict(id="INM-008", tipo="Loteo", nombre="Solares de Loreto",
         lugar="Loreto · Candelaria", precio="Desde USD 8.000", sup="490 a 1.250 m²",
         det="Loteo turístico-residencial propio. Financiación en cuotas fijas.",
         maps="https://maps.app.goo.gl/y89b4WNgwMbJJZAZ7"),
    dict(id="INM-009", tipo="Terraza", nombre="Terraza rooftop · Torre Aymará",
         lugar="Posadas · Beethoven 1650", precio="Consultar", sup="630 m²",
         det="Terraza rooftop con vista.",
         maps="https://www.google.com/maps/search/Beethoven+1650+Posadas+Misiones"),
    dict(id="INM-010", tipo="Local comercial", nombre="Local planta baja · Torre Aymará",
         lugar="Posadas · Beethoven 1650", precio="Consultar", sup="30 m²",
         det="Local a la calle en planta baja.",
         maps="https://www.google.com/maps/search/Beethoven+1650+Posadas+Misiones"),
]


def fotos(inm):
    if not os.path.isdir(ACT):
        return None, []
    for d in sorted(os.listdir(ACT)):
        if d.startswith(inm):
            p = os.path.join(ACT, d)
            return d, sorted(f for f in os.listdir(p) if f.lower().endswith(".jpg"))
    return None, []


CSS = """
:root{--monte:#1B5E20;--monte-dk:#123D16;--tierra:#A64B28;--crema:#F4EFE3;--madera:#7B5333;--oro:#D4AF37;--tinta:#1a1a17}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--crema);color:var(--tinta);font-family:Montserrat,system-ui,sans-serif;line-height:1.55;-webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
header.top{background:var(--monte-dk);color:var(--crema);padding:44px 0 38px;margin-bottom:34px}
header.top h1{font-family:'Playfair Display',Georgia,serif;font-weight:600;font-size:clamp(1.9rem,1.2rem + 2.6vw,2.8rem);line-height:1.1;margin-top:20px}
header.top .sub{opacity:.82;margin-top:12px;font-size:.95rem;max-width:62ch}
.marca{font-family:'Playfair Display',Georgia,serif;font-size:1.5rem;letter-spacing:.02em}
.regla{height:3px;width:74px;background:var(--tierra);margin-top:18px}
.resumen{display:flex;gap:28px;flex-wrap:wrap;margin-top:26px;font-size:.84rem}
.resumen b{display:block;font-family:'Playfair Display',Georgia,serif;font-size:1.7rem;font-weight:600;color:var(--oro)}
.grid{display:grid;gap:22px;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));padding-bottom:60px}
.activo{background:#fff;border:1px solid rgba(123,83,51,.2);border-radius:10px;padding:22px;display:flex;flex-direction:column}
.activo header{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.tipo{font-size:.68rem;font-weight:600;letter-spacing:.11em;text-transform:uppercase;color:var(--tierra)}
.ref{font-size:.68rem;color:var(--madera);opacity:.7}
.activo h2{font-family:'Playfair Display',Georgia,serif;font-size:1.32rem;font-weight:600;color:var(--monte-dk);line-height:1.22}
.lugar{font-size:.85rem;color:var(--madera);margin-top:5px}
.datos{display:flex;gap:26px;margin:16px 0 12px;padding:13px 0;border-top:1px solid rgba(123,83,51,.16);border-bottom:1px solid rgba(123,83,51,.16)}
dt{font-size:.66rem;letter-spacing:.09em;text-transform:uppercase;color:var(--madera);margin-bottom:3px}
dd{font-size:.95rem;font-weight:600}
.precio{color:var(--monte);font-size:1.06rem}
.det{font-size:.87rem;color:#4a4a44;margin-bottom:14px}
.fotos{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-bottom:16px}
.fotos img{width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:5px;cursor:zoom-in;transition:opacity .2s}
.fotos img:hover{opacity:.85}
.sinfoto{grid-column:1/-1;padding:26px;text-align:center;font-size:.82rem;color:var(--madera);background:rgba(123,83,51,.06);border-radius:5px}
.acciones{display:flex;gap:9px;margin-top:auto}
.btn{flex:1;text-align:center;padding:11px;border-radius:5px;font-size:.76rem;font-weight:600;letter-spacing:.06em;text-transform:uppercase;text-decoration:none;background:var(--monte);color:var(--crema);transition:background .2s}
.btn:hover{background:var(--monte-dk)}
.btn.ghost{background:transparent;color:var(--monte);border:1px solid rgba(27,94,32,.35)}
.btn.ghost:hover{background:rgba(27,94,32,.07)}
#lb{display:none;position:fixed;inset:0;background:rgba(10,16,10,.94);z-index:99;align-items:center;justify-content:center;cursor:zoom-out;padding:24px}
#lb img{max-width:100%;max-height:100%;border-radius:6px}
footer{background:var(--monte-dk);color:var(--crema);padding:26px 0;font-size:.8rem;opacity:.92}
@media(max-width:600px){.grid{grid-template-columns:1fr}.datos{gap:18px}}
"""

JS = """
function abrir(src){document.getElementById('lbimg').src=src;document.getElementById('lb').style.display='flex';}
document.addEventListener('keydown',function(e){if(e.key==='Escape'){document.getElementById('lb').style.display='none';}});
"""


def main():
    tarjetas, total_fotos = [], 0
    for a in ACTIVOS:
        carpeta, fs = fotos(a["id"])
        total_fotos += len(fs)
        if fs:
            thumbs = "".join(
                '<img src="media/activos/{}/{}" alt="{}" loading="lazy" onclick="abrir(this.src)">'.format(carpeta, f, a["nombre"])
                for f in fs
            )
        else:
            thumbs = '<div class="sinfoto">Sin fotos cargadas</div>'
        msg = "Hola, quiero informacion sobre: {} ({})".format(a["nombre"], a["id"]).replace(" ", "%20")
        tarjetas.append("""
    <article class="activo">
      <header><span class="tipo">{tipo}</span><span class="ref">{id}</span></header>
      <h2>{nombre}</h2>
      <p class="lugar">{lugar}</p>
      <div class="datos">
        <div><dt>Precio</dt><dd class="precio">{precio}</dd></div>
        <div><dt>Superficie</dt><dd>{sup}</dd></div>
      </div>
      <p class="det">{det}</p>
      <div class="fotos">{thumbs}</div>
      <div class="acciones">
        <a class="btn" target="_blank" rel="noopener" href="https://wa.me/{wa}?text={msg}">Consultar</a>
        <a class="btn ghost" target="_blank" rel="noopener" href="{maps}">Ver en el mapa</a>
      </div>
    </article>""".format(thumbs=thumbs, wa=WA, msg=msg, **a))

    html = """<!doctype html>
<html lang="es"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>Activos CMD - Compania Misionera de Desarrollo</title>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600&family=Montserrat:wght@400;500;600&display=swap" rel="stylesheet">
<style>%s</style></head><body>

<header class="top"><div class="wrap">
  <div class="marca">CMD</div>
  <div class="regla"></div>
  <h1>Activos disponibles</h1>
  <p class="sub">Inventario de la Compa&ntilde;&iacute;a Misionera de Desarrollo. Terrenos, lotes, departamentos y hect&aacute;reas en Misiones y Corrientes. Todos de propiedad directa, sin comisiones de intermediarios.</p>
  <div class="resumen">
    <div><b>%d</b>activos</div>
    <div><b>%d</b>fotos</div>
    <div><b>4</b>localidades</div>
  </div>
</div></header>

<div class="wrap"><div class="grid">%s</div></div>

<footer><div class="wrap">
  Compa&ntilde;&iacute;a Misionera de Desarrollo &middot; Posadas, Misiones &middot; Consultas: 3764 199878<br>
  <span style="opacity:.6">Uso interno y comercial. Precios sujetos a confirmaci&oacute;n.</span>
</div></footer>

<div id="lb" onclick="this.style.display='none'"><img id="lbimg" alt=""></div>
<script>%s</script>
</body></html>""" % (CSS, len(ACTIVOS), total_fotos, "".join(tarjetas), JS)

    salida = os.path.join(REPO, "activos.html")
    with open(salida, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("activos.html generado: {} activos, {} fotos".format(len(ACTIVOS), total_fotos))


if __name__ == "__main__":
    main()
