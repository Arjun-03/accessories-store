# Accessories Store

An online store for handmade press-on nails, built for a Sri Lanka–based
business. Designed to expand into other accessory categories (earrings,
necklaces, hair accessories) without redesign.

**Status:** in development — not yet deployed.

---

## Tech stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Web framework | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Database | PostgreSQL 16 (via Docker) |
| Validation | Pydantic v2 |
| Testing | pytest |

---

## Getting started

### Prerequisites

- Python 3.12+
- Docker Desktop (running)
- Git

### 1. Clone and enter the project

```bash
git clone https://github.com/Arjun-03/accessories-store.git
cd accessories-store
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python -m venv venv
source venv/bin/activate
```

> If PowerShell blocks the activation script, run
> `Set-ExecutionPolicy -Scope CurrentUser -RemoteSigned` once, then retry.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the template and fill in your own values:

```bash
cp .env.example .env
```

`.env` is git-ignored and must never be committed.

### 5. Start the database

```bash
docker compose up -d
docker ps          # confirm accessories_db is running on port 5432
```

### 6. Run migrations

```bash
alembic upgrade head
```

### 7. Seed sample data (optional)

```bash
python seed.py
```

The seed script is idempotent — running it repeatedly will not create
duplicates.

### 8. Run the application

```bash
uvicorn app.main:app --reload
```

| URL | Description |
|---|---|
| http://localhost:8000 | Root endpoint |
| http://localhost:8000/api/products | Product catalogue (JSON) |
| http://localhost:8000/docs | Interactive API documentation |

---

## Running tests

Tests run against a **separate** PostgreSQL database so they never touch
development data. Create it once:

```bash
docker exec -it accessories_db psql -U store_user -d accessories
```

```sql
CREATE DATABASE accessories_test;
```

Then run the suite:

```bash
pytest -v
```

Each test creates all tables, runs against a clean database, and drops them
afterwards, so every test starts from a known empty state.

---

## Project structure

```
accessories-store/
├── alembic/                 # Migration scripts (versioned schema history)
│   └── versions/
├── app/
│   ├── config.py            # Settings loaded from environment variables
│   ├── db.py                # Engine, session factory, declarative Base
│   ├── main.py              # FastAPI application entry point
│   ├── models.py            # SQLAlchemy ORM models (database tables)
│   ├── schemas.py           # Pydantic schemas (API boundary)
│   ├── utils.py             # Small shared helpers
│   ├── routers/             # HTTP endpoints, grouped by resource
│   └── services/            # Business logic
├── docs/
│   ├── adr/                 # Architecture Decision Records
│   └── database-design.md   # Schema reference and design rationale
├── tests/
│   ├── conftest.py          # Shared pytest fixtures
│   └── test_products.py
├── docker-compose.yml       # PostgreSQL service definition
├── requirements.txt         # Pinned Python dependencies
├── seed.py                  # Development seed data
└── VISION.md                # Product vision and MVP scope
```

### Architecture

Requests flow through distinct layers, each with one responsibility:

```
Browser → Router → Service → Model → PostgreSQL
                     ↑
                  Schema (shapes what crosses the API boundary)
```

- **Router** — HTTP plumbing only: receives the request, delegates, returns.
- **Service** — business logic and rules (e.g. only active products are public).
- **Model** — SQLAlchemy tables and queries.
- **Schema** — an explicit allowlist of fields exposed by the API. Database
  models are never returned directly.

---

## Database

The schema is documented in [`docs/database-design.md`](docs/database-design.md),
including an ER diagram and the reasoning behind key decisions.

### Creating a migration

After changing a model:

```bash
alembic revision --autogenerate -m "describe the change"
```

**Always read the generated migration before running it.** Autogenerate
produces a draft, not a finished migration — notably, it cannot detect column
renames and will emit a drop-and-add instead, which destroys data.

```bash
alembic upgrade head     # apply
alembic downgrade -1     # roll back one revision
```

---

## Development workflow

Work happens on feature branches; `main` is always kept in a working state.

```bash
git checkout main
git pull
git checkout -b feat/short-description
# ... make changes, commit ...
git push -u origin feat/short-description
```

Then open a pull request, review the diff, merge, and delete the branch.

### Commit message convention

| Prefix | Used for |
|---|---|
| `feat:` | A new feature |
| `fix:` | A bug fix |
| `docs:` | Documentation only |
| `test:` | Adding or changing tests |
| `chore:` | Tooling, dependencies, config |

---

## Security notes

- Secrets live in `.env`, which is git-ignored. `.env.example` documents the
  required variables without exposing values.
- `alembic.ini` deliberately does not contain a database URL; Alembic reads it
  from `app.config` at runtime.
- Money is stored as `NUMERIC(10,2)` and handled as `Decimal` throughout —
  never as a float.
- Business rules are enforced by database constraints in addition to
  application validation.

---

## Documentation

| Document | Purpose |
|---|---|
| [`VISION.md`](VISION.md) | Product vision and MVP scope |
| [`docs/database-design.md`](docs/database-design.md) | Schema reference and rationale |
| [`docs/adr/`](docs/adr/) | Architecture Decision Records |

---

## Roadmap

**MVP (in progress)**

- [x] Foundation — FastAPI app, PostgreSQL, migrations
- [ ] Product catalogue — list, detail pages
- [ ] Shopping cart
- [ ] Checkout and orders (Cash on Delivery, bank transfer)
- [ ] Admin — product and order management
- [ ] Public pages and deployment

**Post-launch**

- PayHere card payments (see [ADR-001](docs/adr/ADR-001-payment-gateway.md))
- Customer accounts
- Search, filtering, and tags
- Reviews and wishlist
