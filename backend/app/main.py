from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.documents import router as documents_router
from app.api.routes.extraction import router as extraction_router
from app.api.routes.embeddings import router as embeddings_router
from app.api.routes.similarity import router as similarity_router

app = FastAPI(title="ResumeMatch AI API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(documents_router)
app.include_router(extraction_router)
app.include_router(embeddings_router)
app.include_router(similarity_router)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
