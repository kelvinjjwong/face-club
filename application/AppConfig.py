import os
from os.path import exists
import sys
import yaml
import logging
from logging.config import fileConfig


class AppConfig:
    logger = None

    config_file = ""
    external_database_config_file = ""
    external_database_enable = False
    external_database_fetch_amount = 1
    internal_database_url = ""
    internal_database_display_amount = 10

    logging_conf = {}
    database_conf = {}
    workspace_conf = {}

    def __init__(self, config_file):
        self.config_file = config_file
        self.load()
        os.makedirs(self.logging("path"), exist_ok=True)
        os.makedirs("db", exist_ok=True)
        logging.config.fileConfig('conf/logging.conf')
        self.logger = logging.getLogger('Config')
        self.logAllEnvVar()
        self.ensureFileExist("database.external.config", self.external_database_config_file)
        self.logger.info("internal db url:            %s" % self.internal_database_url)
        self.logger.info("internal db display amount: %s" % self.internal_database_display_amount)
        self.logger.info("external db config:         %s" % self.external_database_config_file)
        self.logger.info("external db enabled:        %s" % self.external_database_enable)
        self.logger.info("external db fetch amount:   %s" % self.external_database_fetch_amount)
        self.logger.info("workspace dataset folder:   %s" % self.workspace("dataset"))
        self.logger.info("workspace images  folder:   %s" % self.workspace("images"))
        self.logger.info("workspace model   folder:   %s" % self.workspace("model"))
        os.makedirs(self.workspace("dataset"), exist_ok=True)
        os.makedirs(self.workspace("model"), exist_ok=True)
        os.makedirs(self.workspace("images"), exist_ok=True)
        self.load_external_database_config()

    def load(self):
        with open(self.config_file, "r") as f:
            config = yaml.safe_load(f)
            self.logging_conf = self.realpath(config["logging"])
            self.workspace_conf = self.realpath(config["workspace"])
            self.external_database_config_file = self.realpath(config["database"]["external"]["config"])
            self.external_database_enable = config["database"]["external"]["enable"]
            self.external_database_fetch_amount = config["database"]["external"]["fetch-amount"]
            self.internal_database_url = self.realpath(config["database"]["internal"]["url"])
            self.internal_database_display_amount = config["database"]["internal"]["display-amount"]

    def realpath(self, obj):
        if isinstance(obj, dict):
            for field, val in obj.items():
                obj[field] = self.realpath(val)
            return obj
        else:
            return str(obj).replace("~", os.environ["HOME"])

    def load_external_database_config(self):
        """
        Load configuration from an external YAML file. The file should contain following fields:

        - host: str
        - port: int
        - username: str
        - password: str
        - database: str
        - schema: str
        """
        self.logger.info("Loading database config from yaml file - %s" % self.external_database_config_file)
        with open(self.external_database_config_file, "r") as f:
            config = yaml.safe_load(f)
            self.database_conf = config

    def logAllEnvVar(self):
        for item, value in sorted(os.environ.items()):
            self.logger.info("Env_Var: %s - Value: %s" % (item, value))

    def ensureEnvVar(self, key):
        if os.environ.get(key, "") == "":
            self.logger.error("System environment variable %s is not set" % key)
            sys.exit(1)

    def ensureFileExist(self, name, filepath):
        if not exists(filepath):
            self.logger.error("Config item [%s] file does not exist - %s" % (name, filepath))
            sys.exit(1)

    def logging(self, field):
        return self.logging_conf[field]

    def database(self, field):
        return self.database_conf[field]

    def workspace(self, field):
        return self.workspace_conf[field]
