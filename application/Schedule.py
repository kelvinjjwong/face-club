import logging
from apscheduler.schedulers.background import BackgroundScheduler


class Schedule:
    logger = None
    scheduler = None
    isShuttingDown = False

    job_blockers = []

    def __init__(self):
        self.logger = logging.getLogger('Scheduler')
        self.scheduler = BackgroundScheduler()
        pass

    def start(self):
        self.scheduler.start()

    def add(self, job_id, seconds, func):
        self.scheduler.add_job(
            func,
            trigger='interval',
            seconds=seconds,
            id=job_id
        )
        self.job_blockers.append({
            'job_id': job_id,
            'stop': False,
            'stopped': False
        })

    def mark_job_stopped(self, job_id):
        for job_blocker in self.job_blockers:
            if job_blocker["job_id"] == job_id:
                job_blocker["stopped"] = True

    def mark_job_runnable(self, job_id):
        for job_blocker in self.job_blockers:
            if job_blocker["job_id"] == job_id:
                job_blocker["stopped"] = False

    def force_stop_job(self, job_id):
        self.scheduler.pause_job(job_id)
        for job_blocker in self.job_blockers:
            if job_blocker["job_id"] == job_id:
                job_blocker["stop"] = True

    def unblock_job(self, job_id):
        for job_blocker in self.job_blockers:
            if job_blocker["job_id"] == job_id:
                job_blocker["stop"] = False
        self.mark_job_runnable(job_id)

    def should_stop_job_now(self, job_id):
        for job_blocker in self.job_blockers:
            if job_blocker["job_id"] == job_id and job_blocker["stop"] is True:
                return True
        return False

    def resume(self, job_id):
        self.scheduler.resume_job(job_id)

    def stop(self, job_id):
        self.scheduler.pause_job(job_id)

    def stopAll(self):
        self.scheduler.pause()

    def resumeAll(self):
        self.scheduler.resume()

    def is_job_stopped(self, job_id):
        for job_blocker in self.job_blockers:
            if job_blocker["job_id"] == job_id:
                print(job_blocker)
                return job_blocker["stopped"]
        return True

    def status(self, job_id):
        job = self.scheduler.get_job(job_id)
        if job is not None:
            if str(job.next_run_time) == 'None':
                return {
                    'status': 'stopped',
                    'id': job_id,
                    'start_date': str(job.trigger.start_date),
                    'interval': str(job.trigger.interval)
                }
            else:
                return {
                    'status': 'running',
                    'id': job_id,
                    'start_date': str(job.trigger.start_date),
                    'interval': str(job.trigger.interval)
                }
        else:
            return {
                'status': 'not_initiated',
                'id': job_id
            }

    def list(self):
        schedules = []
        for job in self.scheduler.get_jobs():

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

        self.logger.info(schedules)
        return schedules

    def shutdown(self):
        self.scheduler.remove_all_jobs()
        self.scheduler.shutdown()
