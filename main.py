# main.py - Punto de entrada universal
import os
import sys

# Detectar si estamos en Android
if 'ANDROID_ARGUMENT' in os.environ:
    # Estamos en Android - usar Kivy
    from main_kivy import GestionTiendaApp
    from base_datos import inicializar_db
    inicializar_db()
    GestionTiendaApp().run()
else:
    # Estamos en PC - usar Tkinter
    from base_datos import inicializar_db
    from interfaz import AppTienda
    inicializar_db()
    app = AppTienda()
    app.mainloop()