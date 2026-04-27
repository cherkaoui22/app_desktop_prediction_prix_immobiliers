"""
=============================================================================
FICHIER : app/pages/page_register.py
RÔLE    : Page d'inscription — création de compte utilisateur
=============================================================================
"""

import re
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QLineEdit
)
from PySide6.QtCore import Qt

PAGE_HOME     = 0
PAGE_LOGIN    = 1
PAGE_DASHBOARD = 3

INPUT_STYLE = """
    QLineEdit {
        border: 1.5px solid #E0E0E0;
        border-radius: 10px;
        padding: 0 14px;
        font-size: 14px;
        background: #FAFAFA;
        min-height: 44px;
    }
    QLineEdit:focus {
        border: 2px solid #1565C0;
        background: white;
    }
"""


class PageRegister(QWidget):
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

        card = QFrame()
        card.setFixedWidth(460)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 20px;
            }
        """)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(48, 40, 48, 48)
        cl.setSpacing(16)

        # Retour
        back_btn = QPushButton("← Retour à la connexion")
        back_btn.setStyleSheet("color: #546E7A; font-size: 12px; background: transparent; border: none; text-align: left;")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.clicked.connect(lambda: self.main_window.navigate_to(PAGE_LOGIN))
        cl.addWidget(back_btn)

        # Titre
        title = QLabel("Créer un compte")
        title.setStyleSheet("font-size: 26px; font-weight: 800; color: #0D2F6E;")
        title.setAlignment(Qt.AlignCenter)
        cl.addWidget(title)

        sub = QLabel("Rejoignez notre plateforme d'estimation immobilière IA")
        sub.setStyleSheet("color: #546E7A; font-size: 13px;")
        sub.setAlignment(Qt.AlignCenter)
        sub.setWordWrap(True)
        cl.addWidget(sub)

        cl.addSpacing(4)

        # Champs
        def field(label_text, placeholder, echo=None):
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-weight: 600; color: #1A1A2E; font-size: 13px;")
            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            inp.setStyleSheet(INPUT_STYLE)
            if echo:
                inp.setEchoMode(echo)
            cl.addWidget(lbl)
            cl.addWidget(inp)
            return inp

        self.name_input  = field("Nom complet", "Votre nom et prénom")
        self.email_input = field("Adresse email", "exemple@email.com")
        self.pwd_input   = field("Mot de passe", "••••••••", QLineEdit.Password)
        self.pwd2_input  = field("Confirmer le mot de passe", "••••••••", QLineEdit.Password)

        # Erreur
        self.error_lbl = QLabel("")
        self.error_lbl.setStyleSheet("color: #C62828; font-size: 12px;")
        self.error_lbl.setAlignment(Qt.AlignCenter)
        self.error_lbl.setWordWrap(True)
        self.error_lbl.hide()
        cl.addWidget(self.error_lbl)

        # Bouton
        self.btn = QPushButton("Créer mon compte")
        self.btn.setFixedHeight(48)
        self.btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6D00;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 700;
            }
            QPushButton:hover { background-color: #E65100; }
        """)
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.clicked.connect(self._do_register)
        cl.addWidget(self.btn)

        # Lien login
        login_row = QHBoxLayout()
        login_row.setAlignment(Qt.AlignCenter)
        already_lbl = QLabel("Déjà inscrit ?")
        already_lbl.setStyleSheet("color: #9E9E9E; font-size: 13px;")
        login_lnk = QPushButton("Se connecter")
        login_lnk.setStyleSheet("color: #1565C0; background: transparent; border: none; font-weight: 600; font-size: 13px;")
        login_lnk.setCursor(Qt.PointingHandCursor)
        login_lnk.clicked.connect(lambda: self.main_window.navigate_to(PAGE_LOGIN))
        login_row.addWidget(already_lbl)
        login_row.addWidget(login_lnk)
        cl.addLayout(login_row)

        outer.addWidget(card)

    def _do_register(self):
        name  = self.name_input.text().strip()
        email = self.email_input.text().strip()
        pwd   = self.pwd_input.text()
        pwd2  = self.pwd2_input.text()

        # Validation
        if not all([name, email, pwd, pwd2]):
            self._show_error("Tous les champs sont obligatoires")
            return
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            self._show_error("Format d'email invalide")
            return
        if len(pwd) < 6:
            self._show_error("Mot de passe trop court (minimum 6 caractères)")
            return
        if pwd != pwd2:
            self._show_error("Les mots de passe ne correspondent pas")
            return

        self.btn.setText("Création en cours...")
        self.btn.setEnabled(False)

        db = self.main_window.db
        result = db.register_user(email, pwd, name)

        self.btn.setText("Créer mon compte")
        self.btn.setEnabled(True)

        if result['success']:
            self.main_window.current_user = result['user']
            self.error_lbl.hide()
            self._clear()
            self.main_window.navigate_to(PAGE_DASHBOARD)
        else:
            self._show_error(result.get('error', 'Erreur création compte'))

    def _show_error(self, msg: str):
        self.error_lbl.setText(msg)
        self.error_lbl.show()

    def _clear(self):
        for inp in [self.name_input, self.email_input, self.pwd_input, self.pwd2_input]:
            inp.clear()
        self.error_lbl.hide()

    def on_enter(self):
        self._clear()
