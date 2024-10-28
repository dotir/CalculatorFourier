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
    
# Función para evaluar si una función es par, impar o sin simetría
def evaluar_simetria(f, L, num_puntos=100):
    # Generar puntos en el intervalo (sin incluir el punto cero)
    x = np.linspace(1e-5, L, num_puntos)

    f_x = np.vectorize(f)(x)       # Vectorizar para evaluar f(x) en cada punto
    f_neg_x = np.vectorize(f)(-x)  # Vectorizar para evaluar f(-x) en cada punto

    # Verificar si la función es par: f(x) == f(-x)
    es_par = np.allclose(f_x, f_neg_x, atol=1e-6)

    # Verificar si la función es impar: f(x) == -f(-x)
    es_impar = np.allclose(f_x, -f_neg_x, atol=1e-6)

    # Determinar la simetría
    if es_par:
        return "par"
    elif es_impar:
        return "impar"
    else:
        return "ninguna"

# Función para implementar piecewise
def piecewise(*args):
    if len(args) % 2 == 0:
        raise ValueError("La función piecewise requiere un número impar de argumentos.")
    
    values = args[0::2]      # Valores alternos
    conditions = args[1::2]  # Condiciones alternas
    default = args[-1]       # Valor predeterminado
    
    # Crear un resultado inicial lleno del valor predeterminado
    result = np.full_like(conditions[0], default, dtype=np.float64)
    # Evaluar cada condición y aplicar el valor correspondiente
    for condition, value in zip(conditions, values):
        result = np.where(condition, value, result)
    
    return result
    # result = np.full_like(conditions[0], default)  # Crear un array lleno con el valor predeterminado
    # for value, condition in zip(values, conditions):
    #     result = np.where(condition, value, result)
    # return result

# Función para calcular la serie de Fourier
def calcular_serie_fourier(a, b, fx):
    try:
        # Definir la función a evaluar
        f = lambda x: eval(fx, {"x": x, "piecewise": piecewise, "sin": sin, "cos": cos, "pi": pi})
        L = (b - a) / 2

        # Evaluar simetría de la función
        simetria = evaluar_simetria(f, L)
        print(f"Simetría detectada: {simetria}")
        # Inicializar coeficientes
        a0, an, bn = 0, [], []
        
        # Calcular coeficientes según la simetría
        if simetria == "par":
            a0 = calcular_a0(f, L)
            an = [calcular_an(f, L, n) for n in range(1, 5)]
            bn = [0] * 4  # bn = 0 si la función es par
        elif simetria == "impar":
            an = [0] * 4  # an = 0 si la función es impar
            bn = [calcular_bn(f, L, n) if n % 2 != 0 else 0 for n in range(1, 5)]  # Solo bn para n impar
            # bn = [calcular_bn(f, L, n) for n in range(1, 5) if n % 2 != 0]  # Solo bn para n impar
        else:
            a0 = calcular_a0(f, L)
            an = [calcular_an(f, L, n) for n in range(1, 5)]
            bn = [calcular_bn(f, L, n) for n in range(1, 5)]

        return f"a0: {a0}, an: {an}, bn: {bn}"
    except Exception as ex:
        print(f"Error en el cálculo de Fourier: {ex}")
        return "Error en el cálculo de Fourier"
    
# Funciones auxiliares para detectar simetría
def es_par(f, L):
    # Verifica si la función es par
    return all(abs(f(x) - f(-x)) < 1e-6 for x in np.linspace(-L, L, 100))

def es_impar(f, L):
    # Verifica si la función es impar
    return all(abs(f(x) + f(-x)) < 1e-6 for x in np.linspace(-L, L, 100))

# Cálculo de coeficientes
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
