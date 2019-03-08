# -*- coding:utf-8 -*-

# 用于爬取网站中的数据，但是会有很多问题，由于网页分析不够，
# 爬取的链接会有一些bug,jsonAnalysis会分析出有用的url保存在urls.txt中
import scrapy


class QuotesTalent(scrapy.Spider):
    name = "talent"

    def start_requests(self):
        url = "https://jobs.zhaopin.com/"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        content_lists = response.css('div.main div[class="content clearfix"] .rightTab .content-list')
        for li in content_lists:
            urls = li.css('.listcon a::attr(href)').getall()
            for url in urls:
                yield response.follow(url, self.parse_detail_job)

    def parse_detail_job(self, response):

        is_page = response.css("div.returnpage h1::text").get() is None

        if is_page:
            urls = response.css(
                '.search_list div[class="details_container bg_container "] span.post a::attr(href)').getall()
            next_url = response.css('span.search_page_next a::attr(href)').get()
            yield response.follow(next_url, self.parse_detail_job)
            yield {
                "url": urls
            }
