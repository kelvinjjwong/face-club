import time
import math
import os
import logging
from logging.config import fileConfig
from datetime import datetime

from application.AppConfig import AppConfig


class FaceClub:
    config = None
    app_start_time = None
    app_start_date = None

    def __init__(self, config_file):
        self.app_start_time = time.time()
        self.app_start_date = str(datetime.now())
        self.config = AppConfig(config_file)
        logpath = self.config.logging("path")
        os.makedirs(logpath, exist_ok=True)
        logging.config.fileConfig('logging.conf')

    def health(self):
        execution_time = self.time_since(self.app_start_time)
        current_time = str(datetime.now())
        return {'isAvailable': True,
                'startTime': self.app_start_date,
                'currentTime': current_time,
                'executionTime': execution_time
                }

    def time_since(*arg):
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
