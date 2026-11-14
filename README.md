# S.T.E.M.

Student Technological & Educational Mate is a browser-based student productivity and academic management system.

This repository currently includes the application factory, configuration, the student `User` model, registration/login/logout, and a login-protected dashboard.

## Requirements

- Python 3.11 or newer (3.10+ should work)
- PostgreSQL 14+ for local development and production
- Git

Automated tests use an in-memory SQLite database. You do **not** need PostgreSQL to run Pytest.

## Local setup (Windows PowerShell)

From the project root `stem-student-mate`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

Copy environment variables and edit the values:

```powershell
copy .env.example .env
```

Set at least:

- `SECRET_KEY` — a long random string
- `DATABASE_URL` — your PostgreSQL URL, for example `postgresql+psycopg://USER:PASSWORD@localhost:5432/stem_dev`
- `STEM_CONFIG=development`

Create the database in PostgreSQL (example using `psql`):

```sql
CREATE DATABASE stem_dev;
```

Apply migrations (this is the supported way to create tables; do not rely on `db.create_all()` outside tests):

```powershell
$env:FLASK_APP = "wsgi:app"
flask db upgrade
```

Run the app:

```powershell
flask --app wsgi:app run
```

Open http://127.0.0.1:5000/ — you should be redirected to `/login`. Register a student, then you should land on `/dashboard`.

## Local setup (macOS / Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
cp .env.example .env
# edit .env, create PostgreSQL database stem_dev
export FLASK_APP=wsgi:app
flask db upgrade
flask --app wsgi:app run
```

## Configuration

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Flask session signing and CSRF. Required. |
| `DATABASE_URL` | PostgreSQL URL for development and production. |
| `STEM_CONFIG` | `development` or `production` (tests pass `TestingConfig` in code). |
| `FLASK_DEBUG` | Optional Flask CLI debugger flag. Use `1` locally. |

Do **not** set `FLASK_ENV`. That setting is deprecated.

Do **not** commit `.env`.

## Tests

```powershell
pytest
```

Tests use `TestingConfig`: SQLite in memory, CSRF off except for dedicated CSRF cases.

## Project layout

- `stem/` — application package (`create_app`, config, models, services, blueprints, templates)
- `tests/` — Pytest suite
- `migrations/` — Alembic revisions managed by Flask-Migrate
- `wsgi.py` — WSGI callable (`app`)

Business rules live in `stem/services/`. Flask routes only handle HTTP.
