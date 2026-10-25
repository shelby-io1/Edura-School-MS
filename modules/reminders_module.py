"""
Reminders Module for School Management System.
Redesigned with ModernCard containers, StatusBadge chips, and priority badges.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QDialog, QFormLayout, QLineEdit, QTextEdit,
    QMessageBox, QDateEdit, QScrollArea, QStackedWidget
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, Signal, QDate
import core.theme as theme
import core.database as db
from core.models import TeacherReminder
from core.widgets import ModernCard, StatusBadge, PageHeader
from datetime import date


class RemindersView(QWidget):
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

        self.list_widget = self.create_overview_view()
        self.stack.addWidget(self.list_widget)

        self.create_widget = self.create_new_reminder_view()
        self.stack.addWidget(self.create_widget)

        self.stack.setCurrentIndex(0)
        self.reload_reminders()

    def create_overview_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(18)

        # Header Bar
        header = PageHeader(
            "Task Reminders & Priority Alerts",
            "Institutional milestones, faculty agendas, inspection dates, and action items"
        )
        btn_add = theme.create_primary_button("+ Add New Task Reminder")
        btn_add.setFixedHeight(38)
        btn_add.clicked.connect(self.open_add_dialog)
        header.add_action(btn_add)
        layout.addWidget(header)

        # Filter bar Card
        filter_card = ModernCard()
        filter_lay = QHBoxLayout(filter_card)
        filter_lay.setContentsMargins(20, 12, 20, 12)
        filter_lay.setSpacing(14)

        p_lbl = QLabel("Priority Level:")
        p_lbl.setFont(theme.font_bold())
        filter_lay.addWidget(p_lbl)

        self.priority_filter = QComboBox()
        self.priority_filter.addItems(["All Priorities", "High", "Medium", "Low"])
        self.priority_filter.currentIndexChanged.connect(self.reload_reminders)
        filter_lay.addWidget(self.priority_filter)

        s_lbl = QLabel("Status:")
        s_lbl.setFont(theme.font_bold())
        filter_lay.addWidget(s_lbl)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Statuses", "Pending", "Completed"])
        self.status_filter.currentIndexChanged.connect(self.reload_reminders)
        filter_lay.addWidget(self.status_filter)

        filter_lay.addStretch()

        btn_refresh = theme.create_secondary_button("Refresh")
        btn_refresh.clicked.connect(self.reload_reminders)
        filter_lay.addWidget(btn_refresh)

        layout.addWidget(filter_card)

        # Scroll Area for Cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setSpacing(14)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(self.cards_container)

        layout.addWidget(scroll)

        return widget

    def reload_reminders(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        reminders = db.get_reminders()
        p_filter = self.priority_filter.currentText()
        s_filter = self.status_filter.currentText()

        count = 0
        for r in reminders:
            if p_filter != "All Priorities" and r.priority != p_filter:
                continue
            if s_filter != "All Statuses" and r.status != s_filter:
                continue

            card = self.create_reminder_card(r)
            self.cards_layout.addWidget(card)
            count += 1

        if count == 0:
            empty_card = ModernCard()
            e_lay = QVBoxLayout(empty_card)
            empty_lbl = QLabel("No reminders found matching the selected filter criteria.")
            empty_lbl.setFont(theme.font_regular())
            empty_lbl.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; padding: 25px;")
            empty_lbl.setAlignment(Qt.AlignCenter)
            e_lay.addWidget(empty_lbl)
            self.cards_layout.addWidget(empty_card)

        self.cards_layout.addStretch()

    def create_reminder_card(self, r: TeacherReminder) -> ModernCard:
        card = ModernCard()
        card_lay = QHBoxLayout(card)
        card_lay.setContentsMargins(20, 16, 20, 16)
        card_lay.setSpacing(16)

        # Left: Priority Color Bar Indicator
        p_color = theme.DANGER if r.priority.lower() == "high" else (theme.WARNING if r.priority.lower() == "medium" else theme.SECONDARY)
        indicator = QFrame()
        indicator.setFixedWidth(5)
        indicator.setStyleSheet(f"background-color: {p_color}; border-radius: 2px;")
        card_lay.addWidget(indicator)

        # Center Details
        info_lay = QVBoxLayout()
        info_lay.setSpacing(4)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        lbl_title = QLabel(r.title)
        lbl_title.setFont(theme.font_h2())
        if r.status.lower() == "completed":
            lbl_title.setStyleSheet("text-decoration: line-through; color: #94A3B8;")
        else:
            lbl_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-weight: 700;")
        top_row.addWidget(lbl_title)

        p_badge = StatusBadge.from_status(r.priority)
        top_row.addWidget(p_badge)

        type_badge = StatusBadge(r.reminder_type, "neutral")
        top_row.addWidget(type_badge)
        top_row.addStretch()

        info_lay.addLayout(top_row)

        if r.description:
            lbl_desc = QLabel(r.description)
            lbl_desc.setFont(theme.font_regular())
            lbl_desc.setStyleSheet(f"color: {theme.TEXT_SECONDARY};")
            lbl_desc.setWordWrap(True)
            info_lay.addWidget(lbl_desc)

        lbl_due = QLabel(f"📅 Deadline: {r.due_date or 'No deadline specified'}")
        lbl_due.setFont(theme.font_small())
        lbl_due.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-weight: 600;")
        info_lay.addWidget(lbl_due)

        card_lay.addLayout(info_lay, 5)

        # Right Action Buttons
        act_lay = QVBoxLayout()
        act_lay.setAlignment(Qt.AlignCenter)
        act_lay.setSpacing(6)

        btn_toggle = theme.create_primary_button("✓ Mark Done" if r.status == "Pending" else "↺ Reopen")
        btn_toggle.setFixedHeight(30)
        btn_toggle.clicked.connect(lambda _, rid=r.id, cur=r.status: self.toggle_reminder(rid, cur))
        act_lay.addWidget(btn_toggle)

        btn_del = theme.create_danger_outline_button("Delete")
        btn_del.setFixedHeight(30)
        btn_del.clicked.connect(lambda _, rid=r.id: self.delete_reminder(rid))
        act_lay.addWidget(btn_del)

        card_lay.addLayout(act_lay, 1)
        return card

    def toggle_reminder(self, reminder_id: int, current_status: str):
        new_status = "Completed" if current_status == "Pending" else "Pending"
        db.update_reminder_status(reminder_id, new_status)
        self.reload_reminders()

    def delete_reminder(self, reminder_id: int):
        db.delete_reminder(reminder_id)
        self.reload_reminders()

    def create_new_reminder_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(18)

        header = PageHeader(
            "Schedule Task Reminder & Priority Alert",
            "Set institutional agendas, milestones, priority levels, and completion targets"
        )
        layout.addWidget(header)

        card = ModernCard()
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(24, 24, 24, 24)
        c_lay.setSpacing(16)

        form = QFormLayout()
        form.setSpacing(14)

        self.rem_title_input = QLineEdit()
        self.rem_title_input.setPlaceholderText("e.g. Submit Mid-Term Examination Papers")
        self.rem_title_input.setFixedHeight(38)

        self.rem_desc_input = QTextEdit()
        self.rem_desc_input.setPlaceholderText("Additional instructions or agenda details...")
        self.rem_desc_input.setFixedHeight(80)

        self.rem_priority_combo = QComboBox()
        self.rem_priority_combo.addItems(["High", "Medium", "Low"])
        self.rem_priority_combo.setCurrentText("Medium")
        self.rem_priority_combo.setFixedHeight(38)

        self.rem_type_combo = QComboBox()
        self.rem_type_combo.addItems(["General", "Exam", "Curriculum", "Meeting", "Administrative"])
        self.rem_type_combo.setFixedHeight(38)

        self.rem_date_edit = QDateEdit()
        self.rem_date_edit.setCalendarPopup(True)
        self.rem_date_edit.setDate(QDate.currentDate().addDays(3))
        self.rem_date_edit.setFixedHeight(38)

        form.addRow("Task Title*:", self.rem_title_input)
        form.addRow("Description / Notes:", self.rem_desc_input)
        form.addRow("Priority Level:", self.rem_priority_combo)
        form.addRow("Task Category:", self.rem_type_combo)
        form.addRow("Due Deadline:", self.rem_date_edit)
        c_lay.addLayout(form)

        btn_row = QHBoxLayout()
        btn_save = theme.create_primary_button("✓ Save Task Reminder")
        btn_save.setFixedHeight(38)
        btn_save.clicked.connect(self.save_new_reminder)
        btn_cancel = theme.create_outline_button("Cancel")
        btn_cancel.setFixedHeight(38)
        btn_cancel.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        btn_row.addStretch()
        c_lay.addLayout(btn_row)

        layout.addWidget(card)
        layout.addStretch()
        return widget

    def open_add_dialog(self):
        self.rem_title_input.clear()
        self.rem_desc_input.clear()
        self.rem_priority_combo.setCurrentText("Medium")
        self.rem_date_edit.setDate(QDate.currentDate().addDays(3))
        self.stack.setCurrentIndex(1)

    def save_new_reminder(self):
        t = self.rem_title_input.text().strip()
        if not t:
            QMessageBox.warning(self, "Validation Error", "Task Title is required.")
            return
        new_r = TeacherReminder(
            id=0,
            staff_id="MASTER",
            title=t,
            description=self.rem_desc_input.toPlainText().strip(),
            due_date=self.rem_date_edit.date().toString("yyyy-MM-dd"),
            priority=self.rem_priority_combo.currentText(),
            reminder_type=self.rem_type_combo.currentText(),
            status="Pending"
        )
        db.save_reminder(new_r)
        QMessageBox.information(self, "Saved", f"Task reminder '{t}' saved successfully!")
        self.stack.setCurrentIndex(0)
        self.reload_reminders()
