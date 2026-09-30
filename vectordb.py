import hashlib
import logging
import chromadb
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection("documents")


def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def is_duplicate(fhash):
    result = collection.get(where={"file_hash": fhash}, limit=1)
    return len(result["ids"]) > 0


def chunk_text(text, size=800, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks


def add_document(filename, pages, fhash):
    ids, docs, metas = [], [], []
    for p in pages:
        for i, chunk in enumerate(chunk_text(p["text"])):
            if not chunk.strip():
                continue
            ids.append(f"{fhash}_{p['page']}_{i}")
            docs.append(chunk)
            metas.append({"filename": filename, "page": p["page"], "file_hash": fhash})

    if not docs:
        return 0

    embeddings = model.encode(docs).tolist()
    collection.add(ids=ids, documents=docs, embeddings=embeddings, metadatas=metas)
    logger.info(f"Stored {len(docs)} chunks for {filename}")
    return len(docs)