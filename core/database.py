"""
Database Helper using SQLite for School Management System.
Connects directly to school.db, preserves all tables, and handles CRUD operations.
"""
import os
import sqlite3
import random
import json
from datetime import datetime
from typing import List, Optional, Tuple, Dict
from core.models import Student, Staff, TeacherReminder

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "school.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database() -> None:
    """Ensure all required tables and default master admin account exist."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # 1. Students Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                admissionNo TEXT PRIMARY KEY, firstName TEXT, middleName TEXT, lastName TEXT,
                age INTEGER, fatherName TEXT, bloodGroup TEXT, cnic TEXT, className TEXT,
                address TEXT, contact TEXT, prevInstitution TEXT, notes TEXT, photoPath TEXT,
                status TEXT, admissionDate TEXT
            )
        """)

        # 2. Staff Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS staff (
                staffId TEXT PRIMARY KEY, firstName TEXT, middleName TEXT, lastName TEXT,
                fatherName TEXT, staffType TEXT, designation TEXT, contact TEXT, email TEXT,
                address TEXT, bloodGroup TEXT, qualification TEXT, experience TEXT, notes TEXT,
                photoPath TEXT, salary REAL, joinDate TEXT, status TEXT, assignedClass TEXT, documents TEXT
            )
        """)

        # 3. Application Data Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS application_data (
                key TEXT PRIMARY KEY, value TEXT
            )
        """)

        # 4. Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY, password TEXT, role TEXT, staff_id TEXT
            )
        """)

        # 5. Student Attendance Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_attendance (
                date TEXT, admissionNo TEXT, status TEXT, PRIMARY KEY(date, admissionNo)
            )
        """)

        # 6. Teacher Reminders Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teacher_reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT, staffId TEXT, title TEXT, description TEXT,
                dueDate TEXT, priority TEXT, type TEXT, status TEXT
            )
        """)

        # 7. Teaching Assignments Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teaching_assignments (
                staffId TEXT, className TEXT, subjectName TEXT, PRIMARY KEY(staffId, className, subjectName)
            )
        """)

        # 8. Quizzes Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT, className TEXT, subjectName TEXT, title TEXT, maxMarks REAL, date TEXT
            )
        """)

        # 9. Quiz Marks Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_marks (
                quizId INTEGER, admissionNo TEXT, marksObtained REAL, PRIMARY KEY(quizId, admissionNo)
            )
        """)

        # 10. Assignments Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT, className TEXT, subjectName TEXT, title TEXT, maxMarks REAL, dueDate TEXT
            )
        """)

        # 11. Assignment Marks Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignment_marks (
                assignmentId INTEGER, admissionNo TEXT, marksObtained REAL, PRIMARY KEY(assignmentId, admissionNo)
            )
        """)

        # 12. Academic Promotion History & Audit Trail Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS promotion_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admissionNo TEXT,
                studentName TEXT,
                fromClass TEXT,
                toClass TEXT,
                totalScore REAL,
                maxScore REAL,
                percentage REAL,
                resultStatus TEXT,
                promotionDecision TEXT,
                academicSession TEXT,
                timestamp TEXT
            )
        """)

        # Ensure Master Admin account exists
        cursor.execute("SELECT count(*) FROM users WHERE staff_id = 'MASTER'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO users VALUES('shahikhanio1', 'shahidzahoorkhan', 'ADMIN', 'MASTER')")

        conn.commit()


# --- AUTHENTICATION & CREDENTIALS ---

def authenticate(username: str, password: str) -> Optional[Tuple[str, str]]:
    """Authenticates username and password against users table. Returns (role, staff_id) or None."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role, staff_id FROM users WHERE username = ? AND password = ?", (username, password))
        row = cursor.fetchone()
        if row:
            return (row["role"], row["staff_id"])
    return None


def get_master_admin_credentials() -> Tuple[str, str]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM users WHERE staff_id = 'MASTER' LIMIT 1")
        row = cursor.fetchone()
        if row:
            return (row["username"], row["password"])
    return ("shahikhanio1", "shahidzahoorkhan")


def update_master_admin(new_username: str, new_password: str) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET username = ?, password = ? WHERE staff_id = 'MASTER'", (new_username, new_password))
        if cursor.rowcount == 0:
            cursor.execute("INSERT INTO users VALUES(?, ?, 'ADMIN', 'MASTER')", (new_username, new_password))
        conn.commit()


# --- STUDENT OPERATIONS ---

def get_all_students() -> List[Student]:
    students = []
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")
        for row in cursor.fetchall():
            students.append(Student(
                admission_no=str(row["admissionNo"] or ""),
                first_name=str(row["firstName"] or ""),
                middle_name=str(row["middleName"] or ""),
                last_name=str(row["lastName"] or ""),
                age=int(row["age"] or 0),
                father_name=str(row["fatherName"] or ""),
                blood_group=str(row["bloodGroup"] or ""),
                cnic=str(row["cnic"] or ""),
                class_name=str(row["className"] or "1"),
                address=str(row["address"] or ""),
                contact=str(row["contact"] or ""),
                prev_institution=str(row["prevInstitution"] or ""),
                notes=str(row["notes"] or ""),
                photo_path=str(row["photoPath"] or ""),
                status=str(row["status"] or "ENROLLED"),
                admission_date=str(row["admissionDate"] or "")
            ))
    return students


def save_student(s: Student) -> None:
    sql = """
        INSERT OR REPLACE INTO students 
        (admissionNo, firstName, middleName, lastName, age, fatherName, bloodGroup, cnic, 
         className, address, contact, prevInstitution, notes, photoPath, status, admissionDate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (
            s.admission_no, s.first_name, s.middle_name, s.last_name, s.age,
            s.father_name, s.blood_group, s.cnic, s.class_name, s.address,
            s.contact, s.prev_institution, s.notes, s.photo_path, s.status, s.admission_date
        ))
        conn.commit()


def delete_student(admission_no: str) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE admissionNo = ?", (admission_no,))
        conn.commit()


def bulk_promote_students(promotions: List[Tuple[str, str, str]]) -> int:
    """
    Executes bulk student class and status updates in a single atomic transaction.
    promotions: List of (admission_no, new_class_name, new_status)
    Returns: Number of updated records.
    """
    if not promotions:
        return 0
    with get_connection() as conn:
        cursor = conn.cursor()
        for adm_no, new_class, new_status in promotions:
            cursor.execute(
                "UPDATE students SET className = ?, status = ? WHERE admissionNo = ?",
                (new_class, new_status, adm_no)
            )
        conn.commit()
        return len(promotions)


def log_promotion_history(records: List[Dict]) -> None:
    """
    Inserts audit trail records into promotion_history.
    Each record: {admissionNo, studentName, fromClass, toClass, totalScore, maxScore, percentage, resultStatus, promotionDecision, academicSession, timestamp}
    """
    if not records:
        return
    with get_connection() as conn:
        cursor = conn.cursor()
        for r in records:
            ts = r.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                """
                INSERT INTO promotion_history (
                    admissionNo, studentName, fromClass, toClass, totalScore, maxScore,
                    percentage, resultStatus, promotionDecision, academicSession, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    r.get("admissionNo", ""),
                    r.get("studentName", ""),
                    str(r.get("fromClass", "")),
                    str(r.get("toClass", "")),
                    float(r.get("totalScore", 0.0)),
                    float(r.get("maxScore", 600.0)),
                    float(r.get("percentage", 0.0)),
                    r.get("resultStatus", "PASSED"),
                    r.get("promotionDecision", "Promoted"),
                    r.get("academicSession", "2025-2026"),
                    ts
                )
            )
        conn.commit()


def get_promotion_history(admission_no: Optional[str] = None, session: Optional[str] = None, limit: int = 500) -> List[Dict]:
    """Retrieves promotion audit trail records, optionally filtered by admissionNo or session."""
    history = []
    with get_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM promotion_history"
        params = []
        conditions = []
        if admission_no:
            conditions.append("admissionNo = ?")
            params.append(admission_no)
        if session:
            conditions.append("academicSession = ?")
            params.append(session)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += f" ORDER BY id DESC LIMIT {limit}"
        cursor.execute(query, params)
        for row in cursor.fetchall():
            history.append({
                "id": row["id"],
                "admissionNo": row["admissionNo"],
                "studentName": row["studentName"],
                "fromClass": row["fromClass"],
                "toClass": row["toClass"],
                "totalScore": row["totalScore"],
                "maxScore": row["maxScore"],
                "percentage": row["percentage"],
                "resultStatus": row["resultStatus"],
                "promotionDecision": row["promotionDecision"],
                "academicSession": row["academicSession"],
                "timestamp": row["timestamp"]
            })
    return history


def revert_student_promotion(admission_no: str, target_class: str, target_status: str) -> bool:
    """Reverts a student's class and status (for administrative grade correction)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE students SET className = ?, status = ? WHERE admissionNo = ?",
            (target_class, target_status, admission_no)
        )
        conn.commit()
        return cursor.rowcount > 0


def get_progression_policy() -> Dict:
    """Returns the institutional automated progression policy settings."""
    raw = get_app_data("progression_policy", "")
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            pass
    return {
        "auto_promotion_enabled": True,
        "min_passing_pct": 50.0,
        "min_subject_pct": 40.0,
        "auto_graduate_alumni": True,
        "academic_session": "2025-2026"
    }


def save_progression_policy(policy: Dict) -> None:
    """Persists the automated progression policy."""
    save_app_data("progression_policy", json.dumps(policy))


# --- STAFF OPERATIONS ---

def get_all_staff() -> List[Staff]:
    staff_list = []
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM staff")
        for row in cursor.fetchall():
            staff_list.append(Staff(
                staff_id=str(row["staffId"] or ""),
                first_name=str(row["firstName"] or ""),
                middle_name=str(row["middleName"] or ""),
                last_name=str(row["lastName"] or ""),
                father_name=str(row["fatherName"] or ""),
                staff_type=str(row["staffType"] or ""),
                designation=str(row["designation"] or ""),
                contact=str(row["contact"] or ""),
                email=str(row["email"] or ""),
                address=str(row["address"] or ""),
                blood_group=str(row["bloodGroup"] or ""),
                qualification=str(row["qualification"] or ""),
                experience=str(row["experience"] or ""),
                notes=str(row["notes"] or ""),
                photo_path=str(row["photoPath"] or ""),
                salary=float(row["salary"] or 0.0),
                join_date=str(row["joinDate"] or ""),
                status=str(row["status"] or "ACTIVE"),
                assigned_class=str(row["assignedClass"] or ""),
                documents=str(row["documents"] or "")
            ))
    return staff_list


def save_staff(s: Staff) -> None:
    sql = """
        INSERT OR REPLACE INTO staff 
        (staffId, firstName, middleName, lastName, fatherName, staffType, designation, contact,
         email, address, bloodGroup, qualification, experience, notes, photoPath, salary,
         joinDate, status, assignedClass, documents)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (
            s.staff_id, s.first_name, s.middle_name, s.last_name, s.father_name,
            s.staff_type, s.designation, s.contact, s.email, s.address,
            s.blood_group, s.qualification, s.experience, s.notes, s.photo_path,
            s.salary, s.join_date, s.status, s.assigned_class, s.documents
        ))
        conn.commit()


def delete_staff(staff_id: str) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM staff WHERE staffId = ?", (staff_id,))
        cursor.execute("DELETE FROM users WHERE staff_id = ?", (staff_id,))
        cursor.execute("DELETE FROM teaching_assignments WHERE staffId = ?", (staff_id,))
        conn.commit()


def generate_random_staff_id() -> str:
    """Generate ID matching AAA111 format."""
    letters = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3))
    digits = "".join(random.choices("0123456789", k=3))
    return f"{letters}{digits}"


# --- ATTENDANCE OPERATIONS ---

def get_attendance_for_class(date_str: str, class_name: str) -> Dict[str, str]:
    """Returns {admissionNo: status} for a given date and class."""
    attendance = {}
    with get_connection() as conn:
        cursor = conn.cursor()
        sql = """
            SELECT sa.admissionNo, sa.status 
            FROM student_attendance sa
            JOIN students s ON sa.admissionNo = s.admissionNo
            WHERE sa.date = ? AND s.className = ?
        """
        cursor.execute(sql, (date_str, class_name))
        for row in cursor.fetchall():
            attendance[row["admissionNo"]] = row["status"]
    return attendance


def save_student_attendance(date_str: str, admission_no: str, status: str) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO student_attendance (date, admissionNo, status) VALUES (?, ?, ?)",
            (date_str, admission_no, status)
        )
        conn.commit()


# --- QUIZZES & MARKS ---

def get_quizzes(class_name: str, subject_name: str) -> List[Dict]:
    quizzes = []
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM quizzes WHERE className = ? AND subjectName = ? ORDER BY date DESC",
            (class_name, subject_name)
        )
        for row in cursor.fetchall():
            quizzes.append({
                "id": row["id"],
                "className": row["className"],
                "subjectName": row["subjectName"],
                "title": row["title"],
                "maxMarks": float(row["maxMarks"] or 0.0),
                "date": row["date"]
            })
    return quizzes


def save_quiz(class_name: str, subject_name: str, title: str, max_marks: float, date_str: str) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO quizzes (className, subjectName, title, maxMarks, date) VALUES (?, ?, ?, ?, ?)",
            (class_name, subject_name, title, max_marks, date_str)
        )
        conn.commit()
        return cursor.lastrowid


def delete_quiz(quiz_id: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
        cursor.execute("DELETE FROM quiz_marks WHERE quizId = ?", (quiz_id,))
        conn.commit()


def get_quiz_marks(quiz_id: int) -> Dict[str, float]:
    marks = {}
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT admissionNo, marksObtained FROM quiz_marks WHERE quizId = ?", (quiz_id,))
        for row in cursor.fetchall():
            marks[row["admissionNo"]] = float(row["marksObtained"] or 0.0)
    return marks


def save_quiz_marks(quiz_id: int, marks_dict: Dict[str, float]) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        for adm, mark in marks_dict.items():
            cursor.execute(
                "INSERT OR REPLACE INTO quiz_marks (quizId, admissionNo, marksObtained) VALUES (?, ?, ?)",
                (quiz_id, adm, mark)
            )
        conn.commit()


# --- ASSIGNMENTS & MARKS ---

def get_assignments(class_name: str, subject_name: str) -> List[Dict]:
    assignments = []
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM assignments WHERE className = ? AND subjectName = ? ORDER BY dueDate DESC",
            (class_name, subject_name)
        )
        for row in cursor.fetchall():
            assignments.append({
                "id": row["id"],
                "className": row["className"],
                "subjectName": row["subjectName"],
                "title": row["title"],
                "maxMarks": float(row["maxMarks"] or 0.0),
                "dueDate": row["dueDate"]
            })
    return assignments


def save_assignment(class_name: str, subject_name: str, title: str, max_marks: float, due_date: str) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO assignments (className, subjectName, title, maxMarks, dueDate) VALUES (?, ?, ?, ?, ?)",
            (class_name, subject_name, title, max_marks, due_date)
        )
        conn.commit()
        return cursor.lastrowid


def delete_assignment(assignment_id: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM assignments WHERE id = ?", (assignment_id,))
        cursor.execute("DELETE FROM assignment_marks WHERE assignmentId = ?", (assignment_id,))
        conn.commit()


def get_assignment_marks(assignment_id: int) -> Dict[str, float]:
    marks = {}
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT admissionNo, marksObtained FROM assignment_marks WHERE assignmentId = ?", (assignment_id,))
        for row in cursor.fetchall():
            marks[row["admissionNo"]] = float(row["marksObtained"] or 0.0)
    return marks


def save_assignment_marks(assignment_id: int, marks_dict: Dict[str, float]) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        for adm, mark in marks_dict.items():
            cursor.execute(
                "INSERT OR REPLACE INTO assignment_marks (assignmentId, admissionNo, marksObtained) VALUES (?, ?, ?)",
                (assignment_id, adm, mark)
            )
        conn.commit()


# --- REMINDERS ---

def get_reminders(staff_id: Optional[str] = None) -> List[TeacherReminder]:
    reminders = []
    with get_connection() as conn:
        cursor = conn.cursor()
        if staff_id and staff_id not in ("MASTER", "ADMIN", ""):
            cursor.execute("SELECT * FROM teacher_reminders WHERE staffId = ? ORDER BY dueDate ASC", (staff_id,))
        else:
            cursor.execute("SELECT * FROM teacher_reminders ORDER BY dueDate ASC")
        for row in cursor.fetchall():
            reminders.append(TeacherReminder(
                id=int(row["id"]),
                staff_id=str(row["staffId"] or "MASTER"),
                title=str(row["title"] or ""),
                description=str(row["description"] or ""),
                due_date=str(row["dueDate"] or ""),
                priority=str(row["priority"] or "Medium"),
                reminder_type=str(row["type"] or "General"),
                status=str(row["status"] or "Pending")
            ))
    return reminders


def save_reminder(r: TeacherReminder) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        if r.id == 0:
            cursor.execute(
                "INSERT INTO teacher_reminders (staffId, title, description, dueDate, priority, type, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (r.staff_id, r.title, r.description, r.due_date, r.priority, r.reminder_type, r.status)
            )
            r.id = cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE teacher_reminders SET staffId = ?, title = ?, description = ?, dueDate = ?, priority = ?, type = ?, status = ? WHERE id = ?",
                (r.staff_id, r.title, r.description, r.due_date, r.priority, r.reminder_type, r.status, r.id)
            )
        conn.commit()
        return r.id


def update_reminder_status(reminder_id: int, status: str) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE teacher_reminders SET status = ? WHERE id = ?", (status, reminder_id))
        conn.commit()


def delete_reminder(reminder_id: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM teacher_reminders WHERE id = ?", (reminder_id,))
        conn.commit()


# --- TEACHING ASSIGNMENTS ---

DEFAULT_CLASSES = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
DEFAULT_SUBJECTS = ["English", "Mathematics", "Science", "Urdu", "Computer", "Islamiat"]


def get_teaching_assignments(staff_id: Optional[str] = None) -> List[Tuple[str, str]]:
    """Returns list of (className, subjectName). Defaults to all combinations if none assigned."""
    assignments = []
    with get_connection() as conn:
        cursor = conn.cursor()
        if staff_id and staff_id not in ("MASTER", "ADMIN", ""):
            cursor.execute("SELECT className, subjectName FROM teaching_assignments WHERE staffId = ?", (staff_id,))
        else:
            cursor.execute("SELECT DISTINCT className, subjectName FROM teaching_assignments ORDER BY className, subjectName")
        for row in cursor.fetchall():
            assignments.append((row["className"], row["subjectName"]))

    if not assignments and (not staff_id or staff_id in ("MASTER", "ADMIN", "")):
        for c in DEFAULT_CLASSES:
            for s in DEFAULT_SUBJECTS:
                assignments.append((c, s))
    return assignments


def save_teaching_assignment(staff_id: str, class_name: str, subject_name: str) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO teaching_assignments (staffId, className, subjectName) VALUES (?, ?, ?)",
            (staff_id, class_name, subject_name)
        )
        conn.commit()


def delete_teaching_assignment(staff_id: str, class_name: str, subject_name: str) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM teaching_assignments WHERE staffId = ? AND className = ? AND subjectName = ?",
            (staff_id, class_name, subject_name)
        )
        conn.commit()


# --- APPLICATION CONFIG & DATA STORE ---

def get_app_data(key: str, default: Optional[str] = None) -> Optional[str]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM application_data WHERE key = ?", (key,))
        row = cursor.fetchone()
        if row:
            return row["value"]
    return default


def save_app_data(key: str, value: str) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO application_data VALUES (?, ?)", (key, value))
        conn.commit()


# --- 360° PROFILE DATA AGGREGATION HELPERS ---

def get_student_attendance_history(admission_no: str) -> List[Dict[str, str]]:
    """Returns chronological attendance records for a student."""
    records = []
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT date, status FROM student_attendance WHERE admissionNo = ? ORDER BY date DESC",
            (admission_no,)
        )
        for row in cursor.fetchall():
            records.append({"date": str(row["date"]), "status": str(row["status"])})
    return records


def get_student_fee_ledger(admission_no: str) -> List[Dict]:
    """Aggregates monthly tuition, lab, sports, utilities, status, and payment timestamps for student."""
    ledger = []
    tuition = float(get_app_data("fee_tuition", "5000"))
    it_lab = float(get_app_data("fee_itlab", "1000"))
    sports = float(get_app_data("fee_sports", "800"))
    utilities = float(get_app_data("fee_utilities", "700"))
    total_monthly = tuition + it_lab + sports + utilities
    due_day = int(get_app_data("fee_dueDay", "10"))

    prefix = f"fee_status_{admission_no}_"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT key, value FROM application_data WHERE key LIKE ? ORDER BY key DESC",
            (f"{prefix}%",)
        )
        rows = cursor.fetchall()
        for r in rows:
            k = r["key"]
            status = r["value"]
            month_part = k[len(prefix):]
            pay_date = get_app_data(f"fee_date_{admission_no}_{month_part}", "-")
            try:
                parts = month_part.split("_")
                formatted_month = datetime(int(parts[0]), int(parts[1]), 1).strftime("%B %Y")
                due_date = f"{parts[0]}-{parts[1]}-{due_day:02d}"
            except Exception:
                formatted_month = month_part
                due_date = f"{month_part}-{due_day:02d}"

            ledger.append({
                "month_key": month_part,
                "month_label": formatted_month,
                "tuition": tuition,
                "it_lab": it_lab,
                "sports": sports,
                "utilities": utilities,
                "total": total_monthly,
                "due_date": due_date,
                "status": status,
                "paid_date": pay_date
            })

    if not ledger:
        now = datetime.now()
        for i in range(3):
            y = now.year
            m = now.month - i
            if m <= 0:
                m += 12
                y -= 1
            m_key = f"{y}_{m:02d}"
            m_label = datetime(y, m, 1).strftime("%B %Y")
            st = get_app_data(f"fee_status_{admission_no}_{m_key}", "Paid" if i > 0 else "Pending")
            p_date = get_app_data(f"fee_date_{admission_no}_{m_key}", f"{y}-{m:02d}-05" if st == "Paid" else "-")
            ledger.append({
                "month_key": m_key,
                "month_label": m_label,
                "tuition": tuition,
                "it_lab": it_lab,
                "sports": sports,
                "utilities": utilities,
                "total": total_monthly,
                "due_date": f"{y}-{m:02d}-{due_day:02d}",
                "status": st,
                "paid_date": p_date
            })
    return ledger


def get_student_exam_history(admission_no: str, class_name: Optional[str] = None) -> List[Dict]:
    """Extracts subject-wise marks, totals, percentages, letter grades, and statuses across examination terms."""
    history = []
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM application_data WHERE key LIKE 'exam_results_%'")
        rows = cursor.fetchall()
        for r in rows:
            key = r["key"]
            parts = key.split("_", 3)
            if len(parts) >= 4:
                cls = parts[2]
                term = parts[3]
            elif len(parts) == 3:
                cls = parts[2]
                term = "General Exam"
            else:
                continue

            if class_name and cls != class_name:
                continue

            try:
                data = json.loads(r["value"] or "{}")
                if admission_no in data:
                    subject_scores = data[admission_no]
                    tot = sum(subject_scores.values()) if subject_scores else 0.0
                    max_marks = len(subject_scores) * 100.0 if subject_scores else 600.0
                    pct = (tot / max_marks * 100.0) if max_marks > 0 else 0.0
                    if pct >= 90:
                        grade = "A+"
                    elif pct >= 80:
                        grade = "A"
                    elif pct >= 70:
                        grade = "B"
                    elif pct >= 60:
                        grade = "C"
                    elif pct >= 50:
                        grade = "D"
                    else:
                        grade = "F"
                    status = "Passed" if pct >= 50.0 else "Failed"
                    history.append({
                        "class_name": cls,
                        "term": term,
                        "subjects": subject_scores,
                        "total": tot,
                        "max_marks": max_marks,
                        "percentage": pct,
                        "grade": grade,
                        "status": status
                    })
            except Exception:
                pass
    return sorted(history, key=lambda x: (x["class_name"], x["term"]))


def get_staff_payroll_history(staff_id: str, monthly_salary: float) -> List[Dict]:
    """Compiles historical monthly salary disbursement entries, amounts, and statuses for staff."""
    payroll = []
    now = datetime.now()
    for i in range(6):
        y = now.year
        m = now.month - i
        if m <= 0:
            m += 12
            y -= 1
        m_key = f"{y}_{m:02d}"
        m_label = datetime(y, m, 1).strftime("%B %Y")
        key = f"payroll_status_{staff_id}_{m_key}"
        status = get_app_data(key, "Disbursed" if i > 0 else "Pending")
        disbursed_date = f"{y}-{m:02d}-28" if status == "Disbursed" else "-"
        payroll.append({
            "month_key": m_key,
            "month_label": m_label,
            "salary": monthly_salary,
            "allowances": 0.0,
            "net_payable": monthly_salary,
            "status": status,
            "disbursed_date": disbursed_date
        })
    return payroll
