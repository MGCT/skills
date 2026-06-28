"""Clean and normalise raw records into output rows."""
import pandas as pd

from helpers import normalise_name


def clean_records(raw):
    df = pd.DataFrame(raw)
    df = df.dropna(subset=["name"])
    df["name"] = df["name"].map(normalise_name)
    return df.to_dict("records")
