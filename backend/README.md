# HostelShare - Backend Service

High-performance, privacy-first REST API built with FastAPI, SQLAlchemy, and Supabase PostgreSQL for peer-to-peer campus rentals.

---

## Features & Cyber Defense Architecture

- **Phone OTP Authentication**: Protected by sliding-window rate limiting (max 5 requests / 60s) with mock OTP support for development (`123456`) issuing secure JWT tokens.
- **Strict Privacy Shield**: Sanitized public profiles (`/u/:username`) completely strip phone numbers, room numbers, and hostel wings at the database serialization level.
- **Dual-Handshake State Machine**:
  - `PENDING` $\to$ `ACCEPTED` $\to$ `ACTIVE` $\to$ `RETURNED` $\to$ `COMPLETED` (or `CANCELLED`).
  - **Handover PIN**: 4-digit code provided to Lender, entered by Borrower to activate the rental.
  - **Return PIN**: 4-digit code provided to Borrower, entered by Lender to mark the item returned.
  - **Brute-Force Rate Limiting**: Max 5 failed PIN attempts triggers a 300-second lockout.
  - **Mandatory Trust Reviews**: Post-return 1-5 star peer reviews recalculating trust scores.
- **Mutual Privacy Shield In-App Chat**:
  - Opens automatically upon rental acceptance.
  - Phone numbers are masked by default (`+91 ••••• ••123`).
  - Full phone numbers are revealed **if and only if both parties click 'Share Phone Number'**.
  - **Ephemeral Lifecycle**: Automatically sets expiration to `return_time + 24 hours` on completion or `cancellation_time + 72 hours` on cancellation.
- **Image Processing & Storage**:
  - Strips EXIF metadata (GPS coordinates, camera tags, timestamps) using Pillow to safeguard student hostel locations.
  - 5 MB maximum file upload ceiling rejecting oversized requests with HTTP 413.
  - Uploads to Supabase Storage bucket `hostelshare-media` (`/avatars`, `/items`) with local static serving fallback.
- **HTTP Cyber Defense Headers**:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Permissions-Policy: camera=(), microphone=(), geolocation=()`

---

## Environment Configuration (`.env`)

```ini
# 1. Supabase Hosted PostgreSQL (Use Connection Pooler on port 5432/6543 for IPv4 compatibility)
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@aws-0-YOUR_REGION.pooler.supabase.com:5432/postgres

# 2. Supabase Storage Configuration
# IMPORTANT: Use the service_role key to bypass RLS policies during server uploads
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_KEY=YOUR_SUPABASE_SERVICE_ROLE_KEY
SUPABASE_BUCKET=hostelshare-media

# 3. Security & JWT
JWT_SECRET=supersecretjwtkey_change_me_in_production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# 4. CORS Origins (Set to your Vercel URL in production)
ALLOWED_ORIGINS=https://your-frontend.vercel.app

# 5. Dev Mock OTP
DEV_MOCK_OTP=123456

# 6. Host & Port
HOST=0.0.0.0
PORT=8000
```

> **Note:** If `DATABASE_URL` is left empty, the server automatically defaults to `sqlite:///./hostelshare.db` for offline local testing!

---

## Local Development & Testing

### 1. Install Dependencies
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Run the Development Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive API documentation:
- Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 3. Run Cyber Defense & Lifecycle Test Suites
```bash
# Automated security & rate limiting verification
python tests/test_cyber_defense.py

# Full business logic & dual-handshake lifecycle verification
python tests/test_flow.py
```

### 4. Ephemeral Chat Purge Script
```bash
python scripts/purge_ephemeral.py
```

---

## Deploying to Render

You can deploy the backend using the root `render.yaml` or create a new Web Service on Render:
- **Root Directory**: `backend`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**: Add `DATABASE_URL`, `JWT_SECRET`, `ALLOWED_ORIGINS`, `SUPABASE_URL`, `SUPABASE_KEY` (use `service_role` key), `SUPABASE_BUCKET`.
