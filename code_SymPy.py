import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

# --- DONNÉES ---
x_pts = [0, 1, 2, 3, 4]
y_pts = [1, 3, 2, 5, 4]
valeur_test = 2.5

# ==========================================
# 1. CONSTRUCTION (SymPy)
# ==========================================
x_sym = sp.Symbol('x')

# Le '2' indique le degré du polynôme (2 = Quadratique)
spline_sympy = sp.interpolating_spline(2, x_sym, x_pts, y_pts)

print("Équation mathématique de la Spline par morceaux :")
sp.pprint(spline_sympy) # Affiche joliment les conditions (if/else) dans la console

# ==========================================
# 2. ÉVALUATION (SymPy)
# ==========================================
# Évaluation locale (Substitution puis calcul décimal)
y_test_sympy = spline_sympy.subs(x_sym, valeur_test).evalf()
print(f"\nSymPy | Valeur à x={valeur_test} : {y_test_sympy:.4f}")

# Évaluation globale (Transformation en fonction rapide pour le graphe)
f_rapide = sp.lambdify(x_sym, spline_sympy, 'numpy')

x_fine = np.linspace(min(x_pts), max(x_pts), 100)
y_fine_sympy = f_rapide(x_fine)

# Affichage
plt.plot(x_fine, y_fine_sympy, 'b-', label='Spline SymPy (Symbolique)')
plt.scatter(x_pts, y_pts, color='black', zorder=5)
plt.scatter(valeur_test, float(y_test_sympy), color='red', s=100, marker='*', zorder=10)
plt.title("Spline Quadratique : SymPy")
plt.legend(); plt.grid(True, linestyle=':')
plt.show()