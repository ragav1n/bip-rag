from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
import requests
from sentence_transformers import SentenceTransformer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

EN_MODEL_NAME = "nomic-ai/nomic-embed-text-v1"
EN_CHROMA_PATH = "./chroma_db"

DE_MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"
DE_CHROMA_PATH = "../rag_german/chroma_db"

COLLECTION_NAME = "dew21_docs"
OLLAMA_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "llama3.2:latest"
TOP_K = 5

print("Loading English embedding model...")
en_model = SentenceTransformer(EN_MODEL_NAME, trust_remote_code=True)

print("Loading German embedding model...")
de_model = SentenceTransformer(DE_MODEL_NAME)

en_client = chromadb.PersistentClient(path=EN_CHROMA_PATH)
en_collection = en_client.get_or_create_collection(COLLECTION_NAME)

de_client = chromadb.PersistentClient(path=DE_CHROMA_PATH)
de_collection = de_client.get_or_create_collection(COLLECTION_NAME)

print(f"EN collection: {en_collection.count()} chunks")
print(f"DE collection: {de_collection.count()} chunks")


class QueryRequest(BaseModel):
    query: str
    language: str = "de"


@app.post("/query")
def query(req: QueryRequest):
    if req.language == "de":
        embedding = de_model.encode([req.query]).tolist()
        collection = de_collection
        lang_instruction = "Antworte auf Deutsch und beziehe dich nur auf die Informationen im Kontext."
    else:
        embedding = en_model.encode([f"search_query: {req.query}"]).tolist()
        collection = en_collection
        lang_instruction = "Answer in English using only the information from the context."

    results = collection.query(query_embeddings=embedding, n_results=TOP_K)
    chunks = results["documents"][0]
    metadatas = results["metadatas"][0]
    context = "\n\n".join(chunks)

    if req.language == "de":
        prompt = f"""Du bist ein Assistent für DEW21-Mitarbeiter im Kundenkontakt.
Beantworte die Frage ausschließlich auf Basis des folgenden Kontexts aus den DEW21-Dokumenten.

Regeln:
- Antworte nur mit Informationen aus dem Kontext
- Formatiere deine Antwort in Markdown: nutze **fett** für wichtige Begriffe und Paragrafennummern, Aufzählungspunkte für mehrere Punkte, und kurze Absätze
- Beginne NICHT mit einem Titel oder einer Überschrift — starte direkt mit der Antwort
- Nenne die relevante Paragrafennummer (§) fett, wenn vorhanden, z.B. **§ 4**
- Wenn die Antwort nicht im Kontext steht, antworte genau: "Diese Information ist in den vorliegenden Dokumenten nicht enthalten."

Kontext:
{context}

Frage des Mitarbeiters: {req.query}

Antwort:"""
    else:
        prompt = f"""You are an assistant for DEW21 customer service employees.
Answer the question using only the context below from DEW21 documents.

Rules:
- Only use information from the context
- Format your answer in Markdown: use **bold** for key terms and clause numbers, bullet points for multiple items, and short paragraphs
- Do NOT start with a title or heading — begin directly with the answer
- Reference clause numbers in bold, e.g. **§ 4**
- If not found, say exactly: "This information is not contained in the provided documents."

Context:
{context}

Employee question: {req.query}

Answer:"""

    response = requests.post(
        OLLAMA_URL,
        json={"model": LLM_MODEL, "prompt": prompt, "stream": False},
    )

    answer = response.json()["response"]
    sources = [
        {"content": chunk, "source": meta.get("source", "unknown")}
        for chunk, meta in zip(chunks, metadatas)
    ]

    return {"answer": answer, "sources": sources}


class TitleRequest(BaseModel):
    query: str
    language: str = "de"


@app.post("/title")
def generate_title(req: TitleRequest):
    if req.language == "de":
        prompt = f"""Erstelle einen kurzen Titel (3-5 Wörter) für diese Frage. Gib NUR den Titel aus, keine Erklärung, keine Anführungszeichen.

Frage: {req.query}

Titel:"""
    else:
        prompt = f"""Generate a short title (3-5 words) for this question. Output ONLY the title, no explanation, no quotes.

Question: {req.query}

Title:"""

    response = requests.post(
        OLLAMA_URL,
        json={"model": LLM_MODEL, "prompt": prompt, "stream": False},
    )
    title = response.json()["response"].strip().strip('"').strip("'")
    # Trim to 50 chars max as safety net
    if len(title) > 50:
        title = title[:47] + "…"
    return {"title": title}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "en_chunks": en_collection.count(),
        "de_chunks": de_collection.count(),
    }
