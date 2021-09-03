from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from configuration import MINUTES_INTERVAL_NUMBER

sched = BlockingScheduler()


@sched.scheduled_job(IntervalTrigger(minutes=MINUTES_INTERVAL_NUMBER))
def timed_job():
    print('This job is run every three minutes.')


@sched.scheduled_job(IntervalTrigger(seconds=5))
def seconds_timed_job():
    print('This job is run every 5 seconds.')


sched.start()
