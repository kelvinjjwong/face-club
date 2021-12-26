import asyncpg
import logging


class ImageDatabase:
    logger = None

    username = None
    password = None
    host = None
    port = 0
    database = None
    schema = None

    def __init__(self, database_conf):
        self.logger = logging.getLogger('DB')
        self.username = database_conf["username"]
        self.host = database_conf["host"]
        self.database = database_conf["database"]
        self.port = database_conf["port"] if hasattr(database_conf, "port") else 5432
        self.schema = database_conf["schema"] if hasattr(database_conf, "schema") else ""
        self.password = database_conf["password"] if hasattr(database_conf, "password") else ""
        pass

    async def families(self):
        conn = await asyncpg.connect(user=self.username,
                                     password=self.password,
                                     database=self.database,
                                     host=self.host)
        values = await conn.fetch(
            'SELECT * FROM "Family"'
        )
        self.logger.info("Got %i records" % len(values))
        for value in values:
            self.logger.info(value)
            self.logger.info(value["name"])
        await conn.close()

    async def unrecognizedImages(self, amount, reviewed: bool = None):  # TODO add sql condition for 'reviewed'
        conn = await asyncpg.connect(user=self.username,
                                     password=self.password,
                                     database=self.database,
                                     host=self.host)
        values = await conn.fetch(
            """
SELECT "id","path","photoTakenYear","photoTakenMonth","photoTakenDay" from "Image" where "id" in 
(select t."id" from
(select "id","path","photoTakenYear","photoTakenMonth","photoTakenDay"
from "Image"
where "hiddenByContainer" = 'f' and "hiddenByRepository" = 'f'
order by "photoTakenYear" DESC, "photoTakenMonth" DESC, "photoTakenDay" DESC
OFFSET 0 LIMIT %s
) t)
order by "photoTakenYear","photoTakenMonth","photoTakenDay"
            """ % amount
        )
        self.logger.info("got %i unrecognized Image db records" % len(values))
        await conn.close()
        return values

    async def unrecognizedFaces(self, amount):
        conn = await asyncpg.connect(user=self.username,
                                     password=self.password,
                                     database=self.database,
                                     host=self.host)
        values = await conn.fetch(
            """
SELECT * from "ImageFace"
where "imageId" in (
SELECT t."imageId" from (
SELECT DISTINCT "imageId","imageYear","imageMonth","imageDay" from "ImageFace"
ORDER BY "imageYear" ASC, "imageMonth" ASC, "imageDay" ASC
OFFSET 0 LIMIT %i
) t
)
AND locked='f' AND ("peopleId" = 'Unknown' or "peopleId" is NULL)
order by "imageYear" asc, "imageMonth" asc, "imageDay" asc, "imageId" asc, filename asc
            """ % amount
        )
        self.logger.info("got %i unrecognized ImageFace db records" % len(values))
        await conn.close()
        return values

    async def updateFace(self, id, peopleId):
        self.logger.info("updating ImageFace db record with id=%s peopleId=%s" % (id, peopleId))
        conn = await asyncpg.connect(user=self.username,
                                     password=self.password,
                                     database=self.database,
                                     host=self.host)
        await conn.execute(
            """
            UPDATE "ImageFace"
            SET "peopleId" = $1 
            WHERE "id" = $2
            """, peopleId, id
        )
        await conn.close()

    async def get_people(self):
        conn = await asyncpg.connect(user=self.username,
                                     password=self.password,
                                     database=self.database,
                                     host=self.host)
        values = await conn.fetch(
            """
SELECT * from "People"
            """
        )
        self.logger.info("got %i people db records" % len(values))
        await conn.close()
        return values

    async def get_person(self, peopleId: str):
        conn = await asyncpg.connect(user=self.username,
                                     password=self.password,
                                     database=self.database,
                                     host=self.host)
        values = await conn.fetch(
            """
SELECT * from "People" where "id" = $1
            """, peopleId
        )
        self.logger.info("got %i person db record" % len(values))
        await conn.close()
        if len(values) > 0:
            person = values[0]
            return {
                'peopleId': person["id"],
                'personName': person["name"],
                'shortName': person["shortName"]
            }
        else:
            return None

    async def create_person(self, peopleId: str, personName: str, shortName: str):
            conn = await asyncpg.connect(user=self.username,
                                         password=self.password,
                                         database=self.database,
                                         host=self.host)
            values = await conn.fetch(
                """
    INSERT INTO "People" ("id", "name", "shortName") VALUES ($1, $2, $3)
                """, peopleId, personName, shortName
            )
            self.logger.info("Created 1 person %s" % peopleId)


