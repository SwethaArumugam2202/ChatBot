import logging
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from app.ingest import extract_text
from app.vectordb import file_hash, is_duplicate, add_document
from pydantic import BaseModel
from app.rag import answer_question
from app.database import init_db, save_message, get_history
from fastapi.staticfiles import StaticFiles

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()
init_db()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED = (".pdf", ".txt", ".docx")


@app.get("/status")
def home():
    return {"status": "running"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED:
        raise HTTPException(status_code=400, detail="Only PDF, TXT, DOCX allowed")

    path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(path, "wb") as f:
            f.write(await file.read())

        fhash = file_hash(path)
        if is_duplicate(fhash):
            logger.info(f"Duplicate skipped: {file.filename}")
            return {"filename": file.filename, "status": "already processed"}

        pages = extract_text(path)
        chunks = add_document(file.filename, pages, fhash)
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Could not process file")

    return {"filename": file.filename, "pages": len(pages), "chunks": chunks, "status": "processed"}
class ChatRequest(BaseModel):
    question: str


@app.post("/chat")
def chat(req: ChatRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question is empty")
    try:
        result = answer_question(req.question)
        save_message(req.question, result["answer"], result["sources"])
        return result
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail="Could not generate answer")

@app.get("/history")
def history():
    return get_history()

app.mount("/", StaticFiles(directory="static", html=True), name="static")