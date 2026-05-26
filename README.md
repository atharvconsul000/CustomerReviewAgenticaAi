# Customer Support Analyzer

A full-stack Agentic RAG and data science visualization app for customer support tickets.

## Stack

- **Frontend**: React with Next.js, Tailwind CSS, Plotly.js
- **Backend**: FastAPI
- **Relational Database**: SQLite locally, PostgreSQL-ready through `DATABASE_URL`
- **Vector Store**: Local ChromaDB, with a cosine-search fallback for lightweight environments
- **AI/Data Layer**: LangChain tool wrappers, scikit-learn embeddings, PCA, and similarity search
- **Auth**: JWT bearer auth with role-based access

## What Works Now

- `/auth/signup`, `/auth/login`, and `/auth/me` support JWT sessions.
- `/reviews` lets signed-in users submit and view their own reviews.
- `/admin/reviews` and `/admin/reviews/analysis` let admins analyze user review data.
- `/plot-data` generates support tickets, converts each ticket into a 768-feature local embedding, projects those vectors into 2D with PCA, and returns Plotly-ready points.
- `/chat` routes questions to one of two tools:
  - **Semantic Search Tool** for questions like "What are the most common complaints about login?"
  - **Ticket Counter Tool** for questions like "How many tickets mention billing?"
- The frontend has a customer review portal and an admin dashboard. Agentic AI and vector visualization are admin-only.

The current implementation uses a free local embedding path so the project runs without OpenAI, Gemini, or Groq keys. A hosted LLM provider can be added later by replacing the local router with a LangChain agent executor and provider-specific chat model.

## Run It

Backend:

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:3000`.

Demo accounts:

- Admin: `admin@example.com` / `admin123`
- User: `user@example.com` / `user123`

For PostgreSQL deployment, set:

```bash
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DB_NAME
JWT_SECRET_KEY=replace-this-in-production
```

## Useful Commands

Generate the demo ticket file:

```bash
python backend/generate_tickets.py
```

Try the API directly:

```bash
curl http://localhost:8000/plot-data
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"How many tickets mention billing?"}'
```
