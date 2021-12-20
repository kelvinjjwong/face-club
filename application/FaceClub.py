import time
import math
import logging
from datetime import datetime
import atexit
import sys
import signal
import asyncio
import os

from application import to_json
from application.FaceRecognizer import FaceRecognizer
from application.Workspace import Workspace
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
    workspace = None
    faceRecognizer = None

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
        self.workspace = Workspace(self.config.workspace_conf)
        self.faceRecognizer = FaceRecognizer()
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

    def is_ready_for_start_training(self):
        return (not self.faceRecognizer.isTraining) \
               and (not self.workspace.isCopyingImagesToDataset) \
               and self.workspace.is_ready_for_training() \
               and not self.faceRecognizer.isRecognizing

    def is_ready_for_start_recognition(self):
        return (not self.faceRecognizer.isRecognizing) \
               and (not self.workspace.isCopyingImagesToWorkspace) \
               and self.workspace.is_ready_for_recognition() \
               and not self.faceRecognizer.isTraining

    def should_stop_training(self):
        return self.faceRecognizer.isRecognizing or self.workspace.isCopyingImagesToDataset

    def should_stop_recognition(self):
        return self.faceRecognizer.isTraining or self.workspace.isCopyingImagesToWorkspace

    def fromRepositoryToWorkspace(self, recreate_db=False):
        if self.config.external_database_enable:
            self.workspace.cleanWorkspace()
            self.faceDatabase.dropSchema()
            self.faceDatabase.initSchema()
            external_records = asyncio.run(self.imageDatabase.unrecognizedFaces(100))
            all_mounted, volumes = self.workspace.check_mount_point(external_records)
            if not all_mounted:
                msg = "External volume is not mounted. Operation aborted."
                self.logger.error(msg)
                self.logger.error(volumes)
                return False, volumes
            else:
                self.logger.info(volumes)
                self.logger.info("External volume is mounted.")
            incoming_faces = self.workspace.fromRepositoryToWorkspace(external_records)
            for face in incoming_faces:
                self.faceDatabase.insert_face(face)
            msg = "Processed %s face records" % len(incoming_faces)
            self.logger.info(msg)
            return True, incoming_faces
        else:
            msg = "External DB connection is DISABLED. Operation aborted."
            self.logger.info(msg)
            return False, [msg]

    def fromRepositoryToDataset(self):
        self.workspace.isCopyingImagesToDataset = True
        # TODO copy images from external volumes
        self.workspace.isCopyingImagesToDataset = False
        # finally create a version backup
        self.workspace.backupDataset()
        pass

    def recognize_images(self, limit=10):
        self.faceRecognizer.isRecognizing = True
        model_file = self.workspace.get_model_file_path()
        yield to_json({
            "recognition_progress": "",
            "peopleId": "",
            "state": "STARTUP",
            "face_file": "",
            "source_file": "",
            "file_size_kb": 0,
            "time_cost_sec": 0,
            "pic_size": "",
            "pic_channels": ""
        })
        records = self.faceDatabase.get_faces(limit=limit)
        yield to_json({
            "recognition_progress": "0/{}".format(len(records)),
            "peopleId": "",
            "state": "COUNT",
            "face_file": "",
            "source_file": "",
            "file_size_kb": 0,
            "time_cost_sec": 0,
            "pic_size": "",
            "pic_channels": ""
        })
        i = 0
        folder = self.config.workspace_conf["images"]
        files = os.listdir(folder)
        for filename in files:
            file_path = os.path.join(folder, filename)
            _, extension = os.path.splitext(filename)
            i += 1
            if os.path.isfile(file_path) and extension.lower() in ('.jpg', '.png', '.jpeg'):
                #for record in records:
                file_size = os.path.getsize(file_path) / 1024
                yield to_json({
                    "recognition_progress": "{}/{}".format(i, len(files)),
                    "peopleId": "",
                    "state": "PROCESSING",
                    "face_file": file_path,
                    "source_file": '',
                    "file_size_kb": file_size,
                    "time_cost_sec": 0,
                    "pic_size": "",
                    "pic_channels": ""
                })
                started = datetime.now()
                #file_path = self.workspace.get_image_file_path(record["faceId"], record["fileExt"])
                people, width, height, channels = self.faceRecognizer.recognize_image(model_file, file_path)
                finished = datetime.now()
                delta = (finished - started)
                yield to_json({
                    "recognition_progress": "{}/{}".format(i, len(files)),
                    "peopleId": ",".join(people),
                    "state": "PROCESSED",
                    "face_file": file_path,
                    "source_file": '',
                    "file_size_kb": file_size,
                    "time_cost_sec": delta.seconds,
                    "pic_size": ("%s x %s" % (width, height)),
                    "pic_channels": ("%s" % channels)
                })
        yield to_json({
            "recognition_progress": "",
            "peopleId": "",
            "state": "DONE",
            "face_file": "",
            "source_file": "",
            "file_size_kb": 0,
            "time_cost_sec": 0,
            "pic_size": "",
            "pic_channels": ""
        })
        self.faceRecognizer.isRecognizing = False
        pass
