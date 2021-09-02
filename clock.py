from apscheduler.schedulers.blocking import BlockingScheduler

from configuration import MINUTES_INTERVAL_NUMBER

sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=MINUTES_INTERVAL_NUMBER)
def timed_job():
    print('This job is run every three minutes.')


@sched.scheduled_job('interval', seconds=30)
def seconds_timed_job():
    print('This job is run every 30 seconds.')


sched.start()
