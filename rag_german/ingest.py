import os
import chromadb
from sentence_transformers import SentenceTransformer

DOCS_PATH = "docs"
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "dew21_docs"
MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"
CHUNK_SIZE = 400   # words
CHUNK_OVERLAP = 50  # words


def chunk_by_words(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


def chunk_text(text):
    import re
    section_pattern = re.compile(
        r'(?=§\s*\d+|^\d+\.\d*\s+[A-ZÄÖÜ]|^\d+\.\s+[A-ZÄÖÜ])',
        re.MULTILINE
    )
    sections = section_pattern.split(text)
    sections = [s.strip() for s in sections if s.strip()]

    chunks = []
    for section in sections:
        word_count = len(section.split())
        if word_count > CHUNK_SIZE:
            chunks.extend(chunk_by_words(section))
        elif word_count > 20:
            chunks.append(section)

    if not chunks:
        chunks = chunk_by_words(text)

    return chunks


def load_docs(docs_path):
    docs = []
    for filename in os.listdir(docs_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(docs_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            docs.append({"filename": filename, "text": text})
            print(f"Loaded: {filename} ({len(text.split())} words)")
    return docs


def ingest():
    print("Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    print("Connecting to ChromaDB...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Delete existing collection to avoid duplicates on re-run
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted existing collection '{COLLECTION_NAME}'")

    collection = client.create_collection(COLLECTION_NAME)

    print(f"\nLoading documents from '{DOCS_PATH}'...")
    docs = load_docs(DOCS_PATH)

    all_chunks = []
    all_ids = []
    all_metadatas = []

    for doc in docs:
        chunks = chunk_text(doc["text"])
        print(f"  {doc['filename']}: {len(chunks)} chunks")
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_ids.append(f"{doc['filename']}_chunk_{i}")
            all_metadatas.append({"source": doc["filename"]})

    # FAQ entries — embedded as "F: ... A: ..." for direct question matching
    from faqs_de import FAQS_DE
    print(f"\nLoading {len(FAQS_DE)} FAQ entries...")
    for i, faq in enumerate(FAQS_DE):
        text = f"F: {faq['question']}\nA: {faq['answer']}"
        all_chunks.append(text)
        all_ids.append(f"faq_de_{i}")
        all_metadatas.append({"source": "faq_de", "document": faq.get("document", "general")})

    print(f"\nEmbedding {len(all_chunks)} chunks...")
    embeddings = model.encode(all_chunks, show_progress_bar=True).tolist()

    print("Storing in ChromaDB...")
    # Upsert in batches of 100
    batch_size = 100
    for i in range(0, len(all_chunks), batch_size):
        collection.upsert(
            documents=all_chunks[i:i + batch_size],
            embeddings=embeddings[i:i + batch_size],
            ids=all_ids[i:i + batch_size],
            metadatas=all_metadatas[i:i + batch_size],
        )

    print(f"\nDone! {collection.count()} chunks stored in collection '{COLLECTION_NAME}'")


if __name__ == "__main__":
    ingest()
