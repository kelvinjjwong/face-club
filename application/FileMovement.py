import logging
import os
import shutil
from datetime import datetime


class FileMovement:
    logger = None
    workspace_conf = {}

    def __init__(self, workspace_conf):
        self.logger = logging.getLogger('FileMove')
        self.workspace_conf = workspace_conf
        pass

    def fromRepositoryToWorkspace(self, external_db_records):
        rtn = []
        folder = self.workspace_conf["images"]
        for image in external_db_records:
            src_file = ("%s%s/%s" % (image["cropPath"], image["subPath"], image["filename"]))
            self.logger.info("src: %s" % src_file)
            _, extension = os.path.splitext(image["filename"])
            new_filename = ("%s.%s" % (image["id"], extension))
            dest_file = os.path.join(folder, new_filename)
            self.logger.info("des: %s" % dest_file)
            #shutil.copy(src_file, dest_file)
            rec = {
                "faceId": image["id"],
                "imageId": image["imageId"],
                "sourcePath": src_file,
                "fileExt": extension,
                "peopleId": "Unknown",
                "peopleIdAssign": "Unknown",
                "imageYear": image["imageYear"],
                "sample": False,
                "scanned": False,
                "scanWrong": False
            }
            rtn.append(rec)
        return rtn

    def cleanWorkspace(self):
        folder = self.workspace_conf["images"]
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                self.logger.error('Failed to delete %s. Reason: %s' % (file_path, e))

    def fromWorkspaceToPretrainDataset(self, internal_db_records):
        source_folder = self.workspace_conf["images"]
        dataset = self.workspace_conf["dataset"]
        for face in internal_db_records:
            peopleId = face["peopleIdAssign"] if face["peopleId"] == "Unknown" else face["peopleId"]
            if peopleId == "Unknown":
                continue
                #pass
            filename = ("%s.%s" % (face["faceId"], face["fileExt"]))
            source_filename = os.path.join(source_folder, filename)
            target_folder = os.path.join(dataset, peopleId, filename)
            self.logger.info("pretrain src: %s" % source_filename)
            self.logger.info("pretrain des: %s" % target_folder)
            # shutil.copy(source_filename, target_folder)

    def backupDataset(self):
        folder = os.path.realpath(self.workspace_conf["dataset"])
        parent_folder = os.path.dirname(folder)
        folder_name = os.path.basename(folder)
        now = datetime.now()
        dt = now.strftime("%Y-%m-%d_%H-%M-%S")
        new_folder_name = ("%s_%s" % (folder_name, dt))
        new_folder = os.path.join(parent_folder, new_folder_name)
        print("mv from: %s" % folder)
        print("mv to  : %s" % new_folder)

