import datetime
import pathlib
import json
import logging

import dates
from extract import extract_ram_info
from marktplaats import get_ram_listings

logger = logging.getLogger(__name__)

listings_path = pathlib.Path('downloads/listings_v2.json').resolve()


def get_ram_listing_infos(since: datetime.date) -> dict[str, dict]:
    get_text = lambda l: l['title'] + '\n' + l['description']
    return {
        l['item_id']: l | extract_ram_info(get_text(l))
        for l in get_ram_listings(since, max_pages=100, delay=15)
    }


def load_listings() -> dict[str, dict]:
    if not listings_path.exists():
        write_listings({})
        return {}

    listings = json.load(open(listings_path))
    return listings['listings']


def write_listings(listings: dict[str, dict]) -> None:
    with listings_path.open('w', encoding='utf8') as f:
        json.dump({'listings': listings}, f, indent=2)


def update_listings(since: datetime.date) -> None:
    logger.info("Updating listings since: %s", since)
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
            old_listings[id]['relisted_at'].append(dates.now().isoformat())
            counts['relisted'] += 1
        
        # it was reserved
        elif not old['reserved'] and new['reserved']:
            old_listings[id]['reserved'] = True
            old_listings[id]['reserved_at'] = dates.now_iso()
            counts['reserved'] += 1
    
    # the ids that are only in the new listings
    for id in new_ids - old_ids:
        new = new_listings[id]

        # the new listing might have been reserved immediatly
        if new['reserved']:
            new['reserved_at'] = dates.now_iso()
            counts['reserved'] += 1
        
        # add the new listing
        old_listings[id] = new
        counts['listed'] += 1

    # the ids that are only in the old listings
    # these are either before the since date, reserved or taken down.
    # there is no way to tell the last two apart.
    for id in old_ids - new_ids:
        date = datetime.date.fromisoformat(old_listings[id]['date'])
        if date <= since:
            continue
        
        # either taken down or reserved, but we will assume
        # the post is reserved
        if not old_listings[id]['reserved']:
            old_listings[id]['reserved'] = True
            old_listings[id]['reserved_at'] = dates.now_iso()
            counts['reserved'] += 1
    
    write_listings(old_listings)

    logger.info("Done updating listings.")
    logger.info("Summary:\t %s total, %s listed, %s reserved, %s relisted.",
                len(new_listings), counts['listed'], counts['reserved'], counts['relisted'])
