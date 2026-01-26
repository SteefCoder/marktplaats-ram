import datetime
import requests

from extract import extract_ram_info


def get_listing_page(offset: int):
    url = "https://www.marktplaats.nl/lrp/api/search"
    params = {
        "attributesByKey[]": "offeredSince:Gisteren",
        "l1CategoryId": 322,
        "l2CategoryId": 331,
        "limit": 100,
        "offset": offset
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0",
        "Host": "www.marktplaats.nl",
    }

    response = requests.get(url, params, headers=headers)
    response.raise_for_status()
    return response.json()


def get_all_listings():
    results = []
    for i in range(10):
        page = get_listing_page(100 * i)
        results += page['listings']
        if len(page['listings']) < 100:
            break
    return results


def today_iso():
    return datetime.date.today().isoformat()


def yesterday_iso():
    date = datetime.date.today() - datetime.timedelta(days=1)
    return date.isoformat()


def parse_listings(listings: list[dict]):
    ram_infos = []
    for l in listings:
        info = extract_ram_info(l['title'] + '\n' + l['description'])
        info |= {
            'id': l['itemId'],
            'price (euro)': l['priceInfo']['priceCents'] / 100,
            'price per gb': l['priceInfo']['priceCents'] / 100,
            'price type': l['priceInfo']['priceType'],
            'title': l['title'],
            'description': l['categorySpecificDescription'],
            'seller_id': l['sellerInformation']['sellerId'],
            'city': l['location']['cityName'],
            'reserved': l['reserved'],
            'date': today_iso() if l['date'] == 'Vandaag' else yesterday_iso(),
            'images': l.get('imageUrls', []),
        }

        if info['price type'] in ('BIDDING', 'RESERVED'):
            info['price (euro)'] = None
        if info['total (gb)'] and info['price (euro)'] is not None:
            info['price per gb'] = info['price (euro)'] / info['total (gb)']
        else:
            info['price per gb'] = None
        
        ram_infos.append(info)

    return ram_infos


def get_and_parse_listings():
    listings = get_all_listings()
    return parse_listings(listings)
