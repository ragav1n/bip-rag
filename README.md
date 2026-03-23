# BIP RAG — DEW21 Document Assistant

A local RAG (Retrieval-Augmented Generation) system that answers questions about DEW21's Terms & Conditions and regulatory documents. Built for the academic project **BIP — GenAI meets Reality** at FH Dortmund.

All processing runs entirely on-device — no data leaves the machine.

---

## Architecture

```
bip_rag/
├── rag_english/       Python backend (FastAPI) + English vector store
│   ├── api.py         REST API — handles both EN and DE queries
│   ├── ingest.py      Ingestion pipeline — chunks, embeds, stores docs
│   ├── docs/          English source documents (.txt)
│   └── requirements.txt
│
├── rag_german/        German vector store
│   ├── ingest.py      Ingestion pipeline for German docs
│   └── docs/          German source documents (.txt)
│
└── rag_frontend/      React chat UI
    ├── src/App.tsx    Main application
    └── vite.config.ts Proxies /api → localhost:8000
```

**Stack:**
- **Embeddings:** `nomic-ai/nomic-embed-text-v1` (EN), `paraphrase-multilingual-mpnet-base-v2` (DE)
- **Vector DB:** ChromaDB (local, persistent)
- **LLM:** llama3.2 via Ollama (fully local)
- **Backend:** FastAPI + Python
- **Frontend:** React + TypeScript + Vite + Tailwind CSS

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.com) installed and running

---

## Setup

### 1. Pull the LLM

```bash
ollama pull llama3.2
```

### 2. Backend

```bash
cd rag_english
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Add documents

Place your source `.txt` files in:
- `rag_english/docs/` — English documents
- `rag_german/docs/` — German documents

### 4. Ingest documents

```bash
# English
cd rag_english
source venv/bin/activate
python ingest.py

# German (uses same venv)
cd ../rag_german
python ingest.py
```

This splits each document into chunks, embeds them, and stores them in ChromaDB. Run once — only re-run if documents change.

### 5. Frontend

```bash
cd rag_frontend
npm install
```

---

## Running

Start both services (two terminals):

```bash
# Terminal 1 — Backend
cd rag_english
source venv/bin/activate
uvicorn api:app --reload --port 8000

# Terminal 2 — Frontend
cd rag_frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

---

## API

The backend exposes three endpoints:

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/query` | Query the RAG pipeline |
| `POST` | `/title` | Generate a short title for a query |
| `GET` | `/health` | Check status and chunk counts |

**Query example:**
```json
POST /query
{ "query": "Was passiert bei Zahlungsverzug?", "language": "de" }

→ { "answer": "...", "sources": [...] }
```

Supported `language` values: `"de"` (German), `"en"` (English).

---

## Features

- Bilingual — German and English, each with its own optimised embedding model
- Section-aware chunking — respects legal document structure (§1, §2, …)
- Chat history — persisted in localStorage, survives page refresh
- AI-generated chat titles — LLM summarises each conversation into a short title
- Markdown rendering — structured answers with bold §-references and bullet points
- Fully local — no API keys, no cloud, no data leaves the machine
