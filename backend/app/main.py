from fastapi import FastAPI
from app.api.health import router as health_router

app = FastAPI(
    title = "F1 Strategy Intelligence Platform",
    description = "API for F1 race strategy analysis and predictions",
    version = "0.1.0"
)

app.include_router(health_router, prefix="/api/v1")

@app.get("/")
def root():
    """Root endpoint."""
    return{"message": "F1 Strategy Intelligence Platform API"}