from datetime import timedelta, date, time
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
# since today - every 2 hours
# since yesterday - every 4 hours
# since the last week - every day
# since the last month - every 2 days
# since the last year - every 4 days
UPDATE_INTERVAL_HOURS = [
    (timedelta(days=0), 1),
    (timedelta(days=1), 3),
    (timedelta(days=7), 24),
    (timedelta(days=30), 48),
    (timedelta(days=365), 96)
]


def get_update_since() -> date | None:
    now = dates.now()
    curr_hour = now.day * 24 + now.hour

    if now.time() > time(hour=22) or now.time() < time(hour=8):
        update_hours = [(timedelta(days=1), 4)] + UPDATE_INTERVAL_HOURS[2:]
    else:
        update_hours = UPDATE_INTERVAL_HOURS

    for time_back, hour_interval in update_hours[::-1]:
        if curr_hour % hour_interval == 0:
            return (now - time_back).date()


def schedule_next_update(scheduler: sched.scheduler) -> None:
    new_hour = dates.next_hour()
    wait = (new_hour - dates.now()).total_seconds()
    logging.info(f"Scheduled next update at {new_hour}.")
    scheduler.enter(wait, 1, execute_update, (scheduler,))


def execute_update(scheduler: sched.scheduler):
    logging.info("Start of scheduled update.")

    since = get_update_since()
    if since:
        update_listings(since)

    schedule_next_update(scheduler)


def main():
    scheduler = sched.scheduler()
    schedule_next_update(scheduler)
    scheduler.run()


if __name__ == '__main__':
    main()