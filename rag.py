import logging
import ollama
from app.vectordb import collection, model

logger = logging.getLogger(__name__)

MODEL_NAME = "llama3.2"


def detect_filename(question):
    """If the question mentions a filename already uploaded, return it."""
    all_meta = collection.get()["metadatas"]
    filenames = {m["filename"] for m in all_meta}
    q_lower = question.lower()
    for fname in filenames:
        name_no_ext = fname.rsplit(".", 1)[0].lower()
        if name_no_ext in q_lower or fname.lower() in q_lower:
            return fname
    return None


def retrieve(question, k=4):
    q_emb = model.encode([question]).tolist()
    target_file = detect_filename(question)

    query_args = {"query_embeddings": q_emb, "n_results": k}
    if target_file:
        query_args["where"] = {"filename": target_file}

    res = collection.query(**query_args)
    chunks = []
    for doc, meta in zip(res["documents"][0], res["metadatas"][0]):
        chunks.append({"text": doc, "filename": meta["filename"], "page": meta["page"]})
    return chunks


def answer_question(question):
    if collection.count() == 0:
        return {"answer": "Please upload a document first.", "sources": []}

    chunks = retrieve(question)
    if not chunks:
        return {"answer": "I could not find relevant content for that.", "sources": []}

    context = "\n\n".join(
        f"[{c['filename']} - page {c['page']}]\n{c['text']}" for c in chunks
    )

    messages = [
        {
            "role": "system",
            "content": "You answer questions using ONLY the given context. "
                       "If the answer is not in the context, say you could not find it in the documents.",
        },
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
    ]

    response = ollama.chat(model=MODEL_NAME, messages=messages)
    answer = response["message"]["content"]

    seen, sources = set(), []
    for c in chunks:
        key = (c["filename"], c["page"])
        if key not in seen:
            seen.add(key)
            sources.append({"filename": c["filename"], "page": c["page"]})

    logger.info(f"Answered question using {len(sources)} sources")
    return {"answer": answer, "sources": sources}