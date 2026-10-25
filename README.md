# Edura — Unified School Management System

> **Intelligent Campus Administration, Academic Progression & Student Information System**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-PySide6%20%2F%20Qt6-41CD52.svg?style=flat&logo=qt&logoColor=white)](https://wiki.qt.io/Qt_for_Python)
[![Database](https://img.shields.io/badge/Database-SQLite3-003B57.svg?style=flat&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![Architecture](https://img.shields.io/badge/Architecture-100%25%20Single--Window-8B5CF6.svg?style=flat)](#architectural-principles)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg?style=flat)](#license)

**Edura** is an enterprise-grade desktop School Management System designed for modern educational institutions (K–10 / Primary through High School). Built natively with Python and PySide6 (Qt6), Edura unifies admissions, academics, staff management, timetables, examinations, bulk promotions, daily attendance, fee accounting, and institutional audits into an elegant, responsive desktop workspace.

---

## Table of Contents
1. [Architectural Principles](#architectural-principles)
2. [Core Modules & Features](#core-modules--features)
   - [Executive Dashboard](#1-executive-dashboard)
   - [Student Information System (SIS)](#2-student-information-system-sis)
   - [Faculty & Staff Management](#3-faculty--staff-management)
   - [Academics & Timetable Manager](#4-academics--timetable-manager)
   - [Examinations, Results & Report Cards](#5-examinations-results--report-cards)
   - [Year-End Bulk Student Promotion & Graduation](#6-year-end-bulk-student-promotion--graduation)
   - [Daily Attendance Register](#7-daily-attendance-register)
   - [Classroom Tools (Quizzes, Assignments, Reminders)](#8-classroom-tools)
   - [Finance & Accounts](#9-finance--accounts)
   - [Reports Center & Audits](#10-reports-center--audits)
   - [System Settings & IT Configuration](#11-system-settings--it-configuration)
3. [Technology Stack](#technology-stack)
4. [Installation & Getting Started](#installation--getting-started)
5. [Default Login Credentials](#default-login-credentials)
6. [Project File Structure](#project-file-structure)
7. [Database Persistence & Backups](#database-persistence--backups)
8. [License & Support](#license--support)

---

## Architectural Principles

* **Strict 100% Single-Window Architecture**: Zero popup OS dialogs or secondary floating windows. Form edits, teaching allocations, audit reports, report cards, and bulk progression workflows render directly within the in-page stack (`QStackedWidget`), maintaining window focus and keyboard accessibility.
* **Centered Responsive Headers**: Standardized 3-column layouts with mathematical width mirroring (`left_box.setFixedWidth(actions_widget.sizeHint().width())`) guarantee titles and subtitles remain dead-center across any monitor resolution or resize.
* **Preserved Form Integrity**: Multi-tab admission and registration headers maintain their specialized left-aligned layouts with live badges and status chips.
* **Full ADM Column Visibility**: Standardized 125px column widths across all student tables prevent truncation or ellipsis (`ADM-0002` is always completely visible and centered).
* **Keyboard-First Authentication**: Automatic focus transition from Username to Password on `Enter`, and direct submission on password `Enter`.
* **Atomic Database Transactions**: All batch operations (such as school-wide bulk promotions) run in atomic SQLite transactions to prevent partial updates or data corruption.

---

## Core Modules & Features

### 1. Executive Dashboard
* Real-time KPI Metric Cards displaying total enrolled students, faculty count, daily attendance percentages, and monthly fee collections.
* Quick-action shortcuts for rapid admissions, attendance marking, and fee voucher generation.
* Digital announcements and institutional reminders ticker.

### 2. Student Information System (SIS)
* **Admissions Form**: Comprehensive 4-tab registration card (Basic Info, Parent & Guardian Contacts, Academic Background, Medical & Emergency Notes) with student photograph upload.
* **Searchable Student Directory**: Search students by Admission Number, full name, or father's name with real-time class filters (Classes 1–10).
* **Class Browser**: Dedicated rosters per grade level with quick access to student fee status, records, and guardian details.
* **In-Page Record Editing**: Update student demographics, contact numbers, and status inline without leaving the directory view.

### 3. Faculty & Staff Management
* **Staff Directory**: Complete registry of academic teachers and administrative personnel with automated employee ID generation (`STF-001`, `STF-002`, etc.).
* **In-Page Registration**: Add faculty members with qualifications, designated department, joining date, and monthly salary.
* **Teaching Subject Allocations**: Dedicated in-window allocation matrix to assign faculty members to specific subjects and grade levels.

### 4. Academics & Timetable Manager
* **Weekly Timetable Manager**: Interactive 5-day (Monday to Friday), 6-period matrix.
* **Realistic Schedule Mapping**: Configured with standard school timings (`08:30 AM` to `01:45 PM`) including break intervals.
* **Class-by-Class Schedule Browser**: Dropdown selector to view and edit timetables for Classes 1 through 10.
* **In-Window Save Confirmation**: Instant status badges confirm timetable saves without intrusive alerts.
* **Curriculum & Syllabus**: Module tracking syllabus completion percentages across academic terms.

### 5. Examinations, Results & Report Cards
* **Term Evaluations**: Record marks across 1st Term, Mid-Years, and Annual Final Examinations.
* **Automatic Grade Calculation**: Computes percentage scores, letter grades ($A+$, $A$, $B$, $C$, $D$, $F$), and Pass/Fail statuses in real time.
* **Official Report Cards**: In-window transcript viewer displaying student subject performance, aggregate marks, attendance summary, and remarks with printable layout.

### 6. Year-End Bulk Student Promotion & Graduation
* **Automated Institutional Progression**:
  * **Classes 1–9**: Passing students ($\ge 50\%$) are automatically recommended for advancement to the next class level.
  * **Class 10**: Passing students ($\ge 50\%$) graduate and are transitioned to `ALUMNI` status, preserving records in archives while clearing active classroom registers.
  * **Failing Students ($< 50\%$)**: Flagged for retention in the same class for academic review.
* **Interactive Administrative Overrides**: School administrators can review the entire candidate matrix and override any recommendation (Promote, Retain, or Mark Transferred) via table comboboxes prior to execution.
* **Atomic Batch Execution**: Evaluates hundreds of students simultaneously and updates SQLite records within a single transaction.
* **In-Card Confirmation Banner**: Clear post-execution audit summarizing total promoted, graduated, and retained students.

### 7. Daily Attendance Register
* Daily attendance marking for students and staff with quick statuses (**Present**, **Absent**, **Late**, **Excused**).
* Real-time calculation of overall daily attendance percentage.
* Persistent historical attendance logs for compliance and reporting.

### 8. Classroom Tools
* **Quizzes Module**: Post quizzes, track submissions, and grade student assessments.
* **Homework Assignments**: Set homework tasks with submission deadlines and score evaluations.
* **Task Reminders Board**: Manage institutional deadlines, exams schedules, and administrative reminders.

### 9. Finance & Accounts
* **Class Fee Ledgers**: Track monthly tuition dues, paid vouchers, outstanding balances, and payment methods.
* **Billing Rates Policy**: Configurable class-wise tuition fee rates.
* **Institutional Margin Analysis**: Real-time KPI cards displaying projected monthly inflows vs. faculty payroll liabilities and net operating surplus.

### 10. Reports Center & Audits
* Dedicated in-page audit viewers:
  * **Student Audit Report**: Enrollment demographics and status breakdown.
  * **Faculty Payroll Report**: Department-wise salary allocations and total payroll liabilities.
  * **Attendance Audit**: Institutional attendance trends and absenteeism monitoring.
  * **Financial Audit**: Gross revenue potential, collections, and operating reserves.

### 11. System Settings & IT Configuration
* **Institutional Branding**: Customize School Name, Campus Logo/Emblem, Principal Contact, and Address.
* **Explicit Save Action**: Settings are only saved and applied when clicking the explicit **Save Changes** button.
* **Dynamic Global Propagation**: Updating the school name immediately refreshes the application window title, sidebar emblems, login card, report cards, and Help knowledge base across the entire app.

---

## Technology Stack

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ / 3.14 | Core application logic and data processing |
| **GUI Framework** | PySide6 (Qt 6.5+) | Modern desktop rendering, widgets, and animation |
| **Styling** | Qt Style Sheets (QSS) | Inter/Segoe UI typography, modern card elevation, and soft rounded styling |
| **Database** | SQLite3 | Embedded ACID-compliant database with relational schema |
| **Imaging** | Pillow (PIL) | Student and staff profile picture processing and emblem scaling |

---

## Installation & Getting Started

### Prerequisites
* **Python 3.10 or higher** installed on your system. Ensure Python is added to your system `PATH`.

### 1. Clone or Download the Repository
```bash
git clone https://github.com/shelby-io1/Edura-School-MS.git
cd "Edura-School-MS"
```

### 2. Set Up a Virtual Environment (Recommended)
```powershell
# Create virtual environment
python -m venv venv

# Activate on Windows PowerShell
.\venv\Scripts\Activate.ps1

# Activate on Command Prompt
.\venv\Scripts\activate.bat
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch the Application
You can start Edura directly using Python:
```powershell
python main.py
```
Or simply double-click the included batch launcher:
```powershell
run.bat
```

---

## Default Login Credentials

Upon the first launch, the SQLite database (`school.db`) automatically initializes with default administrative authority:

| Field | Value | Notes |
| :--- | :--- | :--- |
| **Username** | `admin` | Master administrative username |
| **Password** | `STF-001` | Default master password (case-sensitive) |
| **Access Level** | Singular Master Authority | Full institutional access across all modules |

> [!TIP]
> You can navigate the login card rapidly: enter `admin` and press **Enter** to jump immediately to the Password field, then press **Enter** again to sign in.

---

## Project File Structure

```
School MS/
├── assets/                       # UI assets, icons, and logo emblems
├── core/
│   ├── database.py               # SQLite schema, queries, authentication & atomic transactions
│   ├── models.py                 # Domain dataclasses (Student, Staff, FeeRecord, Timetable)
│   ├── theme.py                  # Global QSS stylesheet, colors, badges & typography
│   └── widgets.py                # Reusable UI components (ModernCard, PageHeader, MetricCard)
├── modules/
│   ├── academic_management.py    # Timetable manager & academic syllabus
│   ├── assignments_module.py     # Homework assignments & submissions
│   ├── attendance_module.py      # Daily student & faculty attendance register
│   ├── dashboard.py              # Executive KPI metrics and overview hub
│   ├── finance_management.py     # Fee ledgers, vouchers, billing rates & payroll
│   ├── help_module.py            # Knowledge base, documentation & IT support
│   ├── login.py                  # Singular master admin sign-in card
│   ├── quizzes_module.py         # Quizzes creation, grading & scoring
│   ├── reminders_module.py       # Administrative task reminders board
│   ├── reports_module.py         # Comprehensive audit reports (Students, Staff, Finance)
│   ├── results_module.py         # Examination marks, report cards & bulk promotion center
│   ├── settings_module.py        # Institutional settings, school branding & IT config
│   ├── staff_management.py       # Faculty directory, registration & teaching allocations
│   └── student_management.py     # Admissions, student directory & class rosters
├── main.py                       # Application entry point, QMainWindow shell & navigation
├── requirements.txt              # Python library dependencies
├── run.bat                       # One-click Windows desktop launcher
├── school.db                     # Embedded SQLite database
└── README.md                     # Comprehensive project documentation
```

---

## Database Persistence & Backups

All school data (students, faculty, academic marks, fee ledgers, and institutional configurations) is stored locally in the single embedded database file:
```
school.db
```

### How to Back Up:
1. Ensure the Edura application is closed.
2. Copy `school.db` to a secure external drive, cloud storage, or backup folder.
3. To restore on any computer, place `school.db` in the application root directory before launching.

---

## License & Support

* **Platform**: Edura — Unified School Management System
* **Principal Administrator**: Shahid Zahoor Khan
* **Hotline Support**: `+92 300 555-0199`
* **License**: Proprietary / Educational Institutional License. All rights reserved.
