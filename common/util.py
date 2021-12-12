import yaml

def load_conf_file(config_file):
   with open(config_file, "r") as f:
       config = yaml.safe_load(f)
       logging_conf = config[0]["logging"]
       server_conf = config[1]["server"]
       exec_conf = config[2]["execution"]
   return logging_conf, server_conf, exec_conf