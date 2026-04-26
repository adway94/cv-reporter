# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

Daily CV analytics reporter: queries visit stats from a PostgreSQL DB, generates a natural-language summary via an NVIDIA-hosted LLM (LangChain), and sends it to Telegram. Runs once a day via a systemd timer that triggers `docker compose run --rm cv-reporter`.

## Key commands

**Add/update dependencies** (always use uv, never edit pyproject.toml manually):
```bash
uv add <package>
uv remove <package>
```

**Run the reporter locally** (requires `.env` with all vars):
```bash
uv run python -m cv_reporter.main
```

**Build and run via Docker** (what production uses):
```bash
sudo docker compose build   # required after every code change
sudo docker compose run --rm cv-reporter
```

**Inspect DB directly** (timestamps stored as `timestamptz` in UTC):
```bash
sudo docker compose run --rm cv-reporter uv run python -c "<snippet>"
```

## Architecture

The flow is linear: `main.py` → `db/queries.py` → `report/generator.py` → `telegram/sender.py`.

**`main.py`** — entry point. Calls `build_window()` which returns `(since, until)` as the last 24 hours from `now()` in the configured timezone. No fixed cutoff hour — the window is always relative to when the script runs.

**`db/queries.py`** — all SQL via SQLAlchemy ORM. The `visits` table lives in an external Postgres instance (shared with the `/opt/cv` project that records the visits). Timestamps are stored in UTC; `get_hourly_distribution()` converts to local timezone using `func.timezone(TIMEZONE, Visit.timestamp)` before grouping — this is intentional and must be preserved.

**`report/generator.py`** — builds a LangChain pipeline (`prompt | ChatNVIDIA | StrOutputParser`) and invokes it. Langfuse observability is wired in via `CallbackHandler` passed in `config={"callbacks": [...]}`. Langfuse reads its credentials from env vars automatically (`LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`).

**`config.py`** — all config comes from env vars loaded via `python-dotenv`. Required: `NVIDIA_API_KEY`, `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`, `DATABASE_URL`. Optional: `NVIDIA_MODEL`, `TIMEZONE` (default: `America/Argentina/Buenos_Aires`).

## Deployment

The systemd timer (`systemd/cv-reporter.timer`) fires at 09:00 local system time. After any code change, the Docker image must be rebuilt manually (`sudo docker compose build`) — `docker compose run` reuses the cached image.

The `.env` file is not committed. It must contain all required vars plus the Langfuse keys.

## Important constraints

- The `visits` table is owned by `/opt/cv` — do not run migrations from this repo.
- Always use `uv add` to manage dependencies so `uv.lock` stays in sync with `pyproject.toml`.
- The Docker image copies source at build time (`COPY src/ src/`), so editing files on the host requires a rebuild before changes take effect in Docker.
