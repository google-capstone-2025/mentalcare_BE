from fastapi import APIRouter
from app.schemas.aggregate import AggregateRequest, AggregateResponse
from app.services.rag_service import aggregate as aggregate_service


router = APIRouter(prefix="/api/aggregate", tags=["RAG-Aggregate"])


@router.post("", response_model=AggregateResponse)
def run_aggregate(payload: AggregateRequest):
    out = aggregate_service(retrieved_docs=payload.docs)
    return out