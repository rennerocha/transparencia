# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError, TimeoutError

from transparencia.items import CityItemLoader


class CidadesSpider(scrapy.Spider):
    name = "cidades"
    start_urls = ["https://pt.wikipedia.org/wiki/Lista_de_munic%C3%ADpios_do_Brasil"]

    def parse(self, response):
        le = LinkExtractor(restrict_css=("#bodyContent li"), deny=("index.php"))
        for link in le.extract_links(response):
            yield scrapy.Request(link.url, callback=self.parse_wikipedia_city)

    def parse_wikipedia_city(self, response):
        il = CityItemLoader(response=response)

        il.add_css("name", "#firstHeading::text")
        il.add_xpath(
            "state",
            '//th[contains(., "Unidade federativa")]/following-sibling::td/a/text()',
        )

        # City URLs are included in very different ways in Wikipedia :-(
        il.add_xpath(
            "url",
            '//tr[contains(., "Página oficial")]/following-sibling::tr/td/a[contains(@href, ".gov.br")]/@href',
        )
        il.add_xpath(
            "url", '//a[contains(., "Prefeitura") and contains(@href, ".gov.br")]/@href'
        )
        il.add_xpath(
            "url", '//a[contains(., "prefeitura") and contains(@href, ".gov.br")]/@href'
        )
        il.add_xpath(
            "url",
            '//a[contains(., "Sítio oficial") and contains(@href, ".gov.br")]/@href',
        )

        item = il.load_item()

        url = item.get("url")
        if url:
            yield scrapy.Request(
                url,
                callback=self.parse_city,
                meta={"item": item},
                errback=self.failed_city,
            )
        else:
            self.logger.warning('Unable to find URL for {}'.format(item.get('name')))
            yield item

    def parse_city(self, response):
        il = CityItemLoader(item=response.meta.get("item"))

        le = LinkExtractor(allow=("transparencia", "transparente", "Transparencia"))
        links = [link.url for link in le.extract_links(response)]
        il.add_value("transparency_url", links)  # most likely URL
        il.add_value("all_transparency_url", links)

        le_twitter = LinkExtractor(allow_domains=("twitter.com"))
        twitter_links = [link.url for link in le_twitter.extract_links(response)]
        il.add_value("twitter", twitter_links)

        yield il.load_item()

    def failed_city(self, failure):
        error_message = failure.getErrorMessage()
        il = CityItemLoader(item=failure.request.meta.get("item", {}))

        if failure.check(HttpError):
            response = failure.value.response
            error_message = " - ".join([
                error_message, "Status Code {}".format(response.status)
            ])
            self.logger.error(error_message)
        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error("DNSLookupError on {}".format(request.url))
        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error("TimeoutError on {}".format(request.url))
        else:
            self.logger.error(error_message)

        il.add_value("comments", error_message)
        yield il.load_item()
