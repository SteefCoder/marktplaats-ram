from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


AMS_TZ = ZoneInfo('Europe/Amsterdam')

def now() -> datetime:
    return datetime.now(AMS_TZ)


def now_iso() -> str:
    return now().isoformat()


def today() -> date:
    return now().date()


def days_ago(days: int) -> date:
    return today() - timedelta(days=days)


def next_hour() -> datetime:
    return now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)


def get_absolute_date(rel_date: str) -> date:
    if rel_date == 'Vandaag':
        return today()
    elif rel_date == 'Gisteren':
        return days_ago(1)
    elif rel_date == 'Eergisteren':
        return days_ago(2)
    else:
        dt = datetime.strptime(rel_date, '%d %b %y')
        return dt.date()
