# 💊 MediStock

### Pharmacy Inventory & Operations Management System

**MediStock** is a modern pharmacy management platform designed to streamline **inventory, procurement, batch tracking, point-of-sale billing, alerts, valuation, and audit operations**.

Built with **FastAPI + Next.js + MySQL + Docker**, MediStock focuses on pharmaceutical-specific workflows such as **batch-level expiry tracking, FIFO stock deduction, stock movement auditing, and role-based access control**.

---

## ✨ Highlights

| Module | Features |
|---|---|
| 🔐 **Authentication** | JWT authentication, secure sessions & RBAC |
| 💊 **Medicine Management** | Medicine catalog, categories, dosage forms & strengths |
| 📦 **Batch Inventory** | Batch tracking, expiry monitoring & stock allocation |
| 🛒 **Purchasing** | Vendor procurement & goods receiving |
| 🧾 **POS & Billing** | Fast checkout with automatic FIFO stock deduction |
| 🚨 **Alerts Center** | Low-stock & near-expiry alerts |
| 📊 **Reports** | Inventory, sales, purchases & valuation reports |
| 🔍 **Audit Ledger** | Immutable stock movement tracking |
| ↩️ **Returns** | Customer & supplier return management |
| 👥 **RBAC** | Admin, Pharmacist, Inventory Manager & Auditor |

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │      Next.js 15     │
                    │   Frontend / POS    │
                    └──────────┬──────────┘
                               │
                         REST API / JWT
                               │
                               ▼
                    ┌─────────────────────┐
                    │      FastAPI        │
                    │      Backend        │
                    └──────────┬──────────┘
                               │
                    SQLAlchemy / Alembic
                               │
                               ▼
                    ┌─────────────────────┐
                    │      MySQL 8         │
                    │      InnoDB          │
                    └─────────────────────┘

                         Docker Compose
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
           Frontend         Backend           MySQL
           :3000            :8000             :3306
```

---

# 🚀 Core Features

## 🔐 Authentication & Role-Based Access Control

MediStock provides secure authentication and authorization using:

- JWT authentication
- HTTP cookies
- Bearer tokens
- Role-based access control
- Protected API endpoints
- Secure session handling

### Supported Roles

```text
ADMIN
   │
   ├── Full system access
   │
PHARMACIST
   │
   ├── POS & dispensing operations
   │
INVENTORY_MANAGER
   │
   ├── Procurement & inventory management
   │
AUDITOR
   │
   └── Reports & audit access
```

---

## 💊 Medicine Management

Manage the complete pharmaceutical catalog including:

- Medicine name
- Category
- Dosage form
- Strength
- Unit
- Reorder threshold
- Stock information
- Batch information

Example:

```text
Paracetamol
├── Strength: 500 mg
├── Form: Tablet
├── Unit: Strip
├── Reorder Level: 20
└── Batch-level inventory
```

---

## 📦 Batch-Level Inventory

Unlike basic inventory systems, MediStock tracks stock at the **batch level**.

Each batch maintains:

- Batch number
- Manufacturing date
- Expiry date
- Purchase quantity
- Available quantity
- Purchase price
- Selling price
- Stock status

### Automatic Expiry Status

```text
🟢 VALID
🟡 EXPIRING SOON
🔴 EXPIRED
```

Stock movements support:

```text
IN
OUT
WRITE_OFF
```

Inventory adjustments are designed to maintain transactional consistency and prevent invalid stock states.

---

# 🛒 Purchasing & Goods Receiving

MediStock supports the complete procurement workflow:

```text
Purchase Order
      │
      ▼
Supplier
      │
      ▼
Goods Received
      │
      ▼
Batch Created
      │
      ▼
Inventory Updated
      │
      ▼
Stock Ledger Entry
```

Receiving a shipment automatically:

1. Creates/updates inventory batches
2. Updates available stock
3. Records the stock movement
4. Maintains the audit trail

---

# 🧾 Point of Sale (POS)

The POS module provides a fast pharmacy checkout workflow.

### FIFO Stock Deduction

MediStock automatically follows **First-In-First-Out (FIFO)** batch deduction.

```text
Medicine
   │
   ├── Batch A → 10 units → Older
   │
   ├── Batch B → 20 units
   │
   └── Batch C → 15 units → Newer
          │
          ▼
       Customer Sale
          │
          ▼
   Deduct Batch A first
          │
          ▼
   Then Batch B
```

This helps ensure older inventory is dispensed before newer inventory.

---

# 🚨 Alerts Center

MediStock automatically identifies inventory requiring attention.

### Supported Alerts

- 🔴 Expired batches
- 🟡 Batches approaching expiry
- 🟠 Low-stock medicines
- 📉 Reorder-level violations

Alerts support acknowledgement tracking to help staff manage operational tasks.

---

# 📊 Reports & Valuation

The system provides operational and financial visibility through:

### Inventory

- Current stock
- Batch inventory
- Stock valuation
- Expiry status

### Sales

- Sales summary
- POS transactions
- Sales reports

### Purchases

- Purchase history
- Supplier procurement
- Receiving information

### Audit

- Stock movements
- User actions
- Inventory adjustments
- Transaction history

---

# 🔍 Immutable Stock Audit Ledger

Every inventory movement is recorded.

```text
Purchase Received
       │
       ▼
   STOCK IN
       │
       ▼
Inventory
       │
       ├──────────────┐
       ▼              ▼
   POS SALE       WRITE OFF
       │              │
       ▼              ▼
   STOCK OUT      ADJUSTMENT
       │              │
       └──────┬───────┘
              ▼
        AUDIT LEDGER
```

The ledger provides traceability for:

- Who performed the operation
- What operation occurred
- Which medicine/batch was affected
- Quantity changed
- Previous/new stock state
- Transaction timestamp

---

# ↩️ Returns Management

MediStock supports controlled return workflows.

### Customer Returns

- Sale validation
- Returnable quantity validation
- Stock restoration
- Return integrity checks

### Supplier Returns

- Supplier return processing
- Inventory deduction
- Stock movement recording

---

# 🛠️ Tech Stack

### Backend

- **Python 3.11+**
- **FastAPI**
- **SQLAlchemy 2.0**
- **Pydantic v2**
- **Alembic**

### Frontend

- **Next.js 15**
- **React**
- **TypeScript**
- **Tailwind CSS**
- **Lucide Icons**

### Database

- **MySQL 8.0**
- **InnoDB**

Development can also run using:

- **SQLite**

### Testing

- **Pytest**
- In-memory isolated test database

### DevOps

- **Docker**
- **Docker Compose**

---

# 📁 Project Structure

```text
MediStock/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   └── main.py
│   │
│   ├── tests/
│   ├── alembic/
│   ├── requirements.txt
│   └── venv/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── public/
│   ├── package.json
│   └── next.config.ts
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

# ⚙️ Getting Started

## Prerequisites

Make sure you have the following installed:

- Python 3.11+
- Node.js
- npm
- Git
- Docker Desktop *(recommended)*

Check your installations:

```powershell
python --version
node --version
npm --version
git --version
docker --version
```

---

# 💻 Local Development

SQLite is supported for local development, so MySQL is **not required** to get started.

## 1. Clone the Repository

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>

cd MediStock
```

---

## 2. Start the Backend

```powershell
cd backend

.\venv\Scripts\Activate.ps1

uvicorn app.main:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

### API Documentation

Swagger UI:

```text
http://localhost:8000/api/docs
```

Health Check:

```text
http://localhost:8000/api/v1/health
```

---

## 3. Start the Frontend

Open another terminal:

```powershell
cd frontend

npm install

npm run dev
```

Frontend:

```text
http://localhost:3000
```

---

# 🐳 Docker Deployment

The recommended way to run the complete production-style stack is Docker Compose.

### Services

```text
┌─────────────────────────────┐
│       Docker Compose        │
├─────────────────────────────┤
│                             │
│  Next.js       :3000        │
│       │                     │
│       ▼                     │
│  FastAPI       :8000        │
│       │                     │
│       ▼                     │
│  MySQL         :3306        │
│                             │
└─────────────────────────────┘
```

### Start the Application

```powershell
cp .env.example .env

docker compose up --build
```

### Run in Background

```powershell
docker compose up -d --build
```

### Check Containers

```powershell
docker compose ps
```

### View Logs

```powershell
docker compose logs -f
```

### Stop the Application

```powershell
docker compose down
```

---

# 🧪 Testing

## Backend Tests

```powershell
cd backend

.\venv\Scripts\pytest -v
```

The test suite contains **19 automated tests across 8 test modules**.

### Test Coverage

```text
tests/
│
├── test_alerts.py
├── test_auth.py
├── test_concurrency_and_migrations.py
├── test_inventory_and_sales.py
├── test_medicines.py
├── test_rate_limit.py
├── test_reports_and_audit.py
└── test_returns.py
```

The tests cover:

- Authentication
- Authorization
- Rate limiting
- Medicine management
- Inventory operations
- FIFO stock deduction
- Procurement
- Sales
- Returns
- Alerts
- Reports
- Audit logging
- Database migrations
- Concurrency and stock boundaries

---

# 🔎 Frontend Verification

Run TypeScript verification:

```powershell
cd frontend

npx --no-install tsc --noEmit
```

---

# 🔑 Demo Credentials

The application automatically seeds demo users on first startup.

| Role | Email | Password |
|---|---|---|
| 👑 Admin | `admin@medistock.local` | `Admin@123` |
| 💊 Pharmacist | `pharmacist@medistock.local` | `Pharm@123` |
| 📦 Inventory Manager | `inventory@medistock.local` | `Stock@123` |
| 🔍 Auditor | `auditor@medistock.local` | `Audit@123` |

> ⚠️ **These credentials are for local/demo environments only. Change them before deploying to production.**

---

# 🔄 Application Workflow

```text
                    ┌──────────────┐
                    │    LOGIN     │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │     RBAC     │
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
     PROCUREMENT        INVENTORY          POS
          │                │                │
          ▼                ▼                ▼
     GOODS RECEIVE     BATCH TRACKING     SALE
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                    ┌──────────────┐
                    │ STOCK LEDGER │
                    └──────┬───────┘
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
          REPORTS        ALERTS        AUDIT
```

---

# 🔐 Security

MediStock implements several application-level security mechanisms:

- JWT-based authentication
- Role-based authorization
- Protected API endpoints
- Password hashing
- Login rate limiting
- Transaction validation
- Stock boundary protection
- Audit logging
- Controlled return validation

> For production deployment, configure secure secrets, HTTPS, secure cookies, database credentials, and environment-specific configuration.

---

# 📦 Deployment Stack

MediStock can be deployed using the following architecture:

```text
                  INTERNET
                      │
                      ▼
               Reverse Proxy
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
      Next.js                  FastAPI
       :3000                    :8000
                                  │
                                  ▼
                               MySQL 8
                                :3306
```

Docker Compose provides a reproducible environment for running the complete application stack.

---

# 📈 Future Enhancements

Potential future improvements include:

- 📱 Mobile/PWA support
- 📷 Barcode scanning
- 🧾 Thermal receipt printing
- 📊 Advanced analytics dashboard
- 🤖 AI-based demand forecasting
- 📦 Automated purchase recommendations
- ☁️ Cloud deployment
- 🔔 Email/SMS notifications
- 💳 Payment gateway integration
- 🏪 Multi-branch pharmacy support
- 👤 Advanced user activity analytics

---

# 🗺️ Development Roadmap

```text
[x] Authentication & RBAC
[x] Medicine Management
[x] Batch Inventory
[x] Procurement
[x] Goods Receiving
[x] FIFO POS
[x] Stock Ledger
[x] Alerts
[x] Reports
[x] Returns
[x] Automated Tests
[x] Docker Compose

[ ] Cloud Deployment
[ ] Barcode Integration
[ ] Advanced Analytics
[ ] AI Demand Forecasting
[ ] Multi-Branch Support
```

---

# 📊 Project Quality

| Area | Status |
|---|---|
| Authentication | ✅ |
| RBAC | ✅ |
| Medicine Catalog | ✅ |
| Batch Inventory | ✅ |
| Expiry Tracking | ✅ |
| FIFO POS | ✅ |
| Procurement | ✅ |
| Stock Ledger | ✅ |
| Alerts | ✅ |
| Reports | ✅ |
| Returns | ✅ |
| Backend Tests | ✅ |
| Frontend Type Check | ✅ |
| Docker Compose | ✅ |
| MySQL Support | ✅ |

---

# 👨‍💻 Development

MediStock is designed as a modular full-stack application with a clear separation between:

```text
Frontend
   ↓
API Layer
   ↓
Business Logic
   ↓
Data Access
   ↓
Database
```

This architecture makes the system easier to maintain, test, extend, and deploy.

---

# 📜 License

This project is currently intended for **educational, development, and demonstration purposes**.

Add your preferred license here before public production use.

---

# ⭐ Support

If you find MediStock useful, consider giving the repository a ⭐ on GitHub.

---

## 💊 MediStock

**Inventory. Procurement. POS. Compliance. Auditability.**

> Built to bring modern software engineering practices to pharmacy operations.
