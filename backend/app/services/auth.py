import bcrypt
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate


def hash_password(password: str) -> str:
    """Hash a plain text password using bcrypt."""
    # bcrypt works on bytes not strings, so we encode the password first
    password_bytes = password.encode("utf-8")
    # gensalt generates a random salt - ensures two users with the same
    # password get completely different hashes, defeating bulk cracking attacks
    salt = bcrypt.gensalt()
    # hashpw combines the password and salt, runs bcrypt, returns bytes
    # we decode back to a string so it can be stored in the database as text
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    # bcrypt.checkpw hashes the plain password the same way and compares
    # we never decrypt - bcrypt is a one way function, decryption is impossible
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def get_user_by_email(db: Session, email: str) -> User | None:
    """Fetch a user by email address."""
    # db.query(User) starts a SELECT on the users table
    # filter adds a WHERE clause - only return rows where email matches
    # first() returns one result or None if no match found
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user_in: UserCreate) -> User:
    """Create a new user with a hashed password."""
    # hash the plain password before touching the database
    # the original password is never stored anywhere
    hashed = hash_password(user_in.password)
    # create the SQLAlchemy model instance - just a Python object so far
    # nothing has been written to the database yet
    db_user = User(
        email=user_in.email,
        hashed_password=hashed,
    )
    # add the object to the session - queues it for insertion
    db.add(db_user)
    # commit writes the INSERT statement to PostgreSQL
    # if anything fails, PostgreSQL rolls back automatically
    db.commit()
    # after commit SQLAlchemy clears the object from memory
    # refresh re-fetches it from the database so we get the generated id and created_at
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Verify credentials and return the user, or None if invalid."""
    # fetch the user by email first - this line was missing in your version
    user = get_user_by_email(db, email)
    # if no user found, return None immediately
    if not user:
        return None
    # if password is wrong, return None
    # we return the same None in both cases deliberately - never tell an attacker
    # whether the email exists or the password was wrong, either is useful to them
    if not verify_password(password, user.hashed_password):
        return None
    return user
