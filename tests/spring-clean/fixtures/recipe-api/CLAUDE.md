# recipe-api — Claude notes

This file is the running brain-dump for the recipe-api project. Read it before doing
anything. It has grown over time and contains everything we've learned.

## Project overview

recipe-api is a small HTTP API for storing and retrieving cooking recipes. It started
as a weekend project in 2023 and has slowly grown. Originally it was a single
`app.py` file but we split it up. The whole point is to be simple and not over-engineer
things, so please keep that spirit.

## History (for context)

- We first built this with Flask but then we thought about switching to FastAPI and
  spent a weekend on that and then decided to stay with Flask, so if you see references
  to FastAPI anywhere they are wrong, ignore them.
- At one point all the logic lived in `core.py` which was the heart of the app. We
  later broke `core.py` apart into smaller modules. The handler logic moved out.
- We used to have a `models.py` with SQLAlchemy models but we ripped out the ORM and
  went back to raw SQL because it was simpler for our needs.
- There was a big refactor in the spring where we renamed a bunch of things. The old
  names might still appear in some comments.
- We tried adding a caching layer with Redis but it was overkill so we removed it.
  There may be leftover `cache.py` references — ignore those, cache.py is gone.

## Architecture

The app has these main pieces:

- `app.py` — the entry point. Sets up the server and routes.
- `core.py` — THE most important file, contains all the request handling logic and the
  business rules. When in doubt, look here first.
- `db.py` — database helpers, talks to SQLite.
- `models.py` — the data models (see note above, this might be stale).
- `utils.py` — random helper functions used across the app.

Routes are registered in `app.py` and they call into `core.py` which does the work.

## Database

We use SQLite. The database file is `recipes.db` and it gets created on first run.
The schema is defined inline in `db.py` in the `init_db()` function. There is one
table, `recipes`, with columns id, title, ingredients, instructions, created_at.

To reset the database just delete `recipes.db` and restart.

NOTE: we were going to migrate to Postgres but decided not to for now. If you see a
`DATABASE_URL` env var mentioned, that was for the Postgres plan and isn't used.

## Running the app

```
pip install -r requirements.txt
python app.py
```

It runs on port 5000 by default. You can change the port with the PORT env var.

Wait — actually we moved the entry point. It might be `python -m recipe_api` now? I'm
not 100% sure, check `app.py` to be safe. (TODO: confirm how to run this.)

## API endpoints

- GET /recipes — list all recipes
- GET /recipes/<id> — get one recipe
- POST /recipes — create a recipe
- PUT /recipes/<id> — update a recipe
- DELETE /recipes/<id> — delete a recipe

We were going to add a /search endpoint but haven't yet. (TODO: add search.)
We also talked about pagination on the list endpoint. (TODO: add pagination.)
We also wanted to add user accounts and auth at some point. (TODO: auth.)

## Testing

Run the tests with:

```
pytest
```

The tests live in the `tests/` folder. There's `test_handlers.py` for the handler
logic. We should add more tests. (TODO: more test coverage, especially for db.py.)

NOTE: there used to be a `test_core.py` but since core.py was split up that test file
was removed. If pytest complains about test_core, it's gone.

## Coding conventions

- Keep it simple. This is a small project.
- We use plain functions, not classes, where possible.
- 4-space indentation, standard PEP8-ish but we're not strict.
- Don't add big dependencies without a good reason.
- Error responses should be JSON with an "error" key.

## Things we learned the hard way

- SQLite doesn't like concurrent writes — we hit "database is locked" errors early on.
  We mostly solved this by keeping requests short. If it comes back, that's the cause.
- Don't forget to commit the SQLite transaction or your writes vanish silently.
- The JSON encoder chokes on datetime objects, so we convert created_at to a string
  before returning it.
- Flask's debug mode reloader runs init_db twice which was confusing during dev.

## Deployment

We deploy this to a small VPS. The deploy is manual right now:

1. SSH into the box
2. git pull
3. restart the systemd service `recipe-api.service`

(TODO: automate the deploy, maybe with a GitHub Action.)

There's a `deploy.sh` script that does some of this but it's out of date and references
the old core.py structure, so don't trust it blindly.

## Known issues / tech debt

- The error handling is inconsistent across endpoints. Some return 400, some 500.
- No input validation to speak of — you can POST garbage and it'll try to store it.
- The list endpoint loads everything into memory, won't scale, but fine for now.
- `utils.py` has become a junk drawer of unrelated helpers.
- We have that `handlers_old.py` file lying around from the refactor that we should
  probably delete but haven't gotten around to.

## Random notes

- The favicon situation is unresolved, browsers keep asking for /favicon.ico.
- Someone added a print statement somewhere for debugging, might still be there.
- The Screenshot in the repo root is from when we were debugging a CORS issue.
- scratch.py was me testing something, can probably go.
- If the app won't start, check you're not already running it on port 5000.

## Contact

This is a personal project, ping the maintainer on the usual channel if stuck.
