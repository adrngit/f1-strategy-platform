from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    """Check that the API is running."""
    return {"status": "ok", "service": "f1-strategy-platform"}
