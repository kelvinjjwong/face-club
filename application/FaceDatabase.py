from sqlalchemy import Table, Column, Integer, String, Text, Boolean, MetaData, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.sql import select
import logging

class FaceDatabase:
    logger = None
    engine = None
    faces = None
    metadata = None

    def __init__(self, url):
        self.logger = logging.getLogger('DB')
        self.engine = create_engine(url)
        self.metadata = MetaData()
        self.faces = Table('faces', self.metadata,
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

    def initSchema(self):
        self.metadata.create_all(self.engine)
        self.logger.info("created face db schema")

    def dropSchema(self):
        conn = self.engine.connect()
        conn.execute("""
        DROP TABLE IF EXISTS faces
        """)
        self.logger.info("Dropped face db schema")


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
        self.logger.info("inserting face record %s" % face)
        conn = self.engine.connect()
        conn.execute(self.faces.insert(), face)

    def delete_face(self, face):
        self.logger.info("deleting face record %s" % face)
        conn = self.engine.connect()
        conn.execute(self.faces.delete(), face)

    def get_face(self, faceId, conn=None):
        self.logger.info("getting face record %s" % faceId)
        if conn is None:
            conn = self.engine.connect()
        s = select(self.faces).where(self.faces.c.faceId == faceId)
        print(s.compile(compile_kwargs={"literal_binds": True}))
        result = conn.execute(s)
        row = result.fetchone()
        if row is not None:
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
            self.logger.info(face)
            result.close()
            return face
        else:
            self.logger.error("face record not found: %s" % faceId)
            return None

    def delete_all_faces(self):
        self.logger.info("deleting all faces from face db")
        conn = self.engine.connect()
        conn.execute("DELETE FROM faces")

    def get_faces(self, limit=100, offset=0):
        self.logger.info("getting face records with limit=%s offset=%s" % (limit, offset))
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
        self.logger.info("got %s face records" % len(faces))
        return faces

    def toggle_sample(self, faceId):
        conn = self.engine.connect()
        face = self.get_face(faceId, conn=conn)
        if face is not None:
            u = self.faces.update().where(self.faces.c.faceId == faceId).values(sample=(not face['sample']))
            print(u.compile(compile_kwargs={"literal_binds": True}))
            conn.execute(u)
            self.logger.info("updated face with faceId=%s sample=%s" % (faceId, face['sample']))
        else:
            self.logger.error("face record not found: %s" % faceId)

    def toggle_scan_result(self, faceId):
        conn = self.engine.connect()
        face = self.get_face(faceId, conn=conn)
        if face is not None:
            u = self.faces.update().where(self.faces.c.faceId == faceId).values(scanWrong=(not face['scanWrong']))
            print(u.compile(compile_kwargs={"literal_binds": True}))
            conn.execute(u)
            self.logger.info("updated face with faceId=%s scanWrong=%s" % (faceId, face['scanWrong']))
        else:
            self.logger.error("face record not found: %s" % faceId)
