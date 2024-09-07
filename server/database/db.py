from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .tables import Base, Email, File, Link
import os

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        # Get the current directory of this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to the server directory
        server_dir = os.path.dirname(current_dir)
        # Construct the path to db.sqlite
        db_path = os.path.join(server_dir, 'db.sqlite')
        # Create the SQLite engine with the correct path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=True)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = self.SessionLocal()

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
        if table_name == 'emails':
            return Email
        elif table_name == 'files':
            return File
        elif table_name == 'links':
            return Link
        else:
            raise ValueError(f"Unknown table name: {table_name}")
          
    def clear_all_tables(self):
        self.session.query(Email).delete()
        self.session.query(File).delete()
        self.session.query(Link).delete()
        self.session.commit()
