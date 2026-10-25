"""
Login module for School Management System.
Modern, elegant single-admin sign-in card with soft elevation and clean inputs.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame
)
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import Qt, Signal
import os
import core.theme as theme
import core.database as db
from core.widgets import ModernCard, StatusBadge


class LoginView(QWidget):
    login_success = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"background-color: {theme.BACKGROUND};")
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        # Center Elevated Card
        card = ModernCard(shadow=True)
        card.setFixedWidth(440)
        card.setStyleSheet(f"""
            ModernCard {{
                background-color: {theme.SURFACE};
                border: 1px solid {theme.BORDER_COLOR};
                border-radius: 16px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 40, 36, 40)
        card_layout.setSpacing(14)

        # Top Badge / School Crest
        logo_box = QHBoxLayout()
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        logo_box.addStretch()
        logo_box.addWidget(self.logo_label)
        logo_box.addStretch()
        card_layout.addLayout(logo_box)

        # School Name & Subtitle
        self.title_label = QLabel()
        self.title_label.setFont(theme.font_h1())
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-weight: 800; margin-bottom: 6px;")
        card_layout.addWidget(self.title_label)
        self.refresh_branding()

        # Error notification label (initially hidden)
        self.error_label = QLabel("")
        self.error_label.setFont(theme.font_bold())
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet(f"""
            color: {theme.DANGER};
            background-color: {theme.DANGER_LIGHT};
            border: 1px solid #FECACA;
            border-radius: 8px;
            padding: 8px;
            font-size: 12px;
        """)
        self.error_label.setVisible(False)
        card_layout.addWidget(self.error_label)

        # Username Field
        lbl_user = QLabel("Username")
        lbl_user.setFont(theme.font_bold())
        lbl_user.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 12px;")
        card_layout.addWidget(lbl_user)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter administrator username")
        self.username_input.setFixedHeight(40)
        self.username_input.returnPressed.connect(self.password_input_focus)
        card_layout.addWidget(self.username_input)

        # Password Field
        lbl_pass = QLabel("Password")
        lbl_pass.setFont(theme.font_bold())
        lbl_pass.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 12px;")
        card_layout.addWidget(lbl_pass)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter master password")
        self.password_input.setFixedHeight(40)
        self.password_input.returnPressed.connect(self.handle_login)
        card_layout.addWidget(self.password_input)

        card_layout.addSpacing(6)

        # Sign In Button
        self.login_btn = theme.create_primary_button("Sign In")
        self.login_btn.setFixedHeight(42)
        self.login_btn.setFont(theme.font_h2())
        self.login_btn.clicked.connect(self.handle_login)
        card_layout.addWidget(self.login_btn)

        # Security footer
        foot_box = QHBoxLayout()
        foot_box.addStretch()
        badge = StatusBadge("🔒 Singular Master Authority", "neutral")
        foot_box.addWidget(badge)
        foot_box.addStretch()
        card_layout.addLayout(foot_box)

        lbl_powered = QLabel("Powered by Edura • Institutional Management Suite")
        lbl_powered.setAlignment(Qt.AlignCenter)
        lbl_powered.setStyleSheet(f"color: {theme.TEXT_TERTIARY}; font-size: 11px; font-weight: 600; margin-top: 4px;")
        card_layout.addWidget(lbl_powered)

        main_layout.addWidget(card)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.show_error("Please enter both username and password.")
            return

        auth_result = db.authenticate(username, password)
        if auth_result:
            role, staff_id = auth_result
            self.error_label.setVisible(False)
            self.password_input.clear()
            self.login_success.emit(role, staff_id)
        else:
            self.show_error("Invalid credentials. Please verify your login.")

    def show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.setVisible(True)

    def password_input_focus(self):
        self.password_input.setFocus()
        self.password_input.selectAll()

    def reset_view(self):
        self.username_input.clear()
        self.password_input.clear()
        self.error_label.setVisible(False)
        self.username_input.setFocus()
        self.refresh_branding()

    def refresh_branding(self):
        school_name = db.get_app_data("systemName", "EXCELLENCE SCHOOL SYSTEM")
        if hasattr(self, "title_label"):
            self.title_label.setText(school_name)
        logo_path = db.get_app_data("logoPath", "")
        if hasattr(self, "logo_label"):
            if logo_path and os.path.exists(logo_path):
                pix = QPixmap(logo_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.logo_label.setPixmap(pix)
            else:
                self.logo_label.setText("🏫")
                self.logo_label.setFont(QFont("Segoe UI Emoji", 40))

