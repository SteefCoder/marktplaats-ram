import datetime
from enum import Enum
import time

import requests

import dates

class OfferedSince(Enum):
    TODAY = "Vandaag"
    YESTERDAY = "Gisteren"
    PAST_WEEK = "Een week"
    ALL_TIME = "Altijd"


def get_ram_listing_page(since: OfferedSince, page: int, limit: int = 100) -> list[dict]:
    url = "https://www.marktplaats.nl/lrp/api/search"
    params = {
        "attributesByKey[]": "offeredSince:" + since.value,
        # "attributeRanges[]": ... # for price and stuff
        "sortBy": "SORT_INDEX",  # sort by date
        "sortOrder": "DECREASING",  # newest first
        "l1CategoryId": 322,    # computers en software
        "l2CategoryId": 331,    # werkgeheugen (ram)
        "limit": limit,
        "offset": limit * page,
        # "viewOptions": "list-view",
        # "query": "...",
        # "searchInTitleAndDescription": True,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0",
        "Host": "www.marktplaats.nl",
    }

    response = requests.get(url, params, headers=headers)
    response.raise_for_status()
    return response.json()['listings']


def parse_ram_listing(listing: dict) -> dict:
    attributes = {
        x['key']: x['value']
        for x in listing.get('attributes', []) + listing.get('extendedAttributes', [])
    }
    info = {
        'item_id': listing['itemId'],
        'seller_id': listing['sellerInformation']['sellerId'],
        'seller_name': listing['sellerInformation']['sellerName'],
        'title': listing['title'],
        'description': listing['categorySpecificDescription'],
        'price_euro': listing['priceInfo']['priceCents'] / 100,
        'price_type': listing['priceInfo']['priceType'],
        'city': listing['location']['cityName'],
        'reserved': listing['reserved'],
        'images': listing.get('imageUrls', []),
        'url': listing['vipUrl'],
        'date': listing['date'],
        'priority': listing['priorityProduct'],
        'condition': attributes.get('condition'),
        'delivery': attributes.get('delivery'),
        'capacity': attributes.get('capacity'),
        'intended_for': attributes.get('intendedFor'),
        'generation': attributes.get('memoryType')
    }

    if info['date'] == 'Vandaag':
        info['listed_at'] = dates.now_iso()
        info['date'] = dates.get_absolute_date(info['date']).isoformat()
    else:
        date = dates.get_absolute_date(info['date'])

        # hour=18 is just an arbitrairy choice
        # we don't know at what time in the day it was listed.
        info['listed_at'] = datetime.datetime(
            year=date.year, month=date.month, day=date.day, hour=18
        ).isoformat()
        info['date'] = date.isoformat()

    return info


def get_ram_listings(
    since: datetime.date,
    max_pages: int = 30,
    page_limit: int = 100,
    delay: float = 0.0
):
    listings = []
    for page_n in range(max_pages):
        page = get_ram_listing_page(OfferedSince.ALL_TIME, page_n, page_limit)
        listings += [parse_ram_listing(l) for l in page]
        if len(listings) < page_limit:
            break

        # since the page is sorted, the last listing should contain the earliest date
        date = datetime.date.fromisoformat(listings[-1]['date'])
        if date < since:
            break

        if delay:
            time.sleep(delay)

    return listings
