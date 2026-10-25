"""
Quizzes Module for School Management System.
Redesigned with ModernCard containers, StatusBadge chips, and grading tables.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QMessageBox,
    QStackedWidget
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, Signal
import core.theme as theme
import core.database as db
from core.widgets import ModernCard, StatusBadge, PageHeader
from datetime import date


class QuizzesView(QWidget):
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

        self.list_widget = self.create_quiz_list_view()
        self.stack.addWidget(self.list_widget)

        self.marks_widget = self.create_marks_entry_view()
        self.stack.addWidget(self.marks_widget)

        self.create_quiz_widget = self.create_new_quiz_view()
        self.stack.addWidget(self.create_quiz_widget)

        self.stack.setCurrentIndex(0)

    # --- 1. QUIZ LIST VIEW ---
    def create_quiz_list_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(18)

        header = PageHeader(
            "Quizzes & Class Assessments",
            "Schedule continuous evaluation quizzes, set test weightage, and record student scores"
        )
        btn_new_quiz = theme.create_primary_button("+ Create New Quiz")
        btn_new_quiz.setFixedHeight(38)
        btn_new_quiz.clicked.connect(self.open_create_quiz_dialog)
        header.add_action(btn_new_quiz)
        layout.addWidget(header)

        # Filter bar card
        filter_card = ModernCard()
        filter_lay = QHBoxLayout(filter_card)
        filter_lay.setContentsMargins(20, 12, 20, 12)
        filter_lay.setSpacing(14)

        cls_lbl = QLabel("Class Grade:")
        cls_lbl.setFont(theme.font_bold())
        filter_lay.addWidget(cls_lbl)

        self.class_combo = QComboBox()
        self.class_combo.addItems([f"Class {i}" for i in range(1, 11)])
        self.class_combo.currentIndexChanged.connect(self.load_quizzes)
        filter_lay.addWidget(self.class_combo)

        sub_lbl = QLabel("Subject:")
        sub_lbl.setFont(theme.font_bold())
        filter_lay.addWidget(sub_lbl)

        self.subject_combo = QComboBox()
        self.subject_combo.addItems(db.DEFAULT_SUBJECTS)
        self.subject_combo.currentIndexChanged.connect(self.load_quizzes)
        filter_lay.addWidget(self.subject_combo)

        filter_lay.addStretch()

        btn_refresh = theme.create_secondary_button("Refresh")
        btn_refresh.clicked.connect(self.load_quizzes)
        filter_lay.addWidget(btn_refresh)

        layout.addWidget(filter_card)

        # Quizzes Table Card
        table_card = ModernCard()
        t_lay = QVBoxLayout(table_card)
        t_lay.setContentsMargins(16, 16, 16, 16)

        self.quiz_table = QTableWidget(0, 5)
        self.quiz_table.setHorizontalHeaderLabels(["Quiz ID", "Assessment Title", "Test Date", "Total Marks", "Actions"])
        theme.format_table(self.quiz_table, 46)
        self.quiz_table.setEditTriggers(QTableWidget.NoEditTriggers)

        q_hdr = self.quiz_table.horizontalHeader()
        q_hdr.setSectionResizeMode(0, QHeaderView.Interactive)
        q_hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        q_hdr.setSectionResizeMode(2, QHeaderView.Interactive)
        q_hdr.setSectionResizeMode(3, QHeaderView.Interactive)
        q_hdr.setSectionResizeMode(4, QHeaderView.Interactive)
        self.quiz_table.setColumnWidth(0, 90)
        self.quiz_table.setColumnWidth(2, 125)
        self.quiz_table.setColumnWidth(3, 115)
        self.quiz_table.setColumnWidth(4, 185)
        t_lay.addWidget(self.quiz_table)

        layout.addWidget(table_card)

        self.load_quizzes()
        return widget

    def load_quizzes(self):
        cls = self.class_combo.currentText().replace("Class ", "")
        subj = self.subject_combo.currentText()
        quizzes = db.get_quizzes(cls, subj)

        self.quiz_table.setRowCount(len(quizzes))
        for row, q in enumerate(quizzes):
            self.quiz_table.setItem(row, 0, QTableWidgetItem(f"#{q['id']}"))
            self.quiz_table.setItem(row, 1, QTableWidgetItem(q["title"]))
            self.quiz_table.setItem(row, 2, QTableWidgetItem(q["date"]))

            badge = StatusBadge(f"{q['maxMarks']:.0f} Marks", "primary")
            self.quiz_table.setCellWidget(row, 3, theme.create_cell_widget(badge))

            btn_grade = theme.create_table_button("Grade Scores", "primary")
            btn_grade.clicked.connect(lambda _, qz=q: self.open_marks_entry(qz))

            btn_del = theme.create_table_button("Delete", "danger")
            btn_del.clicked.connect(lambda _, qid=q["id"]: self.delete_quiz(qid))

            self.quiz_table.setCellWidget(row, 4, theme.create_cell_widget(btn_grade, btn_del))

    def create_new_quiz_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(18)

        self.new_quiz_header = PageHeader(
            "Create & Publish Continuous Assessment Quiz",
            "Specify evaluation parameters, target curriculum, and total evaluation points"
        )
        layout.addWidget(self.new_quiz_header)

        card = ModernCard()
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(24, 24, 24, 24)
        c_lay.setSpacing(16)

        self.quiz_info_lbl = QLabel()
        self.quiz_info_lbl.setFont(theme.font_h2())
        self.quiz_info_lbl.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-weight: 700;")
        c_lay.addWidget(self.quiz_info_lbl)

        form = QFormLayout()
        form.setSpacing(14)

        self.quiz_title_input = QLineEdit()
        self.quiz_title_input.setPlaceholderText("e.g. Chapter 4 Diagnostic Quiz")
        self.quiz_title_input.setFixedHeight(38)

        self.quiz_max_marks_spin = QDoubleSpinBox()
        self.quiz_max_marks_spin.setRange(1, 500)
        self.quiz_max_marks_spin.setValue(25.0)
        self.quiz_max_marks_spin.setFixedHeight(38)

        form.addRow("Assessment Title*:", self.quiz_title_input)
        form.addRow("Maximum Points*:", self.quiz_max_marks_spin)
        c_lay.addLayout(form)

        btn_row = QHBoxLayout()
        btn_publish = theme.create_primary_button("✓ Publish Quiz Assessment")
        btn_publish.setFixedHeight(38)
        btn_publish.clicked.connect(self.save_new_quiz)
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

    def open_create_quiz_dialog(self):
        cls = self.class_combo.currentText().replace("Class ", "")
        subj = self.subject_combo.currentText()
        self.quiz_info_lbl.setText(f"Target Course: Class {cls} — {subj}")
        self.quiz_title_input.clear()
        self.quiz_max_marks_spin.setValue(25.0)
        self.stack.setCurrentIndex(2)

    def save_new_quiz(self):
        cls = self.class_combo.currentText().replace("Class ", "")
        subj = self.subject_combo.currentText()
        t = self.quiz_title_input.text().strip()
        if not t:
            QMessageBox.warning(self, "Validation Error", "Quiz Title is required.")
            return
        db.save_quiz(cls, subj, t, self.quiz_max_marks_spin.value(), date.today().isoformat())
        QMessageBox.information(self, "Published", f"Quiz '{t}' published successfully for Class {cls}!")
        self.stack.setCurrentIndex(0)
        self.load_quizzes()

    def delete_quiz(self, quiz_id: int):
        ret = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to remove Quiz #{quiz_id}? All recorded marks will be erased.",
            QMessageBox.Yes | QMessageBox.No
        )
        if ret == QMessageBox.Yes:
            db.delete_quiz(quiz_id)
            self.load_quizzes()

    # --- 2. MARKS ENTRY VIEW ---
    def create_marks_entry_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(18)

        self.marks_header = PageHeader("Record Quiz Marks", "Enter scores for each student candidate")
        btn_save = theme.create_primary_button("💾 Save Recorded Marks")
        btn_save.setFixedHeight(38)
        btn_save.clicked.connect(self.save_marks)
        self.marks_header.add_action(btn_save)

        layout.addWidget(self.marks_header)

        table_card = ModernCard()
        t_lay = QVBoxLayout(table_card)
        t_lay.setContentsMargins(16, 16, 16, 16)

        self.marks_table = QTableWidget(0, 4)
        self.marks_table.setHorizontalHeaderLabels(["Adm #", "Student Name", "Marks Obtained", "Grading Status"])
        theme.format_table(self.marks_table, 46)
        self.marks_table.setEditTriggers(QTableWidget.NoEditTriggers)

        m_hdr = self.marks_table.horizontalHeader()
        m_hdr.setSectionResizeMode(0, QHeaderView.Interactive)
        m_hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        m_hdr.setSectionResizeMode(2, QHeaderView.Interactive)
        m_hdr.setSectionResizeMode(3, QHeaderView.Interactive)
        self.marks_table.setColumnWidth(0, 125)
        self.marks_table.setColumnWidth(2, 160)
        self.marks_table.setColumnWidth(3, 140)
        t_lay.addWidget(self.marks_table)

        layout.addWidget(table_card)
        return widget

    def open_marks_entry(self, quiz: dict):
        self.current_quiz = quiz
        self.marks_header.lbl_title.setText(f"Quiz Grading: {quiz['title']}")
        self.marks_header.lbl_sub.setText(f"Class {quiz['className']} • {quiz['subjectName']} • Maximum Marks: {quiz['maxMarks']:.1f}")

        cls = quiz["className"]
        students = [s for s in db.get_all_students() if s.class_name == cls]
        existing_marks = db.get_quiz_marks(quiz["id"])

        self.marks_table.setRowCount(len(students))
        self.marks_inputs = {}

        for row, s in enumerate(students):
            item_adm = QTableWidgetItem(s.admission_no)
            item_adm.setTextAlignment(Qt.AlignCenter)
            self.marks_table.setItem(row, 0, item_adm)
            self.marks_table.setItem(row, 1, QTableWidgetItem(s.get_full_name()))

            spin = QDoubleSpinBox()
            spin.setRange(0, quiz["maxMarks"])
            spin.setValue(existing_marks.get(s.admission_no, 0.0))
            spin.setFixedHeight(30)
            self.marks_inputs[s.admission_no] = spin
            self.marks_table.setCellWidget(row, 2, theme.create_cell_widget(spin))

            status_str = "GRADED" if s.admission_no in existing_marks else "PENDING"
            badge = StatusBadge.from_status(status_str)
            self.marks_table.setCellWidget(row, 3, theme.create_cell_widget(badge))

        self.stack.setCurrentIndex(1)

    def save_marks(self):
        quiz_id = self.current_quiz["id"]
        marks_dict = {adm_no: spin.value() for adm_no, spin in self.marks_inputs.items()}
        db.save_quiz_marks(quiz_id, marks_dict)
        QMessageBox.information(self, "Saved", f"Recorded scores for {len(marks_dict)} students!")
        self.stack.setCurrentIndex(0)
