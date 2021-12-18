from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class Face(Base):
    __tablename__ = 'faces'
    faceId = Column(String(50), primary_key=True)
    imageId = Column(String(50))
    sourcePath = Column(String(1000))
    peopleId = Column(String(100))
    peopleIdAssign = Column(String(100))
    imageYear = Integer
    sample = Integer

    def __repr__(self):
        return """
        <Face(id='%s', faceId='%s', imageId='%s', 
              peopleId='%s', peopleIdAssign='%s', 
              imageYear='%s', sample='%s', 
              sourcePath='%s')>
        """ % (
            self.id, self.faceId, self.imageId,
            self.peopleId, self.peopleIdAssign,
            self.imageYear, self.sample,
            self.sourcePath)
