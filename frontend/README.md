# HostelShare - Frontend Web Application

High-performance, mobile-responsive React web application built with Vite and Tailwind CSS for peer-to-peer campus rentals.

---

## Features

- **Local Wi-Fi Multi-Phone Testing**:
  - Configured with `server: { host: "0.0.0.0", port: 5173 }`.
  - Scan terminal QR code with any smartphone connected to the same campus Wi-Fi network to test instantly.
- **Mutual Privacy Shield**:
  - Masked phone numbers in deal chat headers (`+91 ••••• ••123`).
  - One-tap mutual consent toggle reveals full contact details only when both parties click "Share Phone Number".
- **Dual-Handshake State Machine UI**:
  - Live state tracking (`PENDING` $\to$ `ACCEPTED` $\to$ `ACTIVE` $\to$ `RETURNED` $\to$ `COMPLETED`).
  - Interactive PIN modal for displaying secret 4-digit codes and submitting verification.
- **Peer Reviews & Campus Feedback**:
  - Interactive 1-to-5 star rating and feedback modal after item return.
  - Dedicated campus feedback system for students and faculty.
- **Sanitized Public Profiles (`/u/:username`)**:
  - Public view strictly concealing phone numbers and room/hostel wing locations.
- **XSS & URI Defense**:
  - Pure React JSX rendering with zero raw HTML injection (`dangerouslySetInnerHTML`).
  - Defensive URI resolver blocking `javascript:`, `vbscript:`, and unsafe schemes.

---

## Environment Configuration (`.env`)

```ini
# Development: Local backend
VITE_API_BASE_URL=http://localhost:8000

# Production on Vercel: Render backend URL (no trailing slash)
# VITE_API_BASE_URL=https://your-backend-name.onrender.com
```

---

## Local Development

```bash
cd frontend
npm install
npm run dev
```

Visit [http://localhost:5173](http://localhost:5173).

---

## Production Build & Deploying to Vercel

### 1. Build Verification
```bash
npm run build
```
Generates production assets in the `dist/` directory.

### 2. Vercel Deployment Settings
- **Framework Preset**: `Vite`
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Environment Variables**:
  - `VITE_API_BASE_URL`: `https://your-backend-name.onrender.com`
- **SPA Routing**: Handled automatically via `vercel.json` (`rewrites: [ { "source": "/(.*)", "destination": "/index.html" } ]`), preventing 404 errors on browser page reloads.
