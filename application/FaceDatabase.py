from sqlalchemy import Table, Column, Integer, String, Text, Boolean, MetaData, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.sql import select


class FaceDatabase:
    engine = None
    faces = None

    def __init__(self, url):
        self.engine = create_engine(url)

    def initSchema(self):
        metadata = MetaData()
        self.faces = Table('faces', metadata,
                           Column('faceId', String(50), primary_key=True),
                           Column('imageId', String(50)),
                           Column("sourcePath", Text),
                           Column("peopleId", String(100)),
                           Column("peopleIdAssign", String(100)),
                           Column("imageYear", Integer),
                           Column("sample", Boolean),
                           )
        metadata.create_all(self.engine)

    def dropSchema(self):
        conn = self.engine.connect()
        conn.execute("""
        DROP TABLE faces
        """)

    def insert_face(self, face):
        conn = self.engine.connect()
        conn.execute(self.faces.insert(), face)

    def update_face(self, face):
        conn = self.engine.connect()
        conn.execute(self.faces.update(), face)

    def delete_face(self, face):
        conn = self.engine.connect()
        conn.execute(self.faces.delete(), face)

    def get_face(self, faceId):
        conn = self.engine.connect()
        s = select(self.faces).where(self.faces.c.faceId == faceId)
        result = conn.execute(s)
        row = result.fetchone()
        face = {
            'faceId': faceId,
            'imageId': row["imageId"],
            'sourcePath': row["sourcePath"],
            'peopleId': row["peopleId"],
            'peopleIdAssign': row["peopleIdAssign"],
            'imageYear': row["imageYear"],
            'sample': row["sample"]
        }

        result.close()
        return face

    def get_faces(self, limit=100, offset=0):
        faces = []
        conn = self.engine.connect()
        result = conn.execute("""
        SELECT * FROM faces 
        ORDER BY imageYear ASC, sourcePath ASC 
        LIMIT %s OFFSET %s
        """ % (limit, offset))
        for faceId, imageId, sourcePath, peopleId, peopleIdAssign, imageYear, sample in result:
            face = {
                'faceId': faceId,
                'imageId': imageId,
                'sourcePath': sourcePath,
                'peopleId': peopleId,
                'peopleIdAssign': peopleIdAssign,
                'imageYear': imageYear,
                'sample': sample
            }
            faces.insert(face)
        return faces
