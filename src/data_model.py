from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Student:
    name: str
    date_of_birth: datetime
    gender: str
    school_class: list[str]
    scores: list[Score]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "date_of_birth": self.date_of_birth.strftime("%Y-%m-%d"),
            "gender": self.gender,
            "school_class": self.school_class,
            "scores": [score.to_dict() for score in self.scores],
        }


@dataclass
class SchoolClass:
    class_name: str
    schoolyear: str
    date_start: datetime
    date_end: datetime
    students: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "class_name": self.class_name,
            "schoolyear": self.schoolyear,
            "date_start": self.date_start.strftime("%Y-%m-%d"),
            "date_end": self.date_end.strftime("%Y-%m-%d"),
            "students": self.students,
        }


@dataclass
class Score:
    group: str
    student_name: str
    subject: str
    value: float
    teacher: str
    date: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "group": self.group,
            "student_name": self.student_name,
            "subject": self.subject,
            "value": self.value,
            "teacher": self.teacher,
            "date": self.date.strftime("%Y-%m-%d"),
        }
