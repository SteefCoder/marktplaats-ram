import datetime
import json
import pathlib

import numpy as np

listings_path = pathlib.Path('downloads/listings.json').resolve()


def to_timestamp(isotime: str) -> float:
    return datetime.datetime.fromisoformat(isotime).timestamp()

def to_strftime(timestamp: int) -> str:
    return datetime.datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")


def load_listings() -> tuple[list[dict], list[dict]]:
    listings = json.load(open(listings_path))
    return listings['active'], listings['reserved']


def print_time_hist(data: list[float], name: str):
    values, edges = np.histogram(data)

    print(f"----- Histogram {name} -----")
    for i, v in enumerate(values):
        print(f"{to_strftime(edges[i])} - {to_strftime(edges[i + 1])}: {v}")
    print()


def time_hist():
    active, reserved = load_listings()
    
    active_times = [to_timestamp(x['listed at']) for x in active + reserved]
    reserved_times = [to_timestamp(x['reserved at']) for x in reserved]

    print_time_hist(active_times, "active times")
    print_time_hist(reserved_times, "reserved times")


if __name__ == '__main__':
    time_hist()