"""
Help & Documentation Module for School Management System.
Redesigned with ModernCard containers, StatusBadge chips, and documentation layout.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, Signal
import core.theme as theme
import core.database as db
from core.widgets import ModernCard, StatusBadge, PageHeader


class HelpView(QWidget):
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

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
            "Help Center & Knowledge Base",
            "Institutional workflows, operational documentation, system diagnostics, and IT technical assistance"
        )
        lay.addWidget(header)

        # 1. Navigation Guide Card
        c1 = ModernCard()
        c1_lay = QVBoxLayout(c1)
        c1_lay.setContentsMargins(26, 22, 26, 22)
        c1_lay.setSpacing(10)

        t1_box = QHBoxLayout()
        c1_title = QLabel("System Architecture & Core Navigation")
        c1_title.setFont(theme.font_h2())
        c1_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-weight: 700;")
        t1_box.addWidget(c1_title)
        t1_box.addStretch()
        t1_box.addWidget(StatusBadge("SUITE GUIDE", "info"))
        c1_lay.addLayout(t1_box)

        c1_text = QLabel(
            "• <b>Executive Dashboard:</b> High-level KPI metric cards for students, staff, attendance, and collections.<br>"
            "• <b>Student Records:</b> Admissions form, class rosters (1-10), bulk fee vouchers, and searchable student archives.<br>"
            "• <b>Faculty Directory:</b> Staff records, automated AAA111 registration, department filtering, and course allocations.<br>"
            "• <b>Academics:</b> Period-wise Monday to Friday class timetable schedule matrix.<br>"
            "• <b>Finance & Payroll:</b> Class fee ledgers, rate configurations, monthly staff payroll, and operating surplus summary.<br>"
            "• <b>Classroom Suite:</b> Daily attendance registers, continuous quizzes, homework assignments, reminders board, and term report cards."
        )
        c1_text.setFont(theme.font_regular())
        c1_lay.addWidget(c1_text)
        lay.addWidget(c1)

        # 2. Storage & Backups Card
        c2 = ModernCard()
        c2_lay = QVBoxLayout(c2)
        c2_lay.setContentsMargins(26, 22, 26, 22)
        c2_lay.setSpacing(10)

        t2_box = QHBoxLayout()
        c2_title = QLabel("Database Engine & Persistence")
        c2_title.setFont(theme.font_h2())
        c2_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-weight: 700;")
        t2_box.addWidget(c2_title)
        t2_box.addStretch()
        t2_box.addWidget(StatusBadge("SQLITE 3", "success"))
        c2_lay.addLayout(t2_box)

        c2_text = QLabel(
            "All candidate records, faculty details, marks, and billing logs reside inside <b>school.db</b>. "
            "Native SQLite transactions ensure zero data loss during power loss or abrupt closures. "
            "To back up your institution data, simply copy <code>school.db</code> to external storage."
        )
        c2_text.setFont(theme.font_regular())
        c2_lay.addWidget(c2_text)
        lay.addWidget(c2)

        # 3. IT Contact Card
        c3 = ModernCard()
        c3_lay = QVBoxLayout(c3)
        c3_lay.setContentsMargins(26, 22, 26, 22)
        c3_lay.setSpacing(10)

        t3_box = QHBoxLayout()
        c3_title = QLabel("Campus Technical Assistance")
        c3_title.setFont(theme.font_h2())
        c3_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-weight: 700;")
        t3_box.addWidget(c3_title)
        t3_box.addStretch()
        t3_box.addWidget(StatusBadge("SUPPORT DESK", "primary"))
        c3_lay.addLayout(t3_box)

        self.c3_text = QLabel()
        self.c3_text.setFont(theme.font_regular())
        c3_lay.addWidget(self.c3_text)
        self.refresh_data()
        lay.addWidget(c3)

        lay.addStretch()

        scroll.setWidget(container)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)

    def refresh_data(self):
        sch = db.get_app_data("systemName", "EXCELLENCE SCHOOL SYSTEM")
        if hasattr(self, "c3_text"):
            self.c3_text.setText(
                f"<b>Software Platform:</b> Edura — Unified School Management Suite (v2.4 LTS)<br>"
                f"<b>Institution:</b> {sch}<br>"
                f"<b>Principal Administrator:</b> Shahid Zahoor Khan<br>"
                f"<b>Campus IT Hotline:</b> +92 300 555-0199<br>"
                f"<b>Framework:</b> Python 3.10+ & PySide6 / Qt6 (Enterprise Desktop Edition)"
            )
