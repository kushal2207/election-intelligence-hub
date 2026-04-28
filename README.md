# 🗳️ Election Intelligence Hub

AI-powered Election Intelligence Hub for Indian elections — combining a **Neo4j Knowledge Graph**, **Weaviate Vector Search**, and **LLM-powered AI Chat** to deliver real-time, cited election insights.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![Vite](https://img.shields.io/badge/Vite-8-646CFF?logo=vite)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-4-38BDF8?logo=tailwindcss)

---

## ✨ Features

- **AI Chat Interface** — Ask any election question; get cited, sourced answers
- **Neo4j Knowledge Graph** — Structured election data (candidates, constituencies, parties, results)
- **Weaviate Vector Search** — Semantic search across election documents
- **Google OAuth 2.0** — Secure authentication with JWT session tokens
- **Election Hub Sidebar** — Live timelines, seat stats, upcoming election dates
- **Multi-language Support** — Translation service for regional language queries
- **Web Search Fallback** — Falls back to web search for general political questions
- **Location-aware** — Auto-detects jurisdiction on first visit

---

## 📁 Project Structure

```
├── main.py                  # FastAPI app entrypoint
├── config.py                # Pydantic settings (env validation)
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template (copy to .env)
├── auth/                    # Google OAuth + JWT auth
│   ├── google_oauth.py
│   ├── jwt_handler.py
│   ├── middleware.py
│   └── dependencies.py
├── routes/                  # API route handlers
│   ├── auth.py              # /auth/* endpoints
│   └── query.py             # /api/v1/* endpoints
├── services/                # Business logic layer
│   ├── neo4j_service.py     # Knowledge graph queries
│   ├── vector_service.py    # Weaviate vector search
│   ├── llm_service.py       # LLM synthesis (Groq)
│   ├── translation_service.py
│   └── web_search_service.py
├── models/                  # Pydantic request/response models
├── cypher/                  # Neo4j schema definitions
├── frontend/                # React + Vite + Tailwind CSS
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── contexts/        # Auth & Jurisdiction contexts
│   │   └── pages/           # Dashboard, Detail, Login
│   └── package.json
└── schema_documentation.md  # Knowledge graph schema docs
```

---

## 🚀 Quick Start

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| **Python** | 3.11+ | Backend runtime |
| **Node.js** | 18+ | Frontend tooling |
| **Neo4j** | 5.x (or Aura) | Knowledge graph database |
| **Weaviate** | Cloud or local | Vector search engine |

### 1. Clone the Repository

```bash
git clone https://github.com/kushal2207/election-intelligence-hub.git
cd election-intelligence-hub
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your actual credentials:

```env
# --- Core Services ---
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_actual_password
WEAVIATE_URL=https://your-cluster.weaviate.network
WEAVIATE_API_KEY=your_weaviate_key
GROQ_API_KEY=your_groq_key
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key

# --- Google OAuth 2.0 ---
GOOGLE_CLIENT_ID=xxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxx
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback

# --- JWT ---
JWT_SECRET=generate_a_long_random_string_here
JWT_ALGORITHM=HS256
```

### 3. Start the Backend

```bash
# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be live at **http://localhost:8000**  
API docs at **http://localhost:8000/docs**

### 4. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be live at **http://localhost:5173**

---

## 🔌 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/health` | ❌ | Health check |
| `GET` | `/auth/login` | ❌ | Initiate Google OAuth |
| `GET` | `/auth/callback` | ❌ | OAuth callback handler |
| `POST` | `/api/v1/query` | ✅ JWT | Query the AI assistant |

Full interactive docs available at `/docs` (Swagger UI) when the backend is running.

---

## 🔑 Getting API Keys

| Service | Where to Get |
|---------|-------------|
| **Neo4j Aura** | [neo4j.com/cloud/aura](https://neo4j.com/cloud/aura/) (free tier available) |
| **Weaviate Cloud** | [console.weaviate.cloud](https://console.weaviate.cloud/) (free sandbox) |
| **Groq** | [console.groq.com](https://console.groq.com/) (free tier) |
| **Anthropic** | [console.anthropic.com](https://console.anthropic.com/) |
| **Google OAuth** | [console.cloud.google.com](https://console.cloud.google.com/) → APIs & Services → Credentials |

---

## 🛡️ Security

- All secrets are loaded from `.env` (never committed — see `.gitignore`)
- JWT tokens for session authentication
- CORS restricted to known origins
- Input validation via Pydantic models
- OAuth state parameter protected by session middleware

---

## 📄 License

MIT

---

<p align="center">
  Built with ❤️ for Indian democracy
</p>
