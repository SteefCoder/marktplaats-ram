import datetime
import json
import sched

from listings import get_and_parse_listings


# every hour or so, do get_and_parse_listings
# then, check for changes.

listings_path = 'downloads/listings.json'


def load_listings() -> tuple[list[dict], list[dict]]:
    listings = json.load(open(listings_path))
    return listings['active'], listings['reserved']


def write_listings(active: list[dict], reserved: list[dict]):
    with open(listings_path, 'w', encoding='utf8') as f:
        json.dump({'active': active, 'reserved': reserved}, f, indent=2)


def now_iso() -> str:
    return datetime.datetime.now().isoformat()


def remove_listing(listings: list[dict], id: int):
    items = [x for x in listings if x['id'] == id]
    if len(items) != 1:
        raise ValueError("whoops, not possible")
    item = items[0]
    listings.remove(item)
    return item


def update_listings():
    new_listings = get_and_parse_listings()
    active, reserved = load_listings()

    active_ids = set(x['id'] for x in active)
    reserved_ids = set(x['id'] for x in reserved)

    for listing in new_listings:
        if listing['price type'] == 'RESERVED':
            if listing['id'] in active_ids:
                active_listing = remove_listing(active, listing['id'])
                active_listing['reserved at'] = now_iso()
                reserved.append(active_listing)
            elif listing['id'] in reserved_ids:
                pass
            else:
                listing['listed at'] = now_iso()
                listing['reserved at'] = now_iso()
                reserved.append(listing)
        else:
            if listing['id'] in active_ids:
                pass
            elif listing['id'] in reserved_ids:
                reserved_listing = remove_listing(reserved, listing['id'])
                if 'relisted at' not in reserved_listing:
                    reserved_listing['relisted at'] = []
                reserved_listing['relisted at'].append(now_iso())
            else:
                listing['listed at'] = now_iso()
                active.append(listing)

    write_listings(active, reserved)


def schedule_update(scheduler: sched.scheduler):
    update_listings()
    scheduler.enter(3600, 1, schedule_update, argument=(scheduler,))


def main():
    scheduler = sched.scheduler()
    schedule_update(scheduler)


if __name__ == '__main__':
    main()
