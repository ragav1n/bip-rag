from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import chromadb
import requests
import json
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
LLM_MODEL = "qwen3.5:4b"
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

# Document source filename mapping (matches metadata stored by ingest.py)
DOC_SOURCES = {
    "strom": {
        "en": ["Allgemeine_Lieferbedingungen_Strom.pdf_en.txt"],
        "de": ["Allgemeine_Lieferbedingungen_Strom.pdf_de.txt"],
    },
    "erdgas": {
        "en": ["Allgemeine_Lieferbedingungen_Erdgas_Haushaltskunenn.pdf_en.txt"],
        "de": ["Allgemeine_Lieferbedingungen_Erdgas_Haushaltskunden.pdf_de.txt"],
    },
    "schufa": {
        "en": ["Anhang_Schufa.pdf_en.txt"],
        "de": ["Anhang_Schufa.pdf_de.txt"],
    },
    "creditreform": {
        "en": ["Anhang Creditreform.pdf_en.txt"],
        "de": ["Anhang Creditreform.pdf_de.txt"],
    },
}

TONE_RULES = {
    "de": {
        "easy": """- Schreibe wie ein freundlicher Mitarbeiter am Telefon — einfach, klar, ohne Fachsprache
- Erkläre Begriffe in Alltagssprache, z.B. statt "Zahlungsverzug" sage "wenn die Zahlung zu spät kommt"
- Erwähne KEINE Paragrafennummern — sage stattdessen "laut Vertrag" oder "laut den Regeln"
- Kurze Sätze. Ein Gedanke pro Satz. Kein Juristendeutsch.
- Fasse die wichtigste Aussage zuerst zusammen, dann erkläre sie kurz
- Wenn die Antwort nicht im Kontext steht, sage genau: "Diese Information liegt mir leider nicht vor."
""",
        "standard": """- Schreibe klar und verständlich für einen informierten Mitarbeiter
- Nutze **fett** für wichtige Begriffe und Paragrafennummern, z.B. **§ 4**
- Verwende Aufzählungspunkte für mehrere Punkte
- Nenne relevante Paragrafennummern fett, wenn vorhanden
- Beginne NICHT mit einem Titel oder einer Überschrift — starte direkt mit der Antwort
- Wenn die Antwort nicht im Kontext steht, antworte genau: "Diese Information ist in den vorliegenden Dokumenten nicht enthalten."
""",
        "technical": """- Verwende präzise Rechtsbegriffe — keine Vereinfachungen
- Nenne ALLE relevanten Paragrafennummern und Unterabsätze fett, z.B. **§ 4 Abs. 2**
- Gib die rechtliche Grundlage zuerst an, dann die Rechtsfolgen
- Nenne Querverweise zwischen Paragraphen, wenn vorhanden
- Verwende formale, juristische Sprache
- Strukturiere mit Aufzählungspunkten für Tatbestandsmerkmale und Rechtsfolgen
- Beginne NICHT mit einem Titel — starte direkt mit der rechtlichen Grundlage
- Wenn die Antwort nicht im Kontext steht, antworte genau: "Diese Information ist in den vorliegenden Dokumenten nicht enthalten."
""",
    },
    "en": {
        "easy": """- Write like a friendly employee explaining over the phone — simple, clear, no jargon
- Use everyday words. Instead of "payment default" say "when a payment is missed"
- Do NOT cite clause numbers — say "according to the contract" or "the rules state" instead
- Short sentences. One idea per sentence. No legal language.
- Lead with the key point first, then briefly explain
- If not found, say exactly: "I'm sorry, I don't have that information available."
""",
        "standard": """- Write clearly and concisely for a knowledgeable employee
- Use **bold** for key terms and clause numbers, e.g. **§ 4**
- Use bullet points for multiple items
- Reference relevant clause numbers in bold where available
- Do NOT start with a title or heading — begin directly with the answer
- If not found, say exactly: "This information is not contained in the provided documents."
""",
        "technical": """- Use precise legal terminology throughout — no simplifications
- Cite ALL relevant clause numbers and sub-clauses in bold, e.g. **§ 4 para. 2**
- State the legal basis first, then the legal consequences
- Include cross-references between clauses where applicable
- Use formal, exact legal language
- Structure with bullet points for elements and consequences
- Do NOT start with a title — begin directly with the legal basis
- If not found, say exactly: "This information is not contained in the provided documents."
""",
    },
}


class HistoryMessage(BaseModel):
    role: str
    content: str


class QueryRequest(BaseModel):
    query: str
    language: str = "de"
    tone: str = "standard"
    document: str = "all"
    history: list[HistoryMessage] = []


@app.post("/query")
def query(req: QueryRequest):
    tone = req.tone if req.tone in ("easy", "standard", "technical") else "standard"
    lang = req.language if req.language in ("en", "de") else "de"

    if lang == "de":
        embedding = de_model.encode([req.query]).tolist()
        collection = de_collection
        rules = TONE_RULES["de"][tone]
    else:
        embedding = en_model.encode([f"search_query: {req.query}"]).tolist()
        collection = en_collection
        rules = TONE_RULES["en"][tone]

    # Document filter
    query_kwargs: dict = {"query_embeddings": embedding, "n_results": TOP_K}
    if req.document != "all" and req.document in DOC_SOURCES:
        filenames = DOC_SOURCES[req.document][lang]
        query_kwargs["where"] = {"source": {"$in": filenames}}

    results = collection.query(**query_kwargs)
    chunks = results["documents"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    sources_payload = [
        {"content": c, "source": m.get("source", "unknown")}
        for c, m in zip(chunks, metadatas)
    ]

    context = "\n\n".join(chunks)

    # Conversation history (last 3 exchanges = up to 6 messages)
    history_section = ""
    if req.history:
        recent = req.history[-6:]
        if lang == "de":
            history_section = "\nBisheriger Gesprächsverlauf:\n"
            for msg in recent:
                label = "Mitarbeiter" if msg.role == "user" else "Assistent"
                # Truncate long assistant answers to keep prompt size manageable
                content = msg.content[:300] + "…" if len(msg.content) > 300 else msg.content
                history_section += f"{label}: {content}\n"
            history_section += "\n"
        else:
            history_section = "\nConversation so far:\n"
            for msg in recent:
                label = "Employee" if msg.role == "user" else "Assistant"
                content = msg.content[:300] + "…" if len(msg.content) > 300 else msg.content
                history_section += f"{label}: {content}\n"
            history_section += "\n"

    if lang == "de":
        prompt = f"""Du bist ein Assistent für DEW21-Mitarbeiter im Kundenkontakt.
Beantworte die Frage ausschließlich auf Basis des folgenden Kontexts aus den DEW21-Dokumenten.
Antworte NUR mit Informationen aus dem Kontext.

Regeln:
{rules}
Kontext:
{context}
{history_section}Aktuelle Frage: {req.query}

Antwort:"""
    else:
        prompt = f"""You are an assistant for DEW21 customer service employees.
Answer the question using ONLY the information from the context below.

Rules:
{rules}
Context:
{context}
{history_section}Current question: {req.query}

Answer:"""

    def generate():
        yield f"data: {json.dumps({'type': 'sources', 'sources': sources_payload})}\n\n"
        response = requests.post(
            OLLAMA_URL,
            json={"model": LLM_MODEL, "prompt": prompt, "stream": True, "think": False},
            stream=True,
        )
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if not data.get("done"):
                    yield f"data: {json.dumps({'type': 'token', 'token': data['response']})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


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
        json={"model": LLM_MODEL, "prompt": prompt, "stream": False, "think": False},
    )
    title = response.json()["response"].strip().strip('"').strip("'")
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
