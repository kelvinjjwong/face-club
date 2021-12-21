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
                           Column('imageId', String(50), primary_key=True),
                           Column("sourcePath", Text),
                           Column("localFilePath", Text),
                           Column("taggedFilePath", Text),
                           Column("fileExt", String(10)),
                           Column("peopleId", Text),
                           Column("peopleIdRecognized", Text),
                           Column("peopleIdAssign", Text),
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
            'imageId': '',
            'sourcePath': '',
            'localFilePath': '',
            'taggedFilePath': '',
            'fileExt': '',
            'peopleId': 'Unknown',
            'peopleIdRecognized': 'Unknown',
            'peopleIdAssign': 'Unknown',
            'imageYear': 0,
            'sample': False,
            'scanned': False,
            'scanWrong': False
        }

    def insert_face(self, face):
        self.logger.info("inserting image record %s" % face)
        conn = self.engine.connect()
        conn.execute(self.faces.insert(), face)

    def delete_face(self, face):
        self.logger.info("deleting image record %s" % face)
        conn = self.engine.connect()
        conn.execute(self.faces.delete(), face)

    def get_face(self, imageId, conn=None):
        self.logger.info("getting image record %s" % imageId)
        if conn is None:
            conn = self.engine.connect()
        s = select(self.faces).where(self.faces.c.imageId == imageId)
        print(s.compile(compile_kwargs={"literal_binds": True}))
        result = conn.execute(s)
        row = result.fetchone()
        if row is not None:
            face = {
                'imageId': row["imageId"],
                'sourcePath': row["sourcePath"],
                'localFilePath': row["localFilePath"],
                'taggedFilePath': row["taggedFilePath"],
                'fileExt': row["fileExt"],
                'peopleId': row["peopleId"],
                'peopleIdRecognized': row["peopleIdRecognized"],
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
            self.logger.error("face record not found: %s" % imageId)
            return None

    def delete_all_faces(self):
        self.logger.info("deleting all images from face db")
        conn = self.engine.connect()
        conn.execute("DELETE FROM faces")

    def get_faces(self, limit=100, offset=0):
        self.logger.info("getting image records with limit=%s offset=%s" % (limit, offset))
        faces = []
        conn = self.engine.connect()
        result = conn.execute("""
        SELECT * FROM faces 
        ORDER BY imageYear ASC, sourcePath ASC 
        LIMIT %s OFFSET %s
        """ % (limit, offset))
        for imageId, sourcePath, localFilePath, taggedFilePath, fileExt, peopleId, peopleIdRecognized, peopleIdAssign, imageYear, sample, scanned, scanWrong in result:
            face = {
                'imageId': imageId,
                'sourcePath': sourcePath,
                'localFilePath': localFilePath,
                'taggedFilePath': taggedFilePath,
                'fileExt': fileExt,
                'peopleId': peopleId,
                'peopleIdRecognized': peopleIdRecognized,
                'peopleIdAssign': peopleIdAssign,
                'imageYear': imageYear,
                'sample': False if sample == 0 else True,
                'scanned': False if scanned == 0 else True,
                'scanWrong': False if scanWrong == 0 else True
            }
            faces.append(face)
        self.logger.info("got %s face records" % len(faces))
        return faces

    def toggle_sample(self, imageId):
        conn = self.engine.connect()
        face = self.get_face(imageId, conn=conn)
        if face is not None:
            u = self.faces.update().where(self.faces.c.imageId == imageId).values(sample=(not face['sample']))
            print(u.compile(compile_kwargs={"literal_binds": True}))
            conn.execute(u)
            self.logger.info("updated image with imageId=%s sample=%s" % (imageId, face['sample']))
        else:
            self.logger.error("image record not found: %s" % imageId)

    def toggle_scan_result(self, imageId):
        conn = self.engine.connect()
        face = self.get_face(imageId, conn=conn)
        if face is not None:
            u = self.faces.update().where(self.faces.c.imageId == imageId).values(scanWrong=(not face['scanWrong']))
            print(u.compile(compile_kwargs={"literal_binds": True}))
            conn.execute(u)
            self.logger.info("updated image with imageId=%s scanWrong=%s" % (imageId, face['scanWrong']))
        else:
            self.logger.error("image record not found: %s" % imageId)

    def update_face(self, imageId, localFilePath, taggedFilePath, peopleIdRecognized):
        conn = self.engine.connect()
        face = self.get_face(imageId, conn=conn)
        if face is not None:
            u = self.faces.update()\
                .where(self.faces.c.imageId == imageId)\
                .values(
                    localFilePath=localFilePath,
                    taggedFilePath=taggedFilePath,
                    peopleIdRecognized=peopleIdRecognized,
                    scanned=1
                )
            print(u.compile(compile_kwargs={"literal_binds": True}))
            conn.execute(u)
            self.logger.info("updated image with imageId=%s" % imageId)
        else:
            self.logger.error("image record not found: %s" % imageId)

    def assign_face(self, imageId, peopleIdAssign):
        conn = self.engine.connect()
        face = self.get_face(imageId, conn=conn)
        if face is not None:
            u = self.faces.update() \
                .where(self.faces.c.imageId == imageId) \
                .values(
                    peopleIdAssign=peopleIdAssign
                )
            print(u.compile(compile_kwargs={"literal_binds": True}))
            conn.execute(u)
            self.logger.info("updated image with imageId=%s scanWrong=%s" % (imageId, face['scanWrong']))
        else:
            self.logger.error("image record not found: %s" % imageId)

