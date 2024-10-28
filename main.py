import os
import io
import base64
import flet as ft
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
from calculadora import evaluar_expresion, calcular_serie_fourier, piecewise

# Create a folder for storing graphs if it doesn't exist
if not os.path.exists("fourier_graphs"):
    os.makedirs("fourier_graphs")
    
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

    # Save to bytes buffer and convert to base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    
    return img_base64


def main(page: ft.Page):
    page.title = "Calculadora"
    page.window.width = 600
    page.window.height = 950

    # Campos de entrada para a, b y f(x)
    input_a = ft.TextField(label="a", width=100)
    input_b = ft.TextField(label="b", width=100)
    input_fx = ft.TextField(label="f(x)", width=200)

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

    # Create initial empty plot and convert to base64
    plt.figure(figsize=(10, 5))
    plt.grid(True)
    plt.title('Fourier Series Plot')
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

    def calcular(e):
        # Verifica si los campos a, b y f(x) están llenos para calcular Fourier
        if input_a.value and input_b.value and input_fx.value:
            try:
                print(f"Input values - a: {input_a.value}, b: {input_b.value}, f(x): {input_fx.value}")
                
                # Convert pi symbols to float value
                a_value = input_a.value.strip().replace('π', str(np.pi)).replace('pi', str(np.pi))
                b_value = input_b.value.strip().replace('π', str(np.pi)).replace('pi', str(np.pi))
            

                a = float(eval(a_value))
                b = float(eval(b_value))
                fx = input_fx.value.strip()

                resultado = calcular_serie_fourier(a, b, fx)

                # Format the display output to be more user-friendly
                if "Error" not in resultado:
                    an_str = resultado.split(", an: ")[1].split(", bn: ")[0]
                    bn_str = resultado.split(", bn: ")[1]
                    a0_str = resultado.split("a0: ")[1].split(",")[0]
                    
                    # Round values to 4 decimal places
                    a0 = float(a0_str)
                    an = [float(x) for x in eval(an_str)]
                    bn = [float(x) for x in eval(bn_str)]
                    
                    formatted_result = f"""Coeficientes de la Serie de Fourier:
a₀ = {a0:.4f}

Coeficientes aₙ:
a₁ = {an[0]:.4f}
a₂ = {an[1]:.4f}
a₃ = {an[2]:.4f}
a₄ = {an[3]:.4f}

Coeficientes bₙ:
b₁ = {bn[0]:.4f}
b₂ = {bn[1]:.4f}
b₃ = {bn[2]:.4f}
b₄ = {bn[3]:.4f}"""

                    display.value = formatted_result
                    base64_img = graficar_fourier(a, b, fx, an, bn)
                    grafica.src_base64 = base64_img
                    page.update()
                else:
                    display.value = resultado
            except ValueError as ve:
                print(f"Conversion error: {ve}")
                display.value = "Error: a y b deben ser números"
        page.update()

    def clear_inputs(e):
        input_a.value = ""
        input_b.value = ""
        input_fx.value = ""
        display.value = ""

        #Create empty plot
        plt.figure(figsize=(10, 5))
        plt.grid(True)
        plt.title('Fourier Series Plot')
        plt.xlabel('x')
        plt.ylabel('f(x)')
        plt.savefig('fourier_plot.png')
        plt.close()
        
        # Update the image source to the empty plot
        grafica.src = 'fourier_plot.png'
        page.update()

    def borrar(e):
        if campo_activo != display:
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