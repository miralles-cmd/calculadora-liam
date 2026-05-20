# pantallas/pantalla_categorias.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.metrics import dp

from base_datos import listar_categorias, editar_categoria

AZUL   = (0.23, 0.23, 0.94, 1)
VERDE  = (0.1,  0.6,  0.1,  1)
BLANCO = (1,    1,    1,    1)
GRIS   = (0.6,  0.6,  0.6,  1)


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


class PantallaCategorias(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._construir()

    def _construir(self):
        raiz = BoxLayout(orientation="vertical",
                         padding=dp(12), spacing=dp(12))

        raiz.add_widget(lbl("Categorias", size=20, bold=True))
        raiz.add_widget(lbl("Edita las 3 categorias disponibles",
                             size=12, color=GRIS))

        self.categorias  = listar_categorias()
        self.inputs      = []

        for cat in self.categorias:
            fila = BoxLayout(size_hint=(1, None), height=dp(48),
                              spacing=dp(8))
            fila.add_widget(lbl(f"Cat {cat[0]}:", size=13,
                                 color=GRIS, halign="left"))
            inp = TextInput(
                text=cat[1], font_size=sp(18),
                multiline=False,
                size_hint=(1, None), height=dp(44)
            )
            self.inputs.append((cat[0], inp))
            fila.add_widget(inp)
            raiz.add_widget(fila)

        b_guardar = btn("Guardar cambios", color=VERDE)
        b_guardar.bind(on_press=lambda x: self._guardar())
        raiz.add_widget(b_guardar)

        b_volver = btn("Volver al menu", color=(0.3, 0.3, 0.3, 1),
                        alto=dp(42))
        b_volver.bind(on_press=lambda x: setattr(
            self.manager, "current", "menu"))
        raiz.add_widget(b_volver)

        self.add_widget(raiz)

    def _guardar(self):
        for cat_id, inp in self.inputs:
            nuevo = inp.text.strip()
            if nuevo:
                editar_categoria(cat_id, nuevo)

        contenido = BoxLayout(orientation="vertical",
                               padding=dp(12), spacing=dp(8))
        contenido.add_widget(lbl("Categorias actualizadas.", size=13))
        popup = Popup(title="Guardado", content=contenido,
                      size_hint=(0.75, 0.28))
        b = btn("OK", color=AZUL, alto=dp(44))
        b.bind(on_press=popup.dismiss)
        contenido.add_widget(b)
        popup.open()