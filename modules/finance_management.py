"""
Finance & Payroll Module for School Management System.
Redesigned with ModernCard containers, StatusBadge chips, and financial KPI metrics.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QDoubleSpinBox, QSpinBox, QLineEdit, QDialog, QFormLayout,
    QMessageBox, QStackedWidget
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, Signal
import core.theme as theme
import core.database as db
from core.widgets import ModernCard, StatusBadge, MetricCard, PageHeader
from datetime import date


class FinanceManagementView(QWidget):
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

        self.hub_widget = self.create_hub_view()
        self.stack.addWidget(self.hub_widget)

        self.ledger_widget = self.create_fee_ledger_view()
        self.stack.addWidget(self.ledger_widget)

        self.config_widget = self.create_fee_config_view()
        self.stack.addWidget(self.config_widget)

        self.payroll_widget = self.create_payroll_view()
        self.stack.addWidget(self.payroll_widget)

        self.pnl_widget = self.create_pnl_view()
        self.stack.addWidget(self.pnl_widget)

        self.stack.setCurrentIndex(0)

    def set_sub_view(self, sub_route: str):
        sub = sub_route.lower().strip()
        if sub in ("hub", "overview", ""):
            self.stack.setCurrentIndex(0)
        elif sub in ("ledger", "fees"):
            self.open_fee_ledger()
        elif sub in ("config", "rates", "structure"):
            self.open_fee_config()
        elif sub in ("payroll", "salaries"):
            self.open_payroll()
        elif sub in ("pnl", "surplus", "summary"):
            self.open_pnl()

    # --- 1. HUB VIEW ---
    def create_hub_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(24)

        header = PageHeader(
            "Finance & Institutional Accounts",
            "Student fee collection, billing rates, staff payroll disbursements, and institutional cash flow"
        )
        layout.addWidget(header)

        tiles_lay = QHBoxLayout()
        tiles_lay.setSpacing(20)

        c1 = self.create_fin_tile(
            "Student Fee Ledger",
            "Track monthly tuition dues, mark receipt payments, and generate challan slips.",
            "💳", theme.PRIMARY, self.open_fee_ledger
        )
        c2 = self.create_fin_tile(
            "Fee Structure Rates",
            "Configure standard tuition, computer lab, sports, and maintenance fees.",
            "⚙️", theme.SECONDARY, self.open_fee_config
        )
        c3 = self.create_fin_tile(
            "Staff Payroll Slips",
            "Disburse faculty salaries and generate official monthly salary slips.",
            "💵", "#8B5CF6", self.open_payroll
        )
        c4 = self.create_fin_tile(
            "Financial Dashboard",
            "Live institutional income vs expenditure and net operating surplus margins.",
            "📈", theme.WARNING, self.open_pnl
        )

        tiles_lay.addWidget(c1)
        tiles_lay.addWidget(c2)
        tiles_lay.addWidget(c3)
        tiles_lay.addWidget(c4)
        layout.addLayout(tiles_lay)

        layout.addStretch()
        return widget

    def create_fin_tile(self, title: str, desc: str, icon: str, color_hex: str, callback) -> ModernCard:
        card = ModernCard()
        card.setFixedHeight(210)
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(22, 22, 22, 22)
        card_lay.setSpacing(10)

        icon_box = QFrame()
        icon_box.setFixedSize(44, 44)
        icon_box.setStyleSheet(f"""
            QFrame {{
                background-color: {color_hex}15;
                border: 1px solid {color_hex}33;
                border-radius: 10px;
            }}
        """)
        i_lay = QVBoxLayout(icon_box)
        i_lay.setContentsMargins(0, 0, 0, 0)
        i_lbl = QLabel(icon)
        i_lbl.setAlignment(Qt.AlignCenter)
        i_lbl.setFont(QFont("Segoe UI Emoji", 18))
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

        btn = theme.create_outline_button(f"Manage {title} →")
        btn.setFixedHeight(32)
        btn.clicked.connect(callback)
        card_lay.addWidget(btn)

        return card

    # --- 2. FEE LEDGER VIEW ---
    def create_fee_ledger_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(18)

        header = PageHeader("Class Fee Collection Ledger", "Review monthly billing status and payment verification")
        layout.addWidget(header)

        bar_card = ModernCard()
        b_lay = QHBoxLayout(bar_card)
        b_lay.setContentsMargins(20, 12, 20, 12)
        b_lay.setSpacing(14)

        cls_lbl = QLabel("Class Grade:")
        cls_lbl.setFont(theme.font_bold())
        b_lay.addWidget(cls_lbl)

        self.ledger_class_selector = QComboBox()
        self.ledger_class_selector.addItems([f"Class {i}" for i in range(1, 11)])
        self.ledger_class_selector.currentIndexChanged.connect(self.reload_fee_ledger)
        b_lay.addWidget(self.ledger_class_selector)

        b_lay.addStretch()
        layout.addWidget(bar_card)

        table_card = ModernCard()
        t_lay = QVBoxLayout(table_card)
        t_lay.setContentsMargins(16, 16, 16, 16)

        self.ledger_table = QTableWidget(0, 6)
        self.ledger_table.setHorizontalHeaderLabels([
            "Adm #", "Student Name", "Monthly Fee (PKR)", "Payment Status", "Payment Date", "Action"
        ])
        theme.format_table(self.ledger_table, 46)
        self.ledger_table.setEditTriggers(QTableWidget.NoEditTriggers)

        l_hdr = self.ledger_table.horizontalHeader()
        l_hdr.setSectionResizeMode(0, QHeaderView.Interactive)
        l_hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        l_hdr.setSectionResizeMode(2, QHeaderView.Interactive)
        l_hdr.setSectionResizeMode(3, QHeaderView.Interactive)
        l_hdr.setSectionResizeMode(4, QHeaderView.Interactive)
        l_hdr.setSectionResizeMode(5, QHeaderView.Interactive)
        self.ledger_table.setColumnWidth(0, 125)
        self.ledger_table.setColumnWidth(2, 150)
        self.ledger_table.setColumnWidth(3, 130)
        self.ledger_table.setColumnWidth(4, 120)
        self.ledger_table.setColumnWidth(5, 140)
        t_lay.addWidget(self.ledger_table)

        layout.addWidget(table_card)
        return widget

    def open_fee_ledger(self):
        self.reload_fee_ledger()
        self.stack.setCurrentIndex(1)

    def reload_fee_ledger(self):
        cls = self.ledger_class_selector.currentText().replace("Class ", "")
        students = [s for s in db.get_all_students() if s.class_name == cls]

        tuition = float(db.get_app_data("fee_tuition", "5000"))
        it_lab = float(db.get_app_data("fee_itlab", "1000"))
        sports = float(db.get_app_data("fee_sports", "800"))
        utilities = float(db.get_app_data("fee_utilities", "700"))
        total_fee = tuition + it_lab + sports + utilities

        self.ledger_table.setRowCount(len(students))
        for row, s in enumerate(students):
            key = f"fee_status_{s.admission_no}_{date.today().strftime('%Y_%m')}"
            status = db.get_app_data(key, "Pending")

            item_adm = QTableWidgetItem(s.admission_no)
            item_adm.setTextAlignment(Qt.AlignCenter)
            self.ledger_table.setItem(row, 0, item_adm)
            self.ledger_table.setItem(row, 1, QTableWidgetItem(s.get_full_name()))
            self.ledger_table.setItem(row, 2, QTableWidgetItem(f"Rs. {total_fee:,.0f}"))

            badge = StatusBadge.from_status(status)
            self.ledger_table.setCellWidget(row, 3, theme.create_cell_widget(badge))

            pay_date = db.get_app_data(f"fee_date_{s.admission_no}_{date.today().strftime('%Y_%m')}", "-")
            self.ledger_table.setItem(row, 4, QTableWidgetItem(pay_date))

            btn_text = "Mark Paid" if status == "Pending" else "Mark Pending"
            btn_var = "primary" if status == "Pending" else "outline"
            btn_toggle = theme.create_table_button(btn_text, btn_var)
            btn_toggle.clicked.connect(lambda _, adm=s.admission_no, cur=status: self.toggle_fee_status(adm, cur))
            self.ledger_table.setCellWidget(row, 5, theme.create_cell_widget(btn_toggle))

    def toggle_fee_status(self, admission_no: str, current_status: str):
        month_key = date.today().strftime('%Y_%m')
        key = f"fee_status_{admission_no}_{month_key}"
        date_key = f"fee_date_{admission_no}_{month_key}"

        new_status = "Paid" if current_status == "Pending" else "Pending"
        db.save_app_data(key, new_status)
        db.save_app_data(date_key, date.today().isoformat() if new_status == "Paid" else "-")
        self.reload_fee_ledger()

    # --- 3. FEE CONFIG VIEW ---
    def create_fee_config_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(18)

        header = PageHeader("School Fee Structure & Rate Policies", "Define standard monthly tuition, lab, and sports rates")
        layout.addWidget(header)

        card = ModernCard()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(35, 30, 35, 30)

        form = QFormLayout()
        form.setSpacing(16)

        self.spin_tuition = QDoubleSpinBox()
        self.spin_tuition.setRange(0, 100000)
        form.addRow("Standard Tuition Fee (PKR):", self.spin_tuition)

        self.spin_itlab = QDoubleSpinBox()
        self.spin_itlab.setRange(0, 50000)
        form.addRow("IT & Computer Lab Fee (PKR):", self.spin_itlab)

        self.spin_sports = QDoubleSpinBox()
        self.spin_sports.setRange(0, 50000)
        form.addRow("Sports & Extra-Curricular (PKR):", self.spin_sports)

        self.spin_utilities = QDoubleSpinBox()
        self.spin_utilities.setRange(0, 50000)
        form.addRow("Campus Maintenance & Utilities (PKR):", self.spin_utilities)

        self.spin_late = QDoubleSpinBox()
        self.spin_late.setRange(0, 10000)
        form.addRow("Late Fee Fine (PKR):", self.spin_late)

        self.spin_due_day = QSpinBox()
        self.spin_due_day.setRange(1, 28)
        form.addRow("Monthly Due Day (Day of Month):", self.spin_due_day)

        self.input_bank = QLineEdit()
        form.addRow("Bank & Account Information:", self.input_bank)

        card_layout.addLayout(form)

        btn_save = theme.create_primary_button("Save Billing Policies")
        btn_save.setFixedHeight(42)
        btn_save.clicked.connect(self.save_fee_config)
        card_layout.addWidget(btn_save)

        layout.addWidget(card)
        return widget

    def open_fee_config(self):
        self.spin_tuition.setValue(float(db.get_app_data("fee_tuition", "5000")))
        self.spin_itlab.setValue(float(db.get_app_data("fee_itlab", "1000")))
        self.spin_sports.setValue(float(db.get_app_data("fee_sports", "800")))
        self.spin_utilities.setValue(float(db.get_app_data("fee_utilities", "700")))
        self.spin_late.setValue(float(db.get_app_data("fee_lateFee", "200")))
        self.spin_due_day.setValue(int(db.get_app_data("fee_dueDay", "10")))
        self.input_bank.setText(db.get_app_data("fee_bankDetails", "HBL Campus Account - 0022-4455"))
        self.stack.setCurrentIndex(2)

    def save_fee_config(self):
        db.save_app_data("fee_tuition", str(self.spin_tuition.value()))
        db.save_app_data("fee_itlab", str(self.spin_itlab.value()))
        db.save_app_data("fee_sports", str(self.spin_sports.value()))
        db.save_app_data("fee_utilities", str(self.spin_utilities.value()))
        db.save_app_data("fee_lateFee", str(self.spin_late.value()))
        db.save_app_data("fee_dueDay", str(self.spin_due_day.value()))
        db.save_app_data("fee_bankDetails", self.input_bank.text().strip())
        QMessageBox.information(self, "Settings Saved", "Fee structure configuration updated successfully!")
        self.stack.setCurrentIndex(0)

    # --- 4. STAFF PAYROLL VIEW ---
    def create_payroll_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(18)

        header = PageHeader("Staff Payroll Disbursements", "Monthly faculty compensation records and official payslips")
        btn_disburse_all = theme.create_primary_button("Disburse All Salaries")
        btn_disburse_all.setFixedHeight(38)
        btn_disburse_all.clicked.connect(self.disburse_all_salaries)
        header.add_action(btn_disburse_all)

        layout.addWidget(header)

        table_card = ModernCard()
        t_lay = QVBoxLayout(table_card)
        t_lay.setContentsMargins(16, 16, 16, 16)

        self.payroll_table = QTableWidget(0, 6)
        self.payroll_table.setHorizontalHeaderLabels([
            "Staff ID", "Employee Name", "Department", "Salary (PKR)", "Disbursement Status", "Payslip"
        ])
        theme.format_table(self.payroll_table, 46)
        self.payroll_table.setEditTriggers(QTableWidget.NoEditTriggers)

        p_hdr = self.payroll_table.horizontalHeader()
        p_hdr.setSectionResizeMode(0, QHeaderView.Interactive)
        p_hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        p_hdr.setSectionResizeMode(2, QHeaderView.Interactive)
        p_hdr.setSectionResizeMode(3, QHeaderView.Interactive)
        p_hdr.setSectionResizeMode(4, QHeaderView.Interactive)
        p_hdr.setSectionResizeMode(5, QHeaderView.Interactive)
        self.payroll_table.setColumnWidth(0, 90)
        self.payroll_table.setColumnWidth(2, 130)
        self.payroll_table.setColumnWidth(3, 120)
        self.payroll_table.setColumnWidth(4, 140)
        self.payroll_table.setColumnWidth(5, 125)
        t_lay.addWidget(self.payroll_table)

        layout.addWidget(table_card)
        return widget

    def open_payroll(self):
        self.reload_payroll()
        self.stack.setCurrentIndex(3)

    def reload_payroll(self):
        staff_list = db.get_all_staff()
        month_key = date.today().strftime('%Y_%m')

        self.payroll_table.setRowCount(len(staff_list))
        for row, st in enumerate(staff_list):
            key = f"payroll_status_{st.staff_id}_{month_key}"
            status = db.get_app_data(key, "Pending")

            self.payroll_table.setItem(row, 0, QTableWidgetItem(st.staff_id))
            self.payroll_table.setItem(row, 1, QTableWidgetItem(st.get_full_name()))

            dept_badge = StatusBadge.from_status(st.staff_type)
            self.payroll_table.setCellWidget(row, 2, theme.create_cell_widget(dept_badge))

            self.payroll_table.setItem(row, 3, QTableWidgetItem(f"Rs. {st.salary:,.0f}"))

            st_badge = StatusBadge.from_status(status)
            self.payroll_table.setCellWidget(row, 4, theme.create_cell_widget(st_badge))

            btn_slip = theme.create_table_button("View Slip", "outline")
            btn_slip.clicked.connect(lambda _, s=st: self.show_salary_slip(s))
            self.payroll_table.setCellWidget(row, 5, theme.create_cell_widget(btn_slip))

    def disburse_all_salaries(self):
        staff_list = db.get_all_staff()
        month_key = date.today().strftime('%Y_%m')
        for st in staff_list:
            db.save_app_data(f"payroll_status_{st.staff_id}_{month_key}", "Disbursed")
        QMessageBox.information(self, "Payroll Completed", f"Salaries disbursed for all {len(staff_list)} staff members!")
        self.reload_payroll()

    def show_salary_slip(self, st):
        month = date.today().strftime("%B %Y")
        school_name = db.get_app_data("systemName", "EXCELLENCE SCHOOL SYSTEM").upper()
        QMessageBox.information(
            self, f"Salary Slip - {st.get_full_name()}",
            f"{school_name} - OFFICIAL PAYSLIP\n\n"
            f"Employee: {st.get_full_name()} (ID: {st.staff_id})\n"
            f"Department: {st.staff_type} | Designation: {st.designation}\n"
            f"Pay Period: {month}\n"
            f"----------------------------------------\n"
            f"Basic Salary: Rs. {st.salary:,.0f}\n"
            f"Allowances: Rs. 0\n"
            f"Deductions: Rs. 0\n"
            f"----------------------------------------\n"
            f"NET SALARY DISBURSED: Rs. {st.salary:,.0f}\n"
            f"Disbursement Mode: Direct Bank Deposit"
        )

    # --- 5. FINANCIAL DASHBOARD VIEW ---
    def create_pnl_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(18)

        header = PageHeader("Financial Summary & Operating Margins", "Monthly revenue projection against faculty payroll liabilities")
        layout.addWidget(header)

        self.pnl_container = QWidget()
        self.pnl_lay = QVBoxLayout(self.pnl_container)
        self.pnl_lay.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.pnl_container)

        return widget

    def open_pnl(self):
        while self.pnl_lay.count():
            item = self.pnl_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        students = db.get_all_students()
        staff_list = db.get_all_staff()

        tuition = float(db.get_app_data("fee_tuition", "5000"))
        it_lab = float(db.get_app_data("fee_itlab", "1000"))
        sports = float(db.get_app_data("fee_sports", "800"))
        utilities = float(db.get_app_data("fee_utilities", "700"))
        total_monthly_fee = tuition + it_lab + sports + utilities

        total_income = len(students) * total_monthly_fee
        total_payroll = sum(st.salary for st in staff_list)
        net_surplus = total_income - total_payroll

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(16)

        m1 = MetricCard("Projected Inflow", f"Rs. {total_income:,.0f}", "💰", theme.PRIMARY, theme.PRIMARY_LIGHT, f"{len(students)} Students")
        m2 = MetricCard("Payroll Liabilities", f"Rs. {total_payroll:,.0f}", "👥", theme.DANGER, theme.DANGER_LIGHT, f"{len(staff_list)} Employees")
        m3 = MetricCard("Operating Surplus", f"Rs. {net_surplus:,.0f}", "📈", theme.SECONDARY, theme.SECONDARY_LIGHT, "Net Institutional Margin")

        kpi_row.addWidget(m1)
        kpi_row.addWidget(m2)
        kpi_row.addWidget(m3)
        self.pnl_lay.addLayout(kpi_row)

        self.stack.setCurrentIndex(4)
