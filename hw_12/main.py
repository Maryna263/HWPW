from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import date, timedelta, datetime
from typing import List, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from database import engine, get_db  
from models import Base 
import models
import schemas

# --- Налаштування безпеки ---
SECRET_KEY = "super_secret_key_change_me" # У реальному проєкті беріть з .env
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Contact Management API with Auth")

# --- Допоміжні функції Auth ---

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_tokens(data: dict):
    # Access token
    access_expire = datetime.utcnow() + timedelta(minutes=15)
    access_token = jwt.encode({"exp": access_expire, "sub": data["sub"], "scope": "access_token"}, SECRET_KEY, algorithm=ALGORITHM)
    # Refresh token
    refresh_expire = datetime.utcnow() + timedelta(days=7)
    refresh_token = jwt.encode({"exp": refresh_expire, "sub": data["sub"], "scope": "refresh_token"}, SECRET_KEY, algorithm=ALGORITHM)
    return access_token, refresh_token

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("scope") != "access_token":
            raise credentials_exception
        email: str = payload.get("sub")
        if email is None: raise credentials_exception
    except JWTError: raise credentials_exception
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None: raise credentials_exception
    return user

# --- Роути Аутентифікації ---

@app.post("/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def signup(body: schemas.UserSchema, db: Session = Depends(get_db)):
    # Перевірка на існуючий email (Error 409)
    exist_user = db.query(models.User).filter(models.User.email == body.email).first()
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    
    new_user = models.User(email=body.email, hashed_password=get_password_hash(body.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.TokenModel)
def login(body: schemas.UserSchema, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    access, refresh = create_tokens({"sub": user.email})
    user.refresh_token = refresh
    db.commit()
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

# --- Захищені операції з контактами (Тільки для власника) ---

@app.post("/contacts/", response_model=schemas.ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_contact = models.Contact(**contact.model_dump(), user_id=current_user.id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@app.get("/contacts/", response_model=List[schemas.ContactResponse])
def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Фільтрація: повертаємо ТІЛЬКИ контакти поточного юзера
    return db.query(models.Contact).filter(models.Contact.user_id == current_user.id).offset(skip).limit(limit).all()

@app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id, models.Contact.user_id == current_user.id).first()
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found or access denied")
    db.delete(db_contact)
    db.commit()
    return None