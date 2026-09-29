# MediStock — Architecture

## 1. System Overview

MediStock is a **modular monolith** consisting of two deployable units:

1. **Backend API** — Python / FastAPI serving a RESTful JSON API.
2. **Frontend App** — Next.js / React / TypeScript serving the admin UI.

Both communicate over HTTP(S). The backend is the **sole authority** for
business logic, data validation and security enforcement. The frontend is a
presentation layer that calls the backend API.

```
┌──────────────────┐       HTTPS/JSON       ┌──────────────────┐
│                  │ ◄───────────────────► │                  │
│   Next.js App    │                        │   FastAPI API    │
│   (Frontend)     │                        │   (Backend)      │
│                  │                        │                  │
│  Port 3000       │                        │  Port 8000       │
└──────────────────┘                        └────────┬─────────┘
                                                     │
                                                     │ SQLAlchemy
                                                     │
                                            ┌────────▼─────────┐
                                            │                  │
                                            │   MySQL 8.x      │
                                            │   (InnoDB)        │
                                            │                  │
                                            │  Port 3306       │
                                            └──────────────────┘
```

## 2. Backend Architecture

### 2.1 Module Structure

Each domain is a self-contained module with its own router, schemas, service
and repository (where needed):

```
backend/app/
├── main.py                 # FastAPI application factory
├── core/
│   ├── config.py           # Settings from environment
│   ├── security.py         # Password hashing, token creation
│   └── dependencies.py     # Shared FastAPI dependencies
├── db/
│   ├── session.py          # Engine, SessionLocal, get_db
│   ├── base.py             # Declarative base & model imports
│   └── seed.py             # Initial seed data
├── common/
│   ├── exceptions.py       # App-level exception classes
│   ├── responses.py        # Standardized response schemas
│   ├── pagination.py       # Pagination utilities
│   └── logging.py          # Structured logging setup
├── auth/
│   ├── router.py           # POST /auth/login, POST /auth/logout
│   ├── schemas.py          # LoginRequest, TokenResponse
│   ├── service.py          # Authenticate, create session
│   └── dependencies.py     # get_current_user, require_role
├── users/
│   ├── router.py           # /users CRUD
│   ├── schemas.py
│   ├── service.py
│   ├── repository.py
│   └── models.py           # User, Role, UserRole
├── medicines/
│   ├── router.py           # /medicines, /categories CRUD
│   ├── schemas.py
│   ├── service.py
│   ├── repository.py
│   └── models.py           # Medicine, Category
├── suppliers/
│   ├── router.py           # /suppliers CRUD
│   ├── schemas.py
│   ├── service.py
│   ├── repository.py
│   └── models.py           # Supplier, MedicineSupplier
├── inventory/
│   ├── router.py           # /inventory, /batches, /stock-movements
│   ├── schemas.py
│   ├── service.py          # Stock operations, reconciliation
│   ├── repository.py
│   └── models.py           # Batch, StockMovement
├── purchases/
│   ├── router.py           # /purchases CRUD + receive
│   ├── schemas.py
│   ├── service.py          # Atomic purchase receiving
│   ├── repository.py
│   └── models.py           # Purchase, PurchaseItem
├── sales/
│   ├── router.py           # /sales CRUD + create sale
│   ├── schemas.py
│   ├── service.py          # Atomic sale with stock deduction
│   ├── repository.py
│   └── models.py           # Sale, SaleItem
├── returns/
│   ├── router.py           # /returns CRUD
│   ├── schemas.py
│   ├── service.py          # Return processing with state machine
│   ├── repository.py
│   └── models.py           # Return, ReturnItem
├── alerts/
│   ├── router.py           # /alerts
│   ├── schemas.py
│   ├── service.py          # Alert generation & deduplication
│   ├── repository.py
│   └── models.py           # Alert
└── reports/
    ├── router.py           # /reports
    ├── schemas.py
    └── service.py          # Aggregation queries
```

### 2.2 Layering Rules

```
Router  →  Service  →  Repository  →  SQLAlchemy / DB
  │            │
  │            └── Business logic, validation, transactions
  │
  └── HTTP concerns: request parsing, response formatting,
      status codes, dependency injection
```

- **Routers** handle HTTP request/response and call services.
- **Services** contain business rules, orchestrate repositories, and manage
  transactions. All stock-changing operations use explicit `db.begin()` or
  commit/rollback patterns.
- **Repositories** encapsulate database queries. They do NOT manage
  transactions — that responsibility belongs to the service layer.
- **Schemas** (Pydantic) validate request/response data.
- **Models** (SQLAlchemy) define database tables.

### 2.3 Transaction Strategy

For stock-changing operations (sales, purchases, returns, adjustments):

1. Service opens an explicit transaction.
2. Acquires row-level locks (`SELECT ... FOR UPDATE`) on affected batches,
   ordered by batch ID to prevent deadlocks.
3. Validates business rules (stock availability, expiry, eligibility).
4. Performs mutations (update quantities, insert movements).
5. Commits atomically — all or nothing.
6. On failure, rolls back and returns a clear error.

Deadlocks are caught and retried up to 3 times with exponential backoff.

### 2.4 Inventory Balance Strategy

**Decision: Cached balance with ledger reconciliation.**

- Each `Batch` row stores a `current_quantity` field (the cached balance).
- Every stock change also inserts a `StockMovement` record (the ledger).
- Both the `current_quantity` update and `StockMovement` insert happen in
  the **same atomic transaction**.
- A reconciliation query can verify:
  `batch.quantity_received + SUM(movements) == batch.current_quantity`
- A CHECK constraint ensures `current_quantity >= 0`.
- Reconciliation tests run as part of the integration test suite.

This approach provides O(1) stock lookups while maintaining full auditability.

## 3. Frontend Architecture

### 3.1 Directory Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx          # Root layout with providers
│   ├── page.tsx            # Redirect to /dashboard or /login
│   ├── login/
│   ├── dashboard/
│   ├── medicines/
│   ├── suppliers/
│   ├── inventory/
│   ├── purchases/
│   ├── sales/
│   ├── returns/
│   ├── alerts/
│   ├── reports/
│   ├── users/
│   └── audit/
├── components/
│   ├── ui/                 # shadcn/ui components
│   ├── layout/             # Sidebar, Header, Navigation
│   ├── forms/              # Reusable form components
│   └── data-display/       # Tables, cards, charts
├── features/               # Feature-specific components
├── hooks/                  # Custom React hooks
├── lib/
│   ├── api.ts              # API client (fetch wrapper)
│   ├── auth.ts             # Auth context & utilities
│   └── utils.ts            # Shared utilities
├── types/                  # TypeScript type definitions
└── tests/                  # Playwright E2E tests
```

### 3.2 API Integration

- A centralized API client in `lib/api.ts` handles:
  - Base URL configuration from environment variables.
  - Cookie-based authentication (credentials: 'include').
  - Standard error handling and response parsing.
  - Request/response type safety.
- Frontend types are derived from or aligned with the OpenAPI spec.

### 3.3 State Management

- Server state managed via React hooks with fetch + SWR-like patterns
  (or React Query if complexity warrants it).
- Form state managed with React Hook Form + Zod validation.
- Auth state in a React context provider.
- No global state library unless justified by complexity.

## 4. API Design Conventions

### 4.1 URL Structure
```
GET    /api/v1/{resource}           List (paginated)
POST   /api/v1/{resource}           Create
GET    /api/v1/{resource}/{id}      Get by ID
PUT    /api/v1/{resource}/{id}      Full update
PATCH  /api/v1/{resource}/{id}      Partial update
DELETE /api/v1/{resource}/{id}      Soft delete / deactivate
```

### 4.2 Standard Response Envelope
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### 4.3 Paginated Response
```json
{
  "success": true,
  "data": {
    "items": [ ... ],
    "total": 150,
    "page": 1,
    "page_size": 20,
    "total_pages": 8
  }
}
```

### 4.4 Error Response
```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_STOCK",
    "message": "Batch B001 has only 5 units available",
    "details": { ... }
  }
}
```

## 5. Security Architecture

See [docs/security.md](security.md) for the full security design.

Key points:
- Authentication via secure HttpOnly cookies.
- RBAC enforced at every API endpoint.
- CSRF protection for cookie-based auth.
- All inputs validated server-side.
- Secrets from environment variables only.

## 6. Deployment Architecture

```
docker-compose.yml
├── backend    (FastAPI, Uvicorn)
├── frontend   (Next.js, standalone)
└── db         (MySQL 8.x)
```

- Environment-specific configuration via `.env` files.
- Health check endpoints: `GET /api/v1/health`.
- Database migrations run on startup or via a separate init container.

## 7. Key Design Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Cached balance + ledger | O(1) lookups with full auditability |
| 2 | Cookie-based auth | Simpler CSRF-protected auth for SPA |
| 3 | FIFO batch deduction | Industry standard for pharmacy stock |
| 4 | Soft deletes for core entities | Preserve referential integrity and audit trail |
| 5 | Server-side totals | Prevent client-side arithmetic manipulation |
| 6 | Idempotency keys for sales | Prevent duplicate transactions |
| 7 | Append-only audit log | Tamper-resistant operation history |
| 8 | UTC timestamps | Consistent time handling across deployments |
