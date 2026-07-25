#!/usr/bin/env python3
"""
Rutina CLOUD de la Fabrica de Flyers CMD - Solares de Loreto.

Corre en la nube de Claude Code (Routines), lunes/miercoles/viernes 10:00 ART.
NO depende de la PC de Felipe ni de estado persistente: la FUENTE DE VERDAD es
lo que realmente esta publicado en Instagram.

Que hace cada corrida:
  1. Si hoy no es lun/mie/vie -> no hace nada.
  2. Lee los ultimos 50 posts de IG y arma la lista de piezas ya publicadas
     (comparando una "huella" normalizada del caption).
  3. Anti-doble: si ya hubo un post HOY, no republica.
  4. Elige la PRIMERA pieza de la secuencia que todavia no salio -> AUTO-REPARABLE:
     si una corrida falla (token vencido, caida de Meta), esa pieza NO se pierde,
     sale en la corrida siguiente.
  5. Publica en Instagram (@ciamisionera) + Pagina de Facebook de CMD.
  6. Si ya salieron todas -> SE FRENA (no repite, no inventa).

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


def _huella(texto):
    """Normaliza un caption para comparar: sin emojis/simbolos, minusculas, 45 chars."""
    if not texto:
        return ""
    limpio = "".join(c.lower() if (c.isalnum() or c.isspace()) else " " for c in texto)
    return " ".join(limpio.split())[:45]


def leer_ig(hoy):
    """Devuelve (huellas_publicadas, hubo_post_hoy). Fuente de verdad = lo que hay en IG."""
    r = api_get(f"{IG_USER_ID}/media", {"fields": "timestamp,caption", "limit": 50})
    huellas, hoy_hubo = set(), False
    for m in r.get("data", []):
        huellas.add(_huella(m.get("caption")))
        ts = m.get("timestamp")
        if ts:
            try:
                if datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S%z").astimezone(ART).date() == hoy:
                    hoy_hubo = True
            except ValueError:
                pass
    return huellas, hoy_hubo


def elegir_pieza(seq, huellas_publicadas):
    """Primera pieza de la secuencia que NO figura publicada en IG. Auto-reparable:
    si una corrida falla, la pieza NO se pierde — sale en la corrida siguiente."""
    for i, p in enumerate(seq):
        if _huella(p["caption"]) not in huellas_publicadas:
            return i, p
    return None, None


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

    if hoy.weekday() not in set(cola["dias_pub"]):
        log("Hoy NO es dia de publicacion (lun/mie/vie). No hago nada.")
        return 0

    # Fuente de verdad: lo que REALMENTE esta publicado en IG (no un contador de fechas).
    # Asi, si una corrida falla, la pieza no se pierde: sale en la siguiente.
    try:
        huellas, hubo_hoy = leer_ig(hoy)
    except Exception as e:
        log(f"ERROR leyendo Instagram (token vencido/invalido?): {e}")
        return 2

    if hubo_hoy:
        log("Ya hay un post de HOY en IG. No republico (anti-doble).")
        return 0

    idx, pieza = elegir_pieza(seq, huellas)
    if pieza is None:
        log(f"SIN MATERIAL (las {len(seq)} piezas ya se publicaron). La rutina se FRENA - no repite ni inventa.")
        return 0

    log(f"Pieza {idx+1}/{len(seq)}: [{pieza['serie']}] {pieza['id']} -> {pieza['file']}")

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
