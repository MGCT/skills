# recipe-api

A tiny HTTP API for storing and retrieving recipes. Stdlib only, SQLite for storage.

## Run

```
python src/app.py
```

Listens on `:5000` (override with `PORT`).

## Endpoints

- `GET /recipes` — list
- `GET /recipes/<id>` — fetch one
- `POST /recipes` — create
