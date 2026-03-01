# 🖥️ Backend – README

## 📦 Requirements

- Python 3.13
- PostgreSQL
- FAISS
- pip
- OpenAI/Gemini/Groq api keys (any one will suffice)

## ⚙️ Installation & Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # on Linux/Mac
venv\Scripts\activate      # on Windows

pip install -r requirements.txt
```

## 🔑 Environment Variables

Create a `.env` file in `backend/` with:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/dbname
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here

DEV_ENV=True

FAISS_INDEX_DIR="./faiss_index"

CLERK_SECRET_KEY=your_clerk_secret_key_here
CLERK_WEBHOOK_SECRET=your_clerk_webhook_secret_here

ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174
```

## 🔑 Obtaining API Keys

- **OpenAI API Key** → Get from [OpenAI Dashboard](https://platform.openai.com/settings/organization/api-keys)
- **Google Gemini API Key** → Get from [Google AI Studio](https://aistudio.google.com/apikey)
- **Groq API Key** → Get from [Groq Console](https://console.groq.com/keys)
- **Clerk Keys** →
  - `CLERK_SECRET_KEY` & `CLERK_WEBHOOK_SECRET` → Head to [Clerk Dashboard](https://dashboard.clerk.com/) -> Select your application -> Configure -> API keys

## ▶️ Run

```bash
py app.py
```

---

## TODO

- [x] Vectorization of plain text data - only when relevant
- [x] Getting structured data from plain text and storing it in the database
- [x] Add react agent.
- [x] Add conversation memory - multiple.
- [x] Testing Stage 1: Thoroughly test the current functionality
  - [x] Conversation Memory
  - [x] Vector Memory
  - [x] Db Memory
  - [x] Data about user themselves are being stored in the database
- [x] Conversation CRUD
- [x] Add user authentication.
- [x] Store user data in the database
- [x] Testing Stage 2: Thoroughly test the current functionality
  - [x] Conversation CRUD
  - [x] Authentication and user data
- [x] Dashboard: Other crud operations (Memories Dashboard, Profile Separation, Global Search Filter)
- [x] Multiagent structure for more efficiency