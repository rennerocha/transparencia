import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity, TakeFirst


class CityItem(scrapy.Item):
    name = scrapy.Field()
    state = scrapy.Field()
    url = scrapy.Field()
    transparency_url = scrapy.Field()
    twitter = scrapy.Field()
    comments = scrapy.Field()


class CityItemLoader(ItemLoader):
    default_item_class = CityItem
    default_output_processor = TakeFirst()

    transparency_url_out = Identity()
    twitter_out = Identity()
