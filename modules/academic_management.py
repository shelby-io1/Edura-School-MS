"""
Academic Management Module for School Management System.
Redesigned with ModernCard containers, period schedule timetable grid, and curriculum tools.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QMessageBox, QStackedWidget
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, Signal
import core.theme as theme
import core.database as db
from core.widgets import ModernCard, StatusBadge, PageHeader
import json


class AcademicManagementView(QWidget):
    back_requested = Signal()
    navigate_requested = Signal(str)

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

        self.timetable_widget = self.create_timetable_view()
        self.stack.addWidget(self.timetable_widget)

        self.stack.setCurrentIndex(0)

    def set_sub_view(self, sub_route: str):
        sub = sub_route.lower().strip()
        if sub in ("hub", "overview", ""):
            self.stack.setCurrentIndex(0)
        elif sub in ("timetable", "schedule"):
            self.stack.setCurrentIndex(1)
            self.load_timetable_for_class()

    def create_hub_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(24)

        header = PageHeader(
            "Academic Management Center",
            "Curriculum schedules, daily class timetables, examination calendars, and terms"
        )
        layout.addWidget(header)

        # 4 Interactive Tiles
        grid_lay = QHBoxLayout()
        grid_lay.setSpacing(20)

        c1 = self.create_hub_tile(
            "Class Timetable",
            "Configure Monday to Friday period-wise subject allocations.",
            "🗓️", theme.PRIMARY, lambda: self.stack.setCurrentIndex(1)
        )
        c2 = self.create_hub_tile(
            "Daily Attendance",
            "Monitor institutional attendance registers and student presence.",
            "📅", theme.SECONDARY, lambda: self.navigate_requested.emit("attendance")
        )
        c3 = self.create_hub_tile(
            "Term Results",
            "Review student assessment performance and print term report cards.",
            "📊", "#8B5CF6", lambda: self.navigate_requested.emit("results")
        )
        c4 = self.create_hub_tile(
            "Syllabus Progress",
            "Track curriculum chapter checklists and lecture topic coverage.",
            "📖", theme.WARNING, lambda: self.navigate_requested.emit("syllabus")
        )

        grid_lay.addWidget(c1)
        grid_lay.addWidget(c2)
        grid_lay.addWidget(c3)
        grid_lay.addWidget(c4)
        layout.addLayout(grid_lay)

        layout.addStretch()
        return widget

    def create_hub_tile(self, title: str, desc: str, icon: str, color_hex: str, callback) -> ModernCard:
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

    def create_timetable_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(18)

        header = PageHeader(
            "Weekly Class Timetable Manager",
            "Period-wise schedule matrix across Monday through Friday"
        )
        btn_save = theme.create_primary_button("💾 Save Timetable")
        btn_save.setFixedHeight(38)
        btn_save.clicked.connect(self.save_current_timetable)
        header.add_action(btn_save)

        layout.addWidget(header)

        # Class Selector Bar Card
        bar_card = ModernCard()
        b_lay = QHBoxLayout(bar_card)
        b_lay.setContentsMargins(20, 14, 20, 14)
        b_lay.setSpacing(14)
        b_lay.addStretch()

        cls_lbl = QLabel("Class Grade:")
        cls_lbl.setFont(theme.font_bold())
        b_lay.addWidget(cls_lbl)

        self.class_selector = QComboBox()
        self.class_selector.addItems([f"Class {i}" for i in range(1, 11)])
        self.class_selector.setFixedWidth(130)
        self.class_selector.currentIndexChanged.connect(self.load_timetable_for_class)
        b_lay.addWidget(self.class_selector)

        b_lay.addSpacing(24)

        self.timetable_status_badge = StatusBadge("✏️ Click any cell to edit subject", "neutral")
        b_lay.addWidget(self.timetable_status_badge)

        b_lay.addStretch()

        layout.addWidget(bar_card)

        # Timetable Table Card
        table_card = ModernCard()
        t_lay = QVBoxLayout(table_card)
        t_lay.setContentsMargins(16, 16, 16, 16)

        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.periods = [
            "Period 1\n(08:30 - 09:15 AM)",
            "Period 2\n(09:15 - 10:00 AM)",
            "Period 3\n(10:00 - 10:45 AM)",
            "Period 4\n(11:00 - 11:45 AM)",
            "Period 5\n(11:45 - 12:30 PM)",
            "Period 6\n(12:30 - 01:15 PM)",
        ]

        self.timetable_table = QTableWidget(len(self.days), len(self.periods))
        self.timetable_table.setVerticalHeaderLabels(self.days)
        self.timetable_table.setHorizontalHeaderLabels(self.periods)
        self.timetable_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.timetable_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.timetable_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.timetable_table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.timetable_table.verticalHeader().setDefaultSectionSize(54)
        self.timetable_table.setMinimumHeight(380)
        self.timetable_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        t_lay.addWidget(self.timetable_table)

        layout.addWidget(table_card)

        self.load_timetable_for_class()
        return widget

    def load_timetable_for_class(self):
        cls = self.class_selector.currentText().replace("Class ", "")
        key = f"timetable_class_{cls}"
        raw = db.get_app_data(key, "")

        if hasattr(self, "timetable_status_badge"):
            self.timetable_status_badge.setText("✏️ Click any cell to edit subject")
            self.timetable_status_badge.setStyleSheet(f"""
                QFrame {{
                    background-color: {theme.SURFACE_MUTED};
                    border: 1px solid {theme.BORDER_COLOR};
                    border-radius: 6px;
                    padding: 4px 12px;
                }}
                QLabel {{
                    color: {theme.TEXT_SECONDARY};
                    font-weight: 700;
                    font-size: 11.5px;
                }}
            """)

        data = {}
        if raw:
            try:
                data = json.loads(raw)
            except Exception:
                data = {}

        default_subjects = ["English", "Mathematics", "Science", "Urdu", "Computer", "Islamiat"]

        for r, day in enumerate(self.days):
            day_data = data.get(day, [])
            for c, period in enumerate(self.periods):
                val = day_data[c] if c < len(day_data) else default_subjects[(r + c) % len(default_subjects)]
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                self.timetable_table.setItem(r, c, item)

    def save_current_timetable(self):
        cls = self.class_selector.currentText().replace("Class ", "")
        key = f"timetable_class_{cls}"

        data = {}
        for r, day in enumerate(self.days):
            row_items = []
            for c in range(len(self.periods)):
                it = self.timetable_table.item(r, c)
                row_items.append(it.text().strip() if it else "")
            data[day] = row_items

        db.save_app_data(key, json.dumps(data))
        if hasattr(self, "timetable_status_badge"):
            self.timetable_status_badge.setText(f"✓ Class {cls} Timetable Saved Successfully!")
            self.timetable_status_badge.setStyleSheet(f"""
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
