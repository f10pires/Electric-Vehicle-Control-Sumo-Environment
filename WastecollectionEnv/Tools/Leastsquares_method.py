import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json

# =========================
# Configuration
# =========================

"""Load config at 'data/dumpsters.json'"""

with open('data/dumpsters.json', "r", encoding="utf-8") as f:
    dumpsters =  json.load(f)

# Approximation SpaceBasis

# base [1,x,x**2,x**3, sin(x),cos(x)]

#Residual ||fi - yi||^2


# fi, matrix mxn, (fi)ij = fij(xi)
#A = fi**T * fi, matrix nxn, aij = fii**TTfij
#Ac = b, b = fi**T * yi, vector nx1, bi = fi**TTyi

D1 = dumpsters["d1"]

time = []

for t in D1["fill_days"]["2025-01-01"]:
    time.append(int(t))

y = []

for t in D1["fill_days"]["2025-01-01"] :
    y.append(D1["fill_days"]["2025-01-01"][t]['fill_waste(Kg)'])


def create_base(time, number_of_harmonics):
    φ = []
    for x in time:

        row = [1]

        for k in range(1, number_of_harmonics + 1):
            row.append(np.sin(2*np.pi*k*x/24))
            row.append(np.cos(2*np.pi*k*x/24))

        φ.append(row)

    φ = np.array(φ)

    return φ


def least_squares_method(φ, y):

    """
    φ: matrix mxn, (φ)ij = φj(xi)
    y: vector mx1, yi = yi
    """

    A = np.transpose(φ) @ φ
    b = np.transpose(φ) @ y
    c = np.linalg.solve(A, b)

    return c

def aprox_function(φ, c):

    """
    φ: matrix mxn, (φ)ij = φj(xi)
    c: vector nx1, ci = ci
    """

    return φ @ c


# ============================================================
# Residual
# ============================================================

def func_residual(y, function):
    """
    y: vector mx1, yi = yi
    f: vector mx1, fi = fi
    """

    res = 0

    for i in range(len(y)):
        res += (y[i] - function[i])**2

    return res


number_of_harmonics = 1


def func_rmse(y, residual):
    """
    y: vector mx1, yi = yi
    function: vector mx1, fi = fi
    """

    res = residual
    rmse = np.sqrt(res / len(y))

    return rmse

while True:
    φ = create_base(time, number_of_harmonics)
    C = least_squares_method(φ, y)
    f = aprox_function(φ, C)
    residual = func_residual(y, f)
    rmse = func_rmse(y,residual)

    if rmse < 10:
        print("Residual is low enough, for number of harmonics: ", number_of_harmonics)
        print(" It is possible to represent the data with error less than 10 kg.", " RMSE: ", rmse)
        break

    else:
        print("Residual is too high, for number of harmonics: ", number_of_harmonics)
        print(" It is not possible to represent the data with error less than 10 kg.", " RMSE: ", rmse)
        number_of_harmonics += 1
    
# ============================================================
# Print results
# ============================================================

print("Base: ", φ)
print("Coefficients: ", C)
print("Time: ", time)
print("Waste: ", y)
print("Function: ", f)
print("Number of Harmonics: ", number_of_harmonics)
print("Residual: ", residual)
print("RMSE: ", rmse)
# ============================================================
# Create the points for the plot
# ============================================================

f_time = f


# ============================================================
# Plot
# ============================================================

plt.figure(figsize=(12, 6))

# Real data
plt.scatter(
    time,
    y,
    color='red',
    s=50,
    label='Data'
)

# Approximation function
plt.plot(
    time,
    f_time,
    label='f(x)'
)

plt.xlabel('Time (hours)')
plt.ylabel('Waste generation')

plt.xlim(0, max(time))
plt.xticks(np.arange(0, max(time) + 1))

plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()

