"""
DEW21 RAG Evaluation Script
============================
Evaluates the RAG system using RAGAS metrics, fully locally via Ollama.

Metrics computed:
  - Faithfulness        : Is the answer grounded in the retrieved chunks?
  - Answer Relevancy    : Does the answer address the question?
  - Context Precision   : Are retrieved chunks ranked by relevance?
  - Context Recall      : Did retrieval find everything needed? (needs ground truth)
  - Answer Correctness  : How close is the answer to the ground truth?

Also computed without an LLM (always available):
  - Semantic Similarity : Cosine similarity between answer and ground truth embeddings
  - Response Time       : Latency of the full pipeline in seconds

Usage:
  # Make sure the FastAPI server is running first:
  #   cd rag_english && uvicorn api:app --reload
  #
  python evaluate.py                  # runs all DE questions
  python evaluate.py --lang en        # runs all EN questions
  python evaluate.py --lang de --no-ragas   # skip RAGAS, only similarity + latency
"""

import argparse
import csv
import json
import time
import sys
import os
from datetime import datetime
from pathlib import Path

import requests as http_requests
import numpy as np

# ── Config ────────────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000"
OLLAMA_BASE = "http://localhost:11434"
OLLAMA_MODEL = "qwen3.5:4b"
RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# ── Helpers ───────────────────────────────────────────────────────────────────

def call_query_api(question: str, language: str, document: str, tone: str = "standard") -> dict:
    """Call the running FastAPI /query endpoint and collect streamed response."""
    payload = {
        "query": question,
        "language": language,
        "tone": tone,
        "document": document,
        "history": [],
    }
    start = time.time()
    resp = http_requests.post(f"{API_BASE}/query", json=payload, stream=True, timeout=120)
    resp.raise_for_status()

    answer_tokens = []
    contexts = []
    buffer = ""

    for raw in resp.iter_lines():
        if not raw:
            continue
        line = raw.decode("utf-8") if isinstance(raw, bytes) else raw
        if not line.startswith("data: "):
            continue
        event = json.loads(line[6:])
        if event["type"] == "sources":
            contexts = [s["content"] for s in event["sources"]]
        elif event["type"] == "token":
            answer_tokens.append(event["token"])
        elif event["type"] == "done":
            break

    latency = time.time() - start
    return {
        "answer": "".join(answer_tokens).strip(),
        "contexts": contexts,
        "latency": round(latency, 2),
    }


def cosine_similarity(a: list[float], b: list[float]) -> float:
    a, b = np.array(a), np.array(b)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom > 0 else 0.0


# Lazy-loaded embedding models (same ones the API uses — already in venv)
_embed_models: dict = {}

def get_embed_model(lang: str):
    """Load the same sentence-transformers model the API uses — cached after first load."""
    if lang not in _embed_models:
        from sentence_transformers import SentenceTransformer
        if lang == "en":
            print("  [info] Loading EN embedding model (first use)...")
            _embed_models[lang] = SentenceTransformer(
                "nomic-ai/nomic-embed-text-v1", trust_remote_code=True
            )
        else:
            print("  [info] Loading DE embedding model (first use)...")
            _embed_models[lang] = SentenceTransformer(
                "paraphrase-multilingual-mpnet-base-v2"
            )
    return _embed_models[lang]


def semantic_similarity(answer: str, ground_truth: str, lang: str) -> float:
    """Cosine similarity between answer and ground truth using the same models as the API."""
    try:
        model = get_embed_model(lang)
        prefix = "search_query: " if lang == "en" else ""
        a_emb = model.encode([prefix + answer])[0].tolist()
        gt_emb = model.encode([prefix + ground_truth])[0].tolist()
        return round(cosine_similarity(a_emb, gt_emb), 4)
    except Exception as e:
        print(f"  [warn] Embedding similarity failed: {e}")
        return None


def keyword_overlap(answer: str, ground_truth: str) -> float:
    """Simple token overlap F1 as a fallback similarity metric."""
    def tokenize(text):
        return set(text.lower().split())
    a_tokens = tokenize(answer)
    gt_tokens = tokenize(ground_truth)
    if not a_tokens or not gt_tokens:
        return 0.0
    precision = len(a_tokens & gt_tokens) / len(a_tokens)
    recall = len(a_tokens & gt_tokens) / len(gt_tokens)
    if precision + recall == 0:
        return 0.0
    return round(2 * precision * recall / (precision + recall), 4)


# ── RAGAS setup ───────────────────────────────────────────────────────────────

def setup_ragas(lang: str):
    """
    Configure RAGAS to use local Ollama instead of OpenAI.
    Returns (metrics_list, ragas_llm, ragas_embeddings) or None if unavailable.
    """
    try:
        from ragas import evaluate as ragas_evaluate
        from ragas.metrics import (
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
            answer_correctness,
        )
        from ragas.llms import LangchainLLMWrapper
        from ragas.embeddings import LangchainEmbeddingsWrapper
        from langchain_community.llms import Ollama
        from langchain_community.embeddings import OllamaEmbeddings

        llm = LangchainLLMWrapper(Ollama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE))
        embed_model = "nomic-embed-text"
        embeddings = LangchainEmbeddingsWrapper(
            OllamaEmbeddings(model=embed_model, base_url=OLLAMA_BASE)
        )

        metrics = [faithfulness, answer_relevancy, context_precision, context_recall, answer_correctness]
        for m in metrics:
            m.llm = llm
            if hasattr(m, "embeddings"):
                m.embeddings = embeddings

        return ragas_evaluate, metrics
    except ImportError:
        return None, None


# ── Main evaluation loop ──────────────────────────────────────────────────────

def run_evaluation(lang: str, use_ragas: bool, tone: str = "standard"):
    print(f"\n{'='*60}")
    print(f"  DEW21 RAG Evaluation — language={lang.upper()}  tone={tone}")
    print(f"{'='*60}\n")

    # Load questions
    if lang == "de":
        from questions_de import QUESTIONS_DE as questions
    else:
        from questions_en import QUESTIONS_EN as questions

    # Try RAGAS
    ragas_evaluate, ragas_metrics = None, None
    if use_ragas:
        ragas_evaluate, ragas_metrics = setup_ragas(lang)
        if ragas_evaluate:
            print("✓ RAGAS configured with local Ollama\n")
        else:
            print("⚠ RAGAS or langchain-community not installed — running similarity metrics only\n")
            print("  To enable RAGAS: pip install ragas langchain-community\n")

    rows = []

    for i, q in enumerate(questions, 1):
        question = q["question"]
        ground_truth = q["ground_truth"]
        doc_filter = q["document"]

        print(f"[{i:02d}/{len(questions):02d}] {question[:70]}...")

        # Call the RAG pipeline
        try:
            result = call_query_api(question, lang, doc_filter, tone)
        except Exception as e:
            print(f"  ✗ API error: {e}")
            rows.append({
                "question": question, "document": doc_filter,
                "answer": "ERROR", "latency_s": None,
                "semantic_similarity": None, "keyword_f1": None,
                "faithfulness": None, "answer_relevancy": None,
                "context_precision": None, "context_recall": None,
                "answer_correctness": None,
            })
            continue

        answer = result["answer"]
        contexts = result["contexts"]
        latency = result["latency"]

        print(f"  ↳ {latency}s  |  {len(contexts)} chunks retrieved")

        # Similarity metrics (no LLM needed)
        sim = semantic_similarity(answer, ground_truth, lang)
        kf1 = keyword_overlap(answer, ground_truth)

        row = {
            "question": question,
            "document": doc_filter,
            "answer": answer,
            "ground_truth": ground_truth,
            "num_contexts": len(contexts),
            "latency_s": latency,
            "semantic_similarity": sim,
            "keyword_f1": kf1,
            "faithfulness": None,
            "answer_relevancy": None,
            "context_precision": None,
            "context_recall": None,
            "answer_correctness": None,
        }
        rows.append(row)

        print(f"  semantic_similarity={sim}  keyword_f1={kf1}")

    # ── RAGAS batch evaluation ────────────────────────────────────────────────
    if ragas_evaluate and ragas_metrics and rows:
        print("\nRunning RAGAS metrics (this may take a few minutes)...")
        try:
            from datasets import Dataset

            valid_rows = [r for r in rows if r["answer"] != "ERROR"]
            dataset = Dataset.from_dict({
                "question": [r["question"] for r in valid_rows],
                "answer": [r["answer"] for r in valid_rows],
                "contexts": [[c for c in rows[i].get("contexts", [])] for i in range(len(valid_rows))],
                "ground_truth": [r["ground_truth"] for r in valid_rows],
            })
            scores = ragas_evaluate(dataset, metrics=ragas_metrics)
            scores_df = scores.to_pandas()

            for i, r in enumerate(valid_rows):
                r["faithfulness"] = round(float(scores_df.iloc[i]["faithfulness"]), 4)
                r["answer_relevancy"] = round(float(scores_df.iloc[i]["answer_relevancy"]), 4)
                r["context_precision"] = round(float(scores_df.iloc[i]["context_precision"]), 4)
                r["context_recall"] = round(float(scores_df.iloc[i]["context_recall"]), 4)
                r["answer_correctness"] = round(float(scores_df.iloc[i]["answer_correctness"]), 4)

            print("✓ RAGAS evaluation complete\n")
        except Exception as e:
            print(f"  ✗ RAGAS evaluation failed: {e}\n")

    # ── Save results ──────────────────────────────────────────────────────────
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = RESULTS_DIR / f"eval_{lang}_{tone}_{timestamp}.csv"
    json_path = RESULTS_DIR / f"eval_{lang}_{tone}_{timestamp}.json"

    fieldnames = [
        "question", "document", "answer", "ground_truth", "num_contexts",
        "latency_s", "semantic_similarity", "keyword_f1",
        "faithfulness", "answer_relevancy", "context_precision",
        "context_recall", "answer_correctness",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    # ── Print summary ─────────────────────────────────────────────────────────
    valid = [r for r in rows if r["answer"] != "ERROR"]
    print(f"\n{'─'*60}")
    print(f"  RESULTS SUMMARY  ({len(valid)}/{len(rows)} questions answered)")
    print(f"{'─'*60}")

    def avg(key):
        vals = [r[key] for r in valid if r[key] is not None]
        return round(sum(vals) / len(vals), 4) if vals else "n/a"

    print(f"  Avg latency              : {avg('latency_s')}s")
    print(f"  Avg semantic similarity  : {avg('semantic_similarity')}")
    print(f"  Avg keyword F1           : {avg('keyword_f1')}")
    print(f"  Avg faithfulness         : {avg('faithfulness')}")
    print(f"  Avg answer relevancy     : {avg('answer_relevancy')}")
    print(f"  Avg context precision    : {avg('context_precision')}")
    print(f"  Avg context recall       : {avg('context_recall')}")
    print(f"  Avg answer correctness   : {avg('answer_correctness')}")
    print(f"\n  Saved → {csv_path.name}")
    print(f"  Saved → {json_path.name}")
    print(f"{'─'*60}\n")

    return rows


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Change to script directory so relative imports work
    os.chdir(Path(__file__).parent)

    parser = argparse.ArgumentParser(description="Evaluate DEW21 RAG system")
    parser.add_argument("--lang", choices=["de", "en", "both"], default="de",
                        help="Language to evaluate (default: de)")
    parser.add_argument("--tone", choices=["easy", "standard", "technical"], default="standard",
                        help="Response tone to evaluate (default: standard)")
    parser.add_argument("--no-ragas", action="store_true",
                        help="Skip RAGAS metrics (faster, no LLM judge needed)")
    args = parser.parse_args()

    use_ragas = not args.no_ragas

    # Check server is running
    try:
        http_requests.get(f"{API_BASE}/health", timeout=5).raise_for_status()
        print(f"✓ API server reachable at {API_BASE}")
    except Exception:
        print(f"✗ Cannot reach API at {API_BASE}")
        print("  Start it with:  cd rag_english && uvicorn api:app --reload")
        sys.exit(1)

    langs = ["de", "en"] if args.lang == "both" else [args.lang]
    for lang in langs:
        run_evaluation(lang, use_ragas, args.tone)
