"""
Main application shell for Excellence School Management System.
Features collapsible sidebar navigation groups with nested sub-modules and deep sub-routing.
"""
import sys
import os
from typing import Dict, Optional
from datetime import date
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QLabel, QPushButton, QScrollArea, QFrame, QMessageBox
)
from PySide6.QtGui import QFont, QPixmap, QIcon
from PySide6.QtCore import Qt

import core.theme as theme
import core.database as db
from core.widgets import StatusBadge, CollapsibleNavGroup, SubNavButton, CollapsibleNavSection, LogoutModalOverlay
from modules.login import LoginView
from modules.dashboard import DashboardView
from modules.student_management import StudentManagementView
from modules.staff_management import StaffManagementView
from modules.academic_management import AcademicManagementView
from modules.finance_management import FinanceManagementView
from modules.reports_module import ReportsView
from modules.attendance_module import AttendanceView
from modules.quizzes_module import QuizzesView
from modules.assignments_module import AssignmentsView
from modules.reminders_module import RemindersView
from modules.syllabus_module import SyllabusView
from modules.results_module import ResultsView
from modules.settings_module import SettingsView
from modules.help_module import HelpView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1400, 880)
        self.setMinimumSize(1150, 720)

        db.initialize_database()
        school_name = db.get_app_data("systemName", "EXCELLENCE SCHOOL SYSTEM")
        self.setWindowTitle(f"Edura — {school_name}")

        self.current_user_role = None
        self.current_staff_id = None
        self.sidebar_sections: Dict[str, CollapsibleNavSection] = {}
        self.standalone_buttons: Dict[str, QPushButton] = {}
        self.nav_groups: Dict[str, CollapsibleNavGroup] = {}
        self.sub_buttons: Dict[str, SubNavButton] = {}

        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.root_layout = QHBoxLayout(self.central_widget)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        # 1. Left Integrated Sidebar with Collapsible Groups
        self.sidebar_widget = self.create_sidebar()
        self.sidebar_widget.setVisible(False)
        self.root_layout.addWidget(self.sidebar_widget)

        # 2. Right Canvas (Direct Main Content Stack - No duplicate headers)
        self.canvas_widget = QWidget()
        self.canvas_layout = QVBoxLayout(self.canvas_widget)
        self.canvas_layout.setContentsMargins(0, 0, 0, 0)
        self.canvas_layout.setSpacing(0)

        # Central Stacked Content
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet(f"background-color: {theme.BACKGROUND};")
        self.canvas_layout.addWidget(self.content_stack, 1)

        self.root_layout.addWidget(self.canvas_widget, 1)

        # Initialize all module views
        self.init_modules()

        # Start on Login
        self.navigate_to("login")

    def create_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setFixedWidth(275)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.SIDEBAR_BG};
                border-right: 1px solid #1E293B;
            }}
        """)
        side_lay = QVBoxLayout(sidebar)
        side_lay.setContentsMargins(0, 0, 0, 0)
        side_lay.setSpacing(0)

        # Top: Integrated Branding Box
        brand_box = QFrame()
        brand_box.setFixedHeight(80)
        brand_box.setStyleSheet(f"""
            QFrame {{
                background-color: #0B1120;
                border-bottom: 1px solid #1E293B;
            }}
        """)
        brand_lay = QHBoxLayout(brand_box)
        brand_lay.setContentsMargins(18, 12, 18, 12)
        brand_lay.setSpacing(12)

        self.sidebar_logo_lbl = QLabel()
        self.sidebar_logo_lbl.setFixedSize(40, 40)
        self.sidebar_logo_lbl.setAlignment(Qt.AlignCenter)
        self.update_sidebar_branding()
        brand_lay.addWidget(self.sidebar_logo_lbl)

        brand_text_box = QVBoxLayout()
        brand_text_box.setSpacing(2)

        school_name = db.get_app_data("systemName", "EXCELLENCE SCHOOL")
        self.sidebar_title_lbl = QLabel(school_name)
        self.sidebar_title_lbl.setFont(theme.font_bold())
        self.sidebar_title_lbl.setStyleSheet("color: #FFFFFF; font-weight: 800; font-size: 13px;")
        brand_text_box.addWidget(self.sidebar_title_lbl)

        badge_row = QHBoxLayout()
        badge_row.setSpacing(6)
        portal_badge = QLabel("ADMIN CONSOLE")
        portal_badge.setFont(theme.font_small())
        portal_badge.setStyleSheet(f"color: {theme.PRIMARY}; font-weight: 700; font-size: 10px; letter-spacing: 0.5px;")
        badge_row.addWidget(portal_badge)

        online_dot = QLabel("● ONLINE")
        online_dot.setFont(theme.font_small())
        online_dot.setStyleSheet(f"color: {theme.SECONDARY}; font-weight: 700; font-size: 9px;")
        badge_row.addWidget(online_dot)
        badge_row.addStretch()
        brand_text_box.addLayout(badge_row)

        brand_lay.addLayout(brand_text_box)
        brand_lay.addStretch()
        side_lay.addWidget(brand_box)

        # Navigation Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { background-color: transparent; border: none; }
            QScrollBar:vertical { width: 4px; background: transparent; }
            QScrollBar::handle:vertical { background: #334155; border-radius: 2px; }
        """)

        nav_container = QWidget()
        nav_container.setStyleSheet("background-color: transparent;")
        self.nav_layout = QVBoxLayout(nav_container)
        self.nav_layout.setContentsMargins(10, 14, 10, 14)
        self.nav_layout.setSpacing(8)

        # 1. MAIN
        sec_main = CollapsibleNavSection("MAIN", self.navigate_to, self)
        sec_main.add_option("Dashboard", "🏠", "dashboard")
        self.nav_layout.addWidget(sec_main)
        self.sidebar_sections["MAIN"] = sec_main

        # 2. STUDENTS
        sec_students = CollapsibleNavSection("STUDENTS", self.navigate_to, self)
        sec_students.add_option("Directory & Archives", "👥", "studentModule:directory")
        sec_students.add_option("New Admission Form", "📝", "studentModule:admission")
        sec_students.add_option("Class Browser (1-10)", "🏫", "studentModule:classes")
        self.nav_layout.addWidget(sec_students)
        self.sidebar_sections["STUDENTS"] = sec_students

        # 3. FACULTY & STAFF
        sec_staff = CollapsibleNavSection("FACULTY & STAFF", self.navigate_to, self)
        sec_staff.add_option("Faculty Directory", "👨‍🏫", "staffModule:directory")
        sec_staff.add_option("Register New Staff", "➕", "staffModule:register")
        self.nav_layout.addWidget(sec_staff)
        self.sidebar_sections["FACULTY & STAFF"] = sec_staff

        # 4. ACADEMICS
        sec_academic = CollapsibleNavSection("ACADEMICS", self.navigate_to, self)
        sec_academic.add_option("Weekly Timetable", "📅", "academicModule:timetable")
        sec_academic.add_option("Curriculum Syllabus", "📖", "syllabus")
        sec_academic.add_option("Exam Results & Cards", "📊", "results")
        sec_academic.add_option("Daily Attendance", "📋", "attendance")
        self.nav_layout.addWidget(sec_academic)
        self.sidebar_sections["ACADEMICS"] = sec_academic

        # 5. FINANCE & ACCOUNTS
        sec_fin = CollapsibleNavSection("FINANCE & ACCOUNTS", self.navigate_to, self)
        sec_fin.add_option("Student Fee Ledger", "💳", "financeModule:ledger")
        sec_fin.add_option("Billing Rates & Policy", "⚙️", "financeModule:config")
        sec_fin.add_option("Staff Payroll Slips", "💵", "financeModule:payroll")
        sec_fin.add_option("Operating Surplus P&L", "📈", "financeModule:pnl")
        self.nav_layout.addWidget(sec_fin)
        self.sidebar_sections["FINANCE & ACCOUNTS"] = sec_fin

        # 6. REPORTS CENTER
        sec_rep = CollapsibleNavSection("REPORTS CENTER", self.navigate_to, self)
        sec_rep.add_option("Student Rosters Audit", "📑", "reportsModule:students")
        sec_rep.add_option("Faculty Breakdown", "👥", "reportsModule:staff")
        sec_rep.add_option("Attendance Audit", "🕒", "reportsModule:attendance")
        sec_rep.add_option("Financial Statement", "💰", "reportsModule:finance")
        self.nav_layout.addWidget(sec_rep)
        self.sidebar_sections["REPORTS CENTER"] = sec_rep

        # 7. CLASSROOM TOOLS
        sec_cls = CollapsibleNavSection("CLASSROOM TOOLS", self.navigate_to, self)
        sec_cls.add_option("Daily Attendance", "📋", "attendance")
        sec_cls.add_option("Quizzes & Assessments", "✏️", "quizzes")
        sec_cls.add_option("Homework Assignments", "📝", "assignments")
        sec_cls.add_option("Curriculum Syllabus", "📖", "syllabus")
        sec_cls.add_option("Exam Results & Cards", "📊", "results")
        self.nav_layout.addWidget(sec_cls)
        self.sidebar_sections["CLASSROOM TOOLS"] = sec_cls

        # 8. SYSTEM & SETTINGS
        sec_sys = CollapsibleNavSection("SYSTEM & SETTINGS", self.navigate_to, self)
        sec_sys.add_option("Task Reminders", "🔔", "reminders")
        sec_sys.add_option("IT Settings", "🛠️", "settingsModule")
        sec_sys.add_option("Help Center", "❓", "helpModule")
        self.nav_layout.addWidget(sec_sys)
        self.sidebar_sections["SYSTEM & SETTINGS"] = sec_sys

        self.nav_layout.addStretch()
        scroll.setWidget(nav_container)
        side_lay.addWidget(scroll, 1)

        # Bottom Pinned Profile Dock
        profile_dock = QFrame()
        profile_dock.setFixedHeight(68)
        profile_dock.setStyleSheet(f"""
            QFrame {{
                background-color: #0B1120;
                border-top: 1px solid #1E293B;
            }}
        """)
        dock_lay = QHBoxLayout(profile_dock)
        dock_lay.setContentsMargins(14, 10, 14, 10)
        dock_lay.setSpacing(10)

        avatar = QLabel("👤")
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFont(QFont("Segoe UI Emoji", 16))
        avatar.setStyleSheet("""
            background-color: #1E293B;
            border-radius: 18px;
            border: 1px solid #334155;
        """)
        dock_lay.addWidget(avatar)

        u_box = QVBoxLayout()
        u_box.setSpacing(1)
        u_name = QLabel("Shahid Khan")
        u_name.setFont(theme.font_bold())
        u_name.setStyleSheet("color: #FFFFFF; font-size: 12px;")
        u_role = QLabel("Administrator")
        u_role.setFont(theme.font_small())
        u_role.setStyleSheet("color: #94A3B8; font-size: 10px;")
        u_box.addWidget(u_name)
        u_box.addWidget(u_role)
        dock_lay.addLayout(u_box)

        dock_lay.addStretch()

        self.btn_logout = QPushButton("⎋ Sign Out")
        self.btn_logout.setToolTip("Sign Out of Console")
        self.btn_logout.setFixedHeight(32)
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        self.btn_logout.setFont(theme.font_bold())
        self.btn_logout.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(239, 68, 68, 0.12);
                color: #F87171;
                border: 1px solid rgba(239, 68, 68, 0.28);
                border-radius: 6px;
                padding: 0 10px;
                font-size: 11px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {theme.DANGER};
                color: #FFFFFF;
                border-color: {theme.DANGER};
            }}
            QPushButton:pressed {{
                background-color: {theme.DANGER_DARK};
            }}
        """)
        self.btn_logout.clicked.connect(self.handle_logout)
        dock_lay.addWidget(self.btn_logout)

        side_lay.addWidget(profile_dock)
        return sidebar

    def add_section_header(self, title: str):
        sec_lbl = QLabel(title)
        sec_lbl.setFont(theme.font_small())
        sec_lbl.setStyleSheet("""
            color: #64748B;
            font-weight: 700;
            font-size: 10px;
            letter-spacing: 0.8px;
            padding-top: 10px;
            padding-bottom: 4px;
            padding-left: 8px;
        """)
        self.nav_layout.addWidget(sec_lbl)

    def update_sidebar_branding(self):
        school_name = db.get_app_data("systemName", "EXCELLENCE SCHOOL SYSTEM")
        logo_path = db.get_app_data("logoPath", "")

        # 1. Update Window Title
        self.setWindowTitle(f"Edura — {school_name}")

        # 2. Update Sidebar Title & Emblem
        if hasattr(self, "sidebar_logo_lbl"):
            if logo_path and os.path.exists(logo_path):
                pix = QPixmap(logo_path).scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.sidebar_logo_lbl.setPixmap(pix)
            else:
                self.sidebar_logo_lbl.setText("🏫")
                self.sidebar_logo_lbl.setFont(QFont("Segoe UI Emoji", 24))

        if hasattr(self, "sidebar_title_lbl"):
            self.sidebar_title_lbl.setText(school_name)

        # 3. Propagate to active views
        if hasattr(self, "view_login") and hasattr(self.view_login, "refresh_branding"):
            self.view_login.refresh_branding()
        if hasattr(self, "view_dashboard") and hasattr(self.view_dashboard, "refresh_data"):
            self.view_dashboard.refresh_data()
        if hasattr(self, "view_help") and hasattr(self.view_help, "refresh_data"):
            self.view_help.refresh_data()

    def get_standalone_btn_style(self, is_active: bool) -> str:
        if is_active:
            return f"""
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
            """
        return f"""
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
        """

    def init_modules(self):
        self.view_login = LoginView()
        self.view_login.login_success.connect(self.handle_login_success)
        self.content_stack.addWidget(self.view_login)

        self.view_dashboard = DashboardView()
        self.view_dashboard.navigate_requested.connect(self.navigate_to)
        self.content_stack.addWidget(self.view_dashboard)

        self.view_students = StudentManagementView()
        self.content_stack.addWidget(self.view_students)

        self.view_staff = StaffManagementView()
        self.content_stack.addWidget(self.view_staff)

        self.view_academic = AcademicManagementView()
        self.view_academic.navigate_requested.connect(self.navigate_to)
        self.content_stack.addWidget(self.view_academic)

        self.view_finance = FinanceManagementView()
        self.content_stack.addWidget(self.view_finance)

        self.view_reports = ReportsView()
        self.content_stack.addWidget(self.view_reports)

        self.view_attendance = AttendanceView()
        self.content_stack.addWidget(self.view_attendance)

        self.view_quizzes = QuizzesView()
        self.content_stack.addWidget(self.view_quizzes)

        self.view_assignments = AssignmentsView()
        self.content_stack.addWidget(self.view_assignments)

        self.view_reminders = RemindersView()
        self.content_stack.addWidget(self.view_reminders)

        self.view_syllabus = SyllabusView()
        self.content_stack.addWidget(self.view_syllabus)

        self.view_results = ResultsView()
        self.content_stack.addWidget(self.view_results)

        self.view_settings = SettingsView()
        self.view_settings.settings_updated.connect(self.update_sidebar_branding)
        self.content_stack.addWidget(self.view_settings)

        self.view_help = HelpView()
        self.content_stack.addWidget(self.view_help)

        self.module_titles = {
            "dashboard": "Dashboard Overview",
            "studentModule": "Student Management",
            "studentModule:hub": "Students / Overview & Hub",
            "studentModule:admission": "Students / New Admission Form",
            "studentModule:classes": "Students / Class Browser (1-10)",
            "studentModule:directory": "Students / Directory & Archives",
            "staffModule": "Faculty & Staff Directory",
            "staffModule:directory": "Faculty & Staff / Directory",
            "staffModule:register": "Faculty & Staff / Register Staff",
            "academicModule": "Academic Management",
            "academicModule:hub": "Academics / Overview",
            "academicModule:timetable": "Academics / Weekly Timetable",
            "financeModule": "Finance & Accounts",
            "financeModule:hub": "Finance / Overview",
            "financeModule:ledger": "Finance / Student Fee Ledger",
            "financeModule:config": "Finance / Billing Rates & Policy",
            "financeModule:payroll": "Finance / Staff Payroll",
            "financeModule:pnl": "Finance / Operating Margin P&L",
            "reportsModule": "Reports Center",
            "reportsModule:hub": "Reports / Overview",
            "reportsModule:students": "Reports / Student Rosters Audit",
            "reportsModule:staff": "Reports / Faculty Breakdown",
            "reportsModule:attendance": "Reports / Attendance Audit",
            "reportsModule:finance": "Reports / Financial Audit",
            "attendance": "Classroom / Daily Attendance",
            "quizzes": "Classroom / Quizzes & Tests",
            "assignments": "Classroom / Homework Assignments",
            "syllabus": "Classroom / Curriculum Syllabus",
            "results": "Classroom / Exam Results & Cards",
            "reminders": "Task Reminders & Priority Alerts",
            "settingsModule": "IT Support & System Settings",
            "helpModule": "Help Documentation & Knowledge Base",
        }

        self.module_mapping = {
            "login": self.view_login,
            "dashboard": self.view_dashboard,
            "studentModule": self.view_students,
            "staffModule": self.view_staff,
            "academicModule": self.view_academic,
            "financeModule": self.view_finance,
            "reportsModule": self.view_reports,
            "attendance": self.view_attendance,
            "quizzes": self.view_quizzes,
            "assignments": self.view_assignments,
            "reminders": self.view_reminders,
            "syllabus": self.view_syllabus,
            "results": self.view_results,
            "settingsModule": self.view_settings,
            "helpModule": self.view_help,
        }

    def navigate_to(self, target_route: str):
        if target_route == "login":
            self.sidebar_widget.setVisible(False)
            self.view_login.reset_view()
            self.content_stack.setCurrentWidget(self.view_login)
            return

        self.sidebar_widget.setVisible(True)

        # Parse parent module and optional sub-route
        if ":" in target_route:
            parent_mod, sub_route = target_route.split(":", 1)
        else:
            parent_mod, sub_route = target_route, ""

        widget = self.module_mapping.get(parent_mod)
        if widget:
            if sub_route and hasattr(widget, "set_sub_view"):
                widget.set_sub_view(sub_route)
            elif hasattr(widget, "refresh_data"):
                widget.refresh_data()
            elif hasattr(widget, "load_attendance"):
                widget.load_attendance()
            elif hasattr(widget, "load_quizzes"):
                widget.load_quizzes()
            elif hasattr(widget, "load_assignments"):
                widget.load_assignments()
            elif hasattr(widget, "reload_reminders"):
                widget.reload_reminders()
            elif hasattr(widget, "load_results"):
                widget.load_results()

            self.content_stack.setCurrentWidget(widget)

        # Update Sidebar Highlighting & Expand active section
        for sec_key, sec in self.sidebar_sections.items():
            contains_route = (target_route in sec.buttons) or (parent_mod in sec.buttons and not sub_route)
            if contains_route:
                sec.set_expanded(True)
            for r_key, btn in sec.buttons.items():
                is_active = (r_key == target_route) or (r_key == parent_mod and not sub_route)
                sec.set_btn_active(btn, is_active)

    def handle_login_success(self, role: str, staff_id: str):
        self.current_user_role = role
        self.current_staff_id = staff_id
        self.navigate_to("dashboard")

    def handle_logout(self):
        self.show_logout_modal()

    def show_logout_modal(self):
        if not hasattr(self, "logout_modal"):
            self.logout_modal = LogoutModalOverlay(self.do_logout, self)
        self.logout_modal.resize(self.size())
        self.logout_modal.show()
        self.logout_modal.raise_()

    def do_logout(self):
        self.current_user_role = None
        self.current_staff_id = None
        if hasattr(self, "view_login") and hasattr(self.view_login, "refresh_branding"):
            self.view_login.refresh_branding()
        self.navigate_to("login")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "logout_modal") and self.logout_modal.isVisible():
            self.logout_modal.resize(self.size())


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(theme.GLOBAL_QSS)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
