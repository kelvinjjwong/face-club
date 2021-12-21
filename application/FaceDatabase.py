from sqlalchemy import Table, Column, Integer, String, Text, Boolean, MetaData, ForeignKey, and_
from sqlalchemy import create_engine
from sqlalchemy.sql import select
import logging


class FaceDatabase:
    logger = None
    engine = None
    faces = None
    positions = None
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
        self.positions = Table('positions', self.metadata,
                               Column("imageId", String(50)),
                               Column("pos_top", String(50)),
                               Column("pos_right", String(50)),
                               Column("pos_bottom", String(50)),
                               Column("pos_left", String(50)),
                               Column("peopleIdRecognized", String(50)),
                               Column("peopleIdAssign", String(50)),
                               Column("peopleId", String(50)),
                               Column("peopleName", String(50))
                               )

    def initSchema(self):
        self.metadata.create_all(self.engine)
        self.logger.info("created face db schema")

    def dropSchema(self):
        conn = self.engine.connect()
        conn.execute("""
        DROP TABLE IF EXISTS faces
        """)
        conn.execute("""
        DROP TABLE IF EXISTS positions
        """)
        self.logger.info("Dropped face db schema")

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
                'localFilePath': localFilePath,
                'taggedFilePath': taggedFilePath,
                'peopleId': peopleId,
                'peopleIdRecognized': peopleIdRecognized,
                'peopleIdAssign': peopleIdAssign,
                'scanned': False if scanned == 0 else True,
                'scanWrong': False if scanWrong == 0 else True,
                'sample': False if sample == 0 else True,
                'sourcePath': sourcePath,
                'imageId': imageId,
                'fileExt': fileExt,
                'imageYear': imageYear
            }
            faces.append(face)
        self.logger.info("got %s face records" % len(faces))
        return faces

    def get_scanned_faces(self, limit=100, offset=0):
        self.logger.info("getting image records with limit=%s offset=%s" % (limit, offset))
        faces = []
        conn = self.engine.connect()
        result = conn.execute("""
        SELECT * FROM faces WHERE scanned=1 AND taggedFilePath <> ''
        ORDER BY imageYear ASC, sourcePath ASC 
        LIMIT %s OFFSET %s
        """ % (limit, offset))
        for imageId, sourcePath, localFilePath, taggedFilePath, fileExt, peopleId, peopleIdRecognized, peopleIdAssign, imageYear, sample, scanned, scanWrong in result:
            face = {
                'localFilePath': localFilePath,
                'taggedFilePath': taggedFilePath,
                'peopleId': peopleId,
                'peopleIdRecognized': peopleIdRecognized,
                'peopleIdAssign': peopleIdAssign,
                'scanned': False if scanned == 0 else True,
                'scanWrong': False if scanWrong == 0 else True,
                'sample': False if sample == 0 else True,
                'sourcePath': sourcePath,
                'imageId': imageId,
                'fileExt': fileExt,
                'imageYear': imageYear
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
            u = self.faces.update() \
                .where(self.faces.c.imageId == imageId) \
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

    def get_position(self, imageId: str, top: int, right: int, bottom: int, left: int, conn=None):
        self.logger.info("getting position record: imageId=%s top=%s right=%s bottom=%s left=%s"
                         % (imageId, top, right, bottom, left))
        if conn is None:
            conn = self.engine.connect()
        s = select(self.positions).where(
            and_(
                self.positions.c.imageId == imageId,
                self.positions.c.pos_top == top,
                self.positions.c.pos_right == right,
                self.positions.c.pos_bottom == bottom,
                self.positions.c.pos_left == left
            )
        )
        print(s.compile(compile_kwargs={"literal_binds": True}))
        result = conn.execute(s)
        row = result.fetchone()
        if row is not None:
            position = {
                'imageId': row["imageId"],
                'pos_top': row["pos_top"],
                'pos_right': row["pos_right"],
                'pos_bottom': row["pos_bottom"],
                'pos_left': row["pos_left"],
                'peopleIdRecognized': row["peopleIdRecognized"],
                'peopleIdAssign': row["peopleIdAssign"],
                'peopleId': row["peopleId"],
                'peopleName': row["peopleName"]
            }
            self.logger.info(position)
            result.close()
            return position
        else:
            self.logger.error("position record not found: imageId=%s top=%s right=%s bottom=%s left=%s"
                              % (imageId, top, right, bottom, left))
            return None

    def insert_position(self, position):
        self.logger.info("inserting position record %s" % position)
        conn = self.engine.connect()
        conn.execute(self.positions.insert(), position)

    def update_position(self, imageId: str, top: int, right: int, bottom: int, left: int,
                        peopleIdRecognized: str, peopleIdAssign: str):
        peopleId = ''
        if peopleIdAssign != '':
            peopleId = peopleIdAssign
        elif peopleIdRecognized != '':
            peopleId = peopleIdRecognized

        # TODO map name to peopleId
        peopleName = ''

        conn = self.engine.connect()
        position = self.get_position(imageId, top, right, bottom, left, conn=conn)
        if position is not None:
            conn.execute("""
            UPDATE positions SET peopleIdRecognized=$1, peopleIdAssign=$2, peopleId=$3, peopleName=$4
            WHERE imageId=$5 AND pos_top=$6 AND pos_right=$7 AND pos_bottom=$8 AND pos_left=$9
                    """, peopleIdRecognized, peopleIdAssign, peopleId, peopleName, imageId, top, right, bottom, left)
            self.logger.info("updated position with imageId=%s top=%s right=%s bottom=%s left=%s"
                             % (imageId, top, right, bottom, left))
        else:
            self.insert_position({
                'imageId': imageId,
                'pos_top': top,
                'pos_right': right,
                'pos_bottom': bottom,
                'pos_left': left,
                'peopleIdRecognized': peopleIdRecognized,
                'peopleIdAssign': peopleIdAssign,
                'peopleId': peopleId,
                'peopleName': peopleName
            })
