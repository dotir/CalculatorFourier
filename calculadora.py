import numpy as np
import re
from math import pi, e, sin, cos, tan, asin, acos, atan, log, log10, sqrt
from scipy import integrate
from fractions import Fraction
from math import gcd
from functools import reduce


# Función para convertir expresiones en formato sin^n(x), cos^n(x), tan^n(x)
def convertir_expresion(expresion):
    # Expresión regular para detectar sin^2(2x), cos^2(2x), tan^2(2x)
    # La expresión regular fue ajustada para evitar duplicación del número
    expresion = re.sub(r'(\b(sin|cos|tan))\^(\d+)\((\d*)x\)', r'(\1(\4 * x))**\3', expresion)
    print(expresion)
    return expresion

def formatear_serie_fourier(a0, an, bn, L):
    # Extraer el factor común si es necesario
    factor_comun = 8 / np.pi  # Factor esperado basado en el cálculo manual
    serie = f"f(x) = {factor_comun} * ("

    # Agregar términos de seno con el factor común extraído
    for n, b_n in enumerate(bn, start=1):
        if b_n != 0:
            coeficiente = b_n / factor_comun
            if n > 1:
                serie += " + " if coeficiente > 0 else " - "
            serie += f"{abs(coeficiente):.4f}sin({n}πx/{L})"
    
    serie += ")"
    return serie

def formatear_serie_fourier_factorizada(a0, an, bn, L):
    # Convertir los coeficientes a fracciones para precisión
    factor_comun = Fraction(a0).limit_denominator(1000) if a0 != 0 else 0
    an_fracciones = [Fraction(a).limit_denominator(1000) for a in an]
    bn_fracciones = [Fraction(b).limit_denominator(1000) for b in bn]

    # Encontrar el MCD de los términos no nulos
    coeficientes_no_nulos = [abs(factor_comun)] + [abs(a) for a in an_fracciones if a != 0] + [abs(b) for b in bn_fracciones if b != 0]
    mcd_comun = mcd_multiple([coef.numerator for coef in coeficientes_no_nulos]) / mcd_multiple([coef.denominator for coef in coeficientes_no_nulos])

    # Dividir cada término por el MCD para extraer el factor común
    factor_comun_final = factor_comun / mcd_comun
    an_simplificados = [a / mcd_comun for a in an_fracciones]
    bn_simplificados = [b / mcd_comun for b in bn_fracciones]

    # Construir la serie factorizada
    serie = f"f(x) = {factor_comun_final} * ("

    # Añadir términos de coseno y seno simplificados
    for n, (a, b) in enumerate(zip(an_simplificados, bn_simplificados), start=1):
        if a != 0:
            serie += f" + {a}cos({n}πx/{L})"
        if b != 0:
            serie += f" + {b}sin({n}πx/{L})"
    
    serie += ")"
    return serie.replace("+ -", "- ").replace("* ( +", "* (")  # Limpia el formato

# Función para calcular el MCD (Máximo Común Divisor) entre múltiples números
def mcd_multiple(numbers):
    return reduce(gcd, numbers)

    
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

# Función para calcular la serie de Fourier
def calcular_serie_fourier(a, b, fx,n_max):
    try:
        # Definir la función a evaluar
        f = lambda x: eval(fx, {"x": x, "piecewise": piecewise, "sin": sin, "cos": cos, "pi": pi})
        L = (b - a) / 2

        # Evaluar simetría de la función
        simetria = evaluar_simetria(f, L)
        #print(f"Simetría detectada: {simetria}")
        # Inicializar coeficientes
        a0, an, bn = 0, [], []
        
        # Calcular coeficientes según la simetría
        if simetria == "par":
            a0 = calcular_a0(f, L)
            an = [calcular_an(f, L, n) for n in range(1, n_max+1)]
            bn = [0] * 4  # bn = 0 si la función es par
        elif simetria == "impar":
            an = [0] * 4  # an = 0 si la función es impar
            bn = [calcular_bn(f, L, n) if n % 2 != 0 else 0 for n in range(1, n_max+1)]  # Solo bn para n impar
            # bn = [calcular_bn(f, L, n) for n in range(1, 5) if n % 2 != 0]  # Solo bn para n impar
        else:
            a0 = calcular_a0(f, L)
            an = [calcular_an(f, L, n) for n in range(1, n_max+1)]
            bn = [calcular_bn(f, L, n) for n in range(1, n_max+1)]
        
        print(f"a0: {a0}, an: {an}, bn: {bn}")

        return f"a0: {a0}, an: {an}, bn: {bn}"
        # Formatear el resultado en forma factorizada
        # return formatear_serie_fourier_factorizada(a0, an, bn, L)
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
