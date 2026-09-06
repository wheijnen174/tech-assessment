import json
import statistics
from pathlib import Path
from typing import Any

import pandas as pd

from data_model import SchoolClass, Student


def students_per_group(
    students: dict[str, Student],
    schoolclasses: dict[str, SchoolClass],
    output_dir: Path,
) -> None:
    students_by_group: dict[str, list[str]] = {}

    for schoolclass in schoolclasses.values():
        schoolclass_name = f"{schoolclass.class_name} ({schoolclass.schoolyear})"

        students_by_group[schoolclass_name] = [
            students[student_key].name for student_key in schoolclass.students
        ]

    # Save the students by group to a JSON file
    with open(output_dir / "output_students_by_group.json", "w", encoding="utf-8") as f:
        json.dump(
            students_by_group,
            f,
            ensure_ascii=False,
            indent=4,
        )


def scores_per_group(
    students: dict[str, Student],
    schoolclasses: dict[str, SchoolClass],
    output_dir: Path,
) -> None:
    scores_by_group: dict[str, dict[str, float | None]] = {}

    for schoolclass in schoolclasses.values():
        # Collect the scores for each student in the class within the class date range
        all_scores_per_student = {
            student_key: [
                score.value
                for score in students[student_key].scores
                if score.date >= schoolclass.date_start
                and score.date <= schoolclass.date_end
            ]
            for student_key in schoolclass.students
        }

        # Calculate the average scores per student
        average_scores_per_student = {
            student_key: (statistics.fmean(scores) if scores else None)
            for student_key, scores in all_scores_per_student.items()
            if len(scores) > 0
        }

        # Calculate the average, median, and standard deviation for the class scores
        scores_by_group[f"{schoolclass.class_name} ({schoolclass.schoolyear})"] = {
            "Gemiddelde": round(
                statistics.fmean(average_scores_per_student.values()),  # type: ignore
                2,
            )
            if len(average_scores_per_student) > 0
            else None,
            "Mediaan": round(statistics.median(average_scores_per_student.values()), 2)  # type: ignore
            if len(average_scores_per_student) > 0
            else None,
            "Standaarddeviatie": round(
                statistics.stdev(average_scores_per_student.values()),  # type: ignore
                2,
            )
            if len(average_scores_per_student) > 1
            else None,
        }

    # Save the scores by group to a JSON file
    with open(output_dir / "output_scores_by_group.json", "w", encoding="utf-8") as f:
        json.dump(
            scores_by_group,
            f,
            ensure_ascii=False,
            indent=4,
        )


def generate_historical_data(
    students: dict[str, Student],
    schoolclasses: dict[str, SchoolClass],
    output_dir: Path,
) -> None:
    historical_data: list[dict[str, Any]] = []

    for student in students.values():
        for schoolclass_key in student.school_class:
            # Retrieve the school class object for the current schoolclass_key
            schoolclass = schoolclasses[schoolclass_key]

            # Calculate the age of the student at the start of the school year
            age_at_start_of_year = (
                schoolclass.date_start - student.date_of_birth
            ).days // 365

            # Retrieve the scores for the current class within the class period
            scores_this_class = [
                score.value
                for score in student.scores
                if score.date >= schoolclass.date_start
                and score.date <= schoolclass.date_end
            ]

            # Append the historical data for the current student and class
            historical_data.append(
                {
                    "Student_Name": student.name,
                    "Date_Of_Birth": student.date_of_birth,
                    "Gender": student.gender,
                    "Age": age_at_start_of_year,
                    "School_Year": schoolclass.schoolyear,
                    "Class_Name": schoolclass.class_name,
                    "Class_Period_Start": schoolclass.date_start,
                    "Class_Period_End": schoolclass.date_end,
                    "Average_Score": round(statistics.fmean(scores_this_class), 2)
                    if len(scores_this_class) > 0
                    else None,
                }
            )

    # Save the historical data to a CSV file
    pd.DataFrame(historical_data).to_csv(
        output_dir / "output_historical_data.csv",
        index=False,
        date_format="%Y-%m-%d",
        sep=";",
        decimal=",",
    )
