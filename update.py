import datetime
import pathlib
import json
import logging

from marktplaats import get_ram_listings, OfferedSince
from extract import extract_ram_info

logger = logging.getLogger(__name__)

listings_path = pathlib.Path('downloads/listings_v2.json').resolve()


def now_iso() -> str:
    return datetime.datetime.now().isoformat()


def date_days_ago(days_ago: int) -> datetime.date:
    today = datetime.date.today()
    return today - datetime.timedelta(days=days_ago)


def offered_since_to_date(since: OfferedSince) -> datetime.date:
    if since == OfferedSince.TODAY:
        return datetime.date.today()
    elif since == OfferedSince.YESTERDAY:
        return date_days_ago(1)
    elif since == OfferedSince.PAST_WEEK:
        return date_days_ago(7)
    elif since == OfferedSince.ALL_TIME:
        # not really possible to have a date here
        return date_days_ago(1000)


def get_absolute_date(rel_date: str) -> datetime.date:
    if rel_date == 'Vandaag':
        return datetime.date.today()
    elif rel_date == 'Gisteren':
        return date_days_ago(1)
    elif rel_date == 'Eergisteren':
        return date_days_ago(2)
    else:
        dt = datetime.datetime.strptime(rel_date, '%d %b %y')
        return dt.date()


def get_ram_listing_infos(since: OfferedSince) -> dict[str, dict]:
    get_text = lambda l: l['title'] + '\n' + l['description']

    results = {}
    for l in get_ram_listings(since, max_pages=100, delay=3):
        x = l | extract_ram_info(get_text(l))

        # this is only for 
        if x['date'] == 'Vandaag':
            x['listed_at'] = now_iso()
            x['date'] = get_absolute_date(x['date']).isoformat()
        else:
            date = get_absolute_date(x['date'])

            # hour=18 is just an arbitrairy choice
            # we don't know at what time in the day it was listed.
            x['listed_at'] = datetime.datetime(
                year=date.year, month=date.month, day=date.day, hour=18
            ).isoformat()
            x['date'] = date.isoformat()

        results[x['item_id']] = x
        
    return results


def load_listings() -> dict[str, dict]:
    if not listings_path.exists():
        write_listings({})
        return {}

    listings = json.load(open(listings_path))
    return listings['listings']


def write_listings(listings: dict[str, dict]) -> None:
    with listings_path.open('w', encoding='utf8') as f:
        json.dump({'listings': listings}, f, indent=2)


def update_listings(since: OfferedSince) -> None:
    logger.info("Updating listings since: %s", since.value)
    new_listings = get_ram_listing_infos(since)
    old_listings = load_listings()

    new_ids = set(new_listings.keys())
    old_ids = set(old_listings.keys())

    counts = {
        'relisted': 0,
        'reserved': 0,
        'listed': 0
    }

    # the ids that are in both
    for id in new_ids & old_ids:
        old = old_listings[id]
        new = new_listings[id]

        # the status hasn't changed
        if old['reserved'] == new['reserved']:
            continue
            
        # it was relisted
        elif old['reserved'] and not new['reserved']:
            old_listings[id]['reserved'] = False
            if 'relisted_at' not in old:
                old_listings[id]['relisted_at'] = []
            old_listings[id]['relisted_at'].append(now_iso())
            counts['relisted'] += 1
        
        # it was reserved
        elif not old['reserved'] and new['reserved']:
            old_listings[id]['reserved'] = True
            old_listings[id]['reserved_at'] = now_iso()
            counts['reserved'] += 1
    
    # the ids that are only in the new listings
    for id in new_ids - old_ids:
        new = new_listings[id]

        # the new listing might have been reserved immediatly
        if new['reserved']:
            new['reserved_at'] = now_iso()
            counts['reserved'] += 1
        
        # add the new listing
        old_listings[id] = new
        counts['listed'] += 1

    # the ids that are only in the old listings
    # these are either before the since date, reserved or taken down.
    # there is no way to tell the last two apart.
    for id in old_ids - new_ids:
        date = datetime.date.fromisoformat(old_listings[id]['date'])

        # check if the listing is before the since date
        if since != OfferedSince.ALL_TIME and date < offered_since_to_date(since):
            continue
        
        # Because of a bug in the Marktplaats api
        # some listings show up as being listed today,
        # but are only found when OfferedSince is yesterday.
        # To prevent needless relisting, we only mark these when checking
        # yesterday or earlier.
        if since == OfferedSince.TODAY:
            continue
        
        # either taken down or reserved, but we will assume
        # the post is reserved
        old_listings[id]['reserved'] = True
        old_listings[id]['reserved_at'] = now_iso()
        counts['reserved'] += 1
    
    write_listings(old_listings)

    logger.info("Done updating listings.")
    logger.info("Summary:\t %s total, %s listed, %s reserved, %s relisted.",
                len(new_listings), counts['listed'], counts['reserved'], counts['relisted'])
