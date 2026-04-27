"""
=============================================================================
FICHIER : app/pages/page_profile.py
RÔLE    : Page profil utilisateur
          - Infos personnelles éditables
          - Upload photo de profil
          - Stats de l'utilisateur
          - Changement de mot de passe
=============================================================================
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QFileDialog, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
from app.widgets.sidebar import Sidebar


class PageProfile(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._new_avatar_path = None
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = Sidebar(self.main_window, active_page='profile')
        root.addWidget(self.sidebar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        root.addWidget(scroll)

        self.content = QWidget()
        self.content.setStyleSheet("background: #F8FAFF;")
        scroll.setWidget(self.content)
        self.main_layout = QVBoxLayout(self.content)
        self.main_layout.setContentsMargins(36, 32, 36, 32)
        self.main_layout.setSpacing(20)

    def on_enter(self):
        root_layout = self.layout()
        old_sb = root_layout.itemAt(0).widget()
        if old_sb:
            old_sb.deleteLater()
        new_sb = Sidebar(self.main_window, active_page='profile')
        root_layout.insertWidget(0, new_sb)

        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        user = self.main_window.current_user or {}

        title = QLabel("Mon Profil")
        title.setObjectName("title")
        self.main_layout.addWidget(title)

        sub = QLabel("Gérez vos informations personnelles et vos préférences")
        sub.setObjectName("subtitle")
        self.main_layout.addWidget(sub)

        # Colonnes
        cols = QHBoxLayout()
        cols.setSpacing(20)
        self.main_layout.addLayout(cols)

        # ── Colonne gauche : avatar + stats ───────────────────────
        left = QFrame()
        left.setStyleSheet("background: white; border: 1px solid #E0E0E0; border-radius: 14px;")
        left.setFixedWidth(260)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(24, 28, 24, 28)
        ll.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        ll.setSpacing(14)

        # Avatar
        self.avatar_lbl = QLabel()
        self.avatar_lbl.setFixedSize(100, 100)
        self.avatar_lbl.setAlignment(Qt.AlignCenter)
        self.avatar_lbl.setStyleSheet("""
            background: #E3F2FD;
            border-radius: 50px;
            font-size: 40px;
        """)

        avatar_path = user.get('avatar_path', '')
        if avatar_path and os.path.exists(avatar_path):
            pix = QPixmap(avatar_path)
            self.avatar_lbl.setPixmap(
                pix.scaled(100, 100, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            )
        else:
            self.avatar_lbl.setText("👤")

        ll.addWidget(self.avatar_lbl, alignment=Qt.AlignCenter)

        change_photo_btn = QPushButton("Changer la photo")
        change_photo_btn.setStyleSheet("""
            QPushButton { background: #E3F2FD; color: #1565C0; border: none; border-radius: 8px;
                padding: 6px 14px; font-size: 12px; font-weight: 600; }
            QPushButton:hover { background: #BBDEFB; }
        """)
        change_photo_btn.setCursor(Qt.PointingHandCursor)
        change_photo_btn.clicked.connect(self._change_avatar)
        ll.addWidget(change_photo_btn, alignment=Qt.AlignCenter)

        # Nom
        name_lbl = QLabel(user.get('full_name') or 'Utilisateur')
        name_lbl.setStyleSheet("font-size: 16px; font-weight: 800; color: #0D2F6E;")
        name_lbl.setAlignment(Qt.AlignCenter)
        name_lbl.setWordWrap(True)
        ll.addWidget(name_lbl)

        role_badge = QLabel("Administrateur" if user.get('role') == 'admin' else "Utilisateur")
        role_badge.setStyleSheet(f"""
            background: {'#FFF3E0' if user.get('role') == 'admin' else '#E3F2FD'};
            color: {'#FF6D00' if user.get('role') == 'admin' else '#1565C0'};
            border-radius: 10px; padding: 4px 14px;
            font-size: 11px; font-weight: 700;
        """)
        role_badge.setAlignment(Qt.AlignCenter)
        ll.addWidget(role_badge, alignment=Qt.AlignCenter)

        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: #E0E0E0;")
        ll.addWidget(sep)

        # Stats
        db = self.main_window.db
        pred_count = db.get_prediction_count(user.get('id', 0)) if db else 0
        props = db.get_user_properties(user.get('id', 0)) if db else []

        for label, value in [
            ("Prédictions", str(pred_count)),
            ("Annonces", str(len(props))),
            ("Membre depuis", str(user.get('created_at', ''))[:10]),
        ]:
            stat_row = QHBoxLayout()
            stat_lbl = QLabel(label)
            stat_lbl.setStyleSheet("color: #546E7A; font-size: 12px;")
            stat_val = QLabel(value)
            stat_val.setStyleSheet("font-weight: 700; color: #0D2F6E; font-size: 12px;")
            stat_row.addWidget(stat_lbl)
            stat_row.addStretch()
            stat_row.addWidget(stat_val)
            ll.addLayout(stat_row)

        cols.addWidget(left)

        # ── Colonne droite : formulaire édition ───────────────────
        right = QFrame()
        right.setStyleSheet("background: white; border: 1px solid #E0E0E0; border-radius: 14px;")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(28, 24, 28, 24)
        rl.setSpacing(16)

        edit_title = QLabel("Modifier les informations")
        edit_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #0D2F6E;")
        rl.addWidget(edit_title)

        inp_style = """
            border: 1.5px solid #E0E0E0; border-radius: 8px;
            padding: 8px 12px; background: white; font-size: 13px; min-height: 38px;
        """

        def field(lbl_text, placeholder, value=''):
            lbl = QLabel(lbl_text)
            lbl.setStyleSheet("font-weight: 600; color: #37474F; font-size: 13px;")
            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            inp.setText(value)
            inp.setStyleSheet(inp_style)
            rl.addWidget(lbl)
            rl.addWidget(inp)
            return inp

        self.edit_name  = field("Nom complet", "Votre nom", user.get('full_name', ''))
        self.edit_phone = field("Téléphone", "+212 6XX XX XX XX", user.get('phone', ''))
        self.edit_city  = field("Ville", "Votre ville", user.get('city', ''))

        # Email (non modifiable)
        email_lbl = QLabel("Adresse email")
        email_lbl.setStyleSheet("font-weight: 600; color: #37474F; font-size: 13px;")
        rl.addWidget(email_lbl)

        email_inp = QLineEdit(user.get('email', ''))
        email_inp.setEnabled(False)
        email_inp.setStyleSheet(inp_style + "background: #F5F5F5; color: #9E9E9E;")
        rl.addWidget(email_inp)

        # Erreur/succès
        self.edit_feedback = QLabel("")
        self.edit_feedback.setStyleSheet("font-size: 12px;")
        self.edit_feedback.hide()
        rl.addWidget(self.edit_feedback)

        save_btn = QPushButton("Enregistrer les modifications")
        save_btn.setFixedHeight(46)
        save_btn.setStyleSheet("""
            QPushButton { background: #FF6D00; color: white; border: none; border-radius: 10px;
                font-size: 14px; font-weight: 700; }
            QPushButton:hover { background: #E65100; }
        """)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._save_profile)
        rl.addWidget(save_btn)

        # Changement mdp
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("background: #E0E0E0; margin: 8px 0;")
        rl.addWidget(sep2)

        pwd_title = QLabel("Changer le mot de passe")
        pwd_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #0D2F6E;")
        rl.addWidget(pwd_title)

        self.pwd_current = QLineEdit()
        self.pwd_current.setPlaceholderText("Mot de passe actuel")
        self.pwd_current.setEchoMode(QLineEdit.Password)
        self.pwd_current.setStyleSheet(inp_style)
        rl.addWidget(self.pwd_current)

        self.pwd_new = QLineEdit()
        self.pwd_new.setPlaceholderText("Nouveau mot de passe (6 car. min)")
        self.pwd_new.setEchoMode(QLineEdit.Password)
        self.pwd_new.setStyleSheet(inp_style)
        rl.addWidget(self.pwd_new)

        self.pwd_confirm = QLineEdit()
        self.pwd_confirm.setPlaceholderText("Confirmer le nouveau mot de passe")
        self.pwd_confirm.setEchoMode(QLineEdit.Password)
        self.pwd_confirm.setStyleSheet(inp_style)
        rl.addWidget(self.pwd_confirm)

        change_pwd_btn = QPushButton("Changer le mot de passe")
        change_pwd_btn.setStyleSheet("""
            QPushButton { background: transparent; color: #1565C0; border: 1.5px solid #1565C0;
                border-radius: 8px; padding: 8px 16px; font-weight: 600; }
            QPushButton:hover { background: #E3F2FD; }
        """)
        change_pwd_btn.setCursor(Qt.PointingHandCursor)
        change_pwd_btn.clicked.connect(self._change_password)
        rl.addWidget(change_pwd_btn)

        # Logout
        sep3 = QFrame()
        sep3.setFrameShape(QFrame.HLine)
        sep3.setStyleSheet("background: #E0E0E0;")
        rl.addWidget(sep3)

        logout_btn = QPushButton("Se déconnecter")
        logout_btn.setStyleSheet("""
            QPushButton { background: transparent; color: #C62828; border: 1.5px solid #C62828;
                border-radius: 8px; padding: 8px 16px; font-weight: 600; }
            QPushButton:hover { background: #FFEBEE; }
        """)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self.main_window.logout)
        rl.addWidget(logout_btn)

        cols.addWidget(right, 1)
        self.main_layout.addStretch()

    def _change_avatar(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Choisir une photo de profil",
            os.path.expanduser("~"),
            "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if path:
            self._new_avatar_path = path
            pix = QPixmap(path)
            if not pix.isNull():
                self.avatar_lbl.setPixmap(
                    pix.scaled(100, 100, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                )

    def _save_profile(self):
        user = self.main_window.current_user
        if not user:
            return

        data = {
            'full_name':   self.edit_name.text().strip(),
            'phone':       self.edit_phone.text().strip(),
            'city':        self.edit_city.text().strip(),
        }
        if self._new_avatar_path:
            data['avatar_path'] = self._new_avatar_path

        ok = self.main_window.db.update_user_profile(user['id'], data)
        if ok:
            # Mettre à jour la session
            self.main_window.current_user.update(data)
            self.edit_feedback.setText("Profil mis à jour avec succès !")
            self.edit_feedback.setStyleSheet("color: #2E7D32; font-size: 12px;")
        else:
            self.edit_feedback.setText("Erreur lors de la mise à jour")
            self.edit_feedback.setStyleSheet("color: #C62828; font-size: 12px;")
        self.edit_feedback.show()

    def _change_password(self):
        user = self.main_window.current_user
        if not user:
            return

        current = self.pwd_current.text()
        new_pwd = self.pwd_new.text()
        confirm = self.pwd_confirm.text()

        if not current or not new_pwd:
            QMessageBox.warning(self, "Erreur", "Remplissez tous les champs.")
            return
        if len(new_pwd) < 6:
            QMessageBox.warning(self, "Erreur", "Nouveau mot de passe trop court.")
            return
        if new_pwd != confirm:
            QMessageBox.warning(self, "Erreur", "Les mots de passe ne correspondent pas.")
            return

        # Vérifier l'ancien mot de passe
        db = self.main_window.db
        u = db.get_user_by_id(user['id'])
        if not u or not db.verify_password(current, u['password_hash']):
            QMessageBox.warning(self, "Erreur", "Mot de passe actuel incorrect.")
            return

        new_hash = db.hash_password(new_pwd)
        ok = db._execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user['id']))
        if ok:
            QMessageBox.information(self, "Succès", "Mot de passe modifié avec succès.")
            self.pwd_current.clear()
            self.pwd_new.clear()
            self.pwd_confirm.clear()
        else:
            QMessageBox.warning(self, "Erreur", "Impossible de changer le mot de passe.")
