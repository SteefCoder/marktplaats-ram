from enum import Enum

from pydantic import BaseModel


class PriceModelType(Enum):
    FIXED = 'fixed'
    BIDDING = 'bidding'
    SEE_DESCRIPTION = 'see description'


class Base(BaseModel):
    pass


# https://api.marktplaats.nl/docs/v1/reference/price-models.html#price-models
class PriceModel(Base):
    model_type: PriceModelType


class FixedPriceModel(PriceModel):
    asking_price: int
    retail_price: int | None = None


class BiddingPriceModel(PriceModel):
    minimal_bid: int | None = None
    asking_price: int | None = None
    retail_price: int | None = None


class SeeDescriptionPriceModel(PriceModel):
    pass


class SellerModel(Base):
    selled_id: int
    seller_name: str
    phone_number: int | None = None
    accept_paypal: bool = False


class LocationModel(Base):
    postcode: str | None = None
    city_name: str | None = None


# https://api.marktplaats.nl/docs/v1/search-result.html#search-result
class SearchResult(Base):
    item_id: int
    category_id: int
    title: str
    description: str
    price_model: PriceModel
    seller: SellerModel | None = None
    location: LocationModel | None = None
    locale: str | None = None


class FilterPriceModel(Base):
    from_: int | None = Field(alias='from')
    to: int | None = None


class FilterModel(Base):
    price: FilterPriceModel | None = None
    post_code: str | None
    distance: int | None = None


class SortModel(Base):
    by: Literal['default', 'location', 'price'] = 'default'
    order: Literal['ascending', 'descending'] = 'descending'


# https://api.marktplaats.nl/docs/v1/search-advertisements.html
class SearchFields(Base):
    offset: int
    limit: int
    query: str | None = None
    category_id: int | None = None
    with_images: bool = False
    search_description: bool = False
    seller_id: int | None = None
    filters: FilterModel | None = None
    sort: SortModel | None = None


