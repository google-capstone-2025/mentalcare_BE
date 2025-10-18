from fastapi import APIRouter
from app.schemas.retrieve import RetrieveRequest, RetrieveResponse
from app.services.rag_service import retrieve as retrieve_service


router = APIRouter(prefix="/api/retrieve", tags=["RAG-Retrieve"])


@router.post("", response_model=RetrieveResponse)
def run_retrieve(payload: RetrieveRequest):
    out = retrieve_service(user_text=payload.input_text, top_k=payload.top_k)
    return out