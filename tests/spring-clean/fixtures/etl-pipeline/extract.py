"""Pull raw records from the source API."""
import requests

from config import SOURCE_URL


def fetch_records():
    resp = requests.get(SOURCE_URL, timeout=30)
    resp.raise_for_status()
    return resp.json()
