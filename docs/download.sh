#!/bin/bash
BASE="/c/Users/mfeli/OneDrive/Desktop/SDL-organizacion"
COOKIE="/tmp/gdcookie.txt"

download() {
  local id="$1"; local out="$2"
  rm -f "$COOKIE"
  # Attempt 1: usercontent endpoint with confirm=t (handles most large files too)
  curl -sL -c "$COOKIE" "https://drive.usercontent.google.com/download?id=${id}&export=download&confirm=t" -o "$out"
  if file -b "$out" | grep -qi 'HTML'; then
    # Attempt 2: parse confirm token + uuid from the returned HTML form
    local page
    page="$(curl -sL -c "$COOKIE" "https://drive.usercontent.google.com/download?id=${id}&export=download")"
    local confirm uuid
    confirm="$(echo "$page" | grep -o 'name="confirm" value="[^"]*"' | sed 's/.*value="//;s/"//')"
    uuid="$(echo "$page" | grep -o 'name="uuid" value="[^"]*"' | sed 's/.*value="//;s/"//')"
    if [ -n "$confirm" ]; then
      curl -sL -b "$COOKIE" "https://drive.usercontent.google.com/download?id=${id}&export=download&confirm=${confirm}&uuid=${uuid}" -o "$out"
    fi
  fi
  if file -b "$out" | grep -qi 'HTML'; then
    # Attempt 3: legacy uc endpoint
    curl -sL -c "$COOKIE" "https://drive.google.com/uc?export=download&id=${id}&confirm=t" -o "$out"
  fi
  # Report
  local sz ftype status
  sz="$(du -h "$out" | cut -f1)"
  ftype="$(file -b "$out")"
  if echo "$ftype" | grep -qi 'HTML'; then status="FAIL-HTML"; else status="OK"; fi
  printf '%-10s %-8s %-45s %s\n' "$status" "$sz" "$out" "$ftype"
}

# FILEID|relative path
LIST='
1xKXkULgMN5WOV4o9h9J4Dx3GsajybuIp|videos/video-ubicacion-sdl.mp4
1wsUb0tZeO0Rb0QaQkoWc0wEcKoWhGhN7|videos/video-primera-etapa.mp4
1YY3796HGaHFiZhbiJeEM-Do97f9-8EfL|entorno-loreto/naturaleza-loreto01.HEIC
1f_o8DOdFraDD4xTf_9kaiSBpp9BBmOXq|entorno-loreto/naturaleza-loreto02-arroyo-yabebiri.HEIC
1IebxqXLqWLbEAIZwP1L5ilwyporjKlI8|entorno-loreto/naturaleza-loreto03-arroyo-yabebiri.HEIC
1kPB074y75s9t1yswwFJhAwPtdNxlUQN8|entorno-loreto/naturaleza-loreto04-arroyo-yabebiri.HEIC
1FIKFBHIdmtL2aEndk7LpHHXEdc9r7-NI|entorno-loreto/iglesia-loreto.HEIC
1IsSc7wV_Z4Cu-zYrW790mFiiTE-3sbTT|entorno-loreto/hombres-plano.HEIC
1p_QY5g1CP4rIpYNX3oMTK6kHRzL9Rozq|entorno-loreto/ruinas-jesuiticas-loreto01.HEIC
1YjEAkmWsqV9DgxAuUxVjQG2_Z6puoUKL|entorno-loreto/ruinas-jesuiticas-loreto02.HEIC
1Yle6zr8c2WeeQ9oj7dl49iTs6eOZw7yH|entorno-loreto/ruinas-jesuiticas-loreto03.HEIC
1u8KHWxSo_zfBj9UES1xPI9c77SaszJm5|loteo-drone/drone-01-SDL.jpg
1Wr89Gka1tv_uX7-pEzLrtq0DS2KxYKcA|loteo-drone/drone-02-SDL.jpg
1V3aTRMZ1-rhJqAuhsMQWjoA6jmJCUNrS|loteo-drone/drone-auto01-SDL.jpg
1kdzC7CV0jv5Mae44C_a-tLOR2WKkDkqC|loteo-drone/drone-auto02-SDL.jpg
1SouJsXfA4r4K2qyiTLk4e20TjExMfgCE|loteo-drone/tractor-mantenimiento.jpg
1UF7NQWw86oADSVoAPzyfqQ8mVwQlh_BU|loteo-drone/kml-celular-aereo-SDL.png
1AtvLYRuyIHx9rNH3--Xn2LEfXV22nZe4|loteo-drone/kml-celular-aereo2-SDL.png
1W5mct9Ox8zwKN01GC7h92GTDnSaUmSAs|aereas-loteo/aerea-loteo-01.jpg
1Vuf_AvMJ-Hy644xOztSjhHVf4FLeld6C|aereas-loteo/aerea-loteo-02.jpg
1fxaULmWbHMeC-Rsrlkb9vNJq2occKG2n|aereas-loteo/aerea-loteo-03.jpg
1nWh7Oi1AhnGA41rOGT8CgjV8NInDDt1D|aereas-loteo/aerea-loteo-04.jpg
1aO9jovwjB8MOLvIFStXFVvJsd40INw_T|aereas-loteo/aerea-loteo-05.jpg
1r-4Ni_OlOA8PydmYhsGupT2cYfpIC7V8|aereas-loteo/aerea-loteo-06.jpg
12miaCRbgeqy5eDaq0Gz6fXyIolbsh8TB|avance-mayo2026/mayo2026-01.jpg
1Sk_hBi_Ya_CH9RJBGv1BcpM1kT_9JWj4|avance-mayo2026/mayo2026-02.jpg
1rJkxKNMzdjNVCIGlirGyzLmRNrLRvMl6|avance-mayo2026/mayo2026-03.jpg
1hba6lsDTM-CnmffYhNGw2v9AhOACDTTV|avance-mayo2026/mayo2026-04.jpg
1dsJfFpZMaUjssrG_DnNbUbx_DPO7Y8R0|avance-mayo2026/mayo2026-05.jpg
1v-WfRAbAgpWv2N5Y5LuhCfv7c3HVN7HA|avance-mayo2026/mayo2026-06.jpg
11aZFTRpra5-jujYatoG4-zDk8x7VoqIV|logo/logo-SDL.png
1BCFgcTujrnlYy5b8VpjKFHy7hOm1m_E1|diseños/diseño-IMG1452.png
1g-9Wv7vwMZ4FBlWGGapleYSXxhHRV7Xi|diseños/diseño-IMG1453.png
1T-nCuGjicW1Ge0VCawJKwm98nGNqUUwp|diseños/diseño-IMG1454.png
1f4kL3Tgxb4XxtDilXUvoUryXZbFiY7yR|diseños/diseño-IMG1455.png
1XLOc_kp_chz7bWsE0kkr162wYG43OlIo|diseños/diseño-4aed6140.jpg
1K60sOQJ2yj44PYzaEOkk-StvnhIGF5jN|info-proyecto/plano-visado-SDL.pdf
10aQwML2-7FQQd47Z3tddCCpwQLOd41Sn|info-proyecto/modelo-1.kml
'

echo "=== DESCARGANDO ==="
while IFS='|' read -r id rel; do
  [ -z "$id" ] && continue
  download "$id" "$BASE/$rel"
done <<< "$LIST"
echo "=== FIN ==="