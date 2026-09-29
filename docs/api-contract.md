# MediStock — API Contract (v1)

Base URL: `/api/v1`

All endpoints require authentication unless noted. Authorization is enforced
per the permission matrix in [security.md](security.md).

---

## Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /auth/login | Login with email/password | No |
| POST | /auth/logout | Clear session | Yes |
| GET | /auth/me | Get current user profile | Yes |

## Users

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | /users | List users (paginated) | ADMIN |
| POST | /users | Create user | ADMIN |
| GET | /users/{id} | Get user by ID | ADMIN |
| PUT | /users/{id} | Update user | ADMIN |
| PATCH | /users/{id}/roles | Update user roles | ADMIN |
| DELETE | /users/{id} | Deactivate user | ADMIN |

## Categories

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | /categories | List categories | All |
| POST | /categories | Create category | ADMIN, INV_MGR |
| GET | /categories/{id} | Get category | All |
| PUT | /categories/{id} | Update category | ADMIN, INV_MGR |
| DELETE | /categories/{id} | Deactivate category | ADMIN |

## Medicines

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | /medicines | List medicines (paginated, filterable) | All |
| POST | /medicines | Create medicine | ADMIN, INV_MGR |
| GET | /medicines/{id} | Get medicine with batches | All |
| PUT | /medicines/{id} | Update medicine | ADMIN, INV_MGR |
| DELETE | /medicines/{id} | Deactivate medicine | ADMIN |

## Suppliers

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | /suppliers | List suppliers | All |
| POST | /suppliers | Create supplier | ADMIN, INV_MGR |
| GET | /suppliers/{id} | Get supplier | All |
| PUT | /suppliers/{id} | Update supplier | ADMIN, INV_MGR |
| DELETE | /suppliers/{id} | Deactivate supplier | ADMIN |

## Inventory / Batches

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | /inventory | Inventory summary by medicine | All |
| GET | /inventory/{medicine_id}/batches | Batches for a medicine | All |
| GET | /batches/{id} | Get batch details | All |
| POST | /inventory/adjustments | Create stock adjustment | ADMIN, INV_MGR |
| GET | /stock-movements | List stock movements (filterable) | All |

## Purchases

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | /purchases | List purchases | All |
| POST | /purchases | Create purchase | ADMIN, INV_MGR |
| GET | /purchases/{id} | Get purchase with items | All |
| PUT | /purchases/{id} | Update draft purchase | ADMIN, INV_MGR |
| POST | /purchases/{id}/receive | Receive purchase (atomic) | ADMIN, INV_MGR |
| PATCH | /purchases/{id}/cancel | Cancel purchase | ADMIN |

## Sales

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | /sales | List sales | All |
| POST | /sales | Create sale (atomic stock deduction) | ADMIN, PHARMACIST |
| GET | /sales/{id} | Get sale with items | All |
| GET | /sales/{id}/invoice | Get printable invoice | All |

## Returns

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | /returns | List returns | All |
| POST | /returns/customer | Create customer return | ADMIN, PHARMACIST, INV_MGR |
| POST | /returns/supplier | Create supplier return | ADMIN, INV_MGR |
| GET | /returns/{id} | Get return details | All |
| PATCH | /returns/{id}/process | Process return (inspect → restock/write-off) | ADMIN, INV_MGR |

## Alerts

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | /alerts | List active alerts | All |
| POST | /alerts/check | Trigger alert check | ADMIN, INV_MGR |
| PATCH | /alerts/{id}/acknowledge | Acknowledge alert | All (except AUDITOR) |

## Reports

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | /reports/inventory | Current inventory valuation | All |
| GET | /reports/purchases | Purchase report (date range) | All |
| GET | /reports/sales | Sales report (date range) | All |
| GET | /reports/expiry | Expiry report | All |
| GET | /reports/stock-movements | Stock movement report | All |

## Audit Logs

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | /audit-logs | List audit logs (paginated, filterable) | ADMIN, AUDITOR |

## Health

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /health | Health check | No |

---

## Common Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| page | int | Page number (default: 1) |
| page_size | int | Items per page (default: 20, max: 100) |
| search | string | Full-text search (where applicable) |
| sort_by | string | Sort field |
| sort_order | string | "asc" or "desc" |

## Standard Response Format

See [architecture.md](architecture.md) §4 for response envelope, pagination
and error response formats.
