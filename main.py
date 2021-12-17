# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from application import FaceClub, to_json
import logging
from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import time
import sys
import signal

isShuttingDown = False

faceClub = FaceClub("config.yaml")

logger = logging.getLogger('Scheduler')

logger.info("Application started.")


@atexit.register
def goodbye():
    logger.info("Cleaning up scheduled jobs ...")
    global isShuttingDown
    isShuttingDown = True
    scheduler.remove_all_jobs()
    scheduler.shutdown()
    logger.info("Application shutdown.")


def shutdown_signal_handler(signum, frame):
    logger.info('Shutting down ...')
    global isShuttingDown
    isShuttingDown = True
    sys.exit(0)


signal.signal(signal.SIGINT, shutdown_signal_handler)


def face_job():
    logger.info('job task started')
    seconds = 15
    while seconds > 0:
        logger.info("is shutting down %s" % isShuttingDown)
        if isShuttingDown:
            logger.info("break job task due to shutting down")
            break
        time.sleep(1)
        seconds -= 1
    logger.info('job task completed')


scheduler = BackgroundScheduler()
scheduler.start()

scheduler.add_job(
    face_job,
    trigger='interval',
    seconds=5,
    id='face_job'
)

app = Flask(__name__)


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/health")
def health():
    return to_json(faceClub.health())


@app.route("/job/status")
def job_status():
    job_id = 'face_job'
    job = scheduler.get_job(job_id)
    if job is not None:
        if str(job.next_run_time) == 'None':
            return to_json({
                'status': 'stopped',
                'id': job_id,
                'start_date': str(job.trigger.start_date),
                'interval': str(job.trigger.interval)
            })
        else:
            return to_json({
                'status': 'running',
                'id': job_id,
                'start_date': str(job.trigger.start_date),
                'interval': str(job.trigger.interval)
            })
    else:
        return to_json({
            'status': 'not_initiated',
            'id': job_id
        })


@app.route("/job/stop")
def stop_job():
    scheduler.pause_job('face_job')
    logger.info("stopped schedule")
    return to_json({'status': 'stopped'})


@app.route("/job/start")
def start_job():
    scheduler.resume_job('face_job')
    logger.info("started schedule")
    return to_json({'status': 'started'})


@app.route("/job/list")
def list_jobs():
    schedules = []
    for job in scheduler.get_jobs():
        # logger.info("id: %s, name: %s, trigger: %s, next run: %s, repr: %s" % (
        #     job.id, job.name, job.trigger, job.next_run_time, repr(job.trigger)))

        job_status = 'running'
        if str(job.next_run_time) == 'None':
            job_status = 'stopped'

        jobdict = {'id': job.id,
                   'start_date': str(job.trigger.start_date),
                   'interval': str(job.trigger.interval),
                   'next_run_time': str(job.next_run_time),
                   'job_status': job_status
                   }

        schedules.append(jobdict)

    logger.info(schedules)
    return to_json(schedules)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
