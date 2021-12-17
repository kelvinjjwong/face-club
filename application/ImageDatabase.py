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

    async def unrecognizedFaces(self):
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
OFFSET 0 LIMIT 100
) t
)
AND locked='f' AND ("peopleId" = 'Unknown' or "peopleId" is NULL)
order by "imageYear" asc, "imageMonth" asc, "imageDay" asc, "imageId" asc, filename asc
            """
        )
        self.logger.info("Got %i records" % len(values))
        for value in values:
            path = ("%s%s/%s" % (value["cropPath"], value["subPath"], value["filename"]))
            self.logger.info(path)
        await conn.close()
