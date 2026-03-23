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
- **LLM:** `qwen3.5:4b` via Ollama (fully local)
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
ollama pull qwen3.5:4b
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

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/query` | Query the RAG pipeline (streaming SSE) |
| `POST` | `/title` | Generate a short AI title for a query |
| `GET` | `/health` | Check status and chunk counts |

**Query request:**
```json
{
  "query": "Was passiert bei Zahlungsverzug?",
  "language": "de",
  "tone": "standard",
  "document": "all",
  "history": [{ "role": "user", "content": "..." }, ...]
}
```

**Query response (SSE stream):**
```
data: {"type": "sources", "sources": [...]}
data: {"type": "token", "token": "..."}
data: {"type": "done"}
```

Supported `language`: `"de"` | `"en"`
Supported `tone`: `"easy"` | `"standard"` | `"technical"`
Supported `document`: `"all"` | `"strom"` | `"erdgas"` | `"schufa"` | `"creditreform"`

---

## Features

- **Bilingual** — German and English, each with its own optimised embedding model
- **Three response tones** — Simplified (plain language), Standard (clear + §-refs), Expert (precise legal terminology)
- **Document filter** — Scope queries to a specific document (Electricity, Gas, SCHUFA, Creditreform)
- **Streaming responses** — Tokens stream in real-time via Server-Sent Events
- **Conversation context** — Last 3 exchanges passed to the LLM for follow-up questions
- **AI-generated chat titles** — LLM summarises each conversation into a short title
- **Chat history** — Persisted in localStorage, survives page refresh
- **Source cards** — Expandable panel showing which document chunks were retrieved
- **Copy answer** — One-click copy of any assistant message
- **Loading animation** — Shimmering text while retrieving, smooth fade-in when answer arrives
- **Markdown rendering** — Bold §-references, bullet points, structured answers
- **Fully local** — No API keys, no cloud, no data leaves the machine

---

## Documents

| Key | Document |
|-----|----------|
| `strom` | Allgemeine Lieferbedingungen Strom |
| `erdgas` | Allgemeine Lieferbedingungen Erdgas Haushaltskunden |
| `schufa` | Anhang SCHUFA |
| `creditreform` | Anhang Creditreform |
