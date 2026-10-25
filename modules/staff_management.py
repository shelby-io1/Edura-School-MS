"""
Staff Management Module for School Management System.
Redesigned with ModernCard containers, StatusBadge chips, and unified Enterprise registration forms.
"""
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QDialog, QMessageBox, QDoubleSpinBox,
    QScrollArea, QGridLayout, QStackedWidget
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, Signal
import core.theme as theme
import core.database as db
from core.models import Staff
from core.widgets import (
    ModernCard, StatusBadge, PageHeader, ModernSearchBar,
    FormHeaderCard, FormSectionHeader, FormFieldGroup
)
from datetime import date


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
            btn_edit.clicked.connect(lambda _, s=st: self.open_edit_staff_dialog(s))

            btns = [btn_edit]
            if st.staff_type == "Teaching Staff":
                btn_assign = theme.create_table_button("Subjects", "outline")
                btn_assign.clicked.connect(lambda _, s=st: self.open_teaching_assignments_dialog(s))
                btns.append(btn_assign)

            btn_del = theme.create_table_button("Delete", "danger")
            btn_del.clicked.connect(lambda _, sid=st.staff_id: self.delete_staff(sid))
            btns.append(btn_del)

            self.table.setCellWidget(row, 7, theme.create_cell_widget(*btns))

    def open_admission_form(self, staff: Optional[Staff] = None):
        while self.form_container_lay.count():
            item = self.form_container_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        form = StaffAdmissionForm(parent=self.form_container, staff=staff)
        form.saved.connect(lambda _: self.close_sub_view())
        form.cancelled.connect(self.close_sub_view)
        self.form_container_lay.addWidget(form)

        self.stack.setCurrentIndex(1)

    def close_sub_view(self):
        self.stack.setCurrentIndex(0)
        self.refresh_data()

    def open_new_staff_dialog(self):
        self.open_admission_form(staff=None)

    def open_edit_staff_dialog(self, st: Staff):
        self.open_admission_form(staff=st)

    def open_teaching_assignments_dialog(self, st: Staff):
        while self.alloc_container_lay.count():
            item = self.alloc_container_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        header = PageHeader(
            f"Course Allocations — {st.get_full_name()} ({st.staff_id})",
            "Manage subjects, curricula, and assigned class grades taught by this faculty member"
        )
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
