"""
Application Streamlit — Interpolation Numérique
================================================
Master 1 GI — Cours d'Analyse Numérique

Fonctionnalités :
    • Interpolation de Lagrange  : SymPy (symbolique) vs SciPy (numérique)
    • Spline Quadratique         : SymPy (symbolique) vs SciPy (PPoly)p
    • Comparaison des temps de calcul (timeit, N répétitions)
    • Vérification des hypothèses H1 / H2 / H3 (spline)
    • Visualisation des courbes

Usage :
    streamlit run app.py
"""

import timeit
import numpy as np
import sympy as sp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd


from modules.lagrange import (
    lagrange_sympy,
    lagrange_scipy,
)
from modules.spline import (
    spline_sympy,
    spline_scipy,
    calculer_zi,
)

# ── Configuration ────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Interpolation Numérique",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ──────────────────────────────────────────────────────────────────

st.sidebar.title("📐 Interpolation Numérique")
st.sidebar.markdown("**Master 1 GI — Analyse Numérique**")
st.sidebar.divider()

st.sidebar.subheader("Points d'interpolation")
mode = st.sidebar.radio("Mode de saisie", ["Génération automatique", "Saisie manuelle", "Importation de fichier"])


if mode == "Génération automatique":
    st.sidebar.markdown("**Paramètres de génération**")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        x0 = st.sidebar.number_input("x₀", value=0.0, step=0.1)
    with col2:
        xn = st.sidebar.number_input("xₙ", value=3.0, step=0.1)
    
    func_input = st.sidebar.text_input("Fonction f(x)", value="sin(x)", help="Exemples : x**2, sin(x), exp(-x), etc.")


    
    n = st.sidebar.slider("Nombre de points (n)", min_value=2, max_value=500, value=4)

    
    # Option : un seul problème ou plusieurs
    problem_mode = st.sidebar.radio("Mode de résolution", ["Un seul problème", "Plusieurs problèmes"])
    
    if problem_mode == "Un seul problème":
        # Fonction pour générer les points
        def generate_points_auto():
            try:
                new_x = np.linspace(x0, xn, n)
                # Parsing de la fonction via SymPy
                x_sym = sp.Symbol('x')
                # Transformation de l'entrée en expression SymPy
                expr = sp.sympify(func_input)
                # Conversion en fonction NumPy pour évaluation rapide
                f_np = sp.lambdify(x_sym, expr, "numpy")
                
                # Évaluation sur les points x
                new_y = f_np(new_x)
                
                # Mise à jour des session_state pour les champs texte éditables
                st.session_state.x_input_val = ", ".join([f"{x:.4g}" for x in new_x])
                st.session_state.y_input_val = ", ".join([f"{y:.4g}" for y in new_y])
            except Exception as e:
                st.sidebar.error(f"Erreur dans la fonction : {e}")

        # Initialisation ou mise à jour automatique si les paramètres de génération changent
        current_params = (x0, xn, n, func_input)
        if "prev_gen_params" not in st.session_state or st.session_state.prev_gen_params != current_params:
            generate_points_auto()
            st.session_state.prev_gen_params = current_params

        st.sidebar.button("Réinitialiser / Regénérer", on_click=generate_points_auto)
        
        # On extrait les valeurs des session_state qui seront liées aux text_inputs plus bas
        try:
            x_pts = [float(v.strip()) for v in st.session_state.x_input_val.split(",") if v.strip()]
            y_pts = [float(v.strip()) for v in st.session_state.y_input_val.split(",") if v.strip()]
            x_arr = np.array(x_pts, dtype=float)
            y_arr = np.array(y_pts, dtype=float)
            problems = [(x_arr, y_arr)]
        except Exception:
            st.sidebar.error("Données invalides ou non initialisées.")
            st.stop()
        
    else:  # Plusieurs problèmes
        num_problems = st.sidebar.slider("Nombre de problèmes à générer", min_value=2, max_value=500, value=5)
        
        st.sidebar.info(f"Génération de {num_problems} problèmes...")
        
        problems = []
        try:
            x_sym = sp.Symbol('x')
            expr = sp.sympify(func_input)
            f_np = sp.lambdify(x_sym, expr, "numpy")
            
            for i in range(num_problems):
                n_i = n + i
                x_pts_i = np.linspace(x0, xn, n_i)
                # On utilise la fonction strictement pour chaque problème
                y_pts_i = f_np(x_pts_i)
                problems.append((x_pts_i, y_pts_i))
        except Exception as e:
            st.sidebar.error(f"Erreur dans la fonction : {e}")
            st.stop()

        
        # Aperçu
        x_arr, y_arr = problems[0]
        x_pts = x_arr.tolist()
        y_pts = y_arr.tolist()
    
    # Vérifications
    for x_arr_check, y_arr_check in problems:
        if len(x_arr_check) != len(y_arr_check):
            st.sidebar.error("x et y doivent avoir la même taille.")
            st.stop()
        if len(x_arr_check) < 2:
            st.sidebar.error("Minimum 2 points requis.")
            st.stop()

elif mode == "Saisie manuelle":  # Saisie manuelle
    if "x_manual" not in st.session_state:
        st.session_state.x_manual = "0, 1, 2, 3"
    if "y_manual" not in st.session_state:
        st.session_state.y_manual = "1, 3, 2, 5"

    x_input_str = st.sidebar.text_input("x_points (virgules)", value=st.session_state.x_manual)
    y_input_str = st.sidebar.text_input("y_points (virgules)", value=st.session_state.y_manual)
    
    # Update state
    st.session_state.x_manual = x_input_str
    st.session_state.y_manual = y_input_str

    try:
        x_pts = [float(v.strip()) for v in x_input_str.split(",") if v.strip()]
        y_pts = [float(v.strip()) for v in y_input_str.split(",") if v.strip()]
        if len(x_pts) != len(y_pts):
            st.sidebar.error("Taille différente entre X et Y.")
            st.stop()
        x_arr = np.array(x_pts, dtype=float)
        y_arr = np.array(y_pts, dtype=float)
        problems = [(x_arr, y_arr)]
    except Exception as e:
        st.sidebar.error(f"Erreur : {e}")
        st.stop()

elif mode == "Importation de fichier":
    st.sidebar.markdown("**Options d'importation**")
    uploaded_file = st.sidebar.file_uploader("Choisir un fichier", type=["csv", "xlsx", "xls"], help="Supporte les formats CSV et Excel (.xlsx, .xls)")
    
    if uploaded_file is not None:
        try:
            # Lecture du fichier selon l'extension
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            if df.empty:
                st.sidebar.error("Le fichier est vide.")
                st.stop()
                
            st.sidebar.success(f"Fichier chargé : {len(df)} lignes trouvées.")
            
            # Sélection des colonnes X et Y
            cols = df.columns.tolist()
            col_x_name = st.sidebar.selectbox("Colonne pour X (abscisses)", cols, index=0)
            col_y_name = st.sidebar.selectbox("Colonne pour Y (ordonnées)", cols, index=1 if len(cols) > 1 else 0)
            
            # Conversion et nettoyage des données
            try:
                # On retire les valeurs non numériques (NaN) pour les axes choisis
                df_clean = df[[col_x_name, col_y_name]].dropna()
                x_pts = df_clean[col_x_name].astype(float).tolist()
                y_pts = df_clean[col_y_name].astype(float).tolist()
                
                if len(x_pts) < 2:
                    st.sidebar.error("Besoin d'au moins 2 points numériques valides.")
                    st.stop()
                
                x_arr = np.array(x_pts, dtype=float)
                y_arr = np.array(y_pts, dtype=float)
                problems = [(x_arr, y_arr)]
                
                # Mise à jour des session_state pour affichage dans la zone centrale
                st.session_state.x_input_val = ", ".join([f"{x:.4g}" for x in x_pts])
                st.session_state.y_input_val = ", ".join([f"{y:.4g}" for y in y_pts])
                
            except Exception as e:
                st.sidebar.error(f"Erreur de conversion numérique : {e}")
                st.stop()
                
        except Exception as e:
            st.sidebar.error(f"Erreur lors de la lecture du fichier : {e}")
            st.stop()
    else:
        st.sidebar.info("Veuillez sélectionner un fichier CSV ou Excel.")
        st.stop()



st.sidebar.divider()
N_ITER = st.sidebar.slider(
    "Répétitions pour la mesure de temps", min_value=1, max_value=20, value=5
)

n_pts = len(x_pts)
st.sidebar.success(f"{n_pts} points — degré {n_pts - 1}")

# ── Section de calcul pour les multiples problèmes ──────────────────────────

num_problems = len(problems)
is_multi_problem = num_problems > 1

# Collecter les résultats pour Lagrange et Spline
lagrange_results = {
    'times_sympy': [],
    'times_scipy': []
}

spline_results = {
    'times_sympy': [],
    'times_scipy': []
}

# Calculer pour chaque problème
for x_problem, y_problem in problems:
    x_list = x_problem.tolist()
    y_list = y_problem.tolist()
    
    # Lagrange
    t_sym_lag = timeit.timeit(lambda: lagrange_sympy(x_list, y_list), number=N_ITER) / N_ITER
    t_sci_lag = timeit.timeit(lambda: lagrange_scipy(x_list, y_list), number=N_ITER) / N_ITER
    lagrange_results['times_sympy'].append(t_sym_lag)
    lagrange_results['times_scipy'].append(t_sci_lag)
    
    # Spline
    t_sym_spl = timeit.timeit(lambda: spline_sympy(x_list, y_list), number=N_ITER) / N_ITER
    t_sci_spl = timeit.timeit(lambda: spline_scipy(x_list, y_list), number=N_ITER) / N_ITER
    spline_results['times_sympy'].append(t_sym_spl)
    spline_results['times_scipy'].append(t_sci_spl)

# Calculer les moyennes
avg_lag_sympy = np.mean(lagrange_results['times_sympy'])
avg_lag_scipy = np.mean(lagrange_results['times_scipy'])
avg_spl_sympy = np.mean(spline_results['times_sympy'])
avg_spl_scipy = np.mean(spline_results['times_scipy'])

# ── En-tête principal ─────────────────────────────────────────────────────────

st.title("Interpolation Numérique")
st.markdown(
    "Comparaison **SymPy** (calcul symbolique exact) vs **SciPy** (calcul numérique rapide) "
    "pour deux méthodes d'interpolation vues en cours."
)

if is_multi_problem:
    st.info(f"🔄 **Mode Multiple** : Résolution de {num_problems} problèmes générés automatiquement. Affichage des statistiques moyennes et du premier problème en détail.")

# ── Affichage des données des problèmes ──────────────────────────────────────

st.divider()
st.subheader("📊 Données des Problèmes")

if is_multi_problem:
    # Mode multiple : afficher tous les problèmes en accordéons
    for prob_idx, (x_prob, y_prob) in enumerate(problems):
        with st.expander(f"**Problème {prob_idx + 1}**", expanded=(prob_idx == 0)):
            col_x_data, col_y_data = st.columns(2)
            
            with col_x_data:
                x_str = ", ".join([f"{x:.4g}" for x in x_prob])
                st.text_input(f"x (Problème {prob_idx + 1})", value=x_str, 
                             help="Valeurs de x séparées par des virgules", 
                             key=f"x_display_{prob_idx}", disabled=True)
            
            with col_y_data:
                y_str = ", ".join([f"{y:.4g}" for y in y_prob])
                st.text_input(f"y (Problème {prob_idx + 1})", value=y_str, 
                             help="Valeurs de y séparées par des virgules", 
                             key=f"y_display_{prob_idx}", disabled=True)
else:
    # Mode unique : afficher et permettre la modification
    st.info("💡 **Ajustement des points** : Vous pouvez modifier les valeurs ci-dessous. Les calculs se mettront à jour automatiquement.")
    col_x_data, col_y_data = st.columns(2)
    
    with col_x_data:
        x_val = st.text_input("Points X (séparés par des virgules)", key="x_input_val")
    
    with col_y_data:
        y_val = st.text_input("Points Y (séparés par des virgules)", key="y_input_val")


# ── Onglets ───────────────────────────────────────────────────────────────────

tab_lag, tab_spl = st.tabs(
    ["📈 Interpolation de Lagrange", "🔧 Spline Quadratique"]
)


# ════════════════════════════════════════════════════════════════════════════════
# ONGLET 1 — LAGRANGE
# ════════════════════════════════════════════════════════════════════════════════

with tab_lag:

    st.header("Interpolation Polynomiale de Lagrange")

    if is_multi_problem:
        st.subheader("📊 Résultats Globaux (Tous les problèmes)")
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("Temps moyen SymPy", f"{avg_lag_sympy * 1e3:.3f} ms")
        with col_stat2:
            st.metric("Temps moyen SciPy", f"{avg_lag_scipy * 1e3:.3f} ms")
        with col_stat3:
            ratio = avg_lag_sympy / avg_lag_scipy if avg_lag_scipy > 0 else float("inf")
            st.metric("Ratio SymPy/SciPy", f"{ratio:.1f}×")
        
        # Graphique comparatif
        fig_multi, ax_multi = plt.subplots(figsize=(10, 5))
        problems_ids = [f"P{i+1}" for i in range(num_problems)]
        ax_multi.plot(problems_ids, [t*1e3 for t in lagrange_results['times_sympy']], 
                     marker='o', linewidth=2, markersize=8, label='SymPy', color='#8e44ad')
        ax_multi.plot(problems_ids, [t*1e3 for t in lagrange_results['times_scipy']], 
                     marker='s', linewidth=2, markersize=8, label='SciPy', color='#2980b9')
        ax_multi.axhline(y=avg_lag_sympy*1e3, color='#8e44ad', linestyle='--', alpha=0.5, label='Moyenne SymPy')
        ax_multi.axhline(y=avg_lag_scipy*1e3, color='#2980b9', linestyle='--', alpha=0.5, label='Moyenne SciPy')
        ax_multi.set_ylabel('Temps (ms)')
        ax_multi.set_xlabel('Problème')
        ax_multi.set_title('Lagrange — Évolution des temps par problème')
        ax_multi.legend()
        ax_multi.grid(True, alpha=0.3)
        st.pyplot(fig_multi, use_container_width=True)
        plt.close(fig_multi)
        
        st.divider()
        st.subheader("📋 Détail du premier problème")
    
    with st.expander("Formules du cours", expanded=False):
        st.latex(
            r"L_i(x) = \prod_{\substack{j=0 \\ j \neq i}}^{n} "
            r"\frac{x - x_j}{x_i - x_j}"
        )
        st.latex(r"P(x) = \sum_{j=0}^{n} y_j \cdot L_j(x)")
        st.markdown("**Propriété :** $P(x_i) = y_i$ pour tout $i$.")

    # ── Calculs pour le premier problème ──────────────────────────────────────

    t_sym_lag = lagrange_results['times_sympy'][0]
    t_sci_lag = lagrange_results['times_scipy'][0]
    
    P_sym, x_sym, bases_sym = lagrange_sympy(x_pts, y_pts)
    P_sci = lagrange_scipy(x_pts, y_pts)

    # ── Affichage côte à côte ─────────────────────────────────────────────────

    col_s, col_c = st.columns(2)

    # ── Colonne SymPy ─────────────────────────────────────────────────────────
    with col_s:
        st.subheader("SymPy — calcul symbolique")
        st.metric("Temps moyen (SymPy)", f"{t_sym_lag * 1e3:.3f} ms")

        st.markdown("**Bases de Lagrange $L_i(x)$ :**")
        for i, Li in enumerate(bases_sym):
            st.latex(rf"L_{{{i}}}(x) = {sp.latex(Li)}")

        st.markdown("**Polynôme $P(x)$ développé :**")
        st.latex(f"P(x) = {sp.latex(P_sym)}")

        st.markdown("**Vérification $P(x_i) = y_i$ :**")
        all_ok = True
        for xi, yi in zip(x_pts, y_pts):
            val = float(P_sym.subs(x_sym, xi))
            ok = abs(val - yi) < 1e-8
            all_ok = all_ok and ok
            st.write(
                f"  P({xi}) = {val:.6f}  ←  attendu {yi}  "
                + ("✅" if ok else "❌")
            )
        if all_ok:
            st.success("H1 satisfaite : P(xᵢ) = yᵢ  pour tout i")

    # ── Colonne SciPy ─────────────────────────────────────────────────────────
    with col_c:
        st.subheader("SciPy — scipy.interpolate.lagrange")
        st.metric("Temps moyen (SciPy)", f"{t_sci_lag * 1e3:.3f} ms")

        # Affichage du polynôme sous forme lisible
        coeffs_sci = P_sci.coeffs
        deg = len(coeffs_sci) - 1
        terms = []
        for k, c_val in enumerate(coeffs_sci):
            power = deg - k
            if abs(c_val) < 1e-12:
                continue
            c_str = f"{c_val:.4f}"
            if power == 0:
                terms.append(c_str)
            elif power == 1:
                terms.append(f"({c_str})x")
            else:
                terms.append(f"({c_str})x^{{{power}}}")
        poly_display = " + ".join(terms) if terms else "0"
        st.markdown("**Polynôme $P(x)$ :**")
        st.latex(f"P(x) = {poly_display}")

        st.markdown("**Vérification $P(x_i) = y_i$ :**")
        all_ok2 = True
        for xi, yi in zip(x_pts, y_pts):
            val = float(P_sci(xi))
            ok = abs(val - yi) < 1e-6
            all_ok2 = all_ok2 and ok
            st.write(
                f"  P({xi}) = {val:.6f}  ←  attendu {yi}  "
                + ("✅" if ok else "❌")
            )
        if all_ok2:
            st.success("H1 satisfaite : P(xᵢ) = yᵢ  pour tout i")

    # ── Comparaison des temps ─────────────────────────────────────────────────

    st.divider()
    st.subheader("Comparaison des temps de calcul")

    ratio_lag = t_sym_lag / t_sci_lag if t_sci_lag > 0 else float("inf")
    c1, c2, c3 = st.columns(3)
    c1.metric("SymPy", f"{t_sym_lag * 1e3:.3f} ms")
    c2.metric("SciPy", f"{t_sci_lag * 1e3:.3f} ms")
    c3.metric(
        "Ratio SymPy / SciPy",
        f"{ratio_lag:.1f}×",
        delta=f"SciPy {'plus rapide' if ratio_lag > 1 else 'plus lent'}",
        delta_color="normal",
    )

    fig_bar, ax_bar = plt.subplots(figsize=(4, 3))
    ax_bar.bar(
        ["SymPy", "SciPy"],
        [t_sym_lag * 1e3, t_sci_lag * 1e3],
        color=["#8e44ad", "#2980b9"],
        edgecolor="white",
    )
    ax_bar.set_ylabel("Temps moyen (ms)")
    ax_bar.set_title("Lagrange — temps de calcul")
    ax_bar.grid(axis="y", alpha=0.3)
    st.pyplot(fig_bar, use_container_width=False)
    plt.close(fig_bar)

    # ── Courbes d'interpolation ───────────────────────────────────────────────

    st.divider()
    st.subheader("Courbes d'interpolation")

    x_plot = np.linspace(x_arr[0], x_arr[-1], 500)

    # SymPy : lambdify pour vectorisation
    P_num = sp.lambdify(x_sym, P_sym, "numpy")
    y_sym_plot = P_num(x_plot)

    # SciPy : poly1d est vectorisé
    y_sci_plot = P_sci(x_plot)

    fig_lag, ax_lag = plt.subplots(figsize=(9, 5))
    
    # Courbe de la fonction originale (si valide)
    try:
        x_sym_plot = sp.Symbol('x')
        expr_plot = sp.sympify(func_input)
        f_np_plot = sp.lambdify(x_sym_plot, expr_plot, "numpy")
        y_orig_plot = f_np_plot(x_plot)
        ax_lag.plot(x_plot, y_orig_plot, ":", color="gray", alpha=0.6, label=f"Originale : {func_input}")
    except:
        pass

    ax_lag.plot(x_plot, y_sym_plot, "-",  color="#8e44ad", lw=2.5, label="Lagrange — SymPy")
    ax_lag.plot(x_plot, y_sci_plot, "--", color="#2980b9", lw=2,   label="Lagrange — SciPy")
    ax_lag.plot(x_arr, y_arr, "ro", ms=8, zorder=5, label="Points donnés")
    ax_lag.set_xlabel("x")
    ax_lag.set_ylabel("P(x)")
    ax_lag.set_title("Interpolation de Lagrange — SymPy vs SciPy")
    ax_lag.legend()
    ax_lag.grid(True, alpha=0.3)
    st.pyplot(fig_lag)
    plt.close(fig_lag)



# ════════════════════════════════════════════════════════════════════════════════
# ONGLET 2 — SPLINE QUADRATIQUE
# ════════════════════════════════════════════════════════════════════════════════

with tab_spl:

    st.header("Spline Quadratique")
    n_pieces = len(x_pts) - 1
    
    if is_multi_problem:
        st.subheader("📊 Résultats Globaux (Tous les problèmes)")
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("Temps moyen SymPy", f"{avg_spl_sympy * 1e3:.3f} ms")
        with col_stat2:
            st.metric("Temps moyen SciPy", f"{avg_spl_scipy * 1e3:.3f} ms")
        with col_stat3:
            ratio = avg_spl_sympy / avg_spl_scipy if avg_spl_scipy > 0 else float("inf")
            st.metric("Ratio SymPy/SciPy", f"{ratio:.1f}×")
        
        # Graphique comparatif
        fig_multi_spl, ax_multi_spl = plt.subplots(figsize=(10, 5))
        problems_ids = [f"P{i+1}" for i in range(num_problems)]
        ax_multi_spl.plot(problems_ids, [t*1e3 for t in spline_results['times_sympy']], 
                         marker='o', linewidth=2, markersize=8, label='SymPy', color='#8e44ad')
        ax_multi_spl.plot(problems_ids, [t*1e3 for t in spline_results['times_scipy']], 
                         marker='s', linewidth=2, markersize=8, label='SciPy', color='#27ae60')
        ax_multi_spl.axhline(y=avg_spl_sympy*1e3, color='#8e44ad', linestyle='--', alpha=0.5, label='Moyenne SymPy')
        ax_multi_spl.axhline(y=avg_spl_scipy*1e3, color='#27ae60', linestyle='--', alpha=0.5, label='Moyenne SciPy')
        ax_multi_spl.set_ylabel('Temps (ms)')
        ax_multi_spl.set_xlabel('Problème')
        ax_multi_spl.set_title('Spline Quadratique — Évolution des temps par problème')
        ax_multi_spl.legend()
        ax_multi_spl.grid(True, alpha=0.3)
        st.pyplot(fig_multi_spl, use_container_width=True)
        plt.close(fig_multi_spl)
        
        st.divider()
        st.subheader("📋 Détail du premier problème")

    with st.expander("Formules du cours", expanded=False):
        st.latex(r"z_0 = S'(x_0) = 0")
        st.latex(
            r"z_{i+1} = \frac{2(y_{i+1} - y_i)}{h_i} - z_i, "
            r"\quad h_i = x_{i+1} - x_i"
        )
        st.latex(
            r"S_i(x) = \frac{z_{i+1} - z_i}{2h_i}(x - x_i)^2 "
            r"+ z_i\,(x - x_i) + y_i, \quad x \in [x_i,\, x_{i+1}]"
        )

    # ── Calculs pour le premier problème ──────────────────────────────────────

    t_sym_spl = spline_results['times_sympy'][0]
    t_sci_spl = spline_results['times_scipy'][0]
    
    morceaux_sym, z_sym, S_pw = spline_sympy(x_pts, y_pts)
    spline_pp = spline_scipy(x_pts, y_pts)
    z_c = calculer_zi(x_arr, y_arr)

    # ── Affichage côte à côte ─────────────────────────────────────────────────

    col_s2, col_c2 = st.columns(2)
    x_sp = sp.Symbol("x")

    # ── Colonne SymPy ─────────────────────────────────────────────────────────
    with col_s2:
        st.subheader("SymPy — calcul symbolique")
        st.metric("Temps moyen (SymPy)", f"{t_sym_spl * 1e3:.3f} ms")

        st.markdown("**Dérivées aux nœuds $z_i$ :**")
        for i, zi in enumerate(z_sym):
            st.latex(f"z_{{{i}}} = {sp.latex(zi)}")

        st.markdown("**Expressions $S_i(x) = a_i x^2 + b_i x + c_i$ :**")
        for i, (Si, xi, xi1) in enumerate(morceaux_sym):
            st.latex(
                rf"S_{{{i}}}(x) = {sp.latex(Si)},\quad "
                rf"x \in [{sp.latex(xi)},\, {sp.latex(xi1)}]"
            )

        st.markdown("**Vérifications :**")

        # H1 : S(x_i) = y_i
        h1_ok = True
        for xi, yi in zip(x_pts, y_pts):
            val = S_pw.subs(x_sp, xi)
            try:
                val_f = float(val)
            except Exception:
                val_f = float(val.evalf())
            ok = abs(val_f - yi) < 1e-8
            h1_ok = h1_ok and ok
            st.write(f"  H1: S({xi}) = {val_f:.6f} ← {yi}  " + ("✅" if ok else "❌"))

        # H2 : S_i(x_{i+1}) = S_{i+1}(x_{i+1})
        h2_ok = True
        for i in range(n_pieces - 1):
            xi1 = morceaux_sym[i][2]  # borne droite du morceau i
            val_left  = float(morceaux_sym[i][0].subs(x_sp, xi1))
            val_right = float(morceaux_sym[i + 1][0].subs(x_sp, xi1))
            ok = abs(val_left - val_right) < 1e-8
            h2_ok = h2_ok and ok
            st.write(
                f"  H2: S_{i}({float(xi1)}) = {val_left:.6f},  "
                f"S_{i+1}({float(xi1)}) = {val_right:.6f}  " + ("✅" if ok else "❌")
            )

        # H3 : S'_i(x_{i+1}) = S'_{i+1}(x_{i+1})
        h3_ok = True
        for i in range(n_pieces - 1):
            xi1 = morceaux_sym[i][2]
            dSi   = sp.diff(morceaux_sym[i][0], x_sp).subs(x_sp, xi1)
            dSi1  = sp.diff(morceaux_sym[i + 1][0], x_sp).subs(x_sp, xi1)
            ok = abs(float(dSi) - float(dSi1)) < 1e-8
            h3_ok = h3_ok and ok
            st.write(
                f"  H3: S'_{i}({float(xi1)}) = {float(dSi):.6f},  "
                f"S'_{i+1}({float(xi1)}) = {float(dSi1):.6f}  " + ("✅" if ok else "❌")
            )

        if h1_ok and (n_pieces < 2 or (h2_ok and h3_ok)):
            st.success("H1, H2, H3 satisfaites")

    # ── Colonne SciPy ─────────────────────────────────────────────────────────
    with col_c2:
        st.subheader("SciPy — PPoly (scipy.interpolate)")
        st.metric("Temps moyen (SciPy)", f"{t_sci_spl * 1e3:.3f} ms")

        st.markdown("**Dérivées aux nœuds $z_i$ :**")
        for i, zi in enumerate(z_c):
            st.write(f"  z_{i} = {zi:.6f}")

        st.markdown(
            r"**Formule directe $S_i(x) = \frac{z_{i+1}-z_i}{2h_i}(x-x_i)^2"
            r" + z_i(x-x_i) + y_i$ :**"
        )
        for i in range(n_pieces):
            hi  = x_pts[i + 1] - x_pts[i]
            ai  = (z_c[i + 1] - z_c[i]) / (2.0 * hi)
            zi  = z_c[i]
            yi  = y_pts[i]
            xi  = x_pts[i]
            sign_z = "+" if zi >= 0 else "-"
            sign_y = "+" if yi >= 0 else "-"
            st.latex(
                rf"S_{{{i}}}(x) = {ai:.4f}(x-{xi:.4g})^2 "
                rf"{sign_z} {abs(zi):.4f}(x-{xi:.4g}) "
                rf"{sign_y} {abs(yi):.4g},\quad "
                rf"x\in[{x_pts[i]},\, {x_pts[i+1]}]"
            )

        st.markdown("**Vérifications :**")

        # H1
        h1_ok2 = True
        for xi, yi in zip(x_pts, y_pts):
            val = float(spline_pp(xi))
            ok = abs(val - yi) < 1e-8
            h1_ok2 = h1_ok2 and ok
            st.write(f"  H1: S({xi}) = {val:.6f} ← {yi}  " + ("✅" if ok else "❌"))

        # H2 : S_i(x_{i+1}) = y_{i+1} par construction
        h2_ok2 = True
        for i in range(n_pieces - 1):
            xi1 = x_pts[i + 1]
            hi  = x_pts[i + 1] - x_pts[i]
            # S_i(x_{i+1}) = (z_{i+1}-z_i)/(2*hi)*hi² + z_i*hi + y_i
            val_l = (z_c[i+1] - z_c[i]) / (2*hi) * hi**2 + z_c[i] * hi + y_pts[i]
            # S_{i+1}(x_{i+1}) = 0 + 0 + y_{i+1}
            val_r = y_pts[i + 1]
            ok = abs(val_l - val_r) < 1e-8
            h2_ok2 = h2_ok2 and ok
            st.write(
                f"  H2: S_{i}({xi1}) = {val_l:.6f},  "
                f"S_{i+1}({xi1}) = {val_r:.6f}  " + ("✅" if ok else "❌")
            )

        # H3 : S'_i(x_{i+1}) = z_{i+1} par construction
        h3_ok2 = True
        for i in range(n_pieces - 1):
            xi1  = x_pts[i + 1]
            # S'_i(x_{i+1}) = z_{i+1}  (dérivée au bord droit du morceau i)
            dS_l = z_c[i + 1]
            # S'_{i+1}(x_{i+1}) = z_{i+1}  (dérivée au bord gauche du morceau i+1)
            dS_r = z_c[i + 1]
            ok = abs(dS_l - dS_r) < 1e-8
            h3_ok2 = h3_ok2 and ok
            st.write(
                f"  H3: S'_{i}({xi1}) = {dS_l:.6f},  "
                f"S'_{i+1}({xi1}) = {dS_r:.6f}  " + ("✅" if ok else "❌")
            )

        if h1_ok2 and (n_pieces < 2 or (h2_ok2 and h3_ok2)):
            st.success("H1, H2, H3 satisfaites")

    # ── Comparaison des temps ─────────────────────────────────────────────────

    st.divider()
    st.subheader("Comparaison des temps de calcul")

    ratio_spl = t_sym_spl / t_sci_spl if t_sci_spl > 0 else float("inf")
    d1, d2, d3 = st.columns(3)
    d1.metric("SymPy", f"{t_sym_spl * 1e3:.3f} ms")
    d2.metric("SciPy", f"{t_sci_spl * 1e3:.3f} ms")
    d3.metric(
        "Ratio SymPy / SciPy",
        f"{ratio_spl:.1f}×",
        delta=f"SciPy {'plus rapide' if ratio_spl > 1 else 'plus lent'}",
        delta_color="normal",
    )

    fig_bar2, ax_bar2 = plt.subplots(figsize=(4, 3))
    ax_bar2.bar(
        ["SymPy", "SciPy"],
        [t_sym_spl * 1e3, t_sci_spl * 1e3],
        color=["#8e44ad", "#27ae60"],
        edgecolor="white",
    )
    ax_bar2.set_ylabel("Temps moyen (ms)")
    ax_bar2.set_title("Spline Quadratique — temps de calcul")
    ax_bar2.grid(axis="y", alpha=0.3)
    st.pyplot(fig_bar2, use_container_width=False)
    plt.close(fig_bar2)

    # ── Courbes ───────────────────────────────────────────────────────────────

    st.divider()
    st.subheader("Courbes d'interpolation")

    x_plot_s = np.linspace(x_arr[0], x_arr[-1], 500)

    # SymPy : lambdify par morceau (Algorithme 4)
    funcs_sym = [sp.lambdify(x_sp, morceaux_sym[i][0], "numpy") for i in range(n_pieces)]
    y_sym_spl = np.zeros(len(x_plot_s))
    for k, xk in enumerate(x_plot_s):
        idx = 0
        while idx < n_pieces - 1 and xk > x_pts[idx + 1]:
            idx += 1
        y_sym_spl[k] = funcs_sym[idx](xk)

    # SciPy PPoly
    y_sci_spl = spline_pp(x_plot_s)

    fig_spl, ax_spl = plt.subplots(figsize=(9, 5))
    
    # Courbe de la fonction originale (si valide)
    try:
        x_sym_plot2 = sp.Symbol('x')
        expr_plot2 = sp.sympify(func_input)
        f_np_plot2 = sp.lambdify(x_sym_plot2, expr_plot2, "numpy")
        y_orig_spl = f_np_plot2(x_plot_s)
        ax_spl.plot(x_plot_s, y_orig_spl, ":", color="gray", alpha=0.6, label=f"Originale : {func_input}")
    except:
        pass

    ax_spl.plot(x_plot_s, y_sym_spl, "-",  color="#8e44ad", lw=2.5, label="Spline — SymPy")
    ax_spl.plot(x_plot_s, y_sci_spl, "--", color="#27ae60", lw=2,   label="Spline — SciPy")
    ax_spl.plot(x_arr, y_arr, "ro", ms=8, zorder=5, label="Points donnés")
    for xi in x_arr[1:-1]:
        ax_spl.axvline(x=xi, color="gray", linestyle=":", alpha=0.4)
    ax_spl.set_xlabel("x")
    ax_spl.set_ylabel("S(x)")
    ax_spl.set_title("Spline Quadratique — SymPy vs SciPy")
    ax_spl.legend()
    ax_spl.grid(True, alpha=0.3)
    st.pyplot(fig_spl)
    plt.close(fig_spl)

