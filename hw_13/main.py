import os
from datetime import date, timedelta, datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Query, status, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
import cloudinary
import cloudinary.uploader
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

from database import engine, get_db  
import models
import schemas

# 1. ЗАВАНТАЖЕННЯ НАЛАШТУВАНЬ
load_dotenv()
# СТВОРЕННЯ ТАБЛИЦЬ ПРИ СТАРТІ (ВАЖЛИВО!)
models.Base.metadata.create_all(bind=engine)

SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key_change_me")
ALGORITHM = "HS256"

# Налаштування Cloudinary (беруться з .env)
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_NAME"), 
    api_key=os.getenv("CLOUDINARY_API_KEY"), 
    api_secret=os.getenv("CLOUDINARY_API_SECRET"), 
    secure=True
)

# Налаштування Пошти
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 465)),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER='templates'
)

# 2. ІНІЦІАЛІЗАЦІЯ LIMITER (REDIS)
REDIS_HOST = os.getenv("REDIS_HOST", "redis") # "redis" для Docker
limiter = Limiter(key_func=get_remote_address, storage_uri=f"redis://{REDIS_HOST}:6379")

app = FastAPI(title="Contact Management API v2")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 3. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- AUTH HELPERS ---

def create_email_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire, "scope": "email_verification"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_password_hash(password: str): return pwd_context.hash(password)

def verify_password(plain, hashed): return pwd_context.verify(plain, hashed)

def create_tokens(data: dict):
    access = jwt.encode({"exp": datetime.utcnow() + timedelta(minutes=30), "sub": data["sub"], "scope": "access_token"}, SECRET_KEY, algorithm=ALGORITHM)
    refresh = jwt.encode({"exp": datetime.utcnow() + timedelta(days=7), "sub": data["sub"], "scope": "refresh_token"}, SECRET_KEY, algorithm=ALGORITHM)
    return access, refresh

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("scope") != "access_token": raise HTTPException(status_code=401)
        email = payload.get("sub")
        user = db.query(models.User).filter(models.User.email == email).first()
        if user is None: raise HTTPException(status_code=401)
        return user
    except JWTError: raise HTTPException(status_code=401)

# --- ROUTES ---

@app.post("/signup", status_code=201)
async def signup(body: schemas.UserSchema, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == body.email).first():
        raise HTTPException(status_code=409, detail="Email exists")
    
    new_user = models.User(email=body.email, hashed_password=get_password_hash(body.password), confirmed=False)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    token = create_email_token({"sub": new_user.email})
    # У відповідь повертаємо токен, щоб ви могли підтвердити пошту без SMTP
    return {"msg": "User created. Use the token to confirm", "verification_token_debug": token}

@app.get("/confirm_email/{token}")
def confirm_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user: raise HTTPException(status_code=404)
        user.confirmed = True
        db.commit()
        return {"msg": "Email confirmed"}
    except JWTError: raise HTTPException(status_code=400, detail="Invalid token")

@app.post("/login")
def login(body: schemas.UserSchema, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.confirmed:
        raise HTTPException(status_code=401, detail="Email not confirmed")
    
    access, refresh = create_tokens({"sub": user.email})
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

@app.patch("/users/avatar")
async def update_avatar(file: UploadFile = File(...), current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    r = cloudinary.uploader.upload(file.file, public_id=f'avatars/{current_user.email}', overwrite=True)
    current_user.avatar = r.get('url')
    db.commit()
    return {"avatar_url": current_user.avatar}

@app.post("/contacts/", status_code=201)
@limiter.limit("2/minute")
async def create_contact(request: Request, contact: schemas.ContactCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_contact = models.Contact(**contact.model_dump(), user_id=current_user.id)
    db.add(db_contact)
    db.commit()
    return db_contact

@app.get("/contacts/")
def read_contacts(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Contact).filter(models.Contact.user_id == current_user.id).all()