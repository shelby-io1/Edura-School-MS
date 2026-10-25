"""
Syllabus & Curriculum Module for School Management System.
Redesigned with ModernCard containers, topic checklists, and animated coverage bar.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QTabWidget, QProgressBar, QCheckBox, QTextEdit, QMessageBox
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, Signal
import core.theme as theme
import core.database as db
from core.widgets import ModernCard, StatusBadge, PageHeader
import json


class SyllabusView(QWidget):
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"background-color: {theme.BACKGROUND};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(18)

        # Header Bar
        header = PageHeader(
            "Curriculum & Syllabus Coverage",
            "Term-wise chapter objectives, lecture notes, and syllabus completion tracker"
        )
        btn_save = theme.create_primary_button("💾 Save Curriculum Progress")
        btn_save.setFixedHeight(38)
        btn_save.clicked.connect(self.save_current_syllabus)
        header.add_action(btn_save)
        layout.addWidget(header)

        # Filter & Progress Bar Card
        filter_card = ModernCard()
        filter_lay = QHBoxLayout(filter_card)
        filter_lay.setContentsMargins(20, 12, 20, 12)
        filter_lay.setSpacing(14)

        cls_lbl = QLabel("Class Grade:")
        cls_lbl.setFont(theme.font_bold())
        filter_lay.addWidget(cls_lbl)

        self.class_combo = QComboBox()
        self.class_combo.addItems([f"Class {i}" for i in range(1, 11)])
        self.class_combo.currentIndexChanged.connect(self.load_syllabus)
        filter_lay.addWidget(self.class_combo)

        sub_lbl = QLabel("Subject:")
        sub_lbl.setFont(theme.font_bold())
        filter_lay.addWidget(sub_lbl)

        self.subject_combo = QComboBox()
        self.subject_combo.addItems(db.DEFAULT_SUBJECTS)
        self.subject_combo.currentIndexChanged.connect(self.load_syllabus)
        filter_lay.addWidget(self.subject_combo)

        filter_lay.addStretch()

        # Coverage Bar
        self.progress_lbl = QLabel("Coverage: 0%")
        self.progress_lbl.setFont(theme.font_bold())
        self.progress_lbl.setStyleSheet(f"color: {theme.TEXT_PRIMARY};")
        filter_lay.addWidget(self.progress_lbl)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedWidth(160)
        filter_lay.addWidget(self.progress_bar)

        layout.addWidget(filter_card)

        # Term Tabs Card
        tabs_card = ModernCard()
        card_lay = QVBoxLayout(tabs_card)
        card_lay.setContentsMargins(16, 16, 16, 16)

        self.tabs = QTabWidget()
        self.term_tables = []
        self.term_notes = []

        for term_idx, term_name in enumerate(["1st Term (Mid-Year)", "2nd Term (Annual)", "3rd Term (Finals)"]):
            tab_widget = QWidget()
            tab_lay = QVBoxLayout(tab_widget)
            tab_lay.setContentsMargins(8, 8, 8, 8)
            tab_lay.setSpacing(12)

            tbl = QTableWidget(5, 3)
            tbl.setHorizontalHeaderLabels(["Chapter / Unit", "Topics & Learning Objectives", "Completion Status"])
            theme.format_table(tbl, 44)
            s_hdr = tbl.horizontalHeader()
            s_hdr.setSectionResizeMode(0, QHeaderView.Interactive)
            s_hdr.setSectionResizeMode(1, QHeaderView.Stretch)
            s_hdr.setSectionResizeMode(2, QHeaderView.Interactive)
            tbl.setColumnWidth(0, 160)
            tbl.setColumnWidth(2, 180)
            tbl.setEditTriggers(QTableWidget.NoEditTriggers)
            tab_lay.addWidget(tbl)
            self.term_tables.append(tbl)

            notes_lbl = QLabel("Teacher Notes & Lecture Guidelines:")
            notes_lbl.setFont(theme.font_bold())
            tab_lay.addWidget(notes_lbl)

            notes = QTextEdit()
            notes.setFixedHeight(65)
            notes.setPlaceholderText("Enter specific exam guidelines or lecture instructions for this term...")
            tab_lay.addWidget(notes)
            self.term_notes.append(notes)

            self.tabs.addTab(tab_widget, term_name)

        card_lay.addWidget(self.tabs)
        layout.addWidget(tabs_card)

        self.load_syllabus()

    def load_syllabus(self):
        cls = self.class_combo.currentText().replace("Class ", "")
        subj = self.subject_combo.currentText()
        key = f"syllabus_data_{cls}_{subj}"
        raw = db.get_app_data(key, "")

        data = {}
        if raw:
            try:
                data = json.loads(raw)
            except Exception:
                data = {}

        total_topics = 0
        completed_topics = 0

        for t_idx in range(3):
            tbl = self.term_tables[t_idx]
            notes = self.term_notes[t_idx]

            term_key = f"term_{t_idx + 1}"
            term_info = data.get(term_key, {})
            notes.setText(term_info.get("notes", ""))

            rows = term_info.get("topics", [])
            if not rows:
                rows = [
                    {"unit": f"Unit {t_idx * 5 + i + 1}", "desc": f"Core topics of {subj} Part {i + 1}", "done": False}
                    for i in range(5)
                ]

            tbl.setRowCount(len(rows))
            for r_idx, r_data in enumerate(rows):
                tbl.setItem(r_idx, 0, QTableWidgetItem(r_data.get("unit", "")))
                tbl.setItem(r_idx, 1, QTableWidgetItem(r_data.get("desc", "")))

                chk = QCheckBox("Mark Completed")
                chk.setChecked(r_data.get("done", False))
                chk.stateChanged.connect(self.calculate_progress)
                tbl.setCellWidget(r_idx, 2, chk)

                total_topics += 1
                if r_data.get("done", False):
                    completed_topics += 1

        pct = int(completed_topics / total_topics * 100) if total_topics > 0 else 0
        self.progress_bar.setValue(pct)
        self.progress_lbl.setText(f"Coverage: {pct}%")

    def calculate_progress(self):
        total = 0
        done = 0
        for tbl in self.term_tables:
            for r in range(tbl.rowCount()):
                chk = tbl.cellWidget(r, 2)
                if isinstance(chk, QCheckBox):
                    total += 1
                    if chk.isChecked():
                        done += 1
        pct = int(done / total * 100) if total > 0 else 0
        self.progress_bar.setValue(pct)
        self.progress_lbl.setText(f"Coverage: {pct}%")

    def save_current_syllabus(self):
        cls = self.class_combo.currentText().replace("Class ", "")
        subj = self.subject_combo.currentText()
        key = f"syllabus_data_{cls}_{subj}"

        data = {}
        for t_idx in range(3):
            tbl = self.term_tables[t_idx]
            notes = self.term_notes[t_idx]

            term_rows = []
            for r in range(tbl.rowCount()):
                u_item = tbl.item(r, 0)
                d_item = tbl.item(r, 1)
                chk = tbl.cellWidget(r, 2)
                term_rows.append({
                    "unit": u_item.text().strip() if u_item else "",
                    "desc": d_item.text().strip() if d_item else "",
                    "done": chk.isChecked() if isinstance(chk, QCheckBox) else False
                })

            data[f"term_{t_idx + 1}"] = {
                "notes": notes.toPlainText().strip(),
                "topics": term_rows
            }

        db.save_app_data(key, json.dumps(data))
        QMessageBox.information(self, "Progress Saved", f"Syllabus coverage updated for Class {cls} ({subj})!")
