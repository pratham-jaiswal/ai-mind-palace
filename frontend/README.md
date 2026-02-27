# 🌐 Frontend – README

## 📦 Requirements

- Node.js 22
- npm / yarn / pnpm

## ⚙️ Installation & Setup

```bash
cd frontend
npm install
```

## 🔑 Environment Variables

Create a `.env` file in `frontend/` with:

```env
VITE_BACKEND_URL=http://127.0.0.1:5000
VITE_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here
```

## 🔑 Obtaining API Keys

- **Clerk Keys** →
  - `VITE_CLERK_PUBLISHABLE_KEY` → Head to [Clerk Dashboard](https://dashboard.clerk.com/) -> Select your application -> Configure -> API keys

## ▶️ Run

```bash
npm run dev
```

## 📝 TODO

- [x] Chat Interface
- [x] Sidebar for conversation list
- [x] New Chat icon
- [x] Delete Chat
- [x] Dashboard CRUD (People, Projects, Decisions)
- [x] Mind Map Graph UI
