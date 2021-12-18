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
                           Column("fileExt", String(10)),
                           Column("peopleId", String(100)),
                           Column("peopleIdAssign", String(100)),
                           Column("imageYear", Integer),
                           Column("sample", Boolean),
                           Column("scanned", Boolean),
                           Column("scanWrong", Boolean)
                           )
        metadata.create_all(self.engine)

    def dropSchema(self):
        conn = self.engine.connect()
        conn.execute("""
        DROP TABLE IF EXISTS faces
        """)

    def empty_face(self):
        return {
            'faceId': '',
            'imageId': '',
            'sourcePath': '',
            'fileExt': '',
            'peopleId': 'Unknown',
            'peopleIdAssign': 'Unknown',
            'imageYear': 0,
            'sample': False,
            'scanned': False,
            'scanWrong': False
        }

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
            'fileExt': row["fileExt"],
            'peopleId': row["peopleId"],
            'peopleIdAssign': row["peopleIdAssign"],
            'imageYear': row["imageYear"],
            'sample': row["sample"],
            'scanned': row["scanned"],
            'scanWrong': row["scanWrong"]
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
        for faceId, imageId, sourcePath, fileExt, peopleId, peopleIdAssign, imageYear, sample, scanned, scanWrong in result:
            face = {
                'faceId': faceId,
                'imageId': imageId,
                'sourcePath': sourcePath,
                'fileExt': fileExt,
                'peopleId': peopleId,
                'peopleIdAssign': peopleIdAssign,
                'imageYear': imageYear,
                'sample': False if sample == 0 else True,
                'scanned': False if scanned == 0 else True,
                'scanWrong': False if scanWrong == 0 else True
            }
            faces.append(face)
        return faces
