from enum import Enum
from typing import Optional
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import DeclarativeBase
import uvicorn
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import Session
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)
class Base(DeclarativeBase):
    pass

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, index=True)
    author = Column(String, index=True)

Base.metadata.create_all(engine)

with Session(engine) as session:
    print("seeding books, count:", session.query(Book).count())
    if session.query(Book).count() == 0:
        print("count:", session.query(Book).count())
        session.add(Book(title="The Great Gatsby", author="F. Scott Fitzgerald"))
        session.add(Book(title="1984", author="George Orwell"))
        session.add(Book(title="Pride and Prejudice", author="Jane Austen"))
        session.commit()

app = FastAPI()










@app.get("/")
def read_root():
    return {"message": "Welcome to the Books API"}


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}

class BookModel(BaseModel):
   model_config = ConfigDict(from_attributes=True)
   id: int
   title: str
   author: str

class Sort(str, Enum):
    id = "id"
    title = "title"
    author = "author"

@app.get("/books")
def get_books(count: int = 10, sort: Sort = Sort.id):
    if sort not in ["id", "title", "author"]:
        raise HTTPException(status_code=400, detail="Invalid sort parameter. Must be one of: id, title, author")
    with Session(engine) as session:
        books = session.query(Book).order_by(getattr(Book, sort)).limit(count).all()
        formatted_books = [BookModel(id=book.id, title=book.title, author=book.author) for book in books]
        print("books:", formatted_books)
        return formatted_books


@app.post("/books")
def add_book(title: str, author: str):
    if not title or not author:
        raise HTTPException(status_code=400, detail="Title and author are required")
    with Session(engine) as session:
        new_book = Book(title=title, author=author)
        session.add(new_book)
        session.commit()
        session.refresh(new_book)
        return {"message": "Book added", "book": new_book}
    

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    with Session(engine) as session:
        book = session.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        session.delete(book)
        session.commit()
        return {"message": "Book deleted"}

@app.put("/books/{book_id}")
def update_book(book_id: int, title: Optional[str] = None, author: Optional[str] = None):
    with Session(engine) as session:
        book = session.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        if title:
            book.title = title
        if author:
            book.author = author
        session.commit()
        session.refresh(book)
        return {"message": "Book updated", "book": book}
    
@app.delete("/books/batch")
def delete_books(book_ids: list[int]):
    with Session(engine) as session:
        for book_id in book_ids:
            book = session.query(Book).filter(Book.id == book_id).first()
            if not book:
                raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")

admin_password = "admin:password"
@app.get("/admin")
def admin_page(Authorization: str = Header(...)):
    if not Authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if Authorization != admin_password:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"message": "Admin page"}
                
def main() -> None:
    uvicorn.run("lab1.main:app", host="0.0.0.0", reload=True)


if __name__ == "__main__":
    main()