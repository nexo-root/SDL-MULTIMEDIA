# -*- coding: utf-8 -*-
"""
Genera flyers de Solares de Loreto con la MISMA plantilla que los ed-*.jpg ya
publicados. 1080x1350 (4:5). Dos variantes:

  - "ventana": foto en una ventana central, bandas verde monte arriba y abajo
    (para las aereas de dron).
  - "sangre": la foto llena todo el marco, con degradados oscuros arriba y abajo
    para que el texto se lea (para las tomas de obra).

Y un tratamiento "humano" aparte para la foto del equipo con el plano: casi sin
texto, porque esa foto se sostiene sola.

Corre con el venv de scrapling (tiene Pillow 12).
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "fonts")
OUT = os.path.join(ROOT, "flyers")

W, H = 1080, 1350

# --- paleta (muestreada de los ed-*.jpg) ---
CREMA = (242, 238, 227)
CREMA_SUB = (233, 229, 218)
TIERRA = (198, 98, 60)          # terracota: numero, viñetas, regla
FOOTER = (188, 196, 182)        # gris verdoso tenue

PLAYFAIR = os.path.join(FONTS, "Playfair.ttf")
MONT = os.path.join(FONTS, "Montserrat.ttf")


def f(path, size):
    return ImageFont.truetype(path, size)


def draw_tracked(draw, xy, text, font, fill, tracking=0, anchor_right=None, stroke=0, stroke_fill=None):
    """Dibuja texto con tracking (espaciado entre letras) manual."""
    x, y = xy
    if anchor_right is not None:
        total = 0
        for ch in text:
            total += draw.textlength(ch, font=font) + tracking
        total -= tracking
        x = anchor_right - total
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        x += draw.textlength(ch, font=font) + tracking
    return x


def cover(img, tw, th):
    """Recorta y escala la imagen para llenar tw x th (object-fit: cover)."""
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return img.crop((left, top, left + tw, top + th))


def vgrad(size, top_rgba, bot_rgba):
    """Degradado vertical con alpha."""
    w, h = size
    grad = Image.new("RGBA", (1, h))
    for y in range(h):
        t = y / max(h - 1, 1)
        px = tuple(int(top_rgba[i] + (bot_rgba[i] - top_rgba[i]) * t) for i in range(4))
        grad.putpixel((0, y), px)
    return grad.resize((w, h))


SHADOW = (6, 10, 6)


def _sh(draw, xy, text, font, dx=2, dy=2):
    draw.text((xy[0] + dx, xy[1] + dy), text, font=font, fill=SHADOW)


def header(draw, shadow=False):
    """Cabecera comun: CMD | MISIONES · ARGENTINA + hairline."""
    cmd = f(PLAYFAIR, 54)
    if shadow:
        _sh(draw, (62, 52), "CMD", cmd)
    draw.text((62, 52), "CMD", font=cmd, fill=CREMA, stroke_width=1, stroke_fill=CREMA)
    lugar = f(MONT, 21)
    if shadow:
        draw_tracked(draw, (0, 72), "MISIONES  ·  ARGENTINA", lugar, SHADOW, tracking=6, anchor_right=1020)
    draw_tracked(draw, (0, 70), "MISIONES  ·  ARGENTINA", lugar, CREMA, tracking=6, anchor_right=1018)
    # hairline, debajo del CMD (no lo cruza)
    draw.line([(62, 124), (1018, 124)], fill=CREMA, width=1)


def subheader(draw, numero, etiqueta, shadow=False):
    num = f(PLAYFAIR, 30)
    draw.text((62, 140), numero, font=num, fill=TIERRA)
    nx = 62 + draw.textlength(numero, font=num) + 18
    lab = f(MONT, 21)
    if shadow:
        draw_tracked(draw, (nx + 2, 150), etiqueta, lab, SHADOW, tracking=7)
    draw_tracked(draw, (nx, 148), etiqueta, lab, CREMA, tracking=7)


def bottom_block(draw, title_lines, subtitle_lines, stats=None, status=None, shadow=False):
    """Titulo Playfair grande + regla + subtitulo + (stats o status) + footer."""
    # titulo
    tsize = 96 if max(len(l) for l in title_lines) <= 11 else 82
    tfont = f(PLAYFAIR, tsize)
    line_h = int(tsize * 1.12)
    # anclamos el bloque para que el footer caiga a ~1305
    y_title = 1350 - 235 - line_h * len(title_lines) - (140 if (stats or status) else 90)
    y = y_title
    for l in title_lines:
        if shadow:
            _sh(draw, (60, y), l, tfont, 3, 3)
        draw.text((60, y), l, font=tfont, fill=CREMA)
        y += line_h
    # regla terracota
    y += 18
    draw.rectangle([60, y, 60 + 86, y + 4], fill=TIERRA)
    y += 34
    # subtitulo
    sub = f(MONT, 31)
    for l in subtitle_lines:
        if shadow:
            _sh(draw, (62, y), l, sub, 2, 2)
        draw.text((62, y), l, font=sub, fill=CREMA_SUB)
        y += 42
    y += 26
    # stats o status
    if stats:
        sf = f(MONT, 24)
        x = 62
        cy = y + sf.size // 2 + 2  # centro vertical de la linea, para la viñeta
        for i, item in enumerate(stats):
            if i > 0:
                x += 14
                r = 4
                draw.ellipse([x, cy - r, x + 2 * r, cy + r], fill=TIERRA)
                x += 2 * r + 16
            x = draw_tracked(draw, (x, y), item, sf, CREMA, tracking=1, stroke=1, stroke_fill=CREMA)
        y += 52
    elif status:
        sf = f(MONT, 24)
        if shadow:
            draw_tracked(draw, (64, y + 2), status, sf, SHADOW, tracking=5)
        draw_tracked(draw, (62, y), status, sf, CREMA, tracking=5, stroke=1, stroke_fill=CREMA)
        y += 52
    # footer
    ff = f(MONT, 19)
    draw_tracked(draw, (62, 1300), "CÍA. MISIONERA DE DESARROLLO", ff, FOOTER, tracking=5)


def render_ventana(src, numero, etiqueta, title_lines, subtitle_lines, stats, out_name):
    canvas = Image.new("RGB", (W, H))
    # fondo: foto muy oscurecida y desenfocada, para que las bandas tengan textura verde
    bg = cover(Image.open(src).convert("RGB"), W, H).filter(ImageFilter.GaussianBlur(28))
    dark = Image.new("RGB", (W, H), (16, 26, 16))
    canvas = Image.blend(bg, dark, 0.72)
    # ventana con la foto nitida
    win_top, win_h = 172, 648
    photo = cover(Image.open(src).convert("RGB"), W, win_h)
    canvas.paste(photo, (0, win_top))
    # degradado suave sobre la parte baja de la ventana para fundir con la banda
    fade = vgrad((W, 140), (16, 26, 16, 0), (16, 26, 16, 235))
    canvas.paste(Image.alpha_composite(canvas.convert("RGBA").crop((0, win_top + win_h - 140, W, win_top + win_h)), fade).convert("RGB"), (0, win_top + win_h - 140))
    d = ImageDraw.Draw(canvas)
    header(d)
    subheader(d, numero, etiqueta)
    bottom_block(d, title_lines, subtitle_lines, stats=stats)
    canvas.save(os.path.join(OUT, out_name), quality=90)
    print("OK", out_name)


def render_sangre(src, numero, etiqueta, title_lines, subtitle_lines, status, out_name):
    canvas = cover(Image.open(src).convert("RGB"), W, H).convert("RGBA")
    top = vgrad((W, 360), (8, 13, 8, 236), (8, 13, 8, 0))
    canvas = _paste_grad(canvas, top, 0)
    bot = vgrad((W, 760), (8, 12, 8, 0), (6, 10, 6, 252))
    canvas = _paste_grad(canvas, bot, H - 760)
    canvas = canvas.convert("RGB")
    d = ImageDraw.Draw(canvas)
    header(d, shadow=True)
    subheader(d, numero, etiqueta, shadow=True)
    bottom_block(d, title_lines, subtitle_lines, status=status, shadow=True)
    canvas.save(os.path.join(OUT, out_name), quality=90)
    print("OK", out_name)


def _paste_grad(base, grad, y):
    base = base.convert("RGBA")
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer.paste(grad, (0, y))
    return Image.alpha_composite(base, layer)


def render_humano(src, out_name):
    """La foto del equipo con el plano: se sostiene sola, casi sin texto."""
    canvas = cover(Image.open(src).convert("RGB"), W, H).convert("RGBA")
    # solo un velo abajo, muy sutil, para apoyar una linea
    bot = vgrad((W, 460), (8, 12, 8, 0), (8, 12, 8, 180))
    canvas = _paste_grad(canvas, bot, H - 460)
    canvas = canvas.convert("RGB")
    d = ImageDraw.Draw(canvas)
    # marca chica arriba
    cmd = f(PLAYFAIR, 40)
    d.text((62, 58), "CMD", font=cmd, fill=CREMA, stroke_width=1, stroke_fill=CREMA)
    # una sola linea abajo, tranquila
    linea = f(PLAYFAIR, 48)
    _sh(d, (62, H - 196), "Parados donde", linea, 2, 2)
    _sh(d, (62, H - 138), "va a estar todo.", linea, 2, 2)
    d.text((62, H - 196), "Parados donde", font=linea, fill=CREMA)
    d.text((62, H - 138), "va a estar todo.", font=linea, fill=CREMA)
    d.rectangle([64, H - 74, 64 + 74, H - 71], fill=TIERRA)
    canvas.save(os.path.join(OUT, out_name), quality=90)
    print("OK", out_name)


if __name__ == "__main__":
    M = os.path.join(ROOT, "media")
    A = os.path.join(M, "aereas-loteo")
    C = os.path.join(M, "apertura-calles")
    E = os.path.join(M, "entorno-loreto")

    # --- 4 aereas de dron (variante ventana) ---
    render_ventana(
        os.path.join(A, "aerea-loteo-07.jpg"),
        "07", "EL LOTEO",
        ["El trazado", "terminado"],
        ["Cada manzana con sus calles", "abiertas y su acceso propio."],
        ["CALLES ABIERTAS", "ESCRITURA 2026"],
        "ed-aerea-loteo-07.jpg",
    )
    render_ventana(
        os.path.join(A, "aerea-loteo-08-panoramica.jpg"),
        "08", "DESDE EL AIRE",
        ["Rodeado", "de monte"],
        ["El loteo entre la forestación", "y la selva paranaense."],
        ["20 HECTÁREAS", "CANDELARIA", "MISIONES"],
        "ed-aerea-loteo-08.jpg",
    )
    render_ventana(
        os.path.join(A, "aerea-loteo-09.jpg"),
        "09", "EL LOTEO",
        ["Lotes", "en el monte"],
        ["Entre el pino y la selva", "misionera, tu lugar propio."],
        ["DESDE USD 8.000", "490 A 1.250 M²"],
        "ed-aerea-loteo-09.jpg",
    )
    render_ventana(
        os.path.join(A, "aerea-loteo-10.jpg"),
        "10", "EL LOTEO",
        ["Veinte", "manzanas"],
        ["El monte ordenado en lotes,", "con acceso a cada uno."],
        ["20 MANZANAS", "CALLES ABIERTAS"],
        "ed-aerea-loteo-10.jpg",
    )

    # --- 2 tomas de apertura de calles (variante sangre) ---
    render_sangre(
        os.path.join(C, "motoniveladora-01.jpg"),
        "11", "APERTURA DE CALLES",
        ["Se abre", "el camino"],
        ["Cada calle del loteo se traza", "con maquinaria propia."],
        "OBRA EN CURSO",
        "ed-motoniveladora-01.jpg",
    )
    render_sangre(
        os.path.join(C, "motoniveladora-02.jpg"),
        "12", "APERTURA DE CALLES",
        ["Calles", "de verdad"],
        ["No es un plano: es una", "motoniveladora trabajando."],
        "OBRA EN CURSO",
        "ed-motoniveladora-02.jpg",
    )

    # --- la foto del equipo con el plano: tratamiento humano ---
    render_humano(os.path.join(E, "hombres-plano.jpg"), "ed-equipo-plano.jpg")

    # limpiar la prueba
    p = os.path.join(OUT, "_prueba-aerea-07.jpg")
    if os.path.exists(p):
        os.remove(p)
