# 🤖 MultiModule AI System

<div align="center">

**A full-stack AI-powered productivity platform with 5 intelligent modules**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com)
[![Vite](https://img.shields.io/badge/Vite-5.0+-646CFF.svg)](https://vitejs.dev)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.3+-38BDF8.svg)](https://tailwindcss.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[🌐 Live Demo](#-live-demo) • [✨ Features](#-features) • [🛠️ Local Setup](#️-local-setup) • [🚀 Deployment](#-deployment) • [📖 API Docs](#-api-reference)

</div>

---

## 🌐 Live Demo

| Service | URL | Status |
|---|---|---|
| 🖥️ **Frontend** | [https://multimodule-ai-system-backend.vercel.com](https://multi-module-ai-system.vercel.app/) | ✅ Live |
| ⚙️ **Backend API** | [https://multimodule-ai-system-backend.onrender.com](https://multimodule-ai-system-backend.onrender.com) | ✅ Live |
| 📄 **Swagger Docs** | [https://multimodule-ai-system-backend.onrender.com/api/docs](https://multimodule-ai-system-backend.onrender.com/api/docs) | ✅ Live |
| ❤️ **Health Check** | [https://multimodule-ai-system-backend.onrender.com/health](https://multimodule-ai-system-backend.onrender.com/health) | ✅ Live |

> 💡 **Demo credentials:** `demo@example.com` / `demo123`

---

## ✨ Features

### 📄 Resume Analyzer
- Upload PDF or TXT resumes
- Automatic skill extraction using NLP
- ATS (Applicant Tracking System) scoring
- Match score against job requirements
- Missing skills detection & feedback

### 🛡️ Spam / Phishing Detector
- ML-based email classification (TF-IDF + Logistic Regression)
- Confidence score with probability output
- Pattern-based phishing link detection
- Real-time analysis with history tracking

### 📝 Notes Summarizer
- Extractive text summarization
- Bullet-point structured output
- Customizable summary length
- Preserves key context and meaning

### 🤖 AI Chatbot
- DistilGPT-2 transformer model (or rule-based fallback)
- Conversation history & session management
- Intent recognition (identity, coding, AI topics, etc.)
- Context-aware multi-turn conversations

### 📊 Analytics Dashboard
- Usage stats across all modules
- Activity timeline & historical data
- Module performance metrics
- Interactive charts with Recharts

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, Vite 5, TailwindCSS, Recharts, Axios |
| **Backend** | FastAPI, Uvicorn, SQLAlchemy, Pydantic v2 |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Auth** | JWT (python-jose + bcrypt) |
| **AI/ML** | HuggingFace Transformers (DistilGPT-2), pure Python NLP |
| **PDF** | PyPDF2 |
| **Frontend Host** | Vercel |
| **Backend Host** | Render |

---

## 📁 Project Structure

```
MultiModule-AI-System/
├── 📁 backend/
│   ├── 📄 main.py              # FastAPI app entry point
│   ├── 📄 config.py            # Environment config
│   ├── 📄 requirements.txt     # Python dependencies
│   ├── 📁 routes/
│   │   ├── 📄 resume.py        # Resume analysis endpoints
│   │   ├── 📄 spam.py          # Spam detection endpoints
│   │   ├── 📄 summary.py       # Summarization endpoints
│   │   ├── 📄 chatbot.py       # Chatbot endpoints
│   │   └── 📄 analytics.py     # Analytics endpoints
│   ├── 📁 services/
│   │   ├── 📄 resume_service.py
│   │   ├── 📄 spam_service.py
│   │   ├── 📄 summary_service.py
│   │   ├── 📄 chatbot_service.py
│   │   └── 📄 lazy_loader.py
│   ├── 📁 models/
│   │   └── 📄 models.py        # SQLAlchemy DB models
│   ├── 📁 database/
│   │   └── 📄 database.py      # DB init & session
│   └── 📁 utils/
│       ├── 📄 logger.py
│       └── 📄 security.py
│
├── 📁 frontend/
│   ├── 📄 index.html
│   ├── 📄 vite.config.js
│   ├── 📄 package.json
│   └── 📁 src/
│       ├── 📄 App.jsx           # Router & layout
│       ├── 📄 main.jsx
│       ├── 📁 pages/
│       │   ├── 📄 Dashboard.jsx
│       │   ├── 📄 Resume.jsx
│       │   ├── 📄 Spam.jsx
│       │   ├── 📄 Summary.jsx
│       │   ├── 📄 Chatbot.jsx
│       │   └── 📄 Analytics.jsx
│       ├── 📁 components/
│       │   ├── 📄 Layout.jsx
│       │   └── 📄 ErrorAlert.jsx
│       └── 📁 services/
│           └── 📄 api.js        # Axios API client
│
├── 📄 .env.example
├── 📄 .gitignore
├── 📄 render.yaml              # Render deploy config
└── 📄 README.md
```

---

## 🛠️ Local Setup

### Prerequisites

- **Python** 3.8+
- **Node.js** 16+
- **Git**

---

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Ramsingh4656/MultiModule-AI-System.git
cd MultiModule-AI-System
```

---

### 2️⃣ Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file inside `backend/`:

```env
SECRET_KEY=your-secret-key-change-this
DEBUG=True
DATABASE_URL=sqlite:///./ai_productivity.db
```

Start the backend:

```bash
python main.py
```

Backend runs at → **http://localhost:8000**
Swagger docs at → **http://localhost:8000/api/docs**

---

### 3️⃣ Frontend Setup

Open a **new terminal**:

```bash
cd frontend

# Install dependencies
npm install
```

Create a `.env` file inside `frontend/`:

```env
VITE_API_URL=http://localhost:8000/api
```

Start the frontend:

```bash
npm run dev
```

Frontend runs at → **http://localhost:5173**

---

### 4️⃣ Quick Launch (Windows)

Alternatively, just double-click:

```
startup.bat
```

This starts both backend and frontend automatically.

---

### ✅ Local URLs Summary

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/api/docs |
| ReDoc | http://localhost:8000/api/redoc |
| Health Check | http://localhost:8000/health |

---

## 🚀 Deployment

### Backend → Render (Free, 24/7)

The backend is deployed on [Render](https://render.com) with GitHub auto-deploy.

**Setup:**
1. Push `backend/` contents to GitHub repo root
2. Go to [render.com](https://render.com) → New Web Service
3. Connect GitHub repo, select **Python** runtime
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add env vars: `SECRET_KEY`, `DEBUG=False`
6. Deploy ✅

**Keep it 24/7 (prevent sleep):**
- Set up [UptimeRobot](https://uptimerobot.com) (free) to ping `/health` every 5 minutes

---

### Frontend → Vercel (Free, Always-On)

1. Push `frontend/` to GitHub
2. Go to [vercel.com](https://vercel.com) → New Project → Import repo
3. Framework: **Vite** (auto-detected)
4. Add Environment Variable:
   ```
   VITE_API_URL = https://multimodule-ai-system-backend.onrender.com/api
   ```
5. Deploy ✅

Every `git push` to `main` triggers an automatic redeploy on both platforms.

---

## 📖 API Reference

Interactive docs available at:
- **Swagger UI:** [/api/docs](https://multimodule-ai-system-backend.onrender.com/api/docs)
- **ReDoc:** [/api/redoc](https://multimodule-ai-system-backend.onrender.com/api/redoc)

### Key Endpoints

#### Resume
```http
POST /api/resume/analyze        # Upload & analyze resume (PDF/TXT)
GET  /api/resume/history        # Get analysis history
GET  /api/resume/analysis/{id}  # Get specific analysis
```

#### Spam Detection
```http
POST /api/spam/check            # Check email/text for spam
GET  /api/spam/history          # Get check history
GET  /api/spam/stats            # Get spam statistics
```

#### Summarization
```http
POST /api/summary/create        # Summarize text
GET  /api/summary/history       # Get summary history
GET  /api/summary/detail/{id}   # Get specific summary
```

#### Chatbot
```http
POST /api/chat/message          # Send message
GET  /api/chat/sessions         # Get all sessions
GET  /api/chat/history/{id}     # Get session history
DELETE /api/chat/session/{id}   # Delete session
GET  /api/chat/model-info       # Get model info
```

#### Analytics
```http
GET /api/analytics/dashboard        # Overall stats
GET /api/analytics/usage-by-module  # Per-module usage
GET /api/analytics/monthly-usage    # Monthly breakdown
GET /api/analytics/activity-timeline # Activity over time
```

---

## ⚙️ Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | *(required)* | JWT signing key |
| `DEBUG` | `False` | Enable debug mode |
| `DATABASE_URL` | `sqlite:///./ai_productivity.db` | Database connection string |

### Frontend (`frontend/.env`)

| Variable | Default | Description |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000/api` | Backend API base URL |

---

## 📊 Performance

| Module | Response Time | Notes |
|---|---|---|
| Resume Analyzer | 2–5 sec | PDF parsing + NLP |
| Spam Detector | < 1 sec | Pure Python, no ML deps |
| Summarizer | 1–3 sec | Extractive NLP |
| Chatbot | 1–2 sec | DistilGPT-2 or rule-based |
| Analytics | < 500ms | DB aggregation queries |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 👨‍💻 Author

**Ramsingh4656**
- GitHub: [@Ramsingh4656](https://github.com/Ramsingh4656)
- Project: [MultiModule-AI-System](https://github.com/Ramsingh4656/MultiModule-AI-System)

---

## ⭐ Show Your Support

If you found this project helpful, please consider giving it a **star** on GitHub!

[![Star this repo](https://img.shields.io/github/stars/Ramsingh4656/MultiModule-AI-System?style=social)](https://github.com/Ramsingh4656/MultiModule-AI-System)
