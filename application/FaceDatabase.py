from sqlalchemy import Table, Column, Integer, String, Text, Boolean, MetaData, ForeignKey, and_
from sqlalchemy import create_engine
from sqlalchemy.sql import select
import logging


class FaceDatabase:
    logger = None
    engine = None
    images = None
    faces = None
    metadata = None

    def __init__(self, url):
        self.logger = logging.getLogger('DB')
        self.engine = create_engine(url)
        self.metadata = MetaData()
        self.images = Table('images', self.metadata,
                            Column('imageId', String(50), primary_key=True),
                            Column("sourcePath", Text),
                            Column("localFilePath", Text),
                            Column("resizedFilePath", Text),
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
        self.faces = Table('faces', self.metadata,
                           Column("imageId", String(50)),
                           Column("pos_top", String(50)),
                           Column("pos_right", String(50)),
                           Column("pos_bottom", String(50)),
                           Column("pos_left", String(50)),
                           Column("peopleIdRecognized", String(50)),
                           Column("peopleIdAssign", String(50)),
                           Column("peopleId", String(50)),
                           Column("peopleName", String(50)),
                           Column("shortName", String(50))
                           )

    def initSchema(self):
        self.metadata.create_all(self.engine)
        self.logger.info("created face db schema")

    def dropSchema(self):
        conn = self.engine.connect()
        conn.execute("""
        DROP TABLE IF EXISTS images
        """)
        conn.execute("""
        DROP TABLE IF EXISTS faces
        """)
        self.logger.info("Dropped face db schema")

    def insert_image(self, face):
        self.logger.info("inserting image record %s" % face)
        conn = self.engine.connect()
        conn.execute(self.images.insert(), face)

    def delete_image(self, face):
        self.logger.info("deleting image record %s" % face)
        conn = self.engine.connect()
        conn.execute(self.images.delete(), face)

    def get_image(self, imageId, conn=None):
        self.logger.info("getting image record %s" % imageId)
        if conn is None:
            conn = self.engine.connect()
        s = select(self.images).where(self.images.c.imageId == imageId)
        print(s.compile(compile_kwargs={"literal_binds": True}))
        result = conn.execute(s)
        row = result.fetchone()
        if row is not None:
            image = {
                'imageId': row["imageId"],
                'sourcePath': row["sourcePath"],
                'localFilePath': row["localFilePath"],
                'resizedFilePath': row["resizedFilePath"],
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
            self.logger.info(image)
            result.close()
            return image
        else:
            self.logger.error("image record not found: %s" % imageId)
            return None

    def delete_all_images(self):
        self.logger.info("deleting all images from face db")
        conn = self.engine.connect()
        conn.execute("DELETE FROM images")

    def get_images(self, limit=100, offset=0):
        self.logger.info("getting image records with limit=%s offset=%s" % (limit, offset))
        images = []
        conn = self.engine.connect()
        result = conn.execute("""
        SELECT * FROM images 
        ORDER BY imageYear ASC, sourcePath ASC 
        LIMIT %s OFFSET %s
        """ % (limit, offset))
        for imageId, sourcePath, localFilePath, resizedFilePath, taggedFilePath, fileExt, peopleId, peopleIdRecognized, peopleIdAssign, imageYear, sample, scanned, scanWrong in result:
            image = {
                'localFilePath': localFilePath,
                'resizedFilePath': resizedFilePath,
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
            images.append(image)
        self.logger.info("got %s image records" % len(images))
        return images

    def get_scanned_faces(self, limit=100, offset=0):
        self.logger.info("getting image records with limit=%s offset=%s" % (limit, offset))
        images = []
        conn = self.engine.connect()
        result = conn.execute("""
        SELECT * FROM images WHERE scanned=1 AND taggedFilePath <> ''
        ORDER BY imageYear ASC, sourcePath ASC 
        LIMIT %s OFFSET %s
        """ % (limit, offset))
        for imageId, sourcePath, localFilePath, resizedFilePath, taggedFilePath, fileExt, peopleId, peopleIdRecognized, peopleIdAssign, imageYear, sample, scanned, scanWrong in result:
            image = {
                'localFilePath': localFilePath,
                'resizedFilePath': resizedFilePath,
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
            images.append(image)
        self.logger.info("got %s image records" % len(images))
        return images

    def toggle_sample(self, imageId):
        conn = self.engine.connect()
        face = self.get_image(imageId, conn=conn)
        if face is not None:
            u = self.images.update().where(self.images.c.imageId == imageId).values(sample=(not face['sample']))
            print(u.compile(compile_kwargs={"literal_binds": True}))
            conn.execute(u)
            self.logger.info("updated image with imageId=%s sample=%s" % (imageId, face['sample']))
        else:
            self.logger.error("image record not found: %s" % imageId)

    def toggle_scan_result(self, imageId):
        conn = self.engine.connect()
        face = self.get_image(imageId, conn=conn)
        if face is not None:
            u = self.images.update().where(self.images.c.imageId == imageId).values(scanWrong=(not face['scanWrong']))
            print(u.compile(compile_kwargs={"literal_binds": True}))
            conn.execute(u)
            self.logger.info("updated image with imageId=%s scanWrong=%s" % (imageId, face['scanWrong']))
        else:
            self.logger.error("image record not found: %s" % imageId)

    def recognize_face_in_image(self, imageId, localFilePath, resizedFilePath, taggedFilePath, peopleIdRecognized):
        conn = self.engine.connect()
        image = self.get_image(imageId, conn=conn)
        if image is not None:
            u = self.images.update() \
                .where(self.images.c.imageId == imageId) \
                .values(
                localFilePath=localFilePath,
                resizedFilePath=resizedFilePath,
                taggedFilePath=taggedFilePath,
                peopleId=self.determine_peopleId(peopleIdRecognized, image['peopleIdAssign']),
                peopleIdRecognized=peopleIdRecognized,
                scanned=1
            )
            print(u.compile(compile_kwargs={"literal_binds": True}))
            conn.execute(u)
            self.logger.info("updated image with imageId=%s" % imageId)
        else:
            self.logger.error("image record not found: %s" % imageId)

    def assign_face_to_image(self, imageId, peopleIdAssign):
        conn = self.engine.connect()
        image = self.get_image(imageId, conn=conn)
        if image is not None:
            u = self.images.update() \
                .where(self.images.c.imageId == imageId) \
                .values(
                peopleIdAssign=peopleIdAssign,
                peopleId=self.determine_peopleId(image['peopleIdRecognized'], peopleIdAssign)
            )
            print(u.compile(compile_kwargs={"literal_binds": True}))
            conn.execute(u)
            self.logger.info("updated image with imageId=%s scanWrong=%s" % (imageId, image['scanWrong']))
        else:
            self.logger.error("image record not found: %s" % imageId)

    def get_faces(self, imageId, conn=None):
        faces = []
        if conn is None:
            conn = self.engine.connect()
        s = select(self.faces).where(self.faces.c.imageId == imageId)
        print(s.compile(compile_kwargs={"literal_binds": True}))
        result = conn.execute(s)
        for imageId, pos_top, pos_right, pos_bottom, pos_left, peopleIdRecognized, peopleIdAssign, peopleId, peopleName, shortName in result:
            face = {
                'imageId': imageId,
                'pos_top': pos_top,
                'pos_right': pos_right,
                'pos_bottom': pos_bottom,
                'pos_left': pos_left,
                'peopleIdRecognized': peopleIdRecognized,
                'peopleIdAssign': peopleIdAssign,
                'peopleId': peopleId,
                'peopleName': peopleName,
                'shortName': shortName
            }
            faces.append(face)
        return faces

    def get_face(self, imageId: str, top: int, right: int, bottom: int, left: int, conn=None):
        self.logger.info("getting face record: imageId=%s top=%s right=%s bottom=%s left=%s"
                         % (imageId, top, right, bottom, left))
        if conn is None:
            conn = self.engine.connect()
        s = select(self.faces).where(
            and_(
                self.faces.c.imageId == imageId,
                self.faces.c.pos_top == top,
                self.faces.c.pos_right == right,
                self.faces.c.pos_bottom == bottom,
                self.faces.c.pos_left == left
            )
        )
        print(s.compile(compile_kwargs={"literal_binds": True}))
        result = conn.execute(s)
        row = result.fetchone()
        if row is not None:
            face = {
                'imageId': row["imageId"],
                'pos_top': row["pos_top"],
                'pos_right': row["pos_right"],
                'pos_bottom': row["pos_bottom"],
                'pos_left': row["pos_left"],
                'peopleIdRecognized': row["peopleIdRecognized"],
                'peopleIdAssign': row["peopleIdAssign"],
                'peopleId': row["peopleId"],
                'peopleName': row["peopleName"],
                'shortName': row["shortName"]
            }
            self.logger.info(face)
            result.close()
            return face
        else:
            self.logger.info("face record not found: imageId=%s top=%s right=%s bottom=%s left=%s"
                              % (imageId, top, right, bottom, left))
            return None

    def insert_face(self, face):
        self.logger.info("inserting face record %s" % face)
        conn = self.engine.connect()
        conn.execute(self.faces.insert(), face)

    def determine_peopleId(self, peopleIdRecognized, peopleIdAssign):
        if peopleIdAssign != '(not_assigned)':
            return peopleIdAssign
        elif peopleIdRecognized != '(not_recognized)':
            return peopleIdRecognized
        else:
            return ''

    def recognize_face(self, imageId: str, top: int, right: int, bottom: int, left: int,
                       peopleIdRecognized: str, personName: str, shortName: str):

        conn = self.engine.connect()
        face = self.get_face(imageId, top, right, bottom, left, conn=conn)
        if face is not None:
            conn.execute("""
            UPDATE faces SET peopleId=$1, peopleIdRecognized=$2, peopleName=$3, shortName=$4
            WHERE imageId=$5 AND pos_top=$6 AND pos_right=$7 AND pos_bottom=$8 AND pos_left=$9
                    """, self.determine_peopleId(peopleIdRecognized, face["peopleIdAssign"]),
                         peopleIdRecognized, personName, shortName, imageId, top, right, bottom, left)
            self.logger.info("Recognized face with imageId=%s top=%s right=%s bottom=%s left=%s peopleIdRecognized=%s"
                             % (imageId, top, right, bottom, left, peopleIdRecognized))
        else:
            self.insert_face({
                'imageId': imageId,
                'pos_top': top,
                'pos_right': right,
                'pos_bottom': bottom,
                'pos_left': left,
                'peopleIdRecognized': peopleIdRecognized,
                'peopleIdAssign': '(not_assigned)',
                'peopleId': self.determine_peopleId(peopleIdRecognized, '(not_assigned)'),
                'peopleName': personName,
                'shortName': shortName
            })

    def assign_face(self, imageId: str, top: int, right: int, bottom: int, left: int,
                    peopleIdAssign: str, personName: str, shortName: str):

        conn = self.engine.connect()
        face = self.get_face(imageId, top, right, bottom, left, conn=conn)
        if face is not None:
            conn.execute("""
            UPDATE faces SET peopleId=$1, peopleIdAssign=$2, peopleName=$3, shortName=$4
            WHERE imageId=$5 AND pos_top=$6 AND pos_right=$7 AND pos_bottom=$8 AND pos_left=$9
                    """, self.determine_peopleId(face['peopleIdRecognized'], peopleIdAssign),
                         peopleIdAssign, personName, shortName, imageId, top, right, bottom, left)
            self.logger.info("Assigned face with imageId=%s top=%s right=%s bottom=%s left=%s peopleIdAssign=%s"
                             % (imageId, top, right, bottom, left, peopleIdAssign))
        else:
            self.insert_face({
                'imageId': imageId,
                'pos_top': top,
                'pos_right': right,
                'pos_bottom': bottom,
                'pos_left': left,
                'peopleIdRecognized': '',
                'peopleIdAssign': peopleIdAssign,
                'peopleId': self.determine_peopleId('', peopleIdAssign),
                'peopleName': personName,
                'shortName': shortName
            })

    def delete_faces(self, imageId: str):
        conn = self.engine.connect()
        conn.execute("""
                    DELETE FROM faces 
                    WHERE imageId=$1
                    """, imageId)

    def delete_face(self, imageId: str, top: int, right: int, bottom: int, left: int):
        conn = self.engine.connect()
        conn.execute("""
                    DELETE FROM faces 
                    WHERE imageId=$1 AND pos_top=$7 AND pos_right=$8 AND pos_bottom=$9 AND pos_left=$10
                    """, imageId, top, right, bottom, left)

    def update_faces(self, imageId: str, faces):
        self.delete_faces(imageId)
        for face in faces:
            self.insert_face(face)

