from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.db.session import get_db, init_db
from api.schemas import UserRegister, UserLogin, Token, UserOut
from core.auth.utils import create_access_token
from core.auth import crud

router = APIRouter(prefix="/users", tags=["users"])

# ----- Registration -----
@router.post("/register", response_model=UserOut)
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(crud.User).filter(crud.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = crud.create_user(db, user.email, user.password)
    # TODO: send verification email with token
    return db_user

# ----- Login -----
@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = crud.authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not db_user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")
    token = create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}

# ----- Verify (Simulated) -----
@router.get("/verify")
def verify(token: str, db: Session = Depends(get_db)):
    # In production, token comes from email link
    db_user = db.query(crud.User).filter(crud.User.email == token).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    crud.verify_user(db, db_user)
    return {"message": "User verified successfully"}

