import numpy as np
from math import pi, e, sin, cos, tan, asin, acos, atan, log, log10, sqrt
from scipy import integrate

# Función para evaluar la expresión ingresada por el usuario
def evaluar_expresion(expresion):
    try:
        if "∫" in expresion or "∑" in expresion:
            return "Error: Fourier no implementado en esta función"
        expresion = expresion.replace("π", str(pi)).replace("e", str(e))
        expresion = expresion.replace("sen", "sin").replace("cos", "cos").replace("tg", "tan")
        expresion = expresion.replace("sen⁻¹", "asin").replace("cos⁻¹", "acos").replace("tg⁻¹", "atan")
        expresion = expresion.replace("log₁₀", "log10").replace("√", "sqrt").replace("ln", "log")
        resultado = eval(expresion)
        return str(resultado)
    except Exception as ex:
        return "Error"

# Función para implementar piecewise
def piecewise(*args):
    if len(args) % 2 == 0:
        raise ValueError("La función piecewise requiere un número impar de argumentos.")
    for i in range(0, len(args) - 1, 2):
        condition = np.where(args[i + 1], True, False)
        if np.any(condition):
            return np.where(condition, args[i], args[-1])
    return args[-1]  # valor predeterminado si ninguna condición es verdadera

# Función para calcular la serie de Fourier
def calcular_serie_fourier(a, b, fx):
    try:
        # Convertir la expresión de f(x) en una función
        f = lambda x: eval(fx, {"x": x, "piecewise": piecewise, "sin": sin, "cos": cos, "pi": pi})
        L = (b - a) / 2  # Longitud del periodo
        print(f"L: {L}")
        a0 = calcular_a0(f, L)
        an = [calcular_an(f, L, n) for n in range(1, 5)]
        bn = [calcular_bn(f, L, n) for n in range(1, 5)]
        return f"a0: {a0}, an: {an}, bn: {bn}"
    except Exception as ex:
        print(f"Error en el cálculo de Fourier: {ex}")
        return "Error en el cálculo de Fourier"

def calcular_a0(f, L):
    return 1/(2*L) * integrate.quad(f, -L, L)[0]

def calcular_an(f, L, n):
    def integrando(x):
        return f(x) * np.cos(n*np.pi*x/L)
    return 1/L * integrate.quad(integrando, -L, L)[0]

def calcular_bn(f, L, n):
    def integrando(x):
        return f(x) * np.sin(n*np.pi*x/L)
    return 1/L * integrate.quad(integrando, -L, L)[0]
