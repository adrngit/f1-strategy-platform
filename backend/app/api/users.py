from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter()

@router.get("/me", response_model=UserResponse)

def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""

    #get_current_user already did all the work, if we reach this line, the user is auth and active and return them.
    #FastAPI filters through UserResponse automatically return current_user
    return current_user