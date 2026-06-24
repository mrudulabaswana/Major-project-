# Student Management System

A full-stack feedback portal — React frontend + Python (FastAPI) backend.

## Project Structure

```
StudentManagementSystem/
├── frontend/          # React 18 + Vite + Tailwind CSS + shadcn/ui
└── backend/           # Python FastAPI + SQLAlchemy + SQLite/PostgreSQL
    ├── main.py        # All API routes + DB models
    ├── run.py         # Quick-start server
    ├── requirements.txt
    └── .env.example
```

---

## Backend — Python (FastAPI)

### Requirements
- Python 3.10+

### Setup & Run

```bash
cd backend

# 1. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) configure database
cp .env.example .env            # edit DATABASE_URL if using PostgreSQL

# 4. Start server
python run.py
# → API running at http://localhost:5000
```

SQLite is used by default — no database installation needed.

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/feedback | List all submissions (filter: ?category=&status=&rating=) |
| POST | /api/feedback | Create a submission |
| GET | /api/feedback/stats | Dashboard statistics |
| GET | /api/feedback/{id} | Single submission |
| PATCH | /api/feedback/{id}/status | Update status (new/reviewed/resolved) |
| DELETE | /api/feedback/{id} | Delete submission |
| GET | /api/healthz | Health check |

Interactive docs: http://localhost:5000/docs

---

## Frontend — React (Vite)

### Requirements
- Node.js 18+
- pnpm (or npm)

### Setup & Run

```bash
cd frontend

# 1. Install dependencies
pnpm install          # or: npm install

# 2. Point at your backend
# In vite.config.ts the proxy already forwards /api → http://localhost:5000

# 3. Start dev server
pnpm dev              # or: npm run dev
# → App running at http://localhost:5173
```

---

## Feedback Categories (6 categories × 5 sub-reasons = 30 total)

| # | Category | Sub-reasons |
|---|----------|-------------|
| 1 | Faculty Feedback | Subject knowledge, Teaching methodology, Communication skills, Doubt clarification, Punctuality |
| 2 | Course / Subject Feedback | Syllabus relevance, Study materials, Course difficulty, Lab integration, Industry alignment |
| 3 | Classroom Environment | Cleanliness, Seating comfort, Projector/AV, Lighting, Ventilation |
| 4 | Laboratory | Equipment availability, Software tools, Lab staff support, Safety measures, Practical sessions |
| 5 | Examination & Assessment | Question paper quality, Evaluation fairness, Result publication, Re-evaluation process, Internal marks |
| 6 | Infrastructure & Facilities | Library resources, Wi-Fi connectivity, Canteen, Hostel facilities, Sports facilities |

---

## Status Lifecycle

```
New  →  Reviewed  →  Resolved
```

Admin updates status inline from the dashboard table.

---

Generated: June 2026
