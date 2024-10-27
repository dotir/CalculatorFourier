import flet as ft
import numpy as np
import matplotlib.pyplot as plt
from calculadora import evaluar_expresion, calcular_serie_fourier, piecewise

def graficar_fourier(a, b, fx, an, bn):
    x = np.linspace(a, b, 400)
    f = lambda x: eval(fx, {"x": x, "piecewise": piecewise, "sin": np.sin, "cos": np.cos, "pi": np.pi})
    y_original = f(x)

    # Calcular la serie de Fourier
    L = (b - a) / 2
    y_fourier = np.full_like(x, an[0] / 2)
    for n in range(1, len(an) + 1):
        y_fourier += an[n - 1] * np.cos(n * np.pi * x / L) + bn[n - 1] * np.sin(n * np.pi * x / L)

    # Graficar
    plt.figure(figsize=(10, 5))
    plt.plot(x, y_original, label='Original', color='blue')
    plt.plot(x, y_fourier, label='Fourier', color='red', linestyle='--')
    plt.legend()
    plt.title('Aproximación de Fourier')
    plt.xlabel('x')
    plt.ylabel('f(x)')
    plt.grid(True)
    plt.savefig('fourier_plot.png')
    plt.close()

def main(page: ft.Page):
    page.title = "Calculadora Científica"
    page.window.width = 600
    page.window.height = 900

    # Campos de entrada para a, b y f(x)
    input_a = ft.TextField(label="a", width=100)
    input_b = ft.TextField(label="b", width=100)
    input_fx = ft.TextField(label="f(x)", width=200)

    # Campo de texto para mostrar la expresión y el resultado
    display = ft.TextField(
        value="", 
        text_align=ft.TextAlign.RIGHT, 
        width=600,
        height=50, 
        read_only=True,
        expand=True
    )
    
    display_container = ft.Container(
        content=display,
        expand=True,
        padding=10
    )

    # Imagen para mostrar la gráfica
    grafica = ft.Image(src='fourier_plot.png', width=600, height=300)

    # Variable para rastrear el campo activo
    campo_activo = display

    # Función para manejar la entrada de los botones
    def agregar_texto(e):
        campo_activo.value += e.control.data
        page.update()

    # Función para cambiar el campo activo
    def set_campo_activo(campo):
        nonlocal campo_activo
        campo_activo = campo

    # Asignar eventos de clic para cambiar el campo activo
    input_a.on_click = lambda e: set_campo_activo(input_a)
    input_b.on_click = lambda e: set_campo_activo(input_b)
    input_fx.on_click = lambda e: set_campo_activo(input_fx)
    display.on_click = lambda e: set_campo_activo(display)

    def calcular(e):
        # Verifica si los campos a, b y f(x) están llenos para calcular Fourier
        if input_a.value and input_b.value and input_fx.value:
            try:
                print(f"Input values - a: {input_a.value}, b: {input_b.value}, f(x): {input_fx.value}")
                a = float(input_a.value.strip())
                b = float(input_b.value.strip())
                fx = input_fx.value.strip()
                resultado = calcular_serie_fourier(a, b, fx)
                print(f"Result: {resultado}")
                display.value = resultado
                if "Error" not in resultado:
                    # Extraer y evaluar los coeficientes an y bn
                    an_str = resultado.split(", an: ")[1].split(", bn: ")[0]
                    bn_str = resultado.split(", bn: ")[1]
                    an = eval(an_str)
                    bn = eval(bn_str)
                    graficar_fourier(a, b, fx, an, bn)
                    grafica.src = 'fourier_plot.png'
            except ValueError as ve:
                print(f"Conversion error: {ve}")
                display.value = "Error: a y b deben ser números"
        page.update()

    def borrar(e):
        campo_activo.value = campo_activo.value[:-1]
        page.update()

    btn_numeros = ft.ElevatedButton("123", on_click=lambda e: mostrar_teclado_numerico(e))
    btn_funciones = ft.ElevatedButton("f(x)", on_click=lambda e: mostrar_teclado_funciones(e))
    btn_letras = ft.ElevatedButton("ABC", on_click=lambda e: mostrar_teclado_letras(e))
    btn_simbolos = ft.ElevatedButton("#&¬", on_click=lambda e: mostrar_teclado_simbolos(e))
    btn_fourier = ft.ElevatedButton("Fourier", on_click=lambda e: mostrar_teclado_fourier(e))

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
        ["1", "2", "3", "="],
        ["0", ".", "←"],
    ]

    botones_funciones = [
        ["sen", "cos", "tg", "e", "10^x"],
        ["sen⁻¹", "cos⁻¹", "tg⁻¹", "<", ">"],
        ["sec", "cosec", "cotg", "≤", "≥"],
        ["ln", "log₁₀", "log₂", "√", "←"],
    ]

    botones_fourier = [
        ["∫", "∑", "a₀", "aₙ", "bₙ"],
        ["∞", "π", "cos", "sen", "n"],
        ["dx", "L", "f(x)", "=", "←"]
    ]

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
        ft.Row([ft.ElevatedButton(text, data=text, on_click=calcular if text == "=" else borrar if text == "←" else agregar_texto)
                for text in fila], alignment=ft.MainAxisAlignment.CENTER)
        for fila in botones_numeros
    ]

    filas_funciones = [
        ft.Row([ft.ElevatedButton(text, data=text, on_click=borrar if text == "←" else agregar_texto)
                for text in fila], alignment=ft.MainAxisAlignment.CENTER)
        for fila in botones_funciones
    ]

    filas_fourier = [
        ft.Row([ft.ElevatedButton(text, data=text, on_click=borrar if text == "←" else agregar_texto)
                for text in fila], alignment=ft.MainAxisAlignment.CENTER)
        for fila in botones_fourier
    ]

    def mostrar_teclado_letras(e):
        if len(page.controls) > 0:
            page.controls.pop()
        page.add(ft.Column([
            input_a, input_b, input_fx,  # Añadir campos de entrada para a, b y f(x)
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
            input_a, input_b, input_fx,  # Añadir campos de entrada para a, b y f(x)
            display_container,
            grafica,
            ft.Row([btn_numeros, btn_funciones, btn_letras, btn_simbolos, btn_fourier], alignment=ft.MainAxisAlignment.CENTER),
            *filas_numeros
        ]))
        page.update()

    cargar_teclado()

if __name__ == "__main__":
    ft.app(target=main)