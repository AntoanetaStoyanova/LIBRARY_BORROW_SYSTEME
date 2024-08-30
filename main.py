from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles  # Importer StaticFiles
from pydantic import BaseModel
from typing import List, Annotated
from flask import Flask
import uvicorn

import models as models
import shemas as shemas
import auth as auth 

from database import engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse  # Importer RedirectResponse pour rediriger vers le HTML

app = FastAPI()

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

models.Base.metadata.create_all(bind=engine) # will create all of the tables and columns in postgres=

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

#api endpoints

@app.get("/")
async def get_index():
    return RedirectResponse(url="/static/index.html")


@app.get("/login")
async def get_index_login():
    return RedirectResponse(url="/static/login.html")

@app.get("/borrow")
async def get_index_borrow():
    return RedirectResponse(url="/static/borrow.html")



@app.post("/token", response_model=shemas.Token)
def login(form_data: auth.OAuth2PasswordRequestForm = Depends(), 
          db:  Session = Depends(get_db)):
    return auth.authenticate_user(form_data, db)

@app.get("/users/me", response_model=shemas.User)
def read_users_me(current_user: shemas.User = Depends(auth.get_current_user)):
    return current_user

@app.post("/users/", response_model=shemas.User)
def create_user(user: shemas.UserCreate, db: db_dependency):
    db_user = models.User(
        first_name=user.first_name, 
        last_name=user.last_name, 
        email=user.email, 
        password=auth.get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}", response_model=shemas.User)
def read_user(user_id: int, 
              db: db_dependency, 
              current_user: models.User = Depends(auth.get_current_user)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/books/", response_model=shemas.Book)
def create_book(book: shemas.BookCreate, db: db_dependency):
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get("/books/{book_id}", response_model=shemas.Book)
def read_book(book_id: int, db: db_dependency):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@app.post("/borrow/{book_id}/{user_id}")
def borrow_book(book_id: int, user_id: int, 
                db: db_dependency, 
                current_user: models.User = Depends(auth.get_current_user)):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if db_book is None or db_user is None:
        raise HTTPException(status_code=404, detail="Book or User not found")
    
    if db_book.borrower_id is not None:
        raise HTTPException(status_code=400, detail="Book is already borrowed")
    
    db_book.borrower_id = user_id
    db.commit()
    return {"message": "Successfully borrowed"}

@app.get("/user/{user_id}/borrowed_books", response_model=List[shemas.Book])
def get_borrowed_books(user_id: int, 
                       db: db_dependency, 
                       current_user: models.User = Depends(auth.get_current_user)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user.borrowed_books

@app.get("/book/{book_id}/available", response_model=bool)
def check_book_availability(book_id: int, db: db_dependency):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book.borrower_id is None



