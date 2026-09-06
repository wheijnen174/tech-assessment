from pathlib import Path

import pandas as pd


def load_source_1(source_dir: Path) -> pd.DataFrame:
    df = pd.read_csv(source_dir, delimiter=",")

    return df


def load_source_2(source_dir: Path) -> pd.DataFrame:
    df = pd.read_csv(source_dir, delimiter=";", decimal=".")

    df_melt = (
        pd.melt(
            df,
            id_vars=["groep", "leerling", "leerkracht", "invuller", "datum"],
            var_name="vak",
            value_name="cijfer",
        )
        .dropna(subset=["cijfer"])
        .reset_index(drop=True)
    )

    return df_melt
