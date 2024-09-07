from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship, mapped_column
from pgvector.sqlalchemy import Vector
import enum

Base = declarative_base()

EMBEDDING_DIMENSION = 3072

class ContentType(enum.Enum):
    EMAIL = 'email'
    FILE = 'file'
    LINK = 'link'

class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True)
    sender = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    message_id = Column(String, unique=True, nullable=False)
    embedding = relationship("Embedding", back_populates="email", cascade="all, delete-orphan")

class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)  # Add this line
    embedding = relationship("Embedding", back_populates="file", cascade="all, delete-orphan")

class Link(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    embedding = relationship("Embedding", back_populates="link", cascade="all, delete-orphan")

class Embedding(Base):
    __tablename__ = 'embeddings'

    id = Column(Integer, primary_key=True)
    embedding = mapped_column(Vector(EMBEDDING_DIMENSION))
    content_type = Column(Enum(ContentType), nullable=False)
    email_id = Column(Integer, ForeignKey('emails.id', ondelete='CASCADE'), nullable=True)
    file_id = Column(Integer, ForeignKey('files.id', ondelete='CASCADE'), nullable=True)
    link_id = Column(Integer, ForeignKey('links.id', ondelete='CASCADE'), nullable=True)
    email = relationship("Email", back_populates="embedding")
    file = relationship("File", back_populates="embedding")
    link = relationship("Link", back_populates="embedding")
