from fastapi import FastAPI
from app.core.config import settings
from app.routers import items

app = FastAPI(title=settings.APP_NAME)

@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok"}

app.include_router(items.router)
