"""
=============================================================================
FICHIER : src/translations.py
RÔLE    : Système de traduction global (FR / EN / AR)
=============================================================================
"""

TRANSLATIONS = {
    "Français": {
        # Navigation / Sidebar
        "Accueil"              : "Accueil",
        "Tableau de bord"      : "Tableau de bord",
        "Prédiction"           : "Prédiction",
        "Historique"           : "Historique",
        "Annonces"             : "Annonces",
        "Messages"             : "Messages",
        "Paramètres"           : "Paramètres",
        "Déconnexion"          : "Déconnexion",
        "Mon profil"           : "Mon profil",

        # Login
        "Connexion"            : "Connexion",
        "Adresse email"        : "Adresse email",
        "Mot de passe"         : "Mot de passe",
        "Se connecter"         : "Se connecter",
        "Créer un compte"      : "Créer un compte",
        "Retour"               : "← Retour",
        "Connexion en cours"   : "Connexion en cours...",

        # Dashboard
        "Bonjour"              : "Bonjour",
        "Prédictions"          : "Prédictions",
        "Dernière estimation"  : "Dernière estimation",
        "Mes annonces"         : "Mes annonces",

        # Boutons généraux
        "Enregistrer"          : "Enregistrer",
        "Annuler"              : "Annuler",
        "Confirmer"            : "Confirmer",
        "Fermer"               : "Fermer",

        # Settings
        "Langue de l'interface": "Langue de l'interface",
        "Redémarrage requis"   : "Redémarrage requis",
        "Thème"                : "Thème",
        "Clair"                : "Clair",
        "Sombre"               : "Sombre",
    },

    "English": {
        # Navigation / Sidebar
        "Accueil"              : "Home",
        "Tableau de bord"      : "Dashboard",
        "Prédiction"           : "Prediction",
        "Historique"           : "History",
        "Annonces"             : "Listings",
        "Messages"             : "Messages",
        "Paramètres"           : "Settings",
        "Déconnexion"          : "Logout",
        "Mon profil"           : "My Profile",

        # Login
        "Connexion"            : "Login",
        "Adresse email"        : "Email address",
        "Mot de passe"         : "Password",
        "Se connecter"         : "Sign in",
        "Créer un compte"      : "Create account",
        "Retour"               : "← Back",
        "Connexion en cours"   : "Signing in...",

        # Dashboard
        "Bonjour"              : "Hello",
        "Prédictions"          : "Predictions",
        "Dernière estimation"  : "Last estimate",
        "Mes annonces"         : "My listings",

        # Boutons généraux
        "Enregistrer"          : "Save",
        "Annuler"              : "Cancel",
        "Confirmer"            : "Confirm",
        "Fermer"               : "Close",

        # Settings
        "Langue de l'interface": "Interface language",
        "Redémarrage requis"   : "Restart required",
        "Thème"                : "Theme",
        "Clair"                : "Light",
        "Sombre"               : "Dark",
    },

    "العربية": {
        # Navigation / Sidebar
        "Accueil"              : "الرئيسية",
        "Tableau de bord"      : "لوحة التحكم",
        "Prédiction"           : "التنبؤ",
        "Historique"           : "السجل",
        "Annonces"             : "الإعلانات",
        "Messages"             : "الرسائل",
        "Paramètres"           : "الإعدادات",
        "Déconnexion"          : "تسجيل الخروج",
        "Mon profil"           : "ملفي الشخصي",

        # Login
        "Connexion"            : "تسجيل الدخول",
        "Adresse email"        : "البريد الإلكتروني",
        "Mot de passe"         : "كلمة المرور",
        "Se connecter"         : "دخول",
        "Créer un compte"      : "إنشاء حساب",
        "Retour"               : "→ رجوع",
        "Connexion en cours"   : "جارٍ تسجيل الدخول...",

        # Dashboard
        "Bonjour"              : "مرحباً",
        "Prédictions"          : "التنبؤات",
        "Dernière estimation"  : "آخر تقدير",
        "Mes annonces"         : "إعلاناتي",

        # Boutons généraux
        "Enregistrer"          : "حفظ",
        "Annuler"              : "إلغاء",
        "Confirmer"            : "تأكيد",
        "Fermer"               : "إغلاق",

        # Settings
        "Langue de l'interface": "لغة الواجهة",
        "Redémarrage requis"   : "إعادة التشغيل مطلوبة",
        "Thème"                : "المظهر",
        "Clair"                : "فاتح",
        "Sombre"               : "داكن",
    },
}

# Langue active (par défaut : Français)
_current_lang = "Français"


def set_language(lang: str):
    """Change la langue active."""
    global _current_lang
    if lang in TRANSLATIONS:
        _current_lang = lang


def get_language() -> str:
    """Retourne la langue active."""
    return _current_lang


def tr(key: str) -> str:
    """Traduit une clé selon la langue active."""
    return TRANSLATIONS.get(_current_lang, {}).get(key, key)
