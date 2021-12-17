import yaml
import time
import math


def config_load(config_file):
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
        logging_conf = config[0]["logging"]
        server_conf = config[1]["server"]
        exec_conf = config[2]["execution"]
    return logging_conf, server_conf, exec_conf


def time_cost(*arg):
    if len(arg) != 0:
        elapsed_time = time.time() - arg[0]
        hours = math.floor(elapsed_time / (60 * 60))
        elapsed_time = elapsed_time - hours * (60 * 60)
        minutes = math.floor(elapsed_time / 60)
        elapsed_time = elapsed_time - minutes * (60)
        seconds = math.floor(elapsed_time)
        elapsed_time = elapsed_time - seconds
        ms = elapsed_time * 1000
        if hours != 0:
            return "%d hours %d minutes %d seconds" % (hours, minutes, seconds)
        elif minutes != 0:
            return "%d minutes %d seconds" % (minutes, seconds)
        else:
            return "%d seconds %f ms" % (seconds, ms)
    else:
        return str(time.time())
