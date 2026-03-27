%Preamble — document class, packages, layout
\documentclass[a4paper,12pt,numbers=noenddot]{scrartcl}
\setlength{\parindent}{1em}
\linespread{1.5}
\usepackage[T1]{fontenc}
\usepackage[english]{babel}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{enumitem}
\usepackage{geometry}
\usepackage{booktabs}
\usepackage{hyperref}

\usepackage{textpos,xcolor,rawfonts,latexsym,graphicx,epsf,verbatim}
\geometry{a4paper, left=35mm, right=25mm, top=20mm, bottom=20mm}
\definecolor{fh_orange}{rgb}{0.953,0.201,0}
\definecolor{fh_grau}{rgb}{0.76,0.75,0.76}


\begin{document}

\begin{titlepage}
    \begin{textblock}{6.5}(-1.5,-3)
        \begin{color}{fh_grau}
            \rule{6.8cm}{33cm}
        \end{color}
    \end{textblock}
    \begin{textblock}{6.5}(-1.3,1)
        {\large \textsf{Seminar Paper}}
    \end{textblock}

    \begin{textblock}{7}(4.1,2)
        {\noindent \huge
            \textsf{\textbf{Privacy-First RAG for Legal Documents\\[0.3cm]
                    \Large A Fully Local Retrieval-Augmented Generation System\\[0.05cm]
                    for DEW21 Customer Service}} }
    \end{textblock}

    \begin{textblock}{6}(4.1,6.5)\noindent
        \textsf{Fachhochschule Dortmund\\
            Department of Computer Science\\
            Computer Science Programme\\
            Seminar Paper submitted for the BIP:\\
            GenAI meets Reality}
    \end{textblock}

    \begin{textblock}{6.5}(-0.9,10.8)
        \noindent
        \textsf{by \\
            Vorname Name \\
            Student-ID: xxxx xxx\\[0.7cm]
            Supervisor: Prof. Dr. Klaus Kaiser \\[0.5cm]
            Dortmund, March 26, 2026}
    \end{textblock}

\end{titlepage}




\begin{abstract}
    DEW21, a Dortmund-based energy utility, needs its customer service staff to
    answer legal questions quickly and accurately --- questions drawn from a set of
    electricity and gas terms, credit check appendices, and a fee schedule. The
    catch: none of those documents can leave DEW21's network. This paper describes
    a Retrieval-Augmented Generation system built under that constraint, using only
    locally-running open-source components: ChromaDB for vector storage,
    sentence-transformer embedding models (one per language), BM25 sparse
    retrieval, a multilingual cross-encoder reranker, and Qwen~3.5~9B via Ollama.
    A FastAPI backend streams answers token-by-token to a React front-end with
    three response tones and per-document filtering.

    Evaluated on 12 German and 11 English questions using RAGAS (itself run
    locally), the system achieves a faithfulness of 0.807, semantic similarity of
    0.748 (DE) and 0.814 (EN), and an average latency of 22.6\,s for German,
    11.9\,s for English, on consumer hardware with no GPU. The hardest failure mode
    --- the system hallucinating a coherent answer when the retrieved chunks simply
    did not contain the relevant information --- affected one question in twelve.
\end{abstract}

\newpage
\tableofcontents

\part{Project Report}

\section{Introduction}

A DEW21 customer calls to ask why their electricity was cut off. The answer is in
\S~19 of the StromGVV, cross-referenced from \S~7.5 of the AGB --- two documents,
two different sections, both written in the kind of German that takes three readings
to parse. The employee has thirty seconds. Getting this wrong has contractual
consequences; looking it up manually every time does not scale.

The natural fix would be to feed all the documents to a large language model and
ask it questions. The problem is that DEW21's documents are confidential. Cloud
LLMs --- GPT-4, Claude, Gemini --- are not an option. Everything has to stay on
DEW21's own hardware.

Retrieval-Augmented Generation (RAG), introduced by Lewis et al.\ \cite{rag},
provides the architecture: instead of relying on a model's memorised training
knowledge, a RAG system retrieves the relevant document passages at query time and
hands them to the LLM alongside the question. The model generates a grounded
answer from what it was just given, not from what it vaguely remembers. As
illustrated in Figure~\ref{fig:rag}, the user's question is embedded into a vector,
matched against a pre-indexed knowledge base, and the closest passages are passed
to the LLM together with the original query.

\begin{figure}[h]
    \begin{center}
        \includegraphics[scale=0.6]{images/rag.png}
    \end{center}
    \caption{The RAG pipeline implemented in this project. The query is rewritten and embedded by two paths; BM25 provides a third retrieval path; all candidates are merged and reranked by a cross-encoder before the top 8 are passed to the LLM.}\label{fig:rag}
\end{figure}

This project builds a fully local version of that architecture for DEW21: no cloud
APIs, no external embedding services, no telemetry. The documents are ingested
into a local ChromaDB instance, queries are answered by Qwen~3.5~9B running
through Ollama, and a React front-end streams the response token-by-token. All of
it runs on a single machine without an internet connection at query time.


\section{Data}

\subsection{Document Corpus}

DEW21 provided five documents. Two are the core supply contracts: the
\textit{Allgemeine Lieferbedingungen Strom} (electricity terms and conditions)
and the \textit{Allgemeine Lieferbedingungen Erdgas Haushaltskunden} (gas terms
for residential customers). These cover billing cycles, metering, cancellation
periods, price adjustments, prepayment rules, and supply interruption procedures
across roughly 25 sections each. Two more are credit check appendices: the
\textit{Anhang Schufa}, which describes DEW21's use of Germany's main credit
reference agency, and the \textit{Anhang Creditreform}, the equivalent for the
commercial provider Creditreform. Both specify what data is shared, under what
legal basis, and what rights customers have. The fifth document is the
\textit{Kostenübersicht DEW21}, the official fee schedule as of 1 April 2025,
listing specific amounts for reconnection fees, reminder fees, default surcharges,
and similar service charges.

Each document exists in two plain-text versions: the original German
(\texttt{\_de.txt}) and an English translation (\texttt{\_en.txt}). The source PDFs
are excluded from version control.

\subsection{Document Characteristics and Challenges}

The AGBs are written in dense legal German: each sentence may reference \S~4,
cross-reference \S~7.5, and use terms like \textit{Zahlungsverzug} or
\textit{Marktlokations-Identifikationsnummer} that general-purpose embedding models
are not specifically trained for. The documents are structured around numbered
sections (\S~1 through \S~21+), which made section-aware chunking straightforward
for the main AGB documents. The \textit{Kostenübersicht} is different --- it has no
section markers at all, just a table of fees --- so it gets treated as one chunk and
retrieved as a unit.

The trickiest retrieval problem is exact-value queries. ``What is the reconnection
fee?'' does not embed close to a fee table. Dense similarity finds passages about
payment processes because they are semantically related to fees, but not the entry
that says ``Wiederherstellung der Anschlussnutzung: 44{,}50\,\texteuro''. This is not
a model quality issue; it is a fundamental property of how dense embeddings work.
BM25 solves it because the fee name appears verbatim in both query and document.

Both German and English versions of each document are ingested, with separate
embedding models per language. German is the primary language for operational use;
the English translations were added for the evaluation and demonstration phases.

\subsection{FAQ Augmentation}

Beyond the raw documents, a hand-crafted FAQ layer was added during the
improvement phase. Each FAQ entry is stored in the format \texttt{Q: ...\textbackslash nA: ...}
and embedded alongside the document chunks. This allows the system to match
common, colloquially phrased customer questions (e.g.\ ``Can DEW21 cut off my
electricity if I don't pay?'') to pre-written answers that cite the relevant clauses
precisely, even when the embedding distance between the colloquial phrasing and the
formal clause text would otherwise be large.

The German collection contains a dedicated FAQ set (\texttt{faqs\_de.py}) and the
English collection contains \texttt{faqs\_en.py}. After ingestion the collections
hold approximately 229 English chunks and 236 German chunks, including all FAQs.


\section{Implementation}

\subsection{System Architecture Overview}

The system has three parts that run on the same machine. First, an ingestion
pipeline reads the plain-text documents, splits them into chunks, embeds each
chunk, and stores the result in a local ChromaDB collection --- this runs once when
documents are added or updated. Second, a FastAPI backend handles queries: it
runs retrieval, reranks the candidates, builds the prompt, calls Ollama, and
streams the response back as Server-Sent Events. Third, a React front-end reads
that SSE stream and renders tokens as they arrive. No internet connection is
needed at query time.

\subsection{Ingestion Pipeline}

\subsubsection{Chunking Strategy}

The ingestion scripts (\texttt{rag\_english/ingest.py}, \texttt{rag\_german/ingest.py})
split documents at legal section boundaries using a regular expression that detects
structural markers in the text:

\begin{verbatim}
r'(?=§\s*\d+|^\d+\.\d*\s+[A-ZÄÖÜ]|^\d+\.\s+[A-ZÄÖÜ])'
\end{verbatim}

This splits immediately before a paragraph symbol followed by a digit (\S~12),
or before a numbered heading beginning with a capitalised word (e.g.\ ``1.\
Allgemeine Bestimmungen''). Each resulting section forms one chunk, provided it
falls between 20 and 400 words. Sections exceeding 400 words are sub-chunked
with a 50-word overlap. Documents with no section markers --- the fee schedule ---
fall back to sliding-window word-based chunking with the same parameters.

\subsubsection{Embedding Models}

English uses \texttt{nomic-ai/nomic-embed-text-v1}, which requires a prefix on
both stored chunks (\texttt{search\_document:}) and queries (\texttt{search\_query:})
to work correctly. German uses \texttt{paraphrase-multilingual-mpnet-base-v2}, a
50-language sentence-transformers model that needs no prefix. The two language
collections live in separate ChromaDB directories so that each maintains its own
index --- cross-language retrieval was never a goal of this project and keeping them
separate avoids any accidental score mixing.

\subsubsection{Storage}

ChromaDB stores each chunk alongside its embedding vector and a metadata
dictionary containing the \texttt{source} filename. This metadata enables the
document filter feature: queries can be restricted to a specific document by adding
a \texttt{where} clause to the ChromaDB query. Chunk IDs follow the scheme
\texttt{<filename>\_chunk\_<index>} for document chunks and \texttt{faq\_<lang>\_<index>}
for FAQ entries.

Ingestion is idempotent: the collection is deleted and re-created on every run to
avoid duplicates when documents or FAQs are updated.

\subsection{Retrieval Pipeline}

Dense retrieval alone does not work well for this domain. A question like ``What is
the reminder fee?'' embeds close to passages about payment processes in general,
not to the fee table entry that has the actual number. The pipeline therefore runs
three retrieval paths in parallel and merges them before reranking.

\subsubsection{Query Rewriting}

Before embedding, the user's query is rewritten into contract vocabulary by a
smaller, faster model (\texttt{qwen3.5:4b}). ``When can DEW21 cut off my gas?''
becomes something like ``supply interruption payment default threshold \S~7.5''.
Both the original and the rewritten query are embedded and used for retrieval,
so if the rewriter produces something unhelpful the original query still runs.
The rewriting call adds 1--3 seconds to total query time, which is acceptable
because it runs before the main generation step.

\subsubsection{Hybrid Retrieval: Dense + BM25}

ChromaDB is queried with both embedding vectors (original and rewritten) and
returns the top-20 candidates each. At the same time, a BM25 index built at
startup from all chunk texts is scored against the concatenated original and
rewritten queries. The three result lists are merged by deduplicating on chunk
text, giving a candidate pool of typically 30--50 unique chunks. BM25 handles
the fee queries that dense retrieval misses; dense retrieval handles everything
where meaning matters more than exact token overlap.

\subsubsection{Cross-Encoder Reranking}

The merged pool is reranked by \texttt{cross-encoder/mmarco-mMiniLMv2-L12-H384-v1}.
A cross-encoder takes the query and a candidate chunk together in a single forward
pass rather than comparing independent vectors, which gives it much more accurate
relevance scores --- at the cost of being too slow to use for first-stage retrieval.
Over a 30--50 chunk pool it is fast enough. The top 8 chunks by cross-encoder score
go to the LLM.

\subsubsection{Document Filtering}

The five document families (\texttt{strom}, \texttt{erdgas}, \texttt{schufa},
\texttt{creditreform}, \texttt{kosten}) are mapped to their exact filenames in the
ChromaDB metadata. When the user selects a specific document in the UI, the
ChromaDB query includes a \texttt{where} clause restricting retrieval to chunks from
that document (plus any language-specific FAQ entries). This avoids cross-document
contamination when the user knows the relevant document in advance.

\subsection{Language Model and Prompt Engineering}

\subsubsection{Model Selection}

The generative model is \texttt{qwen3.5:9b}, served locally via Ollama. Qwen~3.5 was
chosen over \texttt{llama3.2} after qualitative testing showed better
instruction-following, more consistent JSON output, and stronger performance on
German legal text. The model's thinking mode is explicitly disabled
(\texttt{"think": False}) to reduce latency and suppress verbose reasoning traces
that are not useful in a customer service context.

\subsubsection{Prompt Design}

The system prompt assigns the LLM a role (DEW21 customer service assistant) and
then gives it nine numbered rules. The most important ones: answer only from the
provided passages; if the answer is not there, say exactly ``Diese Information ist
in den bereitgestellten Dokumenten nicht enthalten'' and nothing else; never
invent a second value where only one exists in the text; and always append ``as of
April 1, 2025'' when citing any amount from the \textit{Kostenübersicht}. That
last rule came from a concrete risk --- the fee schedule is updated annually, and
an answer citing an outdated amount without a date would be quietly wrong.

Appended to the rules is a tone block that varies by the selected mode. Easy mode:
1--3 plain-language sentences, no clause references. Standard: key fact first,
clause numbers in bold, up to four bullet points. Technical: opens with the legal
basis (\S~X para.~Y), full terminology, all relevant sub-clauses cited. Then come
the eight retrieved passages as numbered blocks, followed by the last six
conversation turns truncated to 300 characters each.

\subsection{Backend API}

The backend is a single FastAPI application (\texttt{rag\_english/api.py}) that
serves both language variants. The main endpoint is \texttt{POST /query}, which
accepts a JSON body with \texttt{query}, \texttt{language}, \texttt{tone},
\texttt{document} filter, and \texttt{history}, and returns a
\texttt{StreamingResponse} in Server-Sent Events format. Events arrive in order:
a \texttt{sources} event with the retrieved passages, then \texttt{token} events
as the LLM generates, then \texttt{done}. Three supporting endpoints handle
title generation (\texttt{POST /title}, used to label sidebar sessions),
voice transcription (\texttt{POST /transcribe}, running \texttt{faster-whisper}
on an uploaded \texttt{.webm}), and a health check (\texttt{GET /health}).

At startup the server loads both embedding models, the cross-encoder, the Whisper
model, and builds the BM25 indices. Subsequent requests reuse these cached
objects, which is what keeps per-query latency to 11--23 seconds rather than
two minutes.

\subsection{Frontend}

The React frontend (\texttt{rag\_frontend/src/App.tsx}, TypeScript, Vite, Tailwind,
shadcn/ui, Framer Motion) renders the SSE stream incrementally via a custom
\texttt{useTextStream} hook. On the first \texttt{token} event the loading indicator
disappears and the message box fades in; the typewriter effect makes 15-second
generation feel like something is actively happening rather than the system being
stuck. New messages carry an \texttt{animated: true} flag that drives the reveal;
the flag is stripped before saving to \texttt{localStorage} so reloaded conversations
display instantly.

The toolbar has two floating action menus: a tone selector (easy / standard /
technical) and a document filter that restricts retrieval to one of the five
document families. Each chat session is stored in localStorage with its full
message history and an AI-generated 3--5 word title in the sidebar. Voice input is
handled by an \texttt{AiVoiceInput} component that records in the browser and sends
the \texttt{.webm} blob to \texttt{/transcribe}, which runs \texttt{faster-whisper}
(base model, int8 quantised, CPU) and returns the transcription.

\subsection{Evaluation Framework}

\texttt{evaluation/evaluate.py} calls the live \texttt{/query} endpoint for each
question, records the answer, retrieved contexts, and latency, and then computes
two categories of metrics. The first --- semantic similarity (cosine between answer
and ground-truth embeddings) and keyword F1 (token overlap) --- requires no judge
model. The second is RAGAS \cite{ragas}: faithfulness, answer relevancy, context
precision, context recall, and answer correctness, each judged by a local LLM.

Getting RAGAS to run locally was its own problem. RAGAS expects OpenAI by default;
wiring it to a local Ollama instance required a \texttt{ChatOllama} wrapped in a
\texttt{LangchainLLMWrapper}, with a specific base URL and model name, plus a
local sentence-transformers embedding adapter. The integration broke several times
across RAGAS version updates. The final setup uses \texttt{qwen2.5:7b} as the judge
and the same mpnet model used for retrieval as the embedding model, keeping the
evaluation fully within the no-cloud-services constraint.


\section{Results}

\subsection{Evaluation Questions}

The German test set consists of 12 questions with hand-written ground-truth answers,
covering three document families: electricity terms (AGB Strom, 5 questions), gas
terms (AGB Erdgas, 4 questions), and the SCHUFA appendix (3 questions). Questions
were deliberately phrased in natural customer language --- the kind of wording a
customer service employee hears on the phone --- to test whether the system
successfully bridges colloquial phrasing and formal document vocabulary. Query types
include cancellation periods, payment default procedures, price adjustment rights,
gas meter obligations, credit check purposes, and data sharing rules.

The English test set consists of 11 questions across the same document families,
translated into natural English. RAGAS metrics were not computed for the English
run in the final evaluation; only embedding-based metrics were collected.

\subsection{Quantitative Results}

Table~\ref{tab:eval} summarises the evaluation results. The German run used
\texttt{qwen2.5:7b} as the RAGAS judge LLM, keeping the evaluation fully local.

\begin{table}[h]
    \centering
    \begin{tabular}{lcc}
        \toprule
        \textbf{Metric}       & \textbf{DE (standard, $n$=12)} & \textbf{EN (standard, $n$=11)} \\
        \midrule
        Semantic Similarity   & 0.748                          & 0.814                          \\
        Keyword F1            & 0.212                          & 0.259                          \\
        Faithfulness          & 0.807                          & ---                            \\
        Answer Relevancy      & 0.544                          & ---                            \\
        Context Precision     & 0.440                          & ---                            \\
        Context Recall        & 0.618                          & ---                            \\
        Answer Correctness    & 0.475                          & ---                            \\
        Avg.\ Latency (s)     & 22.6                           & 11.9                           \\
        \bottomrule
    \end{tabular}
    \caption{Evaluation results for German (with full RAGAS) and English (embedding
        metrics only) standard-tone runs. All metrics range from 0 to 1.}
    \label{tab:eval}
\end{table}

Table~\ref{tab:perq} shows the per-question breakdown for the German run, revealing
the variance across different question types and document families.

\begin{table}[h]
    \centering
    \small
    \begin{tabular}{llccccc}
        \toprule
        \textbf{Document} & \textbf{Question (abbreviated)}             & \textbf{Sim.} & \textbf{Faith.} & \textbf{Prec.} & \textbf{Recall} & \textbf{Corr.} \\
        \midrule
        Strom    & Cancellation period                          & 0.731 & 1.000 & --- & 0.500 & 0.683 \\
        Strom    & Non-payment consequences                     & 0.804 & 0.750 & 0.927 & 0.333 & 0.368 \\
        Strom    & Price adjustment / notification              & 0.860 & 0.750 & --- & --- & 0.465 \\
        Strom    & Liability for outages                        & 0.822 & 1.000 & --- & --- & 0.581 \\
        Strom    & Advance payment instalment                   & 0.810 & 0.800 & --- & --- & 0.503 \\
        Erdgas   & How to cancel gas contract                   & 0.871 & 0.833 & --- & --- & 0.593 \\
        Erdgas   & Gas measurement and billing                  & 0.755 & 1.000 & --- & --- & 0.325 \\
        Erdgas   & Gas outage / supply interruption             & 0.634 & 0.800 & --- & --- & 0.492 \\
        Erdgas   & Customer meter obligations                   & 0.238 & 0.000 & --- & 0.000 & 0.060 \\
        SCHUFA   & Purpose of SCHUFA credit check               & 0.880 & 1.000 & --- & --- & 0.649 \\
        SCHUFA   & Data transmitted to SCHUFA                   & 0.725 & 0.750 & --- & --- & 0.396 \\
        SCHUFA   & Right to object to SCHUFA data sharing       & 0.848 & 1.000 & --- & --- & 0.587 \\
        \bottomrule
    \end{tabular}
    \caption{Per-question results for the German standard-tone evaluation run.
        ``---'' indicates the metric was not computed for that question by the RAGAS
        judge. Sim.\ = Semantic Similarity, Faith.\ = Faithfulness, Prec.\ = Context
        Precision, Recall = Context Recall, Corr.\ = Answer Correctness.}
    \label{tab:perq}
\end{table}

\subsection{Qualitative Observations}

The gas meter obligations question is the clearest failure in the entire evaluation:
faithfulness 0.000, semantic similarity 0.238, correctness 0.060. Looking at what
actually happened, the retrieved chunks did not contain the specific obligation being
asked about --- the relevant text sits inside a longer section that also covers
unrelated topics, and the chunk boundaries did not isolate it. Rather than refusing
(as rule 2 demands), the model generated a plausible answer based on nearby content.
The prompt rule suppresses most hallucination but not when the retrieved text is
close enough to the topic that the model does not register the miss. This is a
chunking problem more than a model problem.

Faithfulness on the remaining eleven questions averages 0.88, which reflects that
the strict grounding rules in the prompt work when retrieval succeeds. Answer
correctness at 0.475 looks worse than it feels when reading the actual answers:
RAGAS penalises answers that are factually correct but structured differently from
the ground truth or include accurate details the ground truth omitted. The
cancellation period question, for instance, scores 0.683 correctness despite the
system correctly citing both the one-month period and the end-of-billing-period
rule --- the ground truth only stated the first.

Answer relevancy at 0.544 captures a real tendency: the model over-explains. Asked
about the advance notice requirement before supply interruption, it gives the full
procedure including steps the customer did not ask about. This is not wrong, but
RAGAS scores it as only partially relevant because the question could not be
cleanly inferred from the answer.

The 11-second English / 23-second German latency gap is almost entirely generation
time. German legal answers are longer --- the sentences are structurally more complex
--- so the LLM produces more tokens. Retrieval and reranking together take under
2 seconds in both languages. All evaluation runs were on CPU only; a GPU would
change the numbers substantially.


\section{Conclusion and Outlook}

The system works. It answers the majority of legal document questions with correct,
grounded answers, runs entirely on local hardware, and keeps all document content
within DEW21's infrastructure. The one clear failure case --- the gas meter
obligations question --- points to a real architectural gap: chunks that contain the
answer but are too broad for the retrieval pipeline to isolate, and a model that
fills in plausibly rather than refusing. That is fixable with better section
detection, but it requires domain-specific knowledge of how these documents are
structured that goes beyond the current regex-based approach.

The bigger lesson from building this is about where the difficulty actually lives.
Getting a local LLM to produce any answer is easy. Getting it to stay grounded in
the retrieved text, cite the right clause number, use the right tone, and refuse
gracefully when the answer is not there --- that took the bulk of the iteration time.
The nine-rule system prompt did more for answer quality than any model switch.
BM25 cost almost nothing to add and fixed the entire category of fee-lookup failures
that had been unsolvable with dense embeddings alone. The FAQ layer, which felt
like a workaround at first, turned out to give the best return on time invested:
a few hours writing FAQ entries covered the most common customer questions better
than any amount of hyperparameter tuning.

For a production deployment, the main gaps are GPU support (to bring latency under
5 seconds for concurrent users), incremental ingestion (the fee schedule updates
annually; right now re-embedding the whole collection is the only option), and a
larger evaluation set drawn from real customer queries rather than hand-crafted
test questions. The current 12-question German evaluation is enough to identify
failure modes but not enough to say anything statistically meaningful about
overall system quality.

\begin{thebibliography}{9}
    \bibitem{rag}
    Lewis, Patrick, et al. ``Retrieval-augmented generation for knowledge-intensive nlp tasks.''
    \textit{Advances in Neural Information Processing Systems 33} (2020): 9459--9474.

    \bibitem{chromadb}
    Chroma. \textit{Chroma: the AI-native open-source embedding database.}
    \url{https://www.trychroma.com}, 2023.

    \bibitem{nomic}
    Nussbaum, Zach, et al. ``Nomic embed: Training a reproducible long context text embedder.''
    \textit{arXiv preprint arXiv:2402.01613} (2024).

    \bibitem{mpnet}
    Reimers, Nils, and Iryna Gurevych. ``Making monolingual sentence embeddings multilingual using
    knowledge distillation.'' \textit{Proceedings of EMNLP 2020}.

    \bibitem{ragas}
    Es, Shahul, et al. ``RAGAS: Automated evaluation of retrieval augmented generation.''
    \textit{arXiv preprint arXiv:2309.15217} (2023).

    \bibitem{bm25}
    Robertson, Stephen, and Hugo Zaragoza. ``The probabilistic relevance framework: BM25 and
    beyond.'' \textit{Foundations and Trends in Information Retrieval} 3.4 (2009): 333--389.

    \bibitem{qwen}
    Qwen Team. ``Qwen2.5 technical report.'' \textit{arXiv preprint arXiv:2412.15115} (2024).

    \bibitem{fastapi}
    Ramírez, Sebastián. \textit{FastAPI}. \url{https://fastapi.tiangolo.com}, 2019.

    \bibitem{whisper}
    Radford, Alec, et al. ``Robust speech recognition via large-scale weak supervision.''
    \textit{Proceedings of ICML 2023}.
\end{thebibliography}


\part{Self-Reflection}

I was primarily responsible for the backend pipeline: the chunking logic in both
ingestion scripts, the BM25 hybrid retrieval, the cross-encoder reranking, the
query rewriting step, the FAQ layer, the prompt engineering, and the RAGAS
evaluation framework. I also contributed to the React frontend, specifically the
streaming rendering and the voice input integration. The frontend design and the
presentation were more evenly split across the team.

This is the first project I have worked on where the constraint came from a legal
requirement rather than a course rubric. DEW21 cannot let their documents leave
their network. That one requirement changed every decision downstream: which
models I could use, how the backend had to be architected, how the evaluation had
to be structured. At the start I found it frustrating --- every tool I knew how to
use quickly was off-limits. By the end I think it made the project technically more
interesting than it would otherwise have been.

The most disorienting part of the early weeks was that I did not know what ``good''
looked like. In coursework the marking criteria tell you. Here, the only signal was
whether the system gave a useful answer when I typed a question. I spent the first
week testing with simple questions and feeling reasonably confident, then tested
with a fee lookup query and got a completely wrong answer --- the system returned
passages about payment processes in general instead of the \textit{Kostenübersicht}
entry with the actual amount. I tried switching embedding models. I tried different
chunk sizes. Nothing helped. The answer turned out to be structural: dense
embeddings cannot do exact-value retrieval by design. Adding BM25 fixed it in
twenty minutes. That was humbling --- I had spent days on the wrong diagnosis ---
but I do not think I would have understood \textit{why} BM25 was the right fix
without having first exhausted all the wrong options.

Prompt engineering was where I spent the most calendar time, and it is the part
of the project I have the most to say about. The initial prompt was a paragraph
long. The final one is nine numbered rules plus a tone block. Each rule was added
because something went wrong without it. Rule 1 (answer only from the provided
passages) was not strong enough on its own: during SCHUFA testing the model cited
a second SCHUFA contact address that did not appear in any document. It apparently
had some knowledge of SCHUFA from training data and mixed it in. The fix was
rule 2 --- a hard instruction to output an exact refusal string if the answer is not
in the passages, with no paraphrasing allowed. That combination is much harder to
slip past than a vague ``use only provided information''.

Rule 9, the fee date caveat, is the one I am most pleased with because I would not
have thought to add it without reading the documents carefully. The
\textit{Kostenübersicht} says ``Stand: 1. April 2025'' at the top. That means any
answer citing a fee amount could be outdated a year from now. Nobody pointed this
out to me; I noticed it while reading. Building a rule around it took five minutes.
If I had treated the documents as data sources to be ingested rather than documents
to be read, that would not have happened.

The vocabulary mismatch between customer language and legal language was something
I underestimated. A customer says ``cut off my electricity''; the AGB says
``Unterbrechung der Anschlussnutzung''. These are the same thing but they do not
embed close together. My first response was to write more FAQ entries. That worked
for the questions I anticipated. For questions I did not anticipate, I needed
something more general, which is how query rewriting ended up in the pipeline.
What made it work --- obvious in retrospect --- is that rewriting replaces one phrasing
of the query, not the query itself. Running both in parallel means a bad rewrite
cannot make things worse, only better. That asymmetry is what makes the feature
safe to ship.

Getting RAGAS to run locally was the most technically tedious part of the project,
and the most opaque. RAGAS is designed for OpenAI. The documentation for local
models is thin and was written for an older API. I went through about four hours of
\texttt{ImportError}s, version conflicts between RAGAS and LangChain Community, and
timeout failures on slow queries before I had a working setup. The frustrating part
was that failures were silent: RAGAS would return a score of 0 or NaN without
explaining why. I only understood what was happening by reading the RAGAS source
code and tracing which internal function was calling which external endpoint.
Tedious, but without that the metric numbers would have been meaningless.

The hardest thing about this project was the evaluation design, and I handled it
badly. I wrote the test questions and ground-truth answers during the improvement
phase rather than before it. That means every qualitative decision I made ---
adding BM25, adding the FAQ layer, tuning the prompt --- was made based on the same
questions I later used to evaluate the system. The 12-question evaluation tells us
something, but it is not a clean measurement of generalisation. If I did this again
I would write a held-out evaluation set before touching the retrieval pipeline, use
it only at the end, and use a separate development set for iteration. That is basic
machine learning hygiene but it is easy to skip when working under time pressure.

What I did not expect going into this project was how much domain knowledge would
matter. Understanding what a \textit{Zahlungsverzug} is, why the liability
limitation in the AGB electricity document differs from the one in the gas
document, what the legal significance of ``\S~7 NAV'' is --- none of this appears in
any machine learning course. But it is what separates a system that produces
correct answers from one that produces confident-sounding plausible answers. I
read the documents, all of them, at least twice. That is probably the single most
useful thing I did for the quality of the final system.

\end{document}
