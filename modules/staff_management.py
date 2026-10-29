"""
Staff Management Module for School Management System.
Redesigned with ModernCard containers, StatusBadge chips, and unified Enterprise registration forms.
"""
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QDialog, QMessageBox, QDoubleSpinBox,
    QScrollArea, QGridLayout, QStackedWidget, QTabWidget
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, Signal
import core.theme as theme
import core.database as db
from core.models import Staff
from core.widgets import (
    ModernCard, StatusBadge, PageHeader, ModernSearchBar,
    FormHeaderCard, FormSectionHeader, FormFieldGroup, MetricCard
)
from datetime import date, datetime


class StaffAdmissionForm(QWidget):
    """
    Unified staff & faculty registration form component.
    Standardized with the same design system, section cards, input dimensions, and action buttons as Student Admission.
    """
    saved = Signal(object)      # emits saved Staff
    cancelled = Signal()

    def __init__(self, parent=None, staff: Optional[Staff] = None):
        super().__init__(parent)
        self.staff = staff
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
        if self.staff:
            self.header_card = FormHeaderCard(
                title=f"Faculty Profile — {self.staff.get_full_name()} ({self.staff.staff_id})",
                subtitle="Official institutional personnel employment record and departmental placement",
                icon_str="👨‍🏫"
            )
            self.header_card.add_badge(StatusBadge.from_status(self.staff.status or "ACTIVE"))
            self.header_card.add_badge(StatusBadge(self.staff.staff_type, "info"))
            self.header_card.add_badge(StatusBadge(f"ID: {self.staff.staff_id}", "neutral"))
        else:
            self.header_card = FormHeaderCard(
                title="Faculty & Staff Admission & Registration",
                subtitle="Official institutional registry for instructional, administrative, and operational personnel",
                icon_str="👨‍🏫"
            )
            self.header_card.add_badge(StatusBadge("NEW REGISTRATION", "primary"))
            self.header_card.add_badge(StatusBadge("CAMPUS FACULTY", "neutral"))

        lay.addWidget(self.header_card)

        # 2. Section 1 Card: Employee Personal & Demographic Information
        sec1_card = ModernCard()
        sec1_lay = QVBoxLayout(sec1_card)
        sec1_lay.setContentsMargins(24, 20, 24, 22)
        sec1_lay.setSpacing(16)

        sec1_lay.addWidget(FormSectionHeader(
            "Employee Personal & Identity Information", "👤",
            "Legal identity, employee registration code, and official parentage"
        ))

        grid1 = QGridLayout()
        grid1.setHorizontalSpacing(18)
        grid1.setVerticalSpacing(14)

        # Staff ID
        self.id_input = QLineEdit()
        self.id_input.setFixedHeight(38)
        if self.staff:
            self.id_input.setText(self.staff.staff_id)
            self.id_input.setReadOnly(True)
            self.id_input.setStyleSheet("QLineEdit { background-color: #F8FAFC; color: #64748B; border: 1.5px solid #E2E8F0; border-radius: 8px; padding: 0 12px; }")
        else:
            self.id_input.setText(db.generate_random_staff_id())
        grid1.addWidget(FormFieldGroup("Staff / Employee ID", self.id_input, required=True, helper_text="Unique institutional staff tracking code"), 0, 0)

        # First Name
        self.first_name_input = QLineEdit(self.staff.first_name if self.staff else "")
        self.first_name_input.setFixedHeight(38)
        self.first_name_input.setPlaceholderText("e.g. Tariq")
        grid1.addWidget(FormFieldGroup("First Name", self.first_name_input, required=True), 0, 1)

        # Last Name
        self.last_name_input = QLineEdit(self.staff.last_name if self.staff else "")
        self.last_name_input.setFixedHeight(38)
        self.last_name_input.setPlaceholderText("e.g. Mehmood")
        grid1.addWidget(FormFieldGroup("Last Name / Surname", self.last_name_input, required=True), 1, 0)

        # Father / Guardian Name
        self.father_name_input = QLineEdit(self.staff.father_name if self.staff else "")
        self.father_name_input.setFixedHeight(38)
        self.father_name_input.setPlaceholderText("e.g. Abdul Ghafoor")
        grid1.addWidget(FormFieldGroup("Father / Guardian Name", self.father_name_input, required=False), 1, 1)

        sec1_lay.addLayout(grid1)
        lay.addWidget(sec1_card)

        # 3. Section 2 Card: Institutional Allocation & Departmental Placement
        sec2_card = ModernCard()
        sec2_lay = QVBoxLayout(sec2_card)
        sec2_lay.setContentsMargins(24, 20, 24, 22)
        sec2_lay.setSpacing(16)

        sec2_lay.addWidget(FormSectionHeader(
            "Institutional Allocation & Departmental Placement", "💼",
            "Department classification, official designation, assigned incharge, and salary"
        ))

        grid2 = QGridLayout()
        grid2.setHorizontalSpacing(18)
        grid2.setVerticalSpacing(14)

        # Department
        self.type_combo = QComboBox()
        self.type_combo.setFixedHeight(38)
        self.type_combo.addItems(["Teaching Staff", "Administrative Staff", "Security Staff", "Support Staff"])
        if self.staff and self.staff.staff_type:
            idx = self.type_combo.findText(self.staff.staff_type)
            if idx >= 0:
                self.type_combo.setCurrentIndex(idx)
        grid2.addWidget(FormFieldGroup("Department / Division", self.type_combo, required=True), 0, 0)

        # Designation
        self.desig_input = QLineEdit(self.staff.designation if self.staff else "Teacher")
        self.desig_input.setFixedHeight(38)
        self.desig_input.setPlaceholderText("e.g. Senior Science Teacher, Vice Principal")
        grid2.addWidget(FormFieldGroup("Designation / Role", self.desig_input, required=True), 0, 1)

        # Assigned Class
        self.class_combo = QComboBox()
        self.class_combo.setFixedHeight(38)
        self.class_combo.addItem("None")
        self.class_combo.addItems([str(i) for i in range(1, 11)])
        if self.staff and self.staff.assigned_class:
            idx = self.class_combo.findText(self.staff.assigned_class)
            if idx >= 0:
                self.class_combo.setCurrentIndex(idx)
        grid2.addWidget(FormFieldGroup("Assigned Class Incharge", self.class_combo, required=False), 1, 0)

        # Monthly Salary
        self.salary_input = QDoubleSpinBox()
        self.salary_input.setFixedHeight(38)
        self.salary_input.setRange(0, 1000000)
        self.salary_input.setValue(self.staff.salary if self.staff else 45000.0)
        self.salary_input.setPrefix("PKR ")
        self.salary_input.setSingleStep(1000)
        grid2.addWidget(FormFieldGroup("Monthly Gross Salary (PKR)", self.salary_input, required=True), 1, 1)

        # Employment Status
        self.status_combo = QComboBox()
        self.status_combo.setFixedHeight(38)
        self.status_combo.addItems(["ACTIVE", "RESIGNED", "TERMINATED", "RETIRED"])
        if self.staff and self.staff.status:
            idx = self.status_combo.findText(self.staff.status)
            if idx >= 0:
                self.status_combo.setCurrentIndex(idx)
        grid2.addWidget(FormFieldGroup("Employment Status", self.status_combo, required=True), 2, 0)

        # Joining Date
        self.date_input = QLineEdit(self.staff.join_date if self.staff and self.staff.join_date else date.today().isoformat())
        self.date_input.setFixedHeight(38)
        self.date_input.setPlaceholderText("YYYY-MM-DD")
        grid2.addWidget(FormFieldGroup("Official Joining Date", self.date_input, required=False), 2, 1)

        sec2_lay.addLayout(grid2)
        lay.addWidget(sec2_card)

        # 4. Section 3 Card: Contact Coordinates & Residential Address
        sec3_card = ModernCard()
        sec3_lay = QVBoxLayout(sec3_card)
        sec3_lay.setContentsMargins(24, 20, 24, 22)
        sec3_lay.setSpacing(16)

        sec3_lay.addWidget(FormSectionHeader(
            "Contact Coordinates & Official Communications", "📍",
            "Telephone lines, official institutional email, and residential address"
        ))

        grid3 = QGridLayout()
        grid3.setHorizontalSpacing(18)
        grid3.setVerticalSpacing(14)

        # Contact Phone
        self.contact_input = QLineEdit(self.staff.contact if self.staff else "")
        self.contact_input.setFixedHeight(38)
        self.contact_input.setPlaceholderText("e.g. 0300-1234567")
        grid3.addWidget(FormFieldGroup("Primary Contact Phone", self.contact_input, required=True), 0, 0)

        # Email
        self.email_input = QLineEdit(self.staff.email if self.staff else "")
        self.email_input.setFixedHeight(38)
        self.email_input.setPlaceholderText("e.g. faculty.member@school.edu.pk")
        grid3.addWidget(FormFieldGroup("Email Address", self.email_input, required=False), 0, 1)

        # Notes / Address
        self.notes_input = QLineEdit(self.staff.notes if self.staff else "")
        self.notes_input.setFixedHeight(38)
        self.notes_input.setPlaceholderText("Residential address, qualifications, or administrative remarks")
        grid3.addWidget(FormFieldGroup("Residential Address & Remarks", self.notes_input, required=False), 1, 0, 1, 2)

        sec3_lay.addLayout(grid3)
        lay.addWidget(sec3_card)

        # 5. Form Action Footer Card
        action_card = ModernCard()
        act_lay = QHBoxLayout(action_card)
        act_lay.setContentsMargins(24, 16, 24, 16)
        act_lay.setSpacing(14)

        self.btn_cancel = theme.create_outline_button("Cancel & Close")
        self.btn_cancel.setFixedHeight(40)
        self.btn_cancel.clicked.connect(self.cancelled.emit)
        act_lay.addWidget(self.btn_cancel)

        act_lay.addStretch()

        submit_text = "✓ Update Faculty Record" if self.staff else "✓ Register Faculty Member"
        self.btn_submit = theme.create_primary_button(submit_text)
        self.btn_submit.setFixedHeight(42)
        self.btn_submit.setMinimumWidth(220)
        self.btn_submit.clicked.connect(self.save_staff_data)
        act_lay.addWidget(self.btn_submit)

        lay.addWidget(action_card)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def save_staff_data(self):
        first = self.first_name_input.text().strip()
        last = self.last_name_input.text().strip()
        sid = self.id_input.text().strip()

        if not first or not last or not sid:
            QMessageBox.warning(self, "Missing Information", "Staff ID, First Name, and Last Name are required fields.")
            return

        assigned = self.class_combo.currentText()
        st = Staff(
            staff_id=sid,
            first_name=first,
            last_name=last,
            father_name=self.father_name_input.text().strip(),
            staff_type=self.type_combo.currentText(),
            designation=self.desig_input.text().strip(),
            contact=self.contact_input.text().strip(),
            email=self.email_input.text().strip(),
            salary=self.salary_input.value(),
            assigned_class="" if assigned == "None" else assigned,
            status=self.status_combo.currentText(),
            join_date=self.date_input.text().strip() or date.today().isoformat(),
            notes=self.notes_input.text().strip()
        )
        db.save_staff(st)

        msg = f"Staff member {st.get_full_name()} updated successfully." if self.staff else f"Staff member {st.get_full_name()} registered successfully!"
        QMessageBox.information(self, "Success", msg)
        self.saved.emit(st)


class StaffAdmissionDialog(QDialog):
    """Dialog window embedding the unified StaffAdmissionForm for registering or editing staff."""
    def __init__(self, staff: Optional[Staff] = None, parent=None):
        super().__init__(parent)
        title = f"Edit Faculty Record — {staff.get_full_name()} ({staff.staff_id})" if staff else "Register New Faculty / Staff Member"
        self.setWindowTitle(title)
        self.resize(850, 720)
        self.setStyleSheet(f"background-color: {theme.BACKGROUND};")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)

        self.form = StaffAdmissionForm(parent=self, staff=staff)
        self.form.saved.connect(self.accept)
        self.form.cancelled.connect(self.reject)
        lay.addWidget(self.form)


class StaffManagementView(QWidget):
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"background-color: {theme.BACKGROUND};")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        # View 0: Faculty Directory Table
        self.dir_widget = self.create_directory_view()
        self.stack.addWidget(self.dir_widget)

        # View 1: In-Page Admission & Registration Form
        self.form_container = QWidget()
        self.form_container_lay = QVBoxLayout(self.form_container)
        self.form_container_lay.setContentsMargins(28, 20, 28, 20)
        self.stack.addWidget(self.form_container)

        # View 2: In-Page Course Allocations View
        self.alloc_container = QWidget()
        self.alloc_container_lay = QVBoxLayout(self.alloc_container)
        self.alloc_container_lay.setContentsMargins(28, 20, 28, 20)
        self.stack.addWidget(self.alloc_container)

        # View 3: In-Page Faculty Portfolio & 360° Profile View
        self.profile_widget = self.create_staff_profile_view()
        self.stack.addWidget(self.profile_widget)

        self.stack.setCurrentIndex(0)
        self.refresh_data()

    def create_directory_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(18)

        # Header Bar
        header = PageHeader(
            "Faculty & Staff Directory",
            "Manage teachers, administrative officers, security staff, and course allocations"
        )
        btn_add = theme.create_primary_button("+ Register New Faculty Member")
        btn_add.setFixedHeight(38)
        btn_add.clicked.connect(self.open_new_staff_dialog)
        header.add_action(btn_add)
        layout.addWidget(header)

        # Filter Card
        filter_card = ModernCard()
        f_lay = QHBoxLayout(filter_card)
        f_lay.setContentsMargins(18, 12, 18, 12)
        f_lay.setSpacing(14)

        self.search_input = ModernSearchBar("Search by ID, name, email, or designation...")
        self.search_input.textChanged.connect(self.filter_staff)
        f_lay.addWidget(self.search_input, 4)

        self.filter_type = QComboBox()
        self.filter_type.addItems(["All Departments", "Teaching Staff", "Administrative Staff", "Security Staff", "Support Staff"])
        self.filter_type.currentIndexChanged.connect(self.filter_staff)
        f_lay.addWidget(self.filter_type, 2)

        self.filter_status = QComboBox()
        self.filter_status.addItems(["All Statuses", "ACTIVE", "RESIGNED", "TERMINATED", "RETIRED"])
        self.filter_status.currentIndexChanged.connect(self.filter_staff)
        f_lay.addWidget(self.filter_status, 2)

        btn_refresh = theme.create_secondary_button("Refresh")
        btn_refresh.clicked.connect(self.refresh_data)
        f_lay.addWidget(btn_refresh, 1)

        layout.addWidget(filter_card)

        # Table Card
        table_card = ModernCard()
        t_lay = QVBoxLayout(table_card)
        t_lay.setContentsMargins(16, 16, 16, 16)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Staff ID", "Full Name", "Department", "Designation",
            "Contact", "Assigned Class", "Salary (PKR)", "Actions"
        ])
        theme.format_table(self.table, 46)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setCursor(Qt.PointingHandCursor)
        self.table.cellClicked.connect(self.on_staff_table_cell_clicked)

        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.Interactive)
        hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.Interactive)
        hdr.setSectionResizeMode(3, QHeaderView.Interactive)
        hdr.setSectionResizeMode(4, QHeaderView.Interactive)
        hdr.setSectionResizeMode(5, QHeaderView.Interactive)
        hdr.setSectionResizeMode(6, QHeaderView.Interactive)
        hdr.setSectionResizeMode(7, QHeaderView.Interactive)
        self.table.setColumnWidth(0, 90)
        self.table.setColumnWidth(2, 130)
        self.table.setColumnWidth(3, 135)
        self.table.setColumnWidth(4, 125)
        self.table.setColumnWidth(5, 110)
        self.table.setColumnWidth(6, 115)
        self.table.setColumnWidth(7, 230)
        t_lay.addWidget(self.table)

        layout.addWidget(table_card)

        return widget

    def set_sub_view(self, sub_route: str):
        sub = sub_route.lower().strip()
        if sub in ("register", "new", "add"):
            self.open_new_staff_dialog()
        else:
            self.refresh_data()

    def refresh_data(self):
        self.all_staff = db.get_all_staff()
        self.filter_staff()

    def filter_staff(self):
        query = self.search_input.text().strip().lower()
        sel_type = self.filter_type.currentText()
        sel_status = self.filter_status.currentText()

        filtered = []
        for st in getattr(self, "all_staff", []):
            if sel_type != "All Departments" and st.staff_type != sel_type:
                continue
            if sel_status != "All Statuses" and st.status != sel_status:
                continue
            if query:
                match = (
                    query in st.staff_id.lower() or
                    query in st.get_full_name().lower() or
                    query in st.email.lower() or
                    query in st.designation.lower() or
                    query in st.contact.lower()
                )
                if not match:
                    continue
            filtered.append(st)

        self.filtered_staff = filtered
        self.table.setRowCount(len(filtered))
        for row, st in enumerate(filtered):
            self.table.setItem(row, 0, QTableWidgetItem(st.staff_id))
            self.table.setItem(row, 1, QTableWidgetItem(st.get_full_name()))

            dept_badge = StatusBadge.from_status(st.staff_type)
            self.table.setCellWidget(row, 2, theme.create_cell_widget(dept_badge))

            self.table.setItem(row, 3, QTableWidgetItem(st.designation))
            self.table.setItem(row, 4, QTableWidgetItem(st.contact or "N/A"))
            self.table.setItem(row, 5, QTableWidgetItem(f"Class {st.assigned_class}" if st.assigned_class else "None"))
            self.table.setItem(row, 6, QTableWidgetItem(f"Rs. {st.salary:,.0f}"))

            btn_edit = theme.create_table_button("Edit", "primary")
            btn_edit.clicked.connect(lambda _, s=st: self.open_edit_staff_dialog(s, return_view="directory"))

            btns = [btn_edit]
            if st.staff_type == "Teaching Staff":
                btn_assign = theme.create_table_button("Subjects", "outline")
                btn_assign.clicked.connect(lambda _, s=st: self.open_teaching_assignments_dialog(s, return_view="directory"))
                btns.append(btn_assign)

            btn_del = theme.create_table_button("Delete", "danger")
            btn_del.clicked.connect(lambda _, sid=st.staff_id: self.delete_staff(sid))
            btns.append(btn_del)

            self.table.setCellWidget(row, 7, theme.create_cell_widget(*btns))

    def on_staff_table_cell_clicked(self, row: int, col: int):
        if col < 7:
            staff_list = getattr(self, "filtered_staff", [])
            if 0 <= row < len(staff_list):
                self.open_staff_profile(staff_list[row])

    def open_admission_form(self, staff: Optional[Staff] = None, return_view: str = "directory"):
        while self.form_container_lay.count():
            item = self.form_container_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        form = StaffAdmissionForm(parent=self.form_container, staff=staff)

        def on_saved(saved_staff):
            if return_view == "profile":
                self.open_staff_profile(saved_staff)
            else:
                self.close_sub_view()

        def on_cancelled():
            if return_view == "profile" and staff:
                self.open_staff_profile(staff)
            else:
                self.close_sub_view()

        form.saved.connect(on_saved)
        form.cancelled.connect(on_cancelled)
        self.form_container_lay.addWidget(form)

        self.stack.setCurrentIndex(1)

    def close_sub_view(self):
        self.stack.setCurrentIndex(0)
        self.refresh_data()

    def open_new_staff_dialog(self):
        self.open_admission_form(staff=None, return_view="directory")

    def open_edit_staff_dialog(self, st: Staff, return_view: str = "directory"):
        self.open_admission_form(staff=st, return_view=return_view)

    def open_teaching_assignments_dialog(self, st: Staff, return_view: str = "directory"):
        while self.alloc_container_lay.count():
            item = self.alloc_container_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        header = PageHeader(
            f"Course Allocations — {st.get_full_name()} ({st.staff_id})",
            "Manage subjects, curricula, and assigned class grades taught by this faculty member"
        )
        btn_back = theme.create_secondary_button("← Return")
        btn_back.clicked.connect(lambda: self.open_staff_profile(st) if return_view == "profile" else self.close_sub_view())
        header.add_action(btn_back)
        self.alloc_container_lay.addWidget(header)

        card = ModernCard()
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(22, 20, 22, 20)
        c_lay.setSpacing(16)

        add_box = QHBoxLayout()
        add_box.setSpacing(12)
        cls_combo = QComboBox()
        cls_combo.addItems([f"Class {i}" for i in range(1, 11)])
        cls_combo.setFixedHeight(38)

        subj_combo = QComboBox()
        subj_combo.addItems(db.DEFAULT_SUBJECTS)
        subj_combo.setFixedHeight(38)

        btn_add = theme.create_primary_button("+ Assign Course")
        btn_add.setFixedHeight(38)

        add_box.addWidget(QLabel("Class Grade:"), 0)
        add_box.addWidget(cls_combo, 2)
        add_box.addWidget(QLabel("Subject:"), 0)
        add_box.addWidget(subj_combo, 2)
        add_box.addWidget(btn_add, 1)
        c_lay.addLayout(add_box)

        alloc_table = QTableWidget(0, 3)
        alloc_table.setHorizontalHeaderLabels(["Class Grade", "Subject Curricula", "Action"])
        theme.format_table(alloc_table, 44)
        a_hdr = alloc_table.horizontalHeader()
        a_hdr.setSectionResizeMode(0, QHeaderView.Interactive)
        a_hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        a_hdr.setSectionResizeMode(2, QHeaderView.Interactive)
        alloc_table.setColumnWidth(0, 140)
        alloc_table.setColumnWidth(2, 120)
        alloc_table.setMinimumHeight(350)
        c_lay.addWidget(alloc_table)
        self.alloc_container_lay.addWidget(card)

        def reload_assignments():
            assignments = db.get_teaching_assignments(st.staff_id)
            alloc_table.setRowCount(len(assignments))
            for row, (c, s) in enumerate(assignments):
                alloc_table.setItem(row, 0, QTableWidgetItem(f"Class {c}"))
                alloc_table.setItem(row, 1, QTableWidgetItem(s))
                btn_remove = theme.create_table_button("Remove", "danger")
                btn_remove.clicked.connect(lambda _, cl=c, su=s: remove_assignment(cl, su))
                alloc_table.setCellWidget(row, 2, theme.create_cell_widget(btn_remove))

        def add_assignment():
            c = cls_combo.currentText().replace("Class ", "")
            s = subj_combo.currentText()
            db.save_teaching_assignment(st.staff_id, c, s)
            reload_assignments()

        def remove_assignment(cl, su):
            db.delete_teaching_assignment(st.staff_id, cl, su)
            reload_assignments()

        btn_add.clicked.connect(add_assignment)
        reload_assignments()
        self.stack.setCurrentIndex(2)

    def delete_staff(self, staff_id: str):
        ret = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to remove Staff #{staff_id}? All course assignments will also be deleted.",
            QMessageBox.Yes | QMessageBox.No
        )
        if ret == QMessageBox.Yes:
            db.delete_staff(staff_id)
            self.refresh_data()

    # --- 4. STAFF FACULTY PORTFOLIO & 360° PROFILE VIEW ---
    def create_staff_profile_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(32, 24, 32, 28)
        lay.setSpacing(18)

        # 1. Hero Profile Header Card
        self.profile_hero_card = ModernCard()
        hero_lay = QHBoxLayout(self.profile_hero_card)
        hero_lay.setContentsMargins(24, 20, 24, 20)
        hero_lay.setSpacing(20)

        # Avatar circle
        avatar_box = QFrame()
        avatar_box.setFixedSize(72, 72)
        avatar_box.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.PRIMARY_LIGHT};
                border: 2px solid {theme.PRIMARY}33;
                border-radius: 36px;
            }}
        """)
        av_lay = QVBoxLayout(avatar_box)
        av_lay.setContentsMargins(0, 0, 0, 0)
        self.lbl_profile_avatar = QLabel("👨‍🏫")
        self.lbl_profile_avatar.setAlignment(Qt.AlignCenter)
        self.lbl_profile_avatar.setFont(QFont("Segoe UI Emoji", 30))
        av_lay.addWidget(self.lbl_profile_avatar)
        hero_lay.addWidget(avatar_box)

        # Staff Main Details
        info_vbox = QVBoxLayout()
        info_vbox.setSpacing(6)

        title_hbox = QHBoxLayout()
        title_hbox.setSpacing(12)
        self.lbl_profile_name = QLabel("Faculty Member Name")
        self.lbl_profile_name.setFont(QFont(theme.FONT_FAMILY, 18, QFont.Bold))
        self.lbl_profile_name.setStyleSheet("color: #0F172A;")
        title_hbox.addWidget(self.lbl_profile_name)

        self.badge_profile_status = StatusBadge("ACTIVE", "success")
        title_hbox.addWidget(self.badge_profile_status)

        self.badge_profile_id = StatusBadge("ID #T101", "neutral")
        title_hbox.addWidget(self.badge_profile_id)
        title_hbox.addStretch()
        info_vbox.addLayout(title_hbox)

        badges_hbox = QHBoxLayout()
        badges_hbox.setSpacing(10)
        self.badge_profile_dept = StatusBadge("Teaching Staff", "primary")
        badges_hbox.addWidget(self.badge_profile_dept)

        self.badge_profile_desig = StatusBadge("Teacher", "info")
        badges_hbox.addWidget(self.badge_profile_desig)

        self.badge_profile_incharge = StatusBadge("Incharge: None", "neutral")
        badges_hbox.addWidget(self.badge_profile_incharge)

        self.lbl_profile_meta = QLabel("Contact: 0300-1234567  •  Email: teacher@excellence.edu.pk  •  Joined: 2024-08-15")
        self.lbl_profile_meta.setStyleSheet("color: #64748B; font-size: 13px; font-weight: 500;")
        badges_hbox.addWidget(self.lbl_profile_meta)
        badges_hbox.addStretch()
        info_vbox.addLayout(badges_hbox)

        hero_lay.addLayout(info_vbox, 1)

        # Action Buttons on right
        act_vbox = QVBoxLayout()
        act_vbox.setSpacing(10)
        act_vbox.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        btn_edit = theme.create_primary_button("✏️ Edit Record")
        btn_edit.setFixedHeight(36)
        btn_edit.clicked.connect(self.on_profile_edit_clicked)
        act_vbox.addWidget(btn_edit)

        self.btn_profile_courses = theme.create_secondary_button("📚 Course Allocations")
        self.btn_profile_courses.setFixedHeight(36)
        self.btn_profile_courses.clicked.connect(self.on_profile_courses_clicked)
        act_vbox.addWidget(self.btn_profile_courses)

        self.btn_profile_return = theme.create_secondary_button("← Return")
        self.btn_profile_return.setFixedHeight(36)
        self.btn_profile_return.clicked.connect(self.close_staff_profile)
        act_vbox.addWidget(self.btn_profile_return)

        hero_lay.addLayout(act_vbox)
        lay.addWidget(self.profile_hero_card)

        # 2. Modern 4-Tab Faculty Portfolio
        self.staff_tabs = QTabWidget()
        self.staff_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: transparent;
            }}
            QTabBar::tab {{
                background: {theme.SURFACE};
                color: {theme.TEXT_SECONDARY};
                font-family: {theme.FONT_FAMILY};
                font-weight: 600;
                font-size: 13px;
                padding: 10px 22px;
                margin-right: 8px;
                border-radius: 8px;
                border: 1px solid {theme.BORDER_COLOR};
            }}
            QTabBar::tab:selected {{
                background: {theme.PRIMARY};
                color: #FFFFFF;
                border: 1px solid {theme.PRIMARY};
            }}
            QTabBar::tab:hover:!selected {{
                background: #F1F5F9;
                color: {theme.TEXT_PRIMARY};
            }}
        """)

        # Add 4 tabs
        self.tab_dossier = self.create_staff_dossier_tab()
        self.staff_tabs.addTab(self.tab_dossier, "👤 Demographics && Dossier")

        self.tab_assignments = self.create_staff_assignments_tab()
        self.staff_tabs.addTab(self.tab_assignments, "📚 Teaching Allocations")

        self.tab_payroll = self.create_staff_payroll_tab()
        self.staff_tabs.addTab(self.tab_payroll, "💰 Salary && Payroll History")

        self.tab_reminders = self.create_staff_reminders_tab()
        self.staff_tabs.addTab(self.tab_reminders, "📌 Tasks && Reminders")

        lay.addWidget(self.staff_tabs)

        scroll.setWidget(container)
        layout.addWidget(scroll)
        return widget

    def create_staff_dossier_tab(self) -> QWidget:
        widget = QWidget()
        self.dossier_content_layout = QVBoxLayout(widget)
        self.dossier_content_layout.setContentsMargins(0, 14, 0, 0)
        self.dossier_content_layout.setSpacing(16)
        return widget

    def create_staff_assignments_tab(self) -> QWidget:
        widget = QWidget()
        lay = QVBoxLayout(widget)
        lay.setContentsMargins(0, 14, 0, 0)
        lay.setSpacing(16)

        m_row = QHBoxLayout()
        m_row.setSpacing(14)
        self.metric_alloc_classes = MetricCard("Assigned Grade Levels", "0", "🏫", theme.INFO, theme.INFO_LIGHT)
        self.metric_alloc_courses = MetricCard("Active Curriculum Courses", "0", "📚", theme.PRIMARY, theme.PRIMARY_LIGHT)
        self.metric_alloc_score = MetricCard("Teaching Load Standing", "Optimal", "⚡", theme.SECONDARY, theme.SECONDARY_LIGHT)
        m_row.addWidget(self.metric_alloc_classes)
        m_row.addWidget(self.metric_alloc_courses)
        m_row.addWidget(self.metric_alloc_score)
        lay.addLayout(m_row)

        card = ModernCard()
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(20, 18, 20, 20)
        c_lay.setSpacing(14)

        t_header = QHBoxLayout()
        header_lbl = QLabel("Instructional Course & Grade Allocations")
        header_lbl.setFont(QFont(theme.FONT_FAMILY, 15, QFont.Bold))
        header_lbl.setStyleSheet(f"color: {theme.TEXT_PRIMARY};")
        t_header.addWidget(header_lbl)
        t_header.addStretch()

        btn_manage = theme.create_secondary_button("⚙️ Manage Course Assignments")
        btn_manage.clicked.connect(self.on_profile_courses_clicked)
        t_header.addWidget(btn_manage)
        c_lay.addLayout(t_header)

        self.profile_alloc_table = QTableWidget(0, 3)
        self.profile_alloc_table.setHorizontalHeaderLabels(["Class Grade Level", "Curriculum Subject", "Instructional Standing"])
        theme.format_table(self.profile_alloc_table, 42)
        self.profile_alloc_table.setEditTriggers(QTableWidget.NoEditTriggers)

        al_hdr = self.profile_alloc_table.horizontalHeader()
        al_hdr.setSectionResizeMode(0, QHeaderView.Interactive)
        al_hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        al_hdr.setSectionResizeMode(2, QHeaderView.Interactive)
        self.profile_alloc_table.setColumnWidth(0, 180)
        self.profile_alloc_table.setColumnWidth(2, 200)
        c_lay.addWidget(self.profile_alloc_table)

        self.lbl_alloc_empty = QLabel("No courses or subjects allocated yet for this faculty member.")
        self.lbl_alloc_empty.setAlignment(Qt.AlignCenter)
        self.lbl_alloc_empty.setStyleSheet("color: #64748B; font-size: 13px; font-weight: 500; padding: 24px;")
        c_lay.addWidget(self.lbl_alloc_empty)

        lay.addWidget(card)
        return widget

    def create_staff_payroll_tab(self) -> QWidget:
        widget = QWidget()
        lay = QVBoxLayout(widget)
        lay.setContentsMargins(0, 14, 0, 0)
        lay.setSpacing(16)

        m_row = QHBoxLayout()
        m_row.setSpacing(14)
        self.metric_pay_salary = MetricCard("Monthly Base Salary", "Rs. 0", "💰", theme.PRIMARY, theme.PRIMARY_LIGHT)
        self.metric_pay_annual = MetricCard("Annual Base Compensation", "Rs. 0", "💼", theme.INFO, theme.INFO_LIGHT)
        self.metric_pay_status = MetricCard("Recent Payroll Status", "Disbursed", "✅", theme.SECONDARY, theme.SECONDARY_LIGHT)
        m_row.addWidget(self.metric_pay_salary)
        m_row.addWidget(self.metric_pay_annual)
        m_row.addWidget(self.metric_pay_status)
        lay.addLayout(m_row)

        card = ModernCard()
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(20, 18, 20, 20)
        c_lay.setSpacing(14)

        header_lbl = QLabel("Historical Monthly Compensation & Payroll Records")
        header_lbl.setFont(QFont(theme.FONT_FAMILY, 15, QFont.Bold))
        header_lbl.setStyleSheet(f"color: {theme.TEXT_PRIMARY};")
        c_lay.addWidget(header_lbl)

        self.profile_payroll_table = QTableWidget(0, 6)
        self.profile_payroll_table.setHorizontalHeaderLabels([
            "Payroll Month", "Base Salary (PKR)", "Allowances", "Net Disbursed", "Payment Status", "Disbursement Date"
        ])
        theme.format_table(self.profile_payroll_table, 42)
        self.profile_payroll_table.setEditTriggers(QTableWidget.NoEditTriggers)

        py_hdr = self.profile_payroll_table.horizontalHeader()
        py_hdr.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 6):
            py_hdr.setSectionResizeMode(i, QHeaderView.Interactive)
            self.profile_payroll_table.setColumnWidth(i, 130 if i < 4 else 145)
        c_lay.addWidget(self.profile_payroll_table)

        lay.addWidget(card)
        return widget

    def create_staff_reminders_tab(self) -> QWidget:
        widget = QWidget()
        lay = QVBoxLayout(widget)
        lay.setContentsMargins(0, 14, 0, 0)
        lay.setSpacing(16)

        m_row = QHBoxLayout()
        m_row.setSpacing(14)
        self.metric_rem_total = MetricCard("Assigned Tasks & Notices", "0", "📌", theme.PRIMARY, theme.PRIMARY_LIGHT)
        self.metric_rem_pending = MetricCard("Pending Deadlines", "0", "⏳", theme.WARNING, theme.WARNING_LIGHT)
        self.metric_rem_done = MetricCard("Completed Actions", "0", "✅", theme.SECONDARY, theme.SECONDARY_LIGHT)
        m_row.addWidget(self.metric_rem_total)
        m_row.addWidget(self.metric_rem_pending)
        m_row.addWidget(self.metric_rem_done)
        lay.addLayout(m_row)

        card = ModernCard()
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(20, 18, 20, 20)
        c_lay.setSpacing(14)

        header_lbl = QLabel("Professional Duties, Reminders & Institutional Notices")
        header_lbl.setFont(QFont(theme.FONT_FAMILY, 15, QFont.Bold))
        header_lbl.setStyleSheet(f"color: {theme.TEXT_PRIMARY};")
        c_lay.addWidget(header_lbl)

        self.profile_task_table = QTableWidget(0, 6)
        self.profile_task_table.setHorizontalHeaderLabels([
            "Task / Notice Title", "Description", "Due Date", "Priority", "Category", "Status"
        ])
        theme.format_table(self.profile_task_table, 42)
        self.profile_task_table.setEditTriggers(QTableWidget.NoEditTriggers)

        r_hdr = self.profile_task_table.horizontalHeader()
        r_hdr.setSectionResizeMode(0, QHeaderView.Interactive)
        r_hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        r_hdr.setSectionResizeMode(2, QHeaderView.Interactive)
        r_hdr.setSectionResizeMode(3, QHeaderView.Interactive)
        r_hdr.setSectionResizeMode(4, QHeaderView.Interactive)
        r_hdr.setSectionResizeMode(5, QHeaderView.Interactive)
        self.profile_task_table.setColumnWidth(0, 180)
        self.profile_task_table.setColumnWidth(2, 110)
        self.profile_task_table.setColumnWidth(3, 100)
        self.profile_task_table.setColumnWidth(4, 115)
        self.profile_task_table.setColumnWidth(5, 115)
        c_lay.addWidget(self.profile_task_table)

        self.lbl_rem_empty = QLabel("No pending tasks, reminders or institutional notices assigned to this staff member.")
        self.lbl_rem_empty.setAlignment(Qt.AlignCenter)
        self.lbl_rem_empty.setStyleSheet("color: #64748B; font-size: 13px; font-weight: 500; padding: 24px;")
        c_lay.addWidget(self.lbl_rem_empty)

        lay.addWidget(card)
        return widget

    # --- 5. STAFF PROFILE POPULATION & NAVIGATION ---
    def open_staff_profile(self, st: Staff):
        self.current_profile_staff = st

        # Hero header update
        self.lbl_profile_name.setText(st.get_full_name())
        self.badge_profile_status.setText(st.status.upper() if st.status else "ACTIVE")
        self.badge_profile_status.set_variant(
            "success" if st.status == "ACTIVE" else "neutral"
        )
        self.badge_profile_id.setText(f"ID #{st.staff_id}")
        self.badge_profile_dept.setText(st.staff_type)
        self.badge_profile_desig.setText(st.designation)

        if st.assigned_class:
            self.badge_profile_incharge.setText(f"Incharge: Class {st.assigned_class}")
            self.badge_profile_incharge.show()
        else:
            self.badge_profile_incharge.setText("Incharge: None")
            self.badge_profile_incharge.show()

        self.lbl_profile_meta.setText(
            f"Contact: {st.contact or 'N/A'}  •  Email: {st.email or 'N/A'}  •  Joined: {st.join_date or 'N/A'}"
        )

        if st.staff_type == "Teaching Staff":
            self.btn_profile_courses.show()
        else:
            self.btn_profile_courses.hide()

        self.btn_profile_return.setText("← Return to Faculty Directory")

        # Populate tabs
        self.populate_staff_dossier(st)
        self.populate_staff_assignments(st)
        self.populate_staff_payroll(st)
        self.populate_staff_reminders(st)

        self.staff_tabs.setCurrentIndex(0)
        self.stack.setCurrentIndex(3)

    def close_staff_profile(self):
        self.stack.setCurrentIndex(0)
        self.refresh_data()

    def on_profile_edit_clicked(self):
        if hasattr(self, "current_profile_staff") and self.current_profile_staff:
            self.open_edit_staff_dialog(self.current_profile_staff, return_view="profile")

    def on_profile_courses_clicked(self):
        if hasattr(self, "current_profile_staff") and self.current_profile_staff:
            self.open_teaching_assignments_dialog(self.current_profile_staff, return_view="profile")

    def _make_info_widget(self, label: str, value: str) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        lbl_title = QLabel(label.upper())
        lbl_title.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;")
        lbl_val = QLabel(str(value) if value and str(value).strip() else "—")
        lbl_val.setStyleSheet("color: #0F172A; font-size: 14px; font-weight: 600;")
        lbl_val.setWordWrap(True)
        lay.addWidget(lbl_title)
        lay.addWidget(lbl_val)
        return w

    def populate_staff_dossier(self, st: Staff):
        while self.dossier_content_layout.count():
            item = self.dossier_content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Card 1: Identity & Vital Information
        card1 = ModernCard()
        c1_lay = QVBoxLayout(card1)
        c1_lay.setContentsMargins(22, 20, 22, 20)
        c1_lay.setSpacing(16)
        c1_lay.addWidget(FormSectionHeader(
            "Employee Personal & Identity Information", "👤",
            "Legal identity, employee registration code, and official parentage"
        ))
        g1 = QGridLayout()
        g1.setHorizontalSpacing(24)
        g1.setVerticalSpacing(14)
        g1.addWidget(self._make_info_widget("Staff / Employee ID", st.staff_id), 0, 0)
        g1.addWidget(self._make_info_widget("Full Legal Name", st.get_full_name()), 0, 1)
        g1.addWidget(self._make_info_widget("Father / Guardian Name", st.father_name), 0, 2)
        g1.addWidget(self._make_info_widget("Blood Group", st.blood_group), 1, 0)
        g1.addWidget(self._make_info_widget("Appointment Date", st.join_date), 1, 1)
        g1.addWidget(self._make_info_widget("Employment Status", st.status), 1, 2)
        c1_lay.addLayout(g1)
        self.dossier_content_layout.addWidget(card1)

        # Card 2: Contact & Residential Coordinates
        card2 = ModernCard()
        c2_lay = QVBoxLayout(card2)
        c2_lay.setContentsMargins(22, 20, 22, 20)
        c2_lay.setSpacing(16)
        c2_lay.addWidget(FormSectionHeader(
            "Communication & Residential Coordinates", "📞",
            "Primary phone contact, official email address, and legal residential address"
        ))
        g2 = QGridLayout()
        g2.setHorizontalSpacing(24)
        g2.setVerticalSpacing(14)
        g2.addWidget(self._make_info_widget("Primary Mobile Contact", st.contact), 0, 0)
        g2.addWidget(self._make_info_widget("Official Email Address", st.email), 0, 1)
        g2.addWidget(self._make_info_widget("Residential Address", st.address), 1, 0, 1, 2)
        c2_lay.addLayout(g2)
        self.dossier_content_layout.addWidget(card2)

        # Card 3: Qualifications & Professional Experience
        card3 = ModernCard()
        c3_lay = QVBoxLayout(card3)
        c3_lay.setContentsMargins(22, 20, 22, 20)
        c3_lay.setSpacing(16)
        c3_lay.addWidget(FormSectionHeader(
            "Academic Qualifications & Teaching Credentials", "🎓",
            "Highest degree, verified pedagogical experience, and official dossier notes"
        ))
        g3 = QGridLayout()
        g3.setHorizontalSpacing(24)
        g3.setVerticalSpacing(14)
        g3.addWidget(self._make_info_widget("Highest Qualification", st.qualification or "Master of Science / Arts"), 0, 0)
        g3.addWidget(self._make_info_widget("Verified Experience", st.experience or "Pedagogical Experience on record"), 0, 1)
        g3.addWidget(self._make_info_widget("Verified Documents on File", st.documents or "National ID Copy, Verified Degrees"), 1, 0)
        g3.addWidget(self._make_info_widget("Administrative Dossier Notes", st.notes or "Faculty member in active institutional standing"), 1, 1)
        c3_lay.addLayout(g3)
        self.dossier_content_layout.addWidget(card3)

        # Card 4: Institutional Role & Departmental Placement
        card4 = ModernCard()
        c4_lay = QVBoxLayout(card4)
        c4_lay.setContentsMargins(22, 20, 22, 20)
        c4_lay.setSpacing(16)
        c4_lay.addWidget(FormSectionHeader(
            "Institutional Placement & Compensation", "💼",
            "Department division, official role, assigned class teacher, and monthly remuneration"
        ))
        g4 = QGridLayout()
        g4.setHorizontalSpacing(24)
        g4.setVerticalSpacing(14)
        g4.addWidget(self._make_info_widget("Department Division", st.staff_type), 0, 0)
        g4.addWidget(self._make_info_widget("Official Designation", st.designation), 0, 1)
        g4.addWidget(self._make_info_widget("Assigned Class Incharge", f"Class {st.assigned_class}" if st.assigned_class else "None"), 1, 0)
        g4.addWidget(self._make_info_widget("Base Remuneration (Monthly)", f"Rs. {st.salary:,.0f}"), 1, 1)
        c4_lay.addLayout(g4)
        self.dossier_content_layout.addWidget(card4)

    def populate_staff_assignments(self, st: Staff):
        assignments = db.get_teaching_assignments(st.staff_id)
        classes_set = set(c for c, _ in assignments)

        self.metric_alloc_classes.set_value(f"{len(classes_set)} Grades")
        self.metric_alloc_courses.set_value(f"{len(assignments)} Courses")
        load = "Balanced" if len(assignments) <= 6 else "Intensive"
        self.metric_alloc_score.set_value(load)

        if assignments:
            self.lbl_alloc_empty.hide()
            self.profile_alloc_table.show()
            self.profile_alloc_table.setRowCount(len(assignments))
            for row, (c, s) in enumerate(assignments):
                self.profile_alloc_table.setItem(row, 0, QTableWidgetItem(f"Class {c}"))
                self.profile_alloc_table.setItem(row, 1, QTableWidgetItem(s))
                b_active = StatusBadge("ACTIVE ALLOCATION", "success")
                self.profile_alloc_table.setCellWidget(row, 2, theme.create_cell_widget(b_active))
        else:
            self.profile_alloc_table.setRowCount(0)
            self.profile_alloc_table.hide()
            self.lbl_alloc_empty.show()

    def populate_staff_payroll(self, st: Staff):
        payroll = db.get_staff_payroll_history(st.staff_id, st.salary)
        self.metric_pay_salary.set_value(f"Rs. {st.salary:,.0f}")
        self.metric_pay_annual.set_value(f"Rs. {st.salary * 12:,.0f}")
        recent_status = payroll[0]["status"] if payroll else "Disbursed"
        self.metric_pay_status.set_value(recent_status)

        self.profile_payroll_table.setRowCount(len(payroll))
        for row, p in enumerate(payroll):
            self.profile_payroll_table.setItem(row, 0, QTableWidgetItem(p["month_label"]))
            self.profile_payroll_table.setItem(row, 1, QTableWidgetItem(f"Rs. {p['salary']:,.0f}"))
            self.profile_payroll_table.setItem(row, 2, QTableWidgetItem(f"Rs. {p['allowances']:,.0f}"))
            self.profile_payroll_table.setItem(row, 3, QTableWidgetItem(f"Rs. {p['net_payable']:,.0f}"))

            badge = StatusBadge.from_status(p["status"])
            self.profile_payroll_table.setCellWidget(row, 4, theme.create_cell_widget(badge))
            self.profile_payroll_table.setItem(row, 5, QTableWidgetItem(p["disbursed_date"]))

    def populate_staff_reminders(self, st: Staff):
        reminders = db.get_reminders(staff_id=st.staff_id)
        tot = len(reminders)
        pending = sum(1 for r in reminders if r.status != "Completed")
        done = sum(1 for r in reminders if r.status == "Completed")

        self.metric_rem_total.set_value(str(tot))
        self.metric_rem_pending.set_value(str(pending))
        self.metric_rem_done.set_value(str(done))

        if reminders:
            self.lbl_rem_empty.hide()
            self.profile_task_table.show()
            self.profile_task_table.setRowCount(len(reminders))
            for row, r in enumerate(reminders):
                self.profile_task_table.setItem(row, 0, QTableWidgetItem(r.title))
                self.profile_task_table.setItem(row, 1, QTableWidgetItem(r.description))
                self.profile_task_table.setItem(row, 2, QTableWidgetItem(r.due_date))

                p_badge = StatusBadge.from_status(r.priority)
                self.profile_task_table.setCellWidget(row, 3, theme.create_cell_widget(p_badge))

                self.profile_task_table.setItem(row, 4, QTableWidgetItem(r.reminder_type))

                s_badge = StatusBadge.from_status(r.status)
                self.profile_task_table.setCellWidget(row, 5, theme.create_cell_widget(s_badge))
        else:
            self.profile_task_table.setRowCount(0)
            self.profile_task_table.hide()
            self.lbl_rem_empty.show()

