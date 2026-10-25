"""
Attendance Module for School Management System.
Redesigned with date navigators, attendance statistics, and modern table cells.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QMessageBox
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, Signal
import core.theme as theme
import core.database as db
from core.widgets import ModernCard, StatusBadge, PageHeader
from datetime import date, timedelta


class AttendanceView(QWidget):
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_date = date.today()
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"background-color: {theme.BACKGROUND};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(18)

        # Header Bar
        header = PageHeader(
            "Daily Student Attendance Register",
            "Record presence, absences, and official leaves across all school grades"
        )
        btn_all_present = theme.create_outline_button("✓ Mark All Present")
        btn_all_present.setFixedHeight(38)
        btn_all_present.clicked.connect(self.mark_all_present)
        header.add_action(btn_all_present)

        btn_save = theme.create_primary_button("💾 Save Register")
        btn_save.setFixedHeight(38)
        btn_save.clicked.connect(self.save_attendance)
        header.add_action(btn_save)

        layout.addWidget(header)

        # Controls & Navigation Card
        ctrl_card = ModernCard()
        ctrl_lay = QHBoxLayout(ctrl_card)
        ctrl_lay.setContentsMargins(20, 12, 20, 12)
        ctrl_lay.setSpacing(14)

        cls_lbl = QLabel("Class Grade:")
        cls_lbl.setFont(theme.font_bold())
        ctrl_lay.addWidget(cls_lbl)

        self.class_selector = QComboBox()
        self.class_selector.addItems([f"Class {i}" for i in range(1, 11)])
        self.class_selector.currentIndexChanged.connect(self.load_attendance)
        ctrl_lay.addWidget(self.class_selector)

        ctrl_lay.addSpacing(10)

        # Date Navigation
        btn_prev = theme.create_outline_button("◀ Prev")
        btn_prev.setFixedHeight(34)
        btn_prev.clicked.connect(self.prev_day)
        ctrl_lay.addWidget(btn_prev)

        self.date_lbl = QLabel(self.current_date.strftime("%A, %d %B %Y"))
        self.date_lbl.setFont(theme.font_bold())
        self.date_lbl.setStyleSheet(f"color: {theme.PRIMARY}; padding: 0 10px; font-size: 13px;")
        ctrl_lay.addWidget(self.date_lbl)

        btn_next = theme.create_outline_button("Next ▶")
        btn_next.setFixedHeight(34)
        btn_next.clicked.connect(self.next_day)
        ctrl_lay.addWidget(btn_next)

        btn_today = theme.create_secondary_button("Today")
        btn_today.setFixedHeight(34)
        btn_today.clicked.connect(self.goto_today)
        ctrl_lay.addWidget(btn_today)

        ctrl_lay.addStretch()

        # Stats Badge
        self.stats_lbl = QLabel("Present: 0 | Absent: 0")
        self.stats_lbl.setFont(theme.font_small())
        self.stats_lbl.setStyleSheet(f"""
            background-color: #F1F5F9;
            color: {theme.TEXT_PRIMARY};
            border-radius: 6px;
            padding: 6px 12px;
            font-weight: 700;
        """)
        ctrl_lay.addWidget(self.stats_lbl)

        layout.addWidget(ctrl_card)

        # Attendance Table Card
        table_card = ModernCard()
        t_lay = QVBoxLayout(table_card)
        t_lay.setContentsMargins(16, 16, 16, 16)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Admission #", "Student Full Name", "Father Name", "Attendance Status"])
        theme.format_table(self.table, 46)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        a_hdr = self.table.horizontalHeader()
        a_hdr.setSectionResizeMode(0, QHeaderView.Interactive)
        a_hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        a_hdr.setSectionResizeMode(2, QHeaderView.Interactive)
        a_hdr.setSectionResizeMode(3, QHeaderView.Interactive)
        self.table.setColumnWidth(0, 125)
        self.table.setColumnWidth(2, 180)
        self.table.setColumnWidth(3, 180)
        t_lay.addWidget(self.table)

        layout.addWidget(table_card)

        self.load_attendance()

    def prev_day(self):
        self.current_date -= timedelta(days=1)
        self.update_date_label()
        self.load_attendance()

    def next_day(self):
        self.current_date += timedelta(days=1)
        self.update_date_label()
        self.load_attendance()

    def goto_today(self):
        self.current_date = date.today()
        self.update_date_label()
        self.load_attendance()

    def update_date_label(self):
        self.date_lbl.setText(self.current_date.strftime("%A, %d %B %Y"))

    def load_attendance(self):
        cls = self.class_selector.currentText().replace("Class ", "")
        date_str = self.current_date.isoformat()
        students = [s for s in db.get_all_students() if s.class_name == cls]
        existing_att = db.get_attendance_for_class(date_str, cls)

        self.table.setRowCount(len(students))
        self.status_combos = {}

        p_count = 0
        a_count = 0

        for row, s in enumerate(students):
            item_adm = QTableWidgetItem(s.admission_no)
            item_adm.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, item_adm)
            self.table.setItem(row, 1, QTableWidgetItem(s.get_full_name()))
            self.table.setItem(row, 2, QTableWidgetItem(s.father_name))

            status = existing_att.get(s.admission_no, "PRESENT")
            combo = theme.create_table_combobox(["PRESENT", "ABSENT", "LEAVE", "LATE"], status.upper())
            combo.currentIndexChanged.connect(self.update_stats)

            self.status_combos[s.admission_no] = combo
            self.table.setCellWidget(row, 3, theme.create_cell_widget(combo))

            if status.upper() == "PRESENT":
                p_count += 1
            else:
                a_count += 1

        self.update_stats()

    def update_stats(self):
        p_count = 0
        a_count = 0
        l_count = 0
        late_count = 0
        for combo in self.status_combos.values():
            st = combo.currentText()
            if st == "PRESENT":
                p_count += 1
            elif st == "ABSENT":
                a_count += 1
            elif st == "LEAVE":
                l_count += 1
            else:
                late_count += 1
        total = len(self.status_combos)
        rate = (p_count / total * 100) if total > 0 else 0
        self.stats_lbl.setText(
            f"Enrolled: {total}  |  Present: {p_count} ({rate:.1f}%)  |  Absent: {a_count}  |  Leave: {l_count}"
        )

    def mark_all_present(self):
        for combo in self.status_combos.values():
            combo.setCurrentText("PRESENT")
        self.update_stats()

    def save_attendance(self):
        cls = self.class_selector.currentText().replace("Class ", "")
        date_str = self.current_date.isoformat()
        for adm_no, combo in self.status_combos.items():
            db.save_student_attendance(date_str, adm_no, combo.currentText())

        QMessageBox.information(
            self, "Attendance Saved",
            f"Successfully updated attendance records for {len(self.status_combos)} students of Class {cls} on {date_str}!"
        )
