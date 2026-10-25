"""
Examination & Results Module for School Management System.
Redesigned with ModernCard containers, StatusBadge letter grades, and report card generator.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QDoubleSpinBox, QMessageBox, QStackedWidget, QScrollArea
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, Signal
import core.theme as theme
import core.database as db
from core.widgets import ModernCard, StatusBadge, MetricCard, PageHeader, ModernSearchBar
import json


class ResultsView(QWidget):
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"background-color: {theme.BACKGROUND};")
        self.main_lay = QVBoxLayout(self)
        self.main_lay.setContentsMargins(0, 0, 0, 0)
        self.main_lay.setSpacing(0)

        self.stack = QStackedWidget()
        self.main_lay.addWidget(self.stack)

        self.overview_widget = self.create_overview_view()
        self.stack.addWidget(self.overview_widget)

        self.report_card_container = QWidget()
        self.report_card_lay = QVBoxLayout(self.report_card_container)
        self.report_card_lay.setContentsMargins(32, 24, 32, 24)
        self.report_card_lay.setSpacing(18)
        self.stack.addWidget(self.report_card_container)

        self.promotion_widget = self.create_promotion_view()
        self.stack.addWidget(self.promotion_widget)

        self.stack.setCurrentIndex(0)
        self.load_results()

    def create_overview_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(18)

        # Header Bar
        header = PageHeader(
            "Examination Results & Official Report Cards",
            "Consolidated term scores, percentage evaluations, letter grades, and printable report cards"
        )
        btn_promote = theme.create_secondary_button("🎓 Year-End Bulk Promotion")
        btn_promote.setFixedHeight(38)
        btn_promote.clicked.connect(self.open_promotion_center)
        header.add_action(btn_promote)

        btn_save = theme.create_primary_button("💾 Save Examination Marks")
        btn_save.setFixedHeight(38)
        btn_save.clicked.connect(self.save_marks)
        header.add_action(btn_save)
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
        self.class_combo.currentIndexChanged.connect(self.load_results)
        filter_lay.addWidget(self.class_combo)

        term_lbl = QLabel("Examination Term:")
        term_lbl.setFont(theme.font_bold())
        filter_lay.addWidget(term_lbl)

        self.term_combo = QComboBox()
        self.term_combo.addItems(["1st Term Examination", "2nd Term Mid-Years", "Annual Final Exams"])
        self.term_combo.currentIndexChanged.connect(self.load_results)
        filter_lay.addWidget(self.term_combo)

        filter_lay.addStretch()

        btn_refresh = theme.create_secondary_button("Refresh")
        btn_refresh.clicked.connect(self.load_results)
        filter_lay.addWidget(btn_refresh)

        self.marks_saved_badge = StatusBadge("✏️ Edit scores & click Save", "neutral")
        filter_lay.addWidget(self.marks_saved_badge)

        layout.addWidget(filter_card)

        # Table Card
        table_card = ModernCard()
        t_lay = QVBoxLayout(table_card)
        t_lay.setContentsMargins(16, 16, 16, 16)

        self.results_table = QTableWidget(0, 7)
        self.results_table.setHorizontalHeaderLabels([
            "Adm #", "Candidate Full Name", "Exam Score (100)", "Total %", "Grade", "Academic Status", "Report Card"
        ])
        theme.format_table(self.results_table, 46)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)

        r_hdr = self.results_table.horizontalHeader()
        r_hdr.setSectionResizeMode(0, QHeaderView.Interactive)
        r_hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        r_hdr.setSectionResizeMode(2, QHeaderView.Interactive)
        r_hdr.setSectionResizeMode(3, QHeaderView.Interactive)
        r_hdr.setSectionResizeMode(4, QHeaderView.Interactive)
        r_hdr.setSectionResizeMode(5, QHeaderView.Interactive)
        r_hdr.setSectionResizeMode(6, QHeaderView.Interactive)
        self.results_table.setColumnWidth(0, 125)
        self.results_table.setColumnWidth(2, 140)
        self.results_table.setColumnWidth(3, 100)
        self.results_table.setColumnWidth(4, 95)
        self.results_table.setColumnWidth(5, 130)
        self.results_table.setColumnWidth(6, 130)
        t_lay.addWidget(self.results_table)

        layout.addWidget(table_card)

        return widget

    def load_results(self):
        cls = self.class_combo.currentText().replace("Class ", "")
        term = self.term_combo.currentText()
        students = [s for s in db.get_all_students() if s.class_name == cls]

        key = f"exam_results_{cls}_{term}"
        raw = db.get_app_data(key, "")
        saved_marks = {}
        if raw:
            try:
                saved_marks = json.loads(raw)
            except Exception:
                saved_marks = {}

        self.results_table.setRowCount(len(students))
        self.mark_spinboxes = {}

        for row, s in enumerate(students):
            item_adm = QTableWidgetItem(s.admission_no)
            item_adm.setTextAlignment(Qt.AlignCenter)
            self.results_table.setItem(row, 0, item_adm)
            self.results_table.setItem(row, 1, QTableWidgetItem(s.get_full_name()))

            score = float(saved_marks.get(s.admission_no, 75.0))
            spin = QDoubleSpinBox()
            spin.setRange(0, 100)
            spin.setValue(score)
            spin.setFixedHeight(30)
            spin.valueChanged.connect(lambda _, r=row, sp=spin: self.update_row_grade(r, sp.value()))
            self.mark_spinboxes[s.admission_no] = spin
            self.results_table.setCellWidget(row, 2, theme.create_cell_widget(spin))

            self.update_row_grade(row, score)

            btn_card = theme.create_table_button("Report Card", "outline")
            btn_card.clicked.connect(lambda _, st=s, sc=score: self.show_report_card(st))
            self.results_table.setCellWidget(row, 6, theme.create_cell_widget(btn_card))

    def update_row_grade(self, row: int, score: float):
        self.results_table.setItem(row, 3, QTableWidgetItem(f"{score:.1f}%"))

        grade, status, variant = self.get_grade(score)
        g_badge = StatusBadge(grade, variant)
        self.results_table.setCellWidget(row, 4, theme.create_cell_widget(g_badge))

        s_badge = StatusBadge.from_status(status)
        self.results_table.setCellWidget(row, 5, theme.create_cell_widget(s_badge))

    def get_grade(self, score: float):
        if score >= 90:
            return ("A+", "Passed", "success")
        elif score >= 80:
            return ("A", "Passed", "success")
        elif score >= 70:
            return ("B", "Passed", "info")
        elif score >= 60:
            return ("C", "Passed", "warning")
        elif score >= 50:
            return ("D", "Passed", "warning")
        else:
            return ("F", "Failed", "danger")

    def save_marks(self):
        cls = self.class_combo.currentText().replace("Class ", "")
        term = self.term_combo.currentText()
        key = f"exam_results_{cls}_{term}"

        marks_dict = {adm_no: spin.value() for adm_no, spin in self.mark_spinboxes.items()}
        db.save_app_data(key, json.dumps(marks_dict))
        if hasattr(self, "marks_saved_badge"):
            self.marks_saved_badge.setText(f"✓ Class {cls} Marks Saved Successfully!")
            self.marks_saved_badge.setStyleSheet(f"""
                QFrame {{
                    background-color: #ECFDF5;
                    border: 1px solid #A7F3D0;
                    border-radius: 6px;
                    padding: 4px 12px;
                }}
                QLabel {{
                    color: #059669;
                    font-weight: 700;
                    font-size: 11.5px;
                }}
            """)

    def show_report_card(self, s):
        while self.report_card_lay.count():
            item = self.report_card_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cls = self.class_combo.currentText()
        term = self.term_combo.currentText()
        spin = self.mark_spinboxes.get(s.admission_no)
        score = spin.value() if spin else 75.0
        grade, status, _ = self.get_grade(score)

        header = PageHeader(
            f"Official Academic Report Card — {s.get_full_name()}",
            f"Comprehensive student academic evaluation for {term}"
        )
        btn_back = theme.create_outline_button("← Return to Results Matrix")
        btn_back.setFixedHeight(38)
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        header.add_action(btn_back)

        btn_print = theme.create_primary_button("Print Official Transcript")
        btn_print.clicked.connect(lambda: None)
        header.add_action(btn_print)
        self.report_card_lay.addWidget(header)

        card = ModernCard()
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(28, 28, 28, 28)
        card_lay.setSpacing(16)

        school_name = db.get_app_data("systemName", "EXCELLENCE SCHOOL SYSTEM")
        sch_lbl = QLabel(school_name)
        sch_lbl.setFont(theme.font_h1())
        sch_lbl.setAlignment(Qt.AlignCenter)
        sch_lbl.setStyleSheet(f"color: {theme.PRIMARY}; font-weight: 800;")
        card_lay.addWidget(sch_lbl)

        sub_lbl = QLabel(f"OFFICIAL TERM TRANSCRIPT & EVALUATION — {term.upper()}")
        sub_lbl.setFont(theme.font_bold())
        sub_lbl.setAlignment(Qt.AlignCenter)
        sub_lbl.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; letter-spacing: 0.5px;")
        card_lay.addWidget(sub_lbl)

        info = QLabel(
            f"<b>Candidate:</b> {s.get_full_name()}<br>"
            f"<b>Admission No:</b> #{s.admission_no}<br>"
            f"<b>Father's Name:</b> {s.father_name}<br>"
            f"<b>Class Grade:</b> {cls}<br>"
            f"<b>Assessment Term:</b> {term}<br>"
            f"<hr style='border: 0.5px solid #E2E8F0;'>"
            f"<b>Cumulative Marks:</b> {score:.1f} / 100.0<br>"
            f"<b>Term Percentage:</b> {score:.1f}%<br>"
            f"<b>Letter Grade Assigned:</b> <b style='color:#10B981; font-size:14px;'>{grade}</b><br>"
            f"<b>Academic Status:</b> <b>{status}</b><br>"
            f"<hr style='border: 0.5px solid #E2E8F0;'>"
            f"<i>Faculty Remarks: Excellent academic aptitude and active classroom participation.</i><br><br>"
            f"<i>Authorized Signature: _______________________</i>"
        )
        info.setFont(theme.font_regular())
        info.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; line-height: 1.8;")
        card_lay.addWidget(info)
        self.report_card_lay.addWidget(card)
        self.report_card_lay.addStretch()

        self.stack.setCurrentIndex(1)

    # --- 3. YEAR-END BULK PROMOTION CENTER ---
    def create_promotion_view(self) -> QWidget:
        container = QWidget()
        outer_lay = QVBoxLayout(container)
        outer_lay.setContentsMargins(0, 0, 0, 0)
        outer_lay.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(18)

        # Header
        header = PageHeader(
            "Academic Year-End Bulk Promotion Center",
            "Evaluate annual examination marks, advance passing students, graduate Class 10 to Alumni, and retain failing candidates"
        )
        btn_back = theme.create_outline_button("← Return to Marks Entry")
        btn_back.setFixedHeight(38)
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        header.add_action(btn_back)
        layout.addWidget(header)

        # Control Card
        ctrl_card = ModernCard()
        c_lay = QHBoxLayout(ctrl_card)
        c_lay.setContentsMargins(20, 14, 20, 14)
        c_lay.setSpacing(14)

        t_lbl = QLabel("Evaluation Term:")
        t_lbl.setFont(theme.font_bold())
        c_lay.addWidget(t_lbl)

        self.promo_term_combo = QComboBox()
        self.promo_term_combo.addItems(["Annual Final Exams", "2nd Term Mid-Years", "1st Term Examination"])
        self.promo_term_combo.currentIndexChanged.connect(self.load_promotion_candidates)
        c_lay.addWidget(self.promo_term_combo)

        cg_lbl = QLabel("Filter Grade:")
        cg_lbl.setFont(theme.font_bold())
        c_lay.addWidget(cg_lbl)

        self.promo_class_combo = QComboBox()
        self.promo_class_combo.addItem("All Grades (1-10)")
        self.promo_class_combo.addItems([f"Class {i}" for i in range(1, 11)])
        self.promo_class_combo.currentIndexChanged.connect(self.load_promotion_candidates)
        c_lay.addWidget(self.promo_class_combo)

        self.promo_search = ModernSearchBar("Search by student name or admission #...")
        self.promo_search.textChanged.connect(self.load_promotion_candidates)
        c_lay.addWidget(self.promo_search, 1)

        btn_refresh = theme.create_secondary_button("Refresh")
        btn_refresh.clicked.connect(self.load_promotion_candidates)
        c_lay.addWidget(btn_refresh)

        layout.addWidget(ctrl_card)

        # 4 Metric Cards Row
        metric_row = QHBoxLayout()
        metric_row.setSpacing(16)

        self.metric_total = MetricCard("TOTAL EVALUATED", "0", "👥", theme.PRIMARY, "#EFF6FF", "All Active Candidates")
        self.metric_promote = MetricCard("PROMOTE TO NEXT GRADE", "0", "📈", "#059669", "#ECFDF5", "Classes 1–9 (≥50%)")
        self.metric_graduate = MetricCard("GRADUATE TO ALUMNI", "0", "🎓", "#7C3AED", "#F5F3FF", "Class 10 (≥50%)")
        self.metric_retain = MetricCard("RETAIN IN GRADE", "0", "⚠️", "#DC2626", "#FEF2F2", "Academic Review (<50%)")

        metric_row.addWidget(self.metric_total)
        metric_row.addWidget(self.metric_promote)
        metric_row.addWidget(self.metric_graduate)
        metric_row.addWidget(self.metric_retain)
        layout.addLayout(metric_row)

        # Status Notification Banner (initially hidden)
        self.promo_banner = QLabel()
        self.promo_banner.setVisible(False)
        self.promo_banner.setStyleSheet("""
            background-color: #ECFDF5;
            color: #065F46;
            border: 1.5px solid #6EE7B7;
            border-radius: 10px;
            padding: 14px 20px;
            font-size: 13px;
            font-weight: 700;
            line-height: 1.6;
        """)
        layout.addWidget(self.promo_banner)

        # Promotion Matrix Table Card
        table_card = ModernCard()
        t_lay = QVBoxLayout(table_card)
        t_lay.setContentsMargins(16, 16, 16, 16)
        t_lay.setSpacing(12)

        self.promo_table = QTableWidget(0, 7)
        self.promo_table.setHorizontalHeaderLabels([
            "Adm #", "Student Name", "Current Grade", "Annual Score", "Result Status", "Promotion Decision", "Target Status"
        ])
        theme.format_table(self.promo_table, 46)
        self.promo_table.setEditTriggers(QTableWidget.NoEditTriggers)

        p_hdr = self.promo_table.horizontalHeader()
        p_hdr.setSectionResizeMode(0, QHeaderView.Interactive)
        p_hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        p_hdr.setSectionResizeMode(2, QHeaderView.Interactive)
        p_hdr.setSectionResizeMode(3, QHeaderView.Interactive)
        p_hdr.setSectionResizeMode(4, QHeaderView.Interactive)
        p_hdr.setSectionResizeMode(5, QHeaderView.Interactive)
        p_hdr.setSectionResizeMode(6, QHeaderView.Interactive)

        self.promo_table.setColumnWidth(0, 125)
        self.promo_table.setColumnWidth(2, 120)
        self.promo_table.setColumnWidth(3, 115)
        self.promo_table.setColumnWidth(4, 120)
        self.promo_table.setColumnWidth(5, 195)
        self.promo_table.setColumnWidth(6, 125)

        t_lay.addWidget(self.promo_table)
        layout.addWidget(table_card)

        # Authoritative Execution Action Card
        action_card = ModernCard()
        ac_lay = QHBoxLayout(action_card)
        ac_lay.setContentsMargins(24, 18, 24, 18)
        ac_lay.setSpacing(16)

        notice_box = QVBoxLayout()
        notice_box.setSpacing(3)
        lbl_act_title = QLabel("Confirm & Execute Institutional Year-End Progression")
        lbl_act_title.setFont(theme.font_bold())
        lbl_act_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 14px;")
        notice_box.addWidget(lbl_act_title)

        lbl_act_desc = QLabel(
            "This action executes permanent academic progression in the institutional database. "
            "Passing students will advance to their next grade, Class 10 graduates will transfer to Alumni, and all school registers will update."
        )
        lbl_act_desc.setFont(theme.font_small())
        lbl_act_desc.setStyleSheet(f"color: {theme.TEXT_SECONDARY};")
        lbl_act_desc.setWordWrap(True)
        notice_box.addWidget(lbl_act_desc)
        ac_lay.addLayout(notice_box, 1)

        btn_execute = theme.create_primary_button("🚀 Execute Year-End Promotion")
        btn_execute.setFixedHeight(44)
        btn_execute.setMinimumWidth(240)
        btn_execute.clicked.connect(self.execute_bulk_promotion)
        ac_lay.addWidget(btn_execute)

        layout.addWidget(action_card)

        scroll.setWidget(scroll_content)
        outer_lay.addWidget(scroll)
        return container

    def open_promotion_center(self):
        if hasattr(self, "promo_banner"):
            self.promo_banner.setVisible(False)
        self.load_promotion_candidates()
        self.stack.setCurrentIndex(2)

    def load_promotion_candidates(self):
        eval_term = self.promo_term_combo.currentText()
        filter_class = self.promo_class_combo.currentText()
        search_query = self.promo_search.text().strip().lower()

        all_students = [s for s in db.get_all_students() if s.status != "ALUMNI"]

        # Load scores for all classes for the selected term
        class_marks = {}
        for c in range(1, 11):
            key = f"exam_results_{c}_{eval_term}"
            raw = db.get_app_data(key, "")
            if raw:
                try:
                    class_marks[str(c)] = json.loads(raw)
                except Exception:
                    class_marks[str(c)] = {}
            else:
                class_marks[str(c)] = {}

        self.promotion_candidates = []
        tot_count = 0
        promote_count = 0
        graduate_count = 0
        retain_count = 0

        for s in all_students:
            cls_str = str(s.class_name)
            marks_for_cls = class_marks.get(cls_str, {})
            score = float(marks_for_cls.get(s.admission_no, 75.0))
            is_passed = score >= 50.0

            if is_passed:
                if cls_str == "10":
                    decision = "Graduate (ALUMNI)"
                    target_class = "10"
                    target_status = "ALUMNI"
                    graduate_count += 1
                else:
                    next_cls = str(int(cls_str) + 1)
                    decision = f"Promote (Class {next_cls})"
                    target_class = next_cls
                    target_status = "ENROLLED"
                    promote_count += 1
            else:
                decision = f"Retain (Class {cls_str})"
                target_class = cls_str
                target_status = "ENROLLED"
                retain_count += 1

            tot_count += 1

            candidate = {
                "student": s,
                "score": score,
                "is_passed": is_passed,
                "decision": decision,
                "target_class": target_class,
                "target_status": target_status
            }
            self.promotion_candidates.append(candidate)

        # Update metric cards
        self.metric_total.set_value(f"{tot_count:,}")
        self.metric_promote.set_value(f"{promote_count:,}")
        self.metric_graduate.set_value(f"{graduate_count:,}")
        self.metric_retain.set_value(f"{retain_count:,}")

        # Filter for table display
        display_list = []
        for cand in self.promotion_candidates:
            s = cand["student"]
            if filter_class != "All Grades (1-10)" and f"Class {s.class_name}" != filter_class:
                continue
            if search_query:
                q_match = (
                    search_query in s.admission_no.lower() or
                    search_query in s.get_full_name().lower() or
                    search_query in s.father_name.lower()
                )
                if not q_match:
                    continue
            display_list.append(cand)

        self.promo_table.setUpdatesEnabled(False)
        self.promo_table.setRowCount(len(display_list))
        self.decision_combos = {}

        for row, cand in enumerate(display_list):
            s = cand["student"]
            cls_str = str(s.class_name)

            # Col 0: Adm #
            item_adm = QTableWidgetItem(s.admission_no)
            item_adm.setTextAlignment(Qt.AlignCenter)
            self.promo_table.setItem(row, 0, item_adm)

            # Col 1: Student Name
            self.promo_table.setItem(row, 1, QTableWidgetItem(s.get_full_name()))

            # Col 2: Current Grade
            item_cls = QTableWidgetItem(f"Class {cls_str}")
            item_cls.setTextAlignment(Qt.AlignCenter)
            self.promo_table.setItem(row, 2, item_cls)

            # Col 3: Score
            item_sc = QTableWidgetItem(f"{cand['score']:.1f}%")
            item_sc.setTextAlignment(Qt.AlignCenter)
            self.promo_table.setItem(row, 3, item_sc)

            # Col 4: Result Status badge
            status_text = "PASSED" if cand["is_passed"] else "FAILED"
            status_badge = StatusBadge.from_status(status_text)
            self.promo_table.setCellWidget(row, 4, theme.create_cell_widget(status_badge))

            # Col 5: Decision Combobox
            if cls_str == "10":
                options = ["Graduate (ALUMNI)", f"Retain (Class {cls_str})", "Mark Transferred"]
            else:
                next_c = str(int(cls_str) + 1)
                options = [f"Promote (Class {next_c})", f"Retain (Class {cls_str})", "Mark Transferred"]

            combo = theme.create_table_combobox(options, cand["decision"])
            self.decision_combos[s.admission_no] = (combo, s)
            self.promo_table.setCellWidget(row, 5, theme.create_cell_widget(combo))

            # Col 6: Target Status badge
            t_badge = StatusBadge.from_status(cand["target_status"])
            self.promo_table.setCellWidget(row, 6, theme.create_cell_widget(t_badge))
        self.promo_table.setUpdatesEnabled(True)

    def execute_bulk_promotion(self):
        if not hasattr(self, "promotion_candidates") or not self.promotion_candidates:
            return

        updates = []
        promoted_count = 0
        graduated_count = 0
        retained_count = 0

        for cand in self.promotion_candidates:
            s = cand["student"]
            adm_no = s.admission_no
            cls_str = str(s.class_name)

            if adm_no in self.decision_combos:
                combo, _ = self.decision_combos[adm_no]
                dec = combo.currentText()
            else:
                dec = cand["decision"]

            if "Promote" in dec:
                target_cls = str(int(cls_str) + 1)
                target_status = "ENROLLED"
                promoted_count += 1
            elif "Graduate" in dec:
                target_cls = "10"
                target_status = "ALUMNI"
                graduated_count += 1
            elif "Transferred" in dec:
                target_cls = cls_str
                target_status = "TRANSFERRED"
            else:  # Retain
                target_cls = cls_str
                target_status = "ENROLLED"
                retained_count += 1

            updates.append((adm_no, target_cls, target_status))

        # Atomic bulk database update
        updated_total = db.bulk_promote_students(updates)

        # Show in-card success notification banner
        self.promo_banner.setText(
            f"✓ Academic Year-End Promotion Successfully Executed for {updated_total:,} Students!\n"
            f"• {promoted_count:,} Students Promoted to the next academic grade level\n"
            f"• {graduated_count:,} Class 10 Students Graduated and transitioned to ALUMNI status\n"
            f"• {retained_count:,} Students Retained in current grade level for subsequent review"
        )
        self.promo_banner.setVisible(True)

        # Refresh candidate list
        self.load_promotion_candidates()
