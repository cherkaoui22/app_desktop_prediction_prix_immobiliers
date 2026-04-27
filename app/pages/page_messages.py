"""
=============================================================================
FICHIER : app/pages/page_messages.py
RÔLE    : Page de messagerie utilisateur ↔ admin / vendeur
=============================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt
from app.widgets.sidebar import Sidebar


class PageMessages(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = Sidebar(self.main_window, active_page='messages')
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
        new_sb = Sidebar(self.main_window, active_page='messages')
        root_layout.insertWidget(0, new_sb)

        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        user = self.main_window.current_user or {}

        title = QLabel("Messagerie")
        title.setObjectName("title")
        self.main_layout.addWidget(title)

        sub = QLabel("Vos conversations avec les vendeurs et l'administration")
        sub.setObjectName("subtitle")
        self.main_layout.addWidget(sub)

        db = self.main_window.db
        msgs = db.get_messages_for_user(user.get('id', 0)) if db else []

        if not msgs:
            empty = QLabel("Aucun message pour le moment.")
            empty.setStyleSheet("color: #9E9E9E; font-size: 14px; padding: 40px;")
            empty.setAlignment(Qt.AlignCenter)
            self.main_layout.addWidget(empty)
        else:
            for msg in msgs:
                is_sent = msg.get('sender_id') == user.get('id')
                card = QFrame()
                card.setStyleSheet(f"""
                    background: {'#E3F2FD' if is_sent else '#F8FAFF'};
                    border: 1px solid {'#BBDEFB' if is_sent else '#E0E0E0'};
                    border-radius: 12px;
                """)
                cl = QVBoxLayout(card)
                cl.setContentsMargins(16, 12, 16, 12)
                cl.setSpacing(4)

                direction = "Envoyé à" if is_sent else "Reçu de"
                contact_email = msg.get('receiver_email' if is_sent else 'sender_email', '?')
                from_lbl = QLabel(f"{direction} : {contact_email}  •  {str(msg.get('created_at', ''))[:16]}")
                from_lbl.setStyleSheet(f"font-size: 11px; color: {'#1565C0' if is_sent else '#546E7A'}; font-weight: 600;")
                cl.addWidget(from_lbl)

                content_lbl = QLabel(msg.get('content', ''))
                content_lbl.setStyleSheet("font-size: 13px; color: #1A1A2E;")
                content_lbl.setWordWrap(True)
                cl.addWidget(content_lbl)

                self.main_layout.addWidget(card)

        # Zone pour contacter l'admin
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: #E0E0E0; margin: 8px 0;")
        self.main_layout.addWidget(sep)

        contact_lbl = QLabel("Contacter l'administration :")
        contact_lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #0D2F6E;")
        self.main_layout.addWidget(contact_lbl)

        self.msg_input = QTextEdit()
        self.msg_input.setPlaceholderText("Écrivez votre message à l'administrateur...")
        self.msg_input.setFixedHeight(80)
        self.msg_input.setStyleSheet("""
            border: 1.5px solid #E0E0E0; border-radius: 8px; padding: 8px; background: white;
        """)
        self.main_layout.addWidget(self.msg_input)

        send_btn = QPushButton("Envoyer à l'admin")
        send_btn.setStyleSheet("""
            QPushButton { background: #1565C0; color: white; border: none; border-radius: 8px;
                padding: 10px 20px; font-weight: 600; max-width: 200px; }
            QPushButton:hover { background: #0D47A1; }
        """)
        send_btn.setCursor(Qt.PointingHandCursor)
        send_btn.clicked.connect(self._send_to_admin)
        self.main_layout.addWidget(send_btn)
        self.main_layout.addStretch()

    def _send_to_admin(self):
        user = self.main_window.current_user
        if not user:
            return
        content = self.msg_input.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "Erreur", "Écrivez un message.")
            return

        db = self.main_window.db
        admin = db._fetchone("SELECT id FROM users WHERE role = 'admin' LIMIT 1") if db else None
        if not admin:
            QMessageBox.warning(self, "Erreur", "Admin introuvable.")
            return

        ok = db.send_message(user['id'], admin['id'], content)
        if ok:
            self.msg_input.clear()
            QMessageBox.information(self, "Envoyé", "Message envoyé à l'administration.")
            self.on_enter()
