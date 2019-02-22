import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity, TakeFirst


class CityItem(scrapy.Item):
    city_name = scrapy.Field()
    city_state = scrapy.Field()
    city_url = scrapy.Field()
    city_transparency_url = scrapy.Field()


class CityItemLoader(ItemLoader):
    default_item_class = CityItem
    default_output_processor = TakeFirst()

    city_transparency_url_out = Identity()
