# MediStock — Pharmacy Inventory & Operations OS

MediStock is a pharmacy inventory, point-of-sale (POS), and operations management system designed for pharmaceutical compliance, batch-level expiry tracking, and auditability.

---

## Key Capabilities

1. **Authentication & RBAC**: Multi-role access control (`ADMIN`, `PHARMACIST`, `INVENTORY_MANAGER`, `AUDITOR`) via JWT cookies and Bearer tokens.
2. **Medicines & Categories**: Complete pharmaceutical catalog with dosage forms, strengths, units, and custom reorder level thresholds.
3. **Batch-Level Inventory**: Expiry date tracking with automatic status badges (Valid, Expiring Soon, Expired), purchase batch allocation, and atomic stock adjustments (`IN`, `OUT`, `WRITE_OFF`).
4. **Purchasing & Goods Receiving**: Vendor procurement workflow where receiving shipments automatically populates inventory batches and updates the ledger.
5. **Point of Sale (POS) & Billing**: Fast cashier checkout with automated First-In-First-Out (**FIFO**) batch stock deduction and receipt generation.
6. **Active Alerts Center**: Automated detection and manual scanning of low-stock medicines and batches nearing expiration with acknowledgement tracking.
7. **Valuation & Audit Ledger**: Immutable signed stock movements ledger tracking every single receipt, dispensing, and adjustment.

---

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic
- **Database**: SQLite (local development mode out-of-the-box) or MySQL 8.0 (InnoDB) for production/Docker
- **Frontend**: Next.js 15 (App Router), TypeScript, Tailwind CSS, Lucide Icons
- **Testing**: Pytest (isolated in-memory test database)
- **Deployment**: Docker Compose multi-container setup

---

## What Needs to Be Installed for Development

### 1. Already Installed on This System
- **Python**: 3.11.9 (installed and virtual environment created at `backend/venv`)
- **Node.js**: v24.21.0 (with `npm` 11.19.0)
- **Git**: 2.55.0

### 2. Recommended to Install (For Production & Full MySQL Containerization)
- **Docker Desktop for Windows**:
  - Download from: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
  - *Why needed:* Docker enables running the complete multi-container stack (`MySQL 8`, `FastAPI backend`, and `Next.js frontend`) with a single command (`docker compose up --build`).
- **MySQL 8 Community Server** *(Only if you prefer running native MySQL without Docker)*:
  - Download from: [https://dev.mysql.com/downloads/installer/](https://dev.mysql.com/downloads/installer/)

> **Note on Database:** You **do not** need MySQL installed immediately to test and develop the application right now. The backend is configured to automatically use a local SQLite database (`backend/medistock.db`) when MySQL is not detected, enabling instant local development!

---

## How to Run the Application

### Option A: Local Development (Ready Right Now)

#### 1. Start the Backend API
Open a PowerShell terminal:
```powershell
cd "c:\Users\sri sindhuja\Downloads\Antigravity\backend"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start FastAPI development server (seeds default admin and roles on startup)
uvicorn app.main:app --reload --port 8000
```
- API will be live at: `http://localhost:8000`
- Interactive Swagger API Documentation: `http://localhost:8000/api/docs`
- Health check: `http://localhost:8000/api/v1/health`

#### 2. Start the Frontend Web Application
Open a second PowerShell terminal:
```powershell
cd "c:\Users\sri sindhuja\Downloads\Antigravity\frontend"

# Start Next.js development server
npm run dev
```
- Web Application will be live at: `http://localhost:3000`

---

### Option B: Run with Docker Compose (Once Docker Desktop is Installed)

To run the full stack with MySQL 8:
```powershell
cd "c:\Users\sri sindhuja\Downloads\Antigravity"

# Copy example environment file
cp .env.example .env

# Build and start all services
docker compose up --build
```
This automatically boots:
- `medistock-db`: MySQL 8.0 on port 3306 with health checks
- `medistock-backend`: FastAPI on port 8000
- `medistock-frontend`: Next.js production build on port 3000

---

## Running Automated Tests

The backend test suite runs against an isolated, in-memory SQLite database:
```powershell
cd "c:\Users\sri sindhuja\Downloads\Antigravity\backend"
.\venv\Scripts\pytest.exe -v
```
All 7 integration and unit tests will execute:
- `test_health_check`
- `test_login_success`
- `test_login_invalid_password`
- `test_get_me`
- `test_create_and_list_category`
- `test_create_and_get_medicine`
- `test_full_inventory_and_sales_flow` (Procurement -> Batch Receiving -> FIFO POS Sale -> Ledger Validation)

---

## Default Login Credentials

On first run, the database automatically seeds the default Administrator:

| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@medistock.local` | `Admin@123` |
| **Test Admin** | `admin@test.com` | `Admin@123` |

*(The frontend login screen includes one-click buttons to auto-populate these credentials).*
