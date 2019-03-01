import re
from urllib.parse import urlparse

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


def remove_invalid_twitter_urls(values):
    forbidden_usernames = ["", "share", "intent", "home", "search"]
    urls = remove_dupes([value.lower() for value in values])
    usernames = []
    for url in urls:
        parsed_url = urlparse(url)

        path = parsed_url.path
        user_m = re.match("\/[@#!]?(?P<username>[\w]*)\/?.*", path)
        if user_m:
            usernames.append(user_m.group("username").lower())

        fragment = parsed_url.fragment
        user_m = re.match("!\/(?P<username>[\w]*)\/?.*", fragment)
        if user_m:
            usernames.append(user_m.group("username").lower())

    usernames = remove_dupes(
        [username for username in usernames if username not in forbidden_usernames]
    )
    if usernames:
        return "https://twitter.com/{}".format(usernames.pop())


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
    twitter_out = Compose(remove_dupes, remove_invalid_twitter_urls)
