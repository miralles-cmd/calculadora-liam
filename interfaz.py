# interfaz.py - Interfaz visual con Tkinter

import tkinter as tk
from tkinter import ttk, messagebox
from base_datos import (inicializar_db, listar_categorias, editar_categoria,
                        agregar_producto, listar_productos, buscar_producto,
                        eliminar_producto, editar_producto)
from tickets import mostrar_ticket
from exportar import generar_imagen_ticket
from base_datos import (obtener_o_crear_ticket_hoy, agregar_linea_ticket,
                        obtener_lineas_ticket, actualizar_gastos, obtener_gastos,
                        listar_tickets, obtener_ticket_por_fecha)
from calculos import calcular_precio


# ══════════════════════════════════════════════════════════
#  VENTANA PRINCIPAL
# ══════════════════════════════════════════════════════════

class AppTienda(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestión de Tienda")
        self.geometry("900x650")
        self.resizable(True, True)
        self.configure(bg="#1e1e2e")

        self._construir_layout()
        self._mostrar_panel(PanelTicket)  # Pantalla de inicio: ticket del día

    def _construir_layout(self):
        # ── Barra lateral izquierda ────────────────────────
        self.sidebar = tk.Frame(self, bg="#13131f", width=180)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="🛒 TIENDA",
                 bg="#13131f", fg="#ffffff",
                 font=("Arial", 14, "bold")).pack(pady=(24, 4))

        tk.Label(self.sidebar, text="Gestión de ventas",
                 bg="#13131f", fg="#888888",
                 font=("Arial", 9)).pack(pady=(0, 24))

        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x", padx=16)

        botones = [
            ("🧾  Ticket del día",  PanelTicket),
            ("📦  Productos",       PanelProductos),
            ("📁  Categorías",      PanelCategorias),
            ("📅  Historial",       PanelHistorial),
        ]

        for texto, panel_clase in botones:
            btn = tk.Button(
                self.sidebar, text=texto,
                bg="#13131f", fg="#cccccc",
                activebackground="#2a2a3e", activeforeground="#ffffff",
                font=("Arial", 11), bd=0, pady=12, anchor="w", padx=20,
                cursor="hand2",
                command=lambda p=panel_clase: self._mostrar_panel(p)
            )
            btn.pack(fill="x")

        # ── Área de contenido principal ────────────────────
        self.contenido = tk.Frame(self, bg="#1e1e2e")
        self.contenido.pack(side="left", fill="both", expand=True)

        self.panel_actual = None

    def _mostrar_panel(self, panel_clase):
        if self.panel_actual:
            self.panel_actual.destroy()
        self.panel_actual = panel_clase(self.contenido)
        self.panel_actual.pack(fill="both", expand=True)


# ══════════════════════════════════════════════════════════
#  HELPERS DE ESTILO
# ══════════════════════════════════════════════════════════

def titulo(parent, texto):
    tk.Label(parent, text=texto, bg="#1e1e2e", fg="#ffffff",
             font=("Arial", 16, "bold")).pack(anchor="w", padx=24, pady=(20, 4))

def subtitulo(parent, texto):
    tk.Label(parent, text=texto, bg="#1e1e2e", fg="#888888",
             font=("Arial", 10)).pack(anchor="w", padx=24, pady=(0, 16))

def boton(parent, texto, comando, color="#3a3af0"):
    tk.Button(parent, text=texto, command=comando,
              bg=color, fg="white", font=("Arial", 10, "bold"),
              bd=0, padx=16, pady=8, cursor="hand2",
              activebackground="#5555ff", activeforeground="white"
              ).pack(side="left", padx=4)

def campo(parent, etiqueta, valor_default=""):
    frame = tk.Frame(parent, bg="#1e1e2e")
    frame.pack(anchor="w", padx=24, pady=4)
    tk.Label(frame, text=etiqueta, bg="#1e1e2e", fg="#aaaaaa",
             font=("Arial", 10), width=18, anchor="w").pack(side="left")
    var = tk.StringVar(value=valor_default)
    entry = tk.Entry(frame, textvariable=var, font=("Arial", 11),
                     bg="#2a2a3e", fg="white", insertbackground="white",
                     relief="flat", bd=6, width=22)
    entry.pack(side="left")
    return var


# ══════════════════════════════════════════════════════════
#  PANEL: TICKET DEL DÍA
# ══════════════════════════════════════════════════════════

class PanelTicket(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#1e1e2e")
        self.ticket_id, self.fecha = obtener_o_crear_ticket_hoy()
        self._construir()

    def _construir(self):
        titulo(self, f"🧾 Ticket del día — {self.fecha}")
        subtitulo(self, "Ventas registradas hoy")

        # ── Tabla de líneas ────────────────────────────────
        frame_tabla = tk.Frame(self, bg="#1e1e2e")
        frame_tabla.pack(fill="both", expand=True, padx=24)

        cols = ("Producto", "Categoría", "Peso (g)", "Precio/g", "Total €")
        self.tabla = ttk.Treeview(frame_tabla, columns=cols, show="headings", height=12)

        for col in cols:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center", width=140)
        self.tabla.column("Producto", width=180)

        scroll = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # ── Totales ────────────────────────────────────────
        self.frame_totales = tk.Frame(self, bg="#13131f")
        self.frame_totales.pack(fill="x", padx=24, pady=8)
        self.lbl_total = tk.Label(self.frame_totales, text="",
                                   bg="#13131f", fg="#64e864",
                                   font=("Arial", 13, "bold"))
        self.lbl_total.pack(side="left", padx=16, pady=8)
        self.lbl_neto = tk.Label(self.frame_totales, text="",
                                  bg="#13131f", fg="#aaaaaa",
                                  font=("Arial", 11))
        self.lbl_neto.pack(side="left", padx=16)

        # ── Botones ────────────────────────────────────────
        frame_botones = tk.Frame(self, bg="#1e1e2e")
        frame_botones.pack(anchor="w", padx=20, pady=8)
        boton(frame_botones, "➕ Añadir venta", self._abrir_añadir)
        boton(frame_botones, "💸 Registrar gastos", self._abrir_gastos, color="#c05000")
        boton(frame_botones, "🖼️ Exportar JPG", self._exportar, color="#007700")

        self._actualizar_tabla()

    def _actualizar_tabla(self):
        for row in self.tabla.get_children():
            self.tabla.delete(row)

        lineas = obtener_lineas_ticket(self.ticket_id)
        total = 0
        for linea in lineas:
            nombre, cat, peso, precio_g, t = linea
            self.tabla.insert("", "end", values=(
                nombre, cat, f"{peso:.2f}", f"{precio_g:.4f}", f"{t:.2f} €"
            ))
            total += t

        gastos = obtener_gastos(self.ticket_id)
        self.lbl_total.config(text=f"Total ventas: {total:.2f} €")
        if gastos > 0:
            self.lbl_neto.config(text=f"  −  Gastos: {gastos:.2f} €   →   Neto: {total - gastos:.2f} €")
        else:
            self.lbl_neto.config(text="")

    def _abrir_añadir(self):
        DialogoVenta(self, self.ticket_id, self._actualizar_tabla)

    def _abrir_gastos(self):
        DialogoGastos(self, self.ticket_id, self._actualizar_tabla)

    def _exportar(self):
        lineas = obtener_lineas_ticket(self.ticket_id)
        if not lineas:
            messagebox.showwarning("Aviso", "El ticket está vacío.")
            return
        ruta = generar_imagen_ticket(self.ticket_id, self.fecha)
        messagebox.showinfo("✅ Exportado", f"Imagen guardada en:\n{ruta}")


# ══════════════════════════════════════════════════════════
#  DIÁLOGO: AÑADIR VENTA
# ══════════════════════════════════════════════════════════

class DialogoVenta(tk.Toplevel):
    def __init__(self, parent, ticket_id, callback):
        super().__init__(parent)
        self.ticket_id = ticket_id
        self.callback  = callback
        self.title("Añadir venta")
        self.geometry("420x360")
        self.configure(bg="#1e1e2e")
        self.grab_set()
        self._construir()

    def _construir(self):
        tk.Label(self, text="Selecciona producto", bg="#1e1e2e", fg="#ffffff",
                 font=("Arial", 13, "bold")).pack(pady=(16, 8))

        self.productos = listar_productos()

        # Lista de productos con búsqueda
        frame_busq = tk.Frame(self, bg="#1e1e2e")
        frame_busq.pack(fill="x", padx=20)
        tk.Label(frame_busq, text="Buscar:", bg="#1e1e2e", fg="#aaaaaa",
                 font=("Arial", 10)).pack(side="left")
        self.var_busqueda = tk.StringVar()
        self.var_busqueda.trace("w", self._filtrar)
        tk.Entry(frame_busq, textvariable=self.var_busqueda,
                 bg="#2a2a3e", fg="white", insertbackground="white",
                 font=("Arial", 11), relief="flat", bd=6).pack(side="left", fill="x", expand=True, padx=8)

        self.listbox = tk.Listbox(self, bg="#2a2a3e", fg="white",
                                   font=("Arial", 11), height=7,
                                   selectbackground="#3a3af0")
        self.listbox.pack(fill="x", padx=20, pady=8)
        self._llenar_lista(self.productos)

        # Peso
        frame_peso = tk.Frame(self, bg="#1e1e2e")
        frame_peso.pack(anchor="w", padx=20, pady=4)
        tk.Label(frame_peso, text="Peso (gramos):", bg="#1e1e2e", fg="#aaaaaa",
                 font=("Arial", 10)).pack(side="left")
        self.var_peso = tk.StringVar()
        tk.Entry(frame_peso, textvariable=self.var_peso,
                 bg="#2a2a3e", fg="white", insertbackground="white",
                 font=("Arial", 11), relief="flat", bd=6, width=12).pack(side="left", padx=8)

        tk.Button(self, text="✅ Añadir al ticket", command=self._añadir,
                  bg="#3a3af0", fg="white", font=("Arial", 11, "bold"),
                  bd=0, pady=10, cursor="hand2").pack(fill="x", padx=20, pady=12)

    def _llenar_lista(self, productos):
        self.listbox.delete(0, "end")
        for p in productos:
            self.listbox.insert("end", f"{p[1]}  ({p[2]:.4f} €/g)  [{p[3]}]")

    def _filtrar(self, *args):
        texto = self.var_busqueda.get().lower()
        filtrados = [p for p in self.productos if texto in p[1].lower()]
        self._llenar_lista(filtrados)
        self._productos_filtrados = filtrados

    def _añadir(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona un producto.", parent=self)
            return

        lista = getattr(self, "_productos_filtrados", self.productos)
        producto = lista[sel[0]]

        peso_txt = self.var_peso.get().replace(",", ".")
        try:
            peso = float(peso_txt)
            if peso <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Aviso", "Ingresa un peso válido.", parent=self)
            return

        total = calcular_precio(peso, producto[2])
        agregar_linea_ticket(
            self.ticket_id, producto[0], producto[1],
            producto[3] or "Sin categoría", peso, producto[2], total
        )
        self.callback()
        self.destroy()


# ══════════════════════════════════════════════════════════
#  DIÁLOGO: GASTOS
# ══════════════════════════════════════════════════════════

class DialogoGastos(tk.Toplevel):
    def __init__(self, parent, ticket_id, callback):
        super().__init__(parent)
        self.ticket_id = ticket_id
        self.callback  = callback
        self.title("Registrar gastos")
        self.geometry("320x180")
        self.configure(bg="#1e1e2e")
        self.grab_set()

        gastos_actuales = obtener_gastos(ticket_id)
        tk.Label(self, text="Gastos del día (€)", bg="#1e1e2e", fg="#ffffff",
                 font=("Arial", 13, "bold")).pack(pady=(20, 8))
        self.var = tk.StringVar(value=str(gastos_actuales))
        tk.Entry(self, textvariable=self.var, bg="#2a2a3e", fg="white",
                 insertbackground="white", font=("Arial", 13),
                 relief="flat", bd=8, justify="center").pack(padx=30, fill="x")
        tk.Button(self, text="Guardar", command=self._guardar,
                  bg="#c05000", fg="white", font=("Arial", 11, "bold"),
                  bd=0, pady=8, cursor="hand2").pack(fill="x", padx=30, pady=16)

    def _guardar(self):
        try:
            valor = float(self.var.get().replace(",", "."))
            if valor < 0:
                raise ValueError
            actualizar_gastos(self.ticket_id, valor)
            self.callback()
            self.destroy()
        except ValueError:
            messagebox.showwarning("Aviso", "Valor no válido.", parent=self)


# ══════════════════════════════════════════════════════════
#  PANEL: PRODUCTOS
# ══════════════════════════════════════════════════════════

class PanelProductos(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#1e1e2e")
        self._construir()

    def _construir(self):
        titulo(self, "📦 Productos")
        subtitulo(self, "Gestiona tu catálogo de productos")

        # Tabla
        frame_tabla = tk.Frame(self, bg="#1e1e2e")
        frame_tabla.pack(fill="both", expand=True, padx=24)

        cols = ("ID", "Nombre", "Precio/g €", "Categoría")
        self.tabla = ttk.Treeview(frame_tabla, columns=cols, show="headings", height=10)
        for col in cols:
            self.tabla.heading(col, text=col)
        self.tabla.column("ID", width=40, anchor="center")
        self.tabla.column("Nombre", width=200)
        self.tabla.column("Precio/g €", width=100, anchor="center")
        self.tabla.column("Categoría", width=120, anchor="center")

        scroll = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Formulario
        frame_form = tk.Frame(self, bg="#1e1e2e")
        frame_form.pack(fill="x", padx=24, pady=8)

        self.var_nombre  = campo(frame_form, "Nombre:")
        self.var_precio  = campo(frame_form, "Precio por gramo:")

        frame_cat = tk.Frame(frame_form, bg="#1e1e2e")
        frame_cat.pack(anchor="w", pady=4)
        tk.Label(frame_cat, text="Categoría:", bg="#1e1e2e", fg="#aaaaaa",
                 font=("Arial", 10), width=18, anchor="w").pack(side="left")
        self.categorias = listar_categorias()
        self.var_cat = tk.StringVar()
        combo = ttk.Combobox(frame_cat, textvariable=self.var_cat, width=20,
                             values=[c[1] for c in self.categorias], state="readonly")
        combo.pack(side="left")
        if self.categorias:
            combo.current(0)

        # Botones
        frame_btn = tk.Frame(self, bg="#1e1e2e")
        frame_btn.pack(anchor="w", padx=20, pady=4)
        boton(frame_btn, "➕ Agregar", self._agregar)
        boton(frame_btn, "🗑️ Eliminar seleccionado", self._eliminar, color="#880000")

        self._actualizar_tabla()

    def _actualizar_tabla(self):
        for row in self.tabla.get_children():
            self.tabla.delete(row)
        for p in listar_productos():
            self.tabla.insert("", "end", values=(p[0], p[1], f"{p[2]:.4f}", p[3]))

    def _agregar(self):
        nombre = self.var_nombre.get().strip()
        precio_txt = self.var_precio.get().replace(",", ".")
        cat_nombre = self.var_cat.get()

        if not nombre:
            messagebox.showwarning("Aviso", "El nombre no puede estar vacío.")
            return
        try:
            precio = float(precio_txt)
            if precio <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Aviso", "Precio no válido.")
            return

        cat_id = next((c[0] for c in self.categorias if c[1] == cat_nombre), None)
        if not cat_id:
            messagebox.showwarning("Aviso", "Selecciona una categoría.")
            return

        agregar_producto(nombre, precio, cat_id)
        self.var_nombre.set("")
        self.var_precio.set("")
        self._actualizar_tabla()

    def _eliminar(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona un producto.")
            return
        valores = self.tabla.item(sel[0])["values"]
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{valores[1]}'?"):
            eliminar_producto(valores[0])
            self._actualizar_tabla()


# ══════════════════════════════════════════════════════════
#  PANEL: CATEGORÍAS
# ══════════════════════════════════════════════════════════

class PanelCategorias(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#1e1e2e")
        self._construir()

    def _construir(self):
        titulo(self, "📁 Categorías")
        subtitulo(self, "Edita las 3 categorías disponibles")

        self.categorias = listar_categorias()
        self.vars = []

        for cat in self.categorias:
            frame = tk.Frame(self, bg="#1e1e2e")
            frame.pack(anchor="w", padx=24, pady=6)
            tk.Label(frame, text=f"Categoría {cat[0]}:", bg="#1e1e2e", fg="#aaaaaa",
                     font=("Arial", 10), width=14, anchor="w").pack(side="left")
            var = tk.StringVar(value=cat[1])
            tk.Entry(frame, textvariable=var, bg="#2a2a3e", fg="white",
                     insertbackground="white", font=("Arial", 11),
                     relief="flat", bd=6, width=22).pack(side="left", padx=8)
            self.vars.append((cat[0], var))

        frame_btn = tk.Frame(self, bg="#1e1e2e")
        frame_btn.pack(anchor="w", padx=20, pady=12)
        boton(frame_btn, "💾 Guardar cambios", self._guardar)

    def _guardar(self):
        for cat_id, var in self.vars:
            nuevo = var.get().strip()
            if nuevo:
                editar_categoria(cat_id, nuevo)
        messagebox.showinfo("✅", "Categorías actualizadas.")


# ══════════════════════════════════════════════════════════
#  PANEL: HISTORIAL
# ══════════════════════════════════════════════════════════

class PanelHistorial(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#1e1e2e")
        self._construir()

    def _construir(self):
        titulo(self, "📅 Historial de tickets")
        subtitulo(self, "Consulta tickets de días anteriores")

        cols = ("Fecha", "Total ventas", "Gastos", "Neto")
        self.tabla = ttk.Treeview(self, columns=cols, show="headings", height=12)
        for col in cols:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center", width=160)

        scroll = ttk.Scrollbar(self, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)

        frame_tabla = tk.Frame(self, bg="#1e1e2e")
        frame_tabla.pack(fill="both", expand=True, padx=24)
        self.tabla = ttk.Treeview(frame_tabla, columns=cols, show="headings", height=12)
        for col in cols:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center", width=160)
        scroll = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tabla.bind("<Double-1>", self._ver_detalle)

        frame_btn = tk.Frame(self, bg="#1e1e2e")
        frame_btn.pack(anchor="w", padx=20, pady=8)
        boton(frame_btn, "🖼️ Exportar ticket seleccionado", self._exportar, color="#007700")

        self._cargar()

    def _cargar(self):
        for row in self.tabla.get_children():
            self.tabla.delete(row)
        for t in listar_tickets():
            tid, fecha, gastos, total = t
            neto = total - gastos
            self.tabla.insert("", "end", values=(fecha, f"{total:.2f} €",
                                      f"{gastos:.2f} €", f"{neto:.2f} €"))

    def _ver_detalle(self, event):
        sel = self.tabla.selection()
        if not sel:
            return
        valores = self.tabla.item(sel[0])["values"]
        fecha = valores[0]
        ticket_id = obtener_ticket_por_fecha(fecha)
        if ticket_id:
            DialogoDetalleTicket(self, ticket_id, fecha)

    def _exportar(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona un ticket.")
            return
        valores = self.tabla.item(sel[0])["values"]
        fecha = valores[0]
        ticket_id = obtener_ticket_por_fecha(fecha)
        if ticket_id:
            ruta = generar_imagen_ticket(ticket_id, fecha)
            messagebox.showinfo("✅ Exportado", f"Imagen guardada en:\n{ruta}")


# ══════════════════════════════════════════════════════════
#  DIÁLOGO: DETALLE DE TICKET
# ══════════════════════════════════════════════════════════

class DialogoDetalleTicket(tk.Toplevel):
    def __init__(self, parent, ticket_id, fecha):
        super().__init__(parent)
        self.title(f"Ticket — {fecha}")
        self.geometry("500x420")
        self.configure(bg="#1e1e2e")
        self.grab_set()

        tk.Label(self, text=f"🧾 {fecha}", bg="#1e1e2e", fg="#ffffff",
                 font=("Arial", 14, "bold")).pack(pady=(16, 8))

        texto = tk.Text(self, bg="#13131f", fg="#dddddd", font=("Courier", 10),
                        relief="flat", padx=12, pady=12)
        texto.pack(fill="both", expand=True, padx=16, pady=8)

        lineas = obtener_lineas_ticket(ticket_id)
        gastos = obtener_gastos(ticket_id)

        categorias = {}
        for l in lineas:
            nombre, cat, peso, precio_g, total = l
            categorias.setdefault(cat, []).append(l)

        gran_total = 0
        for cat, items in categorias.items():
            texto.insert("end", f"\n▸ {cat.upper()}\n")
            subtotal = 0
            for item in items:
                texto.insert("end", f"  {item[0]:20s}  {item[2]:6.2f}g  →  {item[4]:.2f} €\n")
                subtotal += item[4]
                gran_total += item[4]
            texto.insert("end", f"  {'─'*38}\n")
            texto.insert("end", f"  Subtotal: {subtotal:.2f} €\n")

        texto.insert("end", f"\n{'═'*42}\n")
        texto.insert("end", f"  TOTAL VENTAS:   {gran_total:.2f} €\n")
        if gastos > 0:
            texto.insert("end", f"  GASTOS:       - {gastos:.2f} €\n")
            texto.insert("end", f"  NETO:           {gran_total - gastos:.2f} €\n")
        texto.config(state="disabled")