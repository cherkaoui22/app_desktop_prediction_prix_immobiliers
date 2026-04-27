"""
=============================================================================
FICHIER : src/theme.py
RÔLE    : Thème global de l'application
          Palette : Bleu #1565C0 + Blanc + Orange #FF6D00
          Typographie, espacements, animations CSS
=============================================================================
"""

# ── Palette de couleurs ──────────────────────────────────────────────────────
COLORS = {
    'primary':       '#1565C0',   # Bleu principal
    'primary_dark':  '#0D47A1',   # Bleu foncé
    'primary_light': '#E3F2FD',   # Bleu très clair
    'accent':        '#FF6D00',   # Orange accent
    'accent_dark':   '#E65100',   # Orange foncé
    'success':       '#2E7D32',   # Vert
    'warning':       '#F57F17',   # Jaune
    'danger':        '#C62828',   # Rouge
    'bg':            '#F8FAFF',   # Fond général
    'bg_white':      '#FFFFFF',   # Blanc pur
    'text':          '#1A1A2E',   # Texte principal
    'text_sub':      '#546E7A',   # Texte secondaire
    'border':        '#E0E0E0',   # Bordures
    'sidebar_bg':    '#0D2F6E',   # Fond sidebar
    'sidebar_hover': '#1565C0',   # Hover sidebar
    'sidebar_active':'#1976D2',   # Actif sidebar
    'sidebar_text':  '#B3C8F5',   # Texte sidebar
}

# ── Stylesheet principal ─────────────────────────────────────────────────────
STYLESHEET = f"""
/* ════════════════════════════════════════════════════════
   APPLICATION GLOBALE
   ════════════════════════════════════════════════════════ */
QWidget {{
    background-color: {COLORS['bg']};
    color: {COLORS['text']};
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 13px;
}}

QMainWindow {{
    background-color: {COLORS['bg']};
}}

/* ════════════════════════════════════════════════════════
   BOUTONS
   ════════════════════════════════════════════════════════ */
QPushButton {{
    border: none;
    border-radius: 8px;
    padding: 10px 22px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
}}

QPushButton#btn_primary {{
    background-color: {COLORS['accent']};
    color: white;
    min-height: 38px;
}}
QPushButton#btn_primary:hover  {{ background-color: {COLORS['accent_dark']}; }}
QPushButton#btn_primary:pressed{{ background-color: #BF360C; }}
QPushButton#btn_primary:disabled {{ background-color: #BDBDBD; }}

QPushButton#btn_secondary {{
    background-color: {COLORS['primary']};
    color: white;
    min-height: 38px;
}}
QPushButton#btn_secondary:hover  {{ background-color: {COLORS['primary_dark']}; }}
QPushButton#btn_secondary:pressed{{ background-color: #0A2E6E; }}

QPushButton#btn_ghost {{
    background-color: transparent;
    color: {COLORS['primary']};
    border: 1.5px solid {COLORS['primary']};
    min-height: 36px;
}}
QPushButton#btn_ghost:hover {{ background-color: {COLORS['primary_light']}; }}

QPushButton#btn_danger {{
    background-color: {COLORS['danger']};
    color: white;
}}
QPushButton#btn_danger:hover {{ background-color: #B71C1C; }}

QPushButton#btn_success {{
    background-color: {COLORS['success']};
    color: white;
}}
QPushButton#btn_success:hover {{ background-color: #1B5E20; }}

QPushButton#btn_flat {{
    background-color: transparent;
    color: {COLORS['text_sub']};
    font-weight: normal;
    padding: 6px 12px;
}}
QPushButton#btn_flat:hover {{
    color: {COLORS['primary']};
    background-color: {COLORS['primary_light']};
    border-radius: 6px;
}}

/* ════════════════════════════════════════════════════════
   CHAMPS DE SAISIE
   ════════════════════════════════════════════════════════ */
QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    border: 1.5px solid {COLORS['border']};
    border-radius: 8px;
    padding: 9px 14px;
    background-color: #FFFFFF;
    color: {COLORS['text']};
    font-size: 13px;
    min-height: 36px;
}}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus,
QDoubleSpinBox:focus, QComboBox:focus {{
    border: 2px solid {COLORS['primary']};
    background-color: #FAFCFF;
}}
QLineEdit:disabled, QComboBox:disabled {{
    background-color: #F5F5F5;
    color: #9E9E9E;
}}
QComboBox::drop-down {{
    border: none;
    padding-right: 8px;
}}
QComboBox QAbstractItemView {{
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    background: white;
    selection-background-color: {COLORS['primary_light']};
    selection-color: {COLORS['primary']};
}}

/* ════════════════════════════════════════════════════════
   TABLEAUX
   ════════════════════════════════════════════════════════ */
QTableWidget {{
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    gridline-color: #F0F4FF;
    background-color: #FFFFFF;
    alternate-background-color: #F8FAFF;
}}
QTableWidget::item {{
    padding: 8px;
}}
QTableWidget::item:selected {{
    background-color: {COLORS['primary_light']};
    color: {COLORS['primary_dark']};
}}
QHeaderView::section {{
    background-color: {COLORS['primary']};
    color: white;
    padding: 10px 12px;
    border: none;
    font-weight: 700;
    font-size: 12px;
}}

/* ════════════════════════════════════════════════════════
   SCROLLBAR
   ════════════════════════════════════════════════════════ */
QScrollBar:vertical {{
    width: 6px;
    background: transparent;
    border-radius: 3px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: #BDBDBD;
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: {COLORS['primary']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

QScrollBar:horizontal {{
    height: 6px;
    background: transparent;
}}
QScrollBar::handle:horizontal {{
    background: #BDBDBD;
    border-radius: 3px;
}}

/* ════════════════════════════════════════════════════════
   SIDEBAR
   ════════════════════════════════════════════════════════ */
QWidget#sidebar {{
    background-color: {COLORS['sidebar_bg']};
    border-right: 1px solid #1A3A7A;
}}

QPushButton#sidebar_btn {{
    background-color: transparent;
    color: {COLORS['sidebar_text']};
    border: none;
    text-align: left;
    padding: 13px 20px 13px 24px;
    font-size: 13px;
    font-weight: 500;
    border-radius: 0;
    min-height: 44px;
}}
QPushButton#sidebar_btn:hover {{
    background-color: {COLORS['sidebar_hover']};
    color: white;
}}

QPushButton#sidebar_btn_active {{
    background-color: {COLORS['sidebar_active']};
    color: white;
    border-left: 4px solid {COLORS['accent']};
    font-weight: 700;
    padding-left: 20px;
}}

/* ════════════════════════════════════════════════════════
   CARDS ET FRAMES
   ════════════════════════════════════════════════════════ */
QFrame#card {{
    background-color: #FFFFFF;
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
}}
QFrame#card_blue {{
    background-color: {COLORS['primary_light']};
    border: 1px solid #BBDEFB;
    border-radius: 12px;
}}
QFrame#card_accent {{
    background-color: #FFF3E0;
    border: 1px solid #FFE0B2;
    border-radius: 12px;
}}
QFrame#card_success {{
    background-color: #E8F5E9;
    border: 1px solid #C8E6C9;
    border-radius: 12px;
}}
QFrame#result_frame {{
    background-color: #E8F5E9;
    border: 2px solid {COLORS['success']};
    border-radius: 16px;
}}
QFrame#divider {{
    background-color: {COLORS['border']};
    max-height: 1px;
    min-height: 1px;
}}

/* ════════════════════════════════════════════════════════
   LABELS
   ════════════════════════════════════════════════════════ */
QLabel#title {{
    font-size: 24px;
    font-weight: 800;
    color: {COLORS['primary_dark']};
    letter-spacing: -0.5px;
}}
QLabel#subtitle {{
    font-size: 14px;
    color: {COLORS['text_sub']};
    font-weight: 400;
}}
QLabel#section_title {{
    font-size: 14px;
    font-weight: 700;
    color: {COLORS['primary']};
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
QLabel#result_price {{
    font-size: 36px;
    font-weight: 900;
    color: {COLORS['success']};
    letter-spacing: -1px;
}}
QLabel#badge_blue {{
    background-color: {COLORS['primary_light']};
    color: {COLORS['primary']};
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 700;
}}
QLabel#badge_orange {{
    background-color: #FFF3E0;
    color: {COLORS['accent']};
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 700;
}}
QLabel#badge_green {{
    background-color: #E8F5E9;
    color: {COLORS['success']};
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 700;
}}
QLabel#stat_value {{
    font-size: 28px;
    font-weight: 800;
    color: {COLORS['primary']};
}}
QLabel#stat_label {{
    font-size: 12px;
    color: {COLORS['text_sub']};
    font-weight: 500;
}}
QLabel#error_msg {{
    color: {COLORS['danger']};
    font-size: 12px;
}}
QLabel#nav_logo {{
    font-size: 16px;
    font-weight: 800;
    color: white;
    padding: 0 8px;
}}

/* ════════════════════════════════════════════════════════
   CHECKBOX
   ════════════════════════════════════════════════════════ */
QCheckBox {{
    spacing: 8px;
    font-size: 13px;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {COLORS['border']};
    border-radius: 4px;
    background: white;
}}
QCheckBox::indicator:checked {{
    background-color: {COLORS['primary']};
    border-color: {COLORS['primary']};
}}

/* ════════════════════════════════════════════════════════
   TABS
   ════════════════════════════════════════════════════════ */
QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    background: white;
}}
QTabBar::tab {{
    background: #F0F4FF;
    color: {COLORS['text_sub']};
    padding: 8px 20px;
    margin-right: 2px;
    border-radius: 6px 6px 0 0;
    font-weight: 600;
    font-size: 12px;
}}
QTabBar::tab:selected {{
    background: {COLORS['primary']};
    color: white;
}}
QTabBar::tab:hover:!selected {{
    background: {COLORS['primary_light']};
    color: {COLORS['primary']};
}}

/* ════════════════════════════════════════════════════════
   MESSAGEBOX / DIALOGS
   ════════════════════════════════════════════════════════ */
QMessageBox {{
    background-color: white;
}}
QMessageBox QPushButton {{
    min-width: 80px;
    padding: 8px 16px;
}}

/* ════════════════════════════════════════════════════════
   PROGRESS BAR
   ════════════════════════════════════════════════════════ */
QProgressBar {{
    border: none;
    border-radius: 4px;
    background: #E0E0E0;
    height: 8px;
    text-align: center;
    font-size: 0px;
}}
QProgressBar::chunk {{
    background: {COLORS['primary']};
    border-radius: 4px;
}}

/* ════════════════════════════════════════════════════════
   TOOLTIPS
   ════════════════════════════════════════════════════════ */
QToolTip {{
    background-color: {COLORS['primary_dark']};
    color: white;
    border: none;
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 12px;
}}
"""

DARK_STYLESHEET = STYLESHEET.replace(
    f"background-color: {COLORS['bg']};", "background-color: #121218;"
).replace(
    "background-color: #FFFFFF;", "background-color: #1E1E2E;"
).replace(
    f"color: {COLORS['text']};", "color: #E8EAF6;"
).replace(
    "background-color: #F8FAFF;", "background-color: #1A1A28;"
).replace(
    "background-color: #FAFCFF;", "background-color: #1E1E30;"
).replace(
    f"background-color: {COLORS['primary_light']};", "background-color: #1A2A4A;"
).replace(
    "background-color: #F0F4FF;", "background-color: #1A1A28;"
).replace(
    "background: white;", "background: #1E1E2E;"
)
