from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import FRONTEND_ORIGIN

from app.api.routes.documents import router as documents_router
from app.api.routes.extraction import router as extraction_router
from app.api.routes.embeddings import router as embeddings_router
from app.api.routes.similarity import router as similarity_router
from app.api.routes.scoring import router as scoring_router
from app.api.routes.analysis import router as analysis_router
from app.api.routes.pipeline import router as pipeline_router
from app.api.routes.verification import router as verification_router

app = FastAPI(title="ResumeMatch AI API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(documents_router)
app.include_router(extraction_router)
app.include_router(embeddings_router)
app.include_router(similarity_router)
app.include_router(scoring_router)
app.include_router(analysis_router)
app.include_router(pipeline_router)
app.include_router(verification_router)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
