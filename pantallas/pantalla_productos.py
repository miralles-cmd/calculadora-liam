# pantallas/pantalla_productos.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.metrics import dp

from base_datos import (listar_productos, agregar_producto,
                        eliminar_producto, listar_categorias)

AZUL    = (0.23, 0.23, 0.94, 1)
ROJO    = (0.6,  0.1,  0.1,  1)
VERDE   = (0.1,  0.6,  0.1,  1)
BLANCO  = (1,    1,    1,    1)
GRIS    = (0.6,  0.6,  0.6,  1)
FONDO   = (0.12, 0.12, 0.18, 1)


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


class PantallaProductos(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._producto_sel = [None]
        self._construir()

    def _construir(self):
        raiz = BoxLayout(orientation="vertical",
                         padding=dp(12), spacing=dp(8))

        # ── Cabecera ───────────────────────────────────────
        raiz.add_widget(lbl("Productos", size=20, bold=True))
        raiz.add_widget(lbl("Gestiona tu catalogo", size=12, color=GRIS))

        # ── Lista de productos ─────────────────────────────
        self.contenedor = GridLayout(
            cols=1, spacing=dp(4), size_hint_y=None
        )
        self.contenedor.bind(
            minimum_height=self.contenedor.setter("height")
        )

        scroll = ScrollView(size_hint=(1, 0.45))
        scroll.add_widget(self.contenedor)
        raiz.add_widget(scroll)

        # ── Formulario añadir ──────────────────────────────
        raiz.add_widget(lbl("Añadir producto:", size=14, bold=True))

        self.inp_nombre = TextInput(
            hint_text="Nombre del producto",
            font_size=sp(18), multiline=False,
            size_hint=(1, None), height=dp(42),
        )
        raiz.add_widget(self.inp_nombre)

        self.inp_precio = TextInput(
            hint_text="Precio por gramo (ej: 0.05)",
            font_size=sp(18), multiline=False,
            size_hint=(1, None), height=dp(42),
            input_filter="float"
        )
        raiz.add_widget(self.inp_precio)

        # Selector de categoría
        self.categorias = listar_categorias()
        nombres_cat = [c[1] for c in self.categorias]
        self.spinner_cat = Spinner(
            text=nombres_cat[0] if nombres_cat else "Sin categorias",
            values=nombres_cat,
            size_hint=(1, None), height=dp(42),
            font_size=sp(18)
        )
        raiz.add_widget(self.spinner_cat)

        # ── Botones ────────────────────────────────────────
        frame_btn = BoxLayout(size_hint=(1, None), height=dp(52),
                               spacing=dp(8))
        b_agregar  = btn("+ Agregar", color=AZUL, alto=dp(52))
        b_eliminar = btn("Eliminar seleccionado", color=ROJO, alto=dp(52))

        b_agregar.bind(on_press=lambda x: self._agregar())
        b_eliminar.bind(on_press=lambda x: self._eliminar())

        frame_btn.add_widget(b_agregar)
        frame_btn.add_widget(b_eliminar)
        raiz.add_widget(frame_btn)

        # ── Botón volver ───────────────────────────────────
        b_volver = btn("Volver al menu", color=(0.3, 0.3, 0.3, 1), alto=dp(42))
        b_volver.bind(on_press=lambda x: setattr(
            self.manager, "current", "menu"))
        raiz.add_widget(b_volver)

        self.add_widget(raiz)
        self._actualizar()

    def on_enter(self):
        self._actualizar()

    def _actualizar(self):
        self.contenedor.clear_widgets()
        self._producto_sel[0] = None
        self._botones_prod = []

        productos = listar_productos()
        if not productos:
            self.contenedor.add_widget(
                lbl("  Sin productos todavia.", color=GRIS)
            )
            return

        for p in productos:
            fila = Button(
                text=f"{p[1]}   {p[2]:.4f} EUR/g   [{p[3]}]",
                font_size=sp(16),
                size_hint_y=None, height=dp(40),
                background_normal="",
                background_color=(0.2, 0.2, 0.35, 1),
                halign="left", padding=(dp(10), 0)
            )
            fila.bind(on_press=lambda b, prod=p: self._seleccionar(b, prod))
            self._botones_prod.append((fila, p))
            self.contenedor.add_widget(fila)

    def _seleccionar(self, boton_presionado, producto):
        self._producto_sel[0] = producto
        for b, _ in self._botones_prod:
            b.background_color = (0.2, 0.2, 0.35, 1)
        boton_presionado.background_color = (0.23, 0.23, 0.94, 1)

    def _agregar(self):
        nombre = self.inp_nombre.text.strip()
        precio_txt = self.inp_precio.text.replace(",", ".")
        cat_nombre = self.spinner_cat.text

        if not nombre:
            self._aviso("El nombre no puede estar vacio.")
            return
        try:
            precio = float(precio_txt)
            if precio <= 0:
                raise ValueError
        except ValueError:
            self._aviso("Precio no valido.")
            return

        cat_id = next((c[0] for c in self.categorias
                       if c[1] == cat_nombre), None)
        if not cat_id:
            self._aviso("Selecciona una categoria valida.")
            return

        agregar_producto(nombre, precio, cat_id)
        self.inp_nombre.text = ""
        self.inp_precio.text = ""
        self._actualizar()

    def _eliminar(self):
        prod = self._producto_sel[0]
        if not prod:
            self._aviso("Selecciona un producto primero.")
            return

        contenido = BoxLayout(orientation="vertical",
                               padding=dp(12), spacing=dp(8))
        contenido.add_widget(lbl(f"Eliminar '{prod[1]}'?", size=14))

        popup = Popup(title="Confirmar",
                      content=contenido, size_hint=(0.8, 0.3))

        frame = BoxLayout(spacing=dp(8), size_hint=(1, None), height=dp(48))
        b_si = Button(text="Si, eliminar", background_color=ROJO,
                      background_normal="", font_size=sp(16))
        b_no = Button(text="Cancelar", background_color=(0.3, 0.3, 0.3, 1),
                      background_normal="", font_size=sp(16))

        def confirmar(x):
            eliminar_producto(prod[0])
            popup.dismiss()
            self._actualizar()

        b_si.bind(on_press=confirmar)
        b_no.bind(on_press=popup.dismiss)
        frame.add_widget(b_si)
        frame.add_widget(b_no)
        contenido.add_widget(frame)
        popup.open()

    def _aviso(self, mensaje):
        contenido = BoxLayout(orientation="vertical",
                               padding=dp(12), spacing=dp(8))
        contenido.add_widget(lbl(mensaje, size=13))
        popup = Popup(title="Aviso", content=contenido,
                      size_hint=(0.8, 0.3))
        b = btn("Cerrar", color=AZUL, alto=dp(44))
        b.bind(on_press=popup.dismiss)
        contenido.add_widget(b)
        popup.open()