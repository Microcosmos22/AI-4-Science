from sympy import (
    symbols, Function, sin, cos, exp, log,
    sinh, cosh, sqrt, tan,
    besseli, besselk, besselj, bessely,
    gamma
)

t = symbols("t")

# Generic coefficients
a0, a1, a2, a3 = symbols("a0 a1 a2 a3")
A, B, C = symbols("A B C")
omega, phi, k, n = symbols("omega phi k n")


MODEL_LIBRARY = {

    # -------------------------
    # Algebraic models
    # -------------------------

    "constant": {
        "expression": A,
        "parameters": [A]
    },

    "linear": {
        "expression": a0 + a1*t,
        "parameters": [a0, a1]
    },

    "quadratic": {
        "expression": a0 + a1*t + a2*t**2,
        "parameters": [a0, a1, a2]
    },

    "cubic": {
        "expression": a0 + a1*t + a2*t**2 + a3*t**3,
        "parameters": [a0, a1, a2, a3]
    },

    "polynomial_4": {
        "expression": sum(
            symbols(f"a{i}") * t**i
            for i in range(5)
        ),
        "parameters": [
            symbols(f"a{i}")
            for i in range(5)
        ]
    },


    # -------------------------
    # Exponential models
    # -------------------------

    "exponential": {
        "expression": A * exp(k*t),
        "parameters": [A, k]
    },

    "double_exponential": {
        "expression": (
            A*exp(k*t) +
            B*exp(n*t)
        ),
        "parameters": [A, B, k, n]
    },


    # -------------------------
    # Logarithmic models
    # -------------------------

    "logarithmic": {
        "expression": A*log(k*t),
        "parameters": [A, k]
    },


    # -------------------------
    # Oscillatory models
    # -------------------------

    "sinusoidal": {
        "expression": A*sin(omega*t + phi),
        "parameters": [A, omega, phi]
    },

    "cosine": {
        "expression": A*cos(omega*t + phi),
        "parameters": [A, omega, phi]
    },


    # -------------------------
    # Hyperbolic functions
    # -------------------------

    "sinh": {
        "expression": A*sinh(k*t),
        "parameters": [A, k]
    },

    "cosh": {
        "expression": A*cosh(k*t),
        "parameters": [A, k]
    },


    # -------------------------
    # Power laws
    # -------------------------

    "power_law": {
        "expression": A*t**k,
        "parameters": [A, k]
    },


    # -------------------------
    # Special functions
    # -------------------------

    "bessel_first_kind": {
        "expression": A*besselj(n, k*t),
        "parameters": [A, n, k]
    },

    "bessel_second_kind": {
        "expression": A*bessely(n, k*t),
        "parameters": [A, n, k]
    },

    "modified_bessel_first": {
        "expression": A*besseli(n, k*t),
        "parameters": [A, n, k]
    },

    "modified_bessel_second": {
        "expression": A*besselk(n, k*t),
        "parameters": [A, n, k]
    },

}
