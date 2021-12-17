import os
import sys
import yaml
import logging
from logging.config import fileConfig


class AppConfig:
    logger = None

    config_file = ""
    database_config_file = ""

    logging_conf = {}
    database_conf = {}
    server_conf = {}
    execution_conf = {}

    def __init__(self, config_file):
        self.config_file = config_file
        self.load()
        logpath = self.logging("path")
        os.makedirs(logpath, exist_ok=True)
        logging.config.fileConfig('conf/logging.conf')
        self.logger = logging.getLogger('Config')
        self.printAllEnvVar()
        self.ensureEnvVar("FACECLUB_DATABASE_CONFIG")
        self.load_database_config(os.environ["FACECLUB_DATABASE_CONFIG"])

    def load(self):
        with open(self.config_file, "r") as f:
            config = yaml.safe_load(f)
            self.logging_conf = config["logging"]
            self.server_conf = config["server"]
            self.execution_conf = config["execution"]

    def load_database_config(self, database_config_file):
        """
        Load configuration from an external YAML file. The file should contain following fields:

        - host: str
        - port: int
        - username: str
        - password: str
        - database: str
        - schema: str

        :param database_config_file: path of an external YAML file
        """
        self.logger.info("Loading database config from yaml file - %s" % database_config_file)
        self.database_config_file = str(database_config_file).replace("~", os.environ["HOME"])
        with open(self.database_config_file, "r") as f:
            config = yaml.safe_load(f)
            self.database_conf = config

    def printAllEnvVar(self):
        for item, value in sorted(os.environ.items()):
            self.logger.info("Env_Var: %s - Value: %s" % (item, value))

    def ensureEnvVar(self, key):
        if os.environ.get(key, "") == "":
            self.logger.error("System environment variable %s is not set" % key)
            sys.exit(1)

    def logging(self, field):
        return self.logging_conf[field]

    def server(self, field):
        return self.server_conf[field]

    def execution(self, field):
        return self.execution_conf[field]

    def database(self, field):
        return self.database_conf[field]
