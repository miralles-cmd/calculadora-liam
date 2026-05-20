# pantallas/pantalla_ticket.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.metrics import dp

from base_datos import (obtener_o_crear_ticket_hoy, obtener_lineas_ticket,
                        obtener_gastos, actualizar_gastos, listar_productos,
                        agregar_linea_ticket)
from calculos import calcular_precio


# ── Colores ────────────────────────────────────────────────
AZUL       = (0.23, 0.23, 0.94, 1)
VERDE      = (0.1,  0.6,  0.1,  1)
NARANJA    = (0.75, 0.31, 0.0,  1)
FONDO      = (0.12, 0.12, 0.18, 1)
FONDO2     = (0.08, 0.08, 0.13, 1)
BLANCO     = (1,    1,    1,    1)
GRIS       = (0.6,  0.6,  0.6,  1)



from kivy.metrics import dp, sp

def lbl(texto, size=18, color=BLANCO, bold=False, halign="left"):
    l = Label(text=texto, font_size=sp(size), color=color, bold=bold,
               halign=halign, valign="middle")
    l.bind(size=lambda s, v: setattr(s, "text_size", v))
    return l

def btn(texto, color=AZUL, alto=dp(58)):
    return Button(
        text=texto, font_size=sp(18),
        size_hint=(1, None), height=alto,
        background_color=color,
        background_normal=""
    )


class PantallaTicket(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ticket_id, self.fecha = obtener_o_crear_ticket_hoy()
        self._construir()

    def _construir(self):
        raiz = BoxLayout(orientation="vertical",
                         padding=dp(12), spacing=dp(8))

        # ── Cabecera ───────────────────────────────────────
        raiz.add_widget(lbl(f"Ticket del dia — {self.fecha}",
                             size=18, bold=True))
        raiz.add_widget(lbl("Ventas registradas hoy", size=12, color=GRIS))

        # ── Lista de ventas (scrollable) ───────────────────
        self.contenedor_ventas = GridLayout(
            cols=1, spacing=dp(4),
            size_hint_y=None, padding=(0, dp(4))
        )
        self.contenedor_ventas.bind(
            minimum_height=self.contenedor_ventas.setter("height")
        )

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.contenedor_ventas)
        raiz.add_widget(scroll)

        # ── Botones ────────────────────────────────────────
        b1 = Button(text="+ Anadir venta", font_size=sp(18),
                    size_hint=(1, None), height=dp(56),
                    background_color=AZUL, background_normal="")
        b2 = Button(text="Gastos del dia", font_size=sp(18),
                    size_hint=(1, None), height=dp(56),
                    background_color=NARANJA, background_normal="")
        b3 = Button(text="Exportar JPG", font_size=sp(18),
                    size_hint=(1, None), height=dp(56),
                    background_color=VERDE, background_normal="")
        b4 = Button(text="Volver al menu", font_size=sp(16),
                    size_hint=(1, None), height=dp(48),
                    background_color=(0.3, 0.3, 0.3, 1),
                    background_normal="")

        b1.bind(on_press=lambda x: self._abrir_anadir())
        b2.bind(on_press=lambda x: self._abrir_gastos())
        b3.bind(on_press=lambda x: self._exportar())
        b4.bind(on_press=lambda x: setattr(
            self.manager, "current", "menu"))

        raiz.add_widget(b1)
        raiz.add_widget(b2)
        raiz.add_widget(b3)
        raiz.add_widget(b4)

        self.add_widget(raiz)
        self._actualizar()

    def on_enter(self):
        """Se llama cada vez que se entra a esta pantalla."""
        self._actualizar()

    def _actualizar(self):
        self.contenedor_ventas.clear_widgets()
        lineas  = obtener_lineas_ticket(self.ticket_id)
        gastos  = obtener_gastos(self.ticket_id)

        if not lineas:
            self.contenedor_ventas.add_widget(
                lbl("  Sin ventas registradas todavia.", color=GRIS)
            )
        else:
            categorias = {}
            for l in lineas:
                nombre, cat, peso, precio_g, total = l
                categorias.setdefault(cat, []).append(l)

            gran_total = 0
            for cat, items in categorias.items():
                subtotal = sum(i[4] for i in items)
                gran_total += subtotal

                # Cabecera categoría
                cab = lbl(f"  {cat.upper()}",
                           size=13, bold=True, color=(0.4, 0.6, 1, 1))
                cab.size_hint_y = None
                cab.height = dp(30)
                self.contenedor_ventas.add_widget(cab)

                for item in items:
                    fila = BoxLayout(size_hint_y=None, height=dp(28),
                                     spacing=dp(8))
                    fila.add_widget(lbl(f"  {item[0]}", size=13))
                    fila.add_widget(lbl(f"{item[2]:.2f}g",
                                         size=13, color=GRIS, halign="center"))
                    fila.add_widget(lbl(f"{item[4]:.2f} EUR",
                                         size=13, halign="right"))
                    self.contenedor_ventas.add_widget(fila)

                sep = lbl(f"  Subtotal {cat}: {subtotal:.2f} EUR",
                           size=12, color=GRIS)
                sep.size_hint_y = None
                sep.height = dp(24)
                self.contenedor_ventas.add_widget(sep)

            self.lbl_total.text = f"Total ventas: {gran_total:.2f} EUR"
            if gastos > 0:
                self.lbl_neto.text = (f"Gastos: -{gastos:.2f} EUR   "
                                       f"Neto: {gran_total - gastos:.2f} EUR")
            else:
                self.lbl_neto.text = ""

    # ── Popup: Añadir venta ────────────────────────────────

    def _abrir_anadir(self):
        productos = listar_productos()
        if not productos:
            self._popup_aviso("Sin productos",
                              "Primero agrega productos en la seccion Productos.")
            return

        contenido = BoxLayout(orientation="vertical",
                               padding=dp(12), spacing=dp(8))

        contenido.add_widget(lbl("Selecciona producto:", size=14, bold=True))

        # Lista de productos como botones
        scroll = ScrollView(size_hint=(1, 0.6))
        lista  = GridLayout(cols=1, spacing=dp(4), size_hint_y=None)
        lista.bind(minimum_height=lista.setter("height"))

        self._producto_sel = [None]

        botones_prod = []
        for p in productos:
            b = Button(
                text=f"{p[1]}  ({p[2]:.4f} EUR/g)",
                font_size=sp(16), size_hint_y=None, height=dp(40),
                background_normal="",
                background_color=(0.2, 0.2, 0.35, 1)
            )
            botones_prod.append((b, p))
            lista.add_widget(b)

        def seleccionar(btn_presionado, prod):
            self._producto_sel[0] = prod
            for b2, _ in botones_prod:
                b2.background_color = (0.2, 0.2, 0.35, 1)
            btn_presionado.background_color = (0.23, 0.23, 0.94, 1)

        for b, p in botones_prod:
            b.bind(on_press=lambda btn, prod=p: seleccionar(btn, prod))

        scroll.add_widget(lista)
        contenido.add_widget(scroll)

        contenido.add_widget(lbl("Peso en gramos:", size=14))
        inp_peso = TextInput(
            hint_text="Ej: 250 o 0,5",
            font_size=16, multiline=False,
            size_hint=(1, None), height=dp(44),
            input_filter="float"
        )
        contenido.add_widget(inp_peso)

        self._popup_anadir = Popup(
            title="Anadir venta",
            content=contenido,
            size_hint=(0.92, 0.85)
        )

        def confirmar(x):
            prod = self._producto_sel[0]
            if not prod:
                return
            try:
                peso = float(inp_peso.text.replace(",", "."))
                if peso <= 0:
                    return
            except ValueError:
                return
            total = calcular_precio(peso, prod[2])
            agregar_linea_ticket(
                self.ticket_id, prod[0], prod[1],
                prod[3] or "Sin categoria", peso, prod[2], total
            )
            self._popup_anadir.dismiss()
            self._actualizar()

        b_confirmar = btn("Confirmar", color=VERDE)
        b_confirmar.bind(on_press=confirmar)
        contenido.add_widget(b_confirmar)

        self._popup_anadir.open()

    # ── Popup: Gastos ──────────────────────────────────────

    def _abrir_gastos(self):
        gastos_act = obtener_gastos(self.ticket_id)
        contenido  = BoxLayout(orientation="vertical",
                                padding=dp(12), spacing=dp(8))
        contenido.add_widget(lbl("Gastos del dia (EUR):", size=14, bold=True))
        inp = TextInput(
            text=str(gastos_act), font_size=18,
            multiline=False, size_hint=(1, None), height=dp(48),
            input_filter="float"
        )
        contenido.add_widget(inp)

        popup = Popup(title="Registrar gastos",
                      content=contenido, size_hint=(0.8, 0.4))

        def guardar(x):
            try:
                v = float(inp.text.replace(",", "."))
                if v >= 0:
                    actualizar_gastos(self.ticket_id, v)
                    self._actualizar()
                    popup.dismiss()
            except ValueError:
                pass

        b = btn("Guardar", color=NARANJA)
        b.bind(on_press=guardar)
        contenido.add_widget(b)
        popup.open()

    # ── Exportar ───────────────────────────────────────────

    def _exportar(self):
        from exportar import generar_imagen_ticket
        lineas = obtener_lineas_ticket(self.ticket_id)
        if not lineas:
            self._popup_aviso("Aviso", "El ticket esta vacio.")
            return
        ruta = generar_imagen_ticket(self.ticket_id, self.fecha)
        self._popup_aviso("Exportado", f"Imagen guardada en:\n{ruta}")

    # ── Aviso genérico ─────────────────────────────────────

    def _popup_aviso(self, titulo, mensaje):
        contenido = BoxLayout(orientation="vertical",
                               padding=dp(12), spacing=dp(8))
        contenido.add_widget(lbl(mensaje, size=13))
        b = btn("Cerrar", color=AZUL)
        popup = Popup(title=titulo, content=contenido,
                      size_hint=(0.8, 0.35))
        b.bind(on_press=popup.dismiss)
        contenido.add_widget(b)
        popup.open()