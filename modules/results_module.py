"""
Examination & Results Module for School Management System.
Features:
- Subject-wise marks scoring across core subjects (English, Math, Science, Urdu, Computer, Islamiat).
- Real-time aggregate score, percentage, grade, and subject-pass calculation.
- Approach C: Automated Year-End Progression on Annual Final Exams submission.
- Comprehensive subject-by-subject Official Report Card transcripts.
- Institutional Progression Audit Center with historical log review and grade-reversion capability.
"""
import json
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QDoubleSpinBox, QStackedWidget, QScrollArea
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, Signal
import core.theme as theme
import core.database as db
from core.widgets import ModernCard, StatusBadge, MetricCard, PageHeader, ModernSearchBar

SUBJECTS = ["English", "Mathematics", "Science", "Urdu", "Computer", "Islamiat"]


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

        # View 0: Examination Results Table
        self.overview_widget = self.create_overview_view()
        self.stack.addWidget(self.overview_widget)

        # View 1: Official Academic Report Card
        self.report_card_container = QWidget()
        self.report_card_lay = QVBoxLayout(self.report_card_container)
        self.report_card_lay.setContentsMargins(32, 24, 32, 24)
        self.report_card_lay.setSpacing(18)
        self.stack.addWidget(self.report_card_container)

        # View 2: Institutional Progression & Audit Center
        self.promotion_widget = self.create_promotion_view()
        self.stack.addWidget(self.promotion_widget)

        self.load_results()

    # --- 1. OVERVIEW & SUBJECT-WISE MARKS ENTRY ---
    def create_overview_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(18)

        # Header Bar
        header = PageHeader(
            "Examination Results & Official Report Cards",
            "Subject-wise marks entry, automated percentage & grade calculations, and student transcripts"
        )
        btn_promote = theme.create_secondary_button("🎓 Progression & Audit Center")
        btn_promote.setFixedHeight(38)
        btn_promote.clicked.connect(self.open_promotion_center)
        header.add_action(btn_promote)

        btn_save = theme.create_primary_button("💾 Save Examination Marks")
        btn_save.setFixedHeight(38)
        btn_save.clicked.connect(self.save_marks)
        header.add_action(btn_save)
        layout.addWidget(header)

        # Filter & Control Card
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

        self.marks_saved_badge = StatusBadge("✏️ Enter subject scores (out of 100) & Save", "neutral")
        filter_lay.addWidget(self.marks_saved_badge)

        layout.addWidget(filter_card)

        # Subject-Wise Results Table Card
        table_card = ModernCard()
        t_lay = QVBoxLayout(table_card)
        t_lay.setContentsMargins(16, 16, 16, 16)

        # 13 columns: Adm #, Name, 6 Subjects, Total, %, Grade, Status, Report Card
        self.results_table = QTableWidget(0, 13)
        self.results_table.setHorizontalHeaderLabels([
            "Adm #", "Candidate Full Name", "English (100)", "Math (100)", "Science (100)",
            "Urdu (100)", "Computer (100)", "Islamiat (100)", "Total (600)", "Total %", "Grade", "Status", "Report Card"
        ])
        theme.format_table(self.results_table, 46)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)

        r_hdr = self.results_table.horizontalHeader()
        r_hdr.setSectionResizeMode(0, QHeaderView.Interactive)
        r_hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        for c in range(2, 13):
            r_hdr.setSectionResizeMode(c, QHeaderView.Interactive)

        self.results_table.setColumnWidth(0, 125)
        for c in range(2, 8):
            self.results_table.setColumnWidth(c, 85)
        self.results_table.setColumnWidth(8, 90)
        self.results_table.setColumnWidth(9, 80)
        self.results_table.setColumnWidth(10, 75)
        self.results_table.setColumnWidth(11, 95)
        self.results_table.setColumnWidth(12, 115)

        t_lay.addWidget(self.results_table)
        layout.addWidget(table_card)

        return widget

    def load_results(self):
        cls = self.class_combo.currentText().replace("Class ", "")
        term = self.term_combo.currentText()
        students = [s for s in db.get_all_students() if s.class_name == cls and s.status != "ALUMNI"]

        key = f"exam_results_{cls}_{term}"
        raw = db.get_app_data(key, "")
        saved_marks = {}
        if raw:
            try:
                saved_marks = json.loads(raw)
            except Exception:
                saved_marks = {}

        self.results_table.setUpdatesEnabled(False)
        self.results_table.setRowCount(len(students))
        self.mark_spinboxes = {}

        for row, s in enumerate(students):
            item_adm = QTableWidgetItem(s.admission_no)
            item_adm.setTextAlignment(Qt.AlignCenter)
            self.results_table.setItem(row, 0, item_adm)
            self.results_table.setItem(row, 1, QTableWidgetItem(s.get_full_name()))

            # Parse or initialize subject scores
            raw_data = saved_marks.get(s.admission_no)
            student_scores = {}
            if isinstance(raw_data, dict):
                student_scores = raw_data
            elif isinstance(raw_data, (int, float)):
                base = float(raw_data)
                student_scores = {subj: base for subj in SUBJECTS}
            else:
                student_scores = {subj: 75.0 for subj in SUBJECTS}

            self.mark_spinboxes[s.admission_no] = {}

            for col_offset, subj in enumerate(SUBJECTS, start=2):
                sc = float(student_scores.get(subj, 75.0))
                spin = QDoubleSpinBox()
                spin.setRange(0, 100)
                spin.setDecimals(1)
                spin.setValue(sc)
                spin.setFixedHeight(30)
                spin.valueChanged.connect(lambda _, r=row, a=s.admission_no: self.update_row_grade(r, a))
                self.mark_spinboxes[s.admission_no][subj] = spin
                self.results_table.setCellWidget(row, col_offset, theme.create_cell_widget(spin))

            self.update_row_grade(row, s.admission_no)

            btn_card = theme.create_table_button("Report Card", "outline")
            btn_card.clicked.connect(lambda _, st=s: self.show_report_card(st))
            self.results_table.setCellWidget(row, 12, theme.create_cell_widget(btn_card))

        self.results_table.setUpdatesEnabled(True)

    def update_row_grade(self, row: int, adm_no: str):
        sub_spins = self.mark_spinboxes.get(adm_no, {})
        policy = db.get_progression_policy()
        min_passing_pct = float(policy.get("min_passing_pct", 50.0))
        min_subject_pct = float(policy.get("min_subject_pct", 40.0))

        scores = [sp.value() for sp in sub_spins.values()]
        tot = sum(scores) if scores else 0.0
        max_tot = len(sub_spins) * 100.0 if sub_spins else 600.0
        pct = (tot / max_tot * 100.0) if max_tot > 0 else 0.0

        failed_subs = [subj for subj, sp in sub_spins.items() if sp.value() < min_subject_pct]
        is_passed = (pct >= min_passing_pct) and (len(failed_subs) == 0)

        # Col 8: Total Marks
        item_tot = QTableWidgetItem(f"{tot:.0f}/{max_tot:.0f}")
        item_tot.setTextAlignment(Qt.AlignCenter)
        self.results_table.setItem(row, 8, item_tot)

        # Col 9: Percentage
        item_pct = QTableWidgetItem(f"{pct:.1f}%")
        item_pct.setTextAlignment(Qt.AlignCenter)
        self.results_table.setItem(row, 9, item_pct)

        # Col 10: Letter Grade
        grade, variant = self.get_grade(pct)
        g_badge = StatusBadge(grade, variant)
        self.results_table.setCellWidget(row, 10, theme.create_cell_widget(g_badge))

        # Col 11: Status
        status = "Passed" if is_passed else "Failed"
        s_badge = StatusBadge.from_status(status)
        self.results_table.setCellWidget(row, 11, theme.create_cell_widget(s_badge))

    def get_grade(self, score: float):
        if score >= 90:
            return ("A+", "success")
        elif score >= 80:
            return ("A", "success")
        elif score >= 70:
            return ("B", "info")
        elif score >= 60:
            return ("C", "warning")
        elif score >= 50:
            return ("D", "warning")
        else:
            return ("F", "danger")

    def save_marks(self):
        cls = self.class_combo.currentText().replace("Class ", "")
        term = self.term_combo.currentText()
        key = f"exam_results_{cls}_{term}"

        # Build full subject marks dictionary
        marks_dict = {}
        for adm_no, spins in self.mark_spinboxes.items():
            marks_dict[adm_no] = {subj: sp.value() for subj, sp in spins.items()}
        db.save_app_data(key, json.dumps(marks_dict))

        # Read auto-progression policy (Approach C)
        policy = db.get_progression_policy()
        auto_enabled = bool(policy.get("auto_promotion_enabled", True))
        min_passing_pct = float(policy.get("min_passing_pct", 50.0))
        min_subject_pct = float(policy.get("min_subject_pct", 40.0))
        auto_alumni = bool(policy.get("auto_graduate_alumni", True))
        session = str(policy.get("academic_session", "2025-2026"))

        # Automatic progression trigger on Annual Final Exams
        if term == "Annual Final Exams" and auto_enabled:
            students = [s for s in db.get_all_students() if s.class_name == cls and s.status != "ALUMNI"]
            promotions = []
            history_records = []
            promoted_count = 0
            graduated_count = 0
            retained_count = 0

            for s in students:
                sub_scores = marks_dict.get(s.admission_no, {})
                tot = sum(sub_scores.values()) if sub_scores else 0.0
                max_t = len(SUBJECTS) * 100.0
                pct = (tot / max_t * 100.0) if max_t > 0 else 0.0
                failed_subs = [sub for sub, sc in sub_scores.items() if sc < min_subject_pct]
                is_passed = (pct >= min_passing_pct) and (len(failed_subs) == 0)

                if is_passed:
                    if cls == "10":
                        if auto_alumni:
                            target_cls = "10"
                            target_status = "ALUMNI"
                            decision = "Graduated to ALUMNI"
                            graduated_count += 1
                        else:
                            target_cls = "10"
                            target_status = "ENROLLED"
                            decision = "Retained (Senior)"
                            retained_count += 1
                    else:
                        target_cls = str(int(cls) + 1)
                        target_status = "ENROLLED"
                        decision = f"Auto-Promoted to Class {target_cls}"
                        promoted_count += 1
                else:
                    target_cls = cls
                    target_status = "ENROLLED"
                    decision = f"Retained in Class {cls}"
                    retained_count += 1

                promotions.append((s.admission_no, target_cls, target_status))
                history_records.append({
                    "admissionNo": s.admission_no,
                    "studentName": s.get_full_name(),
                    "fromClass": cls,
                    "toClass": target_cls,
                    "totalScore": tot,
                    "maxScore": max_t,
                    "percentage": pct,
                    "resultStatus": "PASSED" if is_passed else "FAILED",
                    "promotionDecision": decision,
                    "academicSession": session,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

            if promotions:
                db.bulk_promote_students(promotions)
                db.log_promotion_history(history_records)

            msg = (
                f"✓ Class {cls} Final Marks Saved! Auto-Progression Executed: "
                f"{promoted_count} Promoted, {graduated_count} Graduated, {retained_count} Retained."
            )
        else:
            msg = f"✓ Class {cls} {term} Subject Marks Saved Successfully!"

        if hasattr(self, "marks_saved_badge"):
            self.marks_saved_badge.setText(msg)
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

    # --- 2. OFFICIAL ACADEMIC REPORT CARD TRANSCRIPT ---
    def show_report_card(self, s):
        while self.report_card_lay.count():
            item = self.report_card_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cls = self.class_combo.currentText()
        cls_num = cls.replace("Class ", "")
        term = self.term_combo.currentText()

        policy = db.get_progression_policy()
        min_passing_pct = float(policy.get("min_passing_pct", 50.0))
        min_subject_pct = float(policy.get("min_subject_pct", 40.0))
        session = policy.get("academic_session", "2025-2026")

        # Get subject marks
        sub_spins = self.mark_spinboxes.get(s.admission_no, {})
        subject_data = {}
        if sub_spins:
            subject_data = {subj: sp.value() for subj, sp in sub_spins.items()}
        else:
            key = f"exam_results_{cls_num}_{term}"
            raw = db.get_app_data(key, "")
            if raw:
                try:
                    saved = json.loads(raw)
                    val = saved.get(s.admission_no, {})
                    if isinstance(val, dict):
                        subject_data = val
                    elif isinstance(val, (int, float)):
                        subject_data = {subj: float(val) for subj in SUBJECTS}
                except Exception:
                    pass
            if not subject_data:
                subject_data = {subj: 75.0 for subj in SUBJECTS}

        total_obtained = sum(subject_data.values())
        max_total = len(SUBJECTS) * 100.0
        pct = (total_obtained / max_total * 100.0) if max_total > 0 else 0.0
        failed_subs = [subj for subj, sc in subject_data.items() if sc < min_subject_pct]
        is_passed = (pct >= min_passing_pct) and (len(failed_subs) == 0)
        grade, _ = self.get_grade(pct)

        header = PageHeader(
            f"Official Academic Report Card — {s.get_full_name()}",
            f"Comprehensive subject-by-subject evaluation for {term} (Session {session})"
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

        sub_lbl = QLabel(f"OFFICIAL TRANSCRIPT & SUBJECT EVALUATION — {term.upper()}")
        sub_lbl.setFont(theme.font_bold())
        sub_lbl.setAlignment(Qt.AlignCenter)
        sub_lbl.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; letter-spacing: 0.5px;")
        card_lay.addWidget(sub_lbl)

        # Candidate Meta Box
        meta_box = QHBoxLayout()
        lbl_left = QLabel(
            f"<b>Candidate:</b> {s.get_full_name()}<br>"
            f"<b>Admission No:</b> #{s.admission_no}<br>"
            f"<b>Father's Name:</b> {s.father_name}"
        )
        lbl_left.setFont(theme.font_regular())
        lbl_left.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; line-height: 1.7;")
        meta_box.addWidget(lbl_left)

        meta_box.addStretch()

        lbl_right = QLabel(
            f"<b>Class Grade:</b> {cls}<br>"
            f"<b>Evaluation Term:</b> {term}<br>"
            f"<b>Academic Session:</b> {session}"
        )
        lbl_right.setFont(theme.font_regular())
        lbl_right.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; line-height: 1.7;")
        meta_box.addWidget(lbl_right)
        card_lay.addLayout(meta_box)

        # Subject Breakdown Table
        table = QTableWidget(len(SUBJECTS), 6)
        table.setHorizontalHeaderLabels(["Subject Name", "Maximum Marks", "Obtained Marks", "Percentage", "Grade", "Status"])
        theme.format_table(table, 38)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        t_hdr = table.horizontalHeader()
        t_hdr.setSectionResizeMode(0, QHeaderView.Stretch)
        for c in range(1, 6):
            t_hdr.setSectionResizeMode(c, QHeaderView.Interactive)
        table.setColumnWidth(1, 110)
        table.setColumnWidth(2, 120)
        table.setColumnWidth(3, 100)
        table.setColumnWidth(4, 90)
        table.setColumnWidth(5, 110)

        for r_idx, subj in enumerate(SUBJECTS):
            sc = float(subject_data.get(subj, 75.0))
            table.setItem(r_idx, 0, QTableWidgetItem(f"📚 {subj}"))

            it_max = QTableWidgetItem("100")
            it_max.setTextAlignment(Qt.AlignCenter)
            table.setItem(r_idx, 1, it_max)

            it_sc = QTableWidgetItem(f"{sc:.1f}")
            it_sc.setTextAlignment(Qt.AlignCenter)
            table.setItem(r_idx, 2, it_sc)

            it_pct = QTableWidgetItem(f"{sc:.1f}%")
            it_pct.setTextAlignment(Qt.AlignCenter)
            table.setItem(r_idx, 3, it_pct)

            sub_grade, sub_var = self.get_grade(sc)
            sub_g_badge = StatusBadge(sub_grade, sub_var)
            table.setCellWidget(r_idx, 4, theme.create_cell_widget(sub_g_badge))

            sub_passed = sc >= min_subject_pct
            sub_s_badge = StatusBadge.from_status("Passed" if sub_passed else "Failed")
            table.setCellWidget(r_idx, 5, theme.create_cell_widget(sub_s_badge))

        card_lay.addWidget(table)

        # Summary Frame
        summary_box = QFrame()
        bg_col = "#ECFDF5" if is_passed else "#FEF2F2"
        bd_col = "#A7F3D0" if is_passed else "#FECACA"
        summary_box.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_col};
                border: 1.5px solid {bd_col};
                border-radius: 8px;
                padding: 10px 16px;
            }}
        """)
        s_lay = QHBoxLayout(summary_box)
        s_lay.setContentsMargins(12, 8, 12, 8)

        lbl_sum_left = QLabel(
            f"<b>Cumulative Marks:</b> {total_obtained:.0f} / {max_total:.0f} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Aggregate Score:</b> {pct:.1f}% &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Final Grade:</b> <b style='color:{theme.PRIMARY}; font-size:14px;'>{grade}</b>"
        )
        lbl_sum_left.setFont(theme.font_regular())
        s_lay.addWidget(lbl_sum_left)
        s_lay.addStretch()

        badge_status = StatusBadge.from_status("Passed" if is_passed else "Failed")
        s_lay.addWidget(badge_status)
        card_lay.addWidget(summary_box)

        # Signatures
        foot = QLabel(
            "<i>Remarks: Demonstrates consistent academic aptitude, diligence, and commendable class engagement.</i><br><br>"
            "<b>Class Teacher Signature:</b> ____________________ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "
            "<b>Principal Authorization:</b> ____________________"
        )
        foot.setFont(theme.font_regular())
        foot.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; line-height: 1.8;")
        card_lay.addWidget(foot)

        self.report_card_lay.addWidget(card)
        self.report_card_lay.addStretch()
        self.stack.setCurrentIndex(1)

    # --- 3. INSTITUTIONAL PROGRESSION & AUDIT CENTER ---
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
            "Academic Progression & Audit Center",
            "Autonomous student grade progression, session evaluation, and historical promotion audit logs"
        )
        btn_back = theme.create_outline_button("← Return to Marks Entry")
        btn_back.setFixedHeight(38)
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        header.add_action(btn_back)
        layout.addWidget(header)

        # Control Card with Tab Switcher
        ctrl_card = ModernCard()
        c_lay = QHBoxLayout(ctrl_card)
        c_lay.setContentsMargins(20, 14, 20, 14)
        c_lay.setSpacing(14)

        self.btn_view_live = theme.create_primary_button("📊 Live Candidate Progression")
        self.btn_view_live.setFixedHeight(36)
        self.btn_view_live.clicked.connect(lambda: self.switch_promo_sub_view(0))
        c_lay.addWidget(self.btn_view_live)

        self.btn_view_history = theme.create_outline_button("📜 Progression Audit Trail")
        self.btn_view_history.setFixedHeight(36)
        self.btn_view_history.clicked.connect(lambda: self.switch_promo_sub_view(1))
        c_lay.addWidget(self.btn_view_history)

        c_lay.addSpacing(16)

        t_lbl = QLabel("Term:")
        t_lbl.setFont(theme.font_bold())
        c_lay.addWidget(t_lbl)

        self.promo_term_combo = QComboBox()
        self.promo_term_combo.addItems(["Annual Final Exams", "2nd Term Mid-Years", "1st Term Examination"])
        self.promo_term_combo.currentIndexChanged.connect(self.load_promotion_candidates)
        c_lay.addWidget(self.promo_term_combo)

        cg_lbl = QLabel("Grade:")
        cg_lbl.setFont(theme.font_bold())
        c_lay.addWidget(cg_lbl)

        self.promo_class_combo = QComboBox()
        self.promo_class_combo.addItem("All Grades (1-10)")
        self.promo_class_combo.addItems([f"Class {i}" for i in range(1, 11)])
        self.promo_class_combo.currentIndexChanged.connect(self.load_promotion_candidates)
        c_lay.addWidget(self.promo_class_combo)

        self.promo_search = ModernSearchBar("Search student name or admission #...")
        self.promo_search.textChanged.connect(self.load_promotion_candidates)
        c_lay.addWidget(self.promo_search, 1)

        btn_refresh = theme.create_secondary_button("Refresh")
        btn_refresh.clicked.connect(self.refresh_promo_view)
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

        # Center Sub-Stack for Tables
        self.promo_stack = QStackedWidget()

        # Tab 0: Live Candidate Table Card
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
        for c in range(2, 7):
            p_hdr.setSectionResizeMode(c, QHeaderView.Interactive)

        self.promo_table.setColumnWidth(0, 125)
        self.promo_table.setColumnWidth(2, 120)
        self.promo_table.setColumnWidth(3, 115)
        self.promo_table.setColumnWidth(4, 120)
        self.promo_table.setColumnWidth(5, 195)
        self.promo_table.setColumnWidth(6, 125)

        t_lay.addWidget(self.promo_table)
        self.promo_stack.addWidget(table_card)

        # Tab 1: Historical Audit Trail Card
        hist_card = ModernCard()
        h_lay = QVBoxLayout(hist_card)
        h_lay.setContentsMargins(16, 16, 16, 16)
        h_lay.setSpacing(12)

        self.history_table = QTableWidget(0, 8)
        self.history_table.setHorizontalHeaderLabels([
            "Timestamp", "Adm #", "Student Name", "From Grade", "To Grade", "Score %", "Decision", "Action"
        ])
        theme.format_table(self.history_table, 46)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)

        h_hdr = self.history_table.horizontalHeader()
        h_hdr.setSectionResizeMode(0, QHeaderView.Interactive)
        h_hdr.setSectionResizeMode(1, QHeaderView.Interactive)
        h_hdr.setSectionResizeMode(2, QHeaderView.Stretch)
        for c in range(3, 8):
            h_hdr.setSectionResizeMode(c, QHeaderView.Interactive)

        self.history_table.setColumnWidth(0, 150)
        self.history_table.setColumnWidth(1, 125)
        self.history_table.setColumnWidth(3, 100)
        self.history_table.setColumnWidth(4, 100)
        self.history_table.setColumnWidth(5, 95)
        self.history_table.setColumnWidth(6, 160)
        self.history_table.setColumnWidth(7, 100)

        h_lay.addWidget(self.history_table)
        self.promo_stack.addWidget(hist_card)

        layout.addWidget(self.promo_stack)

        # Action Card (Manual Check / Force Sync)
        action_card = ModernCard()
        ac_lay = QHBoxLayout(action_card)
        ac_lay.setContentsMargins(24, 18, 24, 18)
        ac_lay.setSpacing(16)

        notice_box = QVBoxLayout()
        notice_box.setSpacing(3)
        lbl_act_title = QLabel("Autonomous Institutional Year-End Progression (Approach C)")
        lbl_act_title.setFont(theme.font_bold())
        lbl_act_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 14px;")
        notice_box.addWidget(lbl_act_title)

        lbl_act_desc = QLabel(
            "Automatic progression executes immediately whenever teachers save Annual Final Exam marks. "
            "Use the button to verify or force-synchronize student progression across all active classes."
        )
        lbl_act_desc.setFont(theme.font_small())
        lbl_act_desc.setStyleSheet(f"color: {theme.TEXT_SECONDARY};")
        lbl_act_desc.setWordWrap(True)
        notice_box.addWidget(lbl_act_desc)
        ac_lay.addLayout(notice_box, 1)

        btn_execute = theme.create_primary_button("⚡ Run / Verify Progression Check")
        btn_execute.setFixedHeight(44)
        btn_execute.setMinimumWidth(240)
        btn_execute.clicked.connect(self.execute_bulk_promotion)
        ac_lay.addWidget(btn_execute)

        layout.addWidget(action_card)

        scroll.setWidget(scroll_content)
        outer_lay.addWidget(scroll)
        return container

    def switch_promo_sub_view(self, index: int):
        self.promo_stack.setCurrentIndex(index)
        btn_active_qss = f"""
            QPushButton {{
                background-color: {theme.PRIMARY};
                color: #FFFFFF;
                border-radius: 8px;
                padding: 6px 16px;
                font-weight: 600;
                border: none;
            }}
        """
        btn_inactive_qss = f"""
            QPushButton {{
                background-color: {theme.SURFACE};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_COLOR};
                border-radius: 8px;
                padding: 6px 16px;
                font-weight: 600;
            }}
        """
        if index == 0:
            self.btn_view_live.setStyleSheet(btn_active_qss)
            self.btn_view_history.setStyleSheet(btn_inactive_qss)
            self.load_promotion_candidates()
        else:
            self.btn_view_live.setStyleSheet(btn_inactive_qss)
            self.btn_view_history.setStyleSheet(btn_active_qss)
            self.load_audit_history()

    def refresh_promo_view(self):
        if self.promo_stack.currentIndex() == 0:
            self.load_promotion_candidates()
        else:
            self.load_audit_history()

    def open_promotion_center(self):
        if hasattr(self, "promo_banner"):
            self.promo_banner.setVisible(False)
        self.switch_promo_sub_view(0)
        self.stack.setCurrentIndex(2)

    def load_promotion_candidates(self):
        eval_term = self.promo_term_combo.currentText()
        filter_class = self.promo_class_combo.currentText()
        search_query = self.promo_search.text().strip().lower()

        policy = db.get_progression_policy()
        min_passing_pct = float(policy.get("min_passing_pct", 50.0))
        min_subject_pct = float(policy.get("min_subject_pct", 40.0))

        all_students = [s for s in db.get_all_students() if s.status != "ALUMNI"]

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
            raw_s = marks_for_cls.get(s.admission_no, {})

            if isinstance(raw_s, dict) and raw_s:
                scores = list(raw_s.values())
                score = (sum(scores) / (len(scores) * 100.0) * 100.0) if scores else 0.0
                failed_subs = [sb for sb, val in raw_s.items() if val < min_subject_pct]
                is_passed = (score >= min_passing_pct) and (len(failed_subs) == 0)
            elif isinstance(raw_s, (int, float)):
                score = float(raw_s)
                is_passed = score >= min_passing_pct
            else:
                score = 75.0
                is_passed = True

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

    def load_audit_history(self):
        records = db.get_promotion_history(limit=200)
        self.history_table.setUpdatesEnabled(False)
        self.history_table.setRowCount(len(records))

        for row, rec in enumerate(records):
            # Col 0: Timestamp
            it_ts = QTableWidgetItem(rec.get("timestamp", ""))
            it_ts.setTextAlignment(Qt.AlignCenter)
            self.history_table.setItem(row, 0, it_ts)

            # Col 1: Adm #
            it_adm = QTableWidgetItem(rec.get("admissionNo", ""))
            it_adm.setTextAlignment(Qt.AlignCenter)
            self.history_table.setItem(row, 1, it_adm)

            # Col 2: Student Name
            self.history_table.setItem(row, 2, QTableWidgetItem(rec.get("studentName", "")))

            # Col 3: From Grade
            it_from = QTableWidgetItem(f"Class {rec.get('fromClass', '')}")
            it_from.setTextAlignment(Qt.AlignCenter)
            self.history_table.setItem(row, 3, it_from)

            # Col 4: To Grade
            it_to = QTableWidgetItem(f"Class {rec.get('toClass', '')}")
            it_to.setTextAlignment(Qt.AlignCenter)
            self.history_table.setItem(row, 4, it_to)

            # Col 5: Percentage
            it_pct = QTableWidgetItem(f"{rec.get('percentage', 0.0):.1f}%")
            it_pct.setTextAlignment(Qt.AlignCenter)
            self.history_table.setItem(row, 5, it_pct)

            # Col 6: Decision Badge
            b_dec = StatusBadge(rec.get("promotionDecision", "Promoted"), "info")
            self.history_table.setCellWidget(row, 6, theme.create_cell_widget(b_dec))

            # Col 7: Revert Action Button
            btn_revert = theme.create_table_button("↺ Revert", "danger")
            btn_revert.clicked.connect(lambda _, r=rec: self.revert_promotion_record(r))
            self.history_table.setCellWidget(row, 7, theme.create_cell_widget(btn_revert))

        self.history_table.setUpdatesEnabled(True)

    def revert_promotion_record(self, record: dict):
        adm_no = record.get("admissionNo")
        orig_class = record.get("fromClass")
        orig_status = "ENROLLED"
        if adm_no and orig_class:
            success = db.revert_student_promotion(adm_no, orig_class, orig_status)
            if success:
                self.promo_banner.setText(
                    f"✓ Reverted Student #{adm_no} back to Class {orig_class} ({orig_status})."
                )
                self.promo_banner.setVisible(True)
                self.load_audit_history()

    def execute_bulk_promotion(self):
        if not hasattr(self, "promotion_candidates") or not self.promotion_candidates:
            self.load_promotion_candidates()

        policy = db.get_progression_policy()
        session = policy.get("academic_session", "2025-2026")

        updates = []
        history_records = []
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
            history_records.append({
                "admissionNo": adm_no,
                "studentName": s.get_full_name(),
                "fromClass": cls_str,
                "toClass": target_cls,
                "totalScore": cand.get("score", 75.0) * 6.0,
                "maxScore": 600.0,
                "percentage": cand.get("score", 75.0),
                "resultStatus": "PASSED" if cand.get("is_passed", True) else "FAILED",
                "promotionDecision": dec,
                "academicSession": session,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        # Atomic bulk database update & audit logging
        updated_total = db.bulk_promote_students(updates)
        db.log_promotion_history(history_records)

        # Show in-card success notification banner
        self.promo_banner.setText(
            f"✓ Academic Year-End Progression Verified & Synchronized for {updated_total:,} Students!\n"
            f"• {promoted_count:,} Students Promoted to next academic grade\n"
            f"• {graduated_count:,} Class 10 Students Graduated and transitioned to ALUMNI status\n"
            f"• {retained_count:,} Students Retained in current grade level for subsequent review"
        )
        self.promo_banner.setVisible(True)

        # Refresh candidate list
        self.load_promotion_candidates()
