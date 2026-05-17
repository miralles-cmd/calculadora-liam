# main.py - Punto de entrada con captura de errores
import os
import sys

def escribir_log(mensaje):
    """Escribe en un archivo de log accesible."""
    try:
        from android.storage import app_storage_path
        ruta = os.path.join(app_storage_path(), "error_log.txt")
    except:
        ruta = "/sdcard/gestiontienda_error.txt"
    try:
        with open(ruta, "a") as f:
            f.write(mensaje + "\n")
    except:
        pass

try:
    escribir_log("=== INICIO APP ===")
    escribir_log(f"Python: {sys.version}")
    escribir_log(f"Android: {'ANDROID_ARGUMENT' in os.environ}")

    escribir_log("Importando kivy...")
    from kivy.app import App
    escribir_log("Kivy OK")

    escribir_log("Importando base_datos...")
    from base_datos import inicializar_db
    escribir_log("base_datos OK")

    escribir_log("Importando pantallas...")
    from main_kivy import GestionTiendaApp
    escribir_log("pantallas OK")

    escribir_log("Iniciando DB...")
    inicializar_db()
    escribir_log("DB OK")

    escribir_log("Arrancando app...")
    GestionTiendaApp().run()

except Exception as e:
    import traceback
    error = traceback.format_exc()
    escribir_log(f"ERROR: {error}")

    # Mostrar error en pantalla
    try:
        from kivy.app import App
        from kivy.uix.label import Label
        from kivy.uix.scrollview import ScrollView

        class ErrorApp(App):
            def build(self):
                scroll = ScrollView()
                lbl = Label(
                    text=f"ERROR:\n{error}",
                    font_size=11,
                    size_hint_y=None,
                    text_size=(800, None)
                )
                lbl.bind(texture_size=lbl.setter('size'))
                scroll.add_widget(lbl)
                return scroll

        ErrorApp().run()
    except:
        pass