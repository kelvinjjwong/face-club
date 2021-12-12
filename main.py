# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import yaml
import logging
import os
from logging.config import fileConfig
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

os.makedirs("log", exist_ok=True)
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('Scheduler')

def load_conf_file(config_file):
   with open(config_file, "r") as f:
       config = yaml.safe_load(f)
       server_conf = config[0]["server"]
       exec_conf = config[1]["execution"]
   return server_conf, exec_conf

server_conf,exec_conf = load_conf_file("config.yaml")
username=server_conf["username"]
url=server_conf["url"]

logger.info("loaded config item - %s", username)
logger.info("loaded config item - %s", url)

logger.info("Application started.")

def job():
	logger.info('job running')

scheduler = BackgroundScheduler()
scheduler.start()

scheduler.add_job(
	job,
	trigger='interval',
	seconds=5,
    id='face_job'
)

app = Flask(__name__)

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/stop")
def stopJob():
    scheduler.pause_job('face_job')
    logger.info("stopped schedule")
    return "stopped"

@app.route("/start")
def startJob():
    scheduler.resume_job('face_job')
    logger.info("started schedule")
    return "started"

@app.route("/list/jobs")
def printJobs():
    scheduler.print_jobs()
    return "printed job list"

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
