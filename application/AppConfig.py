import yaml


class AppConfig:
    config_file = ""

    logging_conf = {}
    server_conf = {}
    execution_conf = {}

    def __init__(self, config_file):
        self.config_file = config_file
        self.load()

    def load(self):
        with open(self.config_file, "r") as f:
            config = yaml.safe_load(f)
            self.logging_conf = config[0]["logging"]
            self.server_conf = config[1]["server"]
            self.execution_conf = config[2]["execution"]

    def logging(self, field):
        return self.logging_conf[field]

    def server(self, field):
        return self.server_conf[field]

    def execution(self, field):
        return self.execution_conf[field]
