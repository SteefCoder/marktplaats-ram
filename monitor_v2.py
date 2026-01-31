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

import dates
from offered_since import OfferedSince
from update import update_listings

UPDATE_INTERVAL_HOURS = {
    OfferedSince.TODAY: 1,
    OfferedSince.YESTERDAY: 1,
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


def schedule_next_update(scheduler: sched.scheduler) -> None:
    new_hour = dates.next_hour()
    wait = (new_hour - dates.now()).total_seconds()
    logging.info(f"Scheduling next update at {new_hour}.")
    scheduler.enter(wait, 1, execute_update, (scheduler,))


def execute_update(scheduler: sched.scheduler):
    logging.info("Start of scheduled update.")

    now = dates.now()
    hour = now.day * 24 + now.hour
    since = get_update_type(hour)
    if since:
        update_listings(since)

    logging.info(f"Update done. [{(dates.now() - now).total_seconds()} sec]")
    schedule_next_update(scheduler)


def main():
    scheduler = sched.scheduler()
    schedule_next_update(scheduler)
    scheduler.run()


if __name__ == '__main__':
    main()