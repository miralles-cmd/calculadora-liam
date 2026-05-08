# base_datos.py - Gestión de la base de datos

import sqlite3
import os
import datetime

# Ruta al archivo de base de datos
RUTA_DB = os.path.join("datos", "tienda.db")


def conectar():
    """Abre la conexión con la base de datos y la devuelve."""
    conexion = sqlite3.connect(RUTA_DB)
    return conexion


def inicializar_db():
    """
    Crea las tablas si no existen todavía.
    Se llama una vez al arrancar la app.
    """
    conexion = conectar()
    cursor = conexion.cursor()

    # Tabla de categorías
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre    TEXT NOT NULL UNIQUE
        )
    """)

    # Tabla de productos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre            TEXT NOT NULL UNIQUE,
            precio_por_gramo  REAL NOT NULL,
            categoria_id      INTEGER,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        )
    """)

    # Insertar 3 categorías por defecto si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM categorias")
    if cursor.fetchone()[0] == 0:
        categorias_default = [("General",), ("Sin categoría",), ("Especial",)]
        cursor.executemany("INSERT INTO categorias (nombre) VALUES (?)", categorias_default)

    conexion.commit()
    conexion.close()
    print("✅ Base de datos lista.")


# ─── CATEGORÍAS ───────────────────────────────────────────

def listar_categorias():
    """Devuelve todas las categorías como lista."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre FROM categorias ORDER BY id")
    categorias = cursor.fetchall()
    conexion.close()
    return categorias


def editar_categoria(categoria_id, nuevo_nombre):
    """Cambia el nombre de una categoría existente."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("UPDATE categorias SET nombre = ? WHERE id = ?", (nuevo_nombre, categoria_id))
    conexion.commit()
    conexion.close()


# ─── PRODUCTOS ────────────────────────────────────────────

def agregar_producto(nombre, precio_por_gramo, categoria_id):
    """Añade un nuevo producto a la base de datos."""
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            "INSERT INTO productos (nombre, precio_por_gramo, categoria_id) VALUES (?, ?, ?)",
            (nombre, precio_por_gramo, categoria_id)
        )
        conexion.commit()
        print(f"✅ Producto '{nombre}' guardado.")
    except sqlite3.IntegrityError:
        print(f"⚠️  Ya existe un producto con el nombre '{nombre}'.")
    finally:
        conexion.close()


def listar_productos():
    """Devuelve todos los productos con su categoría."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT p.id, p.nombre, p.precio_por_gramo, c.nombre
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        ORDER BY c.nombre, p.nombre
    """)
    productos = cursor.fetchall()
    conexion.close()
    return productos


def buscar_producto(nombre):
    """Busca un producto por nombre (búsqueda parcial)."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT p.id, p.nombre, p.precio_por_gramo, c.nombre
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.nombre LIKE ?
    """, (f"%{nombre}%",))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

def eliminar_producto(producto_id):
    """Elimina un producto por su id."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
    conexion.commit()
    conexion.close()


def editar_producto(producto_id, nuevo_nombre, nuevo_precio, nueva_categoria_id):
    """Modifica un producto existente."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE productos
        SET nombre = ?, precio_por_gramo = ?, categoria_id = ?
        WHERE id = ?
    """, (nuevo_nombre, nuevo_precio, nueva_categoria_id, producto_id))
    conexion.commit()
    conexion.close()

# ─── TICKETS ─────────────────────────────────────────────


def inicializar_tablas_ticket(cursor):
    """Crea las tablas de tickets si no existen."""

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha     TEXT NOT NULL UNIQUE,
            gastos    REAL DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lineas_ticket (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id   INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            nombre      TEXT NOT NULL,
            categoria   TEXT NOT NULL,
            peso        REAL NOT NULL,
            precio_gramo REAL NOT NULL,
            total       REAL NOT NULL,
            FOREIGN KEY (ticket_id) REFERENCES tickets(id)
        )
    """)


def obtener_o_crear_ticket_hoy():
    """Devuelve el ticket de hoy (lo crea si no existe)."""
    hoy = datetime.date.today().isoformat()  # Formato: 2026-05-05
    conexion = conectar()
    cursor = conexion.cursor()
    inicializar_tablas_ticket(cursor)
    cursor.execute("SELECT id FROM tickets WHERE fecha = ?", (hoy,))
    fila = cursor.fetchone()
    if fila:
        ticket_id = fila[0]
    else:
        cursor.execute("INSERT INTO tickets (fecha) VALUES (?)", (hoy,))
        ticket_id = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return ticket_id, hoy


def agregar_linea_ticket(ticket_id, producto_id, nombre, categoria, peso, precio_gramo, total):
    """Añade una línea de venta al ticket."""
    conexion = conectar()
    cursor = conexion.cursor()
    inicializar_tablas_ticket(cursor)
    cursor.execute("""
        INSERT INTO lineas_ticket
        (ticket_id, producto_id, nombre, categoria, peso, precio_gramo, total)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ticket_id, producto_id, nombre, categoria, peso, precio_gramo, total))
    conexion.commit()
    conexion.close()


def obtener_lineas_ticket(ticket_id):
    """Devuelve todas las líneas de un ticket."""
    conexion = conectar()
    cursor = conexion.cursor()
    inicializar_tablas_ticket(cursor)
    cursor.execute("""
        SELECT nombre, categoria, peso, precio_gramo, total
        FROM lineas_ticket
        WHERE ticket_id = ?
        ORDER BY categoria, nombre
    """, (ticket_id,))
    lineas = cursor.fetchall()
    conexion.close()
    return lineas


def actualizar_gastos(ticket_id, gastos):
    """Guarda los gastos del día en el ticket."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("UPDATE tickets SET gastos = ? WHERE id = ?", (gastos, ticket_id))
    conexion.commit()
    conexion.close()


def obtener_gastos(ticket_id):
    """Devuelve los gastos guardados del ticket."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT gastos FROM tickets WHERE id = ?", (ticket_id,))
    fila = cursor.fetchone()
    conexion.close()
    return fila[0] if fila else 0

# ─── HISTORIAL ────────────────────────────────────────────

def listar_tickets():
    """Devuelve todos los tickets guardados ordenados por fecha descendente."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT t.id, t.fecha, t.gastos,
               COALESCE(SUM(l.total), 0) as total_ventas
        FROM tickets t
        LEFT JOIN lineas_ticket l ON t.id = l.ticket_id
        GROUP BY t.id
        ORDER BY t.fecha DESC
    """)
    tickets = cursor.fetchall()
    conexion.close()
    return tickets

def obtener_ticket_por_fecha(fecha):
    """Devuelve el id de un ticket dado su fecha (formato YYYY-MM-DD)."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id FROM tickets WHERE fecha = ?", (fecha,))
    fila = cursor.fetchone()
    conexion.close()
    return fila[0] if fila else None