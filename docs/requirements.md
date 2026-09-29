# MediStock — Requirements

## 1. Overview

MediStock is a pharmacy inventory and operations management system. It provides
authenticated, role-based access to medicine catalogs, supplier records,
batch-level inventory, purchasing, sales, returns, alerts and reports.

The system prioritizes **inventory accuracy**, **operational traceability**,
**data integrity** and **usability**.

> **Disclaimer**: MediStock is an inventory management tool. It is not a
> substitute for professional pharmacy dispensing, clinical decision-making or
> regulatory compliance systems.

---

## 2. Functional Requirements

### FR-01 Authentication & Session Management
- Users log in with email and password.
- Passwords are hashed with a modern algorithm (bcrypt or argon2).
- Sessions use secure, HttpOnly, SameSite cookies with JWT or opaque tokens.
- Logout invalidates the session.
- Failed login attempts are rate-limited.

### FR-02 Role-Based Access Control
- Predefined roles: **ADMIN**, **PHARMACIST**, **INVENTORY_MANAGER**, **AUDITOR**.
- A user may hold one or more roles.
- Each API endpoint enforces a permission matrix server-side.
- ADMIN can manage users and roles.
- AUDITOR has read-only access to audit logs and reports.

### FR-03 Medicine & Category Management
- CRUD operations for medicine categories (e.g., Tablets, Syrups, Injectables).
- CRUD operations for medicines with fields: name, generic name, category,
  manufacturer, dosage form, strength, unit, reorder level, description.
- Unique constraint on medicine name + strength + dosage form.
- Search, filter by category, and pagination.

### FR-04 Supplier Management
- CRUD operations for suppliers with fields: name, contact person, email,
  phone, address, GSTIN/tax ID, payment terms, status (active/inactive).
- Unique constraint on supplier name.
- Link suppliers to medicines they supply.

### FR-05 Batch-Level Inventory
- Each medicine stock entry is tracked at the batch level.
- Batch fields: batch number, medicine, supplier, manufacturing date,
  expiry date, quantity received, current quantity, cost price, selling price.
- Unique constraint on medicine + batch number.
- Current quantity must never go negative (enforced at DB level).
- Stock availability = SUM of eligible batch quantities for a medicine.

### FR-06 Purchase Management & Receiving
- Create purchase orders with: supplier, date, items (medicine, quantity,
  unit cost), status, notes.
- Receive purchases: creates or updates batches, records stock movements.
- Purchase receipt and batch creation are atomic (single transaction).
- Purchase statuses: DRAFT → ORDERED → PARTIALLY_RECEIVED → RECEIVED → CANCELLED.

### FR-07 Sales & Billing
- Create sales with: customer name (optional), date, items (medicine, batch,
  quantity, unit price), payment method, notes.
- Server-side total calculation using DECIMAL arithmetic.
- Atomic stock deduction across one or more batches.
- FIFO or explicit batch selection for stock deduction.
- Invoice number generation (unique, sequential).
- Duplicate sale prevention (idempotency key or equivalent).
- Cannot sell expired batches.
- Cannot sell more than available stock.
- Sale statuses: COMPLETED, RETURNED (partial/full).

### FR-08 Returns
- **Customer returns**: linked to original sale, subject to eligibility
  (e.g., within return window, not expired at sale time).
  Return states: PENDING_INSPECTION → RESTOCKED | QUARANTINED | WRITTEN_OFF.
- **Supplier returns**: linked to purchase/batch, reason required.
  Deducts from batch stock. Tracks credit/refund status.
- All returns create stock movement records.

### FR-09 Stock Adjustments
- Authorized users can adjust stock (damage, theft, counting error, etc.).
- Each adjustment requires a reason and creates a stock movement.
- Adjustment permissions restricted to ADMIN and INVENTORY_MANAGER.

### FR-10 Stock Movement Ledger
- Every stock change (purchase receipt, sale, return, adjustment) creates a
  stock_movement record with: batch, movement type, quantity, reference type,
  reference ID, user, timestamp, notes.
- Movement types: PURCHASE_RECEIPT, SALE, CUSTOMER_RETURN, SUPPLIER_RETURN,
  ADJUSTMENT_IN, ADJUSTMENT_OUT, WRITE_OFF.
- The ledger must be reconcilable against batch current quantities.

### FR-11 Expiry & Low-Stock Alerts
- Scheduled or on-demand check for medicines expiring within N days.
- Scheduled or on-demand check for medicines below reorder level.
- Alert states: ACTIVE, ACKNOWLEDGED, RESOLVED.
- Deduplication: do not create duplicate alerts for the same condition.
- Dashboard widget for active alerts.

### FR-12 Dashboard
- Summary cards: total medicines, low-stock count, expiring-soon count,
  today's sales total, today's purchases total.
- Recent sales and recent purchases.
- Top-selling medicines (last 30 days).
- Stock value summary.

### FR-13 Reports
- Inventory report: current stock by medicine/batch with values.
- Purchase report: by date range, supplier, medicine.
- Sales report: by date range, medicine, payment method.
- Expiry report: batches expiring within date range.
- Stock movement report: by date range, movement type, medicine.
- All totals verified against source transactions.

### FR-14 Audit Trail
- Log sensitive operations: user CRUD, role changes, stock adjustments,
  returns, configuration changes.
- Audit fields: action, entity type, entity ID, user, timestamp,
  old values, new values, IP address.
- AUDITOR and ADMIN can view audit logs.
- Audit records are append-only (no updates or deletes).

---

## 3. Non-Functional Requirements

### NFR-01 Security
- See docs/security.md for detailed security requirements.
- OWASP Top 10 awareness in implementation.

### NFR-02 Performance
- API response < 500ms for standard CRUD operations.
- Dashboard loads within 2 seconds.
- Pagination for all list endpoints (default 20, max 100).

### NFR-03 Reliability
- Atomic transactions for all stock-changing operations.
- Database constraints as the last line of defense.
- Graceful error handling with meaningful error messages.

### NFR-04 Maintainability
- Modular architecture with clear separation of concerns.
- Comprehensive test coverage for business logic.
- Up-to-date API documentation via OpenAPI.

### NFR-05 Usability
- Responsive design for desktop and tablet.
- Accessible forms and navigation (WCAG 2.1 AA target).
- Confirmation dialogs for destructive actions.

### NFR-06 Deployment
- Docker Compose for local development.
- Production deployment documentation.
- Database backup and restore procedures.
