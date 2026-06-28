"""Entry point for the ETL pipeline. Wires extract -> transform -> load."""
from extract import fetch_records
from transform import clean_records
from load import write_csv
from config import OUTPUT_PATH


def run():
    raw = fetch_records()
    cleaned = clean_records(raw)
    write_csv(cleaned, OUTPUT_PATH)
    print(f"wrote {len(cleaned)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    run()
