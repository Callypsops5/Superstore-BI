# 🛒 Superstore BI - API FastAPI + Dashboard Streamlit

Système complet d'analyse Business Intelligence du dataset **Sample Superstore** avec API REST et dashboard interactif.

## 🎯 Objectifs pédagogiques

Ce projet permet d'apprendre :
- ✅ Développement d'une **API REST** avec FastAPI
- ✅ Création de **dashboards interactifs** avec Streamlit/Plotly
- ✅ Analyse de données avec **Pandas**
- ✅ Calcul de **KPI e-commerce**
- ✅ Tests unitaires avec **pytest**

---

## 📊 KPI implémentés

### 🔹 KPI Globaux
- 💰 Chiffre d'affaires total
- 🧾 Nombre de commandes
- 👤 Nombre de clients uniques
- 🛒 Panier moyen
- 📦 Quantité vendue
- 💵 Profit total
- 📈 Marge moyenne

### 🔹 KPI Produits
- 🏆 Top 10 produits par CA/Profit/Quantité
- 📦 CA par catégorie
- 💹 Marge par produit
- ⚠️ Produits les moins rentables

### 🔹 KPI Clients
- 💎 Top clients par CA
- 🔄 Clients récurrents vs nouveaux
- 📊 Fréquence d'achat
- 💼 Performance par segment

### 🔹 KPI Temporels
- 📅 Évolution du CA par jour/mois/année
- 📈 Comparaison des périodes
- 🌡️ Saisonnalité

### 🔹 KPI Géographiques
- 🌍 CA par région
- 📍 Nombre de clients par zone

---

## 📁 Structure du projet

```
superstore-bi/
│
├── backend/
│   └── main.py              # API FastAPI (endpoints KPI)
│
├── frontend/
│   └── dashboard.py         # Dashboard Streamlit
│
├── tests/
│   └── test_api.py          # Tests unitaires
│
├── requirements.txt         # Dépendances Python
└── README.md                # Ce fichier
```

---

## 🚀 Installation et démarrage

### 1️⃣ Prérequis

- Python 3.8+ installé
- pip installé

### 2️⃣ Installation des dépendances

```bash
# Cloner ou créer le projet
mkdir superstore-bi
cd superstore-bi

# Installer les dépendances
pip install -r requirements.txt
```

### 3️⃣ Démarrer l'API FastAPI

```bash
# Dans un premier terminal
python backend/main.py
```

✅ L'API sera accessible sur **http://localhost:8000**
📚 Documentation Swagger : **http://localhost:8000/docs**

### 4️⃣ Démarrer le Dashboard Streamlit

```bash
# Dans un second terminal
streamlit run frontend/dashboard.py
```

✅ Le dashboard sera accessible sur **http://localhost:8501**



---

## 📖 Utilisation de l'API

### Exemples de requêtes

#### **1. KPI globaux**
```bash
# Sans filtre
curl http://localhost:8000/kpi/globaux

# Avec filtres
curl "http://localhost:8000/kpi/globaux?date_debut=2015-01-01&categorie=Technology"
```

**Réponse** :
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

#### **2. Top produits**
```bash
# Top 10 par CA
curl http://localhost:8000/kpi/produits/top

# Top 5 par profit
curl "http://localhost:8000/kpi/produits/top?limite=5&tri_par=profit"
```

#### **3. Performance catégories**
```bash
curl http://localhost:8000/kpi/categories
```

#### **4. Évolution temporelle**
```bash
# Par mois
curl "http://localhost:8000/kpi/temporel?periode=mois"

# Par année
curl "http://localhost:8000/kpi/temporel?periode=annee"
```

#### **5. Performance géographique**
```bash
curl http://localhost:8000/kpi/geographique
```

#### **6. Analyse clients**
```bash
curl "http://localhost:8000/kpi/clients?limite=10"
```

---

## 🎨 Fonctionnalités du Dashboard

### ✅ Filtres interactifs
- 📅 Plage de dates
- 📦 Catégorie
- 🌍 Région
- 👥 Segment client

### ✅ Visualisations Plotly
- 📊 Graphiques en barres interactifs
- 📈 Courbes d'évolution temporelle
- 🥧 Graphiques circulaires
- 📉 Graphiques combinés

### ✅ KPI Cards
- Affichage en temps réel
- Mise en forme automatique (€, %, nombres)
- Organisation claire

### ✅ Tabs organisés
- 🏆 Produits
- 📦 Catégories
- 📅 Temporel
- 🌍 Géographique

---

## 🗃️ Dataset utilisé

**Source** : [Sample Superstore sur GitHub](https://github.com/leonism/sample-superstore)

**Colonnes principales** :
- `Order ID` : Identifiant de commande
- `Order Date` : Date de commande
- `Customer ID` : Identifiant client
- `Product Name` : Nom du produit
- `Category` / `Sub-Category` : Catégorie
- `Sales` : Chiffre d'affaires
- `Quantity` : Quantité
- `Discount` : Remise
- `Profit` : Profit
- `Region` : Région géographique

**Période** : 2014-2017
**Taille** : ~10 000 lignes

---

📖 Data Storytelling : Ce que révèlent les données
🎯 Message principal
Le dataset Superstore montre un chiffre d’affaires solide (~2,29 M€) sur 2015–2018, avec 5 009 commandes et 793 clients.
Cependant, la rentabilité est très inégale selon les catégories, les régions et les périodes.

💪 Forces observées
Technology domine largement :

CA le plus élevé (~836 k€)

Profit massif (~145 k€)

Marge excellente (17,4 %)

Produits phares : Canon imageCLASS 2200, HP LaserJet, etc.

Office Supplies reste très rentable (marge 17,04 %, profit ~122 k€).

Fidélité clients exceptionnelle :

98,5 % de clients récurrents

6,32 commandes par client en moyenne

⚠️ Faiblesses critiques
Furniture est le principal problème :

CA élevé (~742 k€)

Profit très faible (~18,5 k€)

Marge catastrophique (2,49 %)

Plusieurs produits vendus à perte

Région Central sous-performe fortement :

CA le plus faible (~502 k€)

Profit souvent proche de zéro ou négatif sur Furniture

Saisonnalité marquée :

Pics en fin d’année

Plusieurs mois avec profit négatif malgré un CA positif

Indice de remises trop agressives ou coûts mal maîtrisés

🚀 Opportunités business
Renforcer Technology : stock, marketing, bundles (ex. copieurs + fournitures).

Réduire les remises sur Furniture : limiter à 10–15 % pour éviter les ventes à perte.

Capitaliser sur West & East : régions les plus dynamiques.

Cibler Corporate & Home Office : segments plus rentables que Consumer.

Valoriser les top clients (ex. Sean Miller, Tamara Chand) via offres personnalisées.

📅 Analyse temporelle
Forte croissance du CA en fin d’année (Q4).

Profit très volatil : plusieurs creux négatifs.

Recommandation :

anticiper les pics (pré‑stock Technology)

éviter les remises destructrices en inter‑saison

---

## 🎓 Exercices pour les élèves

### **Atelier 1 - KPI de base** (30 min)
1. Calculer le CA total
2. Calculer le panier moyen
3. Afficher le CA par mois
4. Trouver le top 5 des produits

### **Atelier 2 - Analyse business** (45 min)
1. Quelle catégorie est la plus rentable ?
2. Quels produits génèrent du CA mais peu de profit ?
3. Quels mois sont les plus performants ?
4. Quelle région a le plus de clients ?

### **Atelier 3 - Dashboard final** (60 min)
1. Créer un dashboard avec :
   - 1 KPI principal
   - 2 graphiques de votre choix
   - 1 tableau filtrable
   - Filtres : date, catégorie, région

---

## 🔧 Personnalisation

### Ajouter un nouveau KPI

**1. Dans l'API (`backend/main.py`)** :
```python
@app.get("/kpi/mon_nouveau_kpi", tags=["KPI"])
def get_mon_nouveau_kpi():
    # Votre calcul ici
    resultat = df.groupby('colonne').sum()
    return resultat.to_dict('records')
```

**2. Dans le dashboard (`frontend/dashboard.py`)** :
```python
# Appeler l'API
data = appeler_api("/kpi/mon_nouveau_kpi")

# Créer la visualisation
fig = px.bar(data, x='colonne', y='valeur')
st.plotly_chart(fig)
```

---

## 🐛 Résolution de problèmes

### ❌ Erreur "Connection refused"
➡️ Vérifiez que l'API est démarrée : `python backend/main.py`

### ❌ Erreur "Module not found"
➡️ Installez les dépendances : `pip install -r requirements.txt`

### ❌ Dashboard vide
➡️ Vérifiez l'URL de l'API dans `dashboard.py` (ligne 41)

### ❌ Erreur de chargement du dataset
➡️ Vérifiez votre connexion internet (le CSV est téléchargé depuis GitHub)

---

## 📚 Documentation complète

### **FastAPI**
- [Documentation officielle](https://fastapi.tiangolo.com/)
- [Tutoriels](https://fastapi.tiangolo.com/tutorial/)

### **Streamlit**
- [Documentation officielle](https://docs.streamlit.io/)
- [Galerie d'exemples](https://streamlit.io/gallery)

### **Plotly**
- [Documentation Python](https://plotly.com/python/)
- [Galerie de graphiques](https://plotly.com/python/basic-charts/)

### **Pandas**
- [Documentation officielle](https://pandas.pydata.org/docs/)
- [10 minutes to pandas](https://pandas.pydata.org/docs/user_guide/10min.html)

---
