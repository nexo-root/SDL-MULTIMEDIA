#!/usr/bin/env python3
"""
Rutina CLOUD de la Fabrica de Flyers CMD - Solares de Loreto.

Corre en la nube de Claude Code (Routines), lunes/miercoles/viernes 10:00 ART.
NO depende de la PC de Felipe. Publica el flyer que corresponde a HOY segun un
calendario fijo (la fecha ES la memoria: no necesita estado persistente).

Que hace cada corrida:
  1. Calcula el indice de hoy: cuantos dias de publicacion (lun/mie/vie) pasaron
     desde fecha_inicio, + indice_inicio.
  2. Anti-doble: consulta el ultimo post de IG; si ya publico hoy, no republica.
  3. Publica la pieza en Instagram (@ciamisionera) + Pagina de Facebook de CMD.
  4. Si el indice supera la cola -> SE FRENA (no repite, no inventa).

El token de Meta se pasa por la variable de entorno META_TOKEN (NUNCA en el repo).
IDs (no secretos) van aca abajo. Solo usa la libreria estandar de Python.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone, timedelta

# --- IDs de CMD (no secretos) ---
IG_USER_ID = "17841446682565595"     # @ciamisionera
PAGE_ID = "1198708749996590"          # Pagina FB Cia Misionera Desarrollo
API = "https://graph.facebook.com/v25.0"
ART = timezone(timedelta(hours=-3))   # America/Buenos_Aires

HERE = os.path.dirname(os.path.abspath(__file__))
COLA = os.path.join(HERE, "cola.json")


def log(msg):
    print(f"[{datetime.now(ART).strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def api_get(path, params):
    params = dict(params); params["access_token"] = TOKEN
    url = f"{API}/{path}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=40) as r:
        return json.loads(r.read().decode("utf-8"))


def api_post(path, params):
    params = dict(params); params["access_token"] = TOKEN
    data = urllib.parse.urlencode(params).encode("utf-8")
    with urllib.request.urlopen(f"{API}/{path}", data=data, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def indice_de_hoy(cola, hoy):
    """Cuenta los dias de publicacion (dias_pub) desde fecha_inicio hasta hoy inclusive."""
    ini = datetime.strptime(cola["fecha_inicio"], "%Y-%m-%d").date()
    dias_pub = set(cola["dias_pub"])
    if hoy < ini:
        return None
    contados = 0
    d = ini
    while d < hoy:
        if d.weekday() in dias_pub:
            contados += 1
        d += timedelta(days=1)
    # hoy cuenta si es dia de publicacion
    if hoy.weekday() not in dias_pub:
        return None
    return cola["indice_inicio"] + contados


def ya_publico_hoy(hoy):
    """True si el ultimo post de IG es de hoy (evita doble publicacion)."""
    try:
        r = api_get(f"{IG_USER_ID}/media", {"fields": "timestamp", "limit": 1})
        d = r.get("data") or []
        if not d:
            return False
        ts = d[0]["timestamp"]  # ej 2026-07-25T13:00:05+0000
        post_dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S%z").astimezone(ART).date()
        return post_dt == hoy
    except Exception as e:
        log(f"  (no pude chequear ultimo post: {e}) - sigo igual")
        return False


def publicar_ig(url, caption):
    cont = api_post(f"{IG_USER_ID}/media", {"image_url": url, "caption": caption})
    time.sleep(3)
    res = api_post(f"{IG_USER_ID}/media_publish", {"creation_id": cont["id"]})
    return res["id"]


def page_token():
    r = api_get("me/accounts", {})
    for pg in r.get("data", []):
        if str(pg.get("id")) == PAGE_ID:
            return pg.get("access_token")
    return None


def publicar_fb(url, caption):
    pt = page_token()
    if not pt:
        raise RuntimeError("no obtuve token de la Pagina")
    data = urllib.parse.urlencode({"url": url, "caption": caption, "access_token": pt}).encode()
    with urllib.request.urlopen(f"{API}/{PAGE_ID}/photos", data=data, timeout=60) as r:
        resp = json.loads(r.read().decode("utf-8"))
    return resp.get("post_id") or resp.get("id")


def main():
    global TOKEN
    TOKEN = os.environ.get("META_TOKEN", "").strip()
    if not TOKEN:
        log("ERROR: falta META_TOKEN en el entorno.")
        return 2

    cola = json.load(open(COLA, encoding="utf-8"))
    seq = cola["secuencia"]
    hoy = datetime.now(ART).date()
    log(f"Corrida cloud. Hoy = {hoy} ({['Lun','Mar','Mie','Jue','Vie','Sab','Dom'][hoy.weekday()]})")

    idx = indice_de_hoy(cola, hoy)
    if idx is None:
        log("Hoy NO es dia de publicacion (o es antes del inicio). No hago nada.")
        return 0
    if idx >= len(seq):
        log(f"SIN MATERIAL (indice {idx} >= {len(seq)}). La rutina se FRENA - no repite ni inventa.")
        return 0

    pieza = seq[idx]
    log(f"Indice {idx}/{len(seq)-1}: [{pieza['serie']}] {pieza['id']} -> {pieza['file']}")

    if ya_publico_hoy(hoy):
        log("Ya hay un post de HOY en IG. No republico (anti-doble).")
        return 0

    url = cola["base_url"] + pieza["file"]
    caption = pieza["caption"]

    ok = False
    try:
        mid = publicar_ig(url, caption)
        log(f"  IG OK  media={mid}")
        ok = True
    except Exception as e:
        log(f"  IG FALLO: {e}")
    try:
        pid = publicar_fb(url, caption)
        log(f"  FB OK  post={pid}")
        ok = True
    except Exception as e:
        log(f"  FB FALLO: {e}")

    quedan = len(seq) - 1 - idx
    log(f"Resultado: {'OK' if ok else 'FALLO'}. Quedan {quedan} piezas despues de esta.")
    if 0 < quedan < 3:
        log(f"AVISO: quedan solo {quedan} piezas. Preparar contenido nuevo.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
