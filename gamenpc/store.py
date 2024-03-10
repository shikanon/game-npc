from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MySQLDatabase:
    def __init__(self, host:str, port:str, user:str, password:str, database:str):
        new_password = quote_plus(password)
        config = f"mysql+pymysql://{user}:{new_password}@{host}:{port}/{database}"
        self.engine = create_engine(config)        
        self.session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def get_engine(self): 
        return self.engine

    def insert_record(self, record):
        session = self.session()
        session.add(record)
        session.commit()

    def delete_record(self, record):
        session = self.session()
        session.delete(record)
        session.commit()

    def update_record(self, record):
        session = self.session()
        session.merge(record)
        session.commit()

    def select_records(self, record_class):
        session = self.session()
        result = session.query(record_class).all()
        return result  