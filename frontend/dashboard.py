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
