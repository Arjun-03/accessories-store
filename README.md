# Accessories Store

An online store for handmade accessories, built for a Sri Lanka–based business.
It launched with press-on nails and is designed to expand across jewellery,
fashion accessories, and beyond without redesign.

Customers browse an editorial storefront, filter by category, add items to a
cart, and place orders with Cash on Delivery or bank transfer — no account
required. A password-protected admin dashboard lets the owner manage products,
categories (with images), and orders.

**Status:** live in production; ongoing visual and feature refinement.

---

## Tech stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Web framework | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Database | PostgreSQL |
| Validation | Pydantic v2 |
| Templating | Jinja2 |
| Styling | Tailwind CSS v4 (compiled) |
| Auth | Argon2 password hashing, server-side sessions |
| Images | Pillow (validation), Amazon S3 (production storage) |
| Testing | pytest |
| Linting / formatting | Ruff + pre-commit |
| Deployment | Docker, Amazon ECR, ECS (Express Mode), RDS, S3 |
| CI/CD | GitHub Actions (OIDC auth) |

---

## Getting started

### Prerequisites

- Python 3.12+
- Node.js 18+ and npm (for compiling CSS)
- Docker Desktop (running)
- Git

### 1. Clone and enter the project

```bash
git clone https://github.com/<your-username>/accessories-store.git
cd accessories-store
```

### 2. Python environment

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

```bash
pip install -r requirements.txt
```

### 3. Frontend (CSS) dependencies

The styling is compiled with Tailwind CSS v4, which needs Node:

```bash
npm install
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
docker compose up -d db
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

### 9. Create an admin account

Admins are created from the command line, not through a signup page:

```bash
python create_admin.py
```

### 10. Build the CSS

```bash
npm run build:css      # one-off build
# or, while developing:
npm run watch:css      # rebuilds automatically on template changes
```

### 11. Run the application

```bash
uvicorn app.main:app --reload
```

| URL | Description |
|---|---|
| http://localhost:8000 | Editorial homepage |
| http://localhost:8000/products | Catalogue (supports ?category=slug filter) |
| http://localhost:8000/cart | Shopping cart |
| http://localhost:8000/checkout | Checkout |
| http://localhost:8000/admin | Admin dashboard (login required) |
| http://localhost:8000/docs | Interactive API documentation |

> **Local dev tip:** run `npm run watch:css` in one terminal and
> `uvicorn app.main:app --reload` in another. If a style change doesn't appear,
> rebuild the CSS and hard-refresh the browser (Ctrl+Shift+R).

---

## Running tests

Tests run against a separate PostgreSQL database so they never touch
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
├── .github/workflows/       # CI (tests) and CD (deploy) pipelines
├── alembic/                 # Migration scripts (versioned schema history)
├── app/
│   ├── config.py            # Settings from environment (incl. ENVIRONMENT, S3)
│   ├── db.py                # Engine, session factory, declarative Base
│   ├── dependencies.py      # Shared dependencies (cart, admin auth, cookies)
│   ├── main.py              # FastAPI application entry point
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic schemas (API boundary)
│   ├── security.py          # Password hashing (Argon2)
│   ├── templating.py        # Jinja2 configuration
│   ├── uploads.py           # Image validation + storage (local dev / S3 prod)
│   ├── utils.py             # Slugs, tokens
│   ├── routers/             # HTTP endpoints, grouped by area
│   ├── services/            # Business logic
│   ├── templates/
│   │   ├── partials/        # Reusable template fragments (e.g. product card)
│   │   └── admin/           # Admin dashboard templates
│   └── static/
│       ├── css/             # input.css (tokens) → main.css (compiled)
│       ├── images/          # Editorial/design images (committed)
│       └── uploads/         # Uploaded product/category images (git-ignored)
├── docs/                    # ADRs and database design
├── tests/                   # pytest suite
├── docker-compose.yml
├── Dockerfile
├── package.json             # Frontend (Tailwind) dependencies
├── requirements.txt         # Python dependencies
├── seed.py                  # Dev seed data
├── create_admin.py          # Create an admin account (CLI)
└── VISION.md
```

### Architecture

Requests flow through distinct layers, each with one responsibility:

```
Browser → Router → Service → Model → PostgreSQL
                     ↑
                  Schema (shapes what crosses the API boundary)
```

- **Router** — HTTP plumbing: receives the request, delegates, returns.
- **Service** — business logic (active-only products, stock checks, cart totals,
  atomic order creation, authentication, filtering).
- **Model** — SQLAlchemy tables and queries.
- **Schema** — an explicit allowlist of fields the JSON API exposes.

Storefront pages call the service layer directly rather than the JSON API.

### Design system

Styling uses Tailwind CSS v4 with a compiled build (not the CDN). Design tokens
(colours, fonts) live in `app/static/css/input.css` via the `@theme` directive
and are used as semantic classes (`bg-background`, `text-ink`, `text-accent`,
`font-serif`). The build scans templates and outputs `app/static/css/main.css`.

---

## Key domain concepts

- **Guest checkout.** No customer accounts at launch; details are captured on
  the order.
- **Admin authentication.** Argon2-hashed passwords, revocable server-side
  sessions in an HttpOnly cookie. Admins are created via CLI. A single
  `require_admin` dependency protects every admin route.
- **Cart vs order.** A cart is a live view (current prices). An order is a
  permanent record — it snapshots product name, SKU, and price at purchase.
- **Atomic checkout.** Order creation, stock decrement, and cart deletion happen
  in one transaction — all succeed or all roll back.
- **Soft delete.** Products are deactivated, never hard-deleted, because they may
  be referenced by historical orders.
- **Category filtering.** `/products?category=slug` filters the catalogue; no
  separate per-category pages.
- **Image storage.** Admin-only uploads, validated by content, stored on local
  disk in development and Amazon S3 in production (chosen by ENVIRONMENT).
- **Money.** Stored as `NUMERIC(10,2)` and handled as `Decimal` everywhere.

---

## Deployment (AWS)

The app is containerized and deployed on AWS:

- **ECR** stores the Docker image.
- **ECS (Express Mode)** runs the container behind a load balancer with HTTPS.
- **RDS** hosts PostgreSQL (private).
- **S3** stores uploaded images (public-read, scoped to `uploads/`).
- **GitHub Actions** builds, pushes, and deploys automatically on merge to
  `main`, authenticating to AWS via OIDC (no long-lived keys).

Production configuration (database, S3 bucket, `ENVIRONMENT=production`) is set
as environment variables on the ECS service, never committed.

### Creating a migration

```bash
alembic revision --autogenerate -m "describe the change"
```

**Always read the generated migration before running it** — autogenerate cannot
detect column renames and will emit a destructive drop-and-add instead.

```bash
alembic upgrade head     # apply
alembic downgrade -1     # roll back one revision
```

---

## Development workflow

Feature branches; `main` is always kept working and is protected (CI must pass
before merge). Merging to `main` triggers automatic deployment.

```bash
git checkout main && git pull
git checkout -b feat/short-description
# ... changes, commit ...
git push -u origin feat/short-description
# open PR → CI runs → review → merge → auto-deploys
```

### Commit message convention

| Prefix | Used for |
|---|---|
| `feat:` | A new feature |
| `fix:` | A bug fix |
| `docs:` | Documentation only |
| `test:` | Adding or changing tests |
| `refactor:` | Restructuring without changing behaviour |
| `chore:` / `ci:` | Tooling, dependencies, pipelines |

### Code quality

Ruff (lint + format) runs before each commit via pre-commit hooks.

```bash
ruff check --fix .
ruff format .
pre-commit run --all-files
```

---

## Security notes

- Secrets live in `.env` (git-ignored); `.env.example` documents required vars.
- `alembic.ini` contains no database URL; Alembic reads it from `app.config`.
- Passwords hashed with Argon2id; session/cart tokens use `secrets`, not `random`.
- Login failures are identical for bad email vs bad password (anti-enumeration).
- Cookies are `HttpOnly` and `SameSite=Lax`; `Secure` is enabled in production.
- Image uploads are validated by content with server-generated filenames.
- CI/CD authenticates to AWS via OIDC — no long-lived credentials stored.
- Business rules are enforced by database constraints in addition to app checks.

### Known limitations

- Order confirmation pages are viewable by anyone with the order number.
- Concurrency: simultaneous checkout of the last unit is prevented by the
  `stock_quantity >= 0` constraint but not handled gracefully.
- Category admin lacks a description input; categories cannot be deactivated
  (they can't be hard-deleted while products reference them).
- Product images: schema supports many per product; UI manages one (primary).
  Multi-image galleries are deferred (no schema change needed to add them).
- Replacing an image leaves the old file orphaned in storage; cleanup deferred.
- Image optimization (resizing/compression) is not yet done; editorial images
  are PNGs.
- Production CSS is currently built locally and committed; building it in the
  Docker image is a planned improvement.

---

## Documentation

| Document | Purpose |
|---|---|
| [`VISION.md`](VISION.md) | Product vision and MVP scope |
| [`docs/database-design.md`](docs/database-design.md) | Schema reference and rationale |
| [`docs/adr/`](docs/adr/) | Architecture Decision Records |

---

## Roadmap

**Done**

- [x] Foundation — FastAPI, PostgreSQL, migrations
- [x] Product catalogue — list, detail, category filtering
- [x] Shopping cart — session-cookie based
- [x] Checkout and orders — guest checkout, COD / bank transfer, atomic
- [x] Admin dashboard — auth, orders, products, categories, image uploads
- [x] Editorial storefront design (Tailwind design system, homepage)
- [x] Deployment on AWS (ECS, RDS, S3) with automated CI/CD

**Next / future**

- Public pages — About, FAQ, Contact
- Custom domain and HTTPS branding
- PayHere card payments (see [ADR-001](docs/adr/ADR-001-payment-gateway.md))
- Customer accounts
- Search, sorting, tags
- Multi-image galleries, image optimization
- Reviews and wishlist, email notifications
