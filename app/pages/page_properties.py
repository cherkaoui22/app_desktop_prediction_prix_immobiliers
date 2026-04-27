"""
=============================================================================
FICHIER : app/pages/page_properties.py
RÔLE    : Page des annonces immobilières
          - Vue acheteur : liste des biens validés avec filtres
          - Formulaire de publication (vendeur)
          - Photos uploadables
=============================================================================
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QLineEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QTextEdit, QFileDialog, QMessageBox,
    QTabWidget, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from app.widgets.sidebar import Sidebar


class PageProperties(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._photo_paths = []
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = Sidebar(self.main_window, active_page='properties')
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
        # Sidebar refresh
        root_layout = self.layout()
        old_sb = root_layout.itemAt(0).widget()
        if old_sb:
            old_sb.deleteLater()
        new_sb = Sidebar(self.main_window, active_page='properties')
        root_layout.insertWidget(0, new_sb)

        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Header
        title = QLabel("Annonces Immobilières")
        title.setObjectName("title")
        self.main_layout.addWidget(title)

        sub = QLabel("Parcourez les biens disponibles ou publiez votre annonce")
        sub.setObjectName("subtitle")
        self.main_layout.addWidget(sub)

        # Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { background: white; border: 1px solid #E0E0E0; border-radius: 10px; }
            QTabBar::tab { background: #F0F4FF; color: #546E7A; padding: 10px 24px; border-radius: 6px 6px 0 0; font-weight: 600; }
            QTabBar::tab:selected { background: #1565C0; color: white; }
        """)
        self.main_layout.addWidget(tabs)

        # Tab 1 : Parcourir
        browse_tab = self._build_browse_tab()
        tabs.addTab(browse_tab, "Parcourir les annonces")

        # Tab 2 : Publier
        publish_tab = self._build_publish_tab()
        tabs.addTab(publish_tab, "Publier une annonce")

        # Tab 3 : Mes annonces
        my_tab = self._build_my_properties_tab()
        tabs.addTab(my_tab, "Mes annonces")

    def _build_browse_tab(self) -> QWidget:
        tab = QWidget()
        tab.setStyleSheet("background: white;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Filtres
        filter_row = QHBoxLayout()
        filter_row.setSpacing(12)

        filter_lbl = QLabel("Filtres :")
        filter_lbl.setStyleSheet("font-weight: 700; color: #1565C0;")
        filter_row.addWidget(filter_lbl)

        self.filter_type = QComboBox()
        self.filter_type.addItems(["Tous types", "vente", "location"])
        self.filter_type.setFixedWidth(140)
        self.filter_type.setStyleSheet("border: 1.5px solid #E0E0E0; border-radius: 8px; padding: 6px 10px; background: white;")
        filter_row.addWidget(self.filter_type)

        self.filter_city = QLineEdit()
        self.filter_city.setPlaceholderText("Ville...")
        self.filter_city.setFixedWidth(150)
        self.filter_city.setStyleSheet("border: 1.5px solid #E0E0E0; border-radius: 8px; padding: 6px 10px;")
        filter_row.addWidget(self.filter_city)

        self.filter_max = QLineEdit()
        self.filter_max.setPlaceholderText("Prix max (MAD)")
        self.filter_max.setFixedWidth(160)
        self.filter_max.setStyleSheet("border: 1.5px solid #E0E0E0; border-radius: 8px; padding: 6px 10px;")
        filter_row.addWidget(self.filter_max)

        search_btn = QPushButton("Rechercher")
        search_btn.setStyleSheet("""
            QPushButton {
                background: #1565C0; color: white;
                border: none; border-radius: 8px;
                padding: 8px 18px; font-weight: 600;
            }
            QPushButton:hover { background: #0D47A1; }
        """)
        search_btn.setCursor(Qt.PointingHandCursor)
        search_btn.clicked.connect(lambda: self._load_properties(layout))
        filter_row.addWidget(search_btn)
        filter_row.addStretch()
        layout.addLayout(filter_row)

        # Liste des propriétés
        self.props_container = QWidget()
        self.props_layout = QVBoxLayout(self.props_container)
        self.props_layout.setSpacing(12)
        self.props_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.props_container)

        self._load_properties(layout)
        return tab

    def _load_properties(self, parent_layout=None):
        # Vider le container
        while self.props_layout.count():
            child = self.props_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        filters = {}
        if hasattr(self, 'filter_type') and self.filter_type.currentIndex() > 0:
            filters['type'] = self.filter_type.currentText()
        if hasattr(self, 'filter_city') and self.filter_city.text().strip():
            filters['city'] = self.filter_city.text().strip()
        if hasattr(self, 'filter_max') and self.filter_max.text().strip():
            try:
                filters['max_price'] = float(self.filter_max.text().replace(' ', '').replace(',', ''))
            except ValueError:
                pass

        props = self.main_window.db.get_properties(filters) if self.main_window.db else []

        if not props:
            empty_lbl = QLabel("Aucune annonce disponible pour le moment.\nSoyez le premier à publier un bien !")
            empty_lbl.setStyleSheet("color: #9E9E9E; font-size: 14px; padding: 40px;")
            empty_lbl.setAlignment(Qt.AlignCenter)
            self.props_layout.addWidget(empty_lbl)
            return

        for prop in props:
            card = self._make_property_card(prop)
            self.props_layout.addWidget(card)

    def _make_property_card(self, prop: dict) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #E0E0E0;
                border-radius: 14px;
            }
            QFrame:hover { border-color: #1565C0; }
        """)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(16)

        # Photo placeholder
        photo_lbl = QLabel()
        photo_lbl.setFixedSize(120, 90)
        photo_lbl.setStyleSheet("background: #E3F2FD; border-radius: 10px;")
        photo_lbl.setAlignment(Qt.AlignCenter)

        photos_str = prop.get('photos', '')
        if photos_str:
            first_photo = photos_str.split('|')[0]
            if os.path.exists(first_photo):
                pix = QPixmap(first_photo)
                if not pix.isNull():
                    photo_lbl.setPixmap(pix.scaled(120, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                photo_lbl.setText("Photo\nnon\ndisponible")
                photo_lbl.setStyleSheet("background: #E3F2FD; border-radius: 10px; color: #9E9E9E; font-size: 11px;")
        else:
            photo_lbl.setText("Pas de\nphoto")
            photo_lbl.setStyleSheet("background: #F5F5F5; border-radius: 10px; color: #BDBDBD; font-size: 11px;")

        layout.addWidget(photo_lbl)

        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        title_row = QHBoxLayout()
        title_lbl = QLabel(prop.get('title', 'Bien immobilier'))
        title_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #0D2F6E;")
        title_row.addWidget(title_lbl)

        type_badge = QLabel(prop.get('transaction_type', 'vente').upper())
        type_badge.setStyleSheet("""
            background: #E3F2FD; color: #1565C0;
            border-radius: 8px; padding: 3px 10px;
            font-size: 10px; font-weight: 800;
        """)
        title_row.addWidget(type_badge)
        title_row.addStretch()
        info_layout.addLayout(title_row)

        city_lbl = QLabel(f"  {prop.get('city', 'Ville non précisée')}")
        city_lbl.setStyleSheet("color: #546E7A; font-size: 12px;")
        info_layout.addWidget(city_lbl)

        chars_lbl = QLabel(
            f"Surface: {prop.get('area', 0):.0f} m²  •  "
            f"{prop.get('bedrooms', 0)} chambres  •  "
            f"{prop.get('bathrooms', 0)} SDB"
        )
        chars_lbl.setStyleSheet("color: #78909C; font-size: 12px;")
        info_layout.addWidget(chars_lbl)

        desc = prop.get('description', '')
        if desc:
            desc_lbl = QLabel(desc[:100] + '...' if len(desc) > 100 else desc)
            desc_lbl.setStyleSheet("color: #9E9E9E; font-size: 11px;")
            desc_lbl.setWordWrap(True)
            info_layout.addWidget(desc_lbl)

        layout.addLayout(info_layout, 1)

        # Prix + contact
        right_col = QVBoxLayout()
        right_col.setAlignment(Qt.AlignCenter)
        right_col.setSpacing(8)

        price_lbl = QLabel(f"{prop.get('price', 0):,.0f}\nMAD")
        price_lbl.setStyleSheet("font-size: 18px; font-weight: 900; color: #1565C0; text-align: center;")
        price_lbl.setAlignment(Qt.AlignCenter)
        right_col.addWidget(price_lbl)

        contact_btn = QPushButton("Contacter")
        contact_btn.setStyleSheet("""
            QPushButton {
                background: #FF6D00; color: white;
                border: none; border-radius: 8px;
                padding: 8px 16px; font-weight: 600; font-size: 12px;
            }
            QPushButton:hover { background: #E65100; }
        """)
        contact_btn.setCursor(Qt.PointingHandCursor)
        contact_btn.clicked.connect(lambda checked, p=prop: self._contact_seller(p))
        right_col.addWidget(contact_btn)

        seller_lbl = QLabel(prop.get('full_name') or prop.get('email', '')[:20])
        seller_lbl.setStyleSheet("color: #9E9E9E; font-size: 10px;")
        seller_lbl.setAlignment(Qt.AlignCenter)
        right_col.addWidget(seller_lbl)

        layout.addLayout(right_col)
        return card

    def _contact_seller(self, prop: dict):
        user = self.main_window.current_user
        if not user:
            QMessageBox.warning(self, "Non connecté", "Connectez-vous pour contacter un vendeur.")
            return

        msg_content = f"Bonjour, je suis intéressé par votre bien : {prop.get('title', '')} ({prop.get('price', 0):,.0f} MAD)"
        ok = self.main_window.db.send_message(
            sender_id=user['id'],
            receiver_id=prop.get('user_id', 0),
            content=msg_content,
            property_id=prop.get('id')
        )
        if ok:
            QMessageBox.information(self, "Message envoyé", "Votre message a été envoyé au vendeur.")
        else:
            QMessageBox.warning(self, "Erreur", "Impossible d'envoyer le message.")

    def _build_publish_tab(self) -> QWidget:
        tab = QWidget()
        tab.setStyleSheet("background: white;")
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll)

        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(14)
        scroll.setWidget(form_widget)

        info_lbl = QLabel("Votre annonce sera soumise à validation par l'administrateur avant publication.")
        info_lbl.setStyleSheet("""
            background: #FFF3E0; color: #E65100;
            border: 1px solid #FFE0B2; border-radius: 8px;
            padding: 10px 14px; font-size: 12px; font-weight: 600;
        """)
        info_lbl.setWordWrap(True)
        form_layout.addWidget(info_lbl)

        def lbl(text):
            l = QLabel(text)
            l.setStyleSheet("font-weight: 600; color: #37474F; font-size: 13px;")
            return l

        inp_style = "border: 1.5px solid #E0E0E0; border-radius: 8px; padding: 8px 12px; background: white; font-size: 13px; min-height: 36px;"

        form_layout.addWidget(lbl("Titre de l'annonce *"))
        self.pub_title = QLineEdit()
        self.pub_title.setPlaceholderText("Ex: Appartement 3 pièces centre-ville")
        self.pub_title.setStyleSheet(inp_style)
        form_layout.addWidget(self.pub_title)

        form_layout.addWidget(lbl("Type de transaction *"))
        self.pub_type = QComboBox()
        self.pub_type.addItems(["vente", "location"])
        self.pub_type.setStyleSheet(inp_style)
        form_layout.addWidget(self.pub_type)

        form_layout.addWidget(lbl("Type de bien"))
        self.pub_prop_type = QComboBox()
        self.pub_prop_type.addItems(["appartement", "maison", "villa", "terrain", "local commercial"])
        self.pub_prop_type.setStyleSheet(inp_style)
        form_layout.addWidget(self.pub_prop_type)

        row2 = QHBoxLayout()
        row2.setSpacing(14)

        col_a = QVBoxLayout()
        col_a.addWidget(lbl("Prix (MAD) *"))
        self.pub_price = QDoubleSpinBox()
        self.pub_price.setRange(0, 999_999_999)
        self.pub_price.setValue(500_000)
        self.pub_price.setSuffix(" MAD")
        self.pub_price.setDecimals(0)
        self.pub_price.setStyleSheet(inp_style)
        col_a.addWidget(self.pub_price)
        row2.addLayout(col_a)

        col_b = QVBoxLayout()
        col_b.addWidget(lbl("Surface (m²) *"))
        self.pub_area = QDoubleSpinBox()
        self.pub_area.setRange(10, 100000)
        self.pub_area.setValue(100)
        self.pub_area.setSuffix(" m²")
        self.pub_area.setDecimals(0)
        self.pub_area.setStyleSheet(inp_style)
        col_b.addWidget(self.pub_area)
        row2.addLayout(col_b)

        form_layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.setSpacing(14)
        for lbl_text, attr, default in [("Chambres", 'pub_beds', 2), ("SDB", 'pub_baths', 1)]:
            col = QVBoxLayout()
            col.addWidget(lbl(lbl_text))
            spin = QSpinBox()
            spin.setRange(0, 20)
            spin.setValue(default)
            spin.setStyleSheet(inp_style)
            setattr(self, attr, spin)
            col.addWidget(spin)
            row3.addLayout(col)
        form_layout.addLayout(row3)

        form_layout.addWidget(lbl("Ville *"))
        self.pub_city = QLineEdit()
        self.pub_city.setPlaceholderText("Ex: Casablanca, Rabat, Marrakech...")
        self.pub_city.setStyleSheet(inp_style)
        form_layout.addWidget(self.pub_city)

        form_layout.addWidget(lbl("Adresse"))
        self.pub_address = QLineEdit()
        self.pub_address.setPlaceholderText("Adresse complète (optionnel)")
        self.pub_address.setStyleSheet(inp_style)
        form_layout.addWidget(self.pub_address)

        form_layout.addWidget(lbl("Description"))
        self.pub_desc = QTextEdit()
        self.pub_desc.setPlaceholderText("Décrivez votre bien : état, équipements, points forts...")
        self.pub_desc.setFixedHeight(90)
        self.pub_desc.setStyleSheet(inp_style)
        form_layout.addWidget(self.pub_desc)

        # Photos
        form_layout.addWidget(lbl("Photos du bien"))
        photo_btn = QPushButton("Choisir des photos")
        photo_btn.setStyleSheet("""
            QPushButton { background: #E3F2FD; color: #1565C0; border: none; border-radius: 8px; padding: 8px 16px; font-weight: 600; }
            QPushButton:hover { background: #BBDEFB; }
        """)
        photo_btn.setCursor(Qt.PointingHandCursor)
        photo_btn.clicked.connect(self._choose_photos)
        form_layout.addWidget(photo_btn)

        self.pub_photos_lbl = QLabel("Aucune photo sélectionnée")
        self.pub_photos_lbl.setStyleSheet("color: #9E9E9E; font-size: 12px;")
        form_layout.addWidget(self.pub_photos_lbl)

        # Submit
        self.pub_error = QLabel("")
        self.pub_error.setStyleSheet("color: #C62828; font-size: 12px;")
        self.pub_error.hide()
        form_layout.addWidget(self.pub_error)

        submit_btn = QPushButton("Soumettre l'annonce")
        submit_btn.setFixedHeight(48)
        submit_btn.setStyleSheet("""
            QPushButton { background: #FF6D00; color: white; border: none; border-radius: 10px; font-size: 15px; font-weight: 700; }
            QPushButton:hover { background: #E65100; }
        """)
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.clicked.connect(self._submit_property)
        form_layout.addWidget(submit_btn)

        return tab

    def _choose_photos(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Choisir des photos", os.path.expanduser("~"),
            "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if paths:
            self._photo_paths = paths
            self.pub_photos_lbl.setText(f"{len(paths)} photo(s) sélectionnée(s)")

    def _submit_property(self):
        user = self.main_window.current_user
        if not user:
            QMessageBox.warning(self, "Non connecté", "Connectez-vous pour publier.")
            return

        title   = self.pub_title.text().strip()
        city    = self.pub_city.text().strip()

        if not title or not city:
            self.pub_error.setText("Le titre et la ville sont obligatoires")
            self.pub_error.show()
            return

        data = {
            'title':            title,
            'description':      self.pub_desc.toPlainText().strip(),
            'property_type':    self.pub_prop_type.currentText(),
            'transaction_type': self.pub_type.currentText(),
            'price':            float(self.pub_price.value()),
            'area':             float(self.pub_area.value()),
            'bedrooms':         self.pub_beds.value(),
            'bathrooms':        self.pub_baths.value(),
            'city':             city,
            'address':          self.pub_address.text().strip(),
            'photos':           '|'.join(self._photo_paths),
        }

        ok = self.main_window.db.create_property(user['id'], data)
        if ok:
            self.pub_error.hide()
            QMessageBox.information(
                self, "Annonce soumise",
                "Votre annonce a été soumise avec succès.\n"
                "Elle sera visible après validation par l'administrateur."
            )
            self.pub_title.clear()
            self.pub_city.clear()
            self.pub_desc.clear()
            self._photo_paths = []
            self.pub_photos_lbl.setText("Aucune photo sélectionnée")
        else:
            self.pub_error.setText("Erreur lors de la soumission")
            self.pub_error.show()

    def _build_my_properties_tab(self) -> QWidget:
        tab = QWidget()
        tab.setStyleSheet("background: white;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        user = self.main_window.current_user or {}
        props = self.main_window.db.get_user_properties(user.get('id', 0)) if self.main_window.db else []

        if not props:
            empty = QLabel("Vous n'avez pas encore d'annonces.\nPubliez votre premier bien dans l'onglet 'Publier une annonce'.")
            empty.setStyleSheet("color: #9E9E9E; font-size: 14px; padding: 40px;")
            empty.setAlignment(Qt.AlignCenter)
            layout.addWidget(empty)
            return tab

        for prop in props:
            row = QFrame()
            row.setStyleSheet("background: #F8FAFF; border: 1px solid #E0E0E0; border-radius: 10px;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(16, 12, 16, 12)

            info = QLabel(f"{prop.get('title', '')}  •  {prop.get('city', '')}  •  {prop.get('price', 0):,.0f} MAD")
            info.setStyleSheet("font-size: 13px; font-weight: 600; color: #0D2F6E;")
            rl.addWidget(info)
            rl.addStretch()

            status = prop.get('status', 'pending')
            status_colors = {'active': '#2E7D32', 'pending': '#FF6D00', 'rejected': '#C62828'}
            status_labels = {'active': 'Validée', 'pending': 'En attente', 'rejected': 'Refusée'}
            s_lbl = QLabel(status_labels.get(status, status))
            s_lbl.setStyleSheet(f"""
                background: {status_colors.get(status, '#9E9E9E')}20;
                color: {status_colors.get(status, '#9E9E9E')};
                border-radius: 8px; padding: 4px 12px; font-size: 11px; font-weight: 700;
            """)
            rl.addWidget(s_lbl)
            layout.addWidget(row)

        layout.addStretch()
        return tab
