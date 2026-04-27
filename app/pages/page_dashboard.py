"""
=============================================================================
FICHIER : app/pages/page_dashboard.py
RÔLE    : Tableau de bord principal (après connexion)
          - Stats : nb prédictions, dernière estimation, nb annonces
          - Accès rapide aux fonctionnalités principales
          - Activité récente
=============================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QGridLayout
)
from PySide6.QtCore import Qt
from app.widgets.sidebar import Sidebar

PAGE_PREDICT    = 4
PAGE_HISTORY    = 5
PAGE_PROPERTIES = 7
PAGE_PROFILE    = 8
PAGE_MODEL_INFO = 6


class PageDashboard(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = Sidebar(self.main_window, active_page='dashboard')
        root.addWidget(self.sidebar)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        root.addWidget(scroll)

        self.content = QWidget()
        self.content.setStyleSheet("background-color: #F8FAFF;")
        scroll.setWidget(self.content)

        self.main_layout = QVBoxLayout(self.content)
        self.main_layout.setContentsMargins(36, 32, 36, 32)
        self.main_layout.setSpacing(24)

    def on_enter(self):
        """Rafraîchit le contenu à chaque visite."""
        # Supprimer le contenu existant
        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Reconstruire la sidebar avec l'utilisateur actuel
        root_layout = self.layout()
        old_sidebar = root_layout.itemAt(0).widget()
        if old_sidebar:
            old_sidebar.deleteLater()
        new_sidebar = Sidebar(self.main_window, active_page='dashboard')
        root_layout.insertWidget(0, new_sidebar)

        user = self.main_window.current_user or {}
        db   = self.main_window.db

        # ── Header ────────────────────────────────────────────────

        header = QHBoxLayout()
        name = user.get('full_name') or user.get('email', 'Utilisateur')
        title = QLabel(f"Bonjour, {name.split()[0]}  !")
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch()



        subtitle = QLabel("Voici un aperçu de votre activité sur la plateforme")
        subtitle.setObjectName("subtitle")
        self.main_layout.addWidget(subtitle)

        # ── Stats Cards ───────────────────────────────────────────
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)

        pred_count = db.get_prediction_count(user.get('id', 0)) if db else 0
        preds = db.get_user_predictions(user.get('id', 0)) if db else []
        last_price = f"{preds[0]['predicted_price']:,.0f} MAD" if preds else "—"
        props = db.get_user_properties(user.get('id', 0)) if db else []

        stats = [
            ("Prédictions", str(pred_count), "#E3F2FD", "#1565C0", "Total de vos estimations"),
            ("Dernière estimation", last_price, "#FFF3E0", "#FF6D00", "Votre dernière prédiction"),
            ("Mes annonces", str(len(props)), "#E8F5E9", "#2E7D32", "Biens publiés"),
        ]

        for label, value, bg, color, desc in stats:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg};
                    border: 1px solid {color}30;
                    border-radius: 14px;
                    min-height: 100px;
                }}
            """)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(20, 18, 20, 18)
            cl.setSpacing(6)

            lbl = QLabel(label)
            lbl.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {color}; text-transform: uppercase;")
            val = QLabel(value)
            val.setStyleSheet(f"font-size: 28px; font-weight: 900; color: {color};")
            d = QLabel(desc)
            d.setStyleSheet("font-size: 11px; color: #9E9E9E;")

            cl.addWidget(lbl)
            cl.addWidget(val)
            cl.addWidget(d)
            stats_row.addWidget(card, 1)

        self.main_layout.addLayout(stats_row)

        # ── Actions rapides ───────────────────────────────────────
        actions_title = QLabel("Actions rapides")
        actions_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #0D2F6E;")
        self.main_layout.addWidget(actions_title)

        actions_grid = QGridLayout()
        actions_grid.setSpacing(16)

        action_items = [
            ("Prédire un prix",   "Estimez la valeur d'un bien immobilier avec nos modèles ML",
             "#1565C0", PAGE_PREDICT),
            ("Voir l'historique", "Consultez toutes vos prédictions précédentes",
             "#FF6D00", PAGE_HISTORY),
            ("Annonces",          "Parcourez ou publiez des biens immobiliers",
             "#2E7D32", PAGE_PROPERTIES),
            ("Mon profil",        "Modifiez vos informations personnelles",
             "#6A1B9A", PAGE_PROFILE),
        ]

        for i, (t, d, color, page) in enumerate(action_items):
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #E0E0E0;
                    border-radius: 14px;
                }
                QFrame:hover {
                    border-color: #1565C0;
                }
            """)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(20, 20, 20, 16)
            cl.setSpacing(8)

            title_lbl = QLabel(t)
            title_lbl.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {color};")

            desc_lbl = QLabel(d)
            desc_lbl.setStyleSheet("font-size: 12px; color: #546E7A;")
            desc_lbl.setWordWrap(True)

            go_btn = QPushButton("Accéder →")
            go_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-size: 12px;
                    font-weight: 600;
                    max-width: 120px;
                }}
                QPushButton:hover {{ opacity: 0.9; }}
            """)
            go_btn.setCursor(Qt.PointingHandCursor)
            go_btn.clicked.connect(lambda checked, p=page: self.main_window.navigate_to(p))

            cl.addWidget(title_lbl)
            cl.addWidget(desc_lbl)
            cl.addWidget(go_btn)

            row, col = divmod(i, 2)
            actions_grid.addWidget(card, row, col)

        self.main_layout.addLayout(actions_grid)

        # ── Activité récente ──────────────────────────────────────
        if preds:
            recent_title = QLabel("Dernières prédictions")
            recent_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #0D2F6E;")
            self.main_layout.addWidget(recent_title)

            for pred in preds[:3]:
                row_widget = QFrame()
                row_widget.setStyleSheet("""
                    QFrame {
                        background-color: white;
                        border: 1px solid #E0E0E0;
                        border-radius: 10px;
                    }
                """)
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(16, 12, 16, 12)

                info = QLabel(
                    f"Surface: {pred.get('area', 0):.0f} m²  •  "
                    f"{pred.get('bedrooms', 0)} chambres  •  "
                    f"Modèle: {pred.get('model_used', '').replace('_', ' ').title()}"
                )
                info.setStyleSheet("font-size: 12px; color: #546E7A;")

                price_lbl = QLabel(f"{pred.get('predicted_price', 0):,.0f} MAD")
                price_lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #1565C0;")

                row_layout.addWidget(info)
                row_layout.addStretch()
                row_layout.addWidget(price_lbl)
                self.main_layout.addWidget(row_widget)

        self.main_layout.addStretch()
