# Accessories Store

An online store for handmade press-on nails, built for a Sri Lanka–based
business. Designed to expand into other accessory categories (earrings,
necklaces, hair accessories) without redesign.

Customers browse a product catalogue, add items to a cart, and place orders
with Cash on Delivery or bank transfer — no account required. A password-
protected admin dashboard lets the shop owner manage products (with image
uploads) and orders.

**Status:** in development — store is operable end to end; not yet deployed.

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
| Templating | Jinja2 |
| Styling | Tailwind CSS (CDN for now) |
| Auth | Argon2 password hashing, server-side sessions |
| Images | Pillow (upload validation) |
| Testing | pytest |
| Linting / formatting | Ruff + pre-commit |

---

## Getting started

### Prerequisites

- Python 3.12+
- Docker Desktop (running)
- Git

### 1. Clone and enter the project

```bash
git clone https://github.com/<your-username>/accessories-store.git
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

### 4. Enable pre-commit hooks (once)

```bash
pre-commit install
```

### 5. Configure environment variables

```bash
cp .env.example .env
```

`.env` is git-ignored and must never be committed.

### 6. Start the database

```bash
docker compose up -d
docker ps          # confirm accessories_db is running on port 5432
```

### 7. Run migrations

```bash
alembic upgrade head
```

### 8. Seed sample data (optional)

```bash
python seed.py
```

The seed script is idempotent — running it repeatedly will not create duplicates.

### 9. Create an admin account

Admins are created from the command line, not through a signup page:

```bash
python create_admin.py
```

### 10. Run the application

```bash
uvicorn app.main:app --reload
```

| URL | Description |
|---|---|
| http://localhost:8000 | Home page |
| http://localhost:8000/products | Product catalogue |
| http://localhost:8000/cart | Shopping cart |
| http://localhost:8000/checkout | Checkout |
| http://localhost:8000/admin | Admin dashboard (login required) |
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

Each test builds all tables, runs against a clean database, and drops them
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
│   ├── dependencies.py      # Shared FastAPI dependencies (cart, admin auth, cookies)
│   ├── main.py              # FastAPI application entry point
│   ├── models.py            # SQLAlchemy ORM models (database tables)
│   ├── schemas.py           # Pydantic schemas (API boundary)
│   ├── security.py          # Password hashing (Argon2)
│   ├── templating.py        # Jinja2 template configuration
│   ├── uploads.py           # Product image upload validation and storage
│   ├── utils.py             # Small shared helpers (slugs, tokens)
│   ├── routers/             # HTTP endpoints, grouped by area
│   │   ├── products.py      #   JSON API for products
│   │   ├── pages.py         #   Storefront pages (home, catalogue, detail)
│   │   ├── cart.py          #   Cart actions
│   │   ├── checkout.py      #   Checkout and order confirmation
│   │   ├── admin_auth.py    #   Admin login / logout
│   │   └── admin.py         #   Admin dashboard (orders, products)
│   ├── services/            # Business logic
│   │   ├── product_service.py
│   │   ├── cart_service.py
│   │   ├── order_service.py
│   │   └── auth_service.py
│   ├── templates/           # Jinja2 HTML templates (incl. admin/ and macros)
│   └── static/
│       └── uploads/         # Uploaded product images (git-ignored)
├── docs/
│   ├── adr/                 # Architecture Decision Records
│   └── database-design.md   # Schema reference and rationale
├── tests/                   # pytest suite
├── docker-compose.yml       # PostgreSQL service definition
├── requirements.txt         # Pinned Python dependencies
├── seed.py                  # Development seed data
├── create_admin.py          # Create an admin account (CLI)
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
- **Service** — business logic and rules (active-only products, stock checks,
  cart totals, atomic order creation, authentication).
- **Model** — SQLAlchemy tables and queries.
- **Schema** — an explicit allowlist of fields the JSON API exposes. Database
  models are never returned directly.

Storefront pages call the service layer directly rather than calling the JSON
API over HTTP — both the pages and the API are presentations of the same
business logic.

---

## Key domain concepts

- **Guest checkout.** No customer accounts at launch. Customer details are
  captured on the order itself.
- **Admin authentication.** Argon2-hashed passwords, server-side sessions
  (revocable), token in an HttpOnly cookie. Admins are created via CLI, never
  a signup page. A single `require_admin` dependency protects every admin route.
- **Cart vs order.** A cart is a live, mutable view — its prices always reflect
  current product prices. An order is a permanent record — it snapshots product
  name, SKU, and price at purchase time, so later product changes never alter
  past orders.
- **Cart storage.** Cart contents live in the database, identified by an opaque
  token in an HttpOnly cookie, so contents can't be tampered with client-side
  (ADR-002).
- **Atomic checkout.** Order creation, stock decrement, and cart deletion happen
  in a single transaction — all succeed or all roll back.
- **Soft delete.** Products are deactivated (`is_active = false`), never hard-
  deleted, because they may be referenced by historical orders.
- **Money.** Stored as `NUMERIC(10,2)` and handled as `Decimal` everywhere —
  never a float.
- **Image uploads.** Admin-only, validated by content (real image, allowed
  format, size limit) with server-generated filenames, stored under
  `static/uploads/`.

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
| `refactor:` | Restructuring without changing behaviour |
| `chore:` | Tooling, dependencies, config |

### Code quality

Linting and formatting run automatically before each commit via pre-commit
hooks (`ruff check` and `ruff format`, plus whitespace and private-key checks).

To run manually:

```bash
ruff check --fix .    # lint
ruff format .         # format
pre-commit run --all-files
```

---

## Security notes

- Secrets live in `.env`, which is git-ignored. `.env.example` documents the
  required variables without exposing values.
- `alembic.ini` deliberately contains no database URL; Alembic reads it from
  `app.config` at runtime.
- Passwords are hashed with Argon2id and never stored in plaintext. Session and
  cart tokens are generated with `secrets`, never `random`.
- Login failures give an identical response for bad email vs bad password
  (prevents account enumeration).
- Cookies are `HttpOnly` and `SameSite=Lax`. `Secure` is off for local HTTP
  development and **must be enabled in production (HTTPS)**.
- Image uploads are validated by content and given server-generated filenames.
- Business rules are enforced by database constraints in addition to
  application validation.

### Known limitations

- Order confirmation pages are viewable by anyone with the order number
  (guest checkout has no accounts to restrict against yet).
- Concurrency: simultaneous checkout of the last unit is prevented by the
  `stock_quantity >= 0` constraint but not yet handled gracefully.
- Product images: the schema supports many images per product, but the UI
  manages only one (the primary). Multi-image galleries are a post-launch
  feature — no schema change needed to add them.
- Replacing a product image leaves the old file orphaned in `static/uploads/`.
  Cleanup is deferred; harmless at low volume.
- Image optimization (resizing/compression on upload) is not yet done.
- Tailwind is loaded via CDN; it will be compiled to a static file before launch.

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
- [x] Product catalogue — list and detail pages, JSON API
- [x] Shopping cart — add, update, remove, session cookies
- [x] Checkout and orders — guest checkout, COD / bank transfer, atomic orders
- [x] Admin dashboard — authentication, order management, product management with image uploads
- [ ] Public pages — About, FAQ, Contact
- [ ] Deployment — Docker, HTTPS, cloud hosting

**Post-launch**

- PayHere card payments (see [ADR-001](docs/adr/ADR-001-payment-gateway.md))
- Customer accounts
- Search, filtering, and tags
- Multi-image product galleries
- Reviews and wishlist
- Email notifications
