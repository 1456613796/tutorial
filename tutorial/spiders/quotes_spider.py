# -*- coding:utf-8 -*-

import scrapy


class Quotes(scrapy.Spider):
    name = 'quotes'

    def start_requests(self):
        yield scrapy.Request("http://quotes.toscrape.com/", callback=self.parse)

    def parse(self, response):
        for href in response.css('.quote span a::attr(href)').getall():
            yield response.follow(href, self.parse_author)

    def parse_author(self, response):
        yield {
            "author name": response.css('.author-details h3::text').get().strip(),
            "author born time": response.css('.author-details p span[class="author-born-date"]::text').get().strip(),
            "author born location": response.css(
                '.author-details p span[class="author-born-location"]::text').get().strip(),
            "test": 123456
        }
