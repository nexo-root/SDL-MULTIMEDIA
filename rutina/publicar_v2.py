#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fabrica de Flyers - publicador v2 (el que obedece al Panel CMD).

NO reemplaza nada de publicar_cloud.py: lo IMPORTA y usa tal cual sus funciones probadas
(leer/publicar en Instagram y Facebook, la huella, los avisos). Lo unico nuevo es COMO SE ELIGE que sale:

  * Cada pieza de cola.json puede traer "fecha" (AAAA-MM-DD), puesta desde el panel.
    Sale la mas vieja con fecha <= hoy que todavia no se publico. Sin nada para hoy, no publica.
  * Si NINGUNA pieza pendiente tiene fecha, se porta igual que la v1 (lun/mie/vie, en orden).
  * Lo publicado se anota en publicadas.json (id, fecha, link). Se suma a lo que dice Instagram, asi
    una pieza vieja no vuelve a salir cuando IG deja de mostrarla entre sus ultimos posts
    (la v1 mira solo los ultimos 50: a partir del post 51 empezaria a repetir).
  * "redes": ["ig"], ["fb"] o las dos (por defecto, las dos).

Modos:
  python publicar_v2.py               publica lo que toca hoy
  python publicar_v2.py --simular     dice que publicaria, sin publicar nada
  python publicar_v2.py --registrar   solo lee Instagram y arma publicadas.json (no publica)
"""
import json
import os
import sys
from datetime import datetime

import publicar_cloud as v1

REGISTRO = os.path.join(v1.HERE, "publicadas.json")
MAX_POSTS = 300


def leer_registro():
    try:
        return json.load(open(REGISTRO, encoding="utf-8")).get("publicadas", [])
    except (OSError, ValueError):
        return []


def guardar_registro(publicadas):
    with open(REGISTRO, "w", encoding="utf-8") as f:
        json.dump({"actualizado": datetime.now(v1.ART).isoformat(timespec="seconds"), "publicadas": publicadas}, f, ensure_ascii=False, indent=2)
        f.write("\n")


def leer_ig_completo(hoy):
    """Como v1.leer_ig pero paginando: huella -> (fecha, link) de hasta MAX_POSTS posts, y si hubo post hoy."""
    posts, hubo_hoy, despues = {}, False, None
    while len(posts) < MAX_POSTS:
        params = {"fields": "timestamp,caption,permalink", "limit": 50}
        if despues:
            params["after"] = despues
        r = v1.api_get(f"{v1.IG_USER_ID}/media", params)
        for m in r.get("data", []):
            fecha = ""
            try:
                fecha = datetime.strptime(m.get("timestamp", ""), "%Y-%m-%dT%H:%M:%S%z").astimezone(v1.ART).date().isoformat()
            except ValueError:
                pass
            if fecha == hoy.isoformat():
                hubo_hoy = True
            posts.setdefault(v1._huella(m.get("caption")), (fecha, m.get("permalink", "")))
        despues = r.get("paging", {}).get("cursors", {}).get("after")
        if not despues or not r.get("paging", {}).get("next"):
            break
    return posts, hubo_hoy


def pendientes(seq, huellas_ig, ids_registrados):
    return [p for p in seq if p["id"] not in ids_registrados and v1._huella(p["caption"]) not in huellas_ig]


def elegir(seq, huellas_ig, ids_registrados, hoy_iso, es_dia_v1):
    """Devuelve (pieza, motivo). pieza None = hoy no sale nada."""
    faltan = pendientes(seq, huellas_ig, ids_registrados)
    if not faltan:
        return None, "sin material"
    con_fecha = [p for p in faltan if p.get("fecha")]
    if con_fecha:
        tocan = sorted((p for p in con_fecha if p["fecha"] <= hoy_iso), key=lambda p: p["fecha"])
        return (tocan[0], "por fecha") if tocan else (None, "nada para hoy")
    # Nadie tiene fecha: todavia no se guardo nada desde el panel. Igual que la v1.
    return (faltan[0], "orden v1") if es_dia_v1 else (None, "no es dia de publicacion")


def armar_registro(seq, posts_ig, previo):
    """Cruza la cola con lo que hay en Instagram. Conserva lo ya anotado: el registro nunca pierde memoria."""
    por_id = {p["id"]: p for p in previo}
    for pieza in seq:
        dato = posts_ig.get(v1._huella(pieza["caption"]))
        if dato and pieza["id"] not in por_id:
            por_id[pieza["id"]] = {"id": pieza["id"], "fecha": dato[0], "ig": dato[1]}
    orden = {p["id"]: i for i, p in enumerate(seq)}
    return sorted(por_id.values(), key=lambda p: (p.get("fecha", ""), orden.get(p["id"], 0)))


def main(args):
    simular, registrar = "--simular" in args, "--registrar" in args
    v1.TOKEN = os.environ.get("META_TOKEN", "").strip()
    if not v1.TOKEN:
        v1.log("ERROR: falta META_TOKEN en el entorno.")
        return 2

    cola = json.load(open(v1.COLA, encoding="utf-8"))
    seq = cola["secuencia"]
    hoy = datetime.now(v1.ART).date()
    v1.log(f"Publicador v2{' (SIMULACRO)' if simular else ''}. Hoy = {hoy}")

    try:
        posts, hubo_hoy = leer_ig_completo(hoy)
    except Exception as e:
        v1.log(f"ERROR leyendo Instagram (token vencido/invalido?): {e}")
        v1.avisar("Fabrica de Flyers: NO publico", "Meta rechazo el token (vencido o sesion invalidada). Hay que renovarlo. Lo de hoy no se pierde: sale en la proxima corrida.")
        return 2

    registro = armar_registro(seq, posts, leer_registro())
    if registrar:
        guardar_registro(registro)
        v1.log(f"Registro armado: {len(registro)} de {len(seq)} piezas figuran publicadas.")
        return 0

    if hubo_hoy:
        v1.log("Ya hay un post de HOY en IG. No republico (una por dia).")
        if not simular:
            guardar_registro(registro)
        return 0

    pieza, motivo = elegir(seq, set(posts), {p["id"] for p in registro}, hoy.isoformat(), hoy.weekday() in set(cola.get("dias_pub", [0, 2, 4])))
    if pieza is None:
        v1.log(f"Hoy no sale nada: {motivo}.")
        if motivo == "sin material":
            v1.avisar("Fabrica de Flyers: sin material", "Ya salio todo lo que habia en la cola. Carga contenido nuevo desde el panel.")
        if not simular:
            guardar_registro(registro)
        return 0

    url = cola["base_url"] + pieza["file"]
    redes = pieza.get("redes") or ["ig", "fb"]
    v1.log(f"Sale ({motivo}): {pieza['id']} -> {pieza['file']} en {'+'.join(redes)}" + (f" [fecha {pieza['fecha']}]" if pieza.get("fecha") else ""))
    if simular:
        v1.log("SIMULACRO: no se publico nada.")
        return 0

    ok = False
    if "ig" in redes:
        try:
            v1.log(f"  IG OK  media={v1.publicar_ig(url, pieza['caption'])}")
            ok = True
        except Exception as e:
            v1.log(f"  IG FALLO: {e}")
    if "fb" in redes:
        try:
            v1.log(f"  FB OK  post={v1.publicar_fb(url, pieza['caption'])}")
            ok = True
        except Exception as e:
            v1.log(f"  FB FALLO: {e}")

    if ok:
        registro.append({"id": pieza["id"], "fecha": hoy.isoformat(), "ig": ""})
    else:
        v1.avisar("Fabrica de Flyers: NO publico", f"Fallo la publicacion de {pieza['id']}. No se pierde: reintenta en la proxima corrida.")
    guardar_registro(registro)

    quedan = len(pendientes(seq, set(posts), {p["id"] for p in registro}))
    v1.log(f"Resultado: {'OK' if ok else 'FALLO'}. Quedan {quedan} en la cola.")
    if ok and 0 < quedan < 3:
        v1.avisar("Fabrica de Flyers: poca cola", f"Quedan {quedan} publicaciones. Sumale contenido desde el panel.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
