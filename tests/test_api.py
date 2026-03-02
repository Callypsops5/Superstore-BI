"""
Tests unitaires pour l'API Superstore BI
🧪 Couvre tous les endpoints implémentés
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
import sys
import os

# Ajouter le répertoire backend au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app

# ================================================================
# CLIENT DE TEST
# ================================================================

client = TestClient(app)

# ================================================================
# FIXTURES - Données de test réutilisables
# ================================================================

@pytest.fixture
def sample_dataframe():
    """Crée un DataFrame de test représentatif du dataset Superstore"""
    return pd.DataFrame({
        'order id':       ['CA-001', 'CA-002', 'CA-003', 'CA-004', 'CA-005'],
        'order date':     pd.to_datetime(['2023-01-15', '2023-02-20', '2023-03-10', '2023-01-25', '2023-04-05']),
        'ship date':      pd.to_datetime(['2023-01-18', '2023-02-24', '2023-03-14', '2023-01-28', '2023-04-09']),
        'customer id':    ['C001', 'C002', 'C001', 'C003', 'C002'],
        'customer name':  ['Alice Martin', 'Bob Dupont', 'Alice Martin', 'Charlie Petit', 'Bob Dupont'],
        'segment':        ['Consumer', 'Corporate', 'Consumer', 'Home Office', 'Corporate'],
        'region':         ['East', 'West', 'East', 'Central', 'West'],
        'state':          ['New York', 'California', 'New York', 'Texas', 'California'],
        'category':       ['Technology', 'Furniture', 'Office Supplies', 'Technology', 'Furniture'],
        'sub-category':   ['Phones', 'Chairs', 'Paper', 'Accessories', 'Tables'],
        'product name':   ['iPhone 14', 'Chaise Bureau', 'Ramette A4', 'Câble HDMI', 'Table Basse'],
        'sales':          [1200.0, 450.0, 80.0, 150.0, 300.0],
        'quantity':       [2, 1, 5, 3, 1],
        'discount':       [0.0, 0.2, 0.0, 0.1, 0.3],
        'profit':         [300.0, -50.0, 20.0, 45.0, -30.0],
    })


@pytest.fixture
def mock_get_dataframe(sample_dataframe):
    """Mock de la fonction get_dataframe pour éviter les appels réseau"""
    with patch('main.get_dataframe', return_value=sample_dataframe):
        yield sample_dataframe


# ================================================================
# TESTS : ENDPOINTS INFO
# ================================================================

class TestInfoEndpoints:
    """Tests des endpoints d'information généraux"""

    def test_root_returns_200(self, mock_get_dataframe):
        """L'endpoint racine doit retourner 200"""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_contains_expected_keys(self, mock_get_dataframe):
        """L'endpoint racine doit contenir les clés attendues"""
        response = client.get("/")
        data = response.json()
        assert "message" in data
        assert "nb_lignes" in data
        assert "endpoints" in data

    def test_health_returns_200(self, mock_get_dataframe):
        """Le health check doit retourner 200"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_status_healthy(self, mock_get_dataframe):
        """Le health check doit indiquer 'healthy'"""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert data["dataset_loaded"] is True
        assert data["nb_records"] == 5


# ================================================================
# TESTS : KPI GLOBAUX
# ================================================================

class TestKPIGlobaux:
    """Tests de l'endpoint /kpi/globaux"""

    def test_kpi_globaux_returns_200(self, mock_get_dataframe):
        response = client.get("/kpi/globaux")
        assert response.status_code == 200

    def test_kpi_globaux_structure(self, mock_get_dataframe):
        """Vérifie que tous les champs attendus sont présents"""
        response = client.get("/kpi/globaux")
        data = response.json()
        expected_keys = ['ca_total', 'nb_commandes', 'nb_clients',
                         'panier_moyen', 'quantite_vendue', 'profit_total', 'marge_moyenne']
        for key in expected_keys:
            assert key in data, f"Champ manquant : {key}"

    def test_kpi_globaux_ca_total(self, mock_get_dataframe):
        """Le CA total doit être la somme des ventes"""
        response = client.get("/kpi/globaux")
        data = response.json()
        assert data['ca_total'] == pytest.approx(2180.0, rel=0.01)

    def test_kpi_globaux_nb_commandes(self, mock_get_dataframe):
        """Le nombre de commandes doit être correct"""
        response = client.get("/kpi/globaux")
        data = response.json()
        assert data['nb_commandes'] == 5

    def test_kpi_globaux_nb_clients(self, mock_get_dataframe):
        """Le nombre de clients uniques doit être correct"""
        response = client.get("/kpi/globaux")
        data = response.json()
        assert data['nb_clients'] == 3

    def test_kpi_globaux_profit_total(self, mock_get_dataframe):
        """Le profit total doit être correct (inclut les pertes)"""
        response = client.get("/kpi/globaux")
        data = response.json()
        assert data['profit_total'] == pytest.approx(285.0, rel=0.01)

    def test_kpi_globaux_filtre_categorie(self, mock_get_dataframe):
        """Le filtre catégorie doit réduire les résultats"""
        response_tout = client.get("/kpi/globaux")
        response_tech = client.get("/kpi/globaux?categorie=Technology")
        ca_tout = response_tout.json()['ca_total']
        ca_tech = response_tech.json()['ca_total']
        assert ca_tech < ca_tout

    def test_kpi_globaux_filtre_region(self, mock_get_dataframe):
        """Le filtre région doit fonctionner"""
        response = client.get("/kpi/globaux?region=East")
        assert response.status_code == 200
        data = response.json()
        assert data['ca_total'] > 0

    def test_kpi_globaux_date_invalide(self, mock_get_dataframe):
        """Une date invalide doit retourner une erreur 400"""
        response = client.get("/kpi/globaux?date_debut=invalid-date")
        assert response.status_code == 400

    def test_kpi_globaux_date_debut_apres_fin(self, mock_get_dataframe):
        """date_debut > date_fin doit retourner une erreur 400"""
        response = client.get("/kpi/globaux?date_debut=2023-12-01&date_fin=2023-01-01")
        assert response.status_code == 400


# ================================================================
# TESTS : TOP PRODUITS
# ================================================================

class TestTopProduits:
    """Tests de l'endpoint /kpi/produits/top"""

    def test_top_produits_returns_200(self, mock_get_dataframe):
        response = client.get("/kpi/produits/top")
        assert response.status_code == 200

    def test_top_produits_est_une_liste(self, mock_get_dataframe):
        response = client.get("/kpi/produits/top")
        assert isinstance(response.json(), list)

    def test_top_produits_limite(self, mock_get_dataframe):
        """La limite doit être respectée"""
        response = client.get("/kpi/produits/top?limite=2")
        assert len(response.json()) <= 2

    def test_top_produits_structure(self, mock_get_dataframe):
        """Chaque produit doit avoir les bons champs"""
        response = client.get("/kpi/produits/top")
        produits = response.json()
        if produits:
            produit = produits[0]
            assert 'produit' in produit
            assert 'categorie' in produit
            assert 'ca' in produit
            assert 'profit' in produit
            assert 'quantite' in produit

    def test_top_produits_tri_par_profit(self, mock_get_dataframe):
        """Le tri par profit doit retourner le produit le plus profitable en premier"""
        response = client.get("/kpi/produits/top?tri_par=profit")
        produits = response.json()
        if len(produits) > 1:
            assert produits[0]['profit'] >= produits[1]['profit']

    def test_top_produits_tri_invalide(self, mock_get_dataframe):
        """Un critère de tri invalide doit retourner une erreur"""
        response = client.get("/kpi/produits/top?tri_par=invalide")
        assert response.status_code == 422


# ================================================================
# TESTS : CATÉGORIES
# ================================================================

class TestCategories:
    """Tests de l'endpoint /kpi/categories"""

    def test_categories_returns_200(self, mock_get_dataframe):
        response = client.get("/kpi/categories")
        assert response.status_code == 200

    def test_categories_est_une_liste(self, mock_get_dataframe):
        response = client.get("/kpi/categories")
        assert isinstance(response.json(), list)

    def test_categories_contient_les_3_categories(self, mock_get_dataframe):
        """Le dataset de test contient 3 catégories"""
        response = client.get("/kpi/categories")
        assert len(response.json()) == 3

    def test_categories_structure(self, mock_get_dataframe):
        response = client.get("/kpi/categories")
        cat = response.json()[0]
        assert 'categorie' in cat
        assert 'ca' in cat
        assert 'profit' in cat
        assert 'marge_pct' in cat
        assert 'nb_commandes' in cat

    def test_categories_marge_calcul(self, mock_get_dataframe):
        """La marge doit être calculée correctement (profit/ca * 100)"""
        response = client.get("/kpi/categories")
        categories = response.json()
        for cat in categories:
            if cat['ca'] > 0:
                marge_attendue = round(cat['profit'] / cat['ca'] * 100, 2)
                assert cat['marge_pct'] == pytest.approx(marge_attendue, abs=0.1)


# ================================================================
# TESTS : TEMPOREL
# ================================================================

class TestTemporel:
    """Tests de l'endpoint /kpi/temporel"""

    def test_temporel_par_mois_returns_200(self, mock_get_dataframe):
        response = client.get("/kpi/temporel?periode=mois")
        assert response.status_code == 200

    def test_temporel_par_annee(self, mock_get_dataframe):
        response = client.get("/kpi/temporel?periode=annee")
        assert response.status_code == 200

    def test_temporel_tri_chronologique(self, mock_get_dataframe):
        """Les périodes doivent être triées chronologiquement"""
        response = client.get("/kpi/temporel?periode=mois")
        data = response.json()
        periodes = [d['periode'] for d in data]
        assert periodes == sorted(periodes)

    def test_temporel_periode_invalide(self, mock_get_dataframe):
        """Une granularité invalide doit retourner une erreur"""
        response = client.get("/kpi/temporel?periode=semaine")
        assert response.status_code == 422


# ================================================================
# TESTS : GÉOGRAPHIQUE
# ================================================================

class TestGeographique:
    """Tests de l'endpoint /kpi/geographique"""

    def test_geographique_returns_200(self, mock_get_dataframe):
        response = client.get("/kpi/geographique")
        assert response.status_code == 200

    def test_geographique_structure(self, mock_get_dataframe):
        response = client.get("/kpi/geographique")
        data = response.json()[0]
        assert 'region' in data
        assert 'ca' in data
        assert 'profit' in data
        assert 'nb_clients' in data
        assert 'nb_commandes' in data

    def test_geographique_toutes_regions_presentes(self, mock_get_dataframe):
        """Les 3 régions du dataset de test doivent être présentes"""
        response = client.get("/kpi/geographique")
        regions = [r['region'] for r in response.json()]
        assert 'East' in regions
        assert 'West' in regions
        assert 'Central' in regions


# ================================================================
# TESTS : CLIENTS
# ================================================================

class TestClients:
    """Tests de l'endpoint /kpi/clients"""

    def test_clients_returns_200(self, mock_get_dataframe):
        response = client.get("/kpi/clients")
        assert response.status_code == 200

    def test_clients_structure(self, mock_get_dataframe):
        response = client.get("/kpi/clients")
        data = response.json()
        assert 'top_clients' in data
        assert 'recurrence' in data
        assert 'segments' in data

    def test_clients_recurrence_coherente(self, mock_get_dataframe):
        """Le total clients doit être cohérent"""
        response = client.get("/kpi/clients")
        rec = response.json()['recurrence']
        assert rec['total_clients'] == rec['clients_1_achat'] + rec['clients_recurrents']

    def test_clients_limite(self, mock_get_dataframe):
        """La limite de top clients doit être respectée"""
        response = client.get("/kpi/clients?limite=2")
        data = response.json()
        assert len(data['top_clients']) <= 2


# ================================================================
# TESTS : RENTABILITÉ
# ================================================================

class TestRentabilite:
    """Tests des endpoints de rentabilité"""

    def test_rentabilite_globale_returns_200(self, mock_get_dataframe):
        response = client.get("/kpi/rentabilite/globale")
        assert response.status_code == 200

    def test_rentabilite_globale_structure(self, mock_get_dataframe):
        response = client.get("/kpi/rentabilite/globale")
        data = response.json()
        assert 'marge_globale' in data
        assert 'profit_total' in data
        assert 'est_sante' in data
        assert 'message' in data

    def test_produits_perte_returns_200(self, mock_get_dataframe):
        response = client.get("/kpi/rentabilite/pertes")
        assert response.status_code == 200

    def test_produits_perte_negatifs(self, mock_get_dataframe):
        """Tous les produits retournés doivent avoir un profit négatif"""
        response = client.get("/kpi/rentabilite/pertes")
        pertes = response.json()
        for p in pertes:
            assert p['perte_montant'] < 0, f"{p['produit']} n'est pas en perte"

    def test_impact_remises_returns_200(self, mock_get_dataframe):
        response = client.get("/kpi/rentabilite/remises")
        assert response.status_code == 200

    def test_rentabilite_categories_returns_200(self, mock_get_dataframe):
        response = client.get("/kpi/rentabilite/categories")
        assert response.status_code == 200

    def test_tendance_rentabilite_returns_200(self, mock_get_dataframe):
        response = client.get("/kpi/rentabilite/tendance")
        assert response.status_code == 200

    def test_tendance_triee_chronologiquement(self, mock_get_dataframe):
        """La tendance doit être triée par période"""
        response = client.get("/kpi/rentabilite/tendance")
        data = response.json()
        periodes = [d['periode'] for d in data]
        assert periodes == sorted(periodes)


# ================================================================
# TESTS : COMPARAISONS TEMPORELLES
# ================================================================

class TestComparaisons:
    """Tests des endpoints de comparaison"""

    def test_comparaison_annuelle_returns_200(self, mock_get_dataframe):
        response = client.get("/kpi/comparaison/annuel?annee_reference=2022&annee_comparaison=2023")
        assert response.status_code == 200

    def test_comparaison_annuelle_structure(self, mock_get_dataframe):
        response = client.get("/kpi/comparaison/annuel?annee_reference=2022&annee_comparaison=2023")
        data = response.json()
        assert 'ca_reference' in data
        assert 'ca_comparaison' in data
        assert 'variation_ca_pct' in data
        assert 'message' in data

    def test_saisonnalite_returns_200(self, mock_get_dataframe):
        response = client.get("/kpi/saisonnalite")
        assert response.status_code == 200

    def test_saisonnalite_12_mois_max(self, mock_get_dataframe):
        """Il ne peut pas y avoir plus de 12 mois"""
        response = client.get("/kpi/saisonnalite")
        data = response.json()
        assert len(data['saisonnalite']) <= 12

    def test_produits_declin_returns_200(self, mock_get_dataframe):
        response = client.get("/kpi/produits/declin")
        assert response.status_code == 200


# ================================================================
# TESTS : FILTRES
# ================================================================

class TestFiltres:
    """Tests de l'endpoint /filters/valeurs"""

    def test_filtres_returns_200(self, mock_get_dataframe):
        response = client.get("/filters/valeurs")
        assert response.status_code == 200

    def test_filtres_contient_categories(self, mock_get_dataframe):
        response = client.get("/filters/valeurs")
        data = response.json()
        assert 'categories' in data
        assert 'regions' in data
        assert 'segments' in data
        assert 'plage_dates' in data

    def test_filtres_plage_dates(self, mock_get_dataframe):
        response = client.get("/filters/valeurs")
        plage = response.json()['plage_dates']
        assert 'min' in plage
        assert 'max' in plage


# ================================================================
# TESTS : DASHBOARD RÉSUMÉ
# ================================================================

class TestDashboardResume:
    """Tests de l'endpoint /kpi/dashboard/resume"""

    def test_resume_returns_200(self, mock_get_dataframe):
        response = client.get("/kpi/dashboard/resume")
        assert response.status_code == 200

    def test_resume_structure(self, mock_get_dataframe):
        response = client.get("/kpi/dashboard/resume")
        data = response.json()
        assert 'performance_globale' in data
        assert 'categories' in data
        assert 'alertes' in data
        assert 'message' in data
        assert 'recommandations' in data

    def test_resume_recommandations_est_liste(self, mock_get_dataframe):
        response = client.get("/kpi/dashboard/resume")
        data = response.json()
        assert isinstance(data['recommandations'], list)
        assert len(data['recommandations']) > 0


# ================================================================
# TESTS : DONNÉES BRUTES
# ================================================================

class TestDonneesBrutes:
    """Tests de l'endpoint /data/commandes"""

    def test_commandes_returns_200(self, mock_get_dataframe):
        response = client.get("/data/commandes")
        assert response.status_code == 200

    def test_commandes_pagination(self, mock_get_dataframe):
        response = client.get("/data/commandes?limite=2&offset=0")
        data = response.json()
        assert data['nb_retourne'] <= 2
        assert 'total' in data

    def test_commandes_offset_trop_grand(self, mock_get_dataframe):
        """Un offset supérieur au total doit retourner 400"""
        response = client.get("/data/commandes?offset=99999")
        assert response.status_code == 400