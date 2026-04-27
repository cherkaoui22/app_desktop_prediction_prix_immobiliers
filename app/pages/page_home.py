"""
=============================================================================
FICHIER : app/pages/page_home.py
RÔLE    : Page d'accueil — première page visible (non connecté)
=============================================================================
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap

PAGE_LOGIN    = 1
PAGE_REGISTER = 2

LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logo.png")


class PageHome(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        outer.addWidget(scroll)

        page = QWidget()
        scroll.setWidget(page)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_navbar())
        layout.addWidget(self._build_hero())
        layout.addWidget(self._build_features())
        layout.addWidget(self._build_stats())
        layout.addWidget(self._build_cta())
        layout.addWidget(self._build_footer())

    def _build_navbar(self) -> QWidget:
        nav = QWidget()
        nav.setFixedHeight(64)
        nav.setStyleSheet("""
            background-color: #0D2F6E;
            border-bottom: 1px solid #1A3A7A;
        """)
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(40, 0, 40, 0)

        # ── Logo PNG ──────────────────────────────────────────────
        logo_label = QLabel()
        logo_pixmap = QPixmap(LOGO_PATH)
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(130, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # Fallback texte si logo introuvable
            logo_label.setText("Real Estate AI")
            logo_label.setStyleSheet("color: white; font-size: 18px; font-weight: 800;")
        logo_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        nav_layout.addWidget(logo_label)
        nav_layout.addStretch()

        # Nav buttons
        for text, page in [("Se connecter", PAGE_LOGIN), ("Créer un compte", PAGE_REGISTER)]:
            btn = QPushButton(text)
            if page == PAGE_REGISTER:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #FF6D00;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 8px 22px;
                        font-size: 13px;
                        font-weight: 700;
                    }
                    QPushButton:hover { background-color: #E65100; }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #B3C8F5;
                        border: 1.5px solid #3A5A9A;
                        border-radius: 8px;
                        padding: 8px 22px;
                        font-size: 13px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        border-color: #7A9CC5;
                        color: white;
                        background-color: #1A3A7A;
                    }
                """)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, p=page: self.main_window.navigate_to(p))
            nav_layout.addWidget(btn)
            nav_layout.addSpacing(8)

        return nav

    def _build_hero(self) -> QWidget:
        hero = QWidget()
        hero.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #0A1F5E, stop:0.5 #0D47A1, stop:1 #1565C0);
        """)
        hero.setMinimumHeight(480)

        layout = QVBoxLayout(hero)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(20)



        title = QLabel("Prédisez les Prix\nImmobiliers avec l'IA")
        title.setStyleSheet("""
            color: white;
            font-size: 44px;
            font-weight: 900;
        """)
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)

        subtitle = QLabel(
            "Application desktop intelligente \n"
            "pour estimer précisément la valeur de vos biens immobiliers"
        )
        subtitle.setStyleSheet("color: #90B4E8; font-size: 16px;")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)

        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignCenter)
        btn_row.setSpacing(16)

        btn_start = QPushButton("  Commencer gratuitement")
        btn_start.setStyleSheet("""
            QPushButton {
                background-color: #FF6D00; color: white;
                border: none; border-radius: 10px;
                padding: 14px 32px; font-size: 15px; font-weight: 700;
            }
            QPushButton:hover { background-color: #E65100; }
        """)
        btn_start.setCursor(Qt.PointingHandCursor)
        btn_start.setFixedHeight(50)
        btn_start.clicked.connect(lambda: self.main_window.navigate_to(PAGE_REGISTER))

        btn_login = QPushButton("  Se connecter")
        btn_login.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: white;
                border: 2px solid rgba(255,255,255,0.5);
                border-radius: 10px; padding: 14px 32px;
                font-size: 15px; font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.1);
                border-color: white;
            }
        """)
        btn_login.setCursor(Qt.PointingHandCursor)
        btn_login.setFixedHeight(50)
        btn_login.clicked.connect(lambda: self.main_window.navigate_to(PAGE_LOGIN))

        btn_row.addWidget(btn_start)
        btn_row.addWidget(btn_login)




        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(10)
        layout.addLayout(btn_row)

        return hero

    def _build_features(self) -> QWidget:
        section = QWidget()
        section.setStyleSheet("background-color: #F8FAFF;")
        layout = QVBoxLayout(section)
        layout.setContentsMargins(60, 50, 60, 50)
        layout.setSpacing(32)

        sec_title = QLabel("Fonctionnalités Clés")
        sec_title.setStyleSheet("font-size: 28px; font-weight: 800; color: #0D2F6E;")
        sec_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(sec_title)

        sec_sub = QLabel("Tout ce dont vous avez besoin pour l'estimation immobilière")
        sec_sub.setStyleSheet("color: #546E7A; font-size: 15px;")
        sec_sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(sec_sub)

        grid = QGridLayout()
        grid.setSpacing(20)

        features = [
            ("Prédiction ML",
             "5 modèles comparés : Régression Linéaire, KNN, Arbre de Décision, Forêt Aléatoire, Régression Logistique",
             "#E3F2FD", "#1565C0"),
            ("Annonces Immobilières",
             "Publiez vos biens à vendre ou à louer. Les acheteurs peuvent filtrer par prix, ville et type",
             "#FFF3E0", "#FF6D00"),
            ("Tableau de Bord",
             "Visualisez vos statistiques, l'historique de vos prédictions et les métriques des modèles ML",
             "#E8F5E9", "#2E7D32"),
            ("Espace Admin",
             "Panneau d'administration complet : gestion des utilisateurs, validation des annonces, statistiques",
             "#FCE4EC", "#C62828"),
            ("Historique",
             "Toutes vos prédictions sauvegardées en base de données avec date, modèle utilisé et résultat",
             "#F3E5F5", "#6A1B9A"),
            ("Messagerie",
             "Chat intégré entre acheteurs et vendeurs. L'admin valide les annonces avant publication",
             "#E0F7FA", "#00838F"),
        ]

        for i, (title, desc, bg, color) in enumerate(features):
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg};
                    border: 1px solid {color}30;
                    border-radius: 14px;
                    padding: 4px;
                }}
            """)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(20, 20, 20, 20)
            cl.setSpacing(10)

            title_lbl = QLabel(title)
            title_lbl.setStyleSheet(f"font-size: 15px; font-weight: 800; color: {color};")
            desc_lbl = QLabel(desc)
            desc_lbl.setStyleSheet("font-size: 12px; color: #546E7A;")
            desc_lbl.setWordWrap(True)

            cl.addWidget(title_lbl)
            cl.addWidget(desc_lbl)
            row, col = divmod(i, 3)
            grid.addWidget(card, row, col)

        layout.addLayout(grid)
        return section

    def _build_stats(self) -> QWidget:
        section = QWidget()
        section.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0D47A1, stop:1 #1565C0);
        """)
        layout = QHBoxLayout(section)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(0)

        for value, label in [("5", "Modèles ML"), ("545", "Biens analysés"), ("100%", "Python"), ("Open", "Source")]:
            stat_widget = QWidget()
            stat_layout = QVBoxLayout(stat_widget)
            stat_layout.setAlignment(Qt.AlignCenter)
            stat_layout.setSpacing(4)

            val_lbl = QLabel(value)
            val_lbl.setStyleSheet("font-size: 40px; font-weight: 900; color: white;")
            val_lbl.setAlignment(Qt.AlignCenter)

            lbl_lbl = QLabel(label)
            lbl_lbl.setStyleSheet("font-size: 13px; color: #90B4E8; font-weight: 500;")
            lbl_lbl.setAlignment(Qt.AlignCenter)

            stat_layout.addWidget(val_lbl)
            stat_layout.addWidget(lbl_lbl)
            layout.addWidget(stat_widget, 1)

        return section

    def _build_cta(self) -> QWidget:
        section = QWidget()
        section.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(section)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(60, 50, 60, 50)
        layout.setSpacing(20)

        title = QLabel("Prêt à commencer ?")
        title.setStyleSheet("font-size: 30px; font-weight: 800; color: #0D2F6E;")
        title.setAlignment(Qt.AlignCenter)

        sub = QLabel("Créez votre compte gratuit et estimez votre premier bien en 30 secondes")
        sub.setStyleSheet("color: #546E7A; font-size: 15px;")
        sub.setAlignment(Qt.AlignCenter)

        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignCenter)

        btn = QPushButton("  Créer un compte gratuit")
        btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6D00; color: white;
                border: none; border-radius: 10px;
                padding: 14px 36px; font-size: 15px; font-weight: 700;
            }
            QPushButton:hover { background-color: #E65100; }
        """)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(50)
        btn.clicked.connect(lambda: self.main_window.navigate_to(PAGE_REGISTER))
        btn_row.addWidget(btn)

        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addLayout(btn_row)
        return section

    def _build_footer(self) -> QWidget:
        footer = QWidget()
        footer.setFixedHeight(50)
        footer.setStyleSheet("background-color: #0D2F6E;")
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(40, 0, 40, 0)



        admin_btn = QPushButton("Admin")
        admin_btn.setStyleSheet("""
            QPushButton { background: transparent; color: #4A6A9A; border: none; font-size: 11px; }
            QPushButton:hover { color: #7A9CC5; }
        """)
        admin_btn.setCursor(Qt.PointingHandCursor)
        admin_btn.clicked.connect(lambda: self.main_window.navigate_to(PAGE_LOGIN))
        layout.addWidget(admin_btn)

        return footer