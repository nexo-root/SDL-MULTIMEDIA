#!/usr/bin/env python3
"""
Chequeo de salud de la Fabrica de Flyers — corre TODOS LOS DIAS a las 09:00 ART,
una hora antes de la publicacion. NO publica nada: solo verifica que todo este
en condiciones y avisa al celular de Felipe si algo esta roto.

Existe por el incidente del 24/07/2026: Meta invalido el token y la falla se
descubrio de casualidad, dias despues. Este chequeo la detecta el mismo dia,
ANTES de que cueste una publicacion.

Que verifica:
  1. El token funciona (y cuando vence, si vence).
  2. La cuenta de Instagram y la Pagina de Facebook responden.
  3. Queda material en la cola.
  4. La imagen del proximo flyer esta accesible en GitHub Pages.

Variables de entorno: META_TOKEN (obligatoria), NTFY_TOPIC (para los avisos).
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta

IG_USER_ID = "17841446682565595"
PAGE_ID = "1198708749996590"
API = "https://graph.facebook.com/v25.0"
ART = timezone(timedelta(hours=-3))

HERE = os.path.dirname(os.path.abspath(__file__))
COLA = os.path.join(HERE, "cola.json")
TOKEN = os.environ.get("META_TOKEN", "").strip()
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "").strip()

AVISAR_SI_VENCE_EN = 10  # dias


def log(m):
    print(f"[{datetime.now(ART).strftime('%Y-%m-%d %H:%M:%S')}] {m}", flush=True)


def avisar(titulo, cuerpo):
    if not NTFY_TOPIC:
        return
    try:
        req = urllib.request.Request(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=cuerpo.encode("utf-8"),
            headers={"Title": titulo.encode("ascii", "ignore").decode(), "Tags": "warning"},
        )
        urllib.request.urlopen(req, timeout=15)
    except Exception:
        pass


def api_get(path, params=None):
    p = dict(params or {})
    p["access_token"] = TOKEN
    with urllib.request.urlopen(f"{API}/{path}?{urllib.parse.urlencode(p)}", timeout=40) as r:
        return json.loads(r.read().decode("utf-8"))


def _huella(texto):
    if not texto:
        return ""
    limpio = "".join(c.lower() if (c.isalnum() or c.isspace()) else " " for c in texto)
    return " ".join(limpio.split())[:45]


def main():
    if not TOKEN:
        log("ERROR: falta META_TOKEN.")
        return 2

    problemas = []
    log("== CHEQUEO DE SALUD - Fabrica de Flyers SDL ==")

    # 1. Token vivo + vencimiento
    try:
        d = api_get("debug_token", {"input_token": TOKEN}).get("data", {})
        exp = d.get("expires_at") or 0
        tipo = d.get("type", "?")
        if exp == 0:
            log(f"[OK] Token {tipo}: valido, NO vence (permanente)")
        else:
            vence = datetime.fromtimestamp(exp, tz=ART)
            dias = (vence.date() - datetime.now(ART).date()).days
            log(f"[OK] Token {tipo}: valido, vence el {vence.strftime('%d/%m/%Y')} ({dias} dias)")
            if dias <= AVISAR_SI_VENCE_EN:
                problemas.append(f"El token de Meta vence en {dias} dias ({vence.strftime('%d/%m')}). Hay que renovarlo.")
    except Exception as e:
        log(f"[X] Token INVALIDO: {e}")
        avisar("Fabrica de Flyers: TOKEN CAIDO",
               "Meta rechazo el token. La proxima publicacion va a fallar. "
               "Avisale a Claude para renovarlo (no se pierde ningun flyer).")
        return 1

    # 2. Instagram y Pagina responden
    try:
        ig = api_get(IG_USER_ID, {"fields": "username,media_count"})
        log(f"[OK] Instagram @{ig.get('username')} ({ig.get('media_count')} posts)")
    except Exception as e:
        log(f"[X] Instagram no responde: {e}")
        problemas.append("La cuenta de Instagram no responde.")

    try:
        pg = api_get(PAGE_ID, {"fields": "name"})
        log(f"[OK] Pagina FB: {pg.get('name')}")
    except Exception as e:
        log(f"[X] Pagina FB no responde: {e}")
        problemas.append("La Pagina de Facebook no responde.")

    # 3. Material en cola + 4. imagen accesible
    try:
        cola = json.load(open(COLA, encoding="utf-8"))
        seq = cola["secuencia"]
        med = api_get(f"{IG_USER_ID}/media", {"fields": "caption", "limit": 50})
        publicadas = {_huella(m.get("caption")) for m in med.get("data", [])}
        pendientes = [p for p in seq if _huella(p["caption"]) not in publicadas]
        log(f"[OK] Cola: {len(pendientes)} de {len(seq)} piezas pendientes")

        if not pendientes:
            problemas.append("Se acabaron los flyers: la Fabrica se freno. Hay que cargar contenido nuevo.")
        else:
            if len(pendientes) < 3:
                problemas.append(f"Quedan solo {len(pendientes)} flyers. Preparar contenido nuevo.")
            prox = pendientes[0]
            url = cola["base_url"] + prox["file"]
            try:
                req = urllib.request.Request(url, method="HEAD")
                with urllib.request.urlopen(req, timeout=30) as r:
                    log(f"[OK] Proximo flyer accesible: {prox['file']} ({r.status})")
            except Exception as e:
                log(f"[X] La imagen del proximo flyer NO carga: {e}")
                problemas.append(f"La imagen {prox['file']} no esta accesible en GitHub Pages.")
    except Exception as e:
        log(f"[X] Error revisando la cola: {e}")
        problemas.append("No pude revisar la cola de flyers.")

    # Resultado
    if problemas:
        log("\n== HAY PROBLEMAS ==")
        for p in problemas:
            log(f"  - {p}")
        avisar("Fabrica de Flyers: revisar", " | ".join(problemas))
        return 1

    log("\n== TODO EN ORDEN ==")
    return 0


if __name__ == "__main__":
    sys.exit(main())
