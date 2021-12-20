import asyncio
import time
import random
import logging
from datetime import datetime
from application import FaceClub, to_json
import flask
from flask import Flask, render_template

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


@app.before_request
def start_timing():
    """ begins timing of single request """
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
def end_timing(error=None):
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
    logger.info("requestId={},method={},path={},nblocks={},block_size={},sleep_ms={},duration={}ms".format(
        flask.g.id, flask.request.method, flask.request.path, nblocks, block_size, sleep_ms, milliseconds)
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
    records = faceClub.faceDatabase.get_faces(limit=faceClub.config.internal_database_display_amount)
    for record in records:
        record["sample"] = {
            'text': record["sample"],
            'actions': [
                {
                    'func': 'toggle_sample',
                    'id': record["faceId"]
                }
            ]
        }
        record["scanWrong"] = {
            'text': record["scanWrong"],
            'actions': [
                {
                    'func': 'toggle_scan_result',
                    'id': record["faceId"]
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


@app.route("/face/toggle/sample/<faceId>")
def toggle_face_sample(faceId):
    faceClub.faceDatabase.toggle_sample(faceId)
    return list_images_in_workspace()


@app.route("/face/toggle/scan/result/<faceId>")
def toggle_face_scan_result(faceId):
    faceClub.faceDatabase.toggle_scan_result(faceId)
    return list_images_in_workspace()


@app.route("/training/start")
def start_training():
    if faceClub.is_ready_for_start_training():
        dataset_folder = faceClub.workspace.workspace_conf["dataset"]
        model_file = faceClub.workspace.get_model_file_path()
        return app.response_class(
            faceClub.faceRecognizer.training(dataset_folder, model_file, chunked_streaming=True),
            "text/html")
    else:
        return to_json([{'training_status': 'not_ready_for_start_training'}])


@app.route("/recognition/start")
def start_recognition():
    if faceClub.is_ready_for_start_recognition():
        model_file = faceClub.workspace.get_model_file_path()

        def generate():
            yield to_json({
                "training_progress": "STARTUP"
            })
            faceClub.faceRecognizer.isRecognizing = True
            records = faceClub.faceDatabase.get_faces(limit=10)
            yield to_json({
                "training_progress": "TOTAL {}".format(len(records))
            })
            i = 0
            for record in records:
                i += 1
                yield to_json({
                    "training_progress": "PROCESSING {}/{}".format(i, len(records))
                })
                file_path = faceClub.workspace.get_image_file_path(record["faceId"], record["fileExt"])
                faceClub.faceRecognizer.recognize(model_file, file_path)
                yield to_json({
                    "training_progress": "PROCESSED {}/{}".format(i, len(records))
                })
                pass
            faceClub.faceRecognizer.isRecognizing = False
            yield to_json({
                "training_progress": "DONE"
            })

        return app.response_class(generate(), "text/html")
    else:
        return to_json([{'training_status': 'not_ready_for_start_training'}])


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
