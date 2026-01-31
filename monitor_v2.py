import datetime
import sched
import logging

logging.basicConfig(
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("monitor.log", encoding="utf8"),
        logging.StreamHandler()
    ]
)

from marktplaats import OfferedSince
from update import update_listings

UPDATE_INTERVAL_HOURS = {
    OfferedSince.TODAY: 1,
    OfferedSince.YESTERDAY: 2,
    OfferedSince.PAST_WEEK: 12,
    OfferedSince.ALL_TIME: 48
}


def get_update_type(hour_count: int) -> OfferedSince | None:
    if hour_count % UPDATE_INTERVAL_HOURS[OfferedSince.ALL_TIME] == 0:
        return OfferedSince.ALL_TIME
    elif hour_count % UPDATE_INTERVAL_HOURS[OfferedSince.PAST_WEEK] == 0:
        return OfferedSince.PAST_WEEK
    elif hour_count % UPDATE_INTERVAL_HOURS[OfferedSince.YESTERDAY] == 0:
        return OfferedSince.YESTERDAY
    elif hour_count % UPDATE_INTERVAL_HOURS[OfferedSince.TODAY] == 0:
        return OfferedSince.TODAY


def schedule_update(scheduler: sched.scheduler, hour_count: int):
    logging.info("Start of scheduled update.")

    since = get_update_type(hour_count)
    if since:
        update_listings(since)

    now = datetime.datetime.now()
    new_hour = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
    logging.info(f"Update done. Scheduling next update at {new_hour}.")
    scheduler.enter((new_hour - now).total_seconds(), 1, schedule_update, argument=(scheduler, hour_count + 1))


def main():
    scheduler = sched.scheduler()
    schedule_update(scheduler, datetime.datetime.now().hour)
    scheduler.run()


if __name__ == '__main__':
    main()