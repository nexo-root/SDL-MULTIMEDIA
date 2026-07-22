# SOLARES DE LORETO · MULTIMEDIA

Archivo multimedia interno de **Solares de Loreto (INM-008)** — Cía. Misionera de Desarrollo.
Uso interno de la familia Mas. No es una página de venta.

## Cómo se usa

Abrir `index.html`. No necesita servidor ni instalar nada: es un solo archivo HTML
con todo su material al lado.

Si se sube a GitHub Pages / Vercel, hay que subir **toda esta carpeta**, no solo el
`index.html` — las fotos y videos viven en `media/`.

## Qué hay adentro

| Carpeta | Qué contiene |
|---|---|
| `index.html` | La página completa (diseño + datos + lógica, todo en un archivo) |
| `media/` | 31 archivos originales bajados del Drive de CMD |
| `media/aereas-loteo/` | 6 aéreas de drone de la cuadrícula del loteo |
| `media/avance-mayo2026/` | 6 tomas del avance de obra de mayo 2026 |
| `media/entorno-loreto/` | 9 fotos del entorno: arroyo Yabebiry, ruinas jesuíticas, iglesia |
| `media/loteo-drone/` | 7 tomas de drone, tractor y capturas satelitales KML |
| `media/videos/` | 2 videos: ubicación y primera etapa de obra |
| `media/logo/` | Logo oficial de Solares de Loreto |
| `flyers/` | Versiones editadas listas para publicar (Fábrica de Flyers CMD) |
| `fonts/` | Montserrat y Playfair Display (variables) |
| `docs/` | Índice del material, datos técnicos del loteo y los scripts de descarga del Drive |

## Las 5 secciones

1. **Imágenes** — los 29 originales sin editar, por categoría
2. **Videos** — los 2 originales sin editar
3. **Imágenes Flyer** — espejo de la sección 1: cada original en su mismo lugar, con su versión editada o marcado como pendiente
4. **Videos Flyer** — lo mismo para los videos
5. **Imágenes nuevas** — botón para subir material nuevo desde el celu o la compu

## Agregar una versión editada

En `index.html`, buscar el bloque `EDITADAS` y agregar una línea con el original
y sus versiones. El recuadro pasa solo de PENDIENTE a listo con su botón de descarga:

```js
const EDITADAS = {
  "aereas-loteo/aerea-loteo-02.jpg": [
    {file:FLY+"terreno-A-institucional.png", nombre:"A · Institucional"},
  ],
  // nueva:
  "avance-mayo2026/mayo2026-01.jpg": [
    {file:FLY+"mi-flyer-nuevo.png", nombre:"Flyer mayo"},
  ],
};
```

El archivo editado va en `flyers/`.

## Sobre la sección "Imágenes nuevas"

Lo que se sube queda guardado **en el dispositivo de quien lo sube** (almacenamiento
del navegador), no se comparte automáticamente entre todos. Sirve para juntar material
en el momento y descargarlo o pasarlo al Drive.

Para que los cuatro vean lo mismo hace falta ponerla online con un almacenamiento
compartido (Vercel + Supabase, por ejemplo).

## Datos del proyecto

- Colonia Santa Ana, Sección Loreto, Depto. Candelaria, Misiones
- 200.000 m² (20 ha) · 20 manzanas · ~170 lotes
- Superficie vendible 148.493,80 m² · calles 51.506,20 m²
- Lote típico 14 × 35 m (490 m²)
- Titular: Asociación Civil Proyecto de Misiones CDM

Detalle completo en `docs/info-superficies-loteo.md`.
