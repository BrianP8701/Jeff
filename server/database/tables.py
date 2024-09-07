from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Float
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class ContentType(enum.Enum):
    EMAIL = 'email'
    FILE = 'file'
    LINK = 'link'

class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True)
    sender = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    message_id = Column(String(255), unique=True, nullable=False)
    embedding = relationship("Embedding", back_populates="email", cascade="all, delete-orphan")

class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    path = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    embedding = relationship("Embedding", back_populates="file", cascade="all, delete-orphan")

class Link(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True)
    url = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    embedding = relationship("Embedding", back_populates="link", cascade="all, delete-orphan")

class Embedding(Base):
    __tablename__ = 'embeddings'

    id = Column(Integer, primary_key=True)
    embedding = Column(ARRAY(Float), nullable=False)
    content_type = Column(Enum(ContentType), nullable=False)
    email_id = Column(Integer, ForeignKey('emails.id', ondelete='CASCADE'), nullable=True)
    file_id = Column(Integer, ForeignKey('files.id', ondelete='CASCADE'), nullable=True)
    link_id = Column(Integer, ForeignKey('links.id', ondelete='CASCADE'), nullable=True)
    email = relationship("Email", back_populates="embedding")
    file = relationship("File", back_populates="embedding")
    link = relationship("Link", back_populates="embedding")
