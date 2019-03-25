import csv
import datetime

import requests
import scrapy


class StatusSpider(scrapy.Spider):
    name = "status_checker"
    handle_httpstatus_all = True

    def __init__(self, url_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_list = url_list

    def start_requests(self):
        with open(self.url_list, "r") as url_list_file:
            reader = csv.DictReader(url_list_file, delimiter=";")
            for row in reader:
                yield scrapy.Request(
                    row["url"],
                    callback=self.parse,
                    errback=self.parse_error,
                    meta={"name": row["name"]},
                )

    def parse(self, response):
        yield {
            "url": response.url,
            "status": "PASSED",
            "name": response.meta["name"],
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def parse_error(self, failure):
        status = "FAILED"
        error_message = failure.getErrorMessage()

        if "response is invalid" in error_message:
            headers = {"User-Agent": failure.request.headers["User-Agent"]}
            response = requests.get(failure.request.url, headers=headers)
            if response.status == 200:
                status, error_message = "PASSED", None

        yield {
            "url": failure.request.url,
            "status": status,
            "name": failure.request.meta["name"],
            "details": error_message,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
