"""
=============================================================================
FICHIER : app/pages/page_login.py
RÔLE    : Page de connexion utilisateur
=============================================================================
"""

import re
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

PAGE_HOME      = 0
PAGE_REGISTER  = 2
PAGE_DASHBOARD = 3
PAGE_ADMIN     = 9

# Remontée de 3 niveaux : page_login.py → pages → app → Projet_gp_ML
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")


class PageLogin(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0A1F5E, stop:1 #1565C0);
            }
        """)

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)

        # ── Card ──────────────────────────────────────────────────
        card = QFrame()
        card.setFixedWidth(440)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 20px;
                border: none;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(48, 40, 48, 48)
        card_layout.setSpacing(20)

        # Retour
        back_row = QHBoxLayout()
        back_btn = QPushButton("← Retour")
        back_btn.setStyleSheet("color: #546E7A; font-size: 12px; background: transparent; border: none;")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.clicked.connect(lambda: self.main_window.navigate_to(PAGE_HOME))
        back_row.addWidget(back_btn)
        back_row.addStretch()
        card_layout.addLayout(back_row)

        # ── Logo ──────────────────────────────────────────────────
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        if os.path.exists(LOGO_PATH):
            pix = QPixmap(str(LOGO_PATH))
            logo_label.setPixmap(pix.scaled(120, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo_label.setText("Real Estate AI")
            logo_label.setStyleSheet("font-size: 18px; font-weight: 800; color: #0D2F6E;")
        card_layout.addWidget(logo_label)

        # Titre
        title = QLabel("Connexion")
        title.setStyleSheet("font-size: 26px; font-weight: 800; color: #0D2F6E;")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)

        sub = QLabel("Entrez vos identifiants pour accéder à votre espace")
        sub.setStyleSheet("color: #546E7A; font-size: 13px;")
        sub.setAlignment(Qt.AlignCenter)
        sub.setWordWrap(True)
        card_layout.addWidget(sub)

        card_layout.addSpacing(8)

        # Email
        email_lbl = QLabel("Adresse email")
        email_lbl.setStyleSheet("font-weight: 600; color: #1A1A2E; font-size: 13px;")
        card_layout.addWidget(email_lbl)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("exemple@email.com")
        self.email_input.setFixedHeight(44)
        self.email_input.setStyleSheet("""
            QLineEdit {
                border: 1.5px solid #E0E0E0; border-radius: 10px;
                padding: 0 14px; font-size: 14px; background: #FAFAFA;
            }
            QLineEdit:focus { border: 2px solid #1565C0; background: white; }
        """)
        card_layout.addWidget(self.email_input)

        # Password
        pwd_lbl = QLabel("Mot de passe")
        pwd_lbl.setStyleSheet("font-weight: 600; color: #1A1A2E; font-size: 13px;")
        card_layout.addWidget(pwd_lbl)

        self.pwd_input = QLineEdit()
        self.pwd_input.setPlaceholderText("••••••••")
        self.pwd_input.setEchoMode(QLineEdit.Password)
        self.pwd_input.setFixedHeight(44)
        self.pwd_input.setStyleSheet("""
            QLineEdit {
                border: 1.5px solid #E0E0E0; border-radius: 10px;
                padding: 0 14px; font-size: 14px; background: #FAFAFA;
            }
            QLineEdit:focus { border: 2px solid #1565C0; background: white; }
        """)
        self.pwd_input.returnPressed.connect(self._do_login)
        card_layout.addWidget(self.pwd_input)

        # Erreur
        self.error_lbl = QLabel("")
        self.error_lbl.setStyleSheet("color: #C62828; font-size: 12px;")
        self.error_lbl.setAlignment(Qt.AlignCenter)
        self.error_lbl.hide()
        card_layout.addWidget(self.error_lbl)

        # Bouton login
        self.login_btn = QPushButton("Se connecter")
        self.login_btn.setFixedHeight(48)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #1565C0; color: white;
                border: none; border-radius: 10px;
                font-size: 15px; font-weight: 700;
            }
            QPushButton:hover { background-color: #0D47A1; }
            QPushButton:pressed { background-color: #0A2E6E; }
        """)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.clicked.connect(self._do_login)
        card_layout.addWidget(self.login_btn)

        # Séparateur
        sep_row = QHBoxLayout()
        sep_l = QFrame(); sep_l.setFrameShape(QFrame.HLine); sep_l.setStyleSheet("color: #E0E0E0;")
        or_lbl = QLabel("ou"); or_lbl.setStyleSheet("color: #9E9E9E; font-size: 12px; padding: 0 8px;")
        sep_r = QFrame(); sep_r.setFrameShape(QFrame.HLine); sep_r.setStyleSheet("color: #E0E0E0;")
        sep_row.addWidget(sep_l); sep_row.addWidget(or_lbl); sep_row.addWidget(sep_r)
        card_layout.addLayout(sep_row)

        # Créer un compte
        reg_btn = QPushButton("Créer un compte")
        reg_btn.setFixedHeight(44)
        reg_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #1565C0;
                border: 1.5px solid #1565C0; border-radius: 10px;
                font-size: 14px; font-weight: 600;
            }
            QPushButton:hover { background-color: #E3F2FD; }
        """)
        reg_btn.setCursor(Qt.PointingHandCursor)
        reg_btn.clicked.connect(lambda: self.main_window.navigate_to(PAGE_REGISTER))
        card_layout.addWidget(reg_btn)



        outer.addWidget(card)

    def _do_login(self):
        email    = self.email_input.text().strip()
        password = self.pwd_input.text()

        if not email or not password:
            self._show_error("Veuillez remplir tous les champs"); return
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            self._show_error("Format d'email invalide"); return

        self.login_btn.setText("Connexion en cours...")
        self.login_btn.setEnabled(False)

        result = self.main_window.db.login_user(email, password)

        self.login_btn.setText("Se connecter")
        self.login_btn.setEnabled(True)

        if result['success']:
            self.main_window.current_user = result['user']
            self.error_lbl.hide()
            self.email_input.clear()
            self.pwd_input.clear()
            page = PAGE_ADMIN if result['user'].get('role') == 'admin' else PAGE_DASHBOARD
            self.main_window.navigate_to(page)
        else:
            self._show_error(result.get('error', 'Erreur de connexion'))

    def _show_error(self, msg: str):
        self.error_lbl.setText(msg)
        self.error_lbl.show()

    def on_enter(self):
        self.email_input.clear()
        self.pwd_input.clear()
        self.error_lbl.hide()