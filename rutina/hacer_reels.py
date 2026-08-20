# -*- coding: utf-8 -*-
"""
Convierte los videos de dron (horizontales, mudos, 848x478) en Reels verticales
1080x1920 con la marca CMD, misma identidad que los flyers:

  - fondo: la propia toma escalada a llenar + desenfocada + oscurecida
    (asi el video horizontal llena el vertical sin perder la vista aerea).
  - la toma nitida centrada encima.
  - placa inferior con titulo Playfair + regla terracota + subtitulo + CTA.
  - placa de cierre (outro) verde monte con CMD y el WhatsApp.
  - musica de fondo con loudnorm y fade out.

Genera las placas PNG con Pillow y arma el Reel con ffmpeg. EL LOOP: renderiza,
se mira, se corrige. Corre con el venv de scrapling (Pillow) + ffmpeg en PATH.
"""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "fonts")
MEDIA = os.path.join(ROOT, "media")
OUTDIR = os.path.join(ROOT, "reels")
TMP = os.path.join(OUTDIR, "_tmp")
os.makedirs(OUTDIR, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

PLAYFAIR = os.path.join(FONTS, "Playfair.ttf")
MONT = os.path.join(FONTS, "Montserrat.ttf")
MUSICA = os.path.join(ROOT, "..", "SDL-VIDEO-PRODUCCION")  # fallback resuelto abajo

CREMA = (245, 242, 233)
CREMA_SUB = (238, 234, 223)
TIERRA = (198, 98, 60)
ORO = (233, 200, 74)          # dorado del ad, para el CTA
FOOTER = (188, 196, 182)
MONTE = (18, 46, 24)
MONTE_DK = (12, 30, 15)
SHADOW = (4, 7, 4)

W, H = 1080, 1920


def f(p, s):
    return ImageFont.truetype(p, s)


def tracked(d, xy, text, font, fill, tr=0, center=None, sh=False):
    x, y = xy
    if center is not None:
        total = sum(d.textlength(c, font=font) + tr for c in text) - tr
        x = center - total / 2
    for c in text:
        if sh:
            d.text((x + 2, y + 2), c, font=font, fill=SHADOW)
        d.text((x, y), c, font=font, fill=fill)
        x += d.textlength(c, font=font) + tr
    return x


def vgrad(size, top, bot):
    w, h = size
    g = Image.new("RGBA", (1, h))
    for y in range(h):
        t = y / max(h - 1, 1)
        g.putpixel((0, y), tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(4)))
    return g.resize((w, h))


def make_lowerthird(path, kicker, title_lines, subtitle, cta):
    """Lower-third LEGIBLE: velo fuerte abajo (no apenas un degradado), titulo
    Playfair, subtitulo grande claro, CTA en dorado del ad. Todo con sombra."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # velo inferior por CAPAS COMPUESTAS (se acumulan): ambiente largo + scrim
    # fuerte en la zona de texto. Asi el texto chico nunca se pierde.
    scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    a1 = vgrad((W, 1000), (5, 10, 7, 0), (4, 10, 6, 140))
    scrim.alpha_composite(a1, (0, H - 1000))
    a2 = vgrad((W, 660), (4, 10, 6, 0), (3, 8, 5, 242))
    scrim.alpha_composite(a2, (0, H - 660))
    img = Image.alpha_composite(img, scrim)
    d = ImageDraw.Draw(img)
    # marca arriba
    d.text((66, 76), "CMD", font=f(PLAYFAIR, 52), fill=SHADOW)
    d.text((64, 74), "CMD", font=f(PLAYFAIR, 52), fill=CREMA, stroke_width=1, stroke_fill=SHADOW)

    # bloque inferior, anclado
    tfont = f(PLAYFAIR, 100)
    lh = int(100 * 1.06)
    block_h = (26 if kicker else 0) + lh * len(title_lines) + 220
    y = H - 150 - block_h
    if kicker:
        tracked(d, (66, y), kicker, f(MONT, 25), ORO, tr=6, sh=True)
        y += 44
    for l in title_lines:
        d.text((62 + 3, y + 3), l, font=tfont, fill=SHADOW)
        d.text((62, y), l, font=tfont, fill=CREMA)
        y += lh
    y += 20
    d.rectangle([64, y, 64 + 96, y + 6], fill=TIERRA)
    y += 40
    sf = f(MONT, 38)
    d.text((64 + 3, y + 3), subtitle, font=sf, fill=SHADOW)
    d.text((64, y), subtitle, font=sf, fill=CREMA)
    y += 72
    tracked(d, (64, y), cta, f(MONT, 30), ORO, tr=2, sh=True)
    img.save(path)


def make_outro(path, wa):
    img = Image.new("RGB", (W, H), MONTE_DK)
    grad = vgrad((W, H), (*MONTE, 255), (*MONTE_DK, 255)).convert("RGB")
    img.paste(grad, (0, 0))
    # textura de grilla tenue
    d = ImageDraw.Draw(img, "RGBA")
    for gx in range(0, W, 64):
        d.line([(gx, 0), (gx, H)], fill=(244, 239, 227, 12))
    for gy in range(0, H, 64):
        d.line([(0, gy), (W, gy)], fill=(244, 239, 227, 12))
    d = ImageDraw.Draw(img)
    cx = W // 2
    d.text((cx, 720), "CMD", font=f(PLAYFAIR, 150), fill=CREMA, anchor="mm", stroke_width=2, stroke_fill=SHADOW)
    tracked(d, (0, 850), "SOLARES DE LORETO", f(MONT, 34), CREMA, tr=10, center=cx)
    d.rectangle([cx - 55, 928, cx + 55, 933], fill=TIERRA)
    tracked(d, (0, 985), "LOTES EN LORETO, MISIONES", f(MONT, 26), CREMA_SUB, tr=4, center=cx)
    tracked(d, (0, 1120), "CONSULTÁ POR WHATSAPP", f(MONT, 28), CREMA, tr=5, center=cx)
    d.text((cx, 1180), wa, font=f(PLAYFAIR, 52), fill=TIERRA, anchor="mm")
    img.save(path)


OUTRO_AD = os.path.join(TMP, "outro-ad.mp4")  # placa final del ad (equipo/marca + contacto)


def musica(nombre):
    p = os.path.abspath(os.path.join(ROOT, "..", "SDL-VIDEO-PRODUCCION", nombre))
    return p if os.path.exists(p) else None


def render_reel(src, kicker, title_lines, subtitle, cta, mus_name, ss, dur, out_name, fade_hold=1.4):
    """Reel vertical: toma de dron en fondo desenfocado + toma nitida centrada +
    lower-third legible, y de cierre la MISMA placa del ad (marca + contacto).
    La musica (mus_name, NO la del ad) corre sobre todo y baja al final."""
    lt = os.path.join(TMP, "lt.png")
    make_lowerthird(lt, kicker, title_lines, subtitle, cta)
    mus = musica(mus_name)
    outro_dur = 3.2
    total = dur + outro_dur

    fc = (
        f"[0:v]trim={ss}:{ss + dur},setpts=PTS-STARTPTS,split[a][b];"
        "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=24,eq=brightness=-0.22:saturation=1.02[bg];"
        "[b]scale=1080:-2[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2[base];"
        "[2:v]format=rgba,fade=in:st=0.5:d=0.8:alpha=1[ltf];"
        "[base][ltf]overlay=0:0,format=yuv420p,fps=30[main];"
        "[3:v]fps=30,format=yuv420p[out];"
        # pequeño fundido a negro entre la toma y la placa del ad
        "[main]fade=out:st=" + f"{dur-0.4}" + ":d=0.4[mainf];"
        "[out]fade=in:st=0:d=0.4[outf];"
        "[mainf][outf]concat=n=2:v=1:a=0[v];"
        f"[1:a]atrim=0:{total},asetpts=PTS-STARTPTS,afade=in:st=0:d=1,afade=out:st={total-fade_hold}:d={fade_hold},loudnorm=I=-15:TP=-1.5[a]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-i", src,
        "-i", mus,
        "-loop", "1", "-t", str(dur), "-i", lt,
        "-i", OUTRO_AD,
        "-filter_complex", fc,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-profile:v", "high", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k",
        "-r", "30", "-movflags", "+faststart",
        os.path.join(OUTDIR, out_name),
    ]
    subprocess.run(cmd, check=True)
    print("OK", out_name)


if __name__ == "__main__":
    # PILOTO v2: aplica los arreglos de Felipe (texto legible, placa del ad,
    # musica que NO es la del ad, mas corto).
    render_reel(
        os.path.join(MEDIA, "videos-drone", "drone-loteo-09.mp4"),
        "",
        ["Tu lote,", "desde el aire"],
        "Veinte hectáreas entre la selva.",
        "DESDE USD 8.000  ·  CANDELARIA",
        "musica2.mp3",
        ss=4, dur=12,
        out_name="_piloto-reel.mp4",
    )
