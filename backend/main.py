"""
API FastAPI pour l'analyse du dataset Superstore
🎯 Version améliorée avec gestion d'erreurs robuste
📊 Tous les KPI e-commerce implémentés
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime
import pandas as pd
from pydantic import BaseModel
import logging
from functools import lru_cache

# Configuration du logger pour faciliter le débogage
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation de l'application FastAPI
app = FastAPI(
    title="Superstore BI API",
    description="API d'analyse Business Intelligence pour le dataset Superstore",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS - À RESTREINDRE EN PRODUCTION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:3000"],  # Ajuster selon vos besoins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === CHARGEMENT DES DONNÉES ===

DATASET_URL = "https://raw.githubusercontent.com/leonism/sample-superstore/master/data/superstore.csv"

# Variable globale pour stocker les données
_dataframe_cache = None


@lru_cache(maxsize=1)
def load_data() -> pd.DataFrame:
    """
    Charge le dataset Superstore depuis GitHub
    Nettoie et prépare les données pour l'analyse
    """
    try:
        logger.info(f"Chargement du dataset depuis {DATASET_URL}")

        df = pd.read_csv(DATASET_URL, encoding='latin-1')
        df.columns = df.columns.str.strip().str.lower()

        # Conversion des dates
        df['order date'] = pd.to_datetime(df['order date'], errors='coerce')
        df['ship date'] = pd.to_datetime(df['ship date'], errors='coerce')

        # Suppression des lignes critiques manquantes
        df = df.dropna(subset=['order id', 'customer id', 'sales'])

        # Validation des données
        if len(df) == 0:
            raise ValueError("Le dataset est vide après nettoyage")

        logger.info(f"✅ Dataset chargé : {len(df)} commandes")
        return df

    except Exception as e:
        logger.error(f"❌ Erreur lors du chargement des données : {e}")
        raise RuntimeError(f"Erreur de chargement des données : {e}")


def get_dataframe() -> pd.DataFrame:
    """Retourne le dataframe, le charge si nécessaire"""
    global _dataframe_cache
    if _dataframe_cache is None:
        _dataframe_cache = load_data()
    return _dataframe_cache


# === MODÈLES PYDANTIC ===

class KPIGlobaux(BaseModel):
    """Modèle pour les KPI globaux"""
    ca_total: float
    nb_commandes: int
    nb_clients: int
    panier_moyen: float
    quantite_vendue: int
    profit_total: float
    marge_moyenne: float


class ProduitTop(BaseModel):
    """Modèle pour les produits top performers"""
    produit: str
    categorie: str
    ca: float
    quantite: int
    profit: float


class CategoriePerf(BaseModel):
    """Modèle pour la performance par catégorie"""
    categorie: str
    ca: float
    profit: float
    nb_commandes: int
    marge_pct: float


class RentabiliteGlobale(BaseModel):
    """Modèle pour la rentabilité globale"""
    marge_globale: float
    profit_total: float
    est_sante: bool
    message: str


class ProduitPerte(BaseModel):
    """Modèle pour les produits en perte"""
    produit: str
    categorie: str
    perte_montant: float


class ImpactRemise(BaseModel):
    """Modèle pour l'impact des remises"""
    remise: float
    profit_moyen: float


class RentabiliteCategorie(BaseModel):
    """Modèle pour la rentabilité par catégorie"""
    categorie: str
    ca: float
    profit: float
    marge_pct: float


class TendanceRentabilite(BaseModel):
    """Modèle pour la tendance de marge"""
    periode: str
    marge_pct: float


class HealthCheck(BaseModel):
    """Modèle pour le health check"""
    status: str
    dataset_loaded: bool
    nb_records: int
    last_check: str


# === FONCTIONS UTILITAIRES ===

def calculer_marge(profit: float, sales: float) -> float:
    """Calcule la marge en pourcentage de manière sécurisée"""
    if sales == 0 or pd.isna(sales):
        return 0.0
    return round((profit / sales * 100), 2)


def filtrer_dataframe(
    df: pd.DataFrame,
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
    categorie: Optional[str] = None,
    region: Optional[str] = None,
    segment: Optional[str] = None
) -> pd.DataFrame:
    """Applique les filtres sur le dataframe"""
    df_filtered = df.copy()

    dt_start = None
    dt_end = None

    if date_debut:
        try:
            dt_start = pd.to_datetime(date_debut)
            df_filtered = df_filtered[df_filtered['order date'] >= dt_start]
        except Exception:
            raise HTTPException(status_code=400, detail="date_debut invalide, format attendu YYYY-MM-DD")

    if date_fin:
        try:
            dt_end = pd.to_datetime(date_fin)
            df_filtered = df_filtered[df_filtered['order date'] <= dt_end]
        except Exception:
            raise HTTPException(status_code=400, detail="date_fin invalide, format attendu YYYY-MM-DD")

    if dt_start and dt_end and dt_start > dt_end:
        raise HTTPException(status_code=400, detail="date_debut ne peut pas être après date_fin")

    if categorie and categorie != "Toutes":
        df_filtered = df_filtered[df_filtered['category'] == categorie]

    if region and region != "Toutes":
        df_filtered = df_filtered[df_filtered['region'] == region]

    if segment and segment != "Tous":
        df_filtered = df_filtered[df_filtered['segment'] == segment]

    if len(df_filtered) == 0:
        raise HTTPException(
            status_code=404,
            detail="Aucune donnée trouvée avec ces filtres"
        )

    return df_filtered


# === ENDPOINTS API ===

@app.get("/health", response_model=HealthCheck, tags=["Info"])
def health_check():
    """🏥 Vérification de l'état de l'API"""
    try:
        df = get_dataframe()
        return HealthCheck(
            status="healthy",
            dataset_loaded=True,
            nb_records=len(df),
            last_check=datetime.now().isoformat()
        )
    except Exception:
        return HealthCheck(
            status="unhealthy",
            dataset_loaded=False,
            nb_records=0,
            last_check=datetime.now().isoformat()
        )


@app.get("/", tags=["Info"])
def root():
    """Endpoint racine - Informations sur l'API"""
    df = get_dataframe()
    return {
        "message": "🛒 API Superstore BI",
        "version": "1.1.0",
        "dataset": "Sample Superstore",
        "nb_lignes": len(df),
        "periode": {
            "debut": df['order date'].min().strftime('%Y-%m-%d'),
            "fin": df['order date'].max().strftime('%Y-%m-%d')
        },
        "endpoints": {
            "documentation": "/docs",
            "health": "/health",
            "resume_executif": "/kpi/dashboard/resume",
            "kpi_globaux": "/kpi/globaux",
            "top_produits": "/kpi/produits/top",
            "categories": "/kpi/categories",
            "evolution_temporelle": "/kpi/temporel",
            "performance_geo": "/kpi/geographique",
            "analyse_clients": "/kpi/clients",
            
            # Endpoints ajoutés pour la rentabilité et l'analyse approfondie
            "rentabilite_globale": "/kpi/rentabilite/globale",
            "produits_perte": "/kpi/rentabilite/pertes",
            "impact_remises": "/kpi/rentabilite/remises",
            "rentabilite_categories": "/kpi/rentabilite/categories",
            "tendance_marge": "/kpi/rentabilite/tendance",
            "comparaison_annuelle": "/kpi/comparaison/annuel",
            "produits_declin": "/kpi/produits/declin",
            "saisonnalite": "/kpi/saisonnalite"
        }
    }


@app.get("/kpi/globaux", response_model=KPIGlobaux, tags=["KPI"])
def get_kpi_globaux(
    date_debut: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)"),
    categorie: Optional[str] = Query(None, description="Catégorie produit"),
    region: Optional[str] = Query(None, description="Région"),
    segment: Optional[str] = Query(None, description="Segment client")
):
    """📊 KPI GLOBAUX - Indicateurs clés de performance"""
    df = get_dataframe()
    df_filtered = filtrer_dataframe(df, date_debut, date_fin, categorie, region, segment)

    ca_total = float(df_filtered['sales'].sum())
    nb_commandes = int(df_filtered['order id'].nunique())
    nb_clients = int(df_filtered['customer id'].nunique())
    panier_moyen = ca_total / nb_commandes if nb_commandes > 0 else 0
    quantite_vendue = int(df_filtered['quantity'].sum())
    profit_total = float(df_filtered['profit'].sum())
    marge_moyenne = calculer_marge(profit_total, ca_total)

    return KPIGlobaux(
        ca_total=round(ca_total, 2),
        nb_commandes=nb_commandes,
        nb_clients=nb_clients,
        panier_moyen=round(panier_moyen, 2),
        quantite_vendue=quantite_vendue,
        profit_total=round(profit_total, 2),
        marge_moyenne=marge_moyenne
    )


@app.get("/kpi/produits/top", response_model=List[ProduitTop], tags=["KPI"])
def get_top_produits(
    limite: int = Query(10, ge=1, le=50, description="Nombre de produits"),
    tri_par: str = Query("ca", pattern="^(ca|profit|quantite)$", description="Critère de tri"),
    date_debut: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)"),
    categorie: Optional[str] = Query(None, description="Catégorie produit"),
    region: Optional[str] = Query(None, description="Région"),
    segment: Optional[str] = Query(None, description="Segment client")
):
    """🏆 TOP PRODUITS - Meilleurs produits selon critère"""
    df = get_dataframe()
    df_filtered = filtrer_dataframe(df, date_debut, date_fin, categorie, region, segment)

    produits = df_filtered.groupby(['product name', 'category']).agg({
        'sales': 'sum',
        'quantity': 'sum',
        'profit': 'sum'
    }).reset_index()

    if len(produits) == 0:
        return []

    col_map = {"ca": "sales", "profit": "profit", "quantite": "quantity"}
    produits = produits.sort_values(col_map[tri_par], ascending=False)

    top = produits.head(limite)

    return [
        ProduitTop(
            produit=row['product name'],
            categorie=row['category'],
            ca=round(row['sales'], 2),
            quantite=int(row['quantity']),
            profit=round(row['profit'], 2)
        ) for _, row in top.iterrows()
    ]


@app.get("/kpi/categories", response_model=List[CategoriePerf], tags=["KPI"])
def get_performance_categories(
    date_debut: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)"),
    region: Optional[str] = Query(None, description="Région"),
    segment: Optional[str] = Query(None, description="Segment client")
):
    """📦 PERFORMANCE PAR CATÉGORIE"""
    df = get_dataframe()
    df_filtered = filtrer_dataframe(df, date_debut, date_fin, None, region, segment)

    categories = df_filtered.groupby('category').agg({
        'sales': 'sum',
        'profit': 'sum',
        'order id': 'nunique'
    }).reset_index()

    result = []
    for _, row in categories.iterrows():
        marge = calculer_marge(row['profit'], row['sales'])
        result.append(CategoriePerf(
            categorie=row['category'],
            ca=round(row['sales'], 2),
            profit=round(row['profit'], 2),
            nb_commandes=int(row['order id']),
            marge_pct=marge
        ))

    return sorted(result, key=lambda x: x.ca, reverse=True)


@app.get("/kpi/temporel", tags=["KPI"])
def get_evolution_temporelle(
    periode: str = Query('mois', pattern='^(jour|mois|annee)$', description="Granularité"),
    date_debut: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)"),
    categorie: Optional[str] = Query(None, description="Catégorie produit"),
    region: Optional[str] = Query(None, description="Région"),
    segment: Optional[str] = Query(None, description="Segment client")
):
    """📈 ÉVOLUTION TEMPORELLE"""
    df = get_dataframe()
    df_filtered = filtrer_dataframe(df, date_debut, date_fin, categorie, region, segment)

    df_temp = df_filtered.copy()

    format_map = {'jour': '%Y-%m-%d', 'mois': '%Y-%m', 'annee': '%Y'}
    df_temp['periode'] = df_temp['order date'].dt.strftime(format_map[periode])

    temporal = df_temp.groupby('periode').agg({
        'sales': 'sum',
        'profit': 'sum',
        'order id': 'nunique',
        'quantity': 'sum'
    }).reset_index()

    temporal.columns = ['periode', 'ca', 'profit', 'nb_commandes', 'quantite']
    temporal = temporal.sort_values('periode')

    temporal['ca'] = temporal['ca'].round(2)
    temporal['profit'] = temporal['profit'].round(2)

    return temporal.to_dict('records')


@app.get("/kpi/geographique", tags=["KPI"])
def get_performance_geographique(
    date_debut: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)"),
    categorie: Optional[str] = Query(None, description="Catégorie produit"),
    segment: Optional[str] = Query(None, description="Segment client")
):
    """🌍 PERFORMANCE GÉOGRAPHIQUE"""
    df = get_dataframe()
    df_filtered = filtrer_dataframe(df, date_debut, date_fin, categorie, None, segment)

    geo = df_filtered.groupby('region').agg({
        'sales': 'sum',
        'profit': 'sum',
        'customer id': 'nunique',
        'order id': 'nunique'
    }).reset_index()

    geo.columns = ['region', 'ca', 'profit', 'nb_clients', 'nb_commandes']
    geo['ca'] = geo['ca'].round(2)
    geo['profit'] = geo['profit'].round(2)
    geo = geo.sort_values('ca', ascending=False)

    return geo.to_dict('records')


@app.get("/kpi/clients", tags=["KPI"])
def get_analyse_clients(
    limite: int = Query(10, ge=1, le=100, description="Nombre de top clients"),
    date_debut: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)"),
    categorie: Optional[str] = Query(None, description="Catégorie produit"),
    region: Optional[str] = Query(None, description="Région")
):
    """👥 ANALYSE CLIENTS"""
    df = get_dataframe()
    df_filtered = filtrer_dataframe(df, date_debut, date_fin, categorie, region, None)

    clients = df_filtered.groupby('customer id').agg({
        'sales': 'sum',
        'profit': 'sum',
        'order id': 'nunique',
        'customer name': 'first'
    }).reset_index()

    clients.columns = ['customer_id', 'ca_total', 'profit_total', 'nb_commandes', 'nom']
    clients['valeur_commande_moy'] = (clients['ca_total'] / clients['nb_commandes']).round(2)

    top_clients = clients.sort_values('ca_total', ascending=False).head(limite)

    recurrence = {
        "clients_1_achat": int(len(clients[clients['nb_commandes'] == 1])),
        "clients_recurrents": int(len(clients[clients['nb_commandes'] > 1])),
        "nb_commandes_moyen": round(clients['nb_commandes'].mean(), 2),
        "total_clients": int(len(clients))
    }

    segments = df_filtered.groupby('segment').agg({
        'sales': 'sum',
        'profit': 'sum',
        'customer id': 'nunique'
    }).reset_index()
    segments.columns = ['segment', 'ca', 'profit', 'nb_clients']
    segments['ca'] = segments['ca'].round(2)
    segments['profit'] = segments['profit'].round(2)

    return {
        "top_clients": top_clients.to_dict('records'),
        "recurrence": recurrence,
        "segments": segments.to_dict('records')
    }


@app.get("/kpi/rentabilite/globale", response_model=RentabiliteGlobale, tags=["Rentabilité"])
def get_rentabilite_globale(
    date_debut: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)"),
    categorie: Optional[str] = Query(None, description="Catégorie produit"),
    region: Optional[str] = Query(None, description="Région"),
    segment: Optional[str] = Query(None, description="Segment client")
):
    """📊 Analyse de la rentabilité globale"""
    df = get_dataframe()
    df_filtered = filtrer_dataframe(df, date_debut, date_fin, categorie, region, segment)

    ca = float(df_filtered['sales'].sum())
    profit = float(df_filtered['profit'].sum())
    marge = calculer_marge(profit, ca)

    seuil_sante = 12.0
    est_sante = marge > seuil_sante
    message = (
        f"✅ La rentabilité est saine avec une marge de {marge}%."
        if est_sante
        else f"⚠️ Attention : Marge faible de {marge}% (seuil recommandé: {seuil_sante}%)."
    )

    return RentabiliteGlobale(
        marge_globale=marge,
        profit_total=round(profit, 2),
        est_sante=est_sante,
        message=message
    )


@app.get("/kpi/rentabilite/pertes", response_model=List[ProduitPerte], tags=["Rentabilité"])
def get_produits_perte(
    limite: int = Query(10, ge=1, le=50, description="Nombre de produits"),
    date_debut: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)"),
    categorie: Optional[str] = Query(None, description="Catégorie produit"),
    region: Optional[str] = Query(None, description="Région")
):
    """⚠️ Identification des produits en perte"""
    df = get_dataframe()
    df_filtered = filtrer_dataframe(df, date_debut, date_fin, categorie, region, None)

    pertes = df_filtered[df_filtered['profit'] < 0].copy()

    if len(pertes) == 0:
        return []

    pertes = pertes.groupby(['product name', 'category']).agg({
        'profit': 'sum'
    }).reset_index()

    pertes = pertes.sort_values('profit', ascending=True).head(limite)

    return [
        ProduitPerte(
            produit=row['product name'],
            categorie=row['category'],
            perte_montant=round(row['profit'], 2)
        ) for _, row in pertes.iterrows()
    ]


@app.get("/kpi/rentabilite/remises", response_model=List[ImpactRemise], tags=["Rentabilité"])
def get_impact_remises(
    date_debut: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)"),
    categorie: Optional[str] = Query(None, description="Catégorie produit")
):
    """📉 Analyse de l'impact des remises sur la rentabilité"""
    df = get_dataframe()
    df_filtered = filtrer_dataframe(df, date_debut, date_fin, categorie, None, None)

    impact = df_filtered.groupby('discount')['profit'].mean().reset_index()
    impact = impact.sort_values('discount')

    return [
        ImpactRemise(
            remise=round(float(row['discount']), 2),
            profit_moyen=round(float(row['profit']), 2)
        ) for _, row in impact.iterrows()
    ]


@app.get("/kpi/rentabilite/categories", response_model=List[RentabiliteCategorie], tags=["Rentabilité"])
def get_rentabilite_categories(
    date_debut: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)"),
    region: Optional[str] = Query(None, description="Région"),
    segment: Optional[str] = Query(None, description="Segment client")
):
    """📦 Analyse de rentabilité par catégorie"""
    df = get_dataframe()
    df_filtered = filtrer_dataframe(df, date_debut, date_fin, None, region, segment)

    cat_df = df_filtered.groupby('category').agg({
        'sales': 'sum',
        'profit': 'sum'
    }).reset_index()

    result = []
    for _, row in cat_df.iterrows():
        marge = calculer_marge(row['profit'], row['sales'])
        result.append(RentabiliteCategorie(
            categorie=row['category'],
            ca=round(row['sales'], 2),
            profit=round(row['profit'], 2),
            marge_pct=marge
        ))

    return sorted(result, key=lambda x: x.marge_pct, reverse=True)


@app.get("/kpi/rentabilite/tendance", response_model=List[TendanceRentabilite], tags=["Rentabilité"])
def get_tendance_rentabilite(
    date_debut: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)"),
    categorie: Optional[str] = Query(None, description="Catégorie produit"),
    region: Optional[str] = Query(None, description="Région")
):
    """📈 Tendance de la marge dans le temps"""
    df = get_dataframe()
    df_filtered = filtrer_dataframe(df, date_debut, date_fin, categorie, region, None)

    df_temp = df_filtered.copy()
    df_temp['periode'] = df_temp['order date'].dt.strftime('%Y-%m')

    tendance = df_temp.groupby('periode').agg({
        'sales': 'sum',
        'profit': 'sum'
    }).reset_index()

    result = []
    for _, row in tendance.iterrows():
        marge = calculer_marge(row['profit'], row['sales'])
        result.append(TendanceRentabilite(
            periode=row['periode'],
            marge_pct=marge
        ))

    return sorted(result, key=lambda x: x.periode)


@app.get("/filters/valeurs", tags=["Filtres"])
def get_valeurs_filtres():
    df = get_dataframe()
    return {
        "categories": sorted(df['category'].unique().tolist()),
        "regions": sorted(df['region'].unique().tolist()),
        "segments": sorted(df['segment'].unique().tolist()),
        "etats": sorted(df['state'].unique().tolist()),
        "annees": sorted(df['order date'].dt.year.unique().tolist()),  # ADD THIS
        "plage_dates": {
            "min": df['order date'].min().strftime('%Y-%m-%d'),
            "max": df['order date'].max().strftime('%Y-%m-%d')
        }
    }

@app.get("/data/commandes", tags=["Données brutes"])
def get_commandes(
    limite: int = Query(100, ge=1, le=1000, description="Nombre de lignes"),
    offset: int = Query(0, ge=0, description="Décalage")
):
    """📋 Données brutes avec pagination"""
    df = get_dataframe()
    total = len(df)

    if offset >= total:
        raise HTTPException(status_code=400, detail="Offset trop grand")

    commandes = df.iloc[offset:offset+limite].copy()

    commandes['order date'] = commandes['order date'].dt.strftime('%Y-%m-%d')
    commandes['ship date'] = commandes['ship date'].dt.strftime('%Y-%m-%d')

    return {
        "total": total,
        "limite": limite,
        "offset": offset,
        "nb_retourne": len(commandes),
        "data": commandes.to_dict('records')
    }


@app.get("/kpi/comparaison/annuel", tags=["Comparaison Temporelle"])
def get_comparaison_annuelle(
    annee_reference: int = Query(..., description="Année de référence (ex: 2023)"),
    annee_comparaison: int = Query(..., description="Année à comparer (ex: 2024)"),
    categorie: Optional[str] = Query(None, description="Catégorie produit"),
    region: Optional[str] = Query(None, description="Région")
):
    """
    📊 COMPARAISON ANNÉE SUR ANNÉE (Year-over-Year)
    Compare les performances entre deux années pour identifier les tendances.
    """
    df = get_dataframe()

    df['annee'] = df['order date'].dt.year
    df_ref = df[df['annee'] == annee_reference].copy()
    df_comp = df[df['annee'] == annee_comparaison].copy()

    if categorie and categorie != "Toutes":
        df_ref = df_ref[df_ref['category'] == categorie]
        df_comp = df_comp[df_comp['category'] == categorie]
    if region and region != "Toutes":
        df_ref = df_ref[df_ref['region'] == region]
        df_comp = df_comp[df_comp['region'] == region]

    ca_ref = float(df_ref['sales'].sum())
    ca_comp = float(df_comp['sales'].sum())
    profit_ref = float(df_ref['profit'].sum())
    profit_comp = float(df_comp['profit'].sum())
    commandes_ref = int(df_ref['order id'].nunique())
    commandes_comp = int(df_comp['order id'].nunique())

    variation_ca = ((ca_comp - ca_ref) / ca_ref * 100) if ca_ref > 0 else 0
    variation_profit = ((profit_comp - profit_ref) / profit_ref * 100) if profit_ref > 0 else 0
    variation_commandes = ((commandes_comp - commandes_ref) / commandes_ref * 100) if commandes_ref > 0 else 0

    tendance = "croissance" if variation_ca > 0 else "déclin"
    message = f"📈 {tendance.capitalize()} de {abs(variation_ca):.1f}% du CA entre {annee_reference} et {annee_comparaison}."

    return {
        "annee_reference": annee_reference,
        "annee_comparaison": annee_comparaison,
        "ca_reference": round(ca_ref, 2),
        "ca_comparaison": round(ca_comp, 2),
        "variation_ca_pct": round(variation_ca, 2),
        "profit_reference": round(profit_ref, 2),
        "profit_comparaison": round(profit_comp, 2),
        "variation_profit_pct": round(variation_profit, 2),
        "commandes_reference": commandes_ref,
        "commandes_comparaison": commandes_comp,
        "variation_commandes_pct": round(variation_commandes, 2),
        "message": message
    }


@app.get("/kpi/produits/declin", tags=["Analyse Produits"])
def get_produits_en_declin(
    limite: int = Query(10, ge=1, le=50, description="Nombre de produits"),
    periode_reference: str = Query('2023-01', description="Période de référence (YYYY-MM)"),
    periode_comparaison: str = Query('2024-01', description="Période de comparaison (YYYY-MM)")
):
    """
    📉 PRODUITS EN DÉCLIN
    Identifie les produits dont les ventes diminuent.
    """
    df = get_dataframe()
    df['periode'] = df['order date'].dt.strftime('%Y-%m')

    ventes_ref = df[df['periode'] == periode_reference].groupby('product name')['sales'].sum()
    ventes_comp = df[df['periode'] == periode_comparaison].groupby('product name')['sales'].sum()

    comparison = pd.DataFrame({
        'ventes_reference': ventes_ref,
        'ventes_comparaison': ventes_comp
    }).fillna(0)

    comparison['variation_pct'] = (
        (comparison['ventes_comparaison'] - comparison['ventes_reference']) /
        comparison['ventes_reference'] * 100
    ).replace([float('inf'), -float('inf')], 0)

    declin = comparison[comparison['variation_pct'] < 0].sort_values('variation_pct').head(limite)

    if len(declin) == 0:
        return {
            "produits": [],
            "message": "✅ Aucun produit en déclin détecté!"
        }

    produits_cat = df[['product name', 'category']].drop_duplicates().set_index('product name')
    declin = declin.join(produits_cat)

    result = []
    for produit, row in declin.iterrows():
        result.append({
            "produit": produit,
            "categorie": row['category'],
            "ventes_reference": round(row['ventes_reference'], 2),
            "ventes_comparaison": round(row['ventes_comparaison'], 2),
            "variation_pct": round(row['variation_pct'], 2)
        })

    pire_declin = declin.iloc[0]
    message = f"⚠️ Le produit le plus en déclin perd {abs(pire_declin['variation_pct']):.1f}% de ses ventes."

    return {
        "produits": result,
        "message": message
    }


@app.get("/kpi/saisonnalite", tags=["Analyse Temporelle"])
def get_analyse_saisonnalite(
    categorie: Optional[str] = Query(None, description="Catégorie produit")
):
    """
    📅 ANALYSE DE SAISONNALITÉ
    Identifie les patterns saisonniers dans les ventes.
    """
    df = get_dataframe()

    if categorie and categorie != "Toutes":
        df = df[df['category'] == categorie]

    df['mois'] = df['order date'].dt.month
    df['mois_nom'] = df['order date'].dt.strftime('%B')

    saisonnalite = df.groupby(['mois', 'mois_nom']).agg({
        'sales': 'sum',
        'profit': 'sum',
        'order id': 'nunique'
    }).reset_index()

    saisonnalite = saisonnalite.sort_values('mois')

    mois_max_ca = saisonnalite.loc[saisonnalite['sales'].idxmax()]
    mois_min_ca = saisonnalite.loc[saisonnalite['sales'].idxmin()]

    message = (
        f"📊 Le mois le plus fort est {mois_max_ca['mois_nom']} ({mois_max_ca['sales']:.2f}€), "
        f"le plus faible est {mois_min_ca['mois_nom']} ({mois_min_ca['sales']:.2f}€)."
    )

    result = []
    for _, row in saisonnalite.iterrows():
        result.append({
            "mois": int(row['mois']),
            "mois_nom": row['mois_nom'],
            "ca": round(row['sales'], 2),
            "profit": round(row['profit'], 2),
            "nb_commandes": int(row['order id'])
        })

    variation_max_min_pct = (
        (mois_max_ca['sales'] - mois_min_ca['sales']) / mois_min_ca['sales'] * 100
        if mois_min_ca['sales'] > 0 else 0
    )

    return {
        "saisonnalite": result,
        "message": message,
        "insights": {
            "meilleur_mois": mois_max_ca['mois_nom'],
            "pire_mois": mois_min_ca['mois_nom'],
            "variation_max_min_pct": round(variation_max_min_pct, 2)
        }
    }


@app.get("/kpi/dashboard/resume", tags=["Dashboard Global"])
def get_resume_executif(
    date_debut: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)")
):
    """
    📋 RÉSUMÉ EXÉCUTIF POUR DÉCIDEURS
    Vue d'ensemble complète avec storytelling intégré.
    """
    df = get_dataframe()
    df_filtered = filtrer_dataframe(df, date_debut, date_fin, None, None, None)

    ca = float(df_filtered['sales'].sum())
    profit = float(df_filtered['profit'].sum())
    marge = calculer_marge(profit, ca)
    nb_commandes = int(df_filtered['order id'].nunique())
    nb_clients = int(df_filtered['customer id'].nunique())

    produits_perte = df_filtered[df_filtered['profit'] < 0]
    nb_produits_perte = len(produits_perte['product name'].unique())
    perte_totale = float(produits_perte['profit'].sum())

    cat_perf = df_filtered.groupby('category').agg({'sales': 'sum', 'profit': 'sum'}).reset_index()
    cat_perf['marge'] = cat_perf.apply(lambda r: calculer_marge(r['profit'], r['sales']), axis=1)
    meilleure_cat = cat_perf.loc[cat_perf['marge'].idxmax()]
    pire_cat = cat_perf.loc[cat_perf['marge'].idxmin()]

    sante = "bonne" if marge > 12 else "préoccupante"
    message_principal = (
        f"🎯 Votre business est en {sante} santé avec une marge de {marge:.1f}%.\n\n"
        f"📊 Points clés:\n"
        f"- {nb_commandes} commandes pour {ca:.2f}€ de CA\n"
        f"- {nb_clients} clients actifs\n"
        f"- Catégorie la plus rentable: {meilleure_cat['category']} ({meilleure_cat['marge']:.1f}%)\n"
        f"- Catégorie à améliorer: {pire_cat['category']} ({pire_cat['marge']:.1f}%)\n\n"
        f"⚠️ Points d'attention:\n"
        f"- {nb_produits_perte} produits en perte ({perte_totale:.2f}€)"
    )

    return {
        "performance_globale": {
            "ca_total": round(ca, 2),
            "profit_total": round(profit, 2),
            "marge_globale_pct": marge,
            "nb_commandes": nb_commandes,
            "nb_clients": nb_clients,
            "panier_moyen": round(ca / nb_commandes, 2) if nb_commandes > 0 else 0
        },
        "categories": {
            "meilleure": {
                "nom": meilleure_cat['category'],
                "marge_pct": round(meilleure_cat['marge'], 2),
                "ca": round(meilleure_cat['sales'], 2)
            },
            "a_ameliorer": {
                "nom": pire_cat['category'],
                "marge_pct": round(pire_cat['marge'], 2),
                "ca": round(pire_cat['sales'], 2)
            }
        },
        "alertes": {
            "produits_en_perte": nb_produits_perte,
            "montant_pertes": round(perte_totale, 2)
        },
        "message": message_principal.strip(),
        "recommandations": [
            "Analyser les produits en perte pour décider d'arrêter ou d'ajuster les prix" if nb_produits_perte > 0 else "Aucun produit en perte, continuez!",
            f"Investir dans la catégorie {meilleure_cat['category']} qui performe bien",
            (
                f"Améliorer la rentabilité de {pire_cat['category']}"
                if pire_cat['marge'] < 10
                else f"La catégorie {pire_cat['category']} est acceptable"
            )
        ]
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage de l'API Superstore BI sur http://localhost:8000")
    print("📚 Documentation disponible sur http://localhost:8000/docs")
    print("🏥 Health check sur http://localhost:8000/health")
    uvicorn.run(app, host="0.0.0.0", port=8000)
