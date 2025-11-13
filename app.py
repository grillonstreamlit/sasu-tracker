#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="SASU Tracker V12.2 @Grillon_", layout="wide", page_icon="")
st.title("SASU Tracker V12.2 - @Grillon_")
st.caption("Tu choisis tes mois | Conges provisionnes | Tresor reel | IS Reel")

def safe_float(val, default=0.0):
    try:
        return float(val)
    except (TypeError, ValueError):
        return default

def safe_int(val, default=0):
    try:
        return int(val)
    except (TypeError, ValueError):
        return default

# Initialiser les clés session_state si absentes
if "depenses" not in st.session_state:
    st.session_state.depenses = [
        {"nom": "Loyer Paris", "montant": 670, "pct": 80, "pro": True},
        {"nom": "Garage", "montant": 130, "pct": 100, "pro": True},
        {"nom": "Repas", "montant": 400, "pct": 50, "pro": True},
    ]

if "mois_travailles" not in st.session_state:
    st.session_state.mois_travailles = 10
if "ca_mensuel" not in st.session_state:
    st.session_state.ca_mensuel = 10000.0
if "salaire_brut" not in st.session_state:
    st.session_state.salaire_brut = 3200.0
if "dividendes" not in st.session_state:
    st.session_state.dividendes = 0.0
if "mois_conges_payes" not in st.session_state:
    st.session_state.mois_conges_payes = 2

# Flag pour contrôler import JSON unique par session
if "json_import_done" not in st.session_state:
    st.session_state.json_import_done = False

# === 1. Mois travaillés ===
st.subheader("1. Combien de mois tu travailles ?")
st.session_state.mois_travailles = st.slider(
    "Mois travailles par an", 1, 12, st.session_state.mois_travailles, 1)

# === 2. CA mensuel ===
st.subheader("2. Combien tu gagnes par mois travaille ?")
st.session_state.ca_mensuel = float(st.session_state.ca_mensuel)
st.session_state.ca_mensuel = st.number_input(
    "CA HT par mois travaille (EUR)", min_value=5000.0, max_value=20000.0,
    value=st.session_state.ca_mensuel, step=500.0)

# === 3. Salaire & dividendes ===
st.subheader("3. Combien tu te payes ?")
col_s1, col_s2 = st.columns(2)
with col_s1:
    st.session_state.salaire_brut = st.number_input(
        "Salaire brut mensuel (EUR)", min_value=0.0, max_value=10000.0, value=st.session_state.salaire_brut, step=100.0)
with col_s2:
    st.session_state.dividendes = st.number_input(
        "Dividendes annuels (EUR)", min_value=0.0, max_value=100000.0, value=st.session_state.dividendes, step=1000.0)

# === 4. Dépenses ===
st.subheader("4. Combien tu dépenses ?")

def add_depense():
    st.session_state.depenses.append({"nom": "", "montant": 0.0, "pct": 100, "pro": True})
    st.rerun()

# Import JSON complet
st.divider()
st.markdown("#### Importer un état complet (JSON)")
uploaded_file = st.file_uploader("Importer un fichier JSON complet", type=["json"])
if uploaded_file is not None and not st.session_state.json_import_done:
    try:
        data = json.load(uploaded_file)
        if isinstance(data, dict):
            # Dépenses
            if "depenses" in data:
                st.session_state.depenses = []
                for dep in data["depenses"]:
                    dep_clean = {
                        "nom": dep.get("nom", ""),
                        "montant": safe_float(dep.get("montant", 0)),
                        "pct": safe_int(dep.get("pct", 100)),
                        "pro": bool(dep.get("pro", True)),
                    }
                    st.session_state.depenses.append(dep_clean)
            # Variables globales avec conversions sécurisées
            if "mois_travailles" in data:
                st.session_state.mois_travailles = safe_int(data.get("mois_travailles", 10))
            if "ca_mensuel" in data:
                st.session_state.ca_mensuel = safe_float(data.get("ca_mensuel", 10000.0))
            if "salaire_brut" in data:
                st.session_state.salaire_brut = safe_float(data.get("salaire_brut", 3200.0))
            if "dividendes" in data:
                st.session_state.dividendes = safe_float(data.get("dividendes", 0.0))
            if "mois_conges_payes" in data:
                st.session_state.mois_conges_payes = safe_int(data.get("mois_conges_payes", 2))
            st.session_state.json_import_done = True
            st.success("Import complet réussi avec normalisation.")
            st.rerun()
        else:
            st.warning("Le fichier JSON doit contenir un dictionnaire complet d'état.")
    except Exception as e:
        st.error(f"Erreur import JSON complet : {e}")

# Bouton ajouter dépense
if st.button("Ajouter une dépense", key="btn_add_depense"):
    add_depense()

depenses_list = []
for i, dep in enumerate(st.session_state.depenses):
    nom = dep.get("nom", "")
    montant = dep.get("montant", 0.0)
    pct = dep.get("pct", 100)
    pro = dep.get("pro", True)

    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
    with col1:
        nom = st.text_input("Nom", value=nom, key=f"dep_nom_{i}")
    with col2:
        montant = float(montant)
        montant = st.number_input("Montant (EUR)", 0.0, 10000.0, montant, key=f"dep_montant_{i}")
    with col3:
        pct = st.slider("% deduc.", 0, 100, pct, 5, key=f"dep_pct_{i}")
    with col4:
        pro = st.checkbox("Pro", value=pro, key=f"dep_pro_{i}")
    with col5:
        if st.button("Supprimer", key=f"dep_del_{i}"):
            st.session_state.depenses.pop(i)
            st.rerun()

    # Mise à jour état
    st.session_state.depenses[i]["nom"] = nom
    st.session_state.depenses[i]["montant"] = montant
    st.session_state.depenses[i]["pct"] = pct
    st.session_state.depenses[i]["pro"] = pro

    deduct = montant * pct / 100 if pro else 0
    non_deduct = montant - deduct
    depenses_list.append({"nom": nom, "brut": montant, "deduct": deduct, "non_deduct": non_deduct})

# Export complet JSON
st.divider()
st.markdown("#### Exporter l’état complet (JSON)")
etat_complet = {
    "depenses": st.session_state.depenses,
    "mois_travailles": st.session_state.mois_travailles,
    "ca_mensuel": st.session_state.ca_mensuel,
    "salaire_brut": st.session_state.salaire_brut,
    "dividendes": st.session_state.dividendes,
    "mois_conges_payes": st.session_state.mois_conges_payes,
}
dep_json = json.dumps(etat_complet, indent=2, ensure_ascii=False)
st.download_button("Télécharger en JSON complet", dep_json, file_name="etat_complet.json", mime="application/json")

# Calculs
ca_annuel = st.session_state.ca_mensuel * st.session_state.mois_travailles
depenses_pro_mensuel = sum(d["deduct"] for d in depenses_list)
depenses_perso_mensuel = sum(d["non_deduct"] for d in depenses_list)
charges_sociales_mensuel = round(st.session_state.salaire_brut * 0.39, 0)
salaire_net_mensuel = st.session_state.salaire_brut - charges_sociales_mensuel

# Congés payés
st.subheader("5. Combien de mois de congés payés ?")

default_index = 0
if st.session_state.mois_conges_payes in [1, 2]:
    default_index = [1, 2].index(st.session_state.mois_conges_payes)

mois_conges_payes = st.selectbox(
    "Mois de congés payés", [1, 2],
    index=default_index,
    key="mois_conges_payes"
)

pct_conges = 0.10 if mois_conges_payes == 1 else 0.20
provision_conges_mensuel = round(st.session_state.salaire_brut * pct_conges, 0)
charges_conges_mensuel = round(provision_conges_mensuel * 0.39, 0)

st.markdown(f"""
**Tu prends {mois_conges_payes} mois de congés → tu provisionnes {int(pct_conges*100)} % du brut**    
**Provision mensuelle** : `{provision_conges_mensuel:,.0f} EUR`    
**Charges sociales** : `{charges_conges_mensuel:,.0f} EUR`
""")

# Bénéfice et IS
reste_sasu_mensuel = (st.session_state.ca_mensuel - depenses_pro_mensuel -
                     st.session_state.salaire_brut - provision_conges_mensuel)
reste_sasu_annuel = reste_sasu_mensuel * st.session_state.mois_travailles
benefice_annuel = reste_sasu_annuel
is_tax = 0.15 * min(benefice_annuel, 42500) + 0.25 * max(benefice_annuel - 42500, 0)

tresor_sasu = reste_sasu_annuel - is_tax - st.session_state.dividendes
cash_perso_mensuel = salaire_net_mensuel - depenses_perso_mensuel
cash_perso_annuel = cash_perso_mensuel * st.session_state.mois_travailles + st.session_state.dividendes * 0.70

# Vue mensuelle
st.divider()
st.subheader("Ce qui se passe chaque mois travaille")
st.markdown(f"""
**Tu gagnes** : `{st.session_state.ca_mensuel:,.0f} EUR`    
**La société depense** : `{depenses_pro_mensuel:,.0f} EUR`    
**Tu payes toi-même** : `{depenses_perso_mensuel:,.0f} EUR`    
**Tu te payes** : `{st.session_state.salaire_brut:,.0f} EUR` (brut) → **{salaire_net_mensuel:,.0f} EUR** (net)

**Tu provisionnes pour tes congés** : `{provision_conges_mensuel:,.0f} EUR` (+ {charges_conges_mensuel:,.0f} EUR charges)

**Argent qui reste dans la SASU (avant IS)** :    
`{st.session_state.ca_mensuel:,.0f} - {depenses_pro_mensuel:,.0f} - ({st.session_state.salaire_brut:,.0f} + {provision_conges_mensuel:,.0f}) = **{reste_sasu_mensuel:,.0f} EUR**`

**Argent en poche (toi)** :    
`{salaire_net_mensuel:,.0f} - {depenses_perso_mensuel:,.0f} = **{cash_perso_mensuel:,.0f} EUR**`
""")

# Vue annuelle
st.divider()
st.subheader("Vue Annuelle")
col_a1, col_a2, col_a3, col_a4 = st.columns(4)
with col_a1:
    st.metric("CA annuel", f"{ca_annuel:,.0f} EUR")
with col_a2:
    st.metric("IS à payer", f"{is_tax:,.0f} EUR")
with col_a3:
    st.metric("Trésorerie SASU après IS", f"{tresor_sasu:,.0f} EUR")
with col_a4:
    st.metric("Ton cash total", f"{cash_perso_annuel:,.0f} EUR")

# Tableau dépenses + export CSV
df_dep = pd.DataFrame(depenses_list)
if not df_dep.empty:
    df_dep = df_dep[["nom", "brut", "deduct", "non_deduct"]]
    df_dep.columns = ["Dépense", "Total (EUR)", "Payé par SASU (EUR)", "Payé par toi (EUR)"]
    st.dataframe(df_dep, width="stretch")

    csv_data = df_dep.to_csv(index=False, sep=";")
    st.download_button("Télécharger le tableau en CSV", csv_data, "depenses.csv", "text/csv")

st.success(f"IS = {is_tax:,.0f} EUR → Ajuste pour 0 !")
st.caption("V12 | @Grillon_ | 2025 | Tu choisis tes mois | Conges provisionnes | Tu domines")

