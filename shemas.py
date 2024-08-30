from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime #gérer les données de type date et heure

class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    borrowed_books: List["Book"] = []

    class Config:
        orm_mode = True

class BookBase(BaseModel):
    title: str
    author: str
    isbn: str

class BookCreate(BookBase):
    pass

class BorrowRequest(BaseModel):
    user_id: int

class Book(BookBase):
    id: int
    borrower_id: Optional[int] = None

    class Config:
        orm_mode = True
        
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str