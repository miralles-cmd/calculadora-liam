# tickets.py - Lógica de visualización y gestión del ticket diario

from base_datos import (obtener_o_crear_ticket_hoy, agregar_linea_ticket,
                        obtener_lineas_ticket, actualizar_gastos, obtener_gastos,
                        listar_productos)
from calculos import calcular_precio, pedir_peso
from base_datos import (obtener_o_crear_ticket_hoy, agregar_linea_ticket,
                        obtener_lineas_ticket, actualizar_gastos, obtener_gastos,
                        listar_productos, listar_tickets, obtener_ticket_por_fecha)
from exportar import generar_imagen_ticket

def mostrar_ticket(ticket_id, fecha):
    """Muestra el ticket del día agrupado por categorías."""
    lineas = obtener_lineas_ticket(ticket_id)
    gastos = obtener_gastos(ticket_id)

    print(f"\n{'═'*46}")
    print(f"  🧾 TICKET DEL DÍA — {fecha}")
    print(f"{'═'*46}")

    if not lineas:
        print("  (sin ventas registradas todavía)")
    else:
        # Agrupar por categoría
        categorias = {}
        for linea in lineas:
            nombre, cat, peso, precio_g, total = linea
            if cat not in categorias:
                categorias[cat] = []
            categorias[cat].append(linea)

        gran_total = 0
        for cat, items in categorias.items():
            subtotal = sum(i[4] for i in items)
            gran_total += subtotal
            print(f"\n  📁 {cat.upper()}")
            for item in items:
                print(f"    {item[0]:20s} {item[2]:6.2f}g  →  {item[4]:.2f} €")
            print(f"    {'─'*38}")
            print(f"    Subtotal {cat}: {subtotal:.2f} €")

        print(f"\n{'─'*46}")
        print(f"  TOTAL VENTAS:      {gran_total:.2f} €")
        if gastos > 0:
            print(f"  GASTOS DEL DÍA:  - {gastos:.2f} €")
            print(f"  {'─'*38}")
            print(f"  RESULTADO NETO:    {gran_total - gastos:.2f} €")

    print(f"{'═'*46}\n")


def menu_ticket():
    """Menú principal del ticket diario."""
    ticket_id, fecha = obtener_o_crear_ticket_hoy()
def menu_ticket():
    ticket_id, fecha = obtener_o_crear_ticket_hoy()

    while True:
        mostrar_ticket(ticket_id, fecha)
        print("  1. Añadir venta")
        print("  2. Registrar gastos del día")
        print("  3. 🖼️  Exportar como imagen JPG")
        print("  0. Volver al menú principal")

        opcion = input("\n  Opción: ").strip()

        if opcion == "1":
            menu_añadir_venta(ticket_id)
        elif opcion == "2":
            menu_gastos(ticket_id)
        elif opcion == "3":
            if not obtener_lineas_ticket(ticket_id):
                print("⚠️  El ticket está vacío, no hay nada que exportar.")
            else:
                ruta = generar_imagen_ticket(ticket_id, fecha)
                print(f"\n✅ Imagen guardada en: {ruta}")
                print("   Puedes abrirla desde el explorador de archivos.")
        elif opcion == "0":
            break
        else:
            print("⚠️  Opción no válida.")

def menu_añadir_venta(ticket_id):
    """Flujo para añadir una línea de venta al ticket."""
    productos = listar_productos()
    if not productos:
        print("⚠️  No hay productos. Añade primero desde el menú principal.")
        return

    print("\n── PRODUCTOS DISPONIBLES ──")
    for p in productos:
        print(f"  [{p[0]}] {p[1]:20s}  {p[2]:.4f} €/g  [{p[3]}]")

    try:
        prod_id = int(input("\nID del producto: "))
    except ValueError:
        print("⚠️  ID no válido.")
        return

    producto = next((p for p in productos if p[0] == prod_id), None)
    if not producto:
        print("⚠️  Producto no encontrado.")
        return

    peso = pedir_peso()
    total = calcular_precio(peso, producto[2])

    print(f"\n  → {producto[1]} | {peso}g | {total:.2f} €")
    confirmar = input("  ¿Añadir al ticket? (s/n): ").strip().lower()

    if confirmar == "s":
        agregar_linea_ticket(
            ticket_id,
            producto[0],
            producto[1],
            producto[3] or "Sin categoría",
            peso,
            producto[2],
            total
        )
        print("✅ Venta añadida al ticket.")
    else:
        print("❌ Cancelado.")

def menu_gastos(ticket_id):
    """Permite registrar o actualizar los gastos del día."""
    gastos_actuales = obtener_gastos(ticket_id)
    print(f"\n  Gastos actuales: {gastos_actuales:.2f} €")
    try:
        nuevos = float(input("  Nuevo importe de gastos: ").replace(",", "."))
        if nuevos < 0:
            print("⚠️  Los gastos no pueden ser negativos.")
            return
        actualizar_gastos(ticket_id, nuevos)
        print("✅ Gastos actualizados.")
    except ValueError:
        print("⚠️  Valor no válido.")

def menu_historial():
    """Muestra el historial de tickets agrupado por mes."""
    tickets = listar_tickets()

    if not tickets:
        print("\n⚠️  No hay tickets guardados todavía.")
        return

    print(f"\n{'═'*46}")
    print(f"  📅 HISTORIAL DE TICKETS")
    print(f"{'═'*46}")

    # Agrupar por mes
    meses = {}
    for t in tickets:
        ticket_id, fecha, gastos, total_ventas = t
        mes = fecha[:7]  # Ejemplo: "2026-05"
        if mes not in meses:
            meses[mes] = []
        meses[mes].append(t)

    for mes, items in meses.items():
        año, num_mes = mes.split("-")
        nombres_mes = {
            "01": "Enero", "02": "Febrero", "03": "Marzo",
            "04": "Abril", "05": "Mayo", "06": "Junio",
            "07": "Julio", "08": "Agosto", "09": "Septiembre",
            "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
        }
        print(f"\n  📆 {nombres_mes[num_mes].upper()} {año}")
        print(f"  {'─'*40}")

        total_mes = 0
        for t in items:
            ticket_id, fecha, gastos, total_ventas = t
            neto = total_ventas - gastos
            total_mes += neto
            print(f"  {fecha}   Ventas: {total_ventas:7.2f} €"
                  f"   Gastos: {gastos:6.2f} €"
                  f"   Neto: {neto:7.2f} €")

        print(f"  {'─'*40}")
        print(f"  Total neto {nombres_mes[num_mes]}: {total_mes:.2f} €")

    print(f"\n{'═'*46}")

    # Consultar un día concreto
    print("\n  ¿Quieres ver el detalle de un día?")
    fecha = input("  Escribe la fecha (YYYY-MM-DD) o Enter para volver: ").strip()

    if fecha:
        ticket_id = obtener_ticket_por_fecha(fecha)
        if ticket_id:
            mostrar_ticket(ticket_id, fecha)
        else:
            print(f"⚠️  No hay ticket para la fecha {fecha}.")