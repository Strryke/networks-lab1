from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, index=True)
    author = Column(String, index=True)


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
