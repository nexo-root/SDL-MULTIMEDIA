# -*- coding: utf-8 -*-
"""Las georeferencias ya estan terminadas (aereas con la grilla + texto 'Primera
etapa / 72 Lotes / MIRADOR'). Solo les falta la marca CMD. Toque minimo: wordmark
arriba a la izquierda (cielo, area vacia) con sombra para contraste. Se mantienen
en 9:16 (formato Story/Reel, como estan)."""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "media", "loteo-drone")
OUT = os.path.join(ROOT, "reels")  # van con el bundle vertical, no al feed 4:5
os.makedirs(OUT, exist_ok=True)
PLAYFAIR = os.path.join(ROOT, "fonts", "Playfair.ttf")

for src, out in [
    ("kml-celular-aereo-SDL.png", "ed-georef-01.jpg"),
    ("kml-celular-aereo2-SDL.png", "ed-georef-02.jpg"),
]:
    img = Image.open(os.path.join(SRC, src)).convert("RGB")
    d = ImageDraw.Draw(img)
    fnt = ImageFont.truetype(PLAYFAIR, 62)
    # sombra + marca (el cielo arriba a la izq esta claro -> sombra oscura)
    d.text((60, 58), "CMD", font=fnt, fill=(8, 12, 8))
    d.text((57, 55), "CMD", font=fnt, fill=(242, 238, 227), stroke_width=1, stroke_fill=(242, 238, 227))
    img.save(os.path.join(OUT, out), quality=92)
    print("OK", out, img.size)
