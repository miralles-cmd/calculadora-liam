# main.py - Punto de entrada

from base_datos import inicializar_db
from interfaz import AppTienda

if __name__ == "__main__":
    inicializar_db()
    app = AppTienda()
    app.mainloop()