# HostelShare: Campus Peer-to-Peer Rental and Utility-Sharing Service

> A production-ready, privacy-first peer-to-peer equipment and utility sharing platform designed for university hostels.

---

## Architecture & Directory Layout

```
Hostel_rental_service/
├── render.yaml               # Render web service blueprint for backend deployment
├── backend/                  # FastAPI 0.111+ & SQLAlchemy 2.0 Backend
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py       # Phone OTP (mock 123456) + JWT generation + Rate limiting
│   │   │   ├── users.py      # Profile onboarding, avatar upload & sanitized /u/:username
│   │   │   ├── items.py      # Item CRUD, photo upload & filtered home feed
│   │   │   ├── rentals.py    # Dual-handshake state machine, PIN masking & reviews
│   │   │   ├── feedback.py   # Campus project & faculty feedback system
│   │   │   └── chat.py       # In-app chat with mutual privacy shield
│   │   ├── models/           # User, Item, RentalRequest, Chat, Message, Review, Feedback
│   │   ├── schemas/          # Pydantic schemas (with strict PublicProfileOut)
│   │   ├── core/
│   │   │   ├── config.py     # Settings (DATABASE_URL, JWT, CORS, Supabase)
│   │   │   ├── database.py   # Engine, SessionLocal, auto table creation
│   │   │   ├── sanitization.py# XSS escaping, URI sanitization & Rate limiters
│   │   │   └── security.py   # JWT utils, EXIF stripper, Supabase Storage, 5MB upload guard
│   │   └── main.py           # FastAPI app, Security Headers middleware, CORS
│   ├── scripts/
│   │   └── purge_ephemeral.py# Standalone script to drop expired chats
│   ├── tests/
│   │   ├── test_flow.py      # Comprehensive automated lifecycle tests
│   │   └── test_cyber_defense.py # Automated XSS, rate limiting & security headers tests
│   ├── .env.example
│   ├── requirements.txt
│   └── README.md
├── frontend/                 # React 18 + Vite + Tailwind CSS Frontend
│   ├── src/
│   │   ├── components/       # Navbar, ItemCard, HandshakeModal, PhoneRevealBanner, ReviewModal
│   │   ├── pages/            # HomeFeed, ItemDetail, ProfilePage, ChatRoom, LoginModal, CreateListing, MyRentals, FeedbackPage
│   │   ├── services/         # Axios client with JWT interceptor & API endpoints
│   │   ├── App.jsx           # Routes and global auth state
│   │   ├── main.jsx          # React DOM entry
│   │   └── index.css         # Glassmorphic Tailwind styling
│   ├── vercel.json           # Vercel SPA rewrite routing rules
│   ├── vite.config.js        # Configured for Vite build
│   ├── package.json
│   ├── tailwind.config.js
│   ├── .env.example
│   └── README.md
└── doc/                      # University Software Engineering Course Deliverables
    ├── SRS.md                # IEEE 830-compliant Software Requirements Specification
    ├── DATABASE_SCHEMA.md    # ERD (Mermaid) + Data dictionary with cascade specifications
    ├── STATE_MACHINE.md      # Dual-handshake state machine and flowchart specs
    └── API_SPECS.md          # REST API contracts, schemas, and sample cURLs
```

---

## Core Value Propositions & Business Logic

1. **Identity & Auth**:
   - Phone OTP verification (Mock dev test code: `123456`).
   - Profile creation: Display Name, unique `@username` (regex `^[a-zA-Z0-9_]{3,20}$`), and confidential Hostel Block / Wing.
   - Public profile (`/u/:username`): **Strict Privacy Shield** — never leaks phone number or room/hostel wing.

2. **Listings & Dynamic Feed**:
   - Category filtering (`Electronics`, `Tools`, `Academic`, `Daily Living`).
   - Free vs. Paid toggle (₹0 for free borrows).
   - Real-time search by title and description.

3. **Rental State Machine & Dual Handshake**:
   - `PENDING` $\to$ `ACCEPTED` $\to$ `ACTIVE` $\to$ `RETURNED` $\to$ `COMPLETED` (or `CANCELLED`).
   - **Handover Handshake**: Lender receives secret 6-digit PIN upon acceptance. Borrower inputs PIN upon meeting to transition to `ACTIVE`.
   - **Return Handshake**: Borrower receives secret 6-digit PIN during return. Lender inputs PIN upon inspecting item to transition to `RETURNED`.
   - **Trust Reviews**: Mandatory post-return 1-to-5 star ratings recalculating overall peer trust score.

4. **In-App Chat & Mutual Privacy Shield**:
   - Dedicated deal chat room opened automatically upon rental acceptance.
   - Masked phone numbers by default (`+91 ••••• ••123`).
   - One-tap "Share Phone Number" consent button; numbers are unmasked **if and only if both parties agree**.
   - Ephemeral auto-expiration: `return_time + 24 hours` (or `cancellation_time + 72 hours`).

---

## Media Storage Architecture: Supabase Storage vs. Local vs. Cloudinary

### Why were images saved locally?
The backend code in `app/core/security.py` is pre-configured to upload images directly to **Supabase Storage** (`hostelshare-media` bucket). However, when the backend connects using the public `anon` key without a configured Row-Level Security (RLS) INSERT policy, Supabase rejects uploads with `403 Unauthorized: new row violates row-level security policy`. The backend catches this error and gracefully falls back to `./uploads/` for offline local development.

> [!WARNING]
> **Ephemeral Disk on Cloud Hosts**: On platforms like Render, the container filesystem is ephemeral. Any images saved locally to `./uploads/` are permanently wiped on redeploys or free-tier sleep cycles. Images must be stored in remote cloud storage.

### Feasibility for ~100 Users: Should you switch to Cloudinary?
* **Storage Calculation for 100 Users**:
  * 100 user avatars × ~150 KB (after PIL compression) = **~15 MB**
  * 100 users × ~3 listing photos × ~250 KB = **~75 MB**
  * **Total Storage**: **~90 MB to 150 MB**
* **Free Tier Comparison**:
  * **Supabase Storage**: Provides **1 GB (1,000 MB)** of free file storage and 2 GB/month bandwidth. 100 users consume **less than 10%** of the Supabase free tier!
  * **Cloudinary**: Provides 25 GB monthly credits.
* **Verdict**: **Stick with Supabase Storage.** Because Supabase already powers your PostgreSQL database, keeping your media in Supabase Storage eliminates the need for an extra vendor, additional SDKs, or redundant API keys. All you need is to provide the `service_role` key or enable the storage RLS policy.

### How to Enable Supabase Storage in 60 Seconds:
1. Go to your **Supabase Dashboard** -> **Storage** -> Click **New Bucket**.
2. Name it `hostelshare-media` and toggle **Public bucket** to **ON**.
3. Go to **Project Settings** -> **API** -> Under **Project API keys**, copy the **`service_role`** key.
4. Set `SUPABASE_KEY=<your_service_role_key>` in your backend `.env` and Render dashboard.

---

## Cyber Security & Defense Architecture

HostelShare implements layered defenses validated by an automated test suite (`tests/test_cyber_defense.py`):

1. **XSS (Cross-Site Scripting) Neutralization**:
   - **Backend**: `sanitize_text()` normalizes control characters and applies HTML entity escaping (`<` $\to$ `&lt;`, `>` $\to$ `&gt;`, `"` $\to$ `&quot;`, `'` $\to$ `&#x27;`) to all stored text (titles, descriptions, reviews, feedback, chat messages).
   - **Frontend**: Zero usage of `dangerouslySetInnerHTML`. React JSX auto-escapes all rendered text nodes.
   - **URI Scheme Injection**: URLs pass through `sanitize_url()` and `resolveImageUrl()`, blocking dangerous schemes (`javascript:`, `vbscript:`, `data:text/html`).

2. **Rate Limiting & Anti-Abuse Throttling**:
   - **Handshake & Return PINs**: `verify_pin_rate_limit()` restricts PIN verification to **5 failed attempts max**, locking the rental for **300 seconds** upon threshold breach to thwart brute-force attacks.
   - **Phone OTP Generation**: `/api/auth/send-otp` is throttled to **5 requests per 60 seconds** per phone number to prevent SMS bombing.
   - **OTP Verification**: `/api/auth/verify-otp` is throttled to **5 attempts per 120 seconds** per phone number to prevent OTP brute-forcing.

3. **File Upload & DoS Defense**:
   - **Payload Ceiling**: 5 MB upload limit enforced server-side; oversized uploads are rejected immediately with `413 Content Too Large` before memory allocation.
   - **EXIF & Privacy Stripping**: Pillow automatically strips all EXIF metadata (camera models, timestamps, and GPS coordinates) before storage, protecting student campus locations.

4. **Access Control & IDOR Protection**:
   - Rental detail endpoints verify that `current_user.id` is either the lender or borrower (`403 Forbidden` for third parties).
   - Handover PIN is visible **only** to the lender; Return PIN is visible **only** to the borrower.

5. **HTTP Cyber Defense Headers**:
   - `X-Content-Type-Options: nosniff` (MIME sniffing prevention)
   - `X-Frame-Options: DENY` (Clickjacking mitigation)
   - `X-XSS-Protection: 1; mode=block`
   - `Referrer-Policy: strict-origin-when-cross-origin`
   - `Permissions-Policy: camera=(), microphone=(), geolocation=()`

---

## Production Deployment Guide

### A. Deploy Backend to Render

1. Create a new **Web Service** on [Render](https://render.com) and connect your GitHub repository.
2. Select the repository root or use the included [render.yaml](render.yaml) blueprint:
   * **Root Directory**: `backend`
   * **Runtime**: `Python 3`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   * **Health Check Path**: `/health`
3. Add Environment Variables on Render:
   * `DATABASE_URL`: Your Supabase connection string.
     *(Use the Session/Transaction Pooler string on port 5432 or 6543, e.g. `aws-0-...pooler.supabase.com:5432`, which supports IPv4).*
   * `JWT_SECRET`: A secure 64-char random string.
   * `ALLOWED_ORIGINS`: Your Vercel frontend URL (e.g., `https://hostelshare.vercel.app`).
   * `SUPABASE_URL`: `https://<your-project-ref>.supabase.co`
   * `SUPABASE_KEY`: Your Supabase `service_role` secret key.
   * `SUPABASE_BUCKET`: `hostelshare-media`
   * `DEV_MOCK_OTP`: `123456`

### B. Deploy Frontend to Vercel

1. Import your GitHub repository on [Vercel](https://vercel.com).
2. Configure project settings:
   * **Framework Preset**: `Vite`
   * **Root Directory**: `frontend`
   * **Build Command**: `npm run build`
   * **Output Directory**: `dist`
3. Add Environment Variable:
   * `VITE_API_BASE_URL`: `https://<your-render-backend-name>.onrender.com` *(omit trailing slash)*
4. Single-Page Application (SPA) routing is pre-configured via [frontend/vercel.json](frontend/vercel.json), preventing 404 errors on browser page reloads.

---

## Local Development & Testing

### 1. Run Backend Locally
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Run Cyber Defense Test Suite
```bash
python backend/tests/test_cyber_defense.py
```

### 3. Run Frontend Locally
```bash
cd frontend
npm install
npm run dev
```
Accessible at [http://localhost:5173](http://localhost:5173).
