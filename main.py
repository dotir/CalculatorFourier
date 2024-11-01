import os
import io
import base64
import flet as ft
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
from fractions import Fraction
from calculadora import convertir_expresion, calcular_serie_fourier, piecewise,formatear_serie_fourier

# Crear una carpeta para almacenar gráficos si no existe
if not os.path.exists("fourier_graphs"):
    os.makedirs("fourier_graphs")
    
def graficar_fourier(a, b, fx, an, bn ,n_max):
    # Generar valores de x
    x = np.linspace(a, b, 400)
    # Evaluar la función original
    f = lambda x: np.full_like(x, eval(fx, {"x": x, "piecewise": piecewise, "sin": np.sin, "cos": np.cos, "pi": np.pi}))
    y_original = f(x)

    # Calcular la serie de Fourier
    L = (b - a) / 2
    y_fourier = np.full_like(x, an[0] / 2)
    for n in range(1, n_max + 1):  # Use n_max to limit the number of terms
        y_fourier += an[n - 1] * np.cos(n * np.pi * x / L) + bn[n - 1] * np.sin(n * np.pi * x / L)

    # for n in range(1, len(an) + 1):
    #     y_fourier += an[n - 1] * np.cos(n * np.pi * x / L) + bn[n - 1] * np.sin(n * np.pi * x / L)

    # Graficar
    plt.figure(figsize=(10, 5))
    plt.plot(x, y_original, label='Original', color='blue')
    plt.plot(x, y_fourier, label='Fourier', color='red', linestyle='--')
    plt.legend()
    plt.title('Aproximación de Fourier')
    plt.xlabel('x')
    plt.ylabel('f(x)')
    plt.grid(True)

    # Guardar la gráfica en un buffer de bytes y convertirla a base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    
    return img_base64


def main(page: ft.Page):
    # Configuración inicial de la ventana
    page.title = "Calculadora"
    page.window.width = 600
    page.window.height = 990

    # Mensaje de ayuda para el campo f(x)
    ayuda_fx = ft.Text(
        "Usa piecewise para funciones que tienen diferentes valores o expresiones en distintos intervalos de x. Escribe la función como piecewise(valor1, condición1, valor2, condición2, ..., valor_predeterminado)",
        style=ft.TextStyle(color=ft.colors.GREY),
        size=10
    )

    # Campos de entrada para a, b y f(x)
    input_a = ft.TextField(label="a", width=100)
    input_b = ft.TextField(label="b", width=100)
    input_fx = ft.TextField(label="f(x)", width=200, tooltip="Escribe tu función aquí")

    # Contenedor para el campo f(x) con su mensaje de ayuda
    fx_container = ft.Column([input_fx, ayuda_fx])

    # Campo de texto para mostrar la expresión y el resultado
    display = ft.TextField(
        value="", 
        text_align=ft.TextAlign.LEFT, 
        width=600,
        height=200, 
        multiline=True,
        read_only=True,
        expand=True
    )
    
    display_container = ft.Container(
        content=display,
        expand=True,
        padding=10
    )

    # Deslizador para seleccionar el número de términos de Fourier
    slider_n = ft.Slider(
        min=1,
        max=20,  # Puedes ajustar el máximo según lo que necesites
        value=5,  # Valor por defecto de n
        divisions=19,
        label="{value}",
        on_change=lambda e: page.update(),
        width=300
    )

    # Create initial empty plot and convert to base64
    plt.figure(figsize=(10, 5))
    plt.grid(True)
    plt.title('Gráfico de la Serie de Fourier')
    plt.xlabel('x')
    plt.ylabel('f(x)')
    
    # Convert initial plot to base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    initial_base64 = base64.b64encode(buf.getvalue()).decode()

    # Imagen para mostrar la gráfica
    grafica =  ft.Image(src_base64=initial_base64)

    # Variable para rastrear el campo activo
    campo_activo = input_a

    # Función para manejar la entrada de los botones
    def agregar_texto(e):
        if campo_activo != display:
            campo_activo.value += e.control.data
            page.update()

    # Función para cambiar el campo activo
    def set_campo_activo(campo):
        nonlocal campo_activo
        campo_activo = campo
        # Update focus state
        input_a.focused = (campo == input_a)
        input_b.focused = (campo == input_b)
        input_fx.focused = (campo == input_fx)
        display.focused = (campo == display)
        page.update()

    # Asignar eventos de clic para cambiar el campo activo
    input_a.on_focus = lambda e: set_campo_activo(input_a)
    input_b.on_focus = lambda e: set_campo_activo(input_b)
    input_fx.on_focus = lambda e: set_campo_activo(input_fx)
    display.on_focus = lambda e: set_campo_activo(display)

    def decimal_to_fraction_str(decimal):
        # Convert float to fraction and return a nice string representation
        fraction = Fraction(decimal).limit_denominator(100)
        if fraction.denominator == 1:
            return f"{fraction.numerator}"
        return f"{fraction.numerator}/{fraction.denominator}"

    def calcular(e):
        # Verifica si los campos a, b y f(x) están llenos para calcular Fourier
        if input_a.value and input_b.value and input_fx.value:
            try:
                print(f"Input values - a: {input_a.value}, b: {input_b.value}, f(x): {input_fx.value}")
                
                # Convertir símbolos de pi a valor flotante
                a_value = input_a.value.strip().replace('π', str(np.pi)).replace('pi', str(np.pi))
                b_value = input_b.value.strip().replace('π', str(np.pi)).replace('pi', str(np.pi))
            

                a = float(eval(a_value))
                b = float(eval(b_value))
                fx = convertir_expresion(input_fx.value.strip())

                # Obtener el valor de n desde el deslizador
                n_max = int(slider_n.value)

                resultado = calcular_serie_fourier(a, b, fx, n_max)

                # Extraer los valores de a0, an y bn desde el resultado
                # a0, an, bn = resultado["a0"], resultado["an"], resultado["bn"]
                
                
                print(f"Resultado: {resultado}")

                # Formatear la salida para que sea más amigable para el usuario
                if "Error" not in resultado:
                    an_str = resultado.split(", an: ")[1].split(", bn: ")[0]
                    bn_str = resultado.split(", bn: ")[1]
                    a0_str = resultado.split("a0: ")[1].split(",")[0]
                    
                    # Redondear valores a 4 decimales
                    a0 = float(a0_str)
                    an = [float(x) for x in an_str.strip('[]').split(', ')]
                    bn = [float(x) for x in bn_str.strip('[]').split(', ')]

                    n_max = min(n_max, len(an), len(bn))

                    # Calcular la Serie de Fourier en formato simplificado
                    L = (b - a) / 2
                    resultado_simplificado = formatear_serie_fourier(a0, an, bn, L)

                    # Construir la expresión de la serie de Fourier
                    # series = f"f(x) = {a0:.4f}"
                    # Ajustar n_max para que no sea mayor que el número de términos calculados
                   
                    
                    series = f"f(x) = {a0 / 2:.4f}"
                    # for n in range(1, n_max + 1):
                    #     if an[n - 1] != 0:
                    #         series += f" + {an[n-1]:.4f}cos({n}πx/{L:.4f})"
                    #     if bn[n - 1] != 0:
                    #         series += f" + {bn[n - 1]:.4f}sin({n}πx/{L:.4f})"

                    for n in range(1, n_max + 1):
                        if an[n-1] != 0:
                            if an[n-1] > 0:
                                series += f" + {abs(an[n-1]):.4f}cos({n}πx/{L:.4f})"
                            else:
                                series += f" - {abs(an[n-1]):.4f}cos({n}πx/{L:.4f})"
                        
                        if bn[n-1] != 0:
                            if bn[n-1] > 0:
                                series += f" + {abs(bn[n-1]):.4f}sin({n}πx/{L:.4f})"
                            else:
                                series += f" - {abs(bn[n-1]):.4f}sin({n}πx/{L:.4f})"


                    formatted_result = f"""Serie de Fourier:
{series}

Serie de Fourier simplificada:
{resultado_simplificado}

Coeficientes de la serie de Fourier:
a₀ = {a0:.4f} = {decimal_to_fraction_str(a0)}

Coeficientes aₙ:
""" + "\n".join([f"aₙ = {an[n-1]:.4f} = {decimal_to_fraction_str(an[n-1])}" for n in range(1, n_max+1)]) + """

Coeficientes bₙ:
""" + "\n".join([f"bₙ = {bn[n-1]:.4f} = {decimal_to_fraction_str(bn[n-1])}" for n in range(1, n_max+1)])

                    display.value = formatted_result
                    base64_img = graficar_fourier(a, b, fx, an, bn, n_max)
                    grafica.src_base64 = base64_img
                    page.update()
                else:
                    display.value = resultado
            except ValueError as ve:
                print(f"Conversion error: {ve}")
                display.value = "Error: a y b deben ser números"
            except Exception as ex:
                print(f"Error en el cálculo de Fourier: {ex}")
                display.value = "Error en el cálculo de Fourier"
        page.update()

    def clear_inputs(e):
        # Limpiar los campos de entrada y la gráfica
        input_a.value = ""
        input_b.value = ""
        input_fx.value = ""
        display.value = ""

        #Crear gráfica vacía
        plt.figure(figsize=(10, 5))
        plt.grid(True)
        plt.title('Fourier Series Plot')
        plt.xlabel('x')
        plt.ylabel('f(x)')
        plt.savefig('fourier_plot.png')
        plt.close()
        
        # Actualizar la imagen de la gráfica a la gráfica vacía
        grafica.src = 'fourier_plot.png'
        page.update()

    def borrar(e):
        # Borrar el último carácter del campo activo
        if campo_activo != display:
            campo_activo.value = campo_activo.value[:-1]
            page.update()

    # Botones para cambiar entre diferentes teclados
    btn_numeros = ft.ElevatedButton("123", on_click=lambda e: mostrar_teclado_numerico(e))
    btn_funciones = ft.ElevatedButton("f(x)", on_click=lambda e: mostrar_teclado_funciones(e))
    btn_letras = ft.ElevatedButton("ABC", on_click=lambda e: mostrar_teclado_letras(e))
    btn_simbolos = ft.ElevatedButton("#&¬", on_click=lambda e: mostrar_teclado_simbolos(e))
    btn_fourier = ft.ElevatedButton("Fourier", on_click=lambda e: mostrar_teclado_fourier(e))

    # Definición de los teclados
    botones_letras = [
        ["A", "B", "C", "D", "E"],
        ["F", "G", "H", "I", "J"],
        ["K", "L", "M", "N", "O"],
        ["P", "Q", "R", "S", "←"],
    ]

    botones_simbolos = [
        ["#", "&", "¬", "@", "$"],
        ["%", "^", "*", "~", "|"],
        ["\\", "{", "}", "[", "]"],
        ["(", ")", "_", "?", "←"],
    ]

    botones_numeros = [
        ["7", "8", "9", "×", "÷"],
        ["4", "5", "6", "+", "-"],
        ["1", "2", "3", "=","C"],
        ["0", ".", "←"],
    ]

    botones_funciones = [
        ["sen", "cos", "tg", "e", "C"],
        ["sen⁻¹", "cos⁻¹", "tg⁻¹", "<", ">"],
        ["sec", "cosec", "cotg", "≤", "≥"],
        ["ln", "log₁₀", "log₂", "√", "←"],
    ]

    botones_fourier = [
        ["∫", "∑", "a₀", "aₙ", "bₙ","C"],
        ["∞", "π", "cos", "sen", "n"],
        ["dx", "L", "f(x)", "=", "←"]
    ]

    # Filas de botones para cada teclado
    filas_letras = [
        ft.Row([ft.ElevatedButton(text, data=text, on_click=borrar if text == "←" else agregar_texto)
                for text in fila], alignment=ft.MainAxisAlignment.CENTER)
        for fila in botones_letras
    ]

    filas_simbolos = [
        ft.Row([ft.ElevatedButton(text, data=text, on_click=borrar if text == "←" else agregar_texto)
                for text in fila], alignment=ft.MainAxisAlignment.CENTER)
        for fila in botones_simbolos
    ]

    filas_numeros = [
        ft.Row([ft.ElevatedButton(text, data=text, 
                on_click=calcular if text == "=" else borrar if text == "←" else clear_inputs if text == "C" else agregar_texto)
                for text in fila], alignment=ft.MainAxisAlignment.CENTER)
        for fila in botones_numeros
    ]

    filas_funciones = [
        ft.Row([ft.ElevatedButton(text, data=text, 
                on_click=borrar if text == "←" else clear_inputs if text == "C" else agregar_texto)
                for text in fila], alignment=ft.MainAxisAlignment.CENTER)
        for fila in botones_funciones
    ]

    filas_fourier = [
        ft.Row([ft.ElevatedButton(text, data=text, 
                on_click=calcular if text == "=" else borrar if text == "←" else clear_inputs if text == "C" else agregar_texto)
                for text in fila], alignment=ft.MainAxisAlignment.CENTER)
        for fila in botones_fourier
    ]
    # Funciones para mostrar diferentes teclados
    def mostrar_teclado_letras(e):
        if len(page.controls) > 0:
            page.controls.pop()
        page.add(ft.Column([
            input_a, input_b, input_fx,  # Añadir campos de entrada para a, b y f(x)
            slider_n,
            display_container,
            grafica,
            ft.Row([btn_numeros, btn_funciones, btn_letras, btn_simbolos, btn_fourier], alignment=ft.MainAxisAlignment.CENTER),
            *filas_letras
        ]))
        page.update()

    def mostrar_teclado_simbolos(e):
        if len(page.controls) > 0:
            page.controls.pop()
        page.add(ft.Column([
            input_a, input_b, input_fx,  # Añadir campos de entrada para a, b y f(x)
            slider_n,
            display_container,
            grafica,
            ft.Row([btn_numeros, btn_funciones, btn_letras, btn_simbolos, btn_fourier], alignment=ft.MainAxisAlignment.CENTER),
            *filas_simbolos
        ]))
        page.update()

    def mostrar_teclado_numerico(e):
        if len(page.controls) > 0:
            page.controls.pop()
        page.add(ft.Column([
            input_a, input_b, input_fx,  # Añadir campos de entrada para a, b y f(x)
            slider_n,
            display_container,
            grafica,
            ft.Row([btn_numeros, btn_funciones, btn_letras, btn_simbolos, btn_fourier], alignment=ft.MainAxisAlignment.CENTER),
            *filas_numeros
        ]))
        page.update()

    def mostrar_teclado_funciones(e):
        if len(page.controls) > 0:
            page.controls.pop()
        page.add(ft.Column([
            input_a, input_b, input_fx,  # Añadir campos de entrada para a, b y f(x)
            slider_n,
            display_container,
            grafica,
            ft.Row([btn_numeros, btn_funciones, btn_letras, btn_simbolos, btn_fourier], alignment=ft.MainAxisAlignment.CENTER),
            *filas_funciones
        ]))
        page.update()

    def mostrar_teclado_fourier(e):
        if len(page.controls) > 0:
            page.controls.pop()
        page.add(ft.Column([
            input_a, input_b, input_fx,  # Añadir campos de entrada para a, b y f(x)
            slider_n,
            display_container,
            grafica,
            ft.Row([btn_numeros, btn_funciones, btn_letras, btn_simbolos, btn_fourier], 
                alignment=ft.MainAxisAlignment.CENTER),
            *filas_fourier
        ]))
        page.update()

    def cargar_teclado():
        if len(page.controls) > 0:
            page.controls.pop()
        page.add(ft.Column([
            input_a, input_b, fx_container,
            slider_n,
            display_container,
            grafica,
            ft.Row([btn_numeros, btn_funciones, btn_letras, btn_simbolos, btn_fourier], alignment=ft.MainAxisAlignment.CENTER),
            *filas_numeros
        ]))
        page.update()

    cargar_teclado()

if __name__ == "__main__":
    ft.app(target=main)