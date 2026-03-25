from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import chromadb
import requests
import json
from sentence_transformers import SentenceTransformer, CrossEncoder

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
LLM_MODEL = "qwen3.5:9b"
TOP_K = 8           # final chunks sent to LLM
TOP_K_RETRIEVE = 20 # candidates retrieved before reranking

print("Loading English embedding model...")
en_model = SentenceTransformer(EN_MODEL_NAME, trust_remote_code=True)

print("Loading German embedding model...")
de_model = SentenceTransformer(DE_MODEL_NAME)

# Multilingual cross-encoder reranker (handles both DE and EN)
print("Loading reranker model...")
reranker = CrossEncoder("cross-encoder/mmarco-mMiniLMv2-L12-H384-v1")

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
        "en": ["Allgemeine_Lieferbedingungen_Erdgas_Haushaltskunden.pdf_en.txt"],
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
        "easy": """- Beantworte die Frage direkt in 1–3 Sätzen — keine Einleitungen, keine Überschriften
- Nenne zuerst die konkrete Antwort (Frist, Betrag, Bedingung), dann nur das Nötigste zur Erklärung
- Alltagssprache: statt "Zahlungsverzug" → "wenn die Zahlung zu spät kommt"
- Erwähne KEINE Paragrafennummern
- Keine Aufzählungen, außer es gibt wirklich mehrere gleichwertige Punkte (max. 3)
- Wenn die Antwort nicht im Kontext steht, sage genau: "Diese Information liegt mir leider nicht vor."
""",
        "standard": """- Beantworte die Frage direkt — starte sofort mit der konkreten Antwort, ohne Einleitung
- Nenne zuerst die wichtigste Aussage (z.B. die Frist, den Betrag, die Regelung), dann ggf. eine kurze Ergänzung
- Nutze **fett** für Schlüsselbegriffe und Paragrafennummern, z.B. **§ 4**
- Maximal 4 Aufzählungspunkte — nur wenn wirklich mehrere gleichwertige Punkte nötig sind
- Keine Aufzählung aller theoretischen Randfälle — nur was zur Frage gehört
- Beginne NICHT mit einem Titel oder einer Überschrift
- Wenn die Antwort nicht im Kontext steht, antworte genau: "Diese Information ist in den vorliegenden Dokumenten nicht enthalten."
""",
        "technical": """- Starte direkt mit der rechtlichen Grundlage (**§ X Abs. Y**), dann die Rechtsfolge — keine Einleitung
- Nenne alle relevanten Paragrafennummern und Unterabsätze fett, z.B. **§ 4 Abs. 2**
- Präzise Rechtsbegriffe, keine Vereinfachungen
- Querverweise nur wenn direkt relevant
- Maximal 5 Aufzählungspunkte — fokussiert auf das Wesentliche, keine Randtatbestände
- Wenn die Antwort nicht im Kontext steht, antworte genau: "Diese Information ist in den vorliegenden Dokumenten nicht enthalten."
""",
    },
    "en": {
        "easy": """- Answer in 1–3 sentences — no preamble, no headings
- Lead with the concrete answer (deadline, amount, condition), then only what's needed to understand it
- Plain language: instead of "payment default" say "missed payment"
- Do NOT cite clause numbers
- No bullet lists unless there are truly multiple equal points (max 3)
- If not found, say exactly: "I'm sorry, I don't have that information available."
""",
        "standard": """- Answer directly — open with the concrete answer immediately, no introduction
- State the key fact first (the deadline, the amount, the rule), then a brief clarification if needed
- Use **bold** for key terms and clause numbers, e.g. **§ 4**
- At most 4 bullet points — only when multiple genuinely distinct points are needed
- Do not list every theoretical edge case — only what is relevant to the question
- Do NOT start with a title or heading
- If not found, say exactly: "This information is not contained in the provided documents."
""",
        "technical": """- Open directly with the legal basis (**§ X para. Y**) and the legal consequence — no introduction
- Cite all relevant clause numbers and sub-clauses in bold, e.g. **§ 4 para. 2**
- Precise legal terminology, no simplifications
- Cross-references only when directly relevant
- At most 5 bullet points — focused on what is essential, not peripheral cases
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

    # Document filter — retrieve TOP_K_RETRIEVE candidates, then rerank down to TOP_K
    n_retrieve = min(TOP_K_RETRIEVE, collection.count())
    query_kwargs: dict = {"query_embeddings": embedding, "n_results": n_retrieve}
    if req.document != "all" and req.document in DOC_SOURCES:
        filenames = DOC_SOURCES[req.document][lang]
        query_kwargs["where"] = {"source": {"$in": filenames}}
        doc_chunks = collection.get(where={"source": {"$in": filenames}})
        doc_count = len(doc_chunks["ids"])
        query_kwargs["n_results"] = min(TOP_K_RETRIEVE, doc_count) if doc_count > 0 else 1

    results = collection.query(**query_kwargs)
    chunks = results["documents"][0]
    metadatas = results["metadatas"][0]

    # Rerank: cross-encoder scores each chunk against the query
    pairs = [[req.query, chunk] for chunk in chunks]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(scores, chunks, metadatas), key=lambda x: x[0], reverse=True)
    top_chunks = ranked[:TOP_K]

    sources_payload = [
        {"content": c, "source": m.get("source", "unknown")}
        for _, c, m in top_chunks
    ]

    context = "\n\n".join(c for _, c, _ in top_chunks)

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
Antworte NUR mit Informationen aus dem Kontext. Sei präzise und kurz — der Nutzer will die Antwort sofort sehen, keinen langen Text lesen.
Gib die direkte Antwort auf die gestellte Frage. Erweitere NICHT auf Randthemen oder Sonderfälle, die nicht gefragt wurden.
Erfinde niemals Informationen.

Regeln:
{rules}
Kontext:
{context}
{history_section}Frage: {req.query}

Antwort:"""
    else:
        prompt = f"""You are an assistant for DEW21 customer service employees.
Answer the question using ONLY the information from the context below.
Be precise and concise — the user wants the answer immediately, not a long text to read.
Give the direct answer to what was asked. Do NOT expand into edge cases or related topics that were not asked about.
Never invent information.

Rules:
{rules}
Context:
{context}
{history_section}Question: {req.query}

Answer:"""

    def generate():
        yield f"data: {json.dumps({'type': 'sources', 'sources': sources_payload})}\n\n"
        response = requests.post(
            OLLAMA_URL,
            json={"model": LLM_MODEL, "prompt": prompt, "stream": True, "think": False, "options": {"temperature": 0}},
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
        json={"model": LLM_MODEL, "prompt": prompt, "stream": False, "think": False, "options": {"temperature": 0}},
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
