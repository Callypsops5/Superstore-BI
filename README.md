# 🛒 Superstore BI — API FastAPI & Tableau de bord Streamlit

Un système complet de **Business Intelligence** construit autour du jeu de données *Sample Superstore*.
Le projet comprend une **API REST développée avec FastAPI** ainsi qu’un **tableau de bord interactif Streamlit** intégrant analyse et narration des données.

---

## 🎯 Objectifs pédagogiques

* Construire une **API REST** avec FastAPI
* Créer des **tableaux de bord interactifs** avec Streamlit et Plotly
* Réaliser des analyses de données avec **Pandas**
* Calculer des **KPI e-commerce** courants
* Écrire et exécuter des **tests unitaires** avec pytest

---

## 📁 Structure du projet

```
superstore-bi/
├── backend/              # Application FastAPI
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── frontend/             # Tableau de bord Streamlit
│   ├── Dockerfile
│   ├── dashboard.py
│   └── requirements.txt
├── tests/                # Tests pytest
│   └── test_api.py
├── docker-compose.yml    # Exécution via Docker (optionnel)
├── requirements.txt      # Dépendances globales
└── README.md
```

> Chaque sous-dossier possède son propre `requirements.txt` afin de permettre des installations isolées si nécessaire.

---

## 🚀 Démarrage rapide

### Prérequis

* Python 3.8 ou supérieur
* pip (ou un gestionnaire de paquets Python équivalent)
* Docker & Docker Compose (optionnel)

---

### Installation locale (Python)

```bash
git clone <repo-url> superstore-bi
cd superstore-bi
pip install -r requirements.txt
```

---

### Lancer l’API

```bash
# terminal 1
python backend/main.py
```

* API : `http://localhost:8000`
* Documentation Swagger : `http://localhost:8000/docs`
* Vérification santé : `http://localhost:8000/health`

---

### Lancer le tableau de bord

```bash
# terminal 2
streamlit run frontend/dashboard.py
```

* Dashboard : `http://localhost:8501`

Vous pouvez modifier l’URL de l’API utilisée par le dashboard via la variable d’environnement :

```
API_URL
```

---

### Exécution avec Docker

```bash
docker-compose up --build
```

* Backend : `http://localhost:8000`
* Frontend : `http://localhost:8501`

Les conteneurs communiquent via un réseau interne Docker ; le dashboard contacte automatiquement l’API (`API_URL=http://backend:8000`).

---

## 📊 Endpoints disponibles

### KPI principaux

| Endpoint                | Description                                                           |
| ----------------------- | --------------------------------------------------------------------- |
| `GET /kpi/globaux`      | Chiffre d’affaires, commandes, clients, panier moyen, profit et marge |
| `GET /kpi/produits/top` | Produits les plus performants                                         |
| `GET /kpi/categories`   | Performance par catégorie                                             |
| `GET /kpi/temporel`     | Série temporelle ventes/profits                                       |
| `GET /kpi/geographique` | Performance par région                                                |
| `GET /kpi/clients`      | Analyse clients et segments                                           |

---

### Rentabilité

| Endpoint                          | Description                              |
| --------------------------------- | ---------------------------------------- |
| `GET /kpi/rentabilite/globale`    | Marge globale avec seuil de santé (12 %) |
| `GET /kpi/rentabilite/pertes`     | Produits vendus à perte                  |
| `GET /kpi/rentabilite/remises`    | Impact des remises                       |
| `GET /kpi/rentabilite/categories` | Marge par catégorie                      |
| `GET /kpi/rentabilite/tendance`   | Évolution mensuelle de la marge          |

---

### Comparaisons & saisonnalité

| Endpoint                      | Description                       |
| ----------------------------- | --------------------------------- |
| `GET /kpi/comparaison/annuel` | Comparaison annuelle              |
| `GET /kpi/saisonnalite`       | Tendances mensuelles              |
| `GET /kpi/produits/declin`    | Produits en baisse de performance |

---

### Endpoints utilitaires

| Endpoint                    | Description                             |
| --------------------------- | --------------------------------------- |
| `GET /kpi/dashboard/resume` | Synthèse exécutive avec recommandations |
| `GET /filters/valeurs`      | Valeurs disponibles pour les filtres    |
| `GET /data/commandes`       | Données brutes paginées                 |
| `GET /health`               | État de l’API                           |

---

## 📖 Exemples de requêtes

```bash
curl http://localhost:8000/kpi/globaux
curl "http://localhost:8000/kpi/globaux?categorie=Technology"
curl "http://localhost:8000/kpi/produits/top?limite=5&tri_par=profit"
curl "http://localhost:8000/kpi/temporel?periode=mois"
curl http://localhost:8000/kpi/rentabilite/pertes
curl http://localhost:8000/kpi/dashboard/resume
```

### Exemple de réponse `/kpi/globaux`

```json
{
  "ca_total": 2297200.86,
  "nb_commandes": 5009,
  "nb_clients": 793,
  "panier_moyen": 458.58,
  "quantite_vendue": 37873,
  "profit_total": 286397.02,
  "marge_moyenne": 12.47
}
```

---

## 🎨 Sections du tableau de bord

| Section            | Contenu                              |
| ------------------ | ------------------------------------ |
| 📊 KPI globaux     | Indicateurs clés dynamiques          |
| 🏆 Produits        | Classements interactifs              |
| 📦 Catégories      | Analyse ventes vs profit             |
| 📅 Temporel        | Évolution dans le temps              |
| 🌍 Géographique    | Performance par région               |
| 👥 Clients         | Fidélité et segmentation             |
| 💰 Rentabilité     | Analyse des marges                   |
| 📅 Comparaisons    | Analyses annuelles et saisonnières   |
| 📋 Résumé exécutif | Synthèse stratégique                 |
| 🧠 Synthèse        | Analyse narrative et recommandations |

---

## 🧪 Exécuter les tests

```bash
pytest tests/test_api.py -v
```

Les tests simulent le dataset et couvrent l’ensemble des endpoints.

---

## 🗃️ Dataset

* **Source :** Sample Superstore (GitHub)
* **Période :** 2014–2017
* **Volume :** ~10 000 lignes

Colonnes principales : `Order ID`, `Order Date`, `Customer ID`, `Product Name`, `Category`, `Sales`, `Quantity`, `Discount`, `Profit`, `Region`.

---

## 🐛 Dépannage

| Problème             | Solution                       |
| -------------------- | ------------------------------ |
| `Connection refused` | Vérifier que l’API est lancée  |
| `Module not found`   | Installer les dépendances      |
| Dashboard vide       | Vérifier `API_URL`             |
| Erreur dataset       | Vérifier la connexion Internet |
| Comparaison vide     | Années hors plage 2014–2017    |

---

## 🔧 Ajouter un nouveau KPI

Le projet est facilement extensible.

### Étape 1 — Backend (`main.py`)

```python
@app.get("/kpi/mon_kpi")
def get_mon_kpi():
    df = get_dataframe()
    resultat = df.groupby("category")["sales"].sum()
    return resultat.to_dict()
```

### Étape 2 — Frontend (`dashboard.py`)

```python
data = appeler_api("/kpi/mon_kpi")
fig = px.bar(...)
st.plotly_chart(fig, use_container_width=True)
```

---

## 📚 Ressources

* FastAPI — [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
* Streamlit — [https://docs.streamlit.io/](https://docs.streamlit.io/)
* Plotly — [https://plotly.com/python/](https://plotly.com/python/)
* Pandas — [https://pandas.pydata.org/docs/](https://pandas.pydata.org/docs/)

---
