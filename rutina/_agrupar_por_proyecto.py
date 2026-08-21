# -*- coding: utf-8 -*-
"""1) Agrupa las categorias por PROYECTO dentro de cada seccion (Imagenes, Videos,
   los Flyer). 2) Le agrega al panel de subida un selector de activo, para que el
   que sube elija a que inmueble corresponde y los nuevos queden ordenados solos."""
import io, os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = os.path.join(REPO, "index.html")

# a que proyecto pertenece cada categoria
PROY = {
    "aereas": "Solares de Loreto", "apertura": "Solares de Loreto",
    "mayo": "Solares de Loreto", "entorno": "Solares de Loreto",
    "drone": "Solares de Loreto", "inm-008": "Solares de Loreto",
    "videos": "Solares de Loreto", "drone-vid": "Solares de Loreto",
    "inm-001": "Torre Aymará", "inm-009": "Torre Aymará", "inm-010": "Torre Aymará",
    "inm-002": "Oberá", "inm-003": "Oberá", "inm-004": "Oberá",
    "inm-005": "Campos y hectáreas", "inm-006": "Campos y hectáreas",
    "logo": "Marca CMD",
}

# orden en que se muestran los proyectos
ORDEN = ["Solares de Loreto", "Torre Aymará", "Oberá", "Campos y hectáreas", "Marca CMD"]

html = io.open(IDX, encoding="utf-8").read()

# ── 1. proy en cada categoria (idempotente) ────────────────────────────────
html = re.sub(r'proy:"[^"]*", ', "", html)
for cid, proy in PROY.items():
    html = html.replace('id:"%s", nombre:' % cid, 'id:"%s", proy:"%s", nombre:' % (cid, proy), 1)

# ── 2. lista de activos para el selector ───────────────────────────────────
if "const ACTIVOS_SEL" not in html:
    lista = """
const ACTIVOS_SEL = [
  {g:"Solares de Loreto", ops:[["INM-008","Solares de Loreto · el loteo"]]},
  {g:"Torre Aymará", ops:[["INM-001","Depto 1 dorm"],["INM-007","Depto 2 dorm unificado"],["INM-009","Terraza rooftop"],["INM-010","Local planta baja"]]},
  {g:"Oberá", ops:[["INM-002","Terreno Río Paraná"],["INM-003","Lotes zona Aeródromo"],["INM-004","Lotes zona Colectora"]]},
  {g:"Campos y hectáreas", ops:[["INM-005","Hectáreas Ruta 117 · Paso de los Libres"],["INM-006","Hectáreas Ruta 14 · San José"]]},
  {g:"Otro", ops:[["otro","Sin asignar / material general"]]},
];
const NOM_ACTIVO = {};
ACTIVOS_SEL.forEach(g=>g.ops.forEach(o=>NOM_ACTIVO[o[0]] = g.g==="Otro" ? o[1] : g.g+" · "+o[1]));

"""
    html = html.replace("const SECCIONES = [", lista + "const SECCIONES = [", 1)

# ── 3. render agrupado por proyecto ────────────────────────────────────────
viejo_loop = "  s.cats.forEach(c=>{\n"
nuevo_loop = """  const ORDEN_PROY=["Solares de Loreto","Torre Aymará","Oberá","Campos y hectáreas","Marca CMD"];
  const porProy={};
  s.cats.forEach(c=>{ const k=c.proy||"Otros"; (porProy[k]=porProy[k]||[]).push(c) });
  const proys=Object.keys(porProy).sort((a,b)=>{
    const ia=ORDEN_PROY.indexOf(a), ib=ORDEN_PROY.indexOf(b);
    return (ia<0?99:ia)-(ib<0?99:ib);
  });
  proys.forEach(proy=>{
    const cs=porProy[proy];
    const nProy=cs.reduce((a,c)=>a+c.items.length,0);
    html+=`<div class="proy"><span class="proy-lin"></span><h3>${proy}</h3><span class="proy-n">${nProy}</span><span class="proy-lin f"></span></div>`;
    cs.forEach(c=>{
"""
assert viejo_loop in html, "no encontre el loop de categorias"
html = html.replace(viejo_loop, nuevo_loop, 1)

# cerrar el forEach extra: el `});` que cerraba s.cats.forEach ahora cierra cs.forEach
viejo_cierre = "    html+=`</div></section>`;\n  });\n  p.innerHTML=html;"
nuevo_cierre = "    html+=`</div></section>`;\n    });\n  });\n  p.innerHTML=html;"
assert viejo_cierre in html, "no encontre el cierre del loop"
html = html.replace(viejo_cierre, nuevo_cierre, 1)

# ── 4. CSS del encabezado de proyecto ──────────────────────────────────────
if ".proy{" not in html:
    css = """
.proy{display:flex;align-items:center;gap:14px;margin:38px 0 6px}
.proy:first-child{margin-top:8px}
.proy h3{font-family:inherit;font-size:1.32rem;font-weight:800;letter-spacing:-.01em;color:var(--tinta);white-space:nowrap}
.proy-n{font-size:.7rem;font-weight:800;padding:3px 10px;border-radius:20px;background:var(--aqua-fuerte);color:#fff}
.proy-lin{height:2px;flex:0 0 26px;background:var(--aqua-fuerte);border-radius:2px}
.proy-lin.f{flex:1 1 auto;opacity:.22}
@media(max-width:700px){.proy{gap:9px;margin:26px 0 4px}.proy h3{font-size:1.05rem}.proy-lin{flex-basis:14px}}
"""
    html = html.replace("</style>", css + "</style>", 1)

# ── 5. selector de activo en el panel de subida ────────────────────────────
viejo_btn = '<button class="btn-subir" id="btnSubir"><span class="flecha">⬆</span> SUBIR NUEVAS IMÁGENES / VIDEOS</button>'
nuevo_btn = """<label class="sel-activo">¿A qué activo corresponde?
    <select id="activoSel"></select>
  </label>
  <button class="btn-subir" id="btnSubir"><span class="flecha">⬆</span> SUBIR NUEVAS IMÁGENES / VIDEOS</button>"""
if 'id="activoSel"' not in html:
    html = html.replace(viejo_btn, nuevo_btn, 1)
    html = html.replace(
        "Desde el celular se abre la galería o la cámara · desde la compu también podés arrastrar los archivos sobre el botón",
        "Elegí primero el activo y después subí: los archivos quedan agrupados por inmueble. Desde el celular se abre la galería o la cámara · en la compu podés arrastrarlos sobre el botón",
        1)
    css2 = """
.sel-activo{display:block;font-size:.74rem;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--tinta-suave);margin-bottom:10px}
.sel-activo select{display:block;width:100%;margin-top:7px;padding:12px 13px;border-radius:11px;border:2px solid var(--aqua-fuerte);background:#fff;font:inherit;font-size:.92rem;font-weight:600;color:var(--tinta);text-transform:none;letter-spacing:0;cursor:pointer}
.sel-activo select:focus{outline:3px solid rgba(60,207,255,.35)}
"""
    html = html.replace("</style>", css2 + "</style>", 1)

# ── 6. llenar el selector + guardar el activo elegido ──────────────────────
if "$sel.innerHTML" not in html:
    llenado = """
const $sel=document.getElementById("activoSel");
$sel.innerHTML = ACTIVOS_SEL.map(g=>`<optgroup label="${g.g}">`+g.ops.map(o=>`<option value="${o[0]}">${o[1]}</option>`).join("")+`</optgroup>`).join("");
$sel.value = localStorage.getItem("sdl-activo") || "INM-008";
$sel.onchange = ()=>localStorage.setItem("sdl-activo", $sel.value);

"""
    html = html.replace("$btn.onclick=()=>$inp.click();", llenado + "$btn.onclick=()=>$inp.click();", 1)

html = html.replace(
    "        nombre:f.name, tipo:f.type, peso:f.size, blob:f,\n        fecha:new Date().toISOString()",
    "        nombre:f.name, tipo:f.type, peso:f.size, blob:f,\n        activo:($sel.value||\"otro\"),\n        fecha:new Date().toISOString()", 1)

# ── 7. agrupar los nuevos por activo al pintarlos ──────────────────────────
viejo_pint = """  $gi.innerHTML = imgs.length ? imgs.map(celdaNueva).join("") : `<div class="vacio">Todavía no hay imágenes nuevas.<br>Tocá el botón de arriba para subir.</div>`;
  $gv.innerHTML = vids.length ? vids.map(celdaNueva).join("") : `<div class="vacio">Todavía no hay videos nuevos.<br>Tocá el botón de arriba para subir.</div>`;"""
nuevo_pint = """  const agrupar = rs => {
    const g={}; rs.forEach(r=>{ const k=r.activo||"otro"; (g[k]=g[k]||[]).push(r) });
    return Object.keys(g).map(k=>
      `<div class="proy"><span class="proy-lin"></span><h3>${NOM_ACTIVO[k]||"Sin asignar"}</h3><span class="proy-n">${g[k].length}</span><span class="proy-lin f"></span></div>`
      + `<div class="grid-n">` + g[k].map(celdaNueva).join("") + `</div>`
    ).join("");
  };
  $gi.innerHTML = imgs.length ? agrupar(imgs) : `<div class="vacio">Todavía no hay imágenes nuevas.<br>Elegí el activo y tocá el botón de arriba.</div>`;
  $gv.innerHTML = vids.length ? agrupar(vids) : `<div class="vacio">Todavía no hay videos nuevos.<br>Elegí el activo y tocá el botón de arriba.</div>`;"""
assert viejo_pint in html, "no encontre el pintado de nuevas"
html = html.replace(viejo_pint, nuevo_pint, 1)

# ── 8. mostrar el activo en el modal del archivo nuevo ─────────────────────
html = html.replace(
    '<div class="m-dato"><b>Pertenece a</b><span>Solares de Loreto · INM-008</span></div>',
    '<div class="m-dato"><b>Pertenece a</b><span>${NOM_ACTIVO[r.activo]||"Sin asignar"}</span></div>', 1)

io.open(IDX, "w", encoding="utf-8").write(html)
print("OK: agrupado por proyecto + selector de activo en la subida")
