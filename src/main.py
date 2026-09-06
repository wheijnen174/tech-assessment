from pathlib import Path

from analysis import generate_historical_data, scores_per_group, students_per_group
from data_loader import load_source_1, load_source_2
from transform import build_data_model

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"


def main():
    # 1. Laad bron data
    source_1 = load_source_1(DATA_DIR / "bron_1.csv")
    source_2 = load_source_2(DATA_DIR / "bron_2.csv")

    # 2. Maak logisch data model
    students, schoolclasses = build_data_model(source_1, source_2, OUTPUT_DIR)

    # 3. Overzicht van studenten per groep
    students_per_group(students, schoolclasses, OUTPUT_DIR)

    # 4. Bereken scores en statistieken
    scores_per_group(students, schoolclasses, OUTPUT_DIR)

    # 5. Genereer historische datapunten
    generate_historical_data(students, schoolclasses, OUTPUT_DIR)

    print("Processing completed successfully.")
    print(f"Output written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
