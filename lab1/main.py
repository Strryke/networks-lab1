from enum import Enum
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, Header, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import uvicorn
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import Session
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


class BookModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    title: str
    author: str


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None

    # don't allow extra
    model_config = ConfigDict(extra="forbid")


class Sort(str, Enum):
    id = "id"
    title = "title"
    author = "author"


@app.get("/books")
def get_books(count: int = 10, sort: Sort = Sort.id, db: Session = Depends(get_db)):
    if sort not in ["id", "title", "author"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort parameter. Must be one of: id, title, author",
        )
    books = db.query(Book).order_by(getattr(Book, sort)).limit(count).all()
    formatted_books = [
        BookModel(id=book.id, title=book.title, author=book.author) for book in books
    ]
    print("books:", formatted_books)
    return formatted_books


@app.get("/books/{book_id}")
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return BookModel.model_validate(book)


@app.post("/books")
def add_book(book: BookModel, db: Session = Depends(get_db)):
    new_book = Book(title=book.title, author=book.author)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return {"message": "Book added", "book": BookModel.model_validate(new_book)}


@app.delete("/books/batch")
def delete_books(book_ids: list[int] = Query(...), db: Session = Depends(get_db)):
    books = db.query(Book).filter(Book.id.in_(book_ids)).all()

    if not books:
        raise HTTPException(status_code=404, detail="No matching books found")

    for book in books:
        db.delete(book)
    db.commit()

    return {"message": f"{len(books)} books deleted"}


@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return {"message": "Book deleted"}


@app.put("/books/{book_id}")
def update_book(
    book_id: int,
    book: BookUpdate,
    db: Session = Depends(get_db),
):
    author = book.author
    title = book.title
    current_book = db.query(Book).filter(Book.id == book_id).first()
    if not current_book:
        raise HTTPException(status_code=404, detail="Book not found")
    if title:
        current_book.title = title
    if author:
        current_book.author = author
    db.commit()
    db.refresh(current_book)
    return {"message": "Book updated", "book": BookModel.model_validate(current_book)}


admin_password = "admin:password"


@app.get("/admin")
def admin_page(Authorization: str = Header(None)):
    if not Authorization:
        raise HTTPException(status_code=401, detail="No Authorization header provided")
    if Authorization != admin_password:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"message": "Admin page"}


def main() -> None:
    uvicorn.run("lab1.main:app", host="0.0.0.0", reload=True)


if __name__ == "__main__":
    main()
