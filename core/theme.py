"""
Theme and styling definitions for the School Management System using PySide6.
Modern Slate & Indigo Enterprise Design System.
"""
import os
from PySide6.QtWidgets import (
    QPushButton, QLineEdit, QComboBox, QTextEdit, QFrame,
    QLabel, QTableWidget, QHeaderView, QWidget, QVBoxLayout, QHBoxLayout,
    QGraphicsDropShadowEffect
)
from PySide6.QtGui import QFont, QColor, QCursor, QIcon
from PySide6.QtCore import Qt

# Icon Assets
CHEVRON_DOWN_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "chevron_down.svg")).replace("\\", "/")


# Color Palette: Slate & Indigo Enterprise System
PRIMARY = "#4F46E5"          # Indigo 600 - Brand Primary
PRIMARY_DARK = "#4338CA"     # Indigo 700 - Hover / Pressed
PRIMARY_LIGHT = "#EEF2FF"    # Indigo 50 - Active Pill / Subtle Background
PRIMARY_RING = "rgba(99, 102, 241, 0.25)" # Focus glow

SECONDARY = "#10B981"        # Emerald 500 - Success
SECONDARY_DARK = "#059669"   # Emerald 600
SECONDARY_LIGHT = "#ECFDF5"  # Emerald 50

DANGER = "#EF4444"           # Rose/Red 500 - Errors & Critical Actions
DANGER_DARK = "#DC2626"      # Rose/Red 600
DANGER_LIGHT = "#FEF2F2"     # Rose/Red 50

WARNING = "#F59E0B"          # Amber 500 - Attention
WARNING_LIGHT = "#FFFBEB"    # Amber 50

INFO = "#3B82F6"             # Blue 500 - Informational
INFO_LIGHT = "#EFF6FF"       # Blue 50

# Neutral Surfaces & Canvas
BACKGROUND = "#F8FAFC"       # Slate 50 - Crisp App Canvas
SURFACE = "#FFFFFF"          # Pure White Surface for Cards
SURFACE_MUTED = "#F1F5F9"    # Slate 100 - Table Header / Input Fill
BORDER_COLOR = "#E2E8F0"     # Slate 200 - Clean 1px Hairline Border
BORDER_FOCUS = "#6366F1"     # Indigo 500 Focus Border

# Typography Colors
TEXT_PRIMARY = "#0F172A"     # Slate 900 - High Contrast Charcoal
TEXT_SECONDARY = "#64748B"   # Slate 500 - Body & Label Gray
TEXT_TERTIARY = "#94A3B8"    # Slate 400 - Muted Placeholders

# Sidebar Midnight Slate Theme
SIDEBAR_BG = "#0F172A"       # Midnight Slate 900
SIDEBAR_SECTION = "#334155"  # Slate 700
SIDEBAR_HOVER = "#1E293B"    # Slate 800
SIDEBAR_TEXT = "#94A3B8"     # Slate 400
SIDEBAR_TEXT_ACTIVE = "#FFFFFF"
SIDEBAR_ACTIVE = "#4F46E5"   # Active Nav Pill

# Global QSS Stylesheet
GLOBAL_QSS = f"""
QMainWindow {{
    background-color: {BACKGROUND};
}}

QWidget {{
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Arial, sans-serif;
    color: {TEXT_PRIMARY};
}}

/* Clean Custom Scrollbars */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0px;
}}
QScrollBar::handle:vertical {{
    background: #CBD5E1;
    min-height: 28px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical:hover {{
    background: #94A3B8;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
    margin: 0px;
}}
QScrollBar::handle:horizontal {{
    background: #CBD5E1;
    min-width: 28px;
    border-radius: 3px;
}}
QScrollBar::handle:horizontal:hover {{
    background: #94A3B8;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* Modern Borderless Striped Tables */
QTableWidget {{
    background-color: {SURFACE};
    alternate-background-color: #FAFAFA;
    gridline-color: #F1F5F9;
    border: 1px solid {BORDER_COLOR};
    border-radius: 10px;
    selection-background-color: {PRIMARY_LIGHT};
    selection-color: {PRIMARY_DARK};
    font-size: 13px;
    outline: none;
}}
QTableWidget::item {{
    padding: 4px 12px;
    border-bottom: 1px solid #F1F5F9;
}}
QTableWidget::item:selected {{
    background-color: {PRIMARY_LIGHT};
    color: {PRIMARY_DARK};
    font-weight: 600;
}}
QHeaderView::section {{
    background-color: #F8FAFC;
    color: {TEXT_SECONDARY};
    font-weight: 700;
    font-size: 11.5px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 10px 12px;
    border: none;
    border-bottom: 2px solid {BORDER_COLOR};
}}


/* Line Edit & Inputs */
QLineEdit {{
    background-color: {SURFACE};
    border: 1px solid {BORDER_COLOR};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    color: {TEXT_PRIMARY};
}}
QLineEdit:hover {{
    border-color: #94A3B8;
}}
QLineEdit:focus {{
    border: 1.5px solid {PRIMARY};
    background-color: #FFFFFF;
}}

/* Text Areas */
QTextEdit {{
    background-color: {SURFACE};
    border: 1px solid {BORDER_COLOR};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    color: {TEXT_PRIMARY};
}}
QTextEdit:hover {{
    border-color: #94A3B8;
}}
QTextEdit:focus {{
    border: 1.5px solid {PRIMARY};
}}

/* ComboBox */
QComboBox {{
    background-color: {SURFACE};
    border: 1px solid {BORDER_COLOR};
    border-radius: 8px;
    padding: 6px 32px 6px 12px;
    font-size: 13px;
    color: {TEXT_PRIMARY};
}}
QComboBox:hover {{
    border-color: #94A3B8;
}}
QComboBox:focus {{
    border: 1.5px solid {PRIMARY};
}}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border-left: none;
}}
QComboBox::down-arrow {{
    image: url("{CHEVRON_DOWN_PATH}");
    width: 11px;
    height: 11px;
}}
QComboBox QAbstractItemView {{
    background-color: {SURFACE};
    border: 1px solid {BORDER_COLOR};
    border-radius: 8px;
    selection-background-color: {PRIMARY_LIGHT};
    selection-color: {PRIMARY_DARK};
    padding: 4px;
    outline: none;
}}

/* Tab Widget */
QTabWidget::pane {{
    border: 1px solid {BORDER_COLOR};
    border-radius: 10px;
    background-color: {SURFACE};
    padding: 14px;
}}
QTabBar::tab {{
    background: transparent;
    color: {TEXT_SECONDARY};
    padding: 10px 20px;
    font-weight: 600;
    font-size: 13px;
    border-bottom: 2px solid transparent;
    margin-right: 8px;
}}
QTabBar::tab:hover {{
    color: {PRIMARY};
}}
QTabBar::tab:selected {{
    color: {PRIMARY};
    border-bottom: 2.5px solid {PRIMARY};
}}

/* Progress Bar */
QProgressBar {{
    background-color: #E2E8F0;
    border: none;
    border-radius: 5px;
    height: 10px;
    text-align: right;
    font-size: 10px;
    color: transparent;
}}
QProgressBar::chunk {{
    background-color: {PRIMARY};
    border-radius: 5px;
}}
"""


# Standard Typography
FONT_FAMILY = "Segoe UI"

def font_title():
    f = QFont(FONT_FAMILY, 20)
    f.setBold(True)
    return f

def font_h1():
    f = QFont("Segoe UI", 16)
    f.setBold(True)
    return f

def font_h2():
    f = QFont("Segoe UI", 13)
    f.setBold(True)
    return f

def font_bold():
    f = QFont("Segoe UI", 10)
    f.setBold(True)
    return f

def font_regular():
    return QFont("Segoe UI", 10)

def font_small():
    return QFont("Segoe UI", 9)


# Elevation & Drop Shadows
def apply_card_shadow(widget: QWidget, blur_radius: int = 14, y_offset: int = 3, opacity: int = 15):
    """Applies a subtle, elegant drop shadow to any card container."""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur_radius)
    shadow.setXOffset(0)
    shadow.setYOffset(y_offset)
    shadow.setColor(QColor(15, 23, 42, opacity))  # Slate 900 tinted shadow
    widget.setGraphicsEffect(shadow)


# Reusable Card Frame
def create_card_frame(shadow: bool = True) -> QFrame:
    card = QFrame()
    card.setStyleSheet(f"""
        QFrame {{
            background-color: {SURFACE};
            border: 1px solid {BORDER_COLOR};
            border-radius: 12px;
        }}
    """)
    if shadow:
        apply_card_shadow(card)
    return card


# Modern Button Helpers
def create_primary_button(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setCursor(QCursor(Qt.PointingHandCursor))
    btn.setFont(font_bold())
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {PRIMARY};
            color: #FFFFFF;
            border-radius: 8px;
            padding: 8px 18px;
            font-weight: 600;
            border: none;
            min-height: 22px;
        }}
        QPushButton:hover {{
            background-color: {PRIMARY_DARK};
        }}
        QPushButton:pressed {{
            background-color: #3730A3;
        }}
    """)
    return btn


def create_secondary_button(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setCursor(QCursor(Qt.PointingHandCursor))
    btn.setFont(font_bold())
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {SECONDARY};
            color: #FFFFFF;
            border-radius: 8px;
            padding: 8px 18px;
            font-weight: 600;
            border: none;
            min-height: 22px;
        }}
        QPushButton:hover {{
            background-color: {SECONDARY_DARK};
        }}
    """)
    return btn


def create_danger_button(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setCursor(QCursor(Qt.PointingHandCursor))
    btn.setFont(font_bold())
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {DANGER};
            color: #FFFFFF;
            border-radius: 8px;
            padding: 8px 18px;
            font-weight: 600;
            border: none;
            min-height: 22px;
        }}
        QPushButton:hover {{
            background-color: {DANGER_DARK};
        }}
    """)
    return btn


def create_outline_button(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setCursor(QCursor(Qt.PointingHandCursor))
    btn.setFont(font_bold())
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {SURFACE};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER_COLOR};
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 600;
            min-height: 22px;
        }}
        QPushButton:hover {{
            background-color: #F8FAFC;
            border-color: #CBD5E1;
            color: {PRIMARY};
        }}
        QPushButton:pressed {{
            background-color: #F1F5F9;
        }}
    """)
    return btn


def create_danger_outline_button(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setCursor(QCursor(Qt.PointingHandCursor))
    btn.setFont(font_bold())
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {SURFACE};
            color: {DANGER};
            border: 1px solid #FECACA;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 600;
            min-height: 22px;
        }}
        QPushButton:hover {{
            background-color: {DANGER_LIGHT};
            border-color: {DANGER};
        }}
    """)
    return btn


def create_ghost_button(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setCursor(QCursor(Qt.PointingHandCursor))
    btn.setFont(font_bold())
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: transparent;
            color: {TEXT_SECONDARY};
            border-radius: 8px;
            padding: 8px 14px;
            font-weight: 600;
            border: none;
            min-height: 22px;
        }}
        QPushButton:hover {{
            background-color: #F1F5F9;
            color: {TEXT_PRIMARY};
        }}
    """)
    return btn


def create_back_button(callback) -> QWidget:
    w = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(0, 10, 0, 10)
    btn = create_outline_button("← Back to Dashboard")
    btn.clicked.connect(callback)
    lay.addWidget(btn)
    return w


def create_table_button(text: str, variant: str = "primary") -> QPushButton:
    """Compact button specifically styled for table cells to avoid clipping."""
    btn = QPushButton(text)
    btn.setCursor(QCursor(Qt.PointingHandCursor))
    btn.setFixedHeight(28)
    if variant == "primary":
        bg, fg, border, hbg = PRIMARY, "#FFFFFF", "transparent", PRIMARY_DARK
    elif variant == "secondary":
        bg, fg, border, hbg = SECONDARY, "#FFFFFF", "transparent", SECONDARY_DARK
    elif variant == "danger":
        bg, fg, border, hbg = SURFACE, DANGER, "#FECACA", DANGER_LIGHT
    elif variant == "outline":
        bg, fg, border, hbg = SURFACE, TEXT_PRIMARY, BORDER_COLOR, "#F1F5F9"
    elif variant == "success":
        bg, fg, border, hbg = SECONDARY, "#FFFFFF", "transparent", SECONDARY_DARK
    else:
        bg, fg, border, hbg = SURFACE, TEXT_PRIMARY, BORDER_COLOR, "#F1F5F9"
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {bg};
            color: {fg};
            border: 1px solid {border};
            border-radius: 6px;
            padding: 2px 10px;
            font-size: 11.5px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {hbg};
        }}
    """)
    return btn


def format_table(table: QTableWidget, row_height: int = 46):
    """Applies standardized enterprise styling and row height to any QTableWidget."""
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(row_height)
    table.setShowGrid(False)
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setSelectionMode(QTableWidget.SingleSelection)
    table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    table.horizontalHeader().setHighlightSections(False)
    table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)


def create_cell_widget(*widgets, spacing: int = 6) -> QWidget:
    """Wraps one or more widgets (badges, action buttons) in a centered table cell container."""
    container = QWidget()
    lay = QHBoxLayout(container)
    lay.setContentsMargins(6, 4, 6, 4)
    lay.setSpacing(spacing)
    lay.setAlignment(Qt.AlignCenter)
    for w in widgets:
        lay.addWidget(w)
    return container


def create_table_combobox(items: list, current_text: str = None) -> QComboBox:
    """Compact QComboBox styled specifically for table cells to avoid clipping and ensure full border visibility."""
    cb = QComboBox()
    cb.addItems(items)
    if current_text:
        idx = cb.findText(current_text)
        if idx >= 0:
            cb.setCurrentIndex(idx)
    cb.setFixedHeight(30)
    cb.setStyleSheet(f"""
        QComboBox {{
            background-color: #FFFFFF;
            border: 1px solid {BORDER_COLOR};
            border-radius: 6px;
            padding: 2px 24px 2px 10px;
            font-size: 11.5px;
            font-weight: 700;
            color: {TEXT_PRIMARY};
        }}
        QComboBox:hover {{
            border-color: #94A3B8;
        }}
        QComboBox:focus {{
            border: 1.5px solid {PRIMARY};
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: none;
        }}
        QComboBox::down-arrow {{
            image: url("{CHEVRON_DOWN_PATH}");
            width: 9px;
            height: 9px;
        }}
    """)
    return cb

