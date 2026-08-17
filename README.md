# Hormuz-Dashboard (ripple)

Early-warning market-signal service. This repository ships a **typed, tested scaffold** — no live data collection, no vendor calls, no secrets.

The Python package is `ripple`. A Next.js dashboard remains in `app/` for a later UI pass; it is not required to run the signal service.

## Stack

Python 3.12, Postgres (Neon-compatible) via SQLAlchemy 2.0 + Alembic, pydantic-settings, httpx, pandas, APScheduler, typer, pytest, ruff. Dependency management is [uv](https://docs.astral.sh/uv/).

## Setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then from the repo root:

```bash
uv python install 3.12
uv sync --group dev
```

Copy the example env file. **Leave optional keys empty** if you do not have them — the process starts and logs a warning instead of crashing (cloud VMs often boot without a `.env`).

```bash
cp .env.example .env
```

`.env.example` lists every key and contains **no values**. Never commit a filled `.env`.

For a local or Neon Postgres database, set `DATABASE_URL` to a SQLAlchemy URL, for example:

```text
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DB?sslmode=require
```

Tests use in-memory / temp SQLite and do not need Postgres.

## Database

```bash
uv run alembic upgrade head
uv run alembic downgrade base
```

Schema:

- `signals` — append-only ledger. Prediction columns cannot be updated (SQLAlchemy listener).
- `signal_outcomes` — separate maturity table (`1h` / `1d` / `1w`) so the ledger stays immutable.
- `price_bars` — OHLCV. All timestamps are UTC.

## CLI

```bash
uv run ripple --help
uv run ripple ingest
uv run ripple detect
uv run ripple mature
uv run ripple backtest
```

Every command is a no-op in this scaffold. APScheduler jobs in `src/ripple/schedule/` are registered the same way and are not started by the CLI.

## Tests and lint

```bash
uv run pytest
uv run ruff check src tests migrations
```

Definition of done for this scaffold: `uv run pytest` is green, `ripple --help` works, Alembic upgrade/downgrade is clean on an empty database, and the ledger-immutability test passes.

## Layout

```text
src/ripple/{config,db,models,connectors,detect,verify,price,corroborate,schedule,cli}/
tests/
migrations/
configs/          # source_registry.yaml, chokepoints.yaml
```

`configs/source_registry.yaml` tiers Taiwan-semis sources `OFFICIAL > WIRE > outlet > aggregator > social`. `configs/chokepoints.yaml` defines the Taiwan/TSMC entry (`2330.TW` leading; `TSM` and `SOXX` lagging).

## Interfaces (seams for later PRs)

`SourceConnector`, `Verifier`, `PriceProvider`, and `Corroborator` are abstract. `GrokCorroborator` raises `NotImplementedError` until live corroboration is added.
