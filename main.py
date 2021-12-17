import asyncio

from application import FaceClub, to_json
import logging
from flask import Flask, render_template
import time

faceClub = FaceClub("conf/config.yaml")

logger = logging.getLogger('Scheduler')
asyncio.run(faceClub.imageDatabase.families())


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

app = Flask(__name__)


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
    return to_json({'status': 'stopped'})


@app.route("/job/start")
def start_job():
    faceClub.schedule.resume('face_job')
    logger.info("started schedule")
    return to_json({'status': 'started'})


@app.route("/job/list")
def list_jobs():
    return to_json(faceClub.schedule.list())


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
