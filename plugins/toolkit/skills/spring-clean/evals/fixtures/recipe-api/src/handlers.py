"""Request handlers for recipe-api. This is the current handler module."""
import json

from db import list_recipes, get_recipe, create_recipe


def _send(handler, status, payload):
    body = json.dumps(payload).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.end_headers()
    handler.wfile.write(body)


def handle_list(handler):
    _send(handler, 200, [_serialize(r) for r in list_recipes()])


def handle_get(handler):
    rid = handler.path.rsplit("/", 1)[-1]
    recipe = get_recipe(rid)
    if recipe is None:
        _send(handler, 404, {"error": "not found"})
        return
    _send(handler, 200, _serialize(recipe))


def handle_create(handler):
    length = int(handler.headers.get("Content-Length", 0))
    data = json.loads(handler.rfile.read(length) or "{}")
    rid = create_recipe(data.get("title", ""), data.get("ingredients", ""),
                        data.get("instructions", ""))
    _send(handler, 201, {"id": rid})


def _serialize(row):
    return {
        "id": row[0],
        "title": row[1],
        "ingredients": row[2],
        "instructions": row[3],
        "created_at": str(row[4]),
    }
