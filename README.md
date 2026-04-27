# 🏠 ImmoAI — Application Desktop de Prédiction Immobilière

> **Plateforme intelligente d'estimation de prix immobiliers propulsée par le Machine Learning**

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![PySide6](https://img.shields.io/badge/PySide6-6.6+-green?logo=qt)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-orange?logo=scikit-learn)
![MySQL](https://img.shields.io/badge/MySQL-XAMPP-blue?logo=mysql)
![License](https://img.shields.io/badge/License-Educational-purple)

---

## 📋 Description du projet

**ImmoAI** est une application desktop professionnelle développée dans le cadre du module de **Gestion de Projet** à l'**ISTA NTIC SYBA** (Formation Intelligence Artificielle, 2025/2026).

Elle permet à des agents immobiliers et particuliers d'**estimer précisément le prix d'un bien immobilier** grâce à des modèles de Machine Learning entraînés sur des données réelles, avec une interface graphique moderne et intuitive.

---

## ✨ Fonctionnalités principales

### 🔐 Authentification & Sécurité
- Connexion / Inscription avec validation robuste
- Hachage des mots de passe avec **bcrypt**
- Gestion des rôles : `USER` et `ADMIN`
- Session management avec déconnexion sécurisée
- Protection contre les injections SQL via **SQLAlchemy ORM**

### 🤖 Prédiction de prix (Page principale)
- **6 modèles ML disponibles** :
  - ⚡ Régression Linéaire (rapide)
  - 🔍 Ridge Regression
  - 🔎 KNN (moyen)
  - 🌲 Arbre de Décision
  - 🌳 Random Forest (recommandé)
  - 🚀 Gradient Boosting (expert)
- Sélection du modèle par l'utilisateur (boutons radio)
- Upload de photo du bien
- Affichage du prix estimé dans un encart visuel coloré
- Message explicatif selon la gamme de prix
- Confirmation et sauvegarde en base de données

### 📋 Historique
- Tableau paginé de toutes les prédictions
- Filtrage et tri
- 15 éléments par page

### 🏢 Annonces immobilières
- Création d'annonces **Vente / Achat**
- Upload d'image de l'annonce
- Cartes visuelles modernes
- Recherche par titre / ville
- Filtres par type
- Validation admin avant publication

### 💬 Messagerie
- Envoi de messages à l'administrateur
- Affichage des réponses en temps réel
- Indicateur de statut (envoyé / lu / répondu)

### 👤 Profil
- Modification du nom et de la photo de profil
- Changement de mot de passe sécurisé
- Statistiques personnelles (nb prédictions, date d'inscription)

### ⚙️ Paramètres
- Thème **Clair / Sombre** (appliqué instantanément)
- Langue **Français / Anglais** (i18n complet)

---

## 🎛️ Interface Administrateur

### 📊 Tableau de bord
- Statistiques globales (utilisateurs, prédictions, annonces, messages)
- Alertes : annonces en attente, messages non lus
- Tableau des derniers inscrits

### 👥 Gestion des utilisateurs (CRUD complet)
- Liste de tous les utilisateurs avec recherche
- Créer / Modifier / Activer-Désactiver / Supprimer
- Attribution des rôles (user/admin)

### 🤖 Supervision des prédictions
- Vue de toutes les prédictions avec utilisateur associé

### 🏢 Modération des annonces
- Approuver / Rejeter les annonces en attente
- Filtrage par statut

### 💬 Gestion des messages
- Lecture des messages utilisateurs
- Réponse directe depuis l'interface
- Marquage comme lu

### 🧠 Gestion des modèles ML
- Déclenchement de l'entraînement depuis l'interface
- Barre de progression en temps réel
- Tableau comparatif des performances (R², MAE, RMSE)
- Affichage du meilleur modèle automatiquement

---

## 🧠 Machine Learning

### Modèles implémentés
| Modèle | Type | Cas d'usage |
|--------|------|-------------|
| Linear Regression | Régression | Rapide, interprétable |
| Ridge Regression | Régression régularisée | Évite le surapprentissage |
| KNN | Instance-based | Données locales similaires |
| Decision Tree | Arbre de décision | Règles explicites |
| Random Forest | Ensemble | Haute précision |
| Gradient Boosting | Boosting | Meilleure performance |

### Pipeline ML
```
1. Chargement données (housing.csv)
2. Nettoyage & imputation
3. Feature Engineering :
   - Encodage localisation (LabelEncoder)
   - Encodage état du bien
   - Calcul de l'âge du bien (2024 - année)
   - Encodage variables binaires (oui/non)
4. StandardScaler
5. Train/Test Split (80/20)
6. Entraînement des 6 modèles
7. Évaluation : R², MAE, RMSE
8. Sélection automatique du meilleur modèle
9. Sauvegarde .pkl (joblib)
```

### Métriques d'évaluation
- **R² Score** : Coefficient de détermination
- **MAE** : Mean Absolute Error (erreur absolue moyenne)
- **RMSE** : Root Mean Squared Error

---

## 🗄️ Base de données (MySQL)

### Tables
```sql
users         -- Comptes utilisateurs (id, email, password_hash, role, image, ...)
predictions   -- Prédictions effectuées (surface, chambres, localisation, prix, modèle, ...)
annonces      -- Annonces vente/achat (titre, prix, localisation, image, statut, ...)
messages      -- Messages utilisateur→admin avec réponse
ml_models     -- Performances des modèles entraînés
```

### Compte admin par défaut
```
Email    : admin@realestate.ai
Password : Admin2025!
```

---

## 🏗️ Architecture réelle du projet

```
Projet_gp_ML/
│
├── logo.png                        # Logo de l'application
├── main.py                         # Point d'entrée principal
├── __init__.py
├── .gitignore
├── README.md
├── requirements.txt
│
├── app/
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── page_admin.py           # Interface administrateur
│   │   ├── page_dashboard.py       # Tableau de bord utilisateur
│   │   ├── page_history.py         # Historique des prédictions
│   │   ├── page_home.py            # Page d'accueil publique
│   │   ├── page_login.py           # Connexion
│   │   ├── page_messages.py        # Messagerie
│   │   ├── page_model_info.py      # Informations sur les modèles ML
│   │   ├── page_predict.py         # Prédiction de prix
│   │   ├── page_profile.py         # Profil utilisateur
│   │   ├── page_properties.py      # Annonces immobilières
│   │   ├── page_register.py        # Inscription
│   │   └── page_settings.py        # Paramètres (thème, langue)
│   │
│   └── widgets/
│       ├── __init__.py
│       └── sidebar.py              # Barre de navigation latérale
│
├── data/
│   └── housing.csv                 # Dataset immobilier (545 biens)
│
├── models/
│   ├── app.db                      # Base SQLite (fallback sans MySQL)
│   ├── best_model.pkl              # Meilleur modèle sélectionné
│   ├── decision_tree_clf.pkl
│   ├── decision_tree_reg.pkl
│   ├── knn_classification.pkl
│   ├── knn_regression.pkl
│   ├── logistic_regression.pkl
│   ├── metadata.json               # Métadonnées des modèles
│   ├── random_forest_clf.pkl
│   ├── random_forest_reg.pkl
│   └── scaler.pkl                  # StandardScaler entraîné
│
└── src/
    ├── __init__.py
    ├── database.py                 # Connexion MySQL + requêtes
    ├── predictor.py                # Chargement et inférence ML
    ├── theme.py                    # Stylesheets clair / sombre
    │   ├── train_model.py          # Entraînement des modèles
    └── translations.py             # la traduction dans la page
    
```

---

## 🚀 Installation et démarrage

### Prérequis
- Python 3.10 ou supérieur
- [XAMPP](https://www.apachefriends.org/) avec MySQL démarré
- Git (optionnel)

### Étape 1 — Cloner ou télécharger le projet
```bash
git clone <url-du-repo>
cd Projet_gp_ML
```

### Étape 2 — Créer un environnement virtuel
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### Étape 3 — Installer les dépendances
```bash
pip install -r requirements.txt
```

### Étape 4 — Démarrer XAMPP
1. Ouvrir XAMPP Control Panel
2. Démarrer **Apache** et **MySQL**
3. La base de données sera créée automatiquement au premier lancement

### Étape 5 — Lancer l'application
```bash
python main.py
```

### Étape 6 — Connexion à la base de données
- **Hôte** : `localhost`
- **Port** : `3306`
- **Utilisateur** : `root`
- **Mot de passe** : (vide par défaut dans XAMPP)
- **Base de données** : `real_estate_ai`

### Étape 7 — Entraîner les modèles ML
Au premier lancement, entraînez les modèles directement :
```bash
python src/train_model.py
```
Les fichiers `.pkl` seront générés automatiquement dans `models/`.

---

## 🖼️ Captures d'écran

```
[ Page d'accueil ]     → Interface bicolore avec présentation
[ Login ]              → Formulaire élégant avec validation
[ Register ]           → Création de compte
[ Dashboard User ]     → Statistiques personnelles + actions rapides
[ Prediction ]         → Formulaire complet + résultat animé
[ Historique ]         → Tableau paginé des prédictions
[ Annonces ]           → Cartes immobilières avec filtres
[ Messages ]           → Messagerie avec admin
[ Profil ]             → Modification des informations
[ Paramètres ]         → Thème + langue
[ Admin Dashboard ]    → Vue globale de la plateforme
[ Admin Users ]        → CRUD complet des utilisateurs
[ Admin Annonces ]     → Modération des annonces
[ Admin Messages ]     → Réponse aux utilisateurs
[ Admin Models ]       → Entraînement + comparaison des modèles
```

---

## 🛠️ Technologies utilisées

| Technologie | Version | Usage |
|-------------|---------|-------|
| Python | 3.10+ | Langage principal |
| PySide6 | 6.6+ | Interface graphique Qt |
| MySQL | XAMPP | Base de données principale |
| SQLite | intégré | Fallback sans MySQL |
| scikit-learn | 1.3+ | Modèles Machine Learning |
| pandas | 2.0+ | Traitement des données |
| numpy | 1.24+ | Calcul numérique |
| joblib | 1.3+ | Sauvegarde des modèles (.pkl) |
| bcrypt | 4.0+ | Hachage des mots de passe |

---

## 🔐 Sécurité

- ✅ Hachage bcrypt (salt aléatoire) pour tous les mots de passe
- ✅ Protection contre les injections SQL
- ✅ Validation côté client de tous les champs
- ✅ Vérification des rôles avant accès aux pages admin
- ✅ Session timeout à la déconnexion
- ✅ Données sensibles jamais stockées en clair

---

## 📐 Architecture MVC

```
├── Models    → src/database.py (requêtes MySQL / SQLite)
├── Views     → app/pages/*.py (PySide6 Pages)
├── Widgets   → app/widgets/sidebar.py
├── Services  → src/theme.py · src/predictor.py
└── ML Layer  → src/train_model.py (indépendant de l'UI)
```

---

## 👨‍💻 Auteur & Contexte académique

| Champ | Valeur |
|-------|--------|
| Établissement | ISTA NTIC SYBA |
| Formation | Intelligence Artificielle |
| Module | Gestion de Projet |
| Année | 2025 / 2026 |
| Encadrante | Mme GOUBRAIM NAIMA |
| Groupes | IA101 / IA102 |
| Niveau | Technicien Spécialisé |

---

## 📝 Livrables du projet

- [x] Code source complet et documenté
- [x] Modèles ML entraînés (.pkl)
- [x] Application Desktop fonctionnelle
- [x] Base de données MySQL (schéma + seed)
- [x] README détaillé
- [x] Rapport technique (PDF) — à rédiger
- [x] Présentation PowerPoint — à préparer

---

## 📄 Licence

Projet éducatif — Usage interne à l'ISTA NTIC SYBA.
Toute reproduction à des fins commerciales est interdite.

---

*Développé avec ❤️ et ☕ par le Groupe IA101/IA102 — ISTA NTIC SYBA 2025/2026*