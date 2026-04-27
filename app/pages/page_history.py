"""
=============================================================================
FICHIER : app/pages/page_history.py
RÔLE    : Historique des prédictions sauvegardées (stocké en DB)
=============================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from app.widgets.sidebar import Sidebar


class PageHistory(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = Sidebar(self.main_window, active_page='history')
        root.addWidget(self.sidebar)

        # Main content
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: #F8FAFF;")
        root.addWidget(self.content_widget)

        self.main_layout = QVBoxLayout(self.content_widget)
        self.main_layout.setContentsMargins(36, 32, 36, 32)
        self.main_layout.setSpacing(20)

    def on_enter(self):
        # Reconstruire sidebar
        root_layout = self.layout()
        old_sb = root_layout.itemAt(0).widget()
        if old_sb:
            old_sb.deleteLater()
        new_sb = Sidebar(self.main_window, active_page='history')
        root_layout.insertWidget(0, new_sb)

        # Clear layout
        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        user = self.main_window.current_user or {}

        # Header
        title = QLabel("Historique des prédictions")
        title.setObjectName("title")
        self.main_layout.addWidget(title)

        sub = QLabel("Toutes vos estimations enregistrées, triées par date")
        sub.setObjectName("subtitle")
        self.main_layout.addWidget(sub)

        # Stats rapides
        preds = self.main_window.db.get_user_predictions(user.get('id', 0)) if self.main_window.db else []

        stats_row = QHBoxLayout()
        stats_data = [
            ("Total", str(len(preds)), "#E3F2FD", "#1565C0"),
            ("Confirmées", str(sum(1 for p in preds if p.get('confirmed'))), "#E8F5E9", "#2E7D32"),
            ("Prix moyen", f"{sum(p.get('predicted_price',0) for p in preds)/len(preds):,.0f} MAD" if preds else "—", "#FFF3E0", "#FF6D00"),
        ]
        for label, value, bg, color in stats_data:
            c = QFrame()
            c.setStyleSheet(f"background: {bg}; border: 1px solid {color}30; border-radius: 12px;")
            cl = QVBoxLayout(c)
            cl.setContentsMargins(16, 14, 16, 14)
            cl.setSpacing(4)
            QLabel(label).setParent(c)
            v_lbl = QLabel(value)
            v_lbl.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {color};")
            l_lbl = QLabel(label)
            l_lbl.setStyleSheet(f"font-size: 11px; color: {color}; font-weight: 600;")
            cl.addWidget(v_lbl)
            cl.addWidget(l_lbl)
            stats_row.addWidget(c, 1)
        self.main_layout.addLayout(stats_row)

        # Table
        if not preds:
            empty = QLabel("Aucune prédiction enregistrée.\nLancez votre première estimation depuis la page Prédiction.")
            empty.setStyleSheet("color: #9E9E9E; font-size: 14px; text-align: center;")
            empty.setAlignment(Qt.AlignCenter)
            self.main_layout.addWidget(empty)
            self.main_layout.addStretch()
            return

        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Surface (m²)", "Chambres", "Étages", "Localisation", "Modèle ML", "Prix Prédit (MAD)", "Date"
        ])
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setFrameShape(QFrame.NoFrame)
        table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid #E0E0E0;
                border-radius: 12px;
                gridline-color: #F0F4FF;
            }
            QTableWidget::item { padding: 10px; font-size: 13px; }
            QTableWidget::item:selected { background: #E3F2FD; color: #0D47A1; }
            QHeaderView::section {
                background: #1565C0;
                color: white;
                padding: 10px;
                font-weight: 700;
                border: none;
            }
            QTableWidget::item:alternate { background: #F8FAFF; }
        """)

        table.setRowCount(len(preds))
        for row, pred in enumerate(preds):
            vals = [
                f"{pred.get('area', 0):.0f}",
                str(pred.get('bedrooms', '')),
                str(pred.get('stories', '')),
                pred.get('price_category', '—'),
                pred.get('model_used', '').replace('_', ' ').title(),
                f"{pred.get('predicted_price', 0):,.0f}",
                str(pred.get('created_at', ''))[:16],
            ]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                if col == 5:  # prix
                    item.setForeground(Qt.darkGreen)
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                table.setItem(row, col, item)

        self.main_layout.addWidget(table)
