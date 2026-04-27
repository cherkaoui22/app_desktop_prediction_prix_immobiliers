"""
=============================================================================
FICHIER : app/main.py
RÔLE    : Point d'entrée de l'application PySide6
=============================================================================
"""

import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

LOGO_PATH = os.path.join(ROOT, "logo.png")

from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QFont, QIcon, QPixmap

# Import du thème
from src.theme import STYLESHEET, DARK_STYLESHEET

# Import des pages
from app.pages.page_home       import PageHome
from app.pages.page_login      import PageLogin
from app.pages.page_register   import PageRegister
from app.pages.page_dashboard  import PageDashboard
from app.pages.page_predict    import PagePredict
from app.pages.page_history    import PageHistory
from app.pages.page_model_info import PageModelInfo
from app.pages.page_properties import PageProperties
from app.pages.page_profile    import PageProfile
from app.pages.page_admin      import PageAdmin
from app.pages.page_settings   import PageSettings
from app.pages.page_messages   import PageMessages

PAGE_HOME       = 0
PAGE_LOGIN      = 1
PAGE_REGISTER   = 2
PAGE_DASHBOARD  = 3
PAGE_PREDICT    = 4
PAGE_HISTORY    = 5
PAGE_MODEL_INFO = 6
PAGE_PROPERTIES = 7
PAGE_PROFILE    = 8
PAGE_ADMIN      = 9
PAGE_SETTINGS   = 10
PAGE_MESSAGES   = 11


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Immobilier_Prediction")
        self.setMinimumSize(1150, 720)
        self.resize(1360, 820)

        # ── Logo dans la barre de titre + taskbar ────────────────
        if os.path.exists(LOGO_PATH):
            self.setWindowIcon(QIcon(str(LOGO_PATH)))

        # Session utilisateur
        self.current_user: dict | None = None
        self.settings_store = QSettings("RealEstatePredictorApp")

        # ── Base de données ──────────────────────────────────────
        from src.database import db
        self.db = db
        connected = self.db.connect()
        if not connected:
            QMessageBox.warning(
                self, "Base de données",
                "Impossible de se connecter à MySQL.\n"
                "L'application utilise SQLite en mode local.\n"
                "(Lancez XAMPP pour utiliser MySQL)"
            )

        # ── Modèles ML ───────────────────────────────────────────
        try:
            from src.predictor import predictor
            self.predictor = predictor
        except Exception as e:
            print(f"[Main] Predictor non disponible: {e}")
            self.predictor = None

        # ── Stack de pages ───────────────────────────────────────
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.pages = [
            PageHome(self),       # 0
            PageLogin(self),      # 1
            PageRegister(self),   # 2
            PageDashboard(self),  # 3
            PagePredict(self),    # 4
            PageHistory(self),    # 5
            PageModelInfo(self),  # 6
            PageProperties(self), # 7
            PageProfile(self),    # 8
            PageAdmin(self),      # 9
            PageSettings(self),   # 10
            PageMessages(self),   # 11
        ]

        for page in self.pages:
            self.stack.addWidget(page)

        self.navigate_to(PAGE_HOME)

        saved_theme = self.settings_store.value("theme", "light")
        self.apply_theme(saved_theme)

    def navigate_to(self, page_index: int):
        self.stack.setCurrentIndex(page_index)
        widget = self.stack.currentWidget()
        if hasattr(widget, "on_enter"):
            widget.on_enter()

    def logout(self):
        self.current_user = None
        self.navigate_to(PAGE_HOME)

    def apply_theme(self, theme: str):
        self.settings_store.setValue("theme", theme)
        self.setStyleSheet(DARK_STYLESHEET if theme == 'dark' else STYLESHEET)

    def closeEvent(self, event):
        if self.db:
            self.db.disconnect()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("IA Real Estate Predictor")

    # ── Logo dans la taskbar Windows ─────────────────────────────
    if os.path.exists(LOGO_PATH):
        app.setWindowIcon(QIcon(str(LOGO_PATH)))

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()