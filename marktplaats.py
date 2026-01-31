from enum import Enum
import time

import requests


class OfferedSince(Enum):
    TODAY = "Vandaag"
    YESTERDAY = "Gisteren"
    PAST_WEEK = "Een week"
    ALL_TIME = "Altijd"


def get_ram_listing_page(since: OfferedSince, page: int, limit: int = 100) -> list[dict]:
    url = "https://www.marktplaats.nl/lrp/api/search"
    params = {
        "attributesByKey[]": "offeredSince:" + since.value,
        # "attributeRanges[]": ...
        # attributenogwat
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
        for x in listing['attributes'] + listing['extendedAttributes']
    }

    return {
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


def get_ram_listings(
    since: OfferedSince,
    max_pages: int = 10,
    page_limit: int = 100,
    delay: float = 0
) -> list[dict]:
    listings = []
    for page_n in range(max_pages):
        page = get_ram_listing_page(since, page_n, page_limit)
        listings += [parse_ram_listing(l) for l in page]
        if len(page) < page_limit:
            break
        
        if delay:
            time.sleep(delay)
    
    return listings
