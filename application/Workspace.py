import logging
import os
import shutil
from datetime import datetime
from distutils.dir_util import copy_tree


class Workspace:
    logger = None
    workspace_conf = {}
    isCopyingImagesToDataset = False
    isCopyingImagesToWorkspace = False

    def __init__(self, workspace_conf):
        self.logger = logging.getLogger('FileMove')
        self.workspace_conf = workspace_conf
        pass

    def check_mount_point(self, external_db_records):
        overall_result = True
        volumes = set()
        volumes_dict = {}
        for image in external_db_records:
            path = os.path.realpath(image["path"])
            parts = path.split(os.path.sep)
            if parts[1] == "Volumes":
                volume = ("/%s/%s" % (parts[1], parts[2]))
                volumes.add(volume)
        for volume in volumes:
            ex = os.path.exists(volume)
            volumes_dict[volume] = ex
            overall_result = overall_result & ex
        return overall_result, volumes_dict

    def fromImageRepositoryToWorkspace(self, external_db_records):
        self.isCopyingImagesToWorkspace = True
        rtn = []
        folder = self.workspace_conf["images"]
        for image in external_db_records:
            src_file = image["path"]
            filename = os.path.basename(src_file)
            self.logger.info("src: %s" % src_file)
            _, extension = os.path.splitext(filename)
            new_filename = ("%s%s" % (image["id"], extension))
            dest_file = os.path.join(folder, new_filename)
            self.logger.info("des: %s" % dest_file)
            shutil.copy(src_file, dest_file)
            rec = {
                "imageId": image["id"],
                "sourcePath": src_file,
                "localFilePath": dest_file,
                "resizedFilePath": '',
                "taggedFilePath": '',
                "fileExt": extension,
                "peopleId": "",
                "peopleIdRecognized": "(not_recognized)",
                "peopleIdAssign": "(not_assigned)",
                "imageYear": image["photoTakenYear"],
                "sample": False,
                "scanned": False,
                "reviewed": False
            }
            rtn.append(rec)
        self.isCopyingImagesToWorkspace = False
        return rtn

    def fromImageFaceRepositoryToWorkspace(self, external_db_records):
        self.isCopyingImagesToWorkspace = True
        rtn = []
        folder = self.workspace_conf["images"]
        for image in external_db_records:
            src_file = ("%s%s/%s" % (image["cropPath"], image["subPath"], image["filename"]))
            self.logger.info("src: %s" % src_file)
            _, extension = os.path.splitext(image["filename"])
            new_filename = ("%s%s" % (image["id"], extension))
            dest_file = os.path.join(folder, new_filename)
            self.logger.info("des: %s" % dest_file)
            shutil.copy(src_file, dest_file)
            rec = {
                "imageId": image["imageId"],
                "sourcePath": src_file,
                "localFilePath": '',
                "resizedFilePath": '',
                "taggedFilePath": '',
                "fileExt": extension,
                "peopleId": "",
                "peopleIdRecognized": "",
                "peopleIdAssign": "",
                "imageYear": image["imageYear"],
                "sample": False,
                "scanned": False,
                "reviewed": False
            }
            rtn.append(rec)
        self.isCopyingImagesToWorkspace = False
        return rtn

    def cleanWorkspace(self):
        self.isCopyingImagesToWorkspace = True
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
        self.isCopyingImagesToWorkspace = False
        self.logger.info("Cleaned up workspace")

    def cleanDataset(self):
        self.isCopyingImagesToDataset = True
        folder = self.workspace_conf["dataset"]
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                self.logger.error('Failed to delete %s. Reason: %s' % (file_path, e))
        self.isCopyingImagesToDataset = False
        self.logger.info("Cleaned up dataset")

    def fromWorkspaceToPretrainDataset(self, internal_db_records):
        self.isCopyingImagesToDataset = True
        source_folder = self.workspace_conf["images"]
        dataset = self.workspace_conf["dataset"]
        for face in internal_db_records:
            peopleId = face["peopleIdAssign"] if face["peopleId"] == "Unknown" else face["peopleId"]
            if peopleId == "Unknown":
                continue
                # pass
            filename = ("%s%s" % (face["imageId"], face["fileExt"]))
            source_filename = os.path.join(source_folder, filename)
            target_folder = os.path.join(dataset, peopleId, filename)
            self.logger.info("pretrain src: %s" % source_filename)
            self.logger.info("pretrain des: %s" % target_folder)
            shutil.copy(source_filename, target_folder)
        self.isCopyingImagesToDataset = False

    def backupDataset(self):
        folder = os.path.realpath(self.workspace_conf["dataset"])
        parent_folder = os.path.dirname(folder)
        folder_name = os.path.basename(folder)
        now = datetime.now()
        dt = now.strftime("%Y-%m-%d_%H-%M-%S")
        new_folder_name = ("%s_%s" % (folder_name, dt))
        new_folder = os.path.join(parent_folder, new_folder_name)
        self.logger.info("mv from: %s" % folder)
        self.logger.info("mv to  : %s" % new_folder)
        shutil.move(folder, new_folder)
        os.makedirs(folder, exist_ok=True)

    def useDataset(self, folder_name):
        self.cleanDataset()
        self.isCopyingImagesToDataset = True
        folder = os.path.realpath(self.workspace_conf["dataset"])
        parent_folder = os.path.dirname(folder)
        new_folder = os.path.join(parent_folder, folder_name)
        self.logger.info("mv from: %s" % new_folder)
        self.logger.info("mv to  : %s" % folder)
        copy_tree(new_folder, folder)
        self.isCopyingImagesToDataset = False
        self.logger.info("replaced dataset")

    def backupModel(self):
        folder = os.path.realpath(self.workspace_conf["model"])
        parent_folder = os.path.dirname(folder)
        folder_name = os.path.basename(folder)
        now = datetime.now()
        dt = now.strftime("%Y-%m-%d_%H-%M-%S")
        new_folder_name = ("%s_%s" % (folder_name, dt))
        new_folder = os.path.join(parent_folder, new_folder_name)
        self.logger.info("mv from: %s" % folder)
        self.logger.info("mv to  : %s" % new_folder)
        shutil.move(folder, new_folder)
        os.makedirs(folder, exist_ok=True)

    def is_ready_for_training(self):
        files_in_dataset = self.list_dataset()
        return len(files_in_dataset) > 0

    def is_ready_for_recognition(self):
        models = self.list_model()
        images = self.list_images()
        return len(models) > 0 and len(images) > 0

    def list_model(self):
        models = []
        folder = os.path.realpath(self.workspace_conf["model"])
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path) and filename.startswith("model."):
                models.append({
                    'file': file_path,
                    'last_modified_time': datetime.fromtimestamp(int(os.path.getmtime(file_path)))
                                                  .strftime("%Y-%m-%d %H:%M:%S")
                })
        return models

    def list_images(self):
        images = []
        folder = os.path.realpath(self.workspace_conf["images"])
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                images.append({
                    'file': file_path,
                    'last_modified_time': datetime.fromtimestamp(int(os.path.getmtime(file_path)))
                                                  .strftime("%Y-%m-%d %H:%M:%S")
                })
        return images

    def list_dataset(self):
        files = []
        folder = os.path.realpath(self.workspace_conf["dataset"])
        for sub_folder in os.listdir(folder):
            sub_folder_path = os.path.join(folder, sub_folder)
            if os.path.isdir(sub_folder_path):
                for filename in os.listdir(sub_folder_path):
                    file_path = os.path.join(sub_folder_path, filename)
                    _, extension = os.path.splitext(filename)
                    if os.path.isfile(file_path) and extension.lower() in ('.jpg', '.png', '.jpeg'):
                        files.append({
                            'peopleId': sub_folder,
                            'file': file_path,
                            'last_modified_time': datetime.fromtimestamp(int(os.path.getmtime(file_path)))
                                                          .strftime("%Y-%m-%d %H:%M:%S")
                        })
        return files

    def list_dataset_people(self):
        datasets = []
        folder = os.path.realpath(self.workspace_conf["dataset"])
        for sub_folder in os.listdir(folder):
            sub_folder_path = os.path.join(folder, sub_folder)
            if os.path.isdir(sub_folder_path):
                datasets.append({
                    'peopleId': sub_folder,
                    'last_modified_time': datetime.fromtimestamp(int(os.path.getmtime(sub_folder_path)))
                                                  .strftime("%Y-%m-%d %H:%M:%S")
                })
        return datasets

    def list_dataset_of_people(self, peopleId):
        files = []
        folder = os.path.realpath(self.workspace_conf["dataset"])
        folder_path = os.path.join(folder, peopleId)
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            _, extension = os.path.splitext(filename)
            if os.path.isfile(file_path) and extension.lower() in ('.jpg', '.png', '.jpeg'):
                files.append({
                    'peopleId': peopleId,
                    'file': file_path,
                    'last_modified_time': datetime.fromtimestamp(int(os.path.getmtime(file_path)))
                        .strftime("%Y-%m-%d %H:%M:%S")
                })
        return files

    def get_dataset_backups(self):
        backups = []
        folder = os.path.realpath(self.workspace_conf["dataset"])
        parent_folder = os.path.dirname(folder)
        for filename in os.listdir(parent_folder):
            file_path = os.path.join(parent_folder, filename)
            if os.path.isdir(file_path) and filename.startswith("dataset_"):
                backups.append({
                    'backup_folder': filename,
                    'last_modified_time': datetime.fromtimestamp(int(os.path.getmtime(file_path)))
                                                  .strftime("%Y-%m-%d %H:%M:%S")
                })
        return backups

    def get_model_backups(self):
        backups = []
        folder = os.path.realpath(self.workspace_conf["model"])
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path) and filename.startswith("model_"):
                backups.append({
                    'backup_model': filename,
                    'last_modified_time': datetime.fromtimestamp(int(os.path.getmtime(file_path)))
                                                  .strftime("%Y-%m-%d %H:%M:%S")
                })
        return backups

    def get_model_file_path(self):
        folder = os.path.realpath(self.workspace_conf["model"])
        return os.path.join(folder, "model.pickle")

    def get_image_file_path(self, imageId, fileExt):
        folder = os.path.realpath(self.workspace_conf["images"])
        filename = ("%s%s" % (imageId, fileExt))
        return os.path.join(folder, filename)

    def generate_backup_file_path(self, origin_file_path, suffix):
        filename = os.path.basename(origin_file_path)
        folder = os.path.dirname(origin_file_path)
        origin_filename, extension = os.path.splitext(filename)
        part = str(origin_filename).partition("_")
        out_filename = "%s_%s%s" % (part[0], suffix, extension)
        out_file_path = os.path.join(folder, out_filename)
        return out_file_path, out_filename, extension

    def backup_model(self, model_file):
        dt = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        out_file_path, out_filename, file_ext = self.generate_backup_file_path(model_file, dt)
        self.logger.info("copy from: %s" % model_file)
        self.logger.info("copy to  : %s" % out_file_path)
        try:
            shutil.copy(model_file, out_file_path)
        except Exception as e:
            print(e)
        return out_file_path
