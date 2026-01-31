from enum import Enum


class OfferedSince(Enum):
    TODAY = "Vandaag"
    YESTERDAY = "Gisteren"
    PAST_WEEK = "Een week"
    ALL_TIME = "Altijd"
