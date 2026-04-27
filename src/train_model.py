"""
=============================================================================
FICHIER : src/train_model.py
RÔLE    : Pipeline ML complet
          1. Chargement & EDA (analyse exploratoire)
          2. Nettoyage & préparation des données
          3. Division train/test (80/20)
          4. Entraînement de 8 modèles (4 régression + 4 classification)
          5. Évaluation complète (R², RMSE, MAE, Accuracy, F1, matrices)
          6. Sélection du meilleur modèle
          7. Sauvegarde (.pkl + metadata.json)

Usage : python src/train_model.py
=============================================================================
"""

import os
import json
import warnings
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use('Agg')  # Pas de display GUI
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import (
    r2_score, mean_squared_error, mean_absolute_error,
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
from sklearn.preprocessing import StandardScaler
import joblib

warnings.filterwarnings('ignore')

# ── Chemins ──────────────────────────────────────────────────────────────────
ROOT       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH  = os.path.join(ROOT, 'data', 'housing.csv')
MODEL_DIR  = os.path.join(ROOT, 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

SEP = "=" * 65


def banner(title: str):
    print(f"\n{SEP}\n  {title}\n{SEP}")


# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 1 : CHARGEMENT & EDA
# ─────────────────────────────────────────────────────────────────────────────
banner("ÉTAPE 1 : CHARGEMENT & ANALYSE EXPLORATOIRE (EDA)")

df = pd.read_csv(DATA_PATH)
print(f"\n  Dataset : {df.shape[0]} lignes × {df.shape[1]} colonnes")
print(f"\n  Colonnes : {list(df.columns)}")
print("\n  Aperçu :")
print(df.head(3).to_string())
print("\n  Statistiques :")
print(df.describe().to_string())
print("\n  Valeurs manquantes :")
print(df.isnull().sum().to_string())
print("\n  Distribution du prix :")
print(f"    Min    : {df['price'].min():>15,.0f}")
print(f"    Max    : {df['price'].max():>15,.0f}")
print(f"    Moyenne: {df['price'].mean():>15,.0f}")
print(f"    Médiane: {df['price'].median():>15,.0f}")
print(f"    Écart-type: {df['price'].std():>12,.0f}")


# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 2 : NETTOYAGE & PRÉPARATION
# ─────────────────────────────────────────────────────────────────────────────
banner("ÉTAPE 2 : NETTOYAGE & PRÉPARATION DES DONNÉES")

df_clean = df.copy()

# Doublons
before = len(df_clean)
df_clean.drop_duplicates(inplace=True)
print(f"\n  Doublons supprimés : {before - len(df_clean)}")

# Encoder les binaires yes/no → 1/0
binary_cols = ['mainroad', 'guestroom', 'basement', 'hotwaterheating', 'airconditioning', 'prefarea']
for col in binary_cols:
    df_clean[col] = df_clean[col].map(
        lambda x: 1 if str(x).strip().lower() in ('yes', '1', 'true') else 0
    ).astype(int)

# Encoder furnishingstatus (ordinal)
furn_map = {'unfurnished': 0, 'semi-furnished': 1, 'furnished': 2}
df_clean['furnishingstatus'] = df_clean['furnishingstatus'].map(
    lambda x: furn_map.get(str(x).strip().lower(), 1)
).astype(int)

print(f"  Dataset nettoyé : {df_clean.shape[0]} lignes × {df_clean.shape[1]} colonnes")

# Features & target
FEATURE_COLS = [
    'area', 'bedrooms', 'bathrooms', 'stories',
    'mainroad', 'guestroom', 'basement', 'hotwaterheating',
    'airconditioning', 'parking', 'prefarea', 'furnishingstatus'
]
X = df_clean[FEATURE_COLS]
y = df_clean['price']

print(f"  Features : {len(FEATURE_COLS)} variables")
print(f"  Target   : 'price' (régression continue)")


# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 3 : DIVISION TRAIN/TEST + SCALER
# ─────────────────────────────────────────────────────────────────────────────
banner("ÉTAPE 3 : DIVISION TRAIN / TEST (80% / 20%)")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"\n  Train : {X_train.shape[0]} échantillons")
print(f"  Test  : {X_test.shape[0]} échantillons")

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

# Classes de prix pour classification
PRICE_BINS   = [0, 4_000_000, 7_000_000, 12_000_000, float('inf')]
PRICE_LABELS = ['Bas', 'Moyen', 'Élevé', 'Très Élevé']
PRICE_VALS   = [0, 1, 2, 3]

y_cls       = pd.cut(y,       bins=PRICE_BINS, labels=PRICE_VALS).astype(int)
y_train_cls = pd.cut(y_train, bins=PRICE_BINS, labels=PRICE_VALS).astype(int)
y_test_cls  = pd.cut(y_test,  bins=PRICE_BINS, labels=PRICE_VALS).astype(int)

print(f"\n  Distribution des classes de prix :")
for v, l in zip(PRICE_VALS, PRICE_LABELS):
    count = (y_cls == v).sum()
    print(f"    {l:15} : {count:3d} biens  ({100*count/len(y_cls):.1f}%)")


# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 4 : ENTRAÎNEMENT & ÉVALUATION
# ─────────────────────────────────────────────────────────────────────────────
banner("ÉTAPE 4 : ENTRAÎNEMENT ET COMPARAISON DES MODÈLES")

results = {}


def eval_regression(name, key, model, Xtr, Xte, ytr, yte):
    model.fit(Xtr, ytr)
    yp   = model.predict(Xte)
    r2   = r2_score(yte, yp)
    rmse = float(np.sqrt(mean_squared_error(yte, yp)))
    mae  = float(mean_absolute_error(yte, yp))
    try:
        cv = float(cross_val_score(model, Xtr, ytr, cv=5, scoring='r2').mean())
    except Exception:
        cv = 0.0

    print(f"\n  [{name}]")
    print(f"    R²      = {r2:.4f}")
    print(f"    RMSE    = {rmse:>14,.0f}")
    print(f"    MAE     = {mae:>14,.0f}")
    print(f"    CV R²   = {cv:.4f}")

    results[key] = {
        'model': model, 'type': 'regression',
        'r2': r2, 'rmse': rmse, 'mae': mae, 'cv_r2': cv,
        'y_pred': yp.tolist()
    }


def eval_classification(name, key, model, Xtr, Xte, ytr, yte):
    model.fit(Xtr, ytr)
    yp   = model.predict(Xte)
    acc  = float(accuracy_score(yte, yp))
    prec = float(precision_score(yte, yp, average='weighted', zero_division=0))
    rec  = float(recall_score(yte, yp, average='weighted', zero_division=0))
    f1   = float(f1_score(yte, yp, average='weighted', zero_division=0))
    cm   = confusion_matrix(yte, yp).tolist()

    print(f"\n  [{name}]")
    print(f"    Accuracy  = {acc:.4f}")
    print(f"    Precision = {prec:.4f}")
    print(f"    Recall    = {rec:.4f}")
    print(f"    F1-score  = {f1:.4f}")
    print(f"    Matrice :\n{confusion_matrix(yte, yp)}")

    results[key] = {
        'model': model, 'type': 'classification',
        'accuracy': acc, 'precision': prec, 'recall': rec, 'f1_score': f1,
        'cm': cm, 'y_pred': yp.tolist()
    }


print("\n  ── MODÈLES DE RÉGRESSION ──────────────────────────────")
eval_regression("Régression Linéaire",   "linear_regression",
                LinearRegression(),
                X_train, X_test, y_train, y_test)

eval_regression("KNN Régression (k=5)",  "knn_regression",
                KNeighborsRegressor(n_neighbors=5),
                X_train_sc, X_test_sc, y_train, y_test)

eval_regression("Arbre de Décision",     "decision_tree_reg",
                DecisionTreeRegressor(max_depth=6, random_state=42),
                X_train, X_test, y_train, y_test)

eval_regression("Forêt Aléatoire",       "random_forest_reg",
                RandomForestRegressor(n_estimators=100, random_state=42),
                X_train, X_test, y_train, y_test)

print("\n  ── MODÈLES DE CLASSIFICATION ──────────────────────────")
eval_classification("Régression Logistique", "logistic_regression",
                    LogisticRegression(max_iter=1000, random_state=42, C=1.0),
                    X_train_sc, X_test_sc, y_train_cls, y_test_cls)

eval_classification("KNN Classification",    "knn_classification",
                    KNeighborsClassifier(n_neighbors=5),
                    X_train_sc, X_test_sc, y_train_cls, y_test_cls)

eval_classification("Arbre de Décision clf", "decision_tree_clf",
                    DecisionTreeClassifier(max_depth=6, random_state=42),
                    X_train, X_test, y_train_cls, y_test_cls)

eval_classification("Forêt Aléatoire clf",   "random_forest_clf",
                    RandomForestClassifier(n_estimators=100, random_state=42),
                    X_train, X_test, y_train_cls, y_test_cls)


# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 5 : SÉLECTION DU MEILLEUR MODÈLE
# ─────────────────────────────────────────────────────────────────────────────
banner("ÉTAPE 5 : SÉLECTION DU MEILLEUR MODÈLE")

reg_results = {k: v for k, v in results.items() if v['type'] == 'regression'}
best_key    = max(reg_results, key=lambda k: reg_results[k]['r2'])
best_info   = reg_results[best_key]

print(f"\n  Meilleur modèle de régression : {best_key}")
print(f"  R² = {best_info['r2']:.4f}  |  RMSE = {best_info['rmse']:,.0f}  |  MAE = {best_info['mae']:,.0f}")

# Tableau récapitulatif
print(f"\n  {'Modèle':<30} {'R²':>8} {'RMSE':>15} {'MAE':>15}")
print(f"  {'-'*70}")
for k, v in reg_results.items():
    star = " ★" if k == best_key else ""
    print(f"  {k:<30} {v['r2']:>8.4f} {v['rmse']:>15,.0f} {v['mae']:>15,.0f}{star}")


# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 6 : SAUVEGARDE
# ─────────────────────────────────────────────────────────────────────────────
banner("ÉTAPE 6 : SAUVEGARDE DES MODÈLES ET MÉTADONNÉES")

# Sauvegarder le meilleur modèle de régression
joblib.dump(best_info['model'], os.path.join(MODEL_DIR, 'best_model.pkl'))
joblib.dump(scaler,             os.path.join(MODEL_DIR, 'scaler.pkl'))

# Sauvegarder tous les modèles individuellement
model_files = {
    'linear_regression':  'best_model.pkl',
    'knn_regression':     'knn_regression.pkl',
    'decision_tree_reg':  'decision_tree_reg.pkl',
    'random_forest_reg':  'random_forest_reg.pkl',
    'logistic_regression':'logistic_regression.pkl',
    'knn_classification': 'knn_classification.pkl',
    'decision_tree_clf':  'decision_tree_clf.pkl',
    'random_forest_clf':  'random_forest_clf.pkl',
}
for key, fname in model_files.items():
    if key in results:
        joblib.dump(results[key]['model'], os.path.join(MODEL_DIR, fname))

# Construire metadata.json
regression_metrics = {}
for k in ['linear_regression', 'knn_regression', 'decision_tree_reg', 'random_forest_reg']:
    if k in results:
        r = results[k]
        regression_metrics[k] = {
            'r2':   r['r2'],
            'rmse': r['rmse'],
            'mae':  r['mae'],
            'cv_r2': r.get('cv_r2', 0),
        }

classification_metrics = {}
confusion_matrices = {}
for k in ['logistic_regression', 'knn_classification', 'decision_tree_clf', 'random_forest_clf']:
    if k in results:
        r = results[k]
        classification_metrics[k] = {
            'accuracy':  r['accuracy'],
            'f1_score':  r['f1_score'],
            'precision': r['precision'],
            'recall':    r['recall'],
        }
        confusion_matrices[k] = r['cm']

metadata = {
    'best_regression_model': best_key,
    'feature_names':         FEATURE_COLS,
    'price_bins':            PRICE_BINS[:-1] + [999_999_999],
    'price_labels':          PRICE_LABELS,
    'regression':            regression_metrics,
    'classification':        classification_metrics,
    'confusion_matrices':    confusion_matrices,
    'dataset_size':          len(df_clean),
    'train_size':            len(X_train),
    'test_size':             len(X_test),
}

with open(os.path.join(MODEL_DIR, 'metadata.json'), 'w', encoding='utf-8') as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print(f"\n  Fichiers sauvegardés dans : {MODEL_DIR}/")
for fname in sorted(os.listdir(MODEL_DIR)):
    size = os.path.getsize(os.path.join(MODEL_DIR, fname))
    print(f"    {fname:<35} {size/1024:>7.1f} KB")

print(f"\n  Pipeline ML terminé avec succès !")
print(f"  Lancez maintenant : python app/main.py")