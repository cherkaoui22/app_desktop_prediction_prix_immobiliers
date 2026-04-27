"""
=============================================================================
FICHIER : app/pages/page_predict.py
RÔLE    : Page de prédiction — cœur ML de l'application
          - Formulaire de saisie des caractéristiques
          - Choix du modèle ML
          - Upload photo du bien
          - Prédiction + confirmation sauvegarde
          - Affichage résultat avec catégorie et message IA
=============================================================================
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox,
    QFileDialog, QScrollArea, QGridLayout, QMessageBox, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from app.widgets.sidebar import Sidebar

LABEL_STYLE = "font-size: 13px; font-weight: 600; color: #37474F;"
INPUT_STYLE = """
    QSpinBox, QDoubleSpinBox, QComboBox {
        border: 1.5px solid #E0E0E0;
        border-radius: 8px;
        padding: 6px 10px;
        background: white;
        font-size: 13px;
        min-height: 36px;
    }
    QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
        border: 2px solid #1565C0;
    }
"""


class PagePredict(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window  = main_window
        self._last_result = None
        self._photo_path  = None
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = Sidebar(self.main_window, active_page='predict')
        root.addWidget(self.sidebar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        root.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet("background-color: #F8FAFF;")
        scroll.setWidget(content)

        self.layout_main = QVBoxLayout(content)
        self.layout_main.setContentsMargins(36, 32, 36, 32)
        self.layout_main.setSpacing(20)

        # ── En-tête ───────────────────────────────────────────────
        title = QLabel("Prédiction du prix immobilier")
        title.setObjectName("title")
        self.layout_main.addWidget(title)

        sub = QLabel("Renseignez les caractéristiques du bien pour obtenir une estimation IA")
        sub.setObjectName("subtitle")
        self.layout_main.addWidget(sub)

        # ── Deux colonnes ─────────────────────────────────────────
        cols = QHBoxLayout()
        cols.setSpacing(20)
        self.layout_main.addLayout(cols)

        # ── Colonne gauche : formulaire ───────────────────────────
        left_card = QFrame()
        left_card.setObjectName("card")
        left_card.setStyleSheet("QFrame#card { background: white; border: 1px solid #E0E0E0; border-radius: 14px; }")
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(24, 22, 24, 22)
        left_layout.setSpacing(14)
        cols.addWidget(left_card, 6)

        # Titre section
        sec1 = QLabel("Caractéristiques du bien")
        sec1.setStyleSheet("font-size: 14px; font-weight: 700; color: #1565C0; border-bottom: 2px solid #E3F2FD; padding-bottom: 8px;")
        left_layout.addWidget(sec1)

        # Grid numérique
        grid = QGridLayout()
        grid.setSpacing(12)

        # Area
        area_lbl = QLabel("Surface (m²)")
        area_lbl.setStyleSheet(LABEL_STYLE)
        self.spin_area = QDoubleSpinBox()
        self.spin_area.setRange(50, 100000)
        self.spin_area.setValue(1500)
        self.spin_area.setSuffix(" m²")
        self.spin_area.setDecimals(0)
        self.spin_area.setStyleSheet(INPUT_STYLE)

        # Bedrooms
        bed_lbl = QLabel("Chambres")
        bed_lbl.setStyleSheet(LABEL_STYLE)
        self.spin_bed = QSpinBox()
        self.spin_bed.setRange(1, 20)
        self.spin_bed.setValue(3)
        self.spin_bed.setStyleSheet(INPUT_STYLE)

        # Bathrooms
        bath_lbl = QLabel("Salles de bain")
        bath_lbl.setStyleSheet(LABEL_STYLE)
        self.spin_bath = QSpinBox()
        self.spin_bath.setRange(1, 10)
        self.spin_bath.setValue(2)
        self.spin_bath.setStyleSheet(INPUT_STYLE)

        # Stories
        stor_lbl = QLabel("Étages")
        stor_lbl.setStyleSheet(LABEL_STYLE)
        self.spin_stories = QSpinBox()
        self.spin_stories.setRange(1, 20)
        self.spin_stories.setValue(2)
        self.spin_stories.setStyleSheet(INPUT_STYLE)

        # Parking
        park_lbl = QLabel("Places parking")
        park_lbl.setStyleSheet(LABEL_STYLE)
        self.spin_parking = QSpinBox()
        self.spin_parking.setRange(0, 10)
        self.spin_parking.setValue(1)
        self.spin_parking.setStyleSheet(INPUT_STYLE)

        for r, (l, w) in enumerate([
            (area_lbl, self.spin_area),
            (bed_lbl, self.spin_bed),
            (bath_lbl, self.spin_bath),
            (stor_lbl, self.spin_stories),
            (park_lbl, self.spin_parking),
        ]):
            grid.addWidget(l, r, 0)
            grid.addWidget(w, r, 1)
        left_layout.addLayout(grid)

        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #F0F4FF;")
        left_layout.addWidget(sep)

        # Options (checkboxes)
        sec2 = QLabel("Équipements & Options")
        sec2.setStyleSheet("font-size: 14px; font-weight: 700; color: #1565C0;")
        left_layout.addWidget(sec2)

        chk_grid = QGridLayout()
        chk_grid.setSpacing(8)

        checks = [
            ('mainroad',        'Route principale'),
            ('guestroom',       'Chambre d\'hôtes'),
            ('basement',        'Sous-sol'),
            ('hotwaterheating', 'Chauffe-eau'),
            ('airconditioning', 'Climatisation'),
            ('prefarea',        'Zone préférentielle'),
        ]
        self.checkboxes = {}
        for i, (key, label) in enumerate(checks):
            chk = QCheckBox(label)
            chk.setStyleSheet("font-size: 13px; color: #37474F;")
            self.checkboxes[key] = chk
            r, c = divmod(i, 2)
            chk_grid.addWidget(chk, r, c)
        left_layout.addLayout(chk_grid)

        # Meublé
        furn_lbl = QLabel("État de la propriété")
        furn_lbl.setStyleSheet(LABEL_STYLE)
        left_layout.addWidget(furn_lbl)

        self.combo_furn = QComboBox()
        self.combo_furn.addItems(["Non meublé", "Semi-meublé", "Meublé"])
        self.combo_furn.setCurrentIndex(1)
        self.combo_furn.setStyleSheet(INPUT_STYLE)
        left_layout.addWidget(self.combo_furn)

        # ── Colonne droite : modèle + photo + résultat ────────────
        right_col = QVBoxLayout()
        right_col.setSpacing(16)
        cols.addLayout(right_col, 4)

        # Card modèle
        model_card = QFrame()
        model_card.setStyleSheet("QFrame { background: white; border: 1px solid #E0E0E0; border-radius: 14px; }")
        ml = QVBoxLayout(model_card)
        ml.setContentsMargins(20, 18, 20, 18)
        ml.setSpacing(12)

        model_title = QLabel("Choix du modèle ML")
        model_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #1565C0;")
        ml.addWidget(model_title)

        model_desc = QLabel("Sélectionnez l'algorithme à utiliser pour la prédiction")
        model_desc.setStyleSheet("font-size: 11px; color: #9E9E9E;")
        model_desc.setWordWrap(True)
        ml.addWidget(model_desc)

        self.model_combo = QComboBox()
        models_available = []
        try:
            if self.main_window.predictor:
                models_available = self.main_window.predictor.get_available_models()
        except Exception:
            pass
        if not models_available:
            models_available = ['Régression Linéaire', 'KNN Régression', 'Arbre de Décision', 'Forêt Aléatoire']
        self.model_combo.addItems(models_available)
        self.model_combo.setStyleSheet("""
            QComboBox {
                border: 1.5px solid #E0E0E0;
                border-radius: 8px;
                padding: 8px 12px;
                background: white;
                font-size: 13px;
                min-height: 38px;
            }
            QComboBox:focus { border: 2px solid #1565C0; }
        """)
        ml.addWidget(self.model_combo)

        # Info modèles rapide
        self.model_info_lbl = QLabel("")
        self.model_info_lbl.setStyleSheet("font-size: 11px; color: #546E7A;")
        self.model_info_lbl.setWordWrap(True)
        ml.addWidget(self.model_info_lbl)
        self.model_combo.currentTextChanged.connect(self._update_model_info)
        self._update_model_info(self.model_combo.currentText())

        right_col.addWidget(model_card)

        # Card photo
        photo_card = QFrame()
        photo_card.setStyleSheet("QFrame { background: white; border: 1px solid #E0E0E0; border-radius: 14px; }")
        pl = QVBoxLayout(photo_card)
        pl.setContentsMargins(20, 18, 20, 18)
        pl.setSpacing(10)

        photo_title = QLabel("Photo du bien (optionnel)")
        photo_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #1565C0;")
        pl.addWidget(photo_title)

        self.photo_preview = QLabel("Aucune photo sélectionnée")
        self.photo_preview.setFixedHeight(120)
        self.photo_preview.setAlignment(Qt.AlignCenter)
        self.photo_preview.setStyleSheet("""
            border: 2px dashed #BDBDBD;
            border-radius: 10px;
            color: #9E9E9E;
            font-size: 12px;
            background: #FAFAFA;
        """)
        pl.addWidget(self.photo_preview)

        photo_btn = QPushButton("Choisir une photo")
        photo_btn.setStyleSheet("""
            QPushButton {
                background: #E3F2FD;
                color: #1565C0;
                border: none;
                border-radius: 8px;
                padding: 8px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover { background: #BBDEFB; }
        """)
        photo_btn.setCursor(Qt.PointingHandCursor)
        photo_btn.clicked.connect(self._choose_photo)
        pl.addWidget(photo_btn)
        right_col.addWidget(photo_card)

        # ── Bouton Prédire ────────────────────────────────────────
        self.predict_btn = QPushButton("  Lancer la prédiction")
        self.predict_btn.setFixedHeight(52)
        self.predict_btn.setStyleSheet("""
            QPushButton {
                background-color: #1565C0;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 700;
            }
            QPushButton:hover { background-color: #0D47A1; }
            QPushButton:pressed { background-color: #0A2E6E; }
        """)
        self.predict_btn.setCursor(Qt.PointingHandCursor)
        self.predict_btn.clicked.connect(self._do_predict)
        self.layout_main.addWidget(self.predict_btn)

        # ── Zone résultat ─────────────────────────────────────────
        self.result_frame = QFrame()
        self.result_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #2E7D32;
                border-radius: 16px;
            }
        """)
        self.result_frame.hide()
        rl = QVBoxLayout(self.result_frame)
        rl.setContentsMargins(28, 24, 28, 24)
        rl.setSpacing(10)

        result_top = QHBoxLayout()
        result_icon = QLabel("Résultat de la prédiction")
        result_icon.setStyleSheet("font-size: 16px; font-weight: 700; color: #1B5E20;")
        result_top.addWidget(result_icon)
        result_top.addStretch()

        self.result_model_lbl = QLabel("")
        self.result_model_lbl.setStyleSheet("""
            background: #E3F2FD;
            color: #1565C0;
            border-radius: 10px;
            padding: 4px 12px;
            font-size: 11px;
            font-weight: 700;
        """)
        result_top.addWidget(self.result_model_lbl)
        rl.addLayout(result_top)

        self.price_lbl = QLabel("0 MAD")
        self.price_lbl.setObjectName("result_price")
        self.price_lbl.setStyleSheet("font-size: 38px; font-weight: 900; color: #2E7D32;")
        rl.addWidget(self.price_lbl)

        row_info = QHBoxLayout()
        self.cat_lbl = QLabel("")
        self.cat_lbl.setStyleSheet("""
            background: #E8F5E9;
            color: #2E7D32;
            border-radius: 10px;
            padding: 4px 14px;
            font-size: 13px;
            font-weight: 700;
        """)
        row_info.addWidget(self.cat_lbl)
        row_info.addStretch()
        rl.addLayout(row_info)

        self.ai_msg_lbl = QLabel("")
        self.ai_msg_lbl.setStyleSheet("font-size: 13px; color: #546E7A; font-style: italic;")
        self.ai_msg_lbl.setWordWrap(True)
        rl.addWidget(self.ai_msg_lbl)

        # Séparateur
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("background-color: #E0E0E0;")
        rl.addWidget(sep2)

        # Boutons résultat
        btn_row_res = QHBoxLayout()
        self.confirm_btn = QPushButton("Confirmer et sauvegarder")
        self.confirm_btn.setFixedHeight(44)
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6D00;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 700;
            }
            QPushButton:hover { background-color: #E65100; }
        """)
        self.confirm_btn.setCursor(Qt.PointingHandCursor)
        self.confirm_btn.clicked.connect(self._do_confirm)

        new_pred_btn = QPushButton("Nouvelle prédiction")
        new_pred_btn.setFixedHeight(44)
        new_pred_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #1565C0;
                border: 1.5px solid #1565C0;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover { background: #E3F2FD; }
        """)
        new_pred_btn.setCursor(Qt.PointingHandCursor)
        new_pred_btn.clicked.connect(self._reset_form)

        btn_row_res.addWidget(self.confirm_btn)
        btn_row_res.addWidget(new_pred_btn)
        rl.addLayout(btn_row_res)

        self.layout_main.addWidget(self.result_frame)
        self.layout_main.addStretch()

    def _update_model_info(self, model_name: str):
        infos = {
            'Régression Linéaire': 'Rapide, idéal pour relations linéaires. Bonne interprétabilité.',
            'KNN Régression':      'Basé sur les voisins les plus proches. Bon pour données locales.',
            'Arbre de Décision':   'Modèle arborescent. Facile à interpréter.',
            'Forêt Aléatoire':     'Ensemble d\'arbres. Robuste et précis.',
        }
        self.model_info_lbl.setText(infos.get(model_name, ''))

    def _choose_photo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Choisir une photo",
            os.path.expanduser("~"),
            "Images (*.png *.jpg *.jpeg *.webp *.bmp)"
        )
        if path:
            self._photo_path = path
            pix = QPixmap(path)
            if not pix.isNull():
                self.photo_preview.setPixmap(
                    pix.scaled(300, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
                self.photo_preview.setAlignment(Qt.AlignCenter)

    def _collect_inputs(self) -> dict:
        return {
            'area':            float(self.spin_area.value()),
            'bedrooms':        self.spin_bed.value(),
            'bathrooms':       self.spin_bath.value(),
            'stories':         self.spin_stories.value(),
            'parking':         self.spin_parking.value(),
            'mainroad':        int(self.checkboxes['mainroad'].isChecked()),
            'guestroom':       int(self.checkboxes['guestroom'].isChecked()),
            'basement':        int(self.checkboxes['basement'].isChecked()),
            'hotwaterheating': int(self.checkboxes['hotwaterheating'].isChecked()),
            'airconditioning': int(self.checkboxes['airconditioning'].isChecked()),
            'prefarea':        int(self.checkboxes['prefarea'].isChecked()),
            'furnishingstatus': self.combo_furn.currentIndex(),
        }

    def _do_predict(self):
        inputs = self._collect_inputs()

        # Validation basique
        if inputs['area'] < 50:
            QMessageBox.warning(self, "Validation", "La surface doit être au moins 50 m²")
            return

        self.predict_btn.setText("  Calcul en cours...")
        self.predict_btn.setEnabled(False)
        self.result_frame.hide()

        model_name = self.model_combo.currentText()
        predictor = self.main_window.predictor

        try:
            if predictor:
                result = predictor.predict(inputs, model_name)
            else:
                # Fallback
                price = inputs['area'] * 3500 + inputs['bedrooms'] * 200_000
                result = {
                    'success': True, 'price': price,
                    'category': 'Standard', 'message': 'Estimation basée sur la surface.',
                    'model_used': model_name
                }

            self._last_result = {**result, **inputs, 'photo_path': self._photo_path or ''}
            self._show_result(result)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la prédiction :\n{e}")
        finally:
            self.predict_btn.setText("  Lancer la prédiction")
            self.predict_btn.setEnabled(True)

    def _show_result(self, result: dict):
        price = result.get('price', 0)
        self.price_lbl.setText(f"{price:,.0f} MAD")
        self.cat_lbl.setText(f"  Catégorie : {result.get('category', '')}  ")
        self.ai_msg_lbl.setText(f"IA : {result.get('message', '')}")
        self.result_model_lbl.setText(f"Modèle : {result.get('model_used', '')}")
        self.confirm_btn.setEnabled(True)
        self.confirm_btn.setText("Confirmer et sauvegarder")
        self.result_frame.show()

        # Scroll vers le résultat
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, lambda: self.result_frame.scroll(0, 0))

    def _do_confirm(self):
        if not self._last_result:
            return
        user = self.main_window.current_user
        if not user:
            QMessageBox.warning(self, "Non connecté", "Vous devez être connecté pour sauvegarder.")
            return

        data = {**self._last_result, 'confirmed': 1}
        ok = self.main_window.db.save_prediction(user['id'], data)
        if ok:
            self.confirm_btn.setText("Sauvegardé !")
            self.confirm_btn.setEnabled(False)
            self.confirm_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2E7D32;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 13px;
                    font-weight: 700;
                    min-height: 44px;
                }
            """)
        else:
            QMessageBox.warning(self, "Erreur", "Impossible de sauvegarder la prédiction.")

    def _reset_form(self):
        self.spin_area.setValue(1500)
        self.spin_bed.setValue(3)
        self.spin_bath.setValue(2)
        self.spin_stories.setValue(2)
        self.spin_parking.setValue(1)
        for chk in self.checkboxes.values():
            chk.setChecked(False)
        self.combo_furn.setCurrentIndex(1)
        self._last_result = None
        self._photo_path = None
        self.photo_preview.setText("Aucune photo sélectionnée")
        self.photo_preview.setPixmap(QPixmap())
        self.result_frame.hide()

    def on_enter(self):
        # Reconstruire sidebar
        root_layout = self.layout()
        old_sb = root_layout.itemAt(0).widget()
        if old_sb and hasattr(old_sb, 'setObjectName'):
            old_sb.deleteLater()
        new_sb = Sidebar(self.main_window, active_page='predict')
        root_layout.insertWidget(0, new_sb)
