"""
Dashboard Streamlit pour l'analyse Superstore
🎯 Niveau débutant - Interface intuitive et code commenté
📊 Visualisations interactives avec Plotly
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os

# === CONFIGURATION PAGE ===
st.set_page_config(
    page_title="Superstore BI Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === STYLES CSS PERSONNALISÉS ===
st.markdown("""
<style>
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    h1 {
        color: #2c3e50;
        font-weight: 700;
    }
    h2 {
        color: #34495e;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# === CONFIGURATION API ===
API_URL = os.getenv("API_URL", "http://localhost:8000")

# === HELPERS ===
@st.cache_data(ttl=300)
def appeler_api(endpoint: str, params: dict = None):
    try:
        url = f"{API_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except:
        st.error("❌ Impossible de se connecter à l'API")
        st.stop()

def formater_euro(v): return f"{v:,.2f} €".replace(",", " ").replace(".", ",")
def formater_nombre(v): return f"{v:,}".replace(",", " ")
def formater_pourcentage(v): return f"{v:.2f}%"

# === CONNEXION API ===
with st.spinner("🔄 Connexion à l'API..."):
    info_api = appeler_api("/")
    st.success(f"✅ Connecté à l'API - Dataset : {info_api['dataset']} ({info_api['nb_lignes']} lignes)")

# === HEADER ===
st.title("🛒 Superstore BI Dashboard")
st.markdown("**Analyse Business Intelligence du dataset Superstore - Tableau de bord interactif**")
st.divider()

# === SIDEBAR ===
st.sidebar.header("🎯 Filtres d'analyse")
valeurs_filtres = appeler_api("/filters/valeurs")

date_min = datetime.strptime(valeurs_filtres['plage_dates']['min'], '%Y-%m-%d')
date_max = datetime.strptime(valeurs_filtres['plage_dates']['max'], '%Y-%m-%d')

col1, col2 = st.sidebar.columns(2)
with col1:
    date_debut = st.date_input("Du", value=date_min, min_value=date_min, max_value=date_max)
with col2:
    date_fin = st.date_input("Au", value=date_max, min_value=date_min, max_value=date_max)

categorie = st.sidebar.selectbox("📦 Catégorie", ["Toutes"] + valeurs_filtres['categories'])
region = st.sidebar.selectbox("🌍 Région", ["Toutes"] + valeurs_filtres['regions'])
segment = st.sidebar.selectbox("👥 Segment client", ["Tous"] + valeurs_filtres['segments'])

if st.sidebar.button("🔄 Réinitialiser les filtres"):
    st.rerun()

params_filtres = {
    'date_debut': date_debut.strftime('%Y-%m-%d'),
    'date_fin': date_fin.strftime('%Y-%m-%d')
}
if categorie != "Toutes": params_filtres['categorie'] = categorie
if region != "Toutes": params_filtres['region'] = region
if segment != "Tous": params_filtres['segment'] = segment

# === SECTION KPI ===
st.header("📊 Indicateurs Clés de Performance (KPI)")

# INSIGHT NARRATIF
st.info("💡 Malgré un chiffre d’affaires solide, la marge reste sensible aux remises et aux produits peu rentables. Les KPI globaux montrent une croissance qui masque des fragilités de rentabilité.")

with st.spinner("📈 Chargement des KPI..."):
    kpi_data = appeler_api("/kpi/globaux", params=params_filtres)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💰 Chiffre d'affaires", formater_euro(kpi_data['ca_total']))
    st.metric("📈 Marge moyenne", formater_pourcentage(kpi_data['marge_moyenne']))

with col2:
    st.metric("🧾 Commandes", formater_nombre(kpi_data['nb_commandes']))
    st.metric("💵 Profit total", formater_euro(kpi_data['profit_total']))

with col3:
    st.metric("👥 Clients", formater_nombre(kpi_data['nb_clients']))
    st.metric("🛒 Panier moyen", formater_euro(kpi_data['panier_moyen']))

with col4:
    st.metric("📦 Quantité vendue", formater_nombre(kpi_data['quantite_vendue']))
    articles_par_commande = kpi_data['quantite_vendue'] / kpi_data['nb_commandes']
    st.metric("📊 Articles/commande", f"{articles_par_commande:.2f}")

st.divider()
# === SECTION 2 : ANALYSES DÉTAILLÉES ===
st.header("📈 Analyses Détaillées")

# Tabs pour organiser les différentes analyses
tab1, tab2, tab3, tab4 = st.tabs(["🏆 Produits", "📦 Catégories", "📅 Temporel", "🌍 Géographique"])

# --- TAB 1 : PRODUITS ---
with tab1:
    st.subheader("Top 10 Produits")

    # INSIGHT PRODUITS
    st.write("💡 Les meilleurs produits génèrent une grande partie du chiffre d’affaires, mais certains affichent un profit faible malgré un volume élevé. Cela indique un risque de dépendance à des produits peu rentables.")

    col_tri, col_limite = st.columns([3, 1])
    with col_tri:
        critere_tri = st.radio(
            "Trier par",
            options=['ca', 'profit', 'quantite'],
            format_func=lambda x: {'ca': '💰 CA', 'profit': '💵 Profit', 'quantite': '📦 Quantité'}[x],
            horizontal=True
        )
    with col_limite:
        nb_produits = st.number_input("Afficher", min_value=5, max_value=50, value=10, step=5)

    top_produits = appeler_api("/kpi/produits/top", params={'limite': nb_produits, 'tri_par': critere_tri})
    df_produits = pd.DataFrame(top_produits)

    labels_criteres = {'ca': 'CA', 'profit': 'Profit', 'quantite': 'Quantité'}

    fig_produits = px.bar(
        df_produits,
        x=critere_tri,
        y='produit',
        color='categorie',
        orientation='h',
        title=f"Top {nb_produits} Produits par {labels_criteres[critere_tri]}",
        labels={
            'ca': 'Chiffre d\'affaires (€)',
            'profit': 'Profit (€)',
            'quantite': 'Quantité vendue',
            'produit': 'Produit',
            'categorie': 'Catégorie'
        },
        color_discrete_sequence=px.colors.qualitative.Set3,
        height=500
    )
    fig_produits.update_layout(showlegend=True, hovermode='closest', yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_produits, use_container_width=True)

    # RISQUE PRODUITS
    st.warning("⚠️ Certains produits à forte remise apparaissent dans le top CA mais détruisent du profit. Une analyse du mix produit est recommandée.")

    with st.expander("📋 Voir le tableau détaillé"):
        st.dataframe(
            df_produits[['produit', 'categorie', 'ca', 'profit', 'quantite']].rename(columns={
                'produit': 'Produit',
                'categorie': 'Catégorie',
                'ca': 'CA (€)',
                'profit': 'Profit (€)',
                'quantite': 'Quantité'
            }),
            use_container_width=True,
            hide_index=True
        )

# --- TAB 2 : CATÉGORIES ---
with tab2:
    st.subheader("Performance par Catégorie")

    # INSIGHT CATÉGORIES
    st.write("💡 La catégorie Technology est la plus rentable, tandis que Furniture présente une marge plus faible malgré un CA important. Cela révèle un problème structurel de rentabilité dans Furniture.")

    categories = appeler_api("/kpi/categories")
    df_cat = pd.DataFrame(categories)

    col_left, col_right = st.columns(2)

    with col_left:
        fig_cat = go.Figure()
        fig_cat.add_trace(go.Bar(
            name='CA',
            x=df_cat['categorie'],
            y=df_cat['ca'],
            marker_color='#667eea',
            text=df_cat['ca'].apply(lambda x: f"{x:,.0f}€"),
            textposition='outside'
        ))
        fig_cat.add_trace(go.Bar(
            name='Profit',
            x=df_cat['categorie'],
            y=df_cat['profit'],
            marker_color='#764ba2',
            text=df_cat['profit'].apply(lambda x: f"{x:,.0f}€"),
            textposition='outside'
        ))
        fig_cat.update_layout(
            title="CA et Profit par Catégorie",
            barmode='group',
            xaxis_title="Catégorie",
            yaxis_title="Montant (€)",
            height=400,
            showlegend=True
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_right:
        fig_marge = px.bar(
            df_cat,
            x='categorie',
            y='marge_pct',
            title="Marge par Catégorie (%)",
            labels={'categorie': 'Catégorie', 'marge_pct': 'Marge (%)'},
            color='marge_pct',
            color_continuous_scale='Viridis',
            text='marge_pct',
            height=400
        )
        fig_marge.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        st.plotly_chart(fig_marge, use_container_width=True)

    # OPPORTUNITÉ CATÉGORIES
    st.info("💡 Opportunité : renforcer l’offre Technology et optimiser les remises dans Furniture pour améliorer la marge.")

    st.markdown("### 📊 Tableau récapitulatif")
    st.dataframe(
        df_cat[['categorie', 'ca', 'profit', 'marge_pct', 'nb_commandes']].rename(columns={
            'categorie': 'Catégorie',
            'ca': 'CA (€)',
            'profit': 'Profit (€)',
            'marge_pct': 'Marge (%)',
            'nb_commandes': 'Nb Commandes'
        }),
        use_container_width=True,
        hide_index=True
    )

# --- TAB 3 : TEMPOREL ---
with tab3:
    st.subheader("Évolution Temporelle")

    # INSIGHT TEMPOREL
    st.write("💡 Le chiffre d’affaires suit une saisonnalité marquée, avec des pics réguliers. Cependant, la marge ne suit pas toujours la même tendance, ce qui indique un problème de maîtrise des coûts ou des remises.")

    granularite = st.radio(
        "Période d'analyse",
        options=['jour', 'mois', 'annee'],
        format_func=lambda x: {'jour': '📅 Par jour', 'mois': '📊 Par mois', 'annee': '📈 Par année'}[x],
        horizontal=True
    )

    temporal = appeler_api("/kpi/temporel", params={'periode': granularite})
    df_temporal = pd.DataFrame(temporal)

    fig_temporal = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Évolution du CA et Profit", "Évolution du Nombre de Commandes"),
        vertical_spacing=0.12,
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
    )

    fig_temporal.add_trace(
        go.Scatter(
            x=df_temporal['periode'],
            y=df_temporal['ca'],
            mode='lines+markers',
            name='CA',
            line=dict(color='#667eea', width=3),
            fill='tozeroy'
        ),
        row=1, col=1
    )

    fig_temporal.add_trace(
        go.Scatter(
            x=df_temporal['periode'],
            y=df_temporal['profit'],
            mode='lines+markers',
            name='Profit',
            line=dict(color='#764ba2', width=3)
        ),
        row=1, col=1
    )

    fig_temporal.add_trace(
        go.Bar(
            x=df_temporal['periode'],
            y=df_temporal['nb_commandes'],
            name='Commandes',
            marker_color='#f39c12'
        ),
        row=2, col=1
    )

    fig_temporal.update_layout(height=700, showlegend=True)
    st.plotly_chart(fig_temporal, use_container_width=True)

    col_stats1, col_stats2, col_stats3 = st.columns(3)
    with col_stats1:
        st.metric("📈 CA moyen/période", formater_euro(df_temporal['ca'].mean()))
    with col_stats2:
        st.metric("📊 Commandes moy/période", formater_nombre(int(df_temporal['nb_commandes'].mean())))
    with col_stats3:
        meilleure_periode = df_temporal.loc[df_temporal['ca'].idxmax()]
        st.metric("🏆 Meilleure période", meilleure_periode['periode'])

# --- TAB 4 : GÉOGRAPHIQUE ---
with tab4:
    st.subheader("Performance Géographique")

    # INSIGHT GÉOGRAPHIQUE
    st.warning("⚠️ La région West génère un CA correct mais reste la moins rentable. Cela suggère un problème de pricing, de coûts logistiques ou de remises trop élevées.")

    geo = appeler_api("/kpi/geographique")
    df_geo = pd.DataFrame(geo)

    col_geo1, col_geo2 = st.columns(2)

    with col_geo1:
        fig_geo_ca = px.bar(
            df_geo,
            x='region',
            y='ca',
            title="Chiffre d'affaires par Région",
            labels={'region': 'Région', 'ca': 'CA (€)'},
            color='ca',
            color_continuous_scale='Blues',
            text='ca',
            height=400
        )
        fig_geo_ca.update_traces(texttemplate='%{text:,.0f}€', textposition='outside')
        st.plotly_chart(fig_geo_ca, use_container_width=True)

    with col_geo2:
        fig_geo_clients = px.pie(
            df_geo,
            values='nb_clients',
            names='region',
            title="Répartition des Clients par Région",
            color_discrete_sequence=px.colors.qualitative.Set3,
            height=400
        )
        fig_geo_clients.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_geo_clients, use_container_width=True)

    st.info("💡 Opportunité : cibler les régions les plus rentables (South, East) pour maximiser la croissance.")

    st.markdown("### 📊 Tableau géographique détaillé")
    st.dataframe(
        df_geo[['region', 'ca', 'profit', 'nb_clients', 'nb_commandes']].rename(columns={
            'region': 'Région',
            'ca': 'CA (€)',
            'profit': 'Profit (€)',
            'nb_clients': 'Nb Clients',
            'nb_commandes': 'Nb Commandes'
        }),
        use_container_width=True,
        hide_index=True
    )

# === SECTION 3 : ANALYSE CLIENTS ===
st.header("👥 Analyse Clients")

# INSIGHT CLIENTS
st.write("💡 Les clients récurrents génèrent une part importante du CA, tandis que les clients à achat unique restent nombreux. Le taux de fidélisation est un levier majeur d’amélioration de la rentabilité.")

clients_data = appeler_api("/kpi/clients", params={'limite': 10})

col_client1, col_client2 = st.columns([2, 1])

with col_client1:
    st.subheader("🏆 Top 10 Clients")
    df_top_clients = pd.DataFrame(clients_data['top_clients'])

    fig_clients = px.bar(
        df_top_clients,
        x='ca_total',
        y='nom',
        orientation='h',
        title="Top Clients par CA",
        labels={'ca_total': 'CA Total (€)', 'nom': 'Client'},
        color='nb_commandes',
        color_continuous_scale='Viridis',
        height=400
    )
    st.plotly_chart(fig_clients, use_container_width=True)

with col_client2:
    st.subheader("📊 Statistiques clients")
    rec = clients_data['recurrence']

    st.metric("Total clients", formater_nombre(rec['total_clients']))
    st.metric("Clients récurrents", formater_nombre(rec['clients_recurrents']))
    st.metric("Clients 1 achat", formater_nombre(rec['clients_1_achat']))
    st.metric("Commandes/client", f"{rec['nb_commandes_moyen']:.2f}")

    taux_fidelisation = (rec['clients_recurrents'] / rec['total_clients'] * 100)
    st.metric("Taux de fidélisation", f"{taux_fidelisation:.1f}%")

# OPPORTUNITÉ CLIENTS
st.info("💡 Opportunité : renforcer les programmes de fidélité pour augmenter la valeur client à long terme.")

# Analyse par segment
st.subheader("💼 Performance par Segment Client")
df_segments = pd.DataFrame(clients_data['segments'])

fig_segments = go.Figure()
fig_segments.add_trace(go.Bar(
    name='CA',
    x=df_segments['segment'],
    y=df_segments['ca'],
    marker_color='#3498db'
))
fig_segments.add_trace(go.Bar(
    name='Profit',
    x=df_segments['segment'],
    y=df_segments['profit'],
    marker_color='#2ecc71'
))
fig_segments.update_layout(
    title="CA et Profit par Segment",
    barmode='group',
    height=350
)
st.plotly_chart(fig_segments, use_container_width=True)

"""
SECTIONS À AJOUTER dans app.py
Coller ces sections APRÈS la section "Analyse Clients" existante
et AVANT la "Synthèse Finale"
"""

# ================================================================
# SECTION 4 : RENTABILITÉ (new)
# ================================================================
st.divider()
st.header("💰 Analyse de Rentabilité")

st.write("💡 La rentabilité va au-delà du chiffre d'affaires. Cette section identifie les produits qui détruisent la marge et l'impact réel des remises.")

tab_rent1, tab_rent2, tab_rent3 = st.tabs(["📊 Vue Globale", "⚠️ Produits en Perte", "📉 Impact Remises"])

# --- TAB : RENTABILITÉ GLOBALE ---
with tab_rent1:
    rentabilite = appeler_api("/kpi/rentabilite/globale", params=params_filtres)
    
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        couleur = "normal" if rentabilite['est_sante'] else "inverse"
        st.metric("📊 Marge Globale", formater_pourcentage(rentabilite['marge_globale']))
    with col_r2:
        st.metric("💵 Profit Total", formater_euro(rentabilite['profit_total']))
    with col_r3:
        statut = "✅ Saine" if rentabilite['est_sante'] else "⚠️ Fragile"
        st.metric("🏥 Santé financière", statut)

    # Message storytelling de l'API
    if rentabilite['est_sante']:
        st.success(rentabilite['message'])
    else:
        st.warning(rentabilite['message'])

    # Rentabilité par catégorie
    st.subheader("Marge par Catégorie")
    rent_cat = appeler_api("/kpi/rentabilite/categories", params=params_filtres)
    df_rent_cat = pd.DataFrame(rent_cat)

    fig_rent_cat = px.bar(
        df_rent_cat,
        x='categorie',
        y='marge_pct',
        color='marge_pct',
        color_continuous_scale='RdYlGn',
        title="Marge (%) par Catégorie — vert = rentable, rouge = fragile",
        labels={'categorie': 'Catégorie', 'marge_pct': 'Marge (%)'},
        text='marge_pct',
        height=400
    )
    fig_rent_cat.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_rent_cat.add_hline(y=12, line_dash="dash", line_color="red",
                        annotation_text="Seuil recommandé 12%")
    st.plotly_chart(fig_rent_cat, use_container_width=True)

    # Tendance de marge dans le temps
    st.subheader("📈 Tendance de la Marge")
    tendance = appeler_api("/kpi/rentabilite/tendance", params=params_filtres)
    df_tendance = pd.DataFrame(tendance)

    fig_tendance = px.line(
        df_tendance,
        x='periode',
        y='marge_pct',
        title="Évolution de la marge mensuelle (%)",
        labels={'periode': 'Période', 'marge_pct': 'Marge (%)'},
        markers=True,
        height=350
    )
    fig_tendance.add_hline(y=12, line_dash="dash", line_color="red",
                        annotation_text="Seuil 12%")
    fig_tendance.update_traces(line=dict(color='#667eea', width=3))
    st.plotly_chart(fig_tendance, use_container_width=True)

# --- TAB : PRODUITS EN PERTE ---
with tab_rent2:
    st.write("⚠️ Ces produits génèrent du CA mais **détruisent de la marge**. Chaque vente de ces produits coûte de l'argent à l'entreprise.")

    pertes = appeler_api("/kpi/rentabilite/pertes", params={
        'limite': 10,
        **{k: v for k, v in params_filtres.items() if k in ['date_debut', 'date_fin', 'categorie', 'region']}
    })

    if pertes:
        df_pertes = pd.DataFrame(pertes)

        fig_pertes = px.bar(
            df_pertes,
            x='perte_montant',
            y='produit',
            color='categorie',
            orientation='h',
            title="Top 10 Produits en Perte (montant de perte en €)",
            labels={'perte_montant': 'Perte (€)', 'produit': 'Produit'},
            color_discrete_sequence=px.colors.qualitative.Set1,
            height=450
        )
        fig_pertes.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_pertes, use_container_width=True)

        perte_totale = df_pertes['perte_montant'].sum()
        st.error(f"💸 Ces {len(df_pertes)} produits génèrent **{formater_euro(abs(perte_totale))}** de pertes cumulées.")
    else:
        st.success("✅ Aucun produit en perte détecté sur cette période !")

# --- TAB : IMPACT REMISES ---
with tab_rent3:
    st.write("📉 Cette analyse montre comment les remises élevées **font chuter le profit moyen par transaction**.")

    remises = appeler_api("/kpi/rentabilite/remises", params={
        k: v for k, v in params_filtres.items()
        if k in ['date_debut', 'date_fin', 'categorie']
    })
    df_remises = pd.DataFrame(remises)

    fig_remises = px.bar(
        df_remises,
        x='remise',
        y='profit_moyen',
        title="Profit moyen selon le taux de remise",
        labels={'remise': 'Taux de remise', 'profit_moyen': 'Profit moyen (€)'},
        color='profit_moyen',
        color_continuous_scale='RdYlGn',
        text='profit_moyen',
        height=400
    )
    fig_remises.update_traces(texttemplate='%{text:.1f}€', textposition='outside')
    fig_remises.add_hline(y=0, line_color="red", line_width=2)
    st.plotly_chart(fig_remises, use_container_width=True)

    # Calcul du seuil où le profit devient négatif
    seuil_negatif = df_remises[df_remises['profit_moyen'] < 0]
    if not seuil_negatif.empty:
        premier_seuil = seuil_negatif.iloc[0]['remise']
        st.warning(f"⚠️ À partir de **{premier_seuil*100:.0f}% de remise**, le profit moyen devient négatif.")

# ================================================================
# SECTION 5 : COMPARAISONS TEMPORELLES (new)
# ================================================================
st.divider()
st.header("📅 Comparaisons & Saisonnalité")

tab_comp1, tab_comp2, tab_comp3 = st.tabs(["📊 Année sur Année", "📅 Saisonnalité", "📉 Produits en Déclin"])

# --- TAB : COMPARAISON ANNUELLE ---
with tab_comp1:
    st.write("💡 Comparer deux années permet d'identifier si la croissance est réelle ou si elle masque une dégradation de la rentabilité.")

    col_annee1, col_annee2 = st.columns(2)
    with col_annee1:
        annee_ref = st.selectbox("📅 Année de référence", [2021, 2022, 2023], index=0)
    with col_annee2:
        annee_comp = st.selectbox("📅 Année de comparaison", [2022, 2023, 2024], index=1)

    comp_params = {'annee_reference': annee_ref, 'annee_comparaison': annee_comp}
    if categorie != "Toutes":
        comp_params['categorie'] = categorie
    if region != "Toutes":
        comp_params['region'] = region

    comparaison = appeler_api("/kpi/comparaison/annuel", params=comp_params)

    # Affichage des variations
    col_v1, col_v2, col_v3 = st.columns(3)
    with col_v1:
        st.metric(
            "💰 CA",
            formater_euro(comparaison['ca_comparaison']),
            delta=f"{comparaison['variation_ca_pct']:+.1f}%",
            help=f"Référence: {formater_euro(comparaison['ca_reference'])}"
        )
    with col_v2:
        st.metric(
            "💵 Profit",
            formater_euro(comparaison['profit_comparaison']),
            delta=f"{comparaison['variation_profit_pct']:+.1f}%",
            help=f"Référence: {formater_euro(comparaison['profit_reference'])}"
        )
    with col_v3:
        st.metric(
            "🧾 Commandes",
            formater_nombre(comparaison['commandes_comparaison']),
            delta=f"{comparaison['variation_commandes_pct']:+.1f}%",
            help=f"Référence: {formater_nombre(comparaison['commandes_reference'])}"
        )

    # Message storytelling de l'API
    if comparaison['variation_ca_pct'] > 0:
        st.success(comparaison['message'])
    else:
        st.warning(comparaison['message'])

    # Graphique comparatif
    df_comp_viz = pd.DataFrame({
        'Métrique': ['CA', 'Profit', 'Commandes'],
        str(annee_ref): [
            comparaison['ca_reference'],
            comparaison['profit_reference'],
            comparaison['commandes_reference']
        ],
        str(annee_comp): [
            comparaison['ca_comparaison'],
            comparaison['profit_comparaison'],
            comparaison['commandes_comparaison']
        ]
    })

    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(
        name=str(annee_ref),
        x=df_comp_viz['Métrique'],
        y=df_comp_viz[str(annee_ref)],
        marker_color='#667eea'
    ))
    fig_comp.add_trace(go.Bar(
        name=str(annee_comp),
        x=df_comp_viz['Métrique'],
        y=df_comp_viz[str(annee_comp)],
        marker_color='#764ba2'
    ))
    fig_comp.update_layout(
        title=f"Comparaison {annee_ref} vs {annee_comp}",
        barmode='group',
        height=400
    )
    st.plotly_chart(fig_comp, use_container_width=True)

# --- TAB : SAISONNALITÉ ---
with tab_comp2:
    st.write("💡 La saisonnalité révèle les périodes de pic et de creux. Anticiper ces cycles permet d'optimiser les stocks et les promotions.")

    saison_params = {}
    if categorie != "Toutes":
        saison_params['categorie'] = categorie

    saisonnalite = appeler_api("/kpi/saisonnalite", params=saison_params)
    df_saison = pd.DataFrame(saisonnalite['saisonnalite'])

    fig_saison = make_subplots(rows=1, cols=2,
                               subplot_titles=("CA par mois", "Profit par mois"))

    fig_saison.add_trace(
        go.Bar(
            x=df_saison['mois_nom'],
            y=df_saison['ca'],
            marker_color='#667eea',
            name='CA'
        ), row=1, col=1
    )

    fig_saison.add_trace(
        go.Bar(
            x=df_saison['mois_nom'],
            y=df_saison['profit'],
            marker_color='#2ecc71',
            name='Profit'
        ), row=1, col=2
    )

    fig_saison.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_saison, use_container_width=True)

    # Insights saisonnalité
    insights = saisonnalite['insights']
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.metric("🏆 Meilleur mois", insights['meilleur_mois'])
    with col_s2:
        st.metric("📉 Mois le plus faible", insights['pire_mois'])
    with col_s3:
        st.metric("📊 Écart max/min", f"{insights['variation_max_min_pct']:.0f}%")

    st.info(saisonnalite['message'])

# --- TAB : PRODUITS EN DÉCLIN ---
with tab_comp3:
    st.write("📉 Identifier les produits qui perdent des ventes permet d'agir avant qu'ils deviennent des produits en perte.")

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        periode_ref_declin = st.text_input("Période de référence (YYYY-MM)", value="2022-01")
    with col_d2:
        periode_comp_declin = st.text_input("Période de comparaison (YYYY-MM)", value="2023-01")

    declin = appeler_api("/kpi/produits/declin", params={
        'limite': 10,
        'periode_reference': periode_ref_declin,
        'periode_comparaison': periode_comp_declin
    })

    if declin['produits']:
        df_declin = pd.DataFrame(declin['produits'])

        fig_declin = px.bar(
            df_declin,
            x='variation_pct',
            y='produit',
            orientation='h',
            color='categorie',
            title="Produits en déclin (variation des ventes %)",
            labels={'variation_pct': 'Variation (%)', 'produit': 'Produit'},
            height=450
        )
        fig_declin.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_declin, use_container_width=True)
        st.warning(declin['message'])
    else:
        st.success(declin['message'])

# ================================================================
# SECTION 6 : RÉSUMÉ EXÉCUTIF (new)
# ================================================================
st.divider()
st.header("📋 Résumé Exécutif")

st.write("Vue consolidée pour les décideurs — tous les indicateurs clés en un seul endroit.")

resume_params = {
    'date_debut': params_filtres.get('date_debut'),
    'date_fin': params_filtres.get('date_fin')
}

resume = appeler_api("/kpi/dashboard/resume", params=resume_params)

# Performance globale
perf = resume['performance_globale']
col_e1, col_e2, col_e3 = st.columns(3)
with col_e1:
    st.metric("💰 CA Total", formater_euro(perf['ca_total']))
    st.metric("🛒 Panier moyen", formater_euro(perf['panier_moyen']))
with col_e2:
    st.metric("💵 Profit Total", formater_euro(perf['profit_total']))
    st.metric("📈 Marge Globale", formater_pourcentage(perf['marge_globale_pct']))
with col_e3:
    st.metric("🧾 Commandes", formater_nombre(perf['nb_commandes']))
    st.metric("👥 Clients", formater_nombre(perf['nb_clients']))

# Catégories : meilleure vs à améliorer
col_cat1, col_cat2 = st.columns(2)
with col_cat1:
    st.success(f"✅ **Meilleure catégorie** : {resume['categories']['meilleure']['nom']} — {resume['categories']['meilleure']['marge_pct']}% de marge")
with col_cat2:
    st.warning(f"⚠️ **À améliorer** : {resume['categories']['a_ameliorer']['nom']} — {resume['categories']['a_ameliorer']['marge_pct']}% de marge")

# Alertes
alertes = resume['alertes']
if alertes['produits_en_perte'] > 0:
    st.error(f"🚨 **{alertes['produits_en_perte']} produits en perte** représentant {formater_euro(abs(alertes['montant_pertes']))} de pertes.")

# Message narratif de l'API
st.info(resume['message'])

# Recommandations de l'API
st.subheader("🎯 Recommandations")
for i, reco in enumerate(resume['recommandations'], 1):
    st.write(f"**{i}.** {reco}")

# === SYNTHÈSE FINALE ===
st.divider()
st.header("🧠 Synthèse Finale")

st.write("""
L’analyse du dataset Superstore met en évidence une situation contrastée : 
l’entreprise génère un chiffre d’affaires solide, mais sa rentabilité reste fragile. 
Plusieurs facteurs expliquent cette tension : des remises trop élevées, des produits structurellement non rentables, 
et des disparités importantes entre les régions et les segments clients.

Les catégories Technology et Office Supplies tirent la performance globale, 
tandis que Furniture souffre d’une marge faible malgré un volume de ventes important. 
La région West apparaît comme un point faible récurrent, avec un profit nettement inférieur aux autres régions.

Enfin, les clients récurrents représentent un levier majeur de valeur, 
mais la proportion de clients à achat unique reste élevée, ce qui limite la croissance de la marge à long terme.
""")

# === RECOMMANDATIONS STRATÉGIQUES ===
st.header("🎯 Recommandations Stratégiques")

st.subheader("1. Optimiser la politique de remises")
st.write("""
Les remises supérieures à 20 % entraînent une chute significative du profit. 
Une politique de remise plus contrôlée, notamment sur les produits sensibles, permettrait d’améliorer la marge globale.
""")

st.subheader("2. Revoir le mix produit")
st.write("""
Certains produits génèrent du chiffre d’affaires mais détruisent du profit. 
Une analyse plus fine du catalogue permettrait de retirer ou repositionner les références les moins rentables.
""")

st.subheader("3. Renforcer la stratégie régionale")
st.write("""
La région West sous-performe nettement. 
Un ajustement des prix, une optimisation logistique ou une réduction des remises pourraient améliorer la rentabilité locale.
""")

st.subheader("4. Investir dans la fidélisation client")
st.write("""
Les clients récurrents génèrent une valeur plus stable et plus rentable. 
Mettre en place des programmes de fidélité ou des offres personnalisées augmenterait la valeur client à long terme.
""")

st.subheader("5. Capitaliser sur les catégories à forte marge")
st.write("""
Technology et Office Supplies sont les moteurs de la rentabilité. 
Renforcer ces gammes, améliorer leur visibilité et optimiser les stocks peut accélérer la croissance.
""")



# === FOOTER ===
st.divider()
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #7f8c8d;'>
        <p>📊 <b>Superstore BI Dashboard</b> | Propulsé par FastAPI + Streamlit + Plotly</p>
        <p>💡 Dashboard pédagogique pour l'apprentissage de la Business Intelligence</p>
    </div>
    """,
    unsafe_allow_html=True
)
