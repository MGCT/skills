"""OLD handler module from before the spring refactor. Superseded by handlers.py.
Kept around 'just in case' and never removed. Uses the old core.py call style that
no longer exists."""
import json

# NOTE: this imports from core, which was deleted when we split it up.
from core import process_list, process_get, process_create


def handle_list(handler):
    result = process_list()
    handler.wfile.write(json.dumps(result).encode())


def handle_get(handler, rid):
    result = process_get(rid)
    handler.wfile.write(json.dumps(result).encode())


def handle_create(handler, data):
    result = process_create(data)
    handler.wfile.write(json.dumps(result).encode())
