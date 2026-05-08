# exportar.py - Generación de imagen JPG del ticket

import os
import datetime
from PIL import Image, ImageDraw, ImageFont
from base_datos import obtener_lineas_ticket, obtener_gastos


# Carpeta donde se guardarán las imágenes
CARPETA_EXPORTS = "exports"


def asegurar_carpeta():
    if not os.path.exists(CARPETA_EXPORTS):
        os.makedirs(CARPETA_EXPORTS)


def generar_imagen_ticket(ticket_id, fecha):
    """Genera una imagen JPG del ticket y la guarda en /exports."""
    asegurar_carpeta()

    lineas = obtener_lineas_ticket(ticket_id)
    gastos = obtener_gastos(ticket_id)

    # ── Agrupar por categoría ──────────────────────────────
    categorias = {}
    for linea in lineas:
        nombre, cat, peso, precio_g, total = linea
        if cat not in categorias:
            categorias[cat] = []
        categorias[cat].append((nombre, total))

    gran_total = sum(l[4] for l in lineas)

    # ── Calcular altura necesaria ──────────────────────────
    lineas_texto = 0
    for cat, items in categorias.items():
        lineas_texto += 2          # Cabecera categoría + separador
        lineas_texto += len(items) # Una línea por producto
        lineas_texto += 1          # Subtotal
    lineas_texto += 4              # Total ventas, gastos, neto, margen

    ANCHO        = 600
    PADDING      = 40
    ALTO_LINEA   = 32
    ALTO_HEADER  = 120
    ALTO_FOOTER  = 80
    ALTO_TOTAL   = ALTO_HEADER + (lineas_texto * ALTO_LINEA) + ALTO_FOOTER

    # ── Crear imagen ───────────────────────────────────────
    img    = Image.new("RGB", (ANCHO, ALTO_TOTAL), color=(255, 255, 255))
    draw   = ImageDraw.Draw(img)

    # Intentar cargar fuente — si no existe usa la de por defecto
    try:
        fuente_titulo  = ImageFont.truetype("arial.ttf", 22)
        fuente_normal  = ImageFont.truetype("arial.ttf", 18)
        fuente_pequena = ImageFont.truetype("arial.ttf", 15)
        fuente_total   = ImageFont.truetype("arial.ttf", 20)
    except:
        fuente_titulo  = ImageFont.load_default()
        fuente_normal  = ImageFont.load_default()
        fuente_pequena = ImageFont.load_default()
        fuente_total   = ImageFont.load_default()

    # ── Colores ────────────────────────────────────────────
    COLOR_FONDO_HEADER = (30, 30, 30)
    COLOR_BLANCO       = (255, 255, 255)
    COLOR_NEGRO        = (20, 20, 20)
    COLOR_GRIS         = (120, 120, 120)
    COLOR_CATEGORIA    = (50, 100, 180)
    COLOR_LINEA        = (220, 220, 220)
    COLOR_TOTAL_FONDO  = (240, 240, 240)

    # ── Cabecera ───────────────────────────────────────────
    draw.rectangle([(0, 0), (ANCHO, ALTO_HEADER)], fill=COLOR_FONDO_HEADER)
    draw.text((PADDING, 20), "🧾 TICKET DE VENTA", font=fuente_titulo, fill=COLOR_BLANCO)
    draw.text((PADDING, 55), f"Fecha: {fecha}", font=fuente_normal, fill=COLOR_BLANCO)
    draw.text((PADDING, 85), f"Total: {gran_total:.2f} €", font=fuente_titulo, fill=(100, 220, 100))

    # ── Cuerpo ─────────────────────────────────────────────
    y = ALTO_HEADER + 20

    for cat, items in categorias.items():
        subtotal = sum(i[1] for i in items)

        # Cabecera de categoría
        draw.rectangle([(PADDING - 10, y - 5), (ANCHO - PADDING + 10, y + 26)],
                       fill=(235, 240, 255))
        draw.text((PADDING, y), f"▸ {cat.upper()}", font=fuente_normal, fill=COLOR_CATEGORIA)
        y += ALTO_LINEA

        # Líneas de productos (sin gramos, solo nombre y precio)
        for nombre, total in items:
            draw.text((PADDING + 15, y), nombre, font=fuente_normal, fill=COLOR_NEGRO)
            precio_txt = f"{total:.2f} €"
            draw.text((ANCHO - PADDING - 80, y), precio_txt, font=fuente_normal, fill=COLOR_NEGRO)
            y += ALTO_LINEA

        # Subtotal categoría
        draw.line([(PADDING, y), (ANCHO - PADDING, y)], fill=COLOR_LINEA, width=1)
        y += 6
        draw.text((PADDING + 15, y), f"Subtotal {cat}:", font=fuente_pequena, fill=COLOR_GRIS)
        draw.text((ANCHO - PADDING - 80, y), f"{subtotal:.2f} €", font=fuente_pequena, fill=COLOR_GRIS)
        y += ALTO_LINEA + 10

    # ── Totales finales ────────────────────────────────────
    draw.rectangle([(0, y), (ANCHO, y + 6)], fill=COLOR_LINEA)
    y += 16

    draw.rectangle([(PADDING - 10, y - 5), (ANCHO - PADDING + 10, y + 26)],
                   fill=COLOR_TOTAL_FONDO)
    draw.text((PADDING, y), "TOTAL VENTAS:", font=fuente_total, fill=COLOR_NEGRO)
    draw.text((ANCHO - PADDING - 100, y), f"{gran_total:.2f} €", font=fuente_total, fill=COLOR_NEGRO)
    y += ALTO_LINEA + 5

    if gastos > 0:
        draw.text((PADDING, y), "GASTOS:", font=fuente_normal, fill=COLOR_GRIS)
        draw.text((ANCHO - PADDING - 100, y), f"- {gastos:.2f} €", font=fuente_normal, fill=(180, 60, 60))
        y += ALTO_LINEA

        neto = gran_total - gastos
        draw.rectangle([(PADDING - 10, y - 5), (ANCHO - PADDING + 10, y + 30)],
                       fill=(30, 30, 30))
        draw.text((PADDING, y), "RESULTADO NETO:", font=fuente_total, fill=COLOR_BLANCO)
        draw.text((ANCHO - PADDING - 100, y), f"{neto:.2f} €", font=fuente_total, fill=(100, 220, 100))

    # ── Guardar ────────────────────────────────────────────
    nombre_archivo = f"ticket_{fecha}.jpg"
    ruta_completa  = os.path.join(CARPETA_EXPORTS, nombre_archivo)
    img.save(ruta_completa, "JPEG", quality=95)

    return ruta_completa