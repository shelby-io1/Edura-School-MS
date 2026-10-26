"""
Settings & IT Support Module for School Management System.
Features unified Save Settings action ensuring changes are only saved and applied on explicit confirmation.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QComboBox, QFileDialog, QMessageBox,
    QFormLayout, QScrollArea, QCheckBox, QDoubleSpinBox
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, Signal
import core.theme as theme
import core.database as db
from core.widgets import ModernCard, StatusBadge, PageHeader, FormSectionHeader
import os


class SettingsView(QWidget):
    settings_updated = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        self.setStyleSheet(f"background-color: {theme.BACKGROUND};")
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(32, 24, 32, 24)
        lay.setSpacing(20)

        header = PageHeader(
            "IT Support & System Configuration",
            "Master administrator credentials, institutional branding, system currency, and portal identity"
        )
        lay.addWidget(header)

        # 1. Admin Security Card
        sec_card = ModernCard()
        sec_lay = QVBoxLayout(sec_card)
        sec_lay.setContentsMargins(28, 24, 28, 24)
        sec_lay.setSpacing(16)

        sec_lay.addWidget(FormSectionHeader(
            "Administrator Security Credentials", "🔐",
            "Update master administrative username and password for singular authority login"
        ))

        form_sec = QFormLayout()
        form_sec.setSpacing(14)

        self.admin_user_input = QLineEdit()
        self.admin_user_input.setFixedHeight(38)
        self.admin_user_input.setPlaceholderText("Master Administrator Username")
        form_sec.addRow("Admin Username*:", self.admin_user_input)

        self.admin_pass_input = QLineEdit()
        self.admin_pass_input.setEchoMode(QLineEdit.Password)
        self.admin_pass_input.setFixedHeight(38)
        self.admin_pass_input.setPlaceholderText("Enter new secure password")
        form_sec.addRow("New Password*:", self.admin_pass_input)

        self.admin_confirm_input = QLineEdit()
        self.admin_confirm_input.setEchoMode(QLineEdit.Password)
        self.admin_confirm_input.setFixedHeight(38)
        self.admin_confirm_input.setPlaceholderText("Re-type password to confirm")
        form_sec.addRow("Confirm Password*:", self.admin_confirm_input)

        sec_lay.addLayout(form_sec)
        lay.addWidget(sec_card)

        # 2. Institutional Branding Card
        ident_card = ModernCard()
        ident_lay = QVBoxLayout(ident_card)
        ident_lay.setContentsMargins(28, 24, 28, 24)
        ident_lay.setSpacing(16)

        ident_lay.addWidget(FormSectionHeader(
            "School Identity & Visual Branding", "🏫",
            "Portal branding, system currency standard, and institutional emblem logo"
        ))

        form_ident = QFormLayout()
        form_ident.setSpacing(14)

        self.school_name_input = QLineEdit()
        self.school_name_input.setFixedHeight(38)
        self.school_name_input.setPlaceholderText("e.g. EXCELLENCE SCHOOL SYSTEM")
        form_ident.addRow("School Name*:", self.school_name_input)

        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["PKR (Rs.)", "USD ($)"])
        self.currency_combo.setFixedHeight(38)
        form_ident.addRow("Currency Standard:", self.currency_combo)

        logo_box = QHBoxLayout()
        logo_box.setSpacing(10)
        self.logo_path_input = QLineEdit()
        self.logo_path_input.setPlaceholderText("Select image file path (.png, .jpg)")
        self.logo_path_input.setFixedHeight(38)
        btn_browse = theme.create_outline_button("Browse...")
        btn_browse.setFixedHeight(38)
        btn_browse.clicked.connect(self.browse_logo)
        logo_box.addWidget(self.logo_path_input)
        logo_box.addWidget(btn_browse)
        form_ident.addRow("School Logo Image:", logo_box)

        ident_lay.addLayout(form_ident)
        lay.addWidget(ident_card)

        # 3. Academic Progression Policy Card (Approach C)
        policy_card = ModernCard()
        pol_lay = QVBoxLayout(policy_card)
        pol_lay.setContentsMargins(28, 24, 28, 24)
        pol_lay.setSpacing(16)

        pol_lay.addWidget(FormSectionHeader(
            "Academic Progression & Auto-Promotion Policy (Approach C)", "🎓",
            "Autonomous student grade advancement, passing percentage thresholds, and session rollover rules"
        ))

        form_pol = QFormLayout()
        form_pol.setSpacing(14)

        self.auto_promo_check = QCheckBox("Enable Autonomous Year-End Progression upon Final Exam Submission")
        self.auto_promo_check.setFont(theme.font_bold())
        self.auto_promo_check.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 13px;")
        form_pol.addRow("Progression Automation:", self.auto_promo_check)

        self.min_passing_spin = QDoubleSpinBox()
        self.min_passing_spin.setRange(33.0, 90.0)
        self.min_passing_spin.setSingleStep(1.0)
        self.min_passing_spin.setSuffix("% Cumulative")
        self.min_passing_spin.setFixedHeight(38)
        form_pol.addRow("Overall Passing Benchmark*:", self.min_passing_spin)

        self.min_subject_spin = QDoubleSpinBox()
        self.min_subject_spin.setRange(25.0, 75.0)
        self.min_subject_spin.setSingleStep(1.0)
        self.min_subject_spin.setSuffix("% Minimum per Subject")
        self.min_subject_spin.setFixedHeight(38)
        form_pol.addRow("Subject Passing Minimum*:", self.min_subject_spin)

        self.auto_alumni_check = QCheckBox("Automatically transition passing Class 10 graduates to ALUMNI status")
        self.auto_alumni_check.setFont(theme.font_regular())
        self.auto_alumni_check.setStyleSheet(f"color: {theme.TEXT_PRIMARY};")
        form_pol.addRow("Senior Graduation:", self.auto_alumni_check)

        self.academic_session_input = QLineEdit()
        self.academic_session_input.setFixedHeight(38)
        self.academic_session_input.setPlaceholderText("e.g. 2025-2026")
        form_pol.addRow("Academic Session Period*:", self.academic_session_input)

        pol_lay.addLayout(form_pol)
        lay.addWidget(policy_card)

        # 4. Form Action Footer Card (Single Authoritative Save)
        action_card = ModernCard()
        act_lay = QHBoxLayout(action_card)
        act_lay.setContentsMargins(24, 18, 24, 18)
        act_lay.setSpacing(14)

        self.btn_save = theme.create_primary_button("💾 Save Settings")
        self.btn_save.setFixedHeight(40)
        self.btn_save.setMinimumWidth(160)
        self.btn_save.clicked.connect(self.save_all_settings)
        act_lay.addWidget(self.btn_save)

        self.btn_reset = theme.create_outline_button("↺ Discard Changes")
        self.btn_reset.setFixedHeight(40)
        self.btn_reset.clicked.connect(self.load_settings)
        act_lay.addWidget(self.btn_reset)

        act_lay.addStretch()

        self.status_feedback_lbl = QLabel("")
        self.status_feedback_lbl.setFont(theme.font_small())
        self.status_feedback_lbl.setStyleSheet(f"color: {theme.TEXT_SECONDARY};")
        act_lay.addWidget(self.status_feedback_lbl)

        lay.addWidget(action_card)
        lay.addStretch()

        scroll.setWidget(container)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)

    def load_settings(self):
        """Loads all settings from database into form inputs."""
        cur_user, cur_pass = db.get_master_admin_credentials()
        self.admin_user_input.setText(cur_user or "")
        self.admin_pass_input.setText(cur_pass or "")
        self.admin_confirm_input.setText(cur_pass or "")

        curr_name = db.get_app_data("systemName", "EXCELLENCE SCHOOL SYSTEM")
        self.school_name_input.setText(curr_name)

        curr_curr = db.get_app_data("currencyName", "PKR")
        idx = self.currency_combo.findText("PKR (Rs.)" if curr_curr == "PKR" else "USD ($)")
        if idx >= 0:
            self.currency_combo.setCurrentIndex(idx)

        curr_logo = db.get_app_data("logoPath", "")
        self.logo_path_input.setText(curr_logo or "")

        policy = db.get_progression_policy()
        self.auto_promo_check.setChecked(bool(policy.get("auto_promotion_enabled", True)))
        self.min_passing_spin.setValue(float(policy.get("min_passing_pct", 50.0)))
        self.min_subject_spin.setValue(float(policy.get("min_subject_pct", 40.0)))
        self.auto_alumni_check.setChecked(bool(policy.get("auto_graduate_alumni", True)))
        self.academic_session_input.setText(str(policy.get("academic_session", "2025-2026")))

        self.status_feedback_lbl.setText("Current saved settings loaded.")
        self.status_feedback_lbl.setStyleSheet(f"color: {theme.TEXT_SECONDARY};")

    def refresh_data(self):
        self.load_settings()

    def browse_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select School Logo", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.logo_path_input.setText(file_path)

    def save_all_settings(self):
        """Only saves and applies changes when explicitly triggered by the user."""
        user = self.admin_user_input.text().strip()
        pwd = self.admin_pass_input.text().strip()
        confirm = self.admin_confirm_input.text().strip()

        if not user:
            self.status_feedback_lbl.setText("❌ Admin username cannot be empty.")
            self.status_feedback_lbl.setStyleSheet(f"color: {theme.DANGER}; font-weight: 700;")
            return

        if not pwd:
            self.status_feedback_lbl.setText("❌ New password cannot be empty.")
            self.status_feedback_lbl.setStyleSheet(f"color: {theme.DANGER}; font-weight: 700;")
            return

        if pwd != confirm:
            self.status_feedback_lbl.setText("❌ Passwords do not match.")
            self.status_feedback_lbl.setStyleSheet(f"color: {theme.DANGER}; font-weight: 700;")
            return

        name = self.school_name_input.text().strip()
        if not name:
            self.status_feedback_lbl.setText("❌ School Name cannot be empty.")
            self.status_feedback_lbl.setStyleSheet(f"color: {theme.DANGER}; font-weight: 700;")
            return

        # 1. Save Admin Credentials
        db.update_master_admin(user, pwd)

        # 2. Save School Identity & Branding
        db.save_app_data("systemName", name)
        db.save_app_data("logoPath", self.logo_path_input.text().strip())
        cur = "PKR" if "PKR" in self.currency_combo.currentText() else "USD"
        db.save_app_data("currencyName", cur)

        # 3. Save Academic Progression Policy (Approach C)
        policy = {
            "auto_promotion_enabled": self.auto_promo_check.isChecked(),
            "min_passing_pct": self.min_passing_spin.value(),
            "min_subject_pct": self.min_subject_spin.value(),
            "auto_graduate_alumni": self.auto_alumni_check.isChecked(),
            "academic_session": self.academic_session_input.text().strip() or "2025-2026"
        }
        db.save_progression_policy(policy)

        # 4. Apply changes across application shell
        self.settings_updated.emit()
        self.status_feedback_lbl.setText("✓ All settings and progression policies saved successfully!")
        self.status_feedback_lbl.setStyleSheet(f"color: {theme.SECONDARY_DARK}; font-weight: 700;")
