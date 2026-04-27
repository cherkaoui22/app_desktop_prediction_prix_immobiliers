"""
=============================================================================
FICHIER : app/pages/page_model_info.py
RÔLE    : Page d'informations sur les modèles ML (admin seulement)
          - Métriques R², RMSE, MAE pour régression
          - Accuracy, F1, Precision, Recall pour classification
          - Matrices de confusion
          - Meilleur modèle sélectionné
=============================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from app.widgets.sidebar import Sidebar


class PageModelInfo(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = Sidebar(self.main_window, active_page='model_info')
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
        # Reconstruire sidebar
        root_layout = self.layout()
        old_sb = root_layout.itemAt(0).widget()
        if old_sb:
            old_sb.deleteLater()
        new_sb = Sidebar(self.main_window, active_page='model_info')
        root_layout.insertWidget(0, new_sb)

        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Header
        title = QLabel("Analyse des Modèles ML")
        title.setObjectName("title")
        self.main_layout.addWidget(title)

        sub = QLabel("Comparaison complète des performances de tous les modèles entraînés")
        sub.setObjectName("subtitle")
        self.main_layout.addWidget(sub)

        # Charger les métriques
        metadata = {}
        try:
            if self.main_window.predictor:
                metadata = self.main_window.predictor.get_model_metrics()
        except Exception:
            pass

        if not metadata:
            lbl = QLabel("Aucune métrique disponible.\nExécutez d'abord src/train_model.py")
            lbl.setStyleSheet("color: #9E9E9E; font-size: 14px;")
            lbl.setAlignment(Qt.AlignCenter)
            self.main_layout.addWidget(lbl)
            return

        # ── Meilleur modèle ───────────────────────────────────────
        best = metadata.get('best_regression_model', '').replace('_', ' ').title()
        best_card = QFrame()
        best_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1565C0, stop:1 #0D47A1);
                border-radius: 14px;
            }
        """)
        bl = QHBoxLayout(best_card)
        bl.setContentsMargins(24, 18, 24, 18)

        best_lbl = QLabel(f"Meilleur modèle sélectionné : {best}")
        best_lbl.setStyleSheet("color: white; font-size: 16px; font-weight: 700;")
        bl.addWidget(best_lbl)
        bl.addStretch()

        badge = QLabel("ACTIF")
        badge.setStyleSheet("""
            background: #FF6D00;
            color: white;
            border-radius: 8px;
            padding: 4px 14px;
            font-size: 12px;
            font-weight: 800;
        """)
        bl.addWidget(badge)
        self.main_layout.addWidget(best_card)

        # ── Tabs Régression  ─────────────────────
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { background: white; border: 1px solid #E0E0E0; border-radius: 10px; }
            QTabBar::tab { background: #F0F4FF; color: #546E7A; padding: 10px 24px; border-radius: 6px 6px 0 0; font-weight: 600; }
            QTabBar::tab:selected { background: #1565C0; color: white; }
        """)
        self.main_layout.addWidget(tabs)

        # Tab Régression
        reg_tab = QWidget()
        reg_tab.setStyleSheet("background: white;")
        reg_layout = QVBoxLayout(reg_tab)
        reg_layout.setContentsMargins(20, 20, 20, 20)
        reg_layout.setSpacing(16)
        tabs.addTab(reg_tab, "Régression (Prix continu)")

        reg_data = metadata.get('regression', {})
        if reg_data:
            reg_table = QTableWidget()
            reg_table.setColumnCount(4)
            reg_table.setHorizontalHeaderLabels(["Modèle", "R² Score", "RMSE", "MAE"])
            reg_table.setRowCount(len(reg_data))
            reg_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            reg_table.verticalHeader().setVisible(False)
            reg_table.setEditTriggers(QTableWidget.NoEditTriggers)
            reg_table.setAlternatingRowColors(True)
            reg_table.setStyleSheet("""
                QTableWidget { border: none; }
                QTableWidget::item { padding: 12px; }
                QHeaderView::section { background: #1565C0; color: white; padding: 10px; font-weight: 700; border: none; }
            """)

            best_r2 = max((v.get('r2', -999) for v in reg_data.values()), default=0)

            for r, (name, metrics) in enumerate(reg_data.items()):
                display_name = name.replace('_', ' ').title()
                r2   = metrics.get('r2', 0)
                rmse = metrics.get('rmse', 0)
                mae  = metrics.get('mae', 0)

                items = [
                    QTableWidgetItem(display_name),
                    QTableWidgetItem(f"{r2:.4f}"),
                    QTableWidgetItem(f"{rmse:,.0f}"),
                    QTableWidgetItem(f"{mae:,.0f}"),
                ]
                for col, item in enumerate(items):
                    item.setTextAlignment(Qt.AlignCenter)
                    if r2 == best_r2:
                        item.setBackground(QColor('#E8F5E9'))
                        if col == 1:
                            item.setForeground(QColor('#2E7D32'))
                            font = item.font()
                            font.setBold(True)
                            item.setFont(font)
                    reg_table.setItem(r, col, item)

            reg_layout.addWidget(QLabel("Résultats de la régression (prédiction du prix continu)"))
            reg_layout.addWidget(reg_table)


        self.main_layout.addStretch()
