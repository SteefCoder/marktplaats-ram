from datetime import timedelta, date, datetime
import sched
import logging

import dates
from update import update_listings

logging.basicConfig(
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("monitor.log", encoding="utf8"),
        logging.StreamHandler()
    ]
)
logging.Formatter.converter = lambda *args: dates.now().timetuple()

# tuples with how many days back we want to get the listings
# and in how many hours we want to check for that
# since today - never
# since yesterday - every 2 hours
# since 2 days ago - every 6 hours
# since the last week - every day
# since the last month - every 2 days
# since the last year - every 4 days

# just checking for today is unreliable and leads to relisting problems.
UPDATE_INTERVAL_HOURS = [
    (timedelta(days=1), 2),
    (timedelta(days=2), 6),
    (timedelta(days=7), 24),
    (timedelta(days=30), 48),
    (timedelta(days=365), 96)
]


def get_update_type(time: datetime) -> date | None:
    hour = time.day * 24 + time.hour

    if time.hour > 22 or time.hour < 6:
        update_hours = UPDATE_INTERVAL_HOURS[2:]
    else:
        update_hours = UPDATE_INTERVAL_HOURS

    for time_back, hour_interval in update_hours[::-1]:
        if hour % hour_interval == 0:
            return dates.today() - time_back


def schedule_next_update(scheduler: sched.scheduler) -> None:
    now_hour = dates.now().replace(minute=0, second=0, microsecond=0) 
    # check for the first update in the next month
    for hour in range(1, 24 * 30):
        t = now_hour + timedelta(hours=hour)
        if get_update_type(t):
            wait = (t - dates.now()).total_seconds()
            logging.info(f"Scheduled next update at {t}.")
            scheduler.enter(wait, 1, execute_update, (scheduler,))
            return

    logging.info("No schedulable updates found.")


def execute_update(scheduler: sched.scheduler):
    logging.info("Start of scheduled update.")

    since = get_update_type(dates.now())
    if since:
        update_listings(since)

    schedule_next_update(scheduler)


def main():
    scheduler = sched.scheduler()
    schedule_next_update(scheduler)
    scheduler.run()


if __name__ == '__main__':
    main()