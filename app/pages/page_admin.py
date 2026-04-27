"""
=============================================================================
FICHIER : app/pages/page_admin.py
RÔLE    : Panneau d'administration (admin uniquement)
          - Statistiques globales
          - Gestion des utilisateurs
          - Validation des annonces
          - Toutes les prédictions
          - Modèles ML info
          - Messagerie admin
=============================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QTableWidget, QTableWidgetItem,
    QHeaderView, QTabWidget, QTextEdit, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from app.widgets.sidebar import Sidebar

PAGE_LOGIN = 1


class PageAdmin(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = Sidebar(self.main_window, active_page='admin')
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
        # Vérifier que l'utilisateur est admin
        user = self.main_window.current_user
        if not user or user.get('role') != 'admin':
            self.main_window.navigate_to(PAGE_LOGIN)
            return

        # Sidebar refresh
        root_layout = self.layout()
        old_sb = root_layout.itemAt(0).widget()
        if old_sb:
            old_sb.deleteLater()
        new_sb = Sidebar(self.main_window, active_page='admin')
        root_layout.insertWidget(0, new_sb)

        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Header admin
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0D2F6E, stop:1 #1565C0);
            border-radius: 14px;
        """)
        hfl = QHBoxLayout(header_frame)
        hfl.setContentsMargins(24, 18, 24, 18)

        admin_title = QLabel("Panneau d'Administration")
        admin_title.setStyleSheet("color: white; font-size: 20px; font-weight: 800;")
        hfl.addWidget(admin_title)
        hfl.addStretch()

        admin_badge = QLabel("ADMIN")
        admin_badge.setStyleSheet("""
            background: #FF6D00; color: white; border-radius: 8px;
            padding: 4px 16px; font-size: 12px; font-weight: 800;
        """)
        hfl.addWidget(admin_badge)
        self.main_layout.addWidget(header_frame)

        # Stats
        db = self.main_window.db
        stats = db.get_stats() if db else {}
        self._build_stats(stats)

        # Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { background: white; border: 1px solid #E0E0E0; border-radius: 10px; }
            QTabBar::tab { background: #F0F4FF; color: #546E7A; padding: 10px 20px; border-radius: 6px 6px 0 0; font-weight: 600; font-size: 12px; }
            QTabBar::tab:selected { background: #1565C0; color: white; }
        """)
        self.main_layout.addWidget(tabs)

        tabs.addTab(self._build_users_tab(), "Utilisateurs")
        tabs.addTab(self._build_properties_tab(), "Annonces en attente")
        tabs.addTab(self._build_predictions_tab(), "Prédictions")
        tabs.addTab(self._build_messages_tab(), "Messagerie")
        tabs.addTab(self._build_ml_tab(), "Modèles ML")

    def _build_stats(self, stats: dict):
        row = QHBoxLayout()
        row.setSpacing(14)

        items = [
            ("Utilisateurs", str(stats.get('total_users', 0)), "#E3F2FD", "#1565C0"),
            ("Prédictions", str(stats.get('total_preds', 0)), "#FFF3E0", "#FF6D00"),
            ("Annonces", str(stats.get('total_props', 0)), "#E8F5E9", "#2E7D32"),
            ("En attente", str(stats.get('pending_props', 0)), "#FCE4EC", "#C62828"),
        ]
        for label, value, bg, color in items:
            card = QFrame()
            card.setStyleSheet(f"background: {bg}; border: 1px solid {color}30; border-radius: 12px;")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 14, 16, 14)
            cl.setSpacing(4)
            v = QLabel(value)
            v.setStyleSheet(f"font-size: 26px; font-weight: 900; color: {color};")
            l = QLabel(label)
            l.setStyleSheet(f"font-size: 11px; color: {color}; font-weight: 700;")
            cl.addWidget(v)
            cl.addWidget(l)
            row.addWidget(card, 1)
        self.main_layout.addLayout(row)

    def _build_users_tab(self) -> QWidget:
        tab = QWidget()
        tab.setStyleSheet("background: white;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        users = self.main_window.db.get_all_users() if self.main_window.db else []

        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["ID", "Email", "Nom", "Rôle", "Ville", "Inscrit le"])
        table.setRowCount(len(users))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget { border: none; }
            QTableWidget::item { padding: 10px; }
            QHeaderView::section { background: #0D2F6E; color: white; padding: 10px; font-weight: 700; border: none; }
        """)

        for r, user in enumerate(users):
            vals = [
                str(user.get('id', '')),
                user.get('email', ''),
                user.get('full_name', '—'),
                user.get('role', 'user'),
                user.get('city', '—'),
                str(user.get('created_at', ''))[:10],
            ]
            for c, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                if val == 'admin':
                    item.setForeground(QColor('#FF6D00'))
                table.setItem(r, c, item)

        layout.addWidget(table)

        # Bouton supprimer
        del_row = QHBoxLayout()
        self.user_id_to_del = QTableWidget()
        table.itemSelectionChanged.connect(lambda: None)

        del_btn = QPushButton("Supprimer l'utilisateur sélectionné")
        del_btn.setStyleSheet("""
            QPushButton { background: #C62828; color: white; border: none; border-radius: 8px; padding: 8px 16px; font-weight: 600; }
            QPushButton:hover { background: #B71C1C; }
        """)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.clicked.connect(lambda: self._delete_user(table))
        del_row.addStretch()
        del_row.addWidget(del_btn)
        layout.addLayout(del_row)

        return tab

    def _delete_user(self, table: QTableWidget):
        row = table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Sélection", "Sélectionnez un utilisateur.")
            return
        user_id = int(table.item(row, 0).text())
        role = table.item(row, 3).text()
        if role == 'admin':
            QMessageBox.warning(self, "Action interdite", "Impossible de supprimer un administrateur.")
            return
        reply = QMessageBox.question(self, "Confirmation", f"Supprimer l'utilisateur ID {user_id} ?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            ok = self.main_window.db.delete_user(user_id)
            if ok:
                table.removeRow(row)
                QMessageBox.information(self, "Supprimé", "Utilisateur supprimé.")

    def _build_properties_tab(self) -> QWidget:
        tab = QWidget()
        tab.setStyleSheet("background: white;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        pending = self.main_window.db.get_pending_properties() if self.main_window.db else []

        if not pending:
            lbl = QLabel("Aucune annonce en attente de validation.")
            lbl.setStyleSheet("color: #9E9E9E; font-size: 14px; padding: 20px;")
            lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl)
            return tab

        for prop in pending:
            card = QFrame()
            card.setStyleSheet("background: #F8FAFF; border: 1px solid #E0E0E0; border-radius: 10px;")
            cl = QHBoxLayout(card)
            cl.setContentsMargins(16, 14, 16, 14)
            cl.setSpacing(12)

            info_col = QVBoxLayout()
            t = QLabel(prop.get('title', ''))
            t.setStyleSheet("font-size: 14px; font-weight: 700; color: #0D2F6E;")
            info_col.addWidget(t)
            d = QLabel(f"{prop.get('city', '')}  •  {prop.get('price', 0):,.0f} MAD  •  {prop.get('email', '')}")
            d.setStyleSheet("font-size: 12px; color: #546E7A;")
            info_col.addWidget(d)
            desc = prop.get('description', '')[:80]
            if desc:
                desc_lbl = QLabel(desc + '...' if len(prop.get('description', '')) > 80 else desc)
                desc_lbl.setStyleSheet("font-size: 11px; color: #9E9E9E;")
                info_col.addWidget(desc_lbl)
            cl.addLayout(info_col, 1)

            btn_col = QVBoxLayout()
            btn_col.setSpacing(6)

            approve_btn = QPushButton("Valider")
            approve_btn.setStyleSheet("""
                QPushButton { background: #2E7D32; color: white; border: none; border-radius: 8px; padding: 6px 16px; font-weight: 600; }
                QPushButton:hover { background: #1B5E20; }
            """)
            approve_btn.setCursor(Qt.PointingHandCursor)
            approve_btn.clicked.connect(lambda checked, p=prop, c=card: self._validate_prop(p['id'], True, c))

            reject_btn = QPushButton("Refuser")
            reject_btn.setStyleSheet("""
                QPushButton { background: #C62828; color: white; border: none; border-radius: 8px; padding: 6px 16px; font-weight: 600; }
                QPushButton:hover { background: #B71C1C; }
            """)
            reject_btn.setCursor(Qt.PointingHandCursor)
            reject_btn.clicked.connect(lambda checked, p=prop, c=card: self._validate_prop(p['id'], False, c))

            btn_col.addWidget(approve_btn)
            btn_col.addWidget(reject_btn)
            cl.addLayout(btn_col)

            layout.addWidget(card)

        layout.addStretch()
        return tab

    def _validate_prop(self, prop_id: int, validated: bool, card: QFrame):
        ok = self.main_window.db.validate_property(prop_id, validated)
        if ok:
            card.setStyleSheet(
                "background: #E8F5E9; border: 1px solid #C8E6C9; border-radius: 10px;" if validated
                else "background: #FFEBEE; border: 1px solid #FFCDD2; border-radius: 10px;"
            )
            for child in card.findChildren(QPushButton):
                child.hide()
            status_lbl = QLabel("Validée" if validated else "Refusée")
            status_lbl.setStyleSheet(
                "color: #2E7D32; font-weight: 700; font-size: 13px;" if validated
                else "color: #C62828; font-weight: 700; font-size: 13px;"
            )
            card.layout().addWidget(status_lbl)

    def _build_predictions_tab(self) -> QWidget:
        tab = QWidget()
        tab.setStyleSheet("background: white;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)

        preds = self.main_window.db.get_all_predictions() if self.main_window.db else []

        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(["Utilisateur", "Surface", "Chambres", "Modèle", "Prix prédit", "Catégorie", "Date"])
        table.setRowCount(len(preds))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget { border: none; }
            QTableWidget::item { padding: 8px; }
            QHeaderView::section { background: #FF6D00; color: white; padding: 10px; font-weight: 700; border: none; }
        """)

        for r, pred in enumerate(preds):
            user_str = pred.get('email', '').split('@')[0] + '...'
            vals = [
                user_str,
                f"{pred.get('area', 0):.0f} m²",
                str(pred.get('bedrooms', '')),
                pred.get('model_used', '').replace('_', ' ')[:20],
                f"{pred.get('predicted_price', 0):,.0f} MAD",
                pred.get('price_category', '—'),
                str(pred.get('created_at', ''))[:16],
            ]
            for c, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                if c == 4:
                    item.setForeground(QColor('#1565C0'))
                table.setItem(r, c, item)

        layout.addWidget(table)
        return tab

    def _build_messages_tab(self) -> QWidget:
        tab = QWidget()
        tab.setStyleSheet("background: white;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        lbl = QLabel("Messages reçus par l'administration")
        lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #0D2F6E;")
        layout.addWidget(lbl)

        msgs = self.main_window.db.get_admin_messages() if self.main_window.db else []

        if not msgs:
            empty = QLabel("Aucun message reçu.")
            empty.setStyleSheet("color: #9E9E9E; font-size: 14px;")
            empty.setAlignment(Qt.AlignCenter)
            layout.addWidget(empty)
        else:
            for msg in msgs[:20]:
                msg_frame = QFrame()
                msg_frame.setStyleSheet("background: #F8FAFF; border: 1px solid #E0E0E0; border-radius: 10px;")
                mfl = QVBoxLayout(msg_frame)
                mfl.setContentsMargins(14, 12, 14, 12)
                mfl.setSpacing(6)

                from_lbl = QLabel(f"De : {msg.get('sender_email', '?')}  •  {str(msg.get('created_at', ''))[:16]}")
                from_lbl.setStyleSheet("font-size: 11px; color: #546E7A; font-weight: 600;")
                mfl.addWidget(from_lbl)

                content_lbl = QLabel(msg.get('content', ''))
                content_lbl.setStyleSheet("font-size: 13px; color: #1A1A2E;")
                content_lbl.setWordWrap(True)
                mfl.addWidget(content_lbl)

                layout.addWidget(msg_frame)

        # Zone de réponse
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: #E0E0E0;")
        layout.addWidget(sep)

        reply_lbl = QLabel("Envoyer un message à un utilisateur :")
        reply_lbl.setStyleSheet("font-size: 13px; font-weight: 700; color: #0D2F6E;")
        layout.addWidget(reply_lbl)

        users = self.main_window.db.get_all_users() if self.main_window.db else []
        self.reply_to = QComboBox()
        for u in users:
            if u.get('role') != 'admin':
                self.reply_to.addItem(u.get('email', ''), u.get('id'))
        self.reply_to.setStyleSheet("border: 1.5px solid #E0E0E0; border-radius: 8px; padding: 6px 10px; background: white;")
        layout.addWidget(self.reply_to)

        self.reply_input = QTextEdit()
        self.reply_input.setPlaceholderText("Écrivez votre message...")
        self.reply_input.setFixedHeight(80)
        self.reply_input.setStyleSheet("border: 1.5px solid #E0E0E0; border-radius: 8px; padding: 8px; background: white;")
        layout.addWidget(self.reply_input)

        send_btn = QPushButton("Envoyer le message")
        send_btn.setStyleSheet("""
            QPushButton { background: #1565C0; color: white; border: none; border-radius: 8px; padding: 8px 18px; font-weight: 600; }
            QPushButton:hover { background: #0D47A1; }
        """)
        send_btn.setCursor(Qt.PointingHandCursor)
        send_btn.clicked.connect(self._send_admin_message)
        layout.addWidget(send_btn)
        layout.addStretch()

        return tab

    def _send_admin_message(self):
        admin = self.main_window.current_user
        if not admin:
            return
        content = self.reply_input.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "Erreur", "Écrivez un message.")
            return
        receiver_id = self.reply_to.currentData()
        if not receiver_id:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un destinataire.")
            return
        ok = self.main_window.db.send_message(admin['id'], receiver_id, content)
        if ok:
            self.reply_input.clear()
            QMessageBox.information(self, "Envoyé", "Message envoyé avec succès.")

    def _build_ml_tab(self) -> QWidget:
        """Redirection vers la page Modèles ML complète."""
        tab = QWidget()
        tab.setStyleSheet("background: white;")
        layout = QVBoxLayout(tab)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)

        info = QLabel("Consultez les métriques complètes dans la page dédiée :")
        info.setStyleSheet("color: #546E7A; font-size: 14px;")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

        btn = QPushButton("Ouvrir la page Modèles ML")
        btn.setFixedHeight(48)
        btn.setStyleSheet("""
            QPushButton { background: #1565C0; color: white; border: none; border-radius: 10px;
                font-size: 14px; font-weight: 700; min-width: 260px; }
            QPushButton:hover { background: #0D47A1; }
        """)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda: self.main_window.navigate_to(6))
        layout.addWidget(btn)

        # Résumé rapide
        metadata = {}
        try:
            if self.main_window.predictor:
                metadata = self.main_window.predictor.get_model_metrics()
        except Exception:
            pass

        if metadata:
            best = metadata.get('best_regression_model', '').replace('_', ' ').title()
            reg = metadata.get('regression', {})
            best_metrics = reg.get(metadata.get('best_regression_model', ''), {})

            summary = QFrame()
            summary.setStyleSheet("background: #E3F2FD; border-radius: 12px; margin-top: 16px;")
            sl = QVBoxLayout(summary)
            sl.setContentsMargins(20, 16, 20, 16)
            sl.setSpacing(6)

            QLabel(f"Meilleur modèle : {best}").setParent(summary)
            title_lbl = QLabel(f"Meilleur modèle sélectionné : {best}")
            title_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #1565C0;")
            sl.addWidget(title_lbl)

            if best_metrics:
                r2   = best_metrics.get('r2', 0)
                rmse = best_metrics.get('rmse', 0)
                m1 = QLabel(f"R² = {r2:.4f}   |   RMSE = {rmse:,.0f}")
                m1.setStyleSheet("font-size: 13px; color: #0D2F6E;")
                sl.addWidget(m1)

            layout.addWidget(summary)

        return tab
