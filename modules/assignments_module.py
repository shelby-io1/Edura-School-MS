"""
Assignments Module for School Management System.
Redesigned with ModernCard containers, StatusBadge chips, and grading views.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QMessageBox,
    QStackedWidget, QDateEdit
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, Signal, QDate
import core.theme as theme
import core.database as db
from core.widgets import ModernCard, StatusBadge, PageHeader
from datetime import date


class AssignmentsView(QWidget):
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"background-color: {theme.BACKGROUND};")
        self.main_lay = QVBoxLayout(self)
        self.main_lay.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        self.main_lay.addWidget(self.stack)

        self.list_widget = self.create_assignment_list_view()
        self.stack.addWidget(self.list_widget)

        self.marks_widget = self.create_marks_entry_view()
        self.stack.addWidget(self.marks_widget)

        self.create_assign_widget = self.create_new_assignment_view()
        self.stack.addWidget(self.create_assign_widget)

        self.stack.setCurrentIndex(0)

    # --- 1. ASSIGNMENT LIST VIEW ---
    def create_assignment_list_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(18)

        header = PageHeader(
            "Homework & Assignments Tracker",
            "Assign coursework projects, manage submission deadlines, and evaluate student work"
        )
        btn_new_assign = theme.create_primary_button("+ Post New Assignment")
        btn_new_assign.setFixedHeight(38)
        btn_new_assign.clicked.connect(self.open_create_assignment_dialog)
        header.add_action(btn_new_assign)
        layout.addWidget(header)

        # Filter Card
        filter_card = ModernCard()
        filter_lay = QHBoxLayout(filter_card)
        filter_lay.setContentsMargins(20, 12, 20, 12)
        filter_lay.setSpacing(14)

        cls_lbl = QLabel("Class Grade:")
        cls_lbl.setFont(theme.font_bold())
        filter_lay.addWidget(cls_lbl)

        self.class_combo = QComboBox()
        self.class_combo.addItems([f"Class {i}" for i in range(1, 11)])
        self.class_combo.currentIndexChanged.connect(self.load_assignments)
        filter_lay.addWidget(self.class_combo)

        sub_lbl = QLabel("Subject:")
        sub_lbl.setFont(theme.font_bold())
        filter_lay.addWidget(sub_lbl)

        self.subject_combo = QComboBox()
        self.subject_combo.addItems(db.DEFAULT_SUBJECTS)
        self.subject_combo.currentIndexChanged.connect(self.load_assignments)
        filter_lay.addWidget(self.subject_combo)

        filter_lay.addStretch()

        btn_refresh = theme.create_secondary_button("Refresh")
        btn_refresh.clicked.connect(self.load_assignments)
        filter_lay.addWidget(btn_refresh)

        layout.addWidget(filter_card)

        # Assignments Table Card
        table_card = ModernCard()
        t_lay = QVBoxLayout(table_card)
        t_lay.setContentsMargins(16, 16, 16, 16)

        self.assign_table = QTableWidget(0, 5)
        self.assign_table.setHorizontalHeaderLabels(["ID", "Coursework Title", "Submission Due", "Max Marks", "Actions"])
        theme.format_table(self.assign_table, 46)
        self.assign_table.setEditTriggers(QTableWidget.NoEditTriggers)

        as_hdr = self.assign_table.horizontalHeader()
        as_hdr.setSectionResizeMode(0, QHeaderView.Interactive)
        as_hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        as_hdr.setSectionResizeMode(2, QHeaderView.Interactive)
        as_hdr.setSectionResizeMode(3, QHeaderView.Interactive)
        as_hdr.setSectionResizeMode(4, QHeaderView.Interactive)
        self.assign_table.setColumnWidth(0, 80)
        self.assign_table.setColumnWidth(2, 130)
        self.assign_table.setColumnWidth(3, 115)
        self.assign_table.setColumnWidth(4, 170)
        t_lay.addWidget(self.assign_table)

        layout.addWidget(table_card)

        self.load_assignments()
        return widget

    def load_assignments(self):
        cls = self.class_combo.currentText().replace("Class ", "")
        subj = self.subject_combo.currentText()
        assignments = db.get_assignments(cls, subj)

        self.assign_table.setRowCount(len(assignments))
        for row, a in enumerate(assignments):
            self.assign_table.setItem(row, 0, QTableWidgetItem(f"#{a['id']}"))
            self.assign_table.setItem(row, 1, QTableWidgetItem(a["title"]))
            self.assign_table.setItem(row, 2, QTableWidgetItem(a["dueDate"]))

            badge = StatusBadge(f"{a['maxMarks']:.0f} Marks", "primary")
            self.assign_table.setCellWidget(row, 3, theme.create_cell_widget(badge))

            btn_grade = theme.create_table_button("Grade", "primary")
            btn_grade.clicked.connect(lambda _, asg=a: self.open_marks_entry(asg))

            btn_del = theme.create_table_button("Delete", "danger")
            btn_del.clicked.connect(lambda _, aid=a["id"]: self.delete_assignment(aid))

            self.assign_table.setCellWidget(row, 4, theme.create_cell_widget(btn_grade, btn_del))

    def create_new_assignment_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(18)

        header = PageHeader(
            "Post Homework & Coursework Assignment",
            "Set project specifications, submission deadlines, and maximum grading weightage"
        )
        layout.addWidget(header)

        card = ModernCard()
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(24, 24, 24, 24)
        c_lay.setSpacing(16)

        self.assign_info_lbl = QLabel()
        self.assign_info_lbl.setFont(theme.font_h2())
        self.assign_info_lbl.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-weight: 700;")
        c_lay.addWidget(self.assign_info_lbl)

        form = QFormLayout()
        form.setSpacing(14)

        self.assign_title_input = QLineEdit()
        self.assign_title_input.setPlaceholderText("e.g. Science Laboratory Workbook")
        self.assign_title_input.setFixedHeight(38)

        self.assign_max_marks_spin = QDoubleSpinBox()
        self.assign_max_marks_spin.setRange(1, 500)
        self.assign_max_marks_spin.setValue(50.0)
        self.assign_max_marks_spin.setFixedHeight(38)

        self.assign_date_edit = QDateEdit()
        self.assign_date_edit.setCalendarPopup(True)
        self.assign_date_edit.setDate(QDate.currentDate().addDays(7))
        self.assign_date_edit.setFixedHeight(38)

        form.addRow("Assignment Title*:", self.assign_title_input)
        form.addRow("Maximum Points*:", self.assign_max_marks_spin)
        form.addRow("Submission Deadline*:", self.assign_date_edit)
        c_lay.addLayout(form)

        btn_row = QHBoxLayout()
        btn_publish = theme.create_primary_button("✓ Post Assignment")
        btn_publish.setFixedHeight(38)
        btn_publish.clicked.connect(self.save_new_assignment)
        btn_cancel = theme.create_outline_button("Cancel")
        btn_cancel.setFixedHeight(38)
        btn_cancel.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_publish)
        btn_row.addStretch()
        c_lay.addLayout(btn_row)

        layout.addWidget(card)
        layout.addStretch()
        return widget

    def open_create_assignment_dialog(self):
        cls = self.class_combo.currentText().replace("Class ", "")
        subj = self.subject_combo.currentText()
        self.assign_info_lbl.setText(f"Target Course: Class {cls} — {subj}")
        self.assign_title_input.clear()
        self.assign_max_marks_spin.setValue(50.0)
        self.assign_date_edit.setDate(QDate.currentDate().addDays(7))
        self.stack.setCurrentIndex(2)

    def save_new_assignment(self):
        cls = self.class_combo.currentText().replace("Class ", "")
        subj = self.subject_combo.currentText()
        t = self.assign_title_input.text().strip()
        if not t:
            QMessageBox.warning(self, "Validation Error", "Assignment Title is required.")
            return
        due_str = self.assign_date_edit.date().toString("yyyy-MM-dd")
        db.save_assignment(cls, subj, t, self.assign_max_marks_spin.value(), due_str)
        QMessageBox.information(self, "Posted", f"Assignment '{t}' posted successfully for Class {cls}!")
        self.stack.setCurrentIndex(0)
        self.load_assignments()

    def delete_assignment(self, assignment_id: int):
        ret = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to remove Assignment #{assignment_id}? All submissions will be cleared.",
            QMessageBox.Yes | QMessageBox.No
        )
        if ret == QMessageBox.Yes:
            db.delete_assignment(assignment_id)
            self.load_assignments()

    # --- 2. MARKS ENTRY VIEW ---
    def create_marks_entry_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(18)

        self.marks_header = PageHeader("Grade Assignment Submissions", "Record marks for student submissions")
        btn_save = theme.create_primary_button("💾 Save Recorded Grades")
        btn_save.setFixedHeight(38)
        btn_save.clicked.connect(self.save_marks)
        self.marks_header.add_action(btn_save)

        layout.addWidget(self.marks_header)

        table_card = ModernCard()
        t_lay = QVBoxLayout(table_card)
        t_lay.setContentsMargins(16, 16, 16, 16)

        self.marks_table = QTableWidget(0, 4)
        self.marks_table.setHorizontalHeaderLabels(["Adm #", "Student Name", "Marks Obtained", "Status"])
        theme.format_table(self.marks_table, 46)
        self.marks_table.setEditTriggers(QTableWidget.NoEditTriggers)

        am_hdr = self.marks_table.horizontalHeader()
        am_hdr.setSectionResizeMode(0, QHeaderView.Interactive)
        am_hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        am_hdr.setSectionResizeMode(2, QHeaderView.Interactive)
        am_hdr.setSectionResizeMode(3, QHeaderView.Interactive)
        self.marks_table.setColumnWidth(0, 125)
        self.marks_table.setColumnWidth(2, 160)
        self.marks_table.setColumnWidth(3, 140)
        t_lay.addWidget(self.marks_table)

        layout.addWidget(table_card)
        return widget

    def open_marks_entry(self, asg: dict):
        self.current_asg = asg
        self.marks_header.lbl_title.setText(f"Grading: {asg['title']}")
        self.marks_header.lbl_sub.setText(f"Class {asg['className']} • {asg['subjectName']} • Due: {asg['dueDate']} • Max Marks: {asg['maxMarks']:.1f}")

        cls = asg["className"]
        students = [s for s in db.get_all_students() if s.class_name == cls]
        existing_marks = db.get_assignment_marks(asg["id"])

        self.marks_table.setRowCount(len(students))
        self.marks_inputs = {}

        for row, s in enumerate(students):
            item_adm = QTableWidgetItem(s.admission_no)
            item_adm.setTextAlignment(Qt.AlignCenter)
            self.marks_table.setItem(row, 0, item_adm)
            self.marks_table.setItem(row, 1, QTableWidgetItem(s.get_full_name()))

            spin = QDoubleSpinBox()
            spin.setRange(0, asg["maxMarks"])
            spin.setValue(existing_marks.get(s.admission_no, 0.0))
            spin.setFixedHeight(30)
            self.marks_inputs[s.admission_no] = spin
            self.marks_table.setCellWidget(row, 2, theme.create_cell_widget(spin))

            status_str = "GRADED" if s.admission_no in existing_marks else "PENDING"
            badge = StatusBadge.from_status(status_str)
            self.marks_table.setCellWidget(row, 3, theme.create_cell_widget(badge))

        self.stack.setCurrentIndex(1)

    def save_marks(self):
        asg_id = self.current_asg["id"]
        marks_dict = {adm_no: spin.value() for adm_no, spin in self.marks_inputs.items()}
        db.save_assignment_marks(asg_id, marks_dict)
        QMessageBox.information(self, "Saved", f"Recorded assignment scores for {len(marks_dict)} students!")
        self.stack.setCurrentIndex(0)
