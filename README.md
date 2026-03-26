# Flask Email Login

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/jelmerdejong/flask-email-login)

A small passwordless Flask app that signs users in with one-time email links.

The project now uses:

- Flask 3.1 with an app factory
- Flask-SQLAlchemy 3.1 and SQLAlchemy 2 style models/querying
- Flask-Migrate/Alembic for schema changes
- Bootstrap 5.3 for the UI
- `pyproject.toml` + `uv.lock` for dependency management
- pytest with hermetic SQLite-backed tests

## Requirements

- Python 3.11
- [uv](https://docs.astral.sh/uv/)

## Quick Start

1. Sync the environment:

   ```bash
   uv sync --extra dev --python 3.11
   ```

2. Copy the example environment file and adjust settings as needed:

   ```bash
   cp .env.example .env
   ```

3. Apply the database migration:

   ```bash
   uv run flask --app app:create_app db upgrade
   ```

4. Start the app:

   ```bash
   uv run flask --app app:create_app run --debug
   ```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Environment Variables

The app loads `.env` and `.flaskenv` with `override=False`, so real environment variables always win over local dotenv files.

Common settings:

- `SECRET_KEY`: set this in every non-local environment
- `DATABASE_URL`: optional override for SQLite, Postgres, or another SQLAlchemy-supported database
- `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USE_SSL`, `MAIL_USERNAME`, `MAIL_PASSWORD`
- `MAIL_DEFAULT_SENDER`: sender address for login emails
- `MAIL_SUPPRESS_SEND=true`: skips SMTP delivery and still logs the magic link to the application logs for local smoke testing

If `DATABASE_URL` is not set, the app uses SQLite in the Flask instance folder.

## Database Workflow

Create migrations with:

```bash
uv run flask --app app:create_app db migrate -m "Describe your change"
```

Apply migrations with:

```bash
uv run flask --app app:create_app db upgrade
```

If you have an old local SQLite database from the pre-Alembic version of this app, delete `instance/app.db` and rerun `db upgrade` so Alembic can create and track the schema cleanly.

## Tests

Run the full test suite with:

```bash
uv run pytest
```

The tests use a temporary SQLite database and do not depend on any pre-existing local Postgres instance.

## Production Notes

Gunicorn works directly with the app factory:

```bash
uv run gunicorn 'app:create_app()'
```

For production deployments:

- set a strong `SECRET_KEY`
- configure real SMTP credentials
- point `DATABASE_URL` at the production database
- run `flask db upgrade` before serving traffic

This repo does not include platform-specific deployment configuration. Staging/production deployment should be layered on top of the documented Flask, Gunicorn, and Alembic commands above.

## Codespaces

This repository includes a `.devcontainer` configuration for Python 3.11 and `uv`. Opening the repo in GitHub Codespaces will install dependencies automatically and expose port `5000`.
