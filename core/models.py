"""
Domain models for the School Management System.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Student:
    admission_no: str
    first_name: str
    middle_name: str = ""
    last_name: str = ""
    age: int = 0
    father_name: str = ""
    blood_group: str = ""
    cnic: str = ""
    class_name: str = "1"
    address: str = ""
    contact: str = ""
    prev_institution: str = ""
    notes: str = ""
    photo_path: str = ""
    status: str = "ENROLLED"
    admission_date: str = ""

    def get_full_name(self) -> str:
        parts = [self.first_name, self.middle_name, self.last_name]
        return " ".join(p.strip() for p in parts if p and p.strip())


@dataclass
class Staff:
    staff_id: str
    first_name: str
    middle_name: str = ""
    last_name: str = ""
    father_name: str = ""
    staff_type: str = "Teaching Staff"
    designation: str = "Teacher"
    contact: str = ""
    email: str = ""
    address: str = ""
    blood_group: str = ""
    qualification: str = ""
    experience: str = ""
    notes: str = ""
    photo_path: str = ""
    salary: float = 0.0
    join_date: str = ""
    status: str = "ACTIVE"
    assigned_class: str = ""
    documents: str = ""

    def get_full_name(self) -> str:
        parts = [self.first_name, self.middle_name, self.last_name]
        return " ".join(p.strip() for p in parts if p and p.strip())


@dataclass
class TeacherReminder:
    id: int
    staff_id: str
    title: str
    description: str = ""
    due_date: str = ""
    priority: str = "Medium"
    reminder_type: str = "General"
    status: str = "Pending"
