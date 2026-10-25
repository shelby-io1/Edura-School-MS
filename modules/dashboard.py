"""
Dashboard Module for School Management System.
Modern Slate & Indigo layout with MetricCard widgets, quick action tiles, and class breakdown.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, Signal
import core.theme as theme
import core.database as db
from core.widgets import ModernCard, MetricCard, StatusBadge, PageHeader
from datetime import date


class DashboardView(QWidget):
    navigate_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"background-color: {theme.BACKGROUND};")
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(20)

        # Page Header
        school_name = db.get_app_data("systemName", "EXCELLENCE SCHOOL SYSTEM")
        self.header = PageHeader(
            "Executive Dashboard",
            f"Institutional metrics and academic operations — {school_name}"
        )
        today_str = date.today().strftime("%A, %d %B %Y")
        date_badge = QLabel(f"📅  {today_str}")
        date_badge.setFont(theme.font_small())
        date_badge.setStyleSheet(f"""
            background-color: #F1F5F9;
            color: {theme.TEXT_SECONDARY};
            border-radius: 6px;
            padding: 5px 12px;
            font-weight: 600;
        """)
        self.header.add_action(date_badge)

        btn_refresh = theme.create_outline_button("↻ Refresh Data")
        btn_refresh.clicked.connect(self.refresh_data)
        self.header.add_action(btn_refresh)
        main_layout.addWidget(self.header)

        # KPI Metrics Row (4 Cards)
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(16)

        self.kpi_students = MetricCard("Total Students", "0", "👥", theme.PRIMARY, theme.PRIMARY_LIGHT, "100% Enrolled")
        self.kpi_staff = MetricCard("Faculty & Staff", "0", "👨‍🏫", theme.SECONDARY, theme.SECONDARY_LIGHT, "Active Directory")
        self.kpi_attendance = MetricCard("Today's Attendance", "96.4%", "📅", "#8B5CF6", "#F5F3FF", "Classes 1-10")
        self.kpi_finance = MetricCard("Monthly Tuition Dues", "Rs. 7.50M", "💰", theme.WARNING, theme.WARNING_LIGHT, "Projected Inflow")

        kpi_layout.addWidget(self.kpi_students)
        kpi_layout.addWidget(self.kpi_staff)
        kpi_layout.addWidget(self.kpi_attendance)
        kpi_layout.addWidget(self.kpi_finance)
        main_layout.addLayout(kpi_layout)

        # Quick Actions Bar
        actions_card = ModernCard()
        actions_lay = QHBoxLayout(actions_card)
        actions_lay.setContentsMargins(20, 14, 20, 14)
        actions_lay.setSpacing(14)

        act_title = QLabel("Fast Actions:")
        act_title.setFont(theme.font_bold())
        act_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 13px;")
        actions_lay.addWidget(act_title)

        btn_add_student = theme.create_primary_button("+ New Student Admission")
        btn_add_student.clicked.connect(lambda: self.navigate_requested.emit("studentModule:admission"))
        actions_lay.addWidget(btn_add_student)

        btn_attendance = theme.create_secondary_button("Mark Daily Attendance")
        btn_attendance.clicked.connect(lambda: self.navigate_requested.emit("attendance"))
        actions_lay.addWidget(btn_attendance)

        btn_finance = theme.create_outline_button("Student Fee Ledgers")
        btn_finance.clicked.connect(lambda: self.navigate_requested.emit("financeModule:ledger"))
        actions_lay.addWidget(btn_finance)

        btn_quizzes = theme.create_outline_button("Grade Quizzes & Tests")
        btn_quizzes.clicked.connect(lambda: self.navigate_requested.emit("quizzes"))
        actions_lay.addWidget(btn_quizzes)

        btn_timetable = theme.create_outline_button("Weekly Timetable")
        btn_timetable.clicked.connect(lambda: self.navigate_requested.emit("academicModule:timetable"))
        actions_lay.addWidget(btn_timetable)

        actions_lay.addStretch()
        main_layout.addWidget(actions_card)

        # Bottom Split Grid: Class Distribution & Tasks
        grid_split = QHBoxLayout()
        grid_split.setSpacing(20)

        # Left: Class Enrollment Table Card
        class_card = ModernCard()
        class_layout = QVBoxLayout(class_card)
        class_layout.setContentsMargins(22, 20, 22, 20)
        class_layout.setSpacing(12)

        c_header = QHBoxLayout()
        class_title = QLabel("Class Enrollment Distribution")
        class_title.setFont(theme.font_h2())
        class_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-weight: 700;")
        c_header.addWidget(class_title)
        c_header.addStretch()

        btn_view_classes = theme.create_ghost_button("View Roster →")
        btn_view_classes.clicked.connect(lambda: self.navigate_requested.emit("studentModule:classes"))
        c_header.addWidget(btn_view_classes)
        class_layout.addLayout(c_header)

        self.class_table = QTableWidget(10, 3)
        self.class_table.setHorizontalHeaderLabels(["Class Grade", "Enrolled Students", "Status"])
        theme.format_table(self.class_table, 42)
        self.class_table.setEditTriggers(QTableWidget.NoEditTriggers)
        cl_hdr = self.class_table.horizontalHeader()
        cl_hdr.setSectionResizeMode(0, QHeaderView.Interactive)
        cl_hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        cl_hdr.setSectionResizeMode(2, QHeaderView.Interactive)
        self.class_table.setColumnWidth(0, 110)
        self.class_table.setColumnWidth(2, 115)
        self.class_table.setMinimumHeight(340)
        class_layout.addWidget(self.class_table)

        grid_split.addWidget(class_card, 3)

        # Right: Upcoming Reminders & Actions Card
        reminders_card = ModernCard()
        reminders_layout = QVBoxLayout(reminders_card)
        reminders_layout.setContentsMargins(22, 20, 22, 20)
        reminders_layout.setSpacing(12)

        rem_header = QHBoxLayout()
        rem_title = QLabel("Pending Tasks & Alerts")
        rem_title.setFont(theme.font_h2())
        rem_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-weight: 700;")
        rem_header.addWidget(rem_title)
        rem_header.addStretch()

        btn_view_rem = theme.create_ghost_button("Open Board →")
        btn_view_rem.clicked.connect(lambda: self.navigate_requested.emit("reminders"))
        rem_header.addWidget(btn_view_rem)
        reminders_layout.addLayout(rem_header)

        self.reminders_table = QTableWidget(0, 3)
        self.reminders_table.setHorizontalHeaderLabels(["Task Title", "Deadline", "Priority"])
        theme.format_table(self.reminders_table, 42)
        self.reminders_table.setEditTriggers(QTableWidget.NoEditTriggers)
        rm_hdr = self.reminders_table.horizontalHeader()
        rm_hdr.setSectionResizeMode(0, QHeaderView.Stretch)
        rm_hdr.setSectionResizeMode(1, QHeaderView.Interactive)
        rm_hdr.setSectionResizeMode(2, QHeaderView.Interactive)
        self.reminders_table.setColumnWidth(1, 120)
        self.reminders_table.setColumnWidth(2, 110)
        self.reminders_table.setMinimumHeight(340)
        reminders_layout.addWidget(self.reminders_table)

        grid_split.addWidget(reminders_card, 2)
        main_layout.addLayout(grid_split)

        scroll.setWidget(container)
        root_lay = QVBoxLayout(self)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.addWidget(scroll)

        self.refresh_data()

    def refresh_data(self):
        school_name = db.get_app_data("systemName", "EXCELLENCE SCHOOL SYSTEM")
        if hasattr(self, "header") and hasattr(self.header, "lbl_sub"):
            self.header.lbl_sub.setText(f"Institutional metrics and academic operations — {school_name}")

        students = db.get_all_students()
        staff_list = db.get_all_staff()

        # Update metric cards
        self.kpi_students.set_value(f"{len(students):,}")
        self.kpi_staff.set_value(f"{len(staff_list):,}")

        tuition = float(db.get_app_data("fee_tuition", "5000"))
        it_lab = float(db.get_app_data("fee_itlab", "1000"))
        sports = float(db.get_app_data("fee_sports", "800"))
        utilities = float(db.get_app_data("fee_utilities", "700"))
        tot_fee = tuition + it_lab + sports + utilities
        self.kpi_finance.set_value(f"Rs. {(len(students) * tot_fee) / 1_000_000:.2f}M")

        # Class Breakdown
        class_counts = {str(i): 0 for i in range(1, 11)}
        for s in students:
            cls = str(s.class_name)
            if cls in class_counts:
                class_counts[cls] += 1

        self.class_table.setRowCount(10)
        for i, cls in enumerate([str(c) for c in range(1, 11)]):
            count = class_counts.get(cls, 0)
            self.class_table.setItem(i, 0, QTableWidgetItem(f"Class {cls}"))
            self.class_table.setItem(i, 1, QTableWidgetItem(f"{count} students enrolled"))

            status_chip = StatusBadge("ACTIVE", "success")
            self.class_table.setCellWidget(i, 2, theme.create_cell_widget(status_chip))

        # Reminders
        reminders = db.get_reminders()
        self.reminders_table.setRowCount(len(reminders))
        for row, r in enumerate(reminders):
            self.reminders_table.setItem(row, 0, QTableWidgetItem(r.title))
            self.reminders_table.setItem(row, 1, QTableWidgetItem(r.due_date or "No date"))

            p_badge = StatusBadge.from_status(r.priority)
            self.reminders_table.setCellWidget(row, 2, theme.create_cell_widget(p_badge))
