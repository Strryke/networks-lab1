from sqlalchemy.orm import Session
from lab1.models import Book


def seed_initial_books(session: Session):
    if session.query(Book).count() == 0:
        session.add(Book(title="The Great Gatsby", author="F. Scott Fitzgerald"))
        session.add(Book(title="1984", author="George Orwell"))
        session.add(Book(title="Pride and Prejudice", author="Jane Austen"))
        session.commit()
