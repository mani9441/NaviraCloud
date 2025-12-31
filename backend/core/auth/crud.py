from sqlalchemy.orm import Session
from core.db.models import User
from core.auth.utils import hash_password, verify_password
from datetime import datetime

# ----- Create user -----
def create_user(db: Session, email: str, password: str) -> User:
    hashed = hash_password(password)
    user = User(email=email, password_hash=hashed, is_verified=False, created_at=datetime.utcnow())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# ----- Authenticate user -----
def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

# ----- Verify user -----
def verify_user(db: Session, user: User):
    user.is_verified = True
    db.commit()
    db.refresh(user)
    return user

