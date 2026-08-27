from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import config
from .chunking import chunk_text
from .claude_client import answer_question
from .embeddings import embed_passages, embed_query
from .extract import extract_text
from .vector_store import store

app = FastAPI(title="RAG Notes Search")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str
    top_k: int | None = None


class SourceOut(BaseModel):
    filename: str
    text: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceOut]


class DocumentOut(BaseModel):
    id: str
    filename: str
    num_chunks: int


@app.get("/api/documents", response_model=list[DocumentOut])
def list_documents() -> list[DocumentOut]:
    return [DocumentOut(**doc.__dict__) for doc in store.list_documents()]


@app.post("/api/documents", response_model=DocumentOut)
async def upload_document(file: UploadFile = File(...)) -> DocumentOut:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    text = extract_text(file.filename, content)
    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=400, detail="Could not extract any text from this file")

    vectors = embed_passages(chunks)
    doc = store.add_document(file.filename, chunks, vectors)
    return DocumentOut(**doc.__dict__)


@app.delete("/api/documents/{doc_id}")
def delete_document(doc_id: str) -> dict:
    deleted = store.delete_document(doc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"deleted": doc_id}


@app.post("/api/query", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty")

    query_vector = embed_query(req.question)
    top_k = req.top_k or config.TOP_K
    results = store.search(query_vector, top_k)

    try:
        answer = answer_question(req.question, [chunk for chunk, _ in results])
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    sources = [
        SourceOut(filename=chunk.filename, text=chunk.text, score=score)
        for chunk, score in results
    ]
    return QueryResponse(answer=answer, sources=sources)


frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
