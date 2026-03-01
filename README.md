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



st.markdown("---")
st.header("📖 Data Storytelling : Ce que les chiffres nous racontent")

with st.expander("Message principal – Un CA solide mais une rentabilité très inégale", expanded=True):
    st.markdown(f"""
    **Chiffre d'affaires global : ~2 297 200 €** sur la période 2015-2018, avec **5 009 commandes** et **793 clients**.  
    **Profit total : ~286 397 €** → marge moyenne **12,47 %** → acceptable mais fragile.

    **Forces observées** :
    - **Technology** domine clairement : CA le plus élevé (~836 k€ dans le tableau catégories), profit massif (~145 k€), marge excellente **17,4 %**.
      Produits phares comme **Canon imageCLASS 2200 Advanced Copier** (CA 61,6 k€ + profit 25,2 k€) ou **HP LaserJet** tirent l'activité vers le haut.
    - **Office Supplies** reste rentable (marge **17,04 %**, profit ~122 k€) malgré un CA légèrement inférieur.
    - Fidélité clients très forte : **98,5 %** de clients récurrents, **6,32 commandes par client** en moyenne.

    **Faiblesses / points d'attention critiques** :
    - **Furniture** est le gros problème : CA important (~742 k€) mais profit ridicule **~18,5 k€ seulement** → marge **2,49 %** (la plus basse de loin).
      Certains meubles (ex. HON Task Chairs) génèrent du CA sans profit net, et d'autres tirent la marge vers le bas.
    - **Région Central** sous-performe nettement : CA le plus faible (~502 k€), profit très impacté (souvent proche de zéro ou négatif sur Furniture).
    - Évolution temporelle : pics saisonniers marqués (fin d'année / Q4), mais plusieurs mois avec **profit négatif** malgré CA positif → signe de remises ou coûts mal maîtrisés.
    """)

    st.warning("⚠️ Risque majeur : Sans correction sur Furniture et Central, la marge globale risque de continuer à fondre malgré la croissance du CA.")

with st.expander("Opportunités business identifiées", expanded=False):
    st.markdown("""
    - **Booster Technology** : catégorie la plus rentable → investir en stock, marketing ciblé, bundles (ex. associer copieurs Canon + accessoires Office Supplies).
    - **Réduire la pression remises sur Furniture** : limiter à 10-15 % max pour éviter les ventes à perte. Potentiel gain marge rapide.
    - **Région West & East** : déjà leaders (CA 678-725 k€) → consolider avec offres Corporate (segment plus rentable par commande).
    - **Segment Corporate & Home Office** : meilleur ratio profit/CA que Consumer → campagnes B2B ciblées pour augmenter leur part.
    - **Top clients** (Sean Miller, Tamara Chand, etc.) : les chouchouter avec offres personnalisées pour maximiser la récurrence déjà élevée.
    """)

    st.success("✅ Opportunité n°1 : Réallouer 20-30 % du budget promo de Furniture vers Technology → impact marge potentiel +3 à 5 % en 12 mois.")

with st.expander("Évolution temporelle – Saisonnalité et alertes", expanded=False):
    st.markdown("""
    Les graphiques montrent une croissance globale du CA, avec des **pics très forts fin d'année** (souvent >20-30 k€/jour en Q4).  
    Mais le profit est beaucoup plus volatile : plusieurs creux négatifs même quand le CA reste positif.

    **Explication probable** : remises agressives en période creuse + coûts fixes/logistiques qui ne suivent pas.  
    **Action recommandée** : anticiper les pics (pré-stock Technology) et éviter les promos destructrices en inter-saison.
    """)



    # Pour rendre le story stelling dynamique , il faut integrer de l' IA (prumpt) avec l'API groq

