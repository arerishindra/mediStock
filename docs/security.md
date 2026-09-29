# MediStock — Security Design

## 1. Authentication

### Method: Cookie-Based JWT

- Users authenticate via `POST /api/v1/auth/login` with email + password.
- On success, the server sets a JWT in an **HttpOnly, Secure, SameSite=Lax**
  cookie.
- JWT contains: user ID, email, roles, expiration.
- JWT secret is loaded from the `SECRET_KEY` environment variable.
- Token expiry: 8 hours (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`).
- Logout: `POST /api/v1/auth/logout` clears the cookie.

### Password Security

- Passwords hashed with **bcrypt** (work factor 12).
- Minimum password length: 8 characters.
- Passwords are never logged, stored in plaintext, or returned in responses.

### Session Security

- CSRF protection via **double-submit cookie** pattern:
  - Server sets a non-HttpOnly CSRF token cookie.
  - Frontend reads the cookie and sends it as `X-CSRF-Token` header.
  - Server validates the header matches the cookie.
- Rate limiting: 5 failed login attempts per 15-minute window per IP.

---

## 2. Authorization

### Role-Based Access Control (RBAC)

| Permission | ADMIN | PHARMACIST | INVENTORY_MANAGER | AUDITOR |
|------------|:-----:|:----------:|:-----------------:|:-------:|
| **Users** | CRUD | — | — | — |
| **Roles** | Manage | — | — | — |
| **Categories** | CRUD | Read | CRUD | Read |
| **Medicines** | CRUD | Read | CRUD | Read |
| **Suppliers** | CRUD | Read | CRUD | Read |
| **Batches** | CRUD | Read | CRUD | Read |
| **Purchases** | CRUD | Read | CRUD | Read |
| **Purchase Receive** | ✓ | — | ✓ | — |
| **Sales** | CRUD | CRUD | Read | Read |
| **Returns** | CRUD | CRUD | CRUD | Read |
| **Stock Adjustments** | ✓ | — | ✓ | — |
| **Alerts** | CRUD | Read/Ack | Read/Ack | Read |
| **Reports** | ✓ | ✓ | ✓ | ✓ |
| **Audit Logs** | Read | — | — | Read |
| **Dashboard** | ✓ | ✓ | ✓ | ✓ |

### Enforcement

- Every protected endpoint uses a FastAPI dependency that:
  1. Extracts the JWT from the cookie.
  2. Validates the JWT signature and expiration.
  3. Loads the user and their roles.
  4. Checks the required permission.
  5. Returns 401 for missing/invalid tokens.
  6. Returns 403 for insufficient permissions.

- Frontend hides UI elements based on role, but this is cosmetic only.
  The backend is the sole enforcement point.

---

## 3. Input Validation

- All request bodies validated by Pydantic schemas.
- String lengths bounded (prevent oversized payloads).
- Enums for constrained fields (status, payment_method, etc.).
- SQL injection prevented by SQLAlchemy parameterized queries.
- Path parameters validated as integers where expected.

---

## 4. CORS

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],  # e.g., "http://localhost:3000"
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "X-CSRF-Token"],
)
```

---

## 5. Error Handling

- Validation errors return 422 with field-level details.
- Business rule violations return 400 or 409 with descriptive codes.
- Authentication failures return 401.
- Authorization failures return 403.
- Not found returns 404.
- Server errors return 500 with a generic message (details logged, not exposed).
- Stack traces are never sent to the client.

---

## 6. Secrets Management

- All secrets loaded from environment variables.
- `.env` files are in `.gitignore`.
- `.env.example` documents required variables without values.
- No secrets in source code, Docker images, or frontend bundles.
- Database connection string uses environment variables.

Required environment variables:
```
SECRET_KEY=           # JWT signing key
DATABASE_URL=         # mysql+pymysql://user:pass@host:port/db
FRONTEND_URL=         # Allowed CORS origin
```

---

## 7. Audit Trail

- Sensitive operations logged to the `audit_logs` table.
- Logged actions: CREATE, UPDATE, DELETE, LOGIN, LOGOUT, ROLE_CHANGE,
  STOCK_ADJUSTMENT, RETURN_PROCESS.
- Audit records are **append-only** — no UPDATE or DELETE operations.
- Fields captured: action, entity_type, entity_id, user_id, old_values (JSON),
  new_values (JSON), ip_address, created_at.

---

## 8. Additional Measures

- HTTP security headers (X-Content-Type-Options, X-Frame-Options, etc.)
  applied via middleware.
- File upload validation if file features are added (type, size, path safety).
- Database user has minimum required privileges (no GRANT, DROP in app user).
