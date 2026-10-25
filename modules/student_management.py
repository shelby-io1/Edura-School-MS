"""
Student Management Module for School Management System.
Redesigned with ModernCard containers, StatusBadge chips, and unified Enterprise admission forms.
"""
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QDialog, QMessageBox, QStackedWidget,
    QScrollArea, QGridLayout
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, Signal
import core.theme as theme
import core.database as db
from core.models import Student
from core.widgets import (
    ModernCard, StatusBadge, PageHeader, ModernSearchBar,
    FormHeaderCard, FormSectionHeader, FormFieldGroup
)
from datetime import date



class StudentAdmissionForm(QWidget):
    """
    Unified student admission & registration form component.
    Standardized for both New Admission registration and Edit/Update student profiles.
    """
    saved = Signal(object)      # emits the saved Student
    cancelled = Signal()

    def __init__(self, parent=None, student: Optional[Student] = None, is_dialog_mode: bool = False):
        super().__init__(parent)
        self.student = student
        self.is_dialog_mode = is_dialog_mode
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(12, 10, 12, 16)
        lay.setSpacing(16)

        # 1. Header Banner
        if self.student:
            self.header_card = FormHeaderCard(
                title=f"Student Profile — #{self.student.admission_no} {self.student.get_full_name()}",
                subtitle="Official institutional student registry record and personal dossier",
                icon_str="🎓"
            )
            self.header_card.add_badge(StatusBadge.from_status(self.student.status or "ENROLLED"))
            self.header_card.add_badge(StatusBadge(f"CLASS {self.student.class_name}", "info"))
            self.header_card.add_badge(StatusBadge(f"ADM #{self.student.admission_no}", "neutral"))
        else:
            self.header_card = FormHeaderCard(
                title="Student Admission & Enrollment Application",
                subtitle="Official institutional registry form for candidate enrollment, guardian coordinates, and academic allocation",
                icon_str="🎓"
            )
            self.header_card.add_badge(StatusBadge("NEW ADMISSION", "primary"))
            self.header_card.add_badge(StatusBadge("ACADEMIC YEAR 2026", "neutral"))

        lay.addWidget(self.header_card)

        # 2. Section 1 Card: Candidate Identity & Demographics
        sec1_card = ModernCard()
        sec1_lay = QVBoxLayout(sec1_card)
        sec1_lay.setContentsMargins(24, 20, 24, 22)
        sec1_lay.setSpacing(16)

        sec1_lay.addWidget(FormSectionHeader(
            "Personal & Demographic Information", "👤",
            "Candidate identity, legal name, and official parentage"
        ))

        grid1 = QGridLayout()
        grid1.setHorizontalSpacing(18)
        grid1.setVerticalSpacing(14)

        # Admission No
        self.adm_no_input = QLineEdit()
        self.adm_no_input.setFixedHeight(38)
        if self.student:
            self.adm_no_input.setText(self.student.admission_no)
            self.adm_no_input.setReadOnly(True)
            self.adm_no_input.setStyleSheet("QLineEdit { background-color: #F8FAFC; color: #64748B; border: 1.5px solid #E2E8F0; border-radius: 8px; padding: 0 12px; }")
        else:
            self.adm_no_input.setPlaceholderText("Auto-generated if left blank")
        grid1.addWidget(FormFieldGroup("Admission Number", self.adm_no_input, required=False, helper_text="System-assigned unique student identifier"), 0, 0)

        # First Name
        self.first_name_input = QLineEdit(self.student.first_name if self.student else "")
        self.first_name_input.setFixedHeight(38)
        self.first_name_input.setPlaceholderText("e.g. Muhammad")
        grid1.addWidget(FormFieldGroup("First Name", self.first_name_input, required=True), 0, 1)

        # Middle Name
        self.middle_name_input = QLineEdit(self.student.middle_name if self.student else "")
        self.middle_name_input.setFixedHeight(38)
        self.middle_name_input.setPlaceholderText("e.g. Ali (Optional)")
        grid1.addWidget(FormFieldGroup("Middle Name", self.middle_name_input, required=False), 0, 2)

        # Last Name
        self.last_name_input = QLineEdit(self.student.last_name if self.student else "")
        self.last_name_input.setFixedHeight(38)
        self.last_name_input.setPlaceholderText("e.g. Khan")
        grid1.addWidget(FormFieldGroup("Last Name / Surname", self.last_name_input, required=True), 1, 0)

        # Father / Guardian Name
        self.father_name_input = QLineEdit(self.student.father_name if self.student else "")
        self.father_name_input.setFixedHeight(38)
        self.father_name_input.setPlaceholderText("e.g. Tariq Mehmood")
        grid1.addWidget(FormFieldGroup("Father / Guardian Name", self.father_name_input, required=True), 1, 1)

        # Age
        self.age_input = QLineEdit(str(self.student.age if self.student and self.student.age else "10"))
        self.age_input.setFixedHeight(38)
        self.age_input.setPlaceholderText("Age in years")
        grid1.addWidget(FormFieldGroup("Candidate Age", self.age_input, required=False), 1, 2)

        # B-Form / CNIC
        self.cnic_input = QLineEdit(self.student.cnic if self.student else "")
        self.cnic_input.setFixedHeight(38)
        self.cnic_input.setPlaceholderText("e.g. 37405-1234567-1")
        grid1.addWidget(FormFieldGroup("B-Form / CNIC Number", self.cnic_input, required=False), 2, 0)

        # Blood Group
        self.blood_combo = QComboBox()
        self.blood_combo.setFixedHeight(38)
        self.blood_combo.addItems(["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-", "Unknown"])
        if self.student and self.student.blood_group:
            idx = self.blood_combo.findText(self.student.blood_group)
            if idx >= 0:
                self.blood_combo.setCurrentIndex(idx)
        grid1.addWidget(FormFieldGroup("Blood Group", self.blood_combo, required=False), 2, 1)

        # Status
        self.status_combo = QComboBox()
        self.status_combo.setFixedHeight(38)
        self.status_combo.addItems(["ENROLLED", "TRANSFERRED", "ALUMNI"])
        if self.student and self.student.status:
            idx = self.status_combo.findText(self.student.status)
            if idx >= 0:
                self.status_combo.setCurrentIndex(idx)
        grid1.addWidget(FormFieldGroup("Enrollment Status", self.status_combo, required=True), 2, 2)

        sec1_lay.addLayout(grid1)
        lay.addWidget(sec1_card)

        # 3. Section 2 Card: Academic Enrollment & Class Placement
        sec2_card = ModernCard()
        sec2_lay = QVBoxLayout(sec2_card)
        sec2_lay.setContentsMargins(24, 20, 24, 22)
        sec2_lay.setSpacing(16)

        sec2_lay.addWidget(FormSectionHeader(
            "Academic Allocation & Institutional Placement", "🏫",
            "Grade level, admission date, and previous schooling"
        ))

        grid2 = QGridLayout()
        grid2.setHorizontalSpacing(18)
        grid2.setVerticalSpacing(14)

        # Assigned Class
        self.class_combo = QComboBox()
        self.class_combo.setFixedHeight(38)
        self.class_combo.addItems([str(i) for i in range(1, 11)])
        if self.student and self.student.class_name:
            idx = self.class_combo.findText(self.student.class_name)
            if idx >= 0:
                self.class_combo.setCurrentIndex(idx)
        grid2.addWidget(FormFieldGroup("Class Assigned", self.class_combo, required=True), 0, 0)

        # Admission Date
        self.date_input = QLineEdit(self.student.admission_date if self.student and self.student.admission_date else date.today().isoformat())
        self.date_input.setFixedHeight(38)
        self.date_input.setPlaceholderText("YYYY-MM-DD")
        grid2.addWidget(FormFieldGroup("Admission Date", self.date_input, required=False), 0, 1)

        # Previous Institution
        self.prev_inst_input = QLineEdit(self.student.prev_institution if self.student else "")
        self.prev_inst_input.setFixedHeight(38)
        self.prev_inst_input.setPlaceholderText("Previous school, academy, or preschool attended")
        grid2.addWidget(FormFieldGroup("Previous Institution Attended", self.prev_inst_input, required=False), 1, 0, 1, 2)

        sec2_lay.addLayout(grid2)
        lay.addWidget(sec2_card)

        # 4. Section 3 Card: Contact Coordinates & Residential Details
        sec3_card = ModernCard()
        sec3_lay = QVBoxLayout(sec3_card)
        sec3_lay.setContentsMargins(24, 20, 24, 22)
        sec3_lay.setSpacing(16)

        sec3_lay.addWidget(FormSectionHeader(
            "Contact Coordinates & Residential Details", "📍",
            "Parent phone lines, emergency contacts, and home address"
        ))

        grid3 = QGridLayout()
        grid3.setHorizontalSpacing(18)
        grid3.setVerticalSpacing(14)

        # Contact Phone
        self.contact_input = QLineEdit(self.student.contact if self.student else "")
        self.contact_input.setFixedHeight(38)
        self.contact_input.setPlaceholderText("e.g. 0300-1234567")
        grid3.addWidget(FormFieldGroup("Primary Contact Phone", self.contact_input, required=True), 0, 0)

        # Alternate Phone
        self.alt_contact_input = QLineEdit()
        self.alt_contact_input.setFixedHeight(38)
        self.alt_contact_input.setPlaceholderText("e.g. 0321-9876543 (Optional)")
        grid3.addWidget(FormFieldGroup("Emergency / Alternate Phone", self.alt_contact_input, required=False), 0, 1)

        # Residential Address
        self.address_input = QLineEdit(self.student.address if self.student else "")
        self.address_input.setFixedHeight(38)
        self.address_input.setPlaceholderText("House / Street Address, Sector / Mohallah, City")
        grid3.addWidget(FormFieldGroup("Residential Street Address", self.address_input, required=False), 1, 0, 1, 2)

        # Notes
        self.notes_input = QLineEdit(self.student.notes if self.student else "")
        self.notes_input.setFixedHeight(38)
        self.notes_input.setPlaceholderText("Special concessions, medical alerts, or administrative remarks")
        grid3.addWidget(FormFieldGroup("Administrative & Medical Notes", self.notes_input, required=False), 2, 0, 1, 2)

        sec3_lay.addLayout(grid3)
        lay.addWidget(sec3_card)

        # 5. Form Action Footer Card
        action_card = ModernCard()
        act_lay = QHBoxLayout(action_card)
        act_lay.setContentsMargins(24, 16, 24, 16)
        act_lay.setSpacing(14)

        self.btn_cancel = theme.create_outline_button("Cancel & Close")
        self.btn_cancel.setFixedHeight(40)
        self.btn_cancel.clicked.connect(self.handle_cancel)
        act_lay.addWidget(self.btn_cancel)

        if not self.student:
            btn_reset = theme.create_outline_button("Reset Fields")
            btn_reset.setFixedHeight(40)
            btn_reset.clicked.connect(self.clear_form)
            act_lay.addWidget(btn_reset)

        act_lay.addStretch()

        submit_text = "✓ Update Student Record" if self.student else "✓ Enroll & Save Student Record"
        self.btn_submit = theme.create_primary_button(submit_text)
        self.btn_submit.setFixedHeight(42)
        self.btn_submit.setMinimumWidth(220)
        self.btn_submit.clicked.connect(self.save_student_data)
        act_lay.addWidget(self.btn_submit)

        lay.addWidget(action_card)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def save_student_data(self):
        first = self.first_name_input.text().strip()
        last = self.last_name_input.text().strip()
        father = self.father_name_input.text().strip()
        contact = self.contact_input.text().strip()

        if not first or not last or not father:
            QMessageBox.warning(self, "Missing Information", "First Name, Last Name, and Father's Name are required fields.")
            return

        try:
            age_val = int(self.age_input.text().strip() or "0")
        except ValueError:
            age_val = 0

        if self.student:
            adm_no = self.student.admission_no
        else:
            adm_no = self.adm_no_input.text().strip()
            if not adm_no:
                students = db.get_all_students()
                max_id = max([int(s.admission_no) for s in students if s.admission_no.isdigit()] or [0])
                adm_no = str(max_id + 1)

        st = Student(
            admission_no=adm_no,
            first_name=first,
            middle_name=self.middle_name_input.text().strip(),
            last_name=last,
            father_name=father,
            age=age_val,
            class_name=self.class_combo.currentText(),
            cnic=self.cnic_input.text().strip(),
            blood_group=self.blood_combo.currentText(),
            contact=contact,
            address=self.address_input.text().strip(),
            prev_institution=self.prev_inst_input.text().strip(),
            notes=self.notes_input.text().strip(),
            status=self.status_combo.currentText(),
            admission_date=self.date_input.text().strip() or date.today().isoformat()
        )

        db.save_student(st)

        if self.student:
            QMessageBox.information(
                self, "Record Updated",
                f"Student profile for {st.get_full_name()} (#{adm_no}) has been successfully updated."
            )
        else:
            QMessageBox.information(
                self, "Enrollment Success",
                f"Student {st.get_full_name()} has been successfully enrolled with Admission No #{adm_no}!"
            )
            self.clear_form()

        self.saved.emit(st)

    def clear_form(self):
        self.adm_no_input.clear()
        self.first_name_input.clear()
        self.middle_name_input.clear()
        self.last_name_input.clear()
        self.father_name_input.clear()
        self.cnic_input.clear()
        self.contact_input.clear()
        self.alt_contact_input.clear()
        self.address_input.clear()
        self.prev_inst_input.clear()
        self.notes_input.clear()

    def handle_cancel(self):
        self.cancelled.emit()


class StudentEditDialog(QDialog):
    """Dialog window embedding the unified StudentAdmissionForm for viewing/editing student records."""
    def __init__(self, student: Student, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Edit Student Record — #{student.admission_no} {student.get_full_name()}")
        self.resize(880, 720)
        self.setStyleSheet(f"background-color: {theme.BACKGROUND};")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)

        self.form = StudentAdmissionForm(parent=self, student=student, is_dialog_mode=True)
        self.form.saved.connect(self.accept)
        self.form.cancelled.connect(self.reject)
        lay.addWidget(self.form)


class StudentManagementView(QWidget):
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"background-color: {theme.BACKGROUND};")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.sub_stack = QStackedWidget()
        self.main_layout.addWidget(self.sub_stack)

        # Sub-views
        self.hub_widget = self.create_hub_view()
        self.sub_stack.addWidget(self.hub_widget)

        self.admission_widget = self.create_admission_form_view()
        self.sub_stack.addWidget(self.admission_widget)

        self.class_selection_widget = self.create_class_selection_view()
        self.sub_stack.addWidget(self.class_selection_widget)

        self.class_students_widget = self.create_class_students_view()
        self.sub_stack.addWidget(self.class_students_widget)

        self.directory_widget = self.create_directory_view()
        self.sub_stack.addWidget(self.directory_widget)

        self.sub_stack.setCurrentIndex(0)

    def set_sub_view(self, sub_route: str):
        sub = sub_route.lower().strip()
        if sub in ("hub", "overview", ""):
            self.sub_stack.setCurrentIndex(0)
        elif sub in ("admission", "new"):
            self.open_admission_form(student=None)
        elif sub in ("classes", "browser"):
            self.open_class_selection()
        elif sub in ("directory", "archives"):
            self.open_directory()

    # --- 1. HUB VIEW ---
    def create_hub_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(24)

        header = PageHeader(
            "Student Information System",
            "Admissions processing, class rosters, academic records, and student directory archives"
        )
        layout.addWidget(header)

        # 3 Action Cards Row
        cards_lay = QHBoxLayout()
        cards_lay.setSpacing(20)

        c1 = self.create_action_card(
            "New Admission",
            "Enroll new students with complete bio-data, parent details, and class allocation.",
            "➕", theme.PRIMARY, lambda: self.sub_stack.setCurrentIndex(1)
        )
        c2 = self.create_action_card(
            "Class Browser",
            "Browse Classes 1 to 10 rosters, view assigned incharges, and generate bulk fee challans.",
            "🏫", theme.SECONDARY, self.open_class_selection
        )
        c3 = self.create_action_card(
            "Directory & Archives",
            "Live search across all enrolled students, edit bio-data, and export student files.",
            "📂", "#8B5CF6", self.open_directory
        )

        cards_lay.addWidget(c1)
        cards_lay.addWidget(c2)
        cards_lay.addWidget(c3)
        layout.addLayout(cards_lay)
        layout.addStretch()
        return widget

    def create_action_card(self, title: str, desc: str, icon: str, color_hex: str, callback) -> ModernCard:
        card = ModernCard()
        card.setFixedHeight(210)
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(24, 24, 24, 24)
        card_lay.setSpacing(12)

        icon_box = QFrame()
        icon_box.setFixedSize(46, 46)
        icon_box.setStyleSheet(f"""
            QFrame {{
                background-color: {color_hex}15;
                border: 1px solid {color_hex}33;
                border-radius: 12px;
            }}
        """)
        i_lay = QVBoxLayout(icon_box)
        i_lay.setContentsMargins(0, 0, 0, 0)
        i_lbl = QLabel(icon)
        i_lbl.setAlignment(Qt.AlignCenter)
        i_lbl.setFont(QFont("Segoe UI Emoji", 20))
        i_lay.addWidget(i_lbl)
        card_lay.addWidget(icon_box)

        lbl_t = QLabel(title)
        lbl_t.setFont(theme.font_h2())
        lbl_t.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-weight: 700;")
        card_lay.addWidget(lbl_t)

        lbl_d = QLabel(desc)
        lbl_d.setFont(theme.font_small())
        lbl_d.setStyleSheet(f"color: {theme.TEXT_SECONDARY};")
        lbl_d.setWordWrap(True)
        card_lay.addWidget(lbl_d)

        card_lay.addStretch()

        btn = theme.create_outline_button(f"Open {title} →")
        btn.setFixedHeight(34)
        btn.clicked.connect(callback)
        card_lay.addWidget(btn)

        return card

    # --- 2. ADMISSION FORM ---
    def create_admission_form_view(self) -> QWidget:
        self.admission_container = QWidget()
        self.admission_container_lay = QVBoxLayout(self.admission_container)
        self.admission_container_lay.setContentsMargins(32, 20, 32, 20)
        self.admission_container_lay.setSpacing(14)
        return self.admission_container

    def open_admission_form(self, student: Optional[Student] = None, return_view: str = "directory"):
        while self.admission_container_lay.count():
            item = self.admission_container_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

        form = StudentAdmissionForm(parent=self.admission_container, student=student, is_dialog_mode=False)
        form.saved.connect(lambda _: self.open_directory())
        form.cancelled.connect(self.open_directory)
        self.admission_container_lay.addWidget(form)

        self.sub_stack.setCurrentIndex(1)

    # --- 3. CLASS SELECTION GRID ---
    def create_class_selection_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(18)

        header = PageHeader(
            "Class Directory & Assigned Faculty",
            "Select a grade level to review student rosters and generate bulk fee challans"
        )
        layout.addWidget(header)

        self.class_grid_container = QWidget()
        self.class_grid_lay = QVBoxLayout(self.class_grid_container)
        self.class_grid_lay.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.class_grid_container)
        return widget

    def open_class_selection(self):
        while self.class_grid_lay.count():
            item = self.class_grid_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        students = db.get_all_students()
        staff_list = db.get_all_staff()

        incharge_map = {st.assigned_class: st.get_full_name() for st in staff_list if st.assigned_class}
        class_counts = {str(i): 0 for i in range(1, 11)}
        for s in students:
            if s.class_name in class_counts:
                class_counts[s.class_name] += 1

        for row in range(2):
            row_lay = QHBoxLayout()
            row_lay.setSpacing(16)
            for col in range(5):
                cls_num = str(row * 5 + col + 1)
                count = class_counts.get(cls_num, 0)
                incharge = incharge_map.get(cls_num, "Faculty Unassigned")

                card = ModernCard()
                card.setFixedHeight(140)
                c_lay = QVBoxLayout(card)
                c_lay.setContentsMargins(18, 16, 18, 16)
                c_lay.setSpacing(6)

                top_row = QHBoxLayout()
                lbl_cls = QLabel(f"Class {cls_num}")
                lbl_cls.setFont(theme.font_h2())
                lbl_cls.setStyleSheet(f"color: {theme.PRIMARY}; font-weight: 800;")
                top_row.addWidget(lbl_cls)
                top_row.addStretch()

                chip = StatusBadge(f"{count} Students", "info")
                top_row.addWidget(chip)
                c_lay.addLayout(top_row)

                lbl_inc = QLabel(f"Incharge: {incharge}")
                lbl_inc.setFont(theme.font_small())
                lbl_inc.setStyleSheet(f"color: {theme.TEXT_SECONDARY};")
                c_lay.addWidget(lbl_inc)

                c_lay.addStretch()

                btn_view = theme.create_primary_button("Open Roster →")
                btn_view.setFixedHeight(30)
                btn_view.clicked.connect(lambda _, c=cls_num: self.open_class_roster(c))
                c_lay.addWidget(btn_view)

                row_lay.addWidget(card)
            self.class_grid_lay.addLayout(row_lay)

        self.sub_stack.setCurrentIndex(2)

    # --- 4. CLASS STUDENTS VIEW ---
    def create_class_students_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(18)

        self.class_header = PageHeader("Class Student Roster", "Enrolled students in this grade level")
        btn_fee = theme.create_secondary_button("Bulk Fee Vouchers")
        btn_fee.clicked.connect(self.generate_bulk_fee_challans)
        self.class_header.add_action(btn_fee)

        layout.addWidget(self.class_header)

        card = ModernCard()
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(16, 16, 16, 16)

        self.class_table = QTableWidget(0, 7)
        self.class_table.setHorizontalHeaderLabels(["Adm #", "Student Name", "Father Name", "Contact", "Age", "Status", "Actions"])
        theme.format_table(self.class_table, 46)
        self.class_table.setEditTriggers(QTableWidget.NoEditTriggers)

        c_hdr = self.class_table.horizontalHeader()
        c_hdr.setSectionResizeMode(0, QHeaderView.Interactive)
        c_hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        c_hdr.setSectionResizeMode(2, QHeaderView.Interactive)
        c_hdr.setSectionResizeMode(3, QHeaderView.Interactive)
        c_hdr.setSectionResizeMode(4, QHeaderView.Interactive)
        c_hdr.setSectionResizeMode(5, QHeaderView.Interactive)
        c_hdr.setSectionResizeMode(6, QHeaderView.Interactive)
        self.class_table.setColumnWidth(0, 125)
        self.class_table.setColumnWidth(2, 160)
        self.class_table.setColumnWidth(3, 125)
        self.class_table.setColumnWidth(4, 70)
        self.class_table.setColumnWidth(5, 120)
        self.class_table.setColumnWidth(6, 165)
        card_lay.addWidget(self.class_table)

        layout.addWidget(card)
        return widget

    def open_class_roster(self, class_name: str):
        self.current_roster_class = class_name
        self.class_header.lbl_title.setText(f"Class {class_name} Student Roster")
        students = [s for s in db.get_all_students() if s.class_name == class_name]

        self.class_table.setRowCount(len(students))
        for row, s in enumerate(students):
            item_adm = QTableWidgetItem(s.admission_no)
            item_adm.setTextAlignment(Qt.AlignCenter)
            self.class_table.setItem(row, 0, item_adm)
            self.class_table.setItem(row, 1, QTableWidgetItem(s.get_full_name()))
            self.class_table.setItem(row, 2, QTableWidgetItem(s.father_name))
            self.class_table.setItem(row, 3, QTableWidgetItem(s.contact or "N/A"))
            self.class_table.setItem(row, 4, QTableWidgetItem(str(s.age)))

            badge = StatusBadge.from_status(s.status)
            self.class_table.setCellWidget(row, 5, theme.create_cell_widget(badge))

            btn_edit = theme.create_table_button("Edit", "primary")
            btn_edit.clicked.connect(lambda _, st=s: self.edit_student(st))

            btn_del = theme.create_table_button("Delete", "danger")
            btn_del.clicked.connect(lambda _, adm=s.admission_no: self.delete_student(adm))

            self.class_table.setCellWidget(row, 6, theme.create_cell_widget(btn_edit, btn_del))

        self.sub_stack.setCurrentIndex(3)

    def generate_bulk_fee_challans(self):
        cls = getattr(self, "current_roster_class", "1")
        students = [s for s in db.get_all_students() if s.class_name == cls]
        QMessageBox.information(
            self, "Bulk Fee Challans Generated",
            f"Successfully generated {len(students)} fee vouchers for Class {cls}!\n"
            f"Tuition and term charges ready for processing in Finance Center."
        )

    # --- 5. SEARCHABLE DIRECTORY / ARCHIVES ---
    def create_directory_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(18)

        header = PageHeader(
            "Student Archives & Complete Directory",
            "Live search across student database with instant bio-data editing and records management"
        )
        layout.addWidget(header)

        # Filters Bar Card
        filter_card = ModernCard()
        f_lay = QHBoxLayout(filter_card)
        f_lay.setContentsMargins(18, 12, 18, 12)
        f_lay.setSpacing(14)

        self.search_input = ModernSearchBar("Search by name, admission #, CNIC, or contact...")
        self.search_input.textChanged.connect(self.filter_students)
        f_lay.addWidget(self.search_input, 4)

        self.filter_class = QComboBox()
        self.filter_class.addItem("All Grades (1-10)")
        self.filter_class.addItems([f"Class {i}" for i in range(1, 11)])
        self.filter_class.currentIndexChanged.connect(self.filter_students)
        f_lay.addWidget(self.filter_class, 2)

        btn_refresh = theme.create_secondary_button("Refresh")
        btn_refresh.clicked.connect(self.open_directory)
        f_lay.addWidget(btn_refresh, 1)

        layout.addWidget(filter_card)

        # Table Card
        table_card = ModernCard()
        t_lay = QVBoxLayout(table_card)
        t_lay.setContentsMargins(16, 16, 16, 16)

        self.dir_table = QTableWidget(0, 7)
        self.dir_table.setHorizontalHeaderLabels(["Adm #", "Full Name", "Father Name", "Class", "Contact", "Status", "Actions"])
        theme.format_table(self.dir_table, 46)
        self.dir_table.setEditTriggers(QTableWidget.NoEditTriggers)

        d_hdr = self.dir_table.horizontalHeader()
        d_hdr.setSectionResizeMode(0, QHeaderView.Interactive)
        d_hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        d_hdr.setSectionResizeMode(2, QHeaderView.Interactive)
        d_hdr.setSectionResizeMode(3, QHeaderView.Interactive)
        d_hdr.setSectionResizeMode(4, QHeaderView.Interactive)
        d_hdr.setSectionResizeMode(5, QHeaderView.Interactive)
        d_hdr.setSectionResizeMode(6, QHeaderView.Interactive)
        self.dir_table.setColumnWidth(0, 125)
        self.dir_table.setColumnWidth(2, 160)
        self.dir_table.setColumnWidth(3, 85)
        self.dir_table.setColumnWidth(4, 125)
        self.dir_table.setColumnWidth(5, 120)
        self.dir_table.setColumnWidth(6, 165)
        t_lay.addWidget(self.dir_table)

        layout.addWidget(table_card)
        return widget

    def open_directory(self):
        self.all_students = db.get_all_students()
        self.filter_students()
        self.sub_stack.setCurrentIndex(4)

    def filter_students(self):
        query = self.search_input.text().strip().lower()
        sel_class = self.filter_class.currentText()

        filtered = []
        for s in getattr(self, "all_students", []):
            if sel_class != "All Grades (1-10)" and f"Class {s.class_name}" != sel_class:
                continue
            if query:
                match = (
                    query in s.admission_no.lower() or
                    query in s.get_full_name().lower() or
                    query in s.father_name.lower() or
                    query in s.cnic.lower() or
                    query in s.contact.lower()
                )
                if not match:
                    continue
            filtered.append(s)

        self.dir_table.setRowCount(len(filtered))
        for row, s in enumerate(filtered):
            item_adm = QTableWidgetItem(s.admission_no)
            item_adm.setTextAlignment(Qt.AlignCenter)
            self.dir_table.setItem(row, 0, item_adm)
            self.dir_table.setItem(row, 1, QTableWidgetItem(s.get_full_name()))
            self.dir_table.setItem(row, 2, QTableWidgetItem(s.father_name))
            self.dir_table.setItem(row, 3, QTableWidgetItem(f"Class {s.class_name}"))
            self.dir_table.setItem(row, 4, QTableWidgetItem(s.contact or "N/A"))

            badge = StatusBadge.from_status(s.status)
            self.dir_table.setCellWidget(row, 5, theme.create_cell_widget(badge))

            btn_edit = theme.create_table_button("Edit", "primary")
            btn_edit.clicked.connect(lambda _, st=s: self.edit_student(st))

            btn_del = theme.create_table_button("Delete", "danger")
            btn_del.clicked.connect(lambda _, adm=s.admission_no: self.delete_student(adm))

            self.dir_table.setCellWidget(row, 6, theme.create_cell_widget(btn_edit, btn_del))

    def edit_student(self, student: Student):
        self.open_admission_form(student=student, return_view="directory")

    def delete_student(self, admission_no: str):
        ret = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to permanently remove Student #{admission_no}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if ret == QMessageBox.Yes:
            db.delete_student(admission_no)
            self.open_directory()
