import asyncio
import time
import random
import logging
from datetime import datetime
from application import FaceClub, to_json
import flask
import os
from flask import Flask, render_template, request, send_from_directory, jsonify

app = Flask(__name__)

faceClub = FaceClub("conf/config.yaml")

logger = logging.getLogger('WebAPI')


def face_job():
    logger.info('job task started')
    seconds = 15
    while seconds > 0:
        logger.info("is shutting down %s" % faceClub.isShuttingDown)
        if faceClub.isShuttingDown:
            logger.info("break job task due to shutting down")
            break
        time.sleep(1)
        seconds -= 1
    logger.info('job task completed')


faceClub.schedule.add('face_job', 5, face_job)
faceClub.schedule.stop('face_job')


@app.before_request
def request_start():
    """ begins timing of single request """
    logger.info("{} {}".format(
        flask.request.method, flask.request.url)
    )
    started = datetime.now()

    # put variables in app context (threadlocal for each request)
    ctx = app.app_context()
    flask.g.id = random.randint(1, 65535)
    flask.g.started = started


@app.after_request
def set_response_headers(response):
    """ Ensures no cache """
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.teardown_request
def request_end(error=None):
    """ end timing of single request """
    finished = datetime.now()

    # retrieve params from request context
    block_size = flask.request.args.get('block_size', default=1024, type=int)
    nblocks = flask.request.args.get('nblocks', default=10, type=int)
    sleep_ms = flask.request.args.get('sleep_ms', default=0, type=int)
    use_static_data = flask.request.args.get('use_static_data', default=0, type=int)

    # retrieve params from app context (threadlocal for each request)
    id = flask.g.id
    started = flask.g.started
    delta = (finished - started)
    milliseconds = delta.microseconds / 1000.0

    # show final stats of request
    logger.info("{} {} duration={}ms".format(
        flask.request.method, flask.request.url, milliseconds)
    )


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/health")
def health():
    return to_json(faceClub.health())


@app.route("/job/status")
def job_status():
    return to_json(faceClub.schedule.status('face_job'))


@app.route("/job/stop")
def stop_job():
    faceClub.schedule.stop('face_job')
    logger.info("stopped schedule")
    return list_jobs()


@app.route("/job/start")
def start_job():
    faceClub.schedule.resume('face_job')
    logger.info("started schedule")
    return list_jobs()


@app.route("/job/list")
def list_jobs():
    records = faceClub.schedule.list()
    for record in records:
        record["actions"] = [
            {
                'func': 'stop_job',
                'id': record["id"]
            },
            {
                'func': 'resume_job',
                'id': record["id"]
            },
            {
                'func': 'kill_job',
                'id': record["id"]
            }
        ]
    return to_json(records)


@app.route("/images/copy")
def copy_images_to_workspace():
    result, records = faceClub.fromRepositoryToWorkspace()
    return to_json(records)


@app.route("/images/list")
def list_images_in_workspace():
    records = faceClub.faceDatabase.get_images(limit=faceClub.config.internal_database_display_amount)
    for record in records:
        resizedFilePath = record["resizedFilePath"]
        taggedFilePath = record["taggedFilePath"]
        record["localFilePath"] = {
            'text': record["localFilePath"],
            'actions': [
                {
                    'func': 'view',
                    'id': record["localFilePath"]
                },
                {
                    'func': 'thumbnail',
                    'id': str(record["localFilePath"]).replace(record["fileExt"], ("_%s%s" % (200, record["fileExt"])))
                }
            ]
        }
        record["resizedFilePath"] = {
            'text': resizedFilePath,
            'actions': [
                {
                    'func': 'view',
                    'id': resizedFilePath
                },
                {
                    'func': 'canvas',
                    'id': resizedFilePath
                }
            ]
        }
        record["taggedFilePath"] = {
            'text': taggedFilePath,
            'actions': [
                {
                    'func': 'view',
                    'id': taggedFilePath
                },
                {
                    'func': 'canvas',
                    'id': resizedFilePath
                }
            ]
        }
        record["sample"] = {
            'text': record["sample"],
            'actions': [
                {
                    'func': 'toggle_sample',
                    'id': record["imageId"]
                }
            ]
        }
        record["scanWrong"] = {
            'text': record["scanWrong"],
            'actions': [
                {
                    'func': 'toggle_scan_result',
                    'id': record["imageId"]
                }
            ]
        }
    return to_json(records)


@app.route("/images/scanned/faces")
def list_scanned_faces_in_workspace():
    records = faceClub.faceDatabase.get_scanned_faces(limit=faceClub.config.internal_database_display_amount)
    for record in records:
        resizedFilePath = record["resizedFilePath"]
        taggedFilePath = record["taggedFilePath"]
        record["localFilePath"] = {
            'text': record["localFilePath"],
            'actions': [
                {
                    'func': 'view',
                    'id': record["localFilePath"]
                },
                {
                    'func': 'thumbnail',
                    'id': str(record["localFilePath"]).replace(record["fileExt"], ("_%s%s" % (200, record["fileExt"])))
                }
            ]
        }
        record["resizedFilePath"] = {
            'text': resizedFilePath,
            'actions': [
                {
                    'func': 'view',
                    'id': resizedFilePath
                },
                {
                    'func': 'canvas',
                    'id': resizedFilePath
                }
            ]
        }
        record["taggedFilePath"] = {
            'text': taggedFilePath,
            'actions': [
                {
                    'func': 'view',
                    'id': taggedFilePath
                },
                {
                    'func': 'canvas',
                    'id': resizedFilePath
                }
            ]
        }
        record["sample"] = {
            'text': record["sample"],
            'actions': [
                {
                    'func': 'scanned_toggle_sample',
                    'id': record["imageId"]
                }
            ]
        }
        record["scanWrong"] = {
            'text': record["scanWrong"],
            'actions': [
                {
                    'func': 'scanned_toggle_scan_result',
                    'id': record["imageId"]
                }
            ]
        }
    return to_json(records)


@app.route("/dataset/backups")
def list_dataset_backups():
    records = faceClub.workspace.get_dataset_backups()
    for record in records:
        record["actions"] = [
            {
                'func': 'use_dataset',
                'id': record["backup_folder"]
            }
        ]
    return to_json(records)


@app.route("/dataset/use/<folder>")
def use_dataset(folder):
    faceClub.workspace.useDataset(folder)
    return to_json([{'use_dataset': 'done', 'dataset_version': folder}])


@app.route("/dataset/list")
def list_dataset_files():
    records = faceClub.workspace.list_dataset()
    for record in records:
        record["file"] = {
            'text': record["file"],
            'actions': [
                {
                    'func': 'view',
                    'id': record["file"]
                }
            ]
        }
    return to_json(records)


@app.route("/dataset/people")
def list_dataset_people():
    records = faceClub.workspace.list_dataset_people()
    for record in records:
        record["actions"] = [
            {
                'func': 'dataset_of_people',
                'id': record["peopleId"]
            }
        ]
    return to_json(records)


@app.route("/dataset/list/people/<peopleId>")
def list_dataset_of_people(peopleId):
    records = faceClub.workspace.list_dataset_of_people(peopleId)
    for record in records:
        record["file"] = {
            'text': record["file"],
            'actions': [
                {
                    'func': 'view',
                    'id': record["file"]
                }
            ]
        }
    return to_json(records)


@app.route("/model/list")
def list_model():
    records = faceClub.workspace.list_model()
    for record in records:
        record["actions"] = [
            {
                'func': 'backup_model',
                'id': ''
            }
        ]
    return to_json(records)


@app.route("/model/backups")
def list_model_backups():
    records = faceClub.workspace.get_model_backups()
    for record in records:
        record["actions"] = [
            {
                'func': 'use_model',
                'id': record["backup_model"]
            }
        ]
    return to_json(records)


@app.route("/face/toggle/sample/<imageId>")
def toggle_face_sample(imageId):
    faceClub.faceDatabase.toggle_sample(imageId)
    return list_images_in_workspace()


@app.route("/face/toggle/scan/result/<imageId>")
def toggle_face_scan_result(imageId):
    faceClub.faceDatabase.toggle_scan_result(imageId)
    return list_images_in_workspace()


@app.route("/face/scanned/toggle/sample/<imageId>")
def toggle_scanned_face_sample(imageId):
    faceClub.faceDatabase.toggle_sample(imageId)
    return list_scanned_faces_in_workspace()


@app.route("/face/scanned/toggle/scan/result/<imageId>")
def toggle_scanned_face_scan_result(imageId):
    faceClub.faceDatabase.toggle_scan_result(imageId)
    return list_scanned_faces_in_workspace()


@app.route("/training/start")
def start_training():
    if faceClub.is_ready_for_start_training():
        dataset_folder = faceClub.workspace.workspace_conf["dataset"]
        model_file = faceClub.workspace.get_model_file_path()
        return app.response_class(
            faceClub.faceRecognizer.training(dataset_folder, model_file, chunked_streaming=True),
            "text/html")
    else:
        return to_json({
            'training_progress': '',
            'peopleId': '',
            'file': '',
            'state': 'not_ready_for_start_training'
        })


@app.route("/recognition/start")
def start_recognition():
    if faceClub.is_ready_for_start_recognition():
        return app.response_class(
            faceClub.recognize_images(limit=20),
            "text/html")
    else:
        return to_json({
            'recognition_progress': 'not_ready_for_start_recognition'
        })


@app.route("/view")
def download_file():
    file_path = request.args.get('file')
    filename = os.path.basename(file_path)
    folder_path = os.path.dirname(file_path)
    return send_from_directory(folder_path, filename, as_attachment=False)


@app.route("/canvas")
def canvas():
    file_path = request.args.get('file')
    if file_path != '':
        filename = os.path.basename(file_path)
        prefix, extension = os.path.splitext(filename)
        imageId = prefix.replace("_1280", "")
        faces = faceClub.faceDatabase.get_faces(imageId)
        return render_template("canvas.html", imageId=imageId, file_path=file_path, faces=faces)
    else:
        return render_template("404.html")


@app.route("/people")
def get_people():
    records = []
    people = asyncio.run(faceClub.imageDatabase.get_people())
    for p in people:
        records.append({
            'peopleId': p['id'],
            'name': p['name'],
            'shortName': p['shortName'],
            'icon_file_path': ("%s%s/%s" % (p['iconCropPath'], p['iconSubPath'], p['iconFilename']))
        })
    return to_json(records)


@app.route("/tag/face", methods=['POST'])
def tag_face():
    try:
        content = request.json
        logger.info("tag_face got json")
        logger.info(content)
        print(content["peopleId"])
        print(content["personName"])
        print(content["shortName"])
        print(content["left"])
        print(content["top"])
        tag_a_person(content)
        update_peopleId_of_image(content["imageId"])
    except Exception as e:
        logger.error(e)
    return jsonify({
        'status': 'ok'
    })


def tag_a_person(content):
    if content["peopleId"] != "":
        person = asyncio.run(faceClub.imageDatabase.get_person(content["peopleId"]))
        if person is None:
            faceClub.imageDatabase.create_person(content["peopleId"], content["personName"], person["shortName"])
    faceClub.faceDatabase.assign_face(content["imageId"],
                                      content["top"], content["right"],
                                      content["bottom"], content["left"],
                                      content["peopleId"],
                                      person['personName'], person['shortName'])
    logger.info("Tagged %s top=%s right=%s bottom=%s left=%s to peopleId: %s"
                % (content["imageId"], content["top"], content["right"], content["bottom"], content["left"],
                   content["peopleId"]))

def update_peopleId_of_image(imageId):
    faces = faceClub.faceDatabase.get_faces(imageId)
    peopleIds = []
    for face in faces:
        peopleIds.append(face['peopleId'])
    faceClub.faceDatabase.assign_face_to_image(imageId, ",".join(peopleIds))
    # TODO re-generate _face image
    pass

@app.route("/tag/faces", methods=['POST'])
def tag_faces():
    array = request.json
    logger.info(array)
    for content in array:
        tag_a_person(content)
    update_peopleId_of_image(content["imageId"])
    return jsonify({
        'status': 'ok'
    })


@app.route("/untag/face", methods=['POST'])
def untag_face():
    content = request.json
    logger.info(content)
    faceClub.faceDatabase.delete_face(content["imageId"],
                                      content["top"], content["right"],
                                      content["bottom"], content["left"])
    update_peopleId_of_image(content["imageId"])
    logger.info("Untagged %s top=%s right=%s bottom=%s left=%s"
                % (content["imageId"], content["top"], content["right"], content["bottom"], content["left"]))
    return jsonify({
        'status': 'ok'
    })


@app.route("/untag/all/<imageId>")
def untag_all(imageId):
    faceClub.faceDatabase.delete_faces(imageId)
    update_peopleId_of_image(imageId)
    logger.info("Untagged ALL in %s" % imageId)
    return jsonify({
        'status': 'ok'
    })


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
