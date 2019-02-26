import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Compose, TakeFirst


def find_most_likely_url(values):
    if values:
        # probably the most likely URL is the shortest
        return min((url for url in values), key=len)


def remove_dupes(values):
    if values:
        return list(set(values))


class CityItem(scrapy.Item):
    name = scrapy.Field()
    state = scrapy.Field()
    url = scrapy.Field()
    transparency_url = scrapy.Field()
    all_transparency_url = scrapy.Field()
    twitter = scrapy.Field()
    comments = scrapy.Field()


class CityItemLoader(ItemLoader):
    default_item_class = CityItem
    default_output_processor = TakeFirst()

    transparency_url_out = Compose(remove_dupes, find_most_likely_url)
    all_transparency_url_out = Compose(remove_dupes)
    twitter_out = Compose(remove_dupes)
