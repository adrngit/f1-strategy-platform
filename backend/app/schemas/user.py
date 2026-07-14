from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel): #What the client sends when registering or logging in
    email: EmailStr #Validates the email format automatically. "notanemail" would be rejected
    password: str #Plain text password. Only the hash is stored not the str

class UserResponse(BaseModel): #UserResponse is what we need to send back to the client
    id: str
    email: str
    is_active: bool
    created_at: datetime

    #This tells pydantic that it can read data from SQLAlchemy model objects
    #Without this, converting a database User object to this schema would fail
    model_config = {"from_attributes": True}

class UserInDB(UserResponse): #UserInDB extends UserResponse with the hashed password
    hashed_password: str #This is used internally between service layer and never shared to the clients

class Token(BaseModel): #Token is then what we return after a successful login
    access_token: str #This is the JWT string the client will store and send together with future responses
    token_type: str #token_type is always the bearer for JWT and it tell the client how to send the token
