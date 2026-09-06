import json
from pathlib import Path
from typing import Any, cast

import pandas as pd

from data_model import SchoolClass, Score, Student


def build_data_model(
    source_1: pd.DataFrame, source_2: pd.DataFrame, output_dir: Path
) -> tuple[dict[str, Student], dict[str, SchoolClass]]:
    students: dict[str, Student] = {}
    schoolclasses: dict[str, SchoolClass] = {}

    for row in source_1.itertuples(index=False):
        # Extracting school class information from the current row
        schoolclass_group = cast(str, row.groep)
        schoolclass_year = cast(str, row.schooljaar)
        schoolclass_key = f"{schoolclass_group}_{schoolclass_year}"

        # Check if the school class already exists in the dictionary. If not, create a new entry
        if schoolclass_key not in schoolclasses:
            schoolclasses[schoolclass_key] = SchoolClass(
                class_name=schoolclass_group,
                schoolyear=schoolclass_year,
                date_start=pd.to_datetime(
                    cast(str, row.latest_toewijzing_ingangsdatum)
                ).to_pydatetime(),
                date_end=pd.to_datetime(
                    cast(str, row.latest_toewijzing_einddatum)
                ).to_pydatetime(),
                students=[],
            )

        # Extracting student information from the current row
        student_name = cast(str, row.leerling)
        student_date_of_birth = pd.to_datetime(
            cast(str, row.geboortedatum)
        ).to_pydatetime()
        student_gender = cast(str, row.geslacht)
        student_key = f"{student_name}_{student_date_of_birth.strftime('%Y-%m-%d')}"

        # If the student is not already in the dictionary, create a new Student object
        if student_key not in students:
            students[student_key] = Student(
                name=student_name,
                date_of_birth=student_date_of_birth,
                gender=student_gender,
                school_class=[],
                scores=[],
            )

        # Adding the schoolclasses to the student's record
        students[student_key].school_class.append(schoolclass_key)
        schoolclasses[schoolclass_key].students.append(student_key)

    unmatched_score_rows: list[dict[str, Any]] = []
    # for row in source_2.itertuples(index=False):
    for i in range(len(source_2)):
        row = source_2.iloc[i]

        # Creating a Score object from the current row in source_2
        score = Score(
            group=cast(str, row.groep),
            student_name=cast(str, row.leerling),
            subject=cast(str, row.vak),
            value=float(cast(float, row.cijfer)),
            teacher=cast(str, row.leerkracht),
            date=pd.to_datetime(cast(str, row.datum), dayfirst=True).to_pydatetime(),
        )

        # Attempt to match the score to a student in the existing data model
        student_key = match_score_to_student(score, students, schoolclasses)

        # If a matching student is found, append the score to their record; otherwise, add it to unmatched_scores
        if student_key is not None:
            students[student_key].scores.append(score)
        else:
            unmatched_score_rows.append(
                dict(zip(source_2.columns.tolist(), row, strict=True))
            )

    unmatched_scores = pd.DataFrame(unmatched_score_rows, columns=source_2.columns)

    print(
        f"There are {len(unmatched_scores)} unmatched scores ({len(unmatched_scores) / len(source_2) * 100:.1f}%)."
    )

    # Save unmatched scores to a JSON or CSV file in the specified output directory
    with open(output_dir / "datamodel_students.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                student_key: student.to_dict()
                for student_key, student in students.items()
            },
            f,
            ensure_ascii=False,
            indent=4,
        )

    with open(output_dir / "datamodel_schoolclasses.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                schoolclass_key: schoolclass.to_dict()
                for schoolclass_key, schoolclass in schoolclasses.items()
            },
            f,
            ensure_ascii=False,
            indent=4,
        )

    unmatched_scores.to_csv(
        output_dir / "datamodel_unmatched_scores.csv", index=False, encoding="utf-8"
    )

    return students, schoolclasses


def match_score_to_student(
    score: Score, students: dict[str, Student], schoolclasses: dict[str, SchoolClass]
) -> str | None:
    # Normalize the student's name and group for comparison purposes
    normalized_score_name = " ".join(score.student_name.split()).casefold()
    normalized_score_group = " ".join(score.group.split()).casefold()

    # List to store keys of students that match the current score
    matching_student_keys: list[str] = []

    for student_key, student in students.items():
        # Normalize the student's name for comparison purposes
        normalized_student_name = " ".join(student.name.split()).casefold()

        # Skip this student if the normalized names do not match
        if normalized_student_name != normalized_score_name:
            continue

        for schoolclass_key in student.school_class:
            # Normalize the school class's group name for comparison purposes
            schoolclass = schoolclasses[schoolclass_key]
            normalized_group = " ".join(schoolclass.class_name.split()).casefold()

            # Check if the normalized group matches and the score date falls within the school class date range
            if (
                normalized_group == normalized_score_group
                and schoolclass.date_start <= score.date <= schoolclass.date_end
            ):
                matching_student_keys.append(student_key)
                break

    # If there is exactly one matching student, return their key; otherwise, return None
    if len(matching_student_keys) == 1:
        return matching_student_keys[0]

    return None
