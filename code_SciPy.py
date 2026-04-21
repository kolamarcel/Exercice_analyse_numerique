import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# --- DONNÉES ---
x_pts = [0, 1, 2, 3, 4, 5]
y_pts = [1, 3, 2, 5, 4, 6]
valeur_test = 2.5

# ==========================================
# 1. CONSTRUCTION (SciPy)
# ==========================================
# kind='quadratic' force le degré 2. 
# SciPy stocke les coefficients en mémoire de manière invisible.
spline_scipy = interp1d(x_pts, y_pts, kind='quadratic')

# ==========================================
# 2. ÉVALUATION (SciPy)
# ==========================================
# Évaluation locale (un seul point)
y_test_scipy = spline_scipy(valeur_test)
print(f"SciPy | Valeur à x={valeur_test} : {y_test_scipy:.4f}")

# Évaluation globale (pour le graphe)
x_fine = np.linspace(min(x_pts), max(x_pts), 100)
y_fine_scipy = spline_scipy(x_fine)

# Affichage
plt.plot(x_fine, y_fine_scipy, 'g-', label='Spline SciPy (Numérique)')
plt.scatter(x_pts, y_pts, color='black', zorder=5)
plt.scatter(valeur_test, y_test_scipy, color='red', s=100, marker='*', zorder=10)
plt.title("Spline Quadratique : SciPy")
plt.legend(); plt.grid(True, linestyle=':')
plt.show()