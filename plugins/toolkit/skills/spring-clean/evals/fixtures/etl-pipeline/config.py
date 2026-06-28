"""Pipeline configuration."""
import os

SOURCE_URL = os.environ.get("SOURCE_URL", "https://example.com/api/records")
OUTPUT_PATH = os.environ.get("OUTPUT_PATH", "output.csv")
