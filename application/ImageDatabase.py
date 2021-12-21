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

    async def unrecognizedImages(self, amount):
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
