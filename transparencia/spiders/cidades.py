# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from transparencia.items import CityItemLoader


class CidadesSpider(scrapy.Spider):
    name = 'cidades'
    start_urls = ['https://pt.wikipedia.org/wiki/Lista_de_munic%C3%ADpios_do_Brasil']

    def parse(self, response):
        le = LinkExtractor(restrict_css=('#bodyContent li'), deny=('index.php'))
        for link in le.extract_links(response):
            yield scrapy.Request(link.url, callback=self.parse_wikipedia_city)

    def parse_wikipedia_city(self, response):
        il = CityItemLoader(response=response)

        il.add_css('city_name', '#firstHeading::text')
        il.add_xpath('city_state', '//th[contains(., "Unidade federativa")]/following-sibling::td/a/text()')

        # City URLs are included in very different ways in Wikipedia :-(
        il.add_xpath('city_url', '//tr[contains(., "Página oficial")]/following-sibling::tr/td/a[contains(@href, ".gov.br")]/@href')
        il.add_xpath('city_url', '//a[contains(., "Prefeitura") and contains(@href, ".gov.br")]/@href')
        il.add_xpath('city_url', '//a[contains(., "prefeitura") and contains(@href, ".gov.br")]/@href')
        il.add_xpath('city_url', '//a[contains(., "Sítio oficial") and contains(@href, ".gov.br")]/@href')

        item = il.load_item()

        city_url = item.get('city_url')
        if city_url:
            yield scrapy.Request(city_url, callback=self.parse_city, meta={'item': item})

    def parse_city(self, response):
        il = CityItemLoader(item=response.meta.get('item'))

        le = LinkExtractor(allow=('transparencia', 'transparente'))
        links = [link.url for link in le.extract_links(response)]

        il.add_value('city_transparency_url', links)

        yield il.load_item()
