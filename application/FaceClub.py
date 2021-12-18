import time
import math
import logging
from datetime import datetime
import atexit
import sys
import signal

from application.AppConfig import AppConfig
from application.FaceDatabase import FaceDatabase
from application.ImageDatabase import ImageDatabase
from application.Schedule import Schedule


class FaceClub:
    logger = None

    config = None
    schedule = None
    imageDatabase = None
    faceDatabase = None

    app_start_time = None
    app_start_date = None

    isShuttingDown = False

    def __init__(self, config_file):
        self.app_start_time = time.time()
        self.app_start_date = str(datetime.now())
        self.config = AppConfig(config_file)
        self.logger = logging.getLogger('App')
        self.faceDatabase = FaceDatabase(self.config.internal_database_url)
        self.imageDatabase = ImageDatabase(self.config.database_conf)
        self.schedule = Schedule()
        self.schedule.start()
        signal.signal(signal.SIGINT, self.shutdown_signal_handler)
        atexit.register(self.shutdown_handler)
        self.logger.info("Application started.")

    def health(self):
        execution_time = self.time_since(self.app_start_time)
        current_time = str(datetime.now())
        return {'isAvailable': True,
                'startTime': self.app_start_date,
                'currentTime': current_time,
                'executionTime': execution_time
                }

    def shutdown_signal_handler(self, signum, frame):
        self.logger.info('Shutting down ...')
        self.isShuttingDown = True
        self.schedule.isShuttingDown = True
        sys.exit(0)

    def shutdown_handler(self):
        self.logger.info("Cleaning up scheduled jobs ...")
        self.isShuttingDown = True
        self.schedule.isShuttingDown = True
        self.schedule.shutdown()
        self.logger.info("Application shutdown.")

    def time_since(self, original_time):
        elapsed_time = time.time() - original_time
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
