from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token
from app.schemas.user import UserCreate, UserResponse, Token
from app.services.auth import create_user, get_user_by_email, authenticate_user

# APIRouter groups related endpoints together
# all routes defined on this router will be registered in main.py
router = APIRouter()


# response_model=UserResponse tells FastAPI to filter the response through this schema
# even though create_user returns a full User object, only UserResponse fields are sent
# status_code=201 is correct REST convention for resource creation
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # check if email is already taken before attempting to create
    existing = get_user_by_email(db, user_in.email)
    if existing:
        # 400 Bad Request - the client sent invalid data (duplicate email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )
    return create_user(db, user_in)


# response_model=Token means FastAPI will validate and shape the response
# as a Token object containing access_token and token_type
@router.post("/login", response_model=Token)
def login(user_in: UserCreate, db: Session = Depends(get_db)):
    """Authenticate a user and return a JWT token."""
    # authenticate_user checks email exists and password matches
    # returns None for both wrong email and wrong password - never reveal which
    user = authenticate_user(db, user_in.email, user_in.password)
    if not user:
        # 401 Unauthorized - the correct status for failed authentication
        # WWW-Authenticate header is required by the HTTP spec for 401 responses
        # it tells the client which authentication scheme to use
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # create a JWT token with the user's email as the subject
    # the token encodes who the user is and when it expires
    token = create_access_token(subject=user.email)
    # return the token and type - the client stores this and sends it
    # in the Authorization header on every future request
    return Token(access_token=token, token_type="bearer")
