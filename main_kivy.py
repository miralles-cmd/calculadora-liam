# main_kivy.py

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.metrics import dp

from base_datos import inicializar_db
from pantallas.pantalla_ticket import PantallaTicket
from pantallas.pantalla_productos import PantallaProductos

Window.size = (400, 700)


class PantallaMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=dp(24), spacing=dp(12))

        layout.add_widget(Label(text="Gestion de Tienda", font_size=22,
                                bold=True, size_hint=(1, 0.15)))
        layout.add_widget(Label(text="Selecciona una opcion", font_size=13,
                                color=(0.6, 0.6, 0.6, 1), size_hint=(1, 0.08)))

        botones = [
            ("Ticket del dia",  "ticket"),
            ("Productos",       "productos"),
            ("Categorias",      "categorias"),
            ("Historial",       "historial"),
        ]

        for texto, destino in botones:
            b = Button(
                text=texto, font_size=16,
                size_hint=(1, None), height=dp(52),
                background_color=(0.23, 0.23, 0.94, 1),
                background_normal=""
            )
            b.bind(on_press=lambda x, d=destino:
                   setattr(self.manager, "current", d))
            layout.add_widget(b)

        self.add_widget(layout)


class GestionTiendaApp(App):
    def build(self):
        inicializar_db()
        sm = ScreenManager()
        sm.add_widget(PantallaMenu(name="menu"))
        sm.add_widget(PantallaTicket(name="ticket"))
        sm.add_widget(PantallaProductos(name="productos"))
        return sm


if __name__ == "__main__":
    GestionTiendaApp().run()