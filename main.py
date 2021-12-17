# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from common import config_load, time_cost
import time
from datetime import datetime
import logging
import os
from logging.config import fileConfig
from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler

app_start_time = time.time()
app_start_date = str(datetime.now())

logging_conf, server_conf, exec_conf = config_load("config.yaml")
logpath = logging_conf["path"]
os.makedirs(logpath, exist_ok=True)
username = server_conf["username"]
url = server_conf["url"]

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('Scheduler')

logger.info("loaded config item - %s", username)
logger.info("loaded config item - %s", url)

logger.info("Application started.")


def face_job():
    logger.info('job running')


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
    return str({'isAvailable': True,
                'startTime': app_start_date,
                'currentTime': str(datetime.now()),
                'executionTime': time_cost(app_start_time)
                }).replace("'", "\"")


@app.route("/job/status")
def job_status():
    job_id = 'face_job'
    job = scheduler.get_job(job_id)
    if job is not None:
        if str(job.next_run_time) == 'None':
            return str({
                'status': 'stopped',
                'id': job_id,
                'start_date': str(job.trigger.start_date),
                'interval': str(job.trigger.interval)
            }).replace("'", "\"")
        else:
            return str({
                'status': 'running',
                'id': job_id,
                'start_date': str(job.trigger.start_date),
                'interval': str(job.trigger.interval)
            }).replace("'", "\"")
    else:
        return str({
            'status': 'not_initiated',
            'id': job_id
        }).replace("'", "\"")


@app.route("/job/stop")
def stop_job():
    scheduler.pause_job('face_job')
    logger.info("stopped schedule")
    return str({'status': 'stopped'}).replace("'", "\"")


@app.route("/job/start")
def start_job():
    scheduler.resume_job('face_job')
    logger.info("started schedule")
    return str({'status': 'started'}).replace("'", "\"")


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
    return str(schedules).replace("'", "\"")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
