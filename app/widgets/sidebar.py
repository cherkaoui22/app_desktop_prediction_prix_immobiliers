"""
=============================================================================
FICHIER : app/widgets/sidebar.py
RÔLE    : Sidebar de navigation commune à toutes les pages authentifiées
          - Logo + nom de l'app
          - Boutons de navigation (utilisateur / admin)
          - Bouton Déconnexion
          - Indicateur de page active
=============================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPixmap


class Sidebar(QWidget):
    """Sidebar de navigation avec indicateur de page active."""

    USER_MENU = [
        ('dashboard',   'Dashboard',       ''),
        ('predict',     'Prédire un prix',  ''),
        ('history',     'Historique',       ''),
        ('properties',  'Annonces',         ''),
        ('messages',    'Messages',         ''),
        ('profile',     'Mon Profil',       ''),
        ('settings',    'Paramètres',       ''),
    ]

    ADMIN_MENU = [
        ('admin',       'Admin Panel',     ''),
        ('dashboard',   'Dashboard',       ''),
        ('predict',     'Prédire',         ''),
        ('history',     'Historique',      ''),
        ('properties',  'Annonces',        ''),
        ('model_info',  'Modèles ML',      ''),
        ('messages',    'Messages',        ''),
        ('profile',     'Mon Profil',      ''),
        ('settings',    'Paramètres',      ''),
    ]

    # Mapping page → index QStackedWidget
    PAGE_INDEX = {
        'admin':      9,
        'dashboard':  3,
        'predict':    4,
        'history':    5,
        'model_info': 6,
        'properties': 7,
        'profile':    8,
        'settings':   10,
        'messages':   11,
    }

    def __init__(self, main_window, active_page: str = 'dashboard'):
        super().__init__()
        self.main_window = main_window
        self.active_page = active_page
        self.setObjectName('sidebar')
        self.setFixedWidth(220)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Logo & Titre ──────────────────────────────────────────
        header = QWidget()
        header.setStyleSheet("background-color: #08215A; padding: 0;")
        header.setFixedHeight(80)
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(20, 14, 20, 14)
        h_layout.setSpacing(2)

        logo_row = QHBoxLayout()
        logo_lbl = QLabel("IA")
        logo_lbl.setStyleSheet("""
            background-color: #FF6D00;
            color: white;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 900;
            padding: 4px 8px;
        """)
        logo_lbl.setFixedSize(36, 36)
        logo_lbl.setAlignment(Qt.AlignCenter)

        name_col = QVBoxLayout()
        name_col.setSpacing(0)
        app_name = QLabel("Real Estate")
        app_name.setObjectName("nav_logo")
        app_name.setStyleSheet("color: white; font-size: 14px; font-weight: 800;")
        sub_name = QLabel("AI Predictor")
        sub_name.setStyleSheet("color: #7A9CC5; font-size: 10px; font-weight: 500;")

        name_col.addWidget(app_name)
        name_col.addWidget(sub_name)

        logo_row.addWidget(logo_lbl)
        logo_row.addSpacing(10)
        logo_row.addLayout(name_col)
        logo_row.addStretch()
        h_layout.addLayout(logo_row)
        layout.addWidget(header)

        # ── Utilisateur connecté ──────────────────────────────────
        user = getattr(self.main_window, 'current_user', None)
        if user:
            user_widget = QWidget()
            user_widget.setStyleSheet("background-color: #0D2F6E; border-bottom: 1px solid #1A3A7A;")
            u_layout = QVBoxLayout(user_widget)
            u_layout.setContentsMargins(20, 12, 20, 12)
            u_layout.setSpacing(2)

            avatar = QLabel("👤")
            avatar.setStyleSheet("""
                background-color: #1565C0;
                border-radius: 18px;
                font-size: 16px;
                padding: 5px;
            """)
            avatar.setFixedSize(36, 36)
            avatar.setAlignment(Qt.AlignCenter)

            email_lbl = QLabel(user.get('email', '')[:24] + ('...' if len(user.get('email','')) > 24 else ''))
            email_lbl.setStyleSheet("color: #B3C8F5; font-size: 11px;")

            role_lbl = QLabel("Administrateur" if user.get('role') == 'admin' else "Utilisateur")
            role_lbl.setStyleSheet(f"""
                color: {'#FF6D00' if user.get('role') == 'admin' else '#4FC3F7'};
                font-size: 10px;
                font-weight: 700;
            """)

            u_layout.addWidget(email_lbl)
            u_layout.addWidget(role_lbl)
            layout.addWidget(user_widget)

        # ── Menu navigation ───────────────────────────────────────
        menu_area = QWidget()
        menu_area.setStyleSheet("background-color: transparent;")
        menu_layout = QVBoxLayout(menu_area)
        menu_layout.setContentsMargins(0, 8, 0, 8)
        menu_layout.setSpacing(2)

        is_admin = user and user.get('role') == 'admin'
        menu_items = self.ADMIN_MENU if is_admin else self.USER_MENU

        # Section label
        sec_lbl = QLabel("  NAVIGATION")
        sec_lbl.setStyleSheet("color: #4A6A9A; font-size: 10px; font-weight: 700; padding: 8px 20px 4px;")
        menu_layout.addWidget(sec_lbl)

        for page_key, label, _ in menu_items:
            btn = QPushButton(f"  {label}")
            is_active = (page_key == self.active_page)
            btn.setObjectName('sidebar_btn_active' if is_active else 'sidebar_btn')
            btn.setFixedHeight(44)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip(label)

            # Navigation
            idx = self.PAGE_INDEX.get(page_key, 3)
            btn.clicked.connect(lambda checked, i=idx: self.main_window.navigate_to(i))
            menu_layout.addWidget(btn)

        layout.addWidget(menu_area)
        layout.addStretch()

        # ── Séparateur + Déconnexion ──────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #1A3A7A; margin: 0 16px;")
        layout.addWidget(sep)

        logout_btn = QPushButton("  Déconnexion")
        logout_btn.setObjectName('sidebar_btn')
        logout_btn.setFixedHeight(48)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #EF9A9A;
                border: none;
                text-align: left;
                padding: 13px 20px 13px 24px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #3A1A1A;
                color: #EF5350;
            }
        """)
        logout_btn.clicked.connect(self.main_window.logout)
        layout.addWidget(logout_btn)

        # Version
        ver_lbl = QLabel("v1.0 · ISTA NTIC SYBA")
        ver_lbl.setStyleSheet("color: #2A4A7A; font-size: 9px; padding: 8px 20px;")
        layout.addWidget(ver_lbl)
