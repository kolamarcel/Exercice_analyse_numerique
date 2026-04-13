ENTRÉE : 5 points connus → x = [0,1,2,3,4], y = [1,3,2,5,4]
OBJECTIF : Trouver f(2.5) = ?

STRATÉGIE :
  - Découper l'axe x en intervalles : [0,1], [1,2], [2,3], [3,4]
  - Sur chaque intervalle, ajuster un polynôme de degré 2
  - Ces polynômes se raccordent proprement aux bords
  → On obtient une fonction f(x) définie par morceaux

-----------------------------SCIPY--------------------------------------------------------------------
ÉTAPE 1 — CONSTRUCTION
  ┌─────────────────────────────────────────────────┐
  │  interp1d(x_pts, y_pts, kind='quadratic')       │
  │                                                 │
  │  → Pour chaque intervalle [i, i+1] :            │
  │      Résoudre un système d'équations            │
  │      pour trouver a, b, c tels que :            │
  │      f(x) = ax² + bx + c                       │
  │                                                 │
  │  → Stocker les coefficients EN MÉMOIRE          │
  │    (l'utilisateur ne les voit pas)              │
  └─────────────────────────────────────────────────┘

ÉTAPE 2 — ÉVALUATION LOCALE (x = 2.5)
  ┌─────────────────────────────────────────────────┐
  │  spline_scipy(2.5)                              │
  │                                                 │
  │  → Chercher dans quel intervalle est 2.5        │
  │    2.5 ∈ [2, 3]  ✓                             │
  │  → Récupérer le polynôme de cet intervalle      │
  │  → Calculer f(2.5) = a(2.5)² + b(2.5) + c      │
  │  → Retourner un nombre décimal                  │
  └─────────────────────────────────────────────────┘

ÉTAPE 3 — ÉVALUATION GLOBALE (pour le graphe)
  ┌─────────────────────────────────────────────────┐
  │  np.linspace(0, 4, 100)  →  100 valeurs de x   │
  │                                                 │
  │  POUR CHAQUE x dans ces 100 valeurs :           │
  │    → Répéter l'étape 2                          │
  │  → Obtenir 100 valeurs y                        │
  │  → Tracer la courbe                             │
  └─────────────────────────────────────────────────┘

-------------------------------------------------------------------------------------------------




-----------------------------SYMPY--------------------------------------------------------------------

ÉTAPE 1 — CONSTRUCTION SYMBOLIQUE
  ┌─────────────────────────────────────────────────┐
  │  interpolating_spline(2, x, x_pts, y_pts)       │
  │                                                 │
  │  → Même calcul qu'avec SciPy MAIS               │
  │    les coefficients sont gardés sous forme      │
  │    de fractions et expressions exactes          │
  │                                                 │
  │  → Le résultat est une fonction Piecewise :     │
  │                                                 │
  │    f(x) = 3x² - x + 1      si x ∈ [0, 1]      │
  │           ...               si x ∈ [1, 2]      │
  │           ...               si x ∈ [2, 3]      │
  │           ...               si x ∈ [3, 4]      │
  │                                                 │
  │  → L'utilisateur PEUT LIRE ces formules         │
  └─────────────────────────────────────────────────┘

ÉTAPE 2 — AFFICHAGE (pprint)
  ┌─────────────────────────────────────────────────┐
  │  → Parcourir chaque morceau de la fonction      │
  │  → Afficher joliment dans la console            │
  └─────────────────────────────────────────────────┘

ÉTAPE 3 — ÉVALUATION LOCALE (x = 2.5)
  ┌─────────────────────────────────────────────────┐
  │  .subs(x, 2.5)  →  Remplacer x par 2.5         │
  │                    dans la formule symbolique   │
  │  .evalf()       →  Calculer le résultat         │
  │                    et convertir en décimal      │
  └─────────────────────────────────────────────────┘

ÉTAPE 4 — ÉVALUATION GLOBALE (pour le graphe)
  ┌─────────────────────────────────────────────────┐
  │  lambdify(x, spline, 'numpy')                   │
  │                                                 │
  │  PROBLÈME : SymPy est trop lent pour            │
  │             évaluer 100 fois l'expression       │
  │                                                 │
  │  SOLUTION :                                     │
  │    → Convertir l'expression symbolique          │
  │      en une vraie fonction Python rapide        │
  │    → Appliquer cette fonction sur les 100 x     │
  │    → Tracer la courbe                           │
  └─────────────────────────────────────────────────┘

-------------------------------------------------------------------------------------------------


-------------------------------RECAPITULATIF--------------------------------------------------------------------


          SciPy                        SymPy
           │                            │
    Reçoit les points            Reçoit les points
           │                            │
    Calcule les coeff.           Calcule les coeff.
           │                            │
      [cache tout]              [montre les formules]
           │                            │
    Évalue f(2.5)               Substitue x ← 2.5
    directement                 puis .evalf()
           │                            │
      Trace le graphe             lambdify → trace
           │                            │
        RAPIDE                      LISIBLE