from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship  # créer les relationships between tables
from database import Base

# Classe User (Lecteur)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)  # PrimaryKey 
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    borrowed_books = relationship("Book", back_populates="borrower")  # relation avec les livres empruntés est férée par borrowed_books

# Classe Book (Livre)
class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    isbn = Column(String, unique=True, index=True)
    
    borrower_id = Column(Integer, ForeignKey('users.id')) # ForeignKey 

    borrower = relationship("User", back_populates="borrowed_books")  # Relation avec le lecteur qui emprunte le livre est gérée par borrowed_id


