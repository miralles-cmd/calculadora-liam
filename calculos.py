# calculos.py - Lógica de cálculo de precios

def calcular_precio(peso_gramos, precio_por_gramo):
    """
    Calcula el precio final de un producto.
    peso_gramos      → cuánto pesa el producto
    precio_por_gramo → cuánto cuesta cada gramo
    """
    resultado = peso_gramos * precio_por_gramo
    return round(resultado, 2)  # Redondeamos a 2 decimales


def pedir_peso():
    """
    Pide al usuario que ingrese un peso en gramos.
    Acepta coma o punto como decimal.
    Máximo 5 dígitos, máximo 2 decimales.
    """
    while True:
        entrada = input("Ingresa el peso en gramos (ej: 0,25 o 125): ")

        # Reemplazamos coma por punto para que Python lo entienda
        entrada = entrada.replace(",", ".")

        try:
            peso = float(entrada)

            # Validar que no sea negativo ni cero
            if peso <= 0:
                print("⚠️  El peso debe ser mayor que cero.")
                continue

            # Validar máximo 5 dígitos en total (sin contar el punto)
            solo_digitos = entrada.replace(".", "")
            if len(solo_digitos) > 5:
                print("⚠️  Máximo 5 dígitos en total.")
                continue

            # Validar máximo 2 decimales
            if "." in entrada:
                decimales = entrada.split(".")[1]
                if len(decimales) > 2:
                    print("⚠️  Máximo 2 decimales.")
                    continue

            return peso  # Todo correcto, devolvemos el peso

        except ValueError:
            print("⚠️  Eso no es un número válido. Intenta de nuevo.")