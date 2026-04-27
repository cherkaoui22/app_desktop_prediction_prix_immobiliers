"""
=============================================================================
FICHIER : app/pages/page_settings.py
RÔLE    : Paramètres de l'application
          - Thème clair/sombre
          - Langue
          - Reset données
          - À propos
=============================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt
from app.widgets.sidebar import Sidebar


class PageSettings(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = Sidebar(self.main_window, active_page='settings')
        root.addWidget(self.sidebar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        root.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet("background: #F8FAFF;")
        scroll.setWidget(content)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop)

        title = QLabel("Paramètres")
        title.setObjectName("title")
        layout.addWidget(title)

        sub = QLabel("Personnalisez votre expérience sur la plateforme")
        sub.setObjectName("subtitle")
        layout.addWidget(sub)

        # ── Apparence ─────────────────────────────────────────────
        layout.addWidget(self._section("Apparence", [
            self._setting_row(
                "Thème",
                "Choisissez entre le mode clair et sombre",
                self._theme_toggle()
            ),
        ]))

        # ── Langue ────────────────────────────────────────────────
        lang_combo = QComboBox()
        lang_combo.addItems(["Français", "English", "العربية"])
        lang_combo.setStyleSheet("border: 1.5px solid #E0E0E0; border-radius: 8px; padding: 6px 10px; background: white; min-height: 34px;")
        layout.addWidget(self._section("Langue", [
            self._setting_row("Langue de l'interface", "Redémarrage requis", lang_combo)
        ]))

        # ── Base de données ───────────────────────────────────────
        reset_btn = QPushButton("Réinitialiser mes données")
        reset_btn.setStyleSheet("""
            QPushButton { background: #FFEBEE; color: #C62828; border: 1px solid #FFCDD2;
                border-radius: 8px; padding: 8px 16px; font-weight: 600; }
            QPushButton:hover { background: #FFCDD2; }
        """)
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.clicked.connect(self._confirm_reset)

        layout.addWidget(self._section("Données", [
            self._setting_row("Réinitialisation", "Supprime votre historique de prédictions", reset_btn)
        ]))

        # ── À propos ──────────────────────────────────────────────
        about_card = QFrame()
        about_card.setStyleSheet("background: white; border: 1px solid #E0E0E0; border-radius: 14px;")
        al = QVBoxLayout(about_card)
        al.setContentsMargins(24, 20, 24, 20)
        al.setSpacing(8)

        about_title = QLabel("À propos de l'application")
        about_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #0D2F6E;")
        al.addWidget(about_title)

        infos = [
            ("Application", "IA Real Estate Predictor"),
            ("Version", "1.0.0"),
            ("Framework", "PySide6 (Qt for Python)"),
            ("ML", "scikit-learn · 5 modèles comparés"),
            ("Base de données", "MySQL (fallback SQLite)")
        ]
        for k, v in infos:
            row = QHBoxLayout()
            k_lbl = QLabel(k + " :")
            k_lbl.setStyleSheet("font-weight: 600; color: #37474F; font-size: 12px; min-width: 130px;")
            v_lbl = QLabel(v)
            v_lbl.setStyleSheet("color: #546E7A; font-size: 12px;")
            row.addWidget(k_lbl)
            row.addWidget(v_lbl)
            row.addStretch()
            al.addLayout(row)

        layout.addWidget(about_card)

    def _section(self, title: str, rows: list) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("background: white; border: 1px solid #E0E0E0; border-radius: 14px;")
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(24, 18, 24, 18)
        fl.setSpacing(12)

        t = QLabel(title)
        t.setStyleSheet("font-size: 15px; font-weight: 700; color: #0D2F6E;")
        fl.addWidget(t)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: #F0F4FF;")
        fl.addWidget(sep)

        for row in rows:
            fl.addLayout(row)

        return frame

    def _setting_row(self, title: str, desc: str, widget) -> QHBoxLayout:
        row = QHBoxLayout()
        col = QVBoxLayout()
        col.setSpacing(2)
        t = QLabel(title)
        t.setStyleSheet("font-size: 13px; font-weight: 600; color: #1A1A2E;")
        d = QLabel(desc)
        d.setStyleSheet("font-size: 11px; color: #9E9E9E;")
        col.addWidget(t)
        col.addWidget(d)
        row.addLayout(col)
        row.addStretch()
        row.addWidget(widget)
        return row

    def _theme_toggle(self) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        light_btn = QPushButton("Clair")
        dark_btn  = QPushButton("Sombre")

        for btn, theme, color in [
            (light_btn, 'light', '#1565C0'),
            (dark_btn,  'dark',  '#37474F'),
        ]:
            btn.setStyleSheet(f"""
                QPushButton {{ background: {color}20; color: {color}; border: 1.5px solid {color};
                    border-radius: 8px; padding: 6px 14px; font-weight: 600; font-size: 12px; }}
                QPushButton:hover {{ background: {color}40; }}
            """)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, t=theme: self.main_window.apply_theme(t))
            layout.addWidget(btn)

        return container

    def _confirm_reset(self):
        user = self.main_window.current_user
        if not user:
            return
        reply = QMessageBox.question(
            self, "Confirmation",
            "Supprimer tout votre historique de prédictions ?\nCette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            ok = self.main_window.db._execute(
                "DELETE FROM predictions WHERE user_id = %s", (user['id'],)
            )
            if ok:
                QMessageBox.information(self, "Réinitialisé", "Votre historique a été supprimé.")

    def on_enter(self):
        root_layout = self.layout()
        old_sb = root_layout.itemAt(0).widget()
        if old_sb:
            old_sb.deleteLater()
        new_sb = Sidebar(self.main_window, active_page='settings')
        root_layout.insertWidget(0, new_sb)
