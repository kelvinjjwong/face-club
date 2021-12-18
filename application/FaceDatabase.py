from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()

class FaceDatabase:

    def __init__(self):
        pass

    def initSchema(self, url):
        engine = create_engine(url, echo=True)
        Base.metadata.create_all(engine, checkfirst=True)
