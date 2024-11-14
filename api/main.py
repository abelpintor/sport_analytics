from fastapi import FastAPI, Form, HTTPException, Request, Depends, status
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
import os
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import models  
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "secret_key_example")
TOKEN_EXPIRATION_TIME = 15 * 60  
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")


app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_token(data: dict):
    data["exp"] = datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRATION_TIME)
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, username: str, email: str, password: str, age: int):
    hashed_password = pwd_context.hash(password)
    db_user = models.User(username=username, email=email, hashed_password=hashed_password, age=age)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/", response_class=JSONResponse)
def root(request: Request):
    return {"message": 'API funcionando'}


@app.post("/login", response_class=JSONResponse)
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    
  
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
  
    token = create_token({"username": user.username, "id": user.id})
    
    
    response = JSONResponse({
        "token": token
    }, status_code=302)
    
    return response


@app.post("/register")
async def register(username: str = Form(...), email: str = Form(...), password: str = Form(...), age: int = Form(...), db: Session = Depends(get_db)):
    if get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = create_user(db, username, email, password, age)
    return {"msg": "User created successfully", "user": user.username}


@app.post("/predict")
async def predict_match(request: Request, home_team: str = Form(...), away_team: str = Form(...)): 
    #prediction = predict(home_team, away_team, season)
    return {
        "probabilidad_equipo_1": 20,
        "nombre_equipo_local":"America",
        "nombre_equipo_visitante":"Chivas",
        "goles_promedio": 3,
        "corners_promedio": 7,

    }
