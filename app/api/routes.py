from pathlib import Path 
from fastapi import APIRouter, UploadFile, File, HTTPException, Header 
from pydantic import BaseModel, Field 
from app.core.config import get_settings 
from app.rag.workflow import ask 
from app.services.ingestion import load_file, chunk_documents, SUPPORTED 
from app.services.audit import write_audit 
from app.rag.vectorstore import add_documents


router = APIRouter(prefix="/api")


settings = get_settings()

class ChatRequest(BaseModel): 
    question : str = Field(min_length=2, max_length=3000)
    
@router.get("/health")
def health():
    return {
        "status":"ok",
        "service":settings.app_name
    }
    
@router.post("/chat")
def chat(payload: ChatRequest):
    try:
        result = ask(payload.question)
        write_audit(payload.question, result["source_used"], result.get("trace",[]))
        
        return {
            "answer": result["answer"],
            "source_used": result["source_used"],
            "trace": result.get("trace",[]),
            "citations": result.get("citations",[]), 
            "rewritten_query": result.get("current_query", payload.question)
        }
        
    except Exception as exc: 
        raise HTTPException(status_code=500, detail=str(exc)) from exc 
    
@router.post("/inngest")
async def ingest(file: UploadFile = File(...), x_admin_key: str = Header(default="")):
    if x_admin_key != settings.admin_api_key: 
        raise HTTPException(status_code=401, detail="Invalid admin key")

    suffix = Path(file.filename or "").suffix.lower()
    
    if suffix not in SUPPORTED: 
        supported_formats = ", ".join(sorted(SUPPORTED))
        raise HTTPException(status_code=400, detail=f"Supported: {supported_formats}")
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing")

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = upload_dir / Path(file.filename).name 
    dest.write_bytes(await file.read())
    docs = load_file(dest)
    chunks = chunk_documents(docs)
    
    ids = add_documents(chunks)
    
    return {
        "message": "Document Indexed", 
        "file": dest.name,
        "chunks_count": len(chunks),
        "document_ids": ids
    }
