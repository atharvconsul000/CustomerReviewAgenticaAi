# Customer Support Analyzer & AI Agent

![Status](https://img.shields.io/badge/Status-Active-success)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-000000?logo=next.js&logoColor=white)

A full-stack, AI-powered customer support platform that uses **Retrieval-Augmented Generation (RAG)** to automate customer troubleshooting and provides advanced 3D **Principal Component Analysis (PCA)** analytics for administrators.

## 🚀 Live Demo
- **Frontend:** [https://meticulous-unity-production-2005.up.railway.app](https://meticulous-unity-production-2005.up.railway.app)
- **Backend API:** FastAPI running on Railway

## ✨ Key Features

### 🔐 Secure Role-Based Access Control (RBAC)
- Robust JWT-based authentication system.
- Strict route protection and data compartmentalization between `admin` and `user` roles.
- Passwords cryptographically hashed via `passlib`.

### 🧠 Dual-Persona Retrieval-Augmented Generation (RAG)
All support tickets are converted into mathematical vector embeddings and stored in a high-dimensional ChromaDB space. The AI dynamically changes its persona based on the logged-in user:
- **For Customers:** Searches past semantically similar tickets and extracts the exact resolution offered by past agents, providing instant, accurate help without revealing internal ticket numbers.
- **For Admins:** Analyzes corpus-level trends and ticket clusters to identify root causes, thematic spikes, and business vulnerabilities. 

### 📊 3D PCA Data Visualization
- Uses `scikit-learn` to mathematically compress 768-dimensional AI text embeddings into a 3D space via Principal Component Analysis.
- Renders an interactive 3D scatter plot (using Plotly) on the Admin dashboard to visually identify clusters of similar customer complaints.

## 🛠️ Technology Stack
- **Frontend:** React, Next.js, Tailwind CSS, Recharts, Plotly.js
- **Backend:** Python, FastAPI, SQLAlchemy
- **Database:** PostgreSQL (Relational), ChromaDB (Vector Store)
- **AI / LLMs:** LangChain, Groq (Llama 3.3), Scikit-Learn
- **Deployment:** Railway

## 💻 Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/atharvconsul000/CustomerReviewAgenticaAi.git
cd CustomerReviewAgenticaAi
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:
```env
DATABASE_URL=postgresql://username:password@localhost/dbname
JWT_SECRET=your_super_secret_key
GROQ_API_KEY=your_groq_api_key
```

Run the backend server:
```bash
uvicorn main:app --reload
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
```

Create a `.env.local` file in the `frontend/` directory:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the frontend development server:
```bash
npm run dev
```

## 📜 License
This project is licensed under the MIT License.
