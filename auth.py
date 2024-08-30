from dotenv import load_dotenv
import os
load_dotenv()  # Charger les variables d'environnement depuis le fichier .env

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Optional
import shemas as shemas
import models as models
from database import SessionLocal
from sqlalchemy.orm import Session




# Configuration pour OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configuration
# Configurer la clé secrète depuis les variables d'environnement
SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# CryptContext pour le hashing des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Fonction pour créer un hash de mot de passe
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)



# Dependency for the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fonction pour créer un token d'accès
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Fonction pour vérifier le token
def get_current_user(token: str = Depends(oauth2_scheme), 
                     db: Session = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = shemas.TokenData(email=email)
    except jwt.PyJWTError:
        raise credentials_exception

    db = SessionLocal()
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

# Fonction pour gérer la connexion et obtenir un token
def authenticate_user(form_data: OAuth2PasswordRequestForm, db: Session) -> shemas.Token:
    db = SessionLocal()
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return shemas.Token(access_token=access_token, token_type="bearer")