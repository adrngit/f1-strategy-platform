from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.f1 import router as f1_router


app = FastAPI(
    title = "F1 Strategy Intelligence Platform",
    description = "API for F1 race strategy analysis and predictions",
    version = "0.1.0"
)
 
app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(f1_router, prefix="/api/v1/f1", tags=["f1"])

@app.get("/")
def root():
    """Root endpoint."""
    return{"message": "F1 Strategy Intelligence Platform API"}