from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .tables import Base, Email, File, Link, Embedding  # Add Embedding to the import
import os
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Float
from sqlalchemy import text

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        # PostgreSQL connection string
        db_url = f"postgresql://jeff_user:jeff_password@localhost:5434/jeff_db"
        self.engine = create_engine(db_url, future=True)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = self.SessionLocal()

        # Create pgvector extension if available
        try:
            with self.engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()
        except Exception as e:
            print(f"Warning: Unable to create vector extension. Error: {e}")
            print("Continuing without vector support. Some functionality may be limited.")

    def get_session(self) -> Session:
        return self.session

    def create(self, table_name: str, data: dict):
        model = self._get_model(table_name)
        db_object = model(**data)
        self.session.add(db_object)
        self.session.commit()
        self.session.refresh(db_object)
        return db_object

    def read(self, table_name: str, id: int):
        model = self._get_model(table_name)
        return self.session.query(model).filter(model.id == id).first()

    def update(self, table_name: str, id: int, data: dict):
        model = self._get_model(table_name)
        db_object = self.session.query(model).filter(model.id == id).first()
        for key, value in data.items():
            setattr(db_object, key, value)
        self.session.commit()
        self.session.refresh(db_object)
        return db_object

    def delete(self, table_name: str, id: int):
        model = self._get_model(table_name)
        db_object = self.session.query(model).filter(model.id == id).first()
        self.session.delete(db_object)
        self.session.commit()
        return db_object

    def _get_model(self, table_name: str):
        models = {
            'emails': Email,
            'files': File,
            'links': Link,
            'embeddings': Embedding  # Add this line
        }
        model = models.get(table_name)
        if model is None:
            raise ValueError(f"Unknown table name: {table_name}")
        return model

    def clear_all_tables(self):
        # First, delete all embeddings
        self.session.query(Embedding).delete()
        
        # Then delete emails, files, and links
        self.session.query(Email).delete()
        self.session.query(File).delete()
        self.session.query(Link).delete()
        
        self.session.commit()

    def reset_tables(self):
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
