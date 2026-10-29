"""
Reusable modern UI components for School Management System.
Includes MetricCard, StatusBadge, PageHeader, ModernSearchBar, CollapsibleNavGroup, and SubNavButton.
"""
from typing import Optional, Dict
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout,
    QLineEdit, QPushButton
)
from PySide6.QtGui import QFont, QColor, QCursor
from PySide6.QtCore import Qt, Signal
import core.theme as theme


class ModernCard(QFrame):
    """Reusable card with subtle border and elevation shadow."""
    def __init__(self, parent=None, shadow: bool = True):
        super().__init__(parent)
        self.setStyleSheet(f"""
            ModernCard {{
                background-color: {theme.SURFACE};
                border: 1px solid {theme.BORDER_COLOR};
                border-radius: 12px;
            }}
        """)
        if shadow:
            theme.apply_card_shadow(self)


class StatusBadge(QLabel):
    """Modern pill badge with pastel background and bold text."""
    VARIANT_STYLES = {
        "success": (theme.SECONDARY, theme.SECONDARY_LIGHT, "#A7F3D0"),
        "danger": (theme.DANGER, theme.DANGER_LIGHT, "#FECACA"),
        "warning": (theme.WARNING, theme.WARNING_LIGHT, "#FDE68A"),
        "info": (theme.INFO, theme.INFO_LIGHT, "#BFDBFE"),
        "neutral": (theme.TEXT_SECONDARY, "#F1F5F9", "#E2E8F0"),
        "primary": (theme.PRIMARY, theme.PRIMARY_LIGHT, "#C7D2FE"),
    }

    def __init__(self, text: str, variant: str = "neutral", parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setFont(theme.font_small())
        self.setFixedHeight(24)
        self.set_variant(variant)

    def set_variant(self, variant: str):
        color, bg, border = self.VARIANT_STYLES.get(variant, self.VARIANT_STYLES["neutral"])
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: {color};
                border: 1px solid {border};
                border-radius: 8px;
                padding: 2px 10px;
                font-weight: 700;
                font-size: 11px;
            }}
        """)

    @classmethod
    def from_status(cls, status: str, parent=None):
        s = status.strip().upper()
        if s in ("ENROLLED", "PRESENT", "ACTIVE", "PAID", "DISBURSED", "PASSED"):
            return cls(status, "success", parent)
        elif s in ("ABSENT", "TERMINATED", "OVERDUE", "FAILED", "HIGH"):
            return cls(status, "danger", parent)
        elif s in ("LEAVE", "LATE", "PENDING", "MEDIUM"):
            return cls(status, "warning", parent)
        elif s in ("TEACHING STAFF", "LOW"):
            return cls(status, "info", parent)
        return cls(status, "neutral", parent)


class MetricCard(ModernCard):
    """Modern KPI metric widget with icon badge, bold stat number, and subtitle."""
    def __init__(self, title: str, value: str, icon_str: str, color_hex: str, bg_hex: str, trend_str: str = "", parent=None):
        super().__init__(parent)
        self.setFixedHeight(90)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(16)

        # Left: Icon inside rounded pastel pill
        icon_box = QFrame()
        icon_box.setFixedSize(52, 52)
        icon_box.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_hex};
                border-radius: 12px;
                border: 1px solid {color_hex}33;
            }}
        """)
        icon_lay = QVBoxLayout(icon_box)
        icon_lay.setContentsMargins(0, 0, 0, 0)
        icon_lbl = QLabel(icon_str)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 22))
        icon_lay.addWidget(icon_lbl)
        lay.addWidget(icon_box)

        # Center/Right: Title, Big Value, and Trend
        text_lay = QVBoxLayout()
        text_lay.setSpacing(2)

        lbl_title = QLabel(title)
        lbl_title.setFont(theme.font_small())
        lbl_title.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;")
        text_lay.addWidget(lbl_title)

        self.lbl_value = QLabel(value)
        self.lbl_value.setFont(theme.font_title())
        self.lbl_value.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-weight: 800;")
        text_lay.addWidget(self.lbl_value)

        if trend_str:
            lbl_trend = QLabel(trend_str)
            lbl_trend.setFont(theme.font_small())
            lbl_trend.setStyleSheet(f"color: {theme.SECONDARY_DARK}; font-weight: 600;")
            text_lay.addWidget(lbl_trend)

        lay.addLayout(text_lay)
        lay.addStretch()

    def set_value(self, val: str):
        self.lbl_value.setText(val)


class ModernSearchBar(QLineEdit):
    """Search input styled with search hint and clear capabilities."""
    def __init__(self, placeholder: str = "Search...", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(f"🔍  {placeholder}")
        self.setClearButtonEnabled(True)
        self.setFixedHeight(38)
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {theme.SURFACE};
                border: 1.5px solid {theme.BORDER_COLOR};
                border-radius: 8px;
                padding-left: 12px;
                padding-right: 12px;
                font-size: 13px;
                color: {theme.TEXT_PRIMARY};
            }}
            QLineEdit:focus {{
                border-color: {theme.PRIMARY};
                background-color: #FFFFFF;
            }}
        """)


class PageHeader(QWidget):
    """Standard modern page header with centered title, subtitle, and balanced action container."""
    def __init__(self, title: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 10)
        self.grid.setSpacing(0)

        # Left spacer container to mirror and balance right actions
        self.left_box = QWidget()
        self.left_box_layout = QHBoxLayout(self.left_box)
        self.left_box_layout.setContentsMargins(0, 0, 0, 0)
        self.grid.addWidget(self.left_box, 0, 0, Qt.AlignLeft | Qt.AlignVCenter)

        # Center Title Box
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title_box.setAlignment(Qt.AlignCenter)

        self.lbl_title = QLabel(title)
        self.lbl_title.setFont(theme.font_title())
        self.lbl_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-weight: 800;")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        title_box.addWidget(self.lbl_title)

        if subtitle:
            self.lbl_sub = QLabel(subtitle)
            self.lbl_sub.setFont(theme.font_regular())
            self.lbl_sub.setStyleSheet(f"color: {theme.TEXT_SECONDARY};")
            self.lbl_sub.setAlignment(Qt.AlignCenter)
            title_box.addWidget(self.lbl_sub)
        else:
            self.lbl_sub = None

        self.grid.addLayout(title_box, 0, 1, Qt.AlignCenter)

        # Right Actions Box
        self.actions_widget = QWidget()
        self.actions_layout = QHBoxLayout(self.actions_widget)
        self.actions_layout.setContentsMargins(0, 0, 0, 0)
        self.actions_layout.setSpacing(10)
        self.grid.addWidget(self.actions_widget, 0, 2, Qt.AlignRight | Qt.AlignVCenter)

        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, 2)
        self.grid.setColumnStretch(2, 1)

    def add_action(self, button: QWidget):
        self.actions_layout.addWidget(button)
        self._sync_balance()

    def _sync_balance(self):
        w = self.actions_widget.sizeHint().width()
        self.left_box.setFixedWidth(w)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._sync_balance()

    def showEvent(self, event):
        super().showEvent(event)
        self._sync_balance()


class SubNavButton(QPushButton):
    """Indented sub-module button with active indicator border."""
    def __init__(self, text: str, target_route: str, callback=None, parent=None):
        super().__init__(text, parent)
        self.target_route = target_route
        self.setFont(theme.font_small())
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setFixedHeight(30)
        self.set_active(False)
        if callback:
            self.clicked.connect(lambda: callback(self.target_route))

    def set_active(self, is_active: bool):
        if is_active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: #312E81;
                    color: #FFFFFF;
                    border-radius: 6px;
                    text-align: left;
                    padding-left: 20px;
                    font-weight: 700;
                    font-size: 11.5px;
                    border: none;
                    border-left: 3px solid {theme.PRIMARY};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {theme.SIDEBAR_TEXT};
                    border-radius: 6px;
                    text-align: left;
                    padding-left: 20px;
                    font-size: 11.5px;
                    font-weight: 500;
                    border: none;
                    border-left: 3px solid transparent;
                }}
                QPushButton:hover {{
                    background-color: {theme.SIDEBAR_HOVER};
                    color: #FFFFFF;
                }}
            """)


class CollapsibleNavGroup(QWidget):
    """Collapsible sidebar category containing expandable sub-module links with chevron."""
    def __init__(self, title: str, icon: str, parent_route: str, on_navigate, parent=None):
        super().__init__(parent)
        self.title = title
        self.icon = icon
        self.parent_route = parent_route
        self.on_navigate = on_navigate
        self.is_expanded = False
        self.sub_buttons: Dict[str, SubNavButton] = {}

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(2)

        # Header Toggle Button
        self.header_btn = QPushButton()
        self.header_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.header_btn.setFixedHeight(36)
        self.header_btn.clicked.connect(self.handle_header_click)
        self.update_header_text()
        self.set_header_active(False)
        self.layout.addWidget(self.header_btn)

        # Collapsible Sub-Items Container
        self.sub_container = QWidget()
        self.sub_layout = QVBoxLayout(self.sub_container)
        self.sub_layout.setContentsMargins(10, 2, 0, 4)
        self.sub_layout.setSpacing(2)
        self.sub_container.setVisible(False)
        self.layout.addWidget(self.sub_container)

    def handle_header_click(self):
        # Toggle expand/collapse
        self.set_expanded(not self.is_expanded)
        # Navigate to the default parent view
        if self.on_navigate:
            self.on_navigate(self.parent_route)

    def update_header_text(self):
        arrow = "▾" if self.is_expanded else "▸"
        self.header_btn.setText(f"  {self.icon}   {self.title}   {arrow}")

    def set_header_active(self, is_active: bool):
        if is_active:
            self.header_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme.PRIMARY};
                    color: #FFFFFF;
                    border-radius: 8px;
                    text-align: left;
                    padding-left: 12px;
                    font-weight: 700;
                    font-size: 12.5px;
                    border: none;
                }}
            """)
        else:
            self.header_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {theme.SIDEBAR_TEXT};
                    border-radius: 8px;
                    text-align: left;
                    padding-left: 12px;
                    font-size: 12.5px;
                    font-weight: 500;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: {theme.SIDEBAR_HOVER};
                    color: {theme.SIDEBAR_TEXT_ACTIVE};
                }}
            """)

    def set_expanded(self, expanded: bool):
        self.is_expanded = expanded
        self.update_header_text()
        self.sub_container.setVisible(expanded)

    def add_sub_item(self, label: str, target_route: str):
        btn = SubNavButton(label, target_route, self.on_navigate, self)
        self.sub_layout.addWidget(btn)
        self.sub_buttons[target_route] = btn
        return btn


class CollapsibleNavSection(QWidget):
    """Sidebar section featuring an uppercase heading and collapsible option items."""
    def __init__(self, title: str, on_navigate, parent=None, collapsible: bool = True):
        super().__init__(parent)
        self.title_text = title
        self.on_navigate = on_navigate
        self.collapsible = collapsible
        self.is_expanded = True
        self.buttons: Dict[str, QPushButton] = {}

        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(0, 2, 0, 4)
        self.lay.setSpacing(2)

        # Uppercase Section Heading Bar
        self.header_btn = QPushButton()
        self.header_btn.setCursor(QCursor(Qt.PointingHandCursor) if collapsible else QCursor(Qt.ArrowCursor))
        self.header_btn.setFont(theme.font_small())
        self.header_btn.setFixedHeight(26)
        self.header_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #64748B;
                font-weight: 700;
                font-size: 10px;
                letter-spacing: 0.8px;
                text-align: left;
                padding-left: 10px;
                padding-top: 6px;
                padding-bottom: 2px;
            }
            QPushButton:hover {
                color: #CBD5E1;
            }
        """)
        self.update_header_text()
        if collapsible:
            self.header_btn.clicked.connect(self.toggle_expanded)
        self.lay.addWidget(self.header_btn)

        # Options Container
        self.options_container = QWidget()
        self.options_lay = QVBoxLayout(self.options_container)
        self.options_lay.setContentsMargins(0, 0, 0, 0)
        self.options_lay.setSpacing(2)
        self.lay.addWidget(self.options_container)

    def update_header_text(self):
        if self.collapsible:
            arrow = "▾" if self.is_expanded else "▸"
            self.header_btn.setText(f"{self.title_text}   {arrow}")
        else:
            self.header_btn.setText(self.title_text)

    def toggle_expanded(self):
        self.set_expanded(not self.is_expanded)

    def set_expanded(self, expanded: bool):
        self.is_expanded = expanded
        self.update_header_text()
        self.options_container.setVisible(expanded)

    def add_option(self, label: str, icon: str, route: str) -> QPushButton:
        btn = QPushButton(f"  {icon}   {label}")
        btn.setFont(theme.font_regular())
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setFixedHeight(36)
        btn.clicked.connect(lambda: self.on_navigate(route))
        self.options_lay.addWidget(btn)
        self.buttons[route] = btn
        self.set_btn_active(btn, False)
        return btn

    def set_btn_active(self, btn: QPushButton, is_active: bool):
        if is_active:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme.PRIMARY};
                    color: #FFFFFF;
                    border-radius: 8px;
                    text-align: left;
                    padding-left: 14px;
                    font-weight: 700;
                    font-size: 12px;
                    border: none;
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {theme.SIDEBAR_TEXT};
                    border-radius: 8px;
                    text-align: left;
                    padding-left: 14px;
                    font-size: 12px;
                    font-weight: 500;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: {theme.SIDEBAR_HOVER};
                    color: {theme.SIDEBAR_TEXT_ACTIVE};
                }}
            """)


class FormHeaderCard(ModernCard):
    """Unified top banner for admission, enrollment, and registration forms."""
    def __init__(self, title: str, subtitle: str, icon_str: str = "📝", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            ModernCard {{
                background-color: {theme.SURFACE};
                border: 1px solid {theme.BORDER_COLOR};
                border-left: 5px solid {theme.PRIMARY};
                border-radius: 12px;
            }}
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(22, 18, 22, 18)
        lay.setSpacing(16)

        # Left: Icon pill
        icon_box = QFrame()
        icon_box.setFixedSize(50, 50)
        icon_box.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.PRIMARY_LIGHT};
                border: 1px solid #C7D2FE;
                border-radius: 12px;
            }}
        """)
        ib_lay = QVBoxLayout(icon_box)
        ib_lay.setContentsMargins(0, 0, 0, 0)
        i_lbl = QLabel(icon_str)
        i_lbl.setAlignment(Qt.AlignCenter)
        i_lbl.setFont(QFont("Segoe UI Emoji", 22))
        ib_lay.addWidget(i_lbl)
        lay.addWidget(icon_box)

        # Center: Titles
        t_lay = QVBoxLayout()
        t_lay.setSpacing(3)
        self.title_lbl = QLabel(title)
        self.title_lbl.setFont(theme.font_title())
        self.title_lbl.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-weight: 800; font-size: 18px;")
        t_lay.addWidget(self.title_lbl)

        self.sub_lbl = QLabel(subtitle)
        self.sub_lbl.setFont(theme.font_small())
        self.sub_lbl.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 12px;")
        self.sub_lbl.setWordWrap(True)
        t_lay.addWidget(self.sub_lbl)
        lay.addLayout(t_lay, 1)

        # Right: Badges / Tags Layout
        self.badges_lay = QHBoxLayout()
        self.badges_lay.setSpacing(8)
        lay.addLayout(self.badges_lay)

    def add_badge(self, badge: QWidget):
        self.badges_lay.addWidget(badge)


class FormSectionHeader(QWidget):
    """Section title bar with icon badge, title, subtitle, and divider line."""
    def __init__(self, title: str, icon_str: str = "📁", subtitle: str = "", parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 8)
        lay.setSpacing(6)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        icon_lbl = QLabel(icon_str)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 15))
        top_row.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setFont(theme.font_h2())
        title_lbl.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-weight: 700; font-size: 14px;")
        top_row.addWidget(title_lbl)

        if subtitle:
            sub_lbl = QLabel(f"— {subtitle}")
            sub_lbl.setFont(theme.font_small())
            sub_lbl.setStyleSheet(f"color: {theme.TEXT_SECONDARY};")
            top_row.addWidget(sub_lbl)

        top_row.addStretch()
        lay.addLayout(top_row)

        # Hairline divider
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Plain)
        line.setStyleSheet(f"background-color: {theme.BORDER_COLOR}; max-height: 1px; border: none;")
        lay.addWidget(line)


class FormFieldGroup(QWidget):
    """Consistent vertical container for a form input paired with a bold label and required mark."""
    def __init__(self, label_text: str, input_widget: QWidget, required: bool = False, helper_text: str = "", parent=None):
        super().__init__(parent)
        self.input_widget = input_widget
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)

        lbl = QLabel()
        lbl.setFont(theme.font_bold())
        if required:
            lbl.setText(f"{label_text} <span style='color: {theme.DANGER}; font-weight: bold;'>*</span>")
        else:
            lbl.setText(label_text)
        lbl.setTextFormat(Qt.RichText)
        lbl.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 12px; font-weight: 600;")
        lay.addWidget(lbl)

        lay.addWidget(input_widget)

        if helper_text:
            h_lbl = QLabel(helper_text)
            h_lbl.setFont(theme.font_small())
            h_lbl.setStyleSheet(f"color: {theme.TEXT_TERTIARY}; font-size: 11px;")
            lay.addWidget(h_lbl)


class LogoutModalOverlay(QWidget):
    """Modern enterprise in-window modal overlay for sign-out confirmation."""
    def __init__(self, on_confirm_logout, parent=None):
        super().__init__(parent)
        self.on_confirm = on_confirm_logout
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("background-color: rgba(15, 23, 42, 0.65);")
        root_lay = QVBoxLayout(self)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setFixedSize(430, 260)
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 16px;
            }
        """)
        theme.apply_card_shadow(card)
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(32, 28, 32, 28)
        card_lay.setSpacing(14)

        icon_box = QHBoxLayout()
        icon_lbl = QLabel("🚪")
        icon_lbl.setFixedSize(54, 54)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 24))
        icon_lbl.setStyleSheet("""
            background-color: #FEF2F2;
            border: 1px solid #FECACA;
            border-radius: 27px;
        """)
        icon_box.addStretch()
        icon_box.addWidget(icon_lbl)
        icon_box.addStretch()
        card_lay.addLayout(icon_box)

        title_lbl = QLabel("Sign Out of Console?")
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setFont(theme.font_title())
        title_lbl.setStyleSheet("color: #0F172A; font-weight: 800; font-size: 17px; background: transparent; border: none;")
        card_lay.addWidget(title_lbl)

        desc_lbl = QLabel("Are you sure you want to end your administrative session? You will need to sign in again to access school records.")
        desc_lbl.setAlignment(Qt.AlignCenter)
        desc_lbl.setWordWrap(True)
        desc_lbl.setFont(theme.font_regular())
        desc_lbl.setStyleSheet("color: #64748B; font-size: 12.5px; background: transparent; border: none; line-height: 1.4;")
        card_lay.addWidget(desc_lbl)

        card_lay.addSpacing(6)

        btn_box = QHBoxLayout()
        btn_box.setSpacing(12)

        btn_cancel = QPushButton("Stay Signed In")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setFixedHeight(38)
        btn_cancel.setFont(theme.font_bold())
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #F8FAFC;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 12.5px;
            }
            QPushButton:hover {
                background-color: #F1F5F9;
                color: #0F172A;
            }
        """)
        btn_cancel.clicked.connect(self.hide)
        btn_box.addWidget(btn_cancel, 1)

        btn_confirm = QPushButton("Yes, Sign Out")
        btn_confirm.setCursor(Qt.PointingHandCursor)
        btn_confirm.setFixedHeight(38)
        btn_confirm.setFont(theme.font_bold())
        btn_confirm.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.DANGER};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 12.5px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {theme.DANGER_DARK};
            }}
        """)
        btn_confirm.clicked.connect(self.handle_confirm)
        btn_box.addWidget(btn_confirm, 1)

        card_lay.addLayout(btn_box)
        root_lay.addWidget(card)

    def handle_confirm(self):
        self.hide()
        if self.on_confirm:
            self.on_confirm()

    def mousePressEvent(self, event):
        child = self.childAt(event.position().toPoint())
        if child == self:
            self.hide()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()
        super().keyPressEvent(event)


