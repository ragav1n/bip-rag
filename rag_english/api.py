from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import chromadb
import requests
import json
import re
import os
import tempfile
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
from faster_whisper import WhisperModel

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
REWRITE_MODEL = "qwen3.5:4b"  # fast model just for query rewriting
TOP_K = 8           # final chunks sent to LLM
TOP_K_RETRIEVE = 20 # candidates retrieved before reranking

def bm25_tokenize(text: str) -> list[str]:
    return re.sub(r'[^\w\s]', ' ', text.lower()).split()


print("Loading English embedding model...")
en_model = SentenceTransformer(EN_MODEL_NAME, trust_remote_code=True)

print("Loading German embedding model...")
de_model = SentenceTransformer(DE_MODEL_NAME)

# Multilingual cross-encoder reranker (handles both DE and EN)
print("Loading reranker model...")
reranker = CrossEncoder("cross-encoder/mmarco-mMiniLMv2-L12-H384-v1")


def rewrite_query(query: str, lang: str) -> str:
    """Rewrite natural language query into technical terms matching the document vocabulary."""
    if lang == "de":
        prompt = f"""Formuliere diese Kundenfrage in technische Begriffe um, die in einem Energieversorgungsvertrag oder AGB vorkommen würden (z.B. Paragrafennummern, Fachbegriffe, Vertragsklauseln). Gib NUR die umformulierte Suchanfrage aus, keine Erklärung.

Frage: {query}
Suchanfrage:"""
    else:
        prompt = f"""Rephrase this customer question into technical terms that would appear in an energy supply contract or terms and conditions (e.g. clause names, legal terms, contract concepts). Output ONLY the rephrased search query, no explanation.

Question: {query}
Search query:"""
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": REWRITE_MODEL, "prompt": prompt, "stream": False, "think": False, "options": {"temperature": 0}},
            timeout=15,
        )
        rewritten = resp.json()["response"].strip()
        return rewritten if rewritten else query
    except Exception:
        return query

en_client = chromadb.PersistentClient(path=EN_CHROMA_PATH)
en_collection = en_client.get_or_create_collection(COLLECTION_NAME)

de_client = chromadb.PersistentClient(path=DE_CHROMA_PATH)
de_collection = de_client.get_or_create_collection(COLLECTION_NAME)

print(f"EN collection: {en_collection.count()} chunks")
print(f"DE collection: {de_collection.count()} chunks")

print("Loading Whisper model (base)...")
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
print("Whisper ready.")

print("Building BM25 indices...")
_en_all = en_collection.get(include=["documents", "metadatas"])
en_bm25_docs  = _en_all["documents"]
en_bm25_metas = _en_all["metadatas"]
en_bm25 = BM25Okapi([bm25_tokenize(d) for d in en_bm25_docs])

_de_all = de_collection.get(include=["documents", "metadatas"])
de_bm25_docs  = _de_all["documents"]
de_bm25_metas = _de_all["metadatas"]
de_bm25 = BM25Okapi([bm25_tokenize(d) for d in de_bm25_docs])
print("BM25 indices ready.")

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
    "kosten": {
        "en": ["Kostenübersicht_DEW21.pdf_en.txt"],
        "de": ["Kostenübersicht_DEW21.pdf_de.txt"],
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

    # Rewrite query into document vocabulary before embedding
    search_query = rewrite_query(req.query, lang)

    if lang == "de":
        orig_embedding = de_model.encode([req.query]).tolist()
        rewritten_embedding = de_model.encode([search_query]).tolist()
        collection = de_collection
        rules = TONE_RULES["de"][tone]
    else:
        orig_embedding = en_model.encode([f"search_query: {req.query}"]).tolist()
        rewritten_embedding = en_model.encode([f"search_query: {search_query}"]).tolist()
        collection = en_collection
        rules = TONE_RULES["en"][tone]

    # Retrieve candidates with both original and rewritten query, then merge
    n_retrieve = min(TOP_K_RETRIEVE, collection.count())
    doc_filter: dict = {}
    if req.document != "all" and req.document in DOC_SOURCES:
        filenames = DOC_SOURCES[req.document][lang]
        faq_source = f"faq_{lang}"
        doc_filter = {"where": {"source": {"$in": filenames + [faq_source]}}}
        doc_count = len(collection.get(where={"source": {"$in": filenames}})["ids"])
        n_retrieve = min(TOP_K_RETRIEVE, doc_count + 5) if doc_count > 0 else 1

    r1 = collection.query(query_embeddings=orig_embedding, n_results=n_retrieve, **doc_filter)
    r2 = collection.query(query_embeddings=rewritten_embedding, n_results=n_retrieve, **doc_filter)

    # BM25 retrieval — exact term matching for numbers, fees, clause references
    bm25_tokens = bm25_tokenize(req.query + " " + search_query)
    if lang == "de":
        bm25_scores = de_bm25.get_scores(bm25_tokens)
        bm25_corpus, bm25_metas = de_bm25_docs, de_bm25_metas
    else:
        bm25_scores = en_bm25.get_scores(bm25_tokens)
        bm25_corpus, bm25_metas = en_bm25_docs, en_bm25_metas

    allowed_sources = None
    if req.document != "all" and req.document in DOC_SOURCES:
        faq_src = f"faq_{lang}"
        allowed_sources = set(DOC_SOURCES[req.document][lang] + [faq_src])

    bm25_ranked = sorted(
        [(i, bm25_scores[i]) for i in range(len(bm25_corpus))
         if allowed_sources is None or bm25_metas[i].get("source") in allowed_sources],
        key=lambda x: x[1], reverse=True,
    )[:TOP_K_RETRIEVE]

    # Merge dense + BM25, deduplicate by chunk text
    seen = {}
    for doc, meta in zip(r1["documents"][0] + r2["documents"][0],
                         r1["metadatas"][0] + r2["metadatas"][0]):
        if doc not in seen:
            seen[doc] = meta
    for idx, _ in bm25_ranked:
        doc = bm25_corpus[idx]
        if doc not in seen:
            seen[doc] = bm25_metas[idx]
    chunks = list(seen.keys())
    metadatas = list(seen.values())

    # Rerank: cross-encoder scores each chunk against the original query
    pairs = [[req.query, chunk] for chunk in chunks]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(scores, chunks, metadatas), key=lambda x: x[0], reverse=True)
    top_chunks = ranked[:TOP_K]

    sources_payload = [
        {"content": c, "source": m.get("source", "unknown")}
        for _, c, m in top_chunks
    ]

    context = "\n\n".join(
        f"[Passage {i+1}]\n{c}" for i, (_, c, _) in enumerate(top_chunks)
    )

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

STRENGE REGELN — halte dich immer daran:
1. Beantworte die Frage AUSSCHLIESSLICH auf Basis der unten stehenden Textpassagen. Nutze KEIN Wissen aus deinem Training.
2. Wenn die Antwort nicht in den Passagen steht, sage genau: "Diese Information ist in den vorliegenden Dokumenten nicht enthalten."
3. Wenn die Passagen die Frage nur teilweise beantworten, gib die verfügbaren Informationen an und weise klar darauf hin, was fehlt.
4. Wenn du dir bei einer Information unsicher bist, sage es explizit ("laut Dokument", "soweit aus dem Kontext ersichtlich").
5. Wenn der Kontext nur einen einzigen Wert enthält (z.B. eine Telefonnummer), nenne ihn nur EINMAL. Erfinde keine zweite Version.
6. Sei präzise und kurz — der Nutzer will die Antwort sofort, keinen langen Text.
7. Gib nur die direkte Antwort auf die gestellte Frage. Keine Randthemen, keine Sonderfälle, die nicht gefragt wurden.
8. Wenn der Nutzer einen Vergleich zwischen zwei Dingen fragt (z.B. Strom- vs. Gasvertrag, SCHUFA vs. Creditreform), fasse die relevanten Fakten aus den Passagen zusammen und stelle sie als strukturierten Vergleich dar — auch wenn das Dokument keinen expliziten Vergleich enthält. Dies überschreibt Regel 2: Sage NICHT "nicht in den Dokumenten enthalten", nur weil kein expliziter Vergleich vorhanden ist. Baue den Vergleich aus den verfügbaren Informationen auf.
9. Wenn du Beträge, Gebühren oder Preise aus der Kostenübersicht nennst, füge immer den Hinweis "Stand: 1. April 2025" hinzu.

Formatregeln:
{rules}
Textpassagen aus den DEW21-Dokumenten:
{context}
{history_section}Frage: {req.query}

Antwort:"""
    else:
        prompt = f"""You are an assistant for DEW21 customer service employees.

STRICT RULES — always follow these:
1. Answer using ONLY the passages provided below. Do NOT use knowledge from your training data.
2. If the answer is not in the passages, say exactly: "This information is not contained in the provided documents."
3. If the passages only partially answer the question, give what is available and explicitly state what is missing.
4. If you are uncertain about a detail, say so explicitly ("according to the document", "as far as the context shows").
5. If the context contains only one value (e.g. one phone number), state it exactly ONCE. Do not invent a second version.
6. Be precise and concise — the user wants the answer immediately, not a long text to read.
7. Answer only what was asked. No tangents, no edge cases that were not asked about.
8. If the user asks for a comparison between two things (e.g. electricity vs gas contract, SCHUFA vs Creditreform), synthesize the relevant facts from the passages and present them as a structured comparison — even if the document does not explicitly compare them. This overrides rule 2: do NOT say "not in the documents" just because no explicit comparison exists. Build the comparison from what is available.
9. When citing any fee, cost, or price from the fee schedule, always append "as of April 1, 2025" to make clear the amounts may change.

Formatting rules:
{rules}
Passages from DEW21 documents:
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
                if data.get("error"):
                    err = data["error"]
                    yield f"data: {json.dumps({'type': 'token', 'token': f'[Model error: {err}]'})}\n\n"
                    break
                if not data.get("done"):
                    yield f"data: {json.dumps({'type': 'token', 'token': data.get('response', '')})}\n\n"
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


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...), language: str = "en"):
    suffix = ".webm"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(await audio.read())
        tmp_path = f.name
    try:
        lang_code = "de" if language == "de" else "en"
        segments, _ = whisper_model.transcribe(tmp_path, language=lang_code)
        text = " ".join(seg.text for seg in segments).strip()
        return {"text": text}
    finally:
        os.unlink(tmp_path)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "en_chunks": en_collection.count(),
        "de_chunks": de_collection.count(),
    }
