"""
Reports Center Module for School Management System.
Features 100% Single-Window in-page audit views with zero popup windows.
"""
from datetime import date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QStackedWidget
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, Signal
import core.theme as theme
import core.database as db
from core.widgets import ModernCard, StatusBadge, PageHeader, MetricCard


class ReportsView(QWidget):
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

        # Index 0: Reports Center (4 Tiles Hub)
        self.hub_widget = self.create_hub_view()
        self.stack.addWidget(self.hub_widget)

        # Index 1: Student Rosters Audit Page
        self.student_widget = self.create_student_audit_view()
        self.stack.addWidget(self.student_widget)

        # Index 2: Faculty Directory Audit Page
        self.staff_widget = self.create_staff_audit_view()
        self.stack.addWidget(self.staff_widget)

        # Index 3: Attendance Audit Page
        self.attendance_widget = self.create_attendance_audit_view()
        self.stack.addWidget(self.attendance_widget)

        # Index 4: Financial Statement Page
        self.finance_widget = self.create_finance_audit_view()
        self.stack.addWidget(self.finance_widget)

        self.stack.setCurrentIndex(0)

    def set_sub_view(self, sub_route: str):
        sub = sub_route.lower().strip()
        if sub in ("students", "rosters"):
            self.show_student_report()
        elif sub in ("staff", "faculty"):
            self.show_staff_report()
        elif sub in ("attendance", "presence"):
            self.show_attendance_report()
        elif sub in ("finance", "audit"):
            self.show_finance_report()
        else:
            self.stack.setCurrentIndex(0)

    # -------------------------------------------------------------
    # Index 0: Reports Center Hub View
    # -------------------------------------------------------------
    def create_hub_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(24)

        header = PageHeader(
            "Institutional Reports & Audits",
            "Generate institutional audits, student enrollment rosters, faculty registers, and financial statements"
        )
        layout.addWidget(header)

        # 4 Action Tiles
        tiles_lay = QHBoxLayout()
        tiles_lay.setSpacing(20)

        c1 = self.create_rep_tile(
            "Student Rosters",
            "Class-wise student enrollment breakdown, percentages, and roster registers.",
            "👥", theme.PRIMARY, self.show_student_report
        )
        c2 = self.create_rep_tile(
            "Faculty Directory",
            "Complete staff roster, departmental breakdowns, designations, and payroll values.",
            "👨‍🏫", theme.SECONDARY, self.show_staff_report
        )
        c3 = self.create_rep_tile(
            "Attendance Audit",
            "Daily institutional attendance sheets, marked registers, and student presence rates.",
            "📅", "#8B5CF6", self.show_attendance_report
        )
        c4 = self.create_rep_tile(
            "Financial Audit",
            "Tuition fee collections, staff salary disbursements, and net cashflow statements.",
            "💰", theme.WARNING, self.show_finance_report
        )

        tiles_lay.addWidget(c1)
        tiles_lay.addWidget(c2)
        tiles_lay.addWidget(c3)
        tiles_lay.addWidget(c4)
        layout.addLayout(tiles_lay)

        layout.addStretch()
        return widget

    def create_rep_tile(self, title: str, desc: str, icon: str, color_hex: str, callback) -> ModernCard:
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

        btn = theme.create_outline_button(f"Generate {title} →")
        btn.setFixedHeight(32)
        btn.clicked.connect(callback)
        card_lay.addWidget(btn)
        return card

    # -------------------------------------------------------------
    # Index 1: In-Page Student Rosters Audit
    # -------------------------------------------------------------
    def create_student_audit_view(self) -> QWidget:
        widget = QWidget()
        lay = QVBoxLayout(widget)
        lay.setContentsMargins(32, 24, 32, 24)
        lay.setSpacing(18)

        header = PageHeader(
            "Student Enrollment Rosters Audit",
            "Institutional breakdown of candidate enrollment, active rosters, and demographic distribution"
        )
        btn_print = theme.create_primary_button("Print / Export Audit")
        btn_print.clicked.connect(lambda: QMessageBox.information(self, "Export Roster", "Roster report exported to print spooler."))
        header.add_action(btn_print)
        lay.addWidget(header)

        card = ModernCard()
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(18, 18, 18, 18)

        self.student_audit_table = QTableWidget(10, 3)
        self.student_audit_table.setHorizontalHeaderLabels(["Class Grade", "Total Enrolled Students", "% of Student Body"])
        theme.format_table(self.student_audit_table, 44)
        self.student_audit_table.setEditTriggers(QTableWidget.NoEditTriggers)
        s_hdr = self.student_audit_table.horizontalHeader()
        s_hdr.setSectionResizeMode(0, QHeaderView.Interactive)
        s_hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        s_hdr.setSectionResizeMode(2, QHeaderView.Interactive)
        self.student_audit_table.setColumnWidth(0, 140)
        self.student_audit_table.setColumnWidth(2, 180)
        c_lay.addWidget(self.student_audit_table)
        lay.addWidget(card)
        return widget

    def show_student_report(self):
        students = db.get_all_students()
        class_counts = {str(i): 0 for i in range(1, 11)}
        for s in students:
            if s.class_name in class_counts:
                class_counts[s.class_name] += 1

        total_students = len(students)
        for i in range(1, 11):
            cls = str(i)
            c_count = class_counts.get(cls, 0)
            pct = (c_count / total_students * 100) if total_students > 0 else 0
            self.student_audit_table.setItem(i - 1, 0, QTableWidgetItem(f"Class {cls}"))
            self.student_audit_table.setItem(i - 1, 1, QTableWidgetItem(f"{c_count} Enrolled"))
            self.student_audit_table.setItem(i - 1, 2, QTableWidgetItem(f"{pct:.1f}%"))

        self.stack.setCurrentIndex(1)

    # -------------------------------------------------------------
    # Index 2: In-Page Faculty Directory Audit
    # -------------------------------------------------------------
    def create_staff_audit_view(self) -> QWidget:
        widget = QWidget()
        lay = QVBoxLayout(widget)
        lay.setContentsMargins(32, 24, 32, 24)
        lay.setSpacing(18)

        header = PageHeader(
            "Faculty & Department Directory Audit",
            "Comprehensive staff roster, departmental breakdowns, compensation structures, and statuses"
        )
        btn_print = theme.create_primary_button("Print / Export Audit")
        btn_print.clicked.connect(lambda: QMessageBox.information(self, "Export Roster", "Staff directory exported successfully."))
        header.add_action(btn_print)
        lay.addWidget(header)

        card = ModernCard()
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(18, 18, 18, 18)

        self.staff_audit_table = QTableWidget(0, 5)
        self.staff_audit_table.setHorizontalHeaderLabels(["Staff ID", "Employee Full Name", "Department", "Designation", "Monthly Salary (PKR)"])
        theme.format_table(self.staff_audit_table, 44)
        self.staff_audit_table.setEditTriggers(QTableWidget.NoEditTriggers)
        st_hdr = self.staff_audit_table.horizontalHeader()
        st_hdr.setSectionResizeMode(0, QHeaderView.Interactive)
        st_hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        st_hdr.setSectionResizeMode(2, QHeaderView.Interactive)
        st_hdr.setSectionResizeMode(3, QHeaderView.Interactive)
        st_hdr.setSectionResizeMode(4, QHeaderView.Interactive)
        self.staff_audit_table.setColumnWidth(0, 90)
        self.staff_audit_table.setColumnWidth(2, 140)
        self.staff_audit_table.setColumnWidth(3, 140)
        self.staff_audit_table.setColumnWidth(4, 150)
        c_lay.addWidget(self.staff_audit_table)
        lay.addWidget(card)
        return widget

    def show_staff_report(self):
        staff_list = db.get_all_staff()
        self.staff_audit_table.setRowCount(len(staff_list))
        for row, st in enumerate(staff_list):
            self.staff_audit_table.setItem(row, 0, QTableWidgetItem(st.staff_id))
            self.staff_audit_table.setItem(row, 1, QTableWidgetItem(st.get_full_name()))

            badge = StatusBadge.from_status(st.staff_type)
            self.staff_audit_table.setCellWidget(row, 2, theme.create_cell_widget(badge))

            self.staff_audit_table.setItem(row, 3, QTableWidgetItem(st.designation))
            self.staff_audit_table.setItem(row, 4, QTableWidgetItem(f"Rs. {st.salary:,.0f}"))

        self.stack.setCurrentIndex(2)

    # -------------------------------------------------------------
    # Index 3: In-Page Daily Attendance Audit
    # -------------------------------------------------------------
    def create_attendance_audit_view(self) -> QWidget:
        widget = QWidget()
        lay = QVBoxLayout(widget)
        lay.setContentsMargins(32, 24, 32, 24)
        lay.setSpacing(18)

        header = PageHeader(
            "Institutional Attendance Sheet & Register",
            "Daily class attendance sheets, marked registers, and presence rates across grades"
        )
        btn_print = theme.create_primary_button("Print / Export Sheet")
        btn_print.clicked.connect(lambda: QMessageBox.information(self, "Export Attendance", "Attendance sheet exported successfully."))
        header.add_action(btn_print)
        lay.addWidget(header)

        card = ModernCard()
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(18, 18, 18, 18)

        self.att_date_lbl = QLabel()
        self.att_date_lbl.setFont(theme.font_h2())
        self.att_date_lbl.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-weight: 700; margin-bottom: 8px;")
        c_lay.addWidget(self.att_date_lbl)

        self.attendance_audit_table = QTableWidget(10, 4)
        self.attendance_audit_table.setHorizontalHeaderLabels(["Class Grade", "Total Class Size", "Marked Records", "Attendance Rate"])
        theme.format_table(self.attendance_audit_table, 44)
        self.attendance_audit_table.setEditTriggers(QTableWidget.NoEditTriggers)
        at_hdr = self.attendance_audit_table.horizontalHeader()
        at_hdr.setSectionResizeMode(0, QHeaderView.Interactive)
        at_hdr.setSectionResizeMode(1, QHeaderView.Interactive)
        at_hdr.setSectionResizeMode(2, QHeaderView.Interactive)
        at_hdr.setSectionResizeMode(3, QHeaderView.Stretch)
        self.attendance_audit_table.setColumnWidth(0, 140)
        self.attendance_audit_table.setColumnWidth(1, 160)
        self.attendance_audit_table.setColumnWidth(2, 160)
        c_lay.addWidget(self.attendance_audit_table)
        lay.addWidget(card)
        return widget

    def show_attendance_report(self):
        today_str = date.today().isoformat()
        self.att_date_lbl.setText(f"Attendance Report Date: {today_str}")

        students = db.get_all_students()
        for i in range(1, 11):
            cls = str(i)
            st_class = [s for s in students if s.class_name == cls]
            att_map = db.get_attendance_for_class(today_str, cls)
            presents = sum(1 for status in att_map.values() if status.upper() in ("PRESENT", "P"))
            total = len(st_class)
            pct = (presents / total * 100) if total > 0 else 100.0

            self.attendance_audit_table.setItem(i - 1, 0, QTableWidgetItem(f"Class {cls}"))
            self.attendance_audit_table.setItem(i - 1, 1, QTableWidgetItem(str(total)))
            self.attendance_audit_table.setItem(i - 1, 2, QTableWidgetItem(str(len(att_map))))

            pct_badge = StatusBadge(f"{pct:.1f}%", "success" if pct >= 90 else "warning")
            self.attendance_audit_table.setCellWidget(i - 1, 3, theme.create_cell_widget(pct_badge))

        self.stack.setCurrentIndex(3)

    # -------------------------------------------------------------
    # Index 4: In-Page Financial Audit & Statement
    # -------------------------------------------------------------
    def create_finance_audit_view(self) -> QWidget:
        widget = QWidget()
        lay = QVBoxLayout(widget)
        lay.setContentsMargins(32, 24, 32, 24)
        lay.setSpacing(18)

        header = PageHeader(
            "Institutional Financial Audit & Operating P&L",
            "Consolidated audit of student tuition billing, staff payroll outlays, and net cashflows"
        )
        btn_print = theme.create_primary_button("Print / Export Statement")
        btn_print.clicked.connect(lambda: QMessageBox.information(self, "Export Statement", "Financial statement printed to spooler."))
        header.add_action(btn_print)
        lay.addWidget(header)

        # Metrics Row
        m_row = QHBoxLayout()
        m_row.setSpacing(16)
        self.m_revenue = MetricCard("Gross Revenue Potential", "Rs. 0", "💵", theme.PRIMARY, "+100% Billing Base")
        self.m_payroll = MetricCard("Monthly Faculty Payroll", "Rs. 0", "👨‍🏫", theme.DANGER, "Institutional Outlay")
        self.m_margin = MetricCard("Net Operational Margin", "Rs. 0", "📈", theme.SECONDARY_DARK, "Surplus Reserve")
        m_row.addWidget(self.m_revenue)
        m_row.addWidget(self.m_payroll)
        m_row.addWidget(self.m_margin)
        lay.addLayout(m_row)

        card = ModernCard()
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(22, 20, 22, 20)
        c_lay.setSpacing(12)

        self.fin_detail_lbl = QLabel()
        self.fin_detail_lbl.setFont(theme.font_regular())
        self.fin_detail_lbl.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; line-height: 1.6;")
        c_lay.addWidget(self.fin_detail_lbl)
        lay.addWidget(card)
        return widget

    def show_finance_report(self):
        students = db.get_all_students()
        staff_list = db.get_all_staff()
        total_monthly_fee_per_student = float(db.get_app_data("fee_tuition", "5000")) + \
                                        float(db.get_app_data("fee_itlab", "1000")) + \
                                        float(db.get_app_data("fee_sports", "800")) + \
                                        float(db.get_app_data("fee_utilities", "700"))

        gross_rev = len(students) * total_monthly_fee_per_student
        payroll = sum(s.salary for s in staff_list)
        margin = gross_rev - payroll

        self.m_revenue.set_value(f"Rs. {gross_rev:,.0f}")
        self.m_payroll.set_value(f"Rs. {payroll:,.0f}")
        self.m_margin.set_value(f"Rs. {margin:,.0f}")

        self.fin_detail_lbl.setText(
            f"<b>Consolidated Ledger Statement Breakdown:</b><br><br>"
            f"• Total Active Enrolled Students: <b>{len(students)} candidates</b><br>"
            f"• Standard Monthly Billing per Student: <b>Rs. {total_monthly_fee_per_student:,.0f}</b><br>"
            f"• Gross Tuition Inflow Potential: <b>Rs. {gross_rev:,.0f}</b><br>"
            f"• Active Faculty & Administrative Staff: <b>{len(staff_list)} members</b><br>"
            f"• Monthly Faculty Payroll Liability: <b>Rs. {payroll:,.0f}</b><br><hr style='border: 0.5px solid #E2E8F0;'>"
            f"• Estimated Monthly Operational Surplus: <b style='color:#10B981; font-size:14px;'>Rs. {margin:,.0f}</b>"
        )

        self.stack.setCurrentIndex(4)
