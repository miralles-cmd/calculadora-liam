# pantallas/pantalla_historial.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.metrics import dp

from base_datos import (listar_tickets, obtener_ticket_por_fecha,
                        obtener_lineas_ticket, obtener_gastos)
from exportar import generar_imagen_ticket

AZUL   = (0.23, 0.23, 0.94, 1)
VERDE  = (0.1,  0.6,  0.1,  1)
BLANCO = (1,    1,    1,    1)
GRIS   = (0.6,  0.6,  0.6,  1)
NARANJA = (0.75, 0.31, 0.0, 1)

NOMBRES_MES = {
    "01": "Enero", "02": "Febrero", "03": "Marzo",
    "04": "Abril", "05": "Mayo", "06": "Junio",
    "07": "Julio", "08": "Agosto", "09": "Septiembre",
    "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
}


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


class PantallaHistorial(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ticket_sel = [None]
        self._construir()

    def _construir(self):
        raiz = BoxLayout(orientation="vertical",
                         padding=dp(12), spacing=dp(8))

        raiz.add_widget(lbl("Historial de tickets", size=20, bold=True))
        raiz.add_widget(lbl("Pulsa un ticket para ver el detalle",
                             size=12, color=GRIS))

        # ── Lista de tickets ───────────────────────────────
        self.contenedor = GridLayout(cols=1, spacing=dp(4),
                                      size_hint_y=None)
        self.contenedor.bind(
            minimum_height=self.contenedor.setter("height")
        )

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.contenedor)
        raiz.add_widget(scroll)

        # ── Botones ────────────────────────────────────────
        frame_btn = BoxLayout(size_hint=(1, None), height=dp(52),
                               spacing=dp(8))
        b_exportar = btn("Exportar JPG", color=VERDE, alto=dp(52))
        b_volver   = btn("Volver", color=(0.3, 0.3, 0.3, 1), alto=dp(52))

        b_exportar.bind(on_press=lambda x: self._exportar())
        b_volver.bind(on_press=lambda x: setattr(
            self.manager, "current", "menu"))

        frame_btn.add_widget(b_exportar)
        frame_btn.add_widget(b_volver)
        raiz.add_widget(frame_btn)

        self.add_widget(raiz)
        self._actualizar()

    def on_enter(self):
        self._actualizar()

    def _actualizar(self):
        self.contenedor.clear_widgets()
        self._ticket_sel[0] = None
        self._botones_tickets = []

        tickets = listar_tickets()

        if not tickets:
            self.contenedor.add_widget(
                lbl("  Sin tickets guardados todavia.", color=GRIS)
            )
            return

        # Agrupar por mes
        meses = {}
        for t in tickets:
            mes = t[1][:7]
            meses.setdefault(mes, []).append(t)

        for mes, items in meses.items():
            anio, num_mes = mes.split("-")
            cab = lbl(f"  {NOMBRES_MES[num_mes].upper()} {anio}",
                       size=13, bold=True,
                       color=(0.4, 0.6, 1, 1))
            cab.size_hint_y = None
            cab.height = dp(32)
            self.contenedor.add_widget(cab)

            for t in items:
                tid, fecha, gastos, total = t
                neto = total - gastos
                texto = f"  {fecha}    Ventas: {total:.2f}    Neto: {neto:.2f} EUR"
                b = Button(
                    text=texto, font_size=12,
                    size_hint_y=None, height=dp(40),
                    background_normal="",
                    background_color=(0.2, 0.2, 0.35, 1),
                    halign="left", padding=(dp(8), 0)
                )
                b.bind(on_press=lambda btn, ticket=t:
                       self._seleccionar(btn, ticket))
                self._botones_tickets.append((b, t))
                self.contenedor.add_widget(b)

    def _seleccionar(self, boton, ticket):
        self._ticket_sel[0] = ticket
        for b, _ in self._botones_tickets:
            b.background_color = (0.2, 0.2, 0.35, 1)
        boton.background_color = (0.23, 0.23, 0.94, 1)
        self._ver_detalle(ticket)

    def _ver_detalle(self, ticket):
        tid, fecha, gastos, total = ticket
        lineas = obtener_lineas_ticket(tid)

        contenido = BoxLayout(orientation="vertical",
                               padding=dp(12), spacing=dp(6))

        scroll = ScrollView(size_hint=(1, 0.85))
        grid   = GridLayout(cols=1, spacing=dp(2), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        categorias = {}
        for l in lineas:
            nombre, cat, peso, precio_g, ltotal = l
            categorias.setdefault(cat, []).append(l)

        gran_total = 0
        for cat, items in categorias.items():
            cab = lbl(f"  {cat.upper()}", size=13, bold=True,
                       color=(0.4, 0.6, 1, 1))
            cab.size_hint_y = None
            cab.height = dp(28)
            grid.add_widget(cab)

            subtotal = 0
            for item in items:
                fila = lbl(f"  {item[0]:20s}  {item[4]:.2f} EUR",
                            size=12)
                fila.size_hint_y = None
                fila.height = dp(26)
                grid.add_widget(fila)
                subtotal += item[4]
                gran_total += item[4]

            sub = lbl(f"  Subtotal: {subtotal:.2f} EUR",
                       size=12, color=GRIS)
            sub.size_hint_y = None
            sub.height = dp(24)
            grid.add_widget(sub)

        scroll.add_widget(grid)
        contenido.add_widget(scroll)

        resumen = lbl(
            f"Total: {gran_total:.2f} EUR"
            + (f"   Gastos: -{gastos:.2f}"
               f"   Neto: {gran_total - gastos:.2f} EUR"
               if gastos > 0 else ""),
            size=13, bold=True, color=VERDE
        )
        resumen.size_hint_y = None
        resumen.height = dp(32)
        contenido.add_widget(resumen)

        popup = Popup(title=f"Ticket {fecha}",
                      content=contenido, size_hint=(0.93, 0.85))
        b = btn("Cerrar", color=(0.3, 0.3, 0.3, 1), alto=dp(42))
        b.bind(on_press=popup.dismiss)
        contenido.add_widget(b)
        popup.open()

    def _exportar(self):
        t = self._ticket_sel[0]
        if not t:
            self._aviso("Selecciona un ticket primero.")
            return
        tid, fecha, gastos, total = t
        ruta = generar_imagen_ticket(tid, fecha)
        self._aviso(f"Imagen guardada en:\n{ruta}")

    def _aviso(self, mensaje):
        contenido = BoxLayout(orientation="vertical",
                               padding=dp(12), spacing=dp(8))
        contenido.add_widget(lbl(mensaje, size=13))
        popup = Popup(title="Aviso", content=contenido,
                      size_hint=(0.8, 0.32))
        b = btn("OK", color=AZUL, alto=dp(44))
        b.bind(on_press=popup.dismiss)
        contenido.add_widget(b)
        popup.open()